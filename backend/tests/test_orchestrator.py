import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from services.orchestrator import AgentOrchestrator, WorkflowType
from agents.input_agent import SiteRequirements
from agents.code_generation_agent import GeneratedCode, CodeMetadata
from agents.audit_agent import AuditResult, CategoryScore, AuditIssue, SeverityLevel, AuditCategory
from agents.deployment_agent import DeploymentMetadata

@pytest.fixture
def mock_context():
    context = MagicMock()
    context.session_id = "test_session"
    context.max_retries = 3
    return context

@pytest.fixture
def mock_state():
    state = MagicMock()
    state.workflow_id = "test_workflow"
    state.completed_agents = []
    state.metrics = MagicMock()
    return state

@pytest.fixture
def orchestrator():
    return AgentOrchestrator()

@pytest.mark.asyncio
async def test_execute_create_site_workflow(orchestrator, mock_context, mock_state):
    # Mock agents
    orchestrator.agents = {
        "InputAgent": MagicMock(),
        "CodeGenerationAgent": MagicMock(),
        "AuditAgent": MagicMock(),
        "DeploymentAgent": MagicMock(),
        "MemoryAgent": MagicMock()
    }
    orchestrator.agent_states = {
        "InputAgent": "ready",
        "CodeGenerationAgent": "ready",
        "AuditAgent": "ready",
        "DeploymentAgent": "ready",
        "MemoryAgent": "ready"
    }
    
    # Mock execute_agent to return appropriate outputs
    async def mock_execute_agent(agent_name, input_data, context, state, enable_retry=True):
        output = MagicMock()
        output.success = True
        
        if agent_name == "InputAgent":
            output.requirements = SiteRequirements(
                site_type="landing_page",
                framework="react",
                ui_library="tailwind"
            )
        elif agent_name == "CodeGenerationAgent":
            output.generated_code = GeneratedCode(
                html="<html></html>",
                additional_files={},
                metadata=CodeMetadata(framework="react", ui_library="tailwind")
            )
        elif agent_name == "AuditAgent":
            output.audit_result = AuditResult(
                overall_score=95,
                seo=CategoryScore(score=90, summary="Good", suggestions=[]),
                accessibility=CategoryScore(score=95, summary="Excellent", suggestions=[]),
                performance=CategoryScore(score=100, summary="Perfect", suggestions=[])
            )
        elif agent_name == "DeploymentAgent":
            output.deployment_metadata = DeploymentMetadata(
                url="https://test.com",
                deployment_id="deploy_123",
                project_id="proj_123",
                project_name="test-site"
            )
        elif agent_name == "MemoryAgent":
            output.site_id = "site_123"
            
        return output

    orchestrator.execute_agent = AsyncMock(side_effect=mock_execute_agent)
    orchestrator._save_workflow_state_to_redis = MagicMock()

    input_data = {"prompt": "Create a landing page"}
    result = await orchestrator._execute_create_site_workflow(input_data, mock_context, mock_state)

    assert result["status"] == "completed"
    assert result["site_id"] == "site_123"
    assert result["deployment_url"] == "https://test.com"
    assert result["audit_score"] == 95
    
    # Verify agent execution order
    expected_calls = ["InputAgent", "CodeGenerationAgent", "AuditAgent", "DeploymentAgent", "MemoryAgent"]
    executed_calls = [call.args[0] for call in orchestrator.execute_agent.call_args_list]
    assert executed_calls == expected_calls

@pytest.mark.asyncio
async def test_execute_update_site_workflow(orchestrator, mock_context, mock_state):
    # Mock agents
    orchestrator.agents = {
        "MemoryAgent": MagicMock(),
        "CodeGenerationAgent": MagicMock(),
        "AuditAgent": MagicMock(),
        "DeploymentAgent": MagicMock()
    }
    orchestrator.agent_states = {
        "MemoryAgent": "ready",
        "CodeGenerationAgent": "ready",
        "AuditAgent": "ready",
        "DeploymentAgent": "ready"
    }

    async def mock_execute_agent(agent_name, input_data, context, state, enable_retry=True):
        output = MagicMock()
        output.success = True
        
        if agent_name == "MemoryAgent":
            if hasattr(input_data, "code"): # SaveSiteInput
                output.version_id = "v2"
            else: # LoadSiteInput
                output.data = {
                    "site": {
                        "name": "test-site",
                        "framework": "react",
                        "latest_version": {"code": "<html>old</html>"}
                    }
                }
        elif agent_name == "CodeGenerationAgent":
            output.generated_code = GeneratedCode(
                html="<html>new</html>",
                additional_files={},
                metadata=CodeMetadata(framework="react", ui_library="tailwind")
            )
        elif agent_name == "AuditAgent":
            output.audit_result = AuditResult(
                overall_score=98,
                seo=CategoryScore(score=95, summary="Great", suggestions=[]),
                accessibility=CategoryScore(score=100, summary="Perfect", suggestions=[]),
                performance=CategoryScore(score=99, summary="Excellent", suggestions=[])
            )
        elif agent_name == "DeploymentAgent":
            output.deployment_metadata = DeploymentMetadata(
                url="https://test.com",
                deployment_id="deploy_456",
                project_id="proj_456",
                project_name="test-site"
            )
            
        return output

    orchestrator.execute_agent = AsyncMock(side_effect=mock_execute_agent)
    orchestrator._save_workflow_state_to_redis = MagicMock()

    input_data = {"site_id": "site_123", "prompt": "Update header"}
    result = await orchestrator._execute_update_site_workflow(input_data, mock_context, mock_state)

    assert result["status"] == "completed"
    assert result["version_id"] == "v2"
    
    # Verify agent execution order
    expected_calls = ["MemoryAgent", "CodeGenerationAgent", "AuditAgent", "DeploymentAgent", "MemoryAgent"]
    executed_calls = [call.args[0] for call in orchestrator.execute_agent.call_args_list]
    assert executed_calls == expected_calls
