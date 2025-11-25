"""
Metrics service for tracking and aggregating agent and workflow metrics.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from models.workflow_log import WorkflowLog
from models.agent_metric import AgentMetric
from utils.logging import logger


class MetricsService:
    """Service for managing metrics and logs."""
    
    def __init__(self, db_session: Session):
        """
        Initialize metrics service.
        
        Args:
            db_session: Database session
        """
        self.db = db_session
    
    def save_workflow_log(
        self,
        workflow_id: str,
        agent_name: Optional[str],
        level: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> WorkflowLog:
        """
        Save a workflow log entry to the database.
        
        Args:
            workflow_id: Workflow ID
            agent_name: Agent name (optional)
            level: Log level (info, warning, error)
            message: Log message
            metadata: Optional metadata
            
        Returns:
            Created WorkflowLog instance
        """
        try:
            log_entry = WorkflowLog(
                workflow_id=workflow_id,
                agent_name=agent_name,
                level=level,
                message=message,
                log_metadata=metadata or {},
            )
            self.db.add(log_entry)
            self.db.commit()
            return log_entry
        except Exception as e:
            logger.error(f"Failed to save workflow log: {str(e)}")
            self.db.rollback()
            raise
    
    def save_workflow_logs_batch(
        self,
        logs: List[Dict[str, Any]],
        workflow_id: str,
    ):
        """
        Save multiple workflow logs in batch.
        
        Args:
            logs: List of log dictionaries
            workflow_id: Workflow ID
        """
        try:
            log_entries = []
            for log in logs:
                log_entry = WorkflowLog(
                    workflow_id=workflow_id,
                    agent_name=log.get("agent"),
                    level=log.get("level", "info"),
                    message=log.get("message", ""),
                    log_metadata=log.get("metadata", {}),
                )
                log_entries.append(log_entry)
            
            self.db.bulk_save_objects(log_entries)
            self.db.commit()
            logger.info(f"Saved {len(log_entries)} workflow logs for workflow {workflow_id}")
        except Exception as e:
            logger.error(f"Failed to save workflow logs batch: {str(e)}")
            self.db.rollback()
            raise
    
    def get_workflow_logs(
        self,
        workflow_id: str,
        level: Optional[str] = None,
        agent_name: Optional[str] = None,
        limit: int = 100,
    ) -> List[WorkflowLog]:
        """
        Get workflow logs with optional filtering.
        
        Args:
            workflow_id: Workflow ID
            level: Optional log level filter
            agent_name: Optional agent name filter
            limit: Maximum number of logs to return
            
        Returns:
            List of WorkflowLog instances
        """
        query = self.db.query(WorkflowLog).filter(
            WorkflowLog.workflow_id == workflow_id
        )
        
        if level:
            query = query.filter(WorkflowLog.level == level)
        
        if agent_name:
            query = query.filter(WorkflowLog.agent_name == agent_name)
        
        return query.order_by(WorkflowLog.created_at.desc()).limit(limit).all()
    
    def update_agent_metrics(
        self,
        agent_name: str,
        execution_time: float,
        success: bool,
    ):
        """
        Update agent metrics in the database.
        
        Args:
            agent_name: Agent name
            execution_time: Execution time in seconds
            success: Whether execution was successful
        """
        try:
            # Get or create agent metrics
            metric = self.db.query(AgentMetric).filter(
                AgentMetric.agent_name == agent_name
            ).first()
            
            if not metric:
                metric = AgentMetric(agent_name=agent_name)
                self.db.add(metric)
            
            # Update metrics
            metric.execution_count += 1
            if success:
                metric.success_count += 1
            else:
                metric.error_count += 1
            
            # Update average duration
            total_time = metric.average_duration * (metric.execution_count - 1) + execution_time
            metric.average_duration = total_time / metric.execution_count
            metric.last_execution_time = datetime.utcnow()
            
            self.db.commit()
        except Exception as e:
            logger.error(f"Failed to update agent metrics: {str(e)}")
            self.db.rollback()
            raise
    
    def get_agent_metrics(
        self,
        agent_name: Optional[str] = None,
    ) -> List[AgentMetric]:
        """
        Get agent metrics.
        
        Args:
            agent_name: Optional agent name filter
            
        Returns:
            List of AgentMetric instances
        """
        query = self.db.query(AgentMetric)
        
        if agent_name:
            query = query.filter(AgentMetric.agent_name == agent_name)
        
        return query.all()
    
    def get_agent_metrics_summary(self) -> Dict[str, Any]:
        """
        Get aggregated metrics summary for all agents.
        
        Returns:
            Dictionary with metrics summary
        """
        metrics = self.get_agent_metrics()
        
        total_executions = sum(m.execution_count for m in metrics)
        total_successes = sum(m.success_count for m in metrics)
        total_errors = sum(m.error_count for m in metrics)
        
        return {
            "total_agents": len(metrics),
            "total_executions": total_executions,
            "total_successes": total_successes,
            "total_errors": total_errors,
            "overall_success_rate": total_successes / total_executions if total_executions > 0 else 0,
            "overall_error_rate": total_errors / total_executions if total_executions > 0 else 0,
            "agents": [
                {
                    "agent_name": m.agent_name,
                    "execution_count": m.execution_count,
                    "success_count": m.success_count,
                    "error_count": m.error_count,
                    "success_rate": m.success_count / m.execution_count if m.execution_count > 0 else 0,
                    "average_duration": m.average_duration,
                    "last_execution_time": m.last_execution_time.isoformat() if m.last_execution_time else None,
                }
                for m in metrics
            ],
        }
    
    def get_workflow_metrics(
        self,
        workflow_id: str,
    ) -> Dict[str, Any]:
        """
        Get metrics for a specific workflow.
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            Dictionary with workflow metrics
        """
        logs = self.get_workflow_logs(workflow_id, limit=1000)
        
        total_logs = len(logs)
        error_logs = len([log for log in logs if log.level == "error"])
        warning_logs = len([log for log in logs if log.level == "warning"])
        info_logs = len([log for log in logs if log.level == "info"])
        
        # Get unique agents
        agents = set(log.agent_name for log in logs if log.agent_name)
        
        return {
            "workflow_id": workflow_id,
            "total_logs": total_logs,
            "error_count": error_logs,
            "warning_count": warning_logs,
            "info_count": info_logs,
            "agents_involved": list(agents),
            "agent_count": len(agents),
        }
    
    def get_metrics_trends(
        self,
        agent_name: Optional[str] = None,
        days: int = 7,
    ) -> Dict[str, Any]:
        """
        Get metrics trends over time.
        
        Args:
            agent_name: Optional agent name filter
            days: Number of days to look back
            
        Returns:
            Dictionary with trend data
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        query = self.db.query(
            func.date(WorkflowLog.created_at).label("date"),
            func.count(WorkflowLog.id).label("count"),
            WorkflowLog.level,
        ).filter(
            WorkflowLog.created_at >= cutoff_date
        )
        
        if agent_name:
            query = query.filter(WorkflowLog.agent_name == agent_name)
        
        results = query.group_by(
            func.date(WorkflowLog.created_at),
            WorkflowLog.level
        ).all()
        
        # Organize by date
        trends = {}
        for date, count, level in results:
            date_str = date.isoformat()
            if date_str not in trends:
                trends[date_str] = {"date": date_str, "info": 0, "warning": 0, "error": 0}
            trends[date_str][level] = count
        
        return {
            "agent_name": agent_name,
            "days": days,
            "trends": list(trends.values()),
        }
    
    def cleanup_old_logs(self, days: int = 90):
        """
        Clean up old workflow logs.
        
        Args:
            days: Number of days to keep logs
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            deleted = self.db.query(WorkflowLog).filter(
                WorkflowLog.created_at < cutoff_date
            ).delete()
            
            self.db.commit()
            logger.info(f"Cleaned up {deleted} old workflow logs")
            return deleted
        except Exception as e:
            logger.error(f"Failed to cleanup old logs: {str(e)}")
            self.db.rollback()
            raise
    
    def export_metrics_prometheus(self) -> str:
        """
        Export metrics in Prometheus format.
        
        Returns:
            Prometheus-formatted metrics string
        """
        metrics = self.get_agent_metrics()
        
        lines = []
        lines.append("# HELP agent_execution_count Total number of agent executions")
        lines.append("# TYPE agent_execution_count counter")
        
        for metric in metrics:
            lines.append(f'agent_execution_count{{agent="{metric.agent_name}"}} {metric.execution_count}')
        
        lines.append("")
        lines.append("# HELP agent_success_count Total number of successful agent executions")
        lines.append("# TYPE agent_success_count counter")
        
        for metric in metrics:
            lines.append(f'agent_success_count{{agent="{metric.agent_name}"}} {metric.success_count}')
        
        lines.append("")
        lines.append("# HELP agent_error_count Total number of failed agent executions")
        lines.append("# TYPE agent_error_count counter")
        
        for metric in metrics:
            lines.append(f'agent_error_count{{agent="{metric.agent_name}"}} {metric.error_count}')
        
        lines.append("")
        lines.append("# HELP agent_average_duration_seconds Average execution duration in seconds")
        lines.append("# TYPE agent_average_duration_seconds gauge")
        
        for metric in metrics:
            lines.append(f'agent_average_duration_seconds{{agent="{metric.agent_name}"}} {metric.average_duration}')
        
        return "\n".join(lines)
