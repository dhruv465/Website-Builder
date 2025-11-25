from locust import HttpUser, task, between
import random

class WebsiteBuilderUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Called when a user starts"""
        # Create a session
        response = self.client.post("/api/sessions")
        if response.status_code == 200:
            self.session_id = response.json().get("session_id")
        else:
            self.session_id = None
    
    @task(3)
    def view_homepage(self):
        """View the homepage"""
        self.client.get("/")
    
    @task(2)
    def health_check(self):
        """Check API health"""
        self.client.get("/health")
    
    @task(5)
    def create_workflow(self):
        """Create a new workflow"""
        if not self.session_id:
            return
        
        frameworks = ["html", "react", "vue"]
        design_styles = ["modern", "minimal", "classic", "bold"]
        
        self.client.post("/api/workflows", json={
            "session_id": self.session_id,
            "requirements": f"Create a {random.choice(design_styles)} portfolio website",
            "framework": random.choice(frameworks),
            "design_style": random.choice(design_styles),
        })
    
    @task(2)
    def get_workflow_status(self):
        """Get workflow status"""
        if not self.session_id:
            return
        
        self.client.get(f"/api/workflows/{self.session_id}/status")
    
    @task(1)
    def get_templates(self):
        """Get available templates"""
        self.client.get("/api/templates")
    
    @task(1)
    def search_unsplash(self):
        """Search Unsplash for images"""
        queries = ["nature", "technology", "business", "abstract", "people"]
        self.client.get("/api/assets/unsplash/search", params={
            "query": random.choice(queries),
            "per_page": 10,
        })
    
    @task(1)
    def get_google_fonts(self):
        """Get Google Fonts"""
        self.client.get("/api/assets/fonts")
    
    @task(2)
    def parse_edit_command(self):
        """Parse an edit command"""
        commands = [
            "Change the header background to blue",
            "Add a contact form",
            "Make the text larger",
            "Center the content",
        ]
        
        self.client.post("/api/edit/parse", json={
            "command": random.choice(commands),
            "html_code": "<div>Sample HTML</div>",
            "css_code": "body { margin: 0; }",
        })


class AdminUser(HttpUser):
    """Simulates admin users accessing admin endpoints"""
    wait_time = between(2, 5)
    
    @task
    def view_metrics(self):
        """View system metrics"""
        self.client.get("/metrics")
    
    @task
    def view_health(self):
        """View health status"""
        self.client.get("/health")


class StressTestUser(HttpUser):
    """Simulates heavy load scenarios"""
    wait_time = between(0.1, 0.5)
    
    @task(10)
    def rapid_health_checks(self):
        """Rapid health checks to test rate limiting"""
        self.client.get("/health")
    
    @task(5)
    def rapid_api_calls(self):
        """Rapid API calls"""
        self.client.get("/api/templates")
