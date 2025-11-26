"""
Memory Agent for session and site data persistence.

This agent manages:
- Session storage and retrieval
- Site record storage with version history
- User preferences persistence with Redis caching
- Automatic cleanup of old sessions
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import uuid
import json
import gzip
import base64

from agents.base_agent import (
    BaseAgent,
    AgentInput,
    AgentOutput,
    AgentContext,
    ValidationResult,
    AgentError,
    ErrorType,
)
from repositories.session_repository import SessionRepository
from repositories.site_repository import SiteRepository
from repositories.preferences_repository import PreferencesRepository
from services.redis_service import redis_service
from models.site import FrameworkTypeDB, DesignStyleTypeDB
from utils.logging import logger
from pydantic import Field


# Input Models
class SaveSessionInput(AgentInput):
    """Input for saving session data."""
    session_id: str
    user_id: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class LoadSessionInput(AgentInput):
    """Input for loading session data."""
    session_id: str


class SaveSiteInput(AgentInput):
    """Input for saving site data."""
    session_id: str
    site_id: Optional[str] = None
    site_name: str
    code: str
    requirements: Optional[Dict[str, Any]] = None
    changes: Optional[str] = None
    framework: Optional[str] = None
    design_style: Optional[str] = None


class LoadSiteInput(AgentInput):
    """Input for loading site data."""
    site_id: str


class SavePreferencesInput(AgentInput):
    """Input for saving user preferences."""
    session_id: str
    default_color_scheme: Optional[str] = None
    default_site_type: Optional[str] = None
    favorite_features: Optional[List[str]] = None
    design_style: Optional[str] = None
    framework_preference: Optional[str] = None
    design_style_preference: Optional[str] = None


class LoadPreferencesInput(AgentInput):
    """Input for loading user preferences."""
    session_id: str


class CleanupInput(AgentInput):
    """Input for cleanup operation."""
    days: int = Field(default=90, description="Number of days to keep sessions")


class ExportSessionInput(AgentInput):
    """Input for exporting session data."""
    session_id: str


class ImportSessionInput(AgentInput):
    """Input for importing session data."""
    session_data: Dict[str, Any]


class GetFrameworkChangesInput(AgentInput):
    """Input for getting framework changes."""
    site_id: str


# Output Models
class SessionOutput(AgentOutput):
    """Output for session operations."""
    session_id: Optional[str] = None


class SiteOutput(AgentOutput):
    """Output for site operations."""
    site_id: Optional[str] = None
    version_id: Optional[str] = None


class SaveSiteOutput(SiteOutput):
    """Output for save site operation."""
    pass


class PreferencesOutput(AgentOutput):
    """Output for preferences operations."""
    preferences: Optional[Dict[str, Any]] = None


class CleanupOutput(AgentOutput):
    """Output for cleanup operations."""
    deleted_count: int = 0


class FrameworkChangesOutput(AgentOutput):
    """Output for framework changes operations."""
    changes: Optional[List[Dict[str, Any]]] = None


class MemoryAgent(BaseAgent):
    """
    Memory Agent for managing persistent storage.
    
    Responsibilities:
    - Save and load user sessions
    - Store site records with version history
    - Manage user preferences with Redis caching
    - Automatic cleanup of old sessions
    """
    
    def __init__(self):
        """Initialize Memory Agent."""
        super().__init__(name="MemoryAgent")
        self.session_repo = SessionRepository()
        self.site_repo = SiteRepository()
        self.preferences_repo = PreferencesRepository()
        self.redis = redis_service
        logger.info("Memory Agent initialized")
    
    async def execute(self, input_data: AgentInput, context: AgentContext) -> AgentOutput:
        """
        Execute memory operation based on input type.
        
        Args:
            input_data: Input data for the operation
            context: Execution context
            
        Returns:
            AgentOutput with results
            
        Raises:
            AgentError: If operation fails
        """
        try:
            # Route to appropriate handler based on input type
            if isinstance(input_data, SaveSessionInput):
                return await self._save_session(input_data, context)
            elif isinstance(input_data, LoadSessionInput):
                return await self._load_session(input_data, context)
            elif isinstance(input_data, SaveSiteInput):
                return await self._save_site(input_data, context)
            elif isinstance(input_data, LoadSiteInput):
                return await self._load_site(input_data, context)
            elif isinstance(input_data, SavePreferencesInput):
                return await self._save_preferences(input_data, context)
            elif isinstance(input_data, LoadPreferencesInput):
                return await self._load_preferences(input_data, context)
            elif isinstance(input_data, CleanupInput):
                return await self._cleanup(input_data, context)
            elif isinstance(input_data, ExportSessionInput):
                return await self._export_session(input_data, context)
            elif isinstance(input_data, ImportSessionInput):
                return await self._import_session(input_data, context)
            elif isinstance(input_data, GetFrameworkChangesInput):
                return await self._get_framework_changes(input_data, context)
            else:
                raise AgentError(
                    message=f"Unsupported input type: {type(input_data).__name__}",
                    error_type=ErrorType.VALIDATION_ERROR,
                    agent_name=self.name,
                    recoverable=False,
                    retryable=False,
                )
        except AgentError:
            raise
        except Exception as e:
            logger.error(f"Memory Agent execution error: {str(e)}")
            raise AgentError(
                message=f"Memory operation failed: {str(e)}",
                error_type=ErrorType.STORAGE_ERROR,
                agent_name=self.name,
                recoverable=False,
                retryable=True,
            )
    
    async def _save_session(self, input_data: SaveSessionInput, context: AgentContext) -> SessionOutput:
        """Save session data."""
        try:
            session_uuid = uuid.UUID(input_data.session_id)
            user_uuid = uuid.UUID(input_data.user_id) if input_data.user_id else None
            
            # Check if session exists
            existing_session = self.session_repo.get_by_id(session_uuid)
            
            if existing_session:
                # Update existing session
                session = self.session_repo.update(
                    session_id=session_uuid,
                    preferences=input_data.preferences,
                )
            else:
                # Create new session
                session = self.session_repo.create(
                    user_id=user_uuid,
                    preferences=input_data.preferences,
                )
            
            # Cache in Redis
            session_data = {
                "id": str(session.id),
                "user_id": str(session.user_id) if session.user_id else None,
                "preferences": session.preferences,
                "created_at": session.created_at.isoformat(),
                "last_accessed_at": session.last_accessed_at.isoformat(),
                "sites": [],
            }
            self.redis.set_session(str(session.id), session_data)
            
            logger.info(f"Saved session {session.id}")
            
            return SessionOutput(
                success=True,
                session_id=str(session.id),
                data={"session": session_data},
            )
        except Exception as e:
            logger.error(f"Error saving session: {str(e)}")
            raise AgentError(
                message=f"Failed to save session: {str(e)}",
                error_type=ErrorType.STORAGE_ERROR,
                agent_name=self.name,
                recoverable=False,
                retryable=True,
            )
    
    async def _load_session(self, input_data: LoadSessionInput, context: AgentContext) -> SessionOutput:
        """Load session data."""
        try:
            session_id = input_data.session_id
            
            # Try Redis cache first
            cached_session = self.redis.get_session(session_id)
            if cached_session:
                logger.info(f"Loaded session {session_id} from cache")
                return SessionOutput(
                    success=True,
                    session_id=session_id,
                    data={"session": cached_session},
                )
            
            # Load from database
            session_uuid = uuid.UUID(session_id)
            session = self.session_repo.get_by_id(session_uuid)
            
            if not session:
                logger.warning(f"Session {session_id} not found")
                return SessionOutput(
                    success=False,
                    data={"error": "Session not found"},
                )
            
            # Cache in Redis
            session_data = {
                "id": str(session.id),
                "user_id": str(session.user_id) if session.user_id else None,
                "preferences": session.preferences,
                "created_at": session.created_at.isoformat(),
                "last_accessed_at": session.last_accessed_at.isoformat(),
                "sites": [],
            }
            self.redis.set_session(str(session.id), session_data)
            
            logger.info(f"Loaded session {session_id} from database")
            
            return SessionOutput(
                success=True,
                session_id=str(session.id),
                data={"session": session_data},
            )
        except Exception as e:
            logger.error(f"Error loading session: {str(e)}")
            raise AgentError(
                message=f"Failed to load session: {str(e)}",
                error_type=ErrorType.STORAGE_ERROR,
                agent_name=self.name,
                recoverable=False,
                retryable=True,
            )
    
    async def _save_site(self, input_data: SaveSiteInput, context: AgentContext) -> SiteOutput:
        """Save site data with version history."""
        try:
            session_uuid = uuid.UUID(input_data.session_id)
            
            # Convert framework and design_style strings to enums
            framework_enum = None
            if input_data.framework:
                try:
                    framework_enum = FrameworkTypeDB(input_data.framework.lower())
                except ValueError:
                    logger.warning(f"Invalid framework value: {input_data.framework}")
            
            design_style_enum = None
            if input_data.design_style:
                try:
                    design_style_enum = DesignStyleTypeDB(input_data.design_style.lower())
                except ValueError:
                    logger.warning(f"Invalid design_style value: {input_data.design_style}")
            
            # Compress code if large
            code = input_data.code
            if len(code) > 10000:  # Compress if larger than 10KB
                code = self._compress_code(code)
            
            if input_data.site_id:
                # Update existing site
                site_uuid = uuid.UUID(input_data.site_id)
                site = self.site_repo.get_site_by_id(site_uuid)
                
                if not site:
                    raise AgentError(
                        message=f"Site {input_data.site_id} not found",
                        error_type=ErrorType.VALIDATION_ERROR,
                        agent_name=self.name,
                        recoverable=False,
                        retryable=False,
                    )
                
                # Update site with framework and design_style if provided
                if framework_enum is not None or design_style_enum is not None:
                    self.site_repo.update_site(
                        site_id=site_uuid,
                        framework=framework_enum,
                        design_style=design_style_enum,
                    )
                    # Refresh site object
                    site = self.site_repo.get_site_by_id(site_uuid)
                
                # Create new version
                version = self.site_repo.create_version(
                    site_id=site_uuid,
                    code=code,
                    requirements=input_data.requirements,
                    changes=input_data.changes,
                )
            else:
                # Create new site
                site = self.site_repo.create_site(
                    session_id=session_uuid,
                    name=input_data.site_name,
                    framework=framework_enum,
                    design_style=design_style_enum,
                )
                
                # Create initial version
                version = self.site_repo.create_version(
                    site_id=site.id,
                    code=code,
                    requirements=input_data.requirements,
                    changes="Initial version",
                )
            
            # Cache latest site data in Redis
            site_data = {
                "id": str(site.id),
                "name": site.name,
                "framework": site.framework.value if site.framework else None,
                "design_style": site.design_style.value if site.design_style else None,
                "latest_version": {
                    "id": str(version.id),
                    "version_number": version.version_number,
                    "code": code,
                    "requirements": version.requirements,
                    "changes": version.changes,
                    "created_at": version.created_at.isoformat(),
                },
            }
            self.redis.set_site_cache(str(site.id), site_data)
            
            logger.info(f"Saved site {site.id} version {version.version_number} with framework {site.framework} and design style {site.design_style}")
            
            return SiteOutput(
                success=True,
                site_id=str(site.id),
                version_id=str(version.id),
                data={
                    "site": site_data,
                    "version_number": version.version_number,
                },
            )
        except AgentError:
            raise
        except Exception as e:
            logger.error(f"Error saving site: {str(e)}")
            raise AgentError(
                message=f"Failed to save site: {str(e)}",
                error_type=ErrorType.STORAGE_ERROR,
                agent_name=self.name,
                recoverable=False,
                retryable=True,
            )
    
    async def _load_site(self, input_data: LoadSiteInput, context: AgentContext) -> SiteOutput:
        """Load site data."""
        try:
            site_id = input_data.site_id
            
            # Try Redis cache first
            cached_site = self.redis.get_site_cache(site_id)
            if cached_site:
                logger.info(f"Loaded site {site_id} from cache")
                return SiteOutput(
                    success=True,
                    site_id=site_id,
                    data={"site": cached_site},
                )
            
            # Load from database
            site_uuid = uuid.UUID(site_id)
            site = self.site_repo.get_site_by_id(site_uuid)
            
            if not site:
                logger.warning(f"Site {site_id} not found")
                return SiteOutput(
                    success=False,
                    data={"error": "Site not found"},
                )
            
            # Get latest version
            latest_version = self.site_repo.get_latest_version(site_uuid)
            
            # Decompress code if needed
            code = latest_version.code if latest_version else ""
            if code and code.startswith("gzip:"):
                code = self._decompress_code(code)
            
            # Build site data
            site_data = {
                "id": str(site.id),
                "name": site.name,
                "session_id": str(site.session_id),
                "framework": site.framework.value if site.framework else None,
                "design_style": site.design_style.value if site.design_style else None,
                "created_at": site.created_at.isoformat(),
                "updated_at": site.updated_at.isoformat(),
            }
            
            if latest_version:
                site_data["latest_version"] = {
                    "id": str(latest_version.id),
                    "version_number": latest_version.version_number,
                    "code": code,
                    "requirements": latest_version.requirements,
                    "changes": latest_version.changes,
                    "created_at": latest_version.created_at.isoformat(),
                    "audit_score": latest_version.audit_score,
                }
            
            # Get version history
            versions = self.site_repo.get_versions_by_site(site_uuid)
            site_data["versions"] = [
                {
                    "id": str(v.id),
                    "version_number": v.version_number,
                    "changes": v.changes,
                    "created_at": v.created_at.isoformat(),
                    "audit_score": v.audit_score,
                }
                for v in versions
            ]
            
            # Cache in Redis
            self.redis.set_site_cache(str(site.id), site_data)
            
            logger.info(f"Loaded site {site_id} from database")
            
            return SiteOutput(
                success=True,
                site_id=str(site.id),
                data={"site": site_data},
            )
        except Exception as e:
            logger.error(f"Error loading site: {str(e)}")
            raise AgentError(
                message=f"Failed to load site: {str(e)}",
                error_type=ErrorType.STORAGE_ERROR,
                agent_name=self.name,
                recoverable=False,
                retryable=True,
            )
    
    async def _save_preferences(self, input_data: SavePreferencesInput, context: AgentContext) -> PreferencesOutput:
        """Save user preferences."""
        try:
            session_uuid = uuid.UUID(input_data.session_id)
            
            # Convert framework and design_style preferences to enums
            framework_pref_enum = None
            if input_data.framework_preference:
                try:
                    framework_pref_enum = FrameworkTypeDB(input_data.framework_preference.lower())
                except ValueError:
                    logger.warning(f"Invalid framework_preference value: {input_data.framework_preference}")
            
            design_style_pref_enum = None
            if input_data.design_style_preference:
                try:
                    design_style_pref_enum = DesignStyleTypeDB(input_data.design_style_preference.lower())
                except ValueError:
                    logger.warning(f"Invalid design_style_preference value: {input_data.design_style_preference}")
            
            # Update preferences in database
            preferences = self.preferences_repo.update(
                session_id=session_uuid,
                default_color_scheme=input_data.default_color_scheme,
                default_site_type=input_data.default_site_type,
                favorite_features=input_data.favorite_features,
                design_style=input_data.design_style,
                framework_preference=framework_pref_enum,
                design_style_preference=design_style_pref_enum,
            )
            
            # Build preferences data
            prefs_data = {
                "default_color_scheme": preferences.default_color_scheme,
                "default_site_type": preferences.default_site_type,
                "favorite_features": preferences.favorite_features,
                "design_style": preferences.design_style,
                "framework_preference": preferences.framework_preference.value if preferences.framework_preference else None,
                "design_style_preference": preferences.design_style_preference.value if preferences.design_style_preference else None,
            }
            
            # Update session cache with new preferences
            cached_session = self.redis.get_session(input_data.session_id)
            if cached_session:
                cached_session["preferences"] = prefs_data
                self.redis.set_session(input_data.session_id, cached_session)
            
            logger.info(f"Saved preferences for session {input_data.session_id}")
            
            return PreferencesOutput(
                success=True,
                preferences=prefs_data,
                data={"preferences": prefs_data},
            )
        except Exception as e:
            logger.error(f"Error saving preferences: {str(e)}")
            raise AgentError(
                message=f"Failed to save preferences: {str(e)}",
                error_type=ErrorType.STORAGE_ERROR,
                agent_name=self.name,
                recoverable=False,
                retryable=True,
            )
    
    async def _load_preferences(self, input_data: LoadPreferencesInput, context: AgentContext) -> PreferencesOutput:
        """Load user preferences."""
        try:
            # Try to get from session cache first
            cached_session = self.redis.get_session(input_data.session_id)
            if cached_session and cached_session.get("preferences"):
                logger.info(f"Loaded preferences from cache for session {input_data.session_id}")
                return PreferencesOutput(
                    success=True,
                    preferences=cached_session["preferences"],
                    data={"preferences": cached_session["preferences"]},
                )
            
            # Load from database
            session_uuid = uuid.UUID(input_data.session_id)
            preferences = self.preferences_repo.get_by_session_id(session_uuid)
            
            if not preferences:
                logger.info(f"No preferences found for session {input_data.session_id}")
                return PreferencesOutput(
                    success=True,
                    preferences={},
                    data={"preferences": {}},
                )
            
            prefs_data = {
                "default_color_scheme": preferences.default_color_scheme,
                "default_site_type": preferences.default_site_type,
                "favorite_features": preferences.favorite_features,
                "design_style": preferences.design_style,
                "framework_preference": preferences.framework_preference.value if preferences.framework_preference else None,
                "design_style_preference": preferences.design_style_preference.value if preferences.design_style_preference else None,
            }
            
            logger.info(f"Loaded preferences from database for session {input_data.session_id}")
            
            return PreferencesOutput(
                success=True,
                preferences=prefs_data,
                data={"preferences": prefs_data},
            )
        except Exception as e:
            logger.error(f"Error loading preferences: {str(e)}")
            raise AgentError(
                message=f"Failed to load preferences: {str(e)}",
                error_type=ErrorType.STORAGE_ERROR,
                agent_name=self.name,
                recoverable=False,
                retryable=True,
            )
    
    async def _cleanup(self, input_data: CleanupInput, context: AgentContext) -> CleanupOutput:
        """Cleanup old sessions."""
        try:
            deleted_count = self.session_repo.cleanup_old_sessions(days=input_data.days)
            
            logger.info(f"Cleaned up {deleted_count} sessions older than {input_data.days} days")
            
            return CleanupOutput(
                success=True,
                deleted_count=deleted_count,
                data={"deleted_count": deleted_count, "days": input_data.days},
            )
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            raise AgentError(
                message=f"Failed to cleanup sessions: {str(e)}",
                error_type=ErrorType.STORAGE_ERROR,
                agent_name=self.name,
                recoverable=False,
                retryable=True,
            )
    
    async def _export_session(self, input_data: ExportSessionInput, context: AgentContext) -> AgentOutput:
        """Export session data to JSON."""
        try:
            session_uuid = uuid.UUID(input_data.session_id)
            
            # Load session
            session = self.session_repo.get_by_id(session_uuid)
            if not session:
                return AgentOutput(
                    success=False,
                    data={"error": "Session not found"},
                )
            
            # Load all sites for this session
            sites = self.site_repo.get_sites_by_session(session_uuid)
            
            # Build export data
            export_data = {
                "session": {
                    "id": str(session.id),
                    "user_id": str(session.user_id) if session.user_id else None,
                    "preferences": session.preferences,
                    "created_at": session.created_at.isoformat(),
                    "last_accessed_at": session.last_accessed_at.isoformat(),
                },
                "sites": [],
            }
            
            # Add site data
            for site in sites:
                versions = self.site_repo.get_versions_by_site(site.id)
                audits = self.site_repo.get_audits_by_site(site.id)
                deployments = self.site_repo.get_deployments_by_site(site.id)
                
                site_data = {
                    "id": str(site.id),
                    "name": site.name,
                    "framework": site.framework.value if site.framework else None,
                    "design_style": site.design_style.value if site.design_style else None,
                    "created_at": site.created_at.isoformat(),
                    "updated_at": site.updated_at.isoformat(),
                    "versions": [
                        {
                            "id": str(v.id),
                            "version_number": v.version_number,
                            "code": v.code,
                            "requirements": v.requirements,
                            "changes": v.changes,
                            "created_at": v.created_at.isoformat(),
                            "audit_score": v.audit_score,
                        }
                        for v in versions
                    ],
                    "audits": [
                        {
                            "id": str(a.id),
                            "seo_score": a.seo_score,
                            "accessibility_score": a.accessibility_score,
                            "performance_score": a.performance_score,
                            "overall_score": a.overall_score,
                            "details": a.details,
                            "created_at": a.created_at.isoformat(),
                        }
                        for a in audits
                    ],
                    "deployments": [
                        {
                            "id": str(d.id),
                            "url": d.url,
                            "deployment_id": d.deployment_id,
                            "project_id": d.project_id,
                            "status": d.status,
                            "build_time": d.build_time,
                            "created_at": d.created_at.isoformat(),
                        }
                        for d in deployments
                    ],
                }
                export_data["sites"].append(site_data)
            
            # Compress export data
            compressed = self._compress_json(export_data)
            
            logger.info(f"Exported session {input_data.session_id}")
            
            return AgentOutput(
                success=True,
                data={
                    "export_data": compressed,
                    "session_id": input_data.session_id,
                    "exported_at": datetime.utcnow().isoformat(),
                },
            )
        except Exception as e:
            logger.error(f"Error exporting session: {str(e)}")
            raise AgentError(
                message=f"Failed to export session: {str(e)}",
                error_type=ErrorType.STORAGE_ERROR,
                agent_name=self.name,
                recoverable=False,
                retryable=False,
            )
    
    async def _import_session(self, input_data: ImportSessionInput, context: AgentContext) -> AgentOutput:
        """Import session data from JSON."""
        try:
            # Decompress if needed
            session_data = input_data.session_data
            if isinstance(session_data, str) and session_data.startswith("gzip:"):
                session_data = self._decompress_json(session_data)
            
            # Create new session
            session = self.session_repo.create(
                user_id=uuid.UUID(session_data["session"]["user_id"]) if session_data["session"].get("user_id") else None,
                preferences=session_data["session"].get("preferences", {}),
            )
            
            # Import sites
            imported_sites = []
            for site_data in session_data.get("sites", []):
                # Convert framework and design_style to enums if present
                framework_enum = None
                if site_data.get("framework"):
                    try:
                        framework_enum = FrameworkTypeDB(site_data["framework"])
                    except ValueError:
                        logger.warning(f"Invalid framework in import: {site_data['framework']}")
                
                design_style_enum = None
                if site_data.get("design_style"):
                    try:
                        design_style_enum = DesignStyleTypeDB(site_data["design_style"])
                    except ValueError:
                        logger.warning(f"Invalid design_style in import: {site_data['design_style']}")
                
                # Create site
                site = self.site_repo.create_site(
                    session_id=session.id,
                    name=site_data["name"],
                    framework=framework_enum,
                    design_style=design_style_enum,
                )
                
                # Create versions
                for version_data in site_data.get("versions", []):
                    version = self.site_repo.create_version(
                        site_id=site.id,
                        code=version_data["code"],
                        requirements=version_data.get("requirements"),
                        changes=version_data.get("changes"),
                    )
                    
                    # Update audit score if present
                    if version_data.get("audit_score"):
                        self.site_repo.update_version_audit_score(
                            version_id=version.id,
                            audit_score=version_data["audit_score"],
                        )
                
                imported_sites.append(str(site.id))
            
            logger.info(f"Imported session with {len(imported_sites)} sites")
            
            return AgentOutput(
                success=True,
                data={
                    "session_id": str(session.id),
                    "imported_sites": imported_sites,
                    "imported_at": datetime.utcnow().isoformat(),
                },
            )
        except Exception as e:
            logger.error(f"Error importing session: {str(e)}")
            raise AgentError(
                message=f"Failed to import session: {str(e)}",
                error_type=ErrorType.STORAGE_ERROR,
                agent_name=self.name,
                recoverable=False,
                retryable=False,
            )
    
    async def _get_framework_changes(self, input_data: GetFrameworkChangesInput, context: AgentContext) -> FrameworkChangesOutput:
        """Get framework change history for a site."""
        try:
            site_uuid = uuid.UUID(input_data.site_id)
            
            # Get framework changes from repository
            changes = self.site_repo.get_framework_changes(site_uuid)
            
            # Build changes data
            changes_data = [
                {
                    "id": str(change.id),
                    "site_id": str(change.site_id),
                    "from_framework": change.from_framework.value if change.from_framework else None,
                    "to_framework": change.to_framework.value if change.to_framework else None,
                    "reason": change.reason,
                    "created_at": change.created_at.isoformat(),
                }
                for change in changes
            ]
            
            logger.info(f"Retrieved {len(changes_data)} framework changes for site {input_data.site_id}")
            
            return FrameworkChangesOutput(
                success=True,
                changes=changes_data,
                data={"changes": changes_data, "count": len(changes_data)},
            )
        except Exception as e:
            logger.error(f"Error getting framework changes: {str(e)}")
            raise AgentError(
                message=f"Failed to get framework changes: {str(e)}",
                error_type=ErrorType.STORAGE_ERROR,
                agent_name=self.name,
                recoverable=False,
                retryable=True,
            )
    
    def validate(self, output: AgentOutput) -> ValidationResult:
        """
        Validate Memory Agent output.
        
        Args:
            output: Output to validate
            
        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult(is_valid=True, confidence=1.0)
        
        if not output.success:
            result.add_error("Operation failed")
            return result
        
        # Validate based on output type
        if isinstance(output, SessionOutput):
            if not output.session_id:
                result.add_warning("Session ID not set")
        elif isinstance(output, SiteOutput):
            if not output.site_id:
                result.add_warning("Site ID not set")
        elif isinstance(output, CleanupOutput):
            if output.deleted_count < 0:
                result.add_error("Invalid deleted count")
        
        return result
    
    # Helper methods
    def _compress_code(self, code: str) -> str:
        """Compress code using gzip."""
        try:
            compressed = gzip.compress(code.encode("utf-8"))
            encoded = base64.b64encode(compressed).decode("utf-8")
            return f"gzip:{encoded}"
        except Exception as e:
            logger.warning(f"Failed to compress code: {str(e)}")
            return code
    
    def _decompress_code(self, compressed_code: str) -> str:
        """Decompress code from gzip."""
        try:
            if not compressed_code.startswith("gzip:"):
                return compressed_code
            
            encoded = compressed_code[5:]  # Remove "gzip:" prefix
            compressed = base64.b64decode(encoded)
            decompressed = gzip.decompress(compressed).decode("utf-8")
            return decompressed
        except Exception as e:
            logger.error(f"Failed to decompress code: {str(e)}")
            return compressed_code
    
    def _compress_json(self, data: Dict[str, Any]) -> str:
        """Compress JSON data using gzip."""
        try:
            json_str = json.dumps(data)
            compressed = gzip.compress(json_str.encode("utf-8"))
            encoded = base64.b64encode(compressed).decode("utf-8")
            return f"gzip:{encoded}"
        except Exception as e:
            logger.warning(f"Failed to compress JSON: {str(e)}")
            return json.dumps(data)
    
    def _decompress_json(self, compressed_data: str) -> Dict[str, Any]:
        """Decompress JSON data from gzip."""
        try:
            if not compressed_data.startswith("gzip:"):
                return json.loads(compressed_data)
            
            encoded = compressed_data[5:]  # Remove "gzip:" prefix
            compressed = base64.b64decode(encoded)
            decompressed = gzip.decompress(compressed).decode("utf-8")
            return json.loads(decompressed)
        except Exception as e:
            logger.error(f"Failed to decompress JSON: {str(e)}")
            return {}
