#!/bin/bash

# Smart Website Builder Deployment Script
# This script helps deploy the application to various environments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check for required tools
    command -v docker >/dev/null 2>&1 || { log_error "docker is required but not installed."; exit 1; }
    command -v kubectl >/dev/null 2>&1 || { log_error "kubectl is required but not installed."; exit 1; }
    
    log_info "Prerequisites check passed"
}

deploy_kubernetes() {
    local environment=$1
    log_info "Deploying to Kubernetes ($environment)..."
    
    # Create namespace if it doesn't exist
    kubectl create namespace smart-website-builder --dry-run=client -o yaml | kubectl apply -f -
    
    # Apply configurations
    log_info "Applying ConfigMap..."
    kubectl apply -f k8s/configmap.yml
    
    log_info "Applying Secrets (ensure secrets are created manually)..."
    if ! kubectl get secret swb-secrets -n smart-website-builder >/dev/null 2>&1; then
        log_warn "Secrets not found. Please create secrets manually:"
        log_warn "kubectl create secret generic swb-secrets --from-literal=... -n smart-website-builder"
        read -p "Press enter to continue after creating secrets..."
    fi
    
    # Deploy databases
    log_info "Deploying PostgreSQL..."
    kubectl apply -f k8s/postgres-deployment.yml
    
    log_info "Deploying Redis..."
    kubectl apply -f k8s/redis-deployment.yml
    
    # Wait for databases
    log_info "Waiting for databases to be ready..."
    kubectl wait --for=condition=ready pod -l app=postgres -n smart-website-builder --timeout=300s
    kubectl wait --for=condition=ready pod -l app=redis -n smart-website-builder --timeout=300s
    
    # Deploy application
    log_info "Deploying backend..."
    kubectl apply -f k8s/backend-deployment.yml
    
    log_info "Deploying Celery workers..."
    kubectl apply -f k8s/celery-deployment.yml
    
    log_info "Deploying frontend..."
    kubectl apply -f k8s/frontend-deployment.yml
    
    # Deploy ingress
    log_info "Deploying ingress..."
    kubectl apply -f k8s/ingress.yml
    
    # Wait for deployments
    log_info "Waiting for deployments to be ready..."
    kubectl rollout status deployment/backend -n smart-website-builder
    kubectl rollout status deployment/frontend -n smart-website-builder
    
    # Run migrations
    log_info "Running database migrations..."
    BACKEND_POD=$(kubectl get pods -n smart-website-builder -l app=backend -o jsonpath='{.items[0].metadata.name}')
    kubectl exec -it $BACKEND_POD -n smart-website-builder -- alembic upgrade head
    
    log_info "Deployment complete!"
    log_info "Access the application at:"
    kubectl get ingress -n smart-website-builder
}

deploy_docker_compose() {
    local environment=$1
    log_info "Deploying with Docker Compose ($environment)..."
    
    # Check for .env file
    if [ ! -f .env.local ]; then
        log_error ".env.local file not found. Please create it from .env.example"
        exit 1
    fi
    
    # Build images
    log_info "Building Docker images..."
    docker-compose build
    
    # Start services
    log_info "Starting services..."
    if [ "$environment" = "production" ]; then
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
    else
        docker-compose up -d
    fi
    
    # Wait for services
    log_info "Waiting for services to be healthy..."
    sleep 30
    
    # Run migrations
    log_info "Running database migrations..."
    docker-compose exec -T api alembic upgrade head
    
    log_info "Deployment complete!"
    log_info "Frontend: http://localhost:80"
    log_info "API: http://localhost:8000"
    log_info "API Docs: http://localhost:8000/docs"
    log_info "Flower: http://localhost:5555"
}

rollback_kubernetes() {
    local deployment=$1
    log_warn "Rolling back deployment: $deployment"
    kubectl rollout undo deployment/$deployment -n smart-website-builder
    kubectl rollout status deployment/$deployment -n smart-website-builder
    log_info "Rollback complete"
}

health_check() {
    log_info "Running health checks..."
    
    # Check API health
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        log_info "API health check: PASSED"
    else
        log_error "API health check: FAILED"
        return 1
    fi
    
    # Check frontend health
    if curl -f http://localhost:80/health >/dev/null 2>&1; then
        log_info "Frontend health check: PASSED"
    else
        log_error "Frontend health check: FAILED"
        return 1
    fi
    
    log_info "All health checks passed"
}

backup_database() {
    log_info "Creating database backup..."
    
    local backup_file="backup_$(date +%Y%m%d_%H%M%S).sql"
    
    if command -v kubectl >/dev/null 2>&1; then
        # Kubernetes backup
        POSTGRES_POD=$(kubectl get pods -n smart-website-builder -l app=postgres -o jsonpath='{.items[0].metadata.name}')
        kubectl exec $POSTGRES_POD -n smart-website-builder -- pg_dump -U postgres smart_website_builder > $backup_file
    else
        # Docker Compose backup
        docker-compose exec -T postgres pg_dump -U postgres smart_website_builder > $backup_file
    fi
    
    log_info "Backup created: $backup_file"
}

show_logs() {
    local service=$1
    
    if command -v kubectl >/dev/null 2>&1; then
        kubectl logs -f -l app=$service -n smart-website-builder
    else
        docker-compose logs -f $service
    fi
}

# Main script
case "$1" in
    k8s)
        check_prerequisites
        deploy_kubernetes "${2:-production}"
        ;;
    docker)
        deploy_docker_compose "${2:-development}"
        ;;
    rollback)
        if [ -z "$2" ]; then
            log_error "Please specify deployment to rollback (backend|frontend|celery-worker)"
            exit 1
        fi
        rollback_kubernetes "$2"
        ;;
    health)
        health_check
        ;;
    backup)
        backup_database
        ;;
    logs)
        if [ -z "$2" ]; then
            log_error "Please specify service (backend|frontend|celery-worker|postgres|redis)"
            exit 1
        fi
        show_logs "$2"
        ;;
    *)
        echo "Smart Website Builder Deployment Script"
        echo ""
        echo "Usage: $0 {k8s|docker|rollback|health|backup|logs} [options]"
        echo ""
        echo "Commands:"
        echo "  k8s [environment]           Deploy to Kubernetes (default: production)"
        echo "  docker [environment]        Deploy with Docker Compose (default: development)"
        echo "  rollback <deployment>       Rollback a Kubernetes deployment"
        echo "  health                      Run health checks"
        echo "  backup                      Create database backup"
        echo "  logs <service>              Show logs for a service"
        echo ""
        echo "Examples:"
        echo "  $0 k8s production          Deploy to Kubernetes production"
        echo "  $0 docker development      Deploy with Docker Compose for development"
        echo "  $0 rollback backend        Rollback backend deployment"
        echo "  $0 health                  Check application health"
        echo "  $0 backup                  Backup database"
        echo "  $0 logs backend            Show backend logs"
        exit 1
        ;;
esac
