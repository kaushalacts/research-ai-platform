"""Services for integrating with FastAPI and AI agents."""
import httpx
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class FastAPIService:
    """Service class for communicating with FastAPI microservices."""
    
    def __init__(self):
        self.base_url = settings.FASTAPI_SERVICE_URL
        self.timeout = 30.0
    
    async def analyze_paper(self, task_id, paper_id):
        """Send paper analysis request to FastAPI service."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/agents/analyze-paper",
                    json={
                        'task_id': str(task_id),
                        'paper_id': str(paper_id)
                    },
                    timeout=self.timeout
                )
                response.raise_for_status()
                data = response.json()
                return data.get('task_id')
            except httpx.RequestError as e:
                logger.error(f"Request error to FastAPI service: {e}")
                raise
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error from FastAPI service: {e}")
                raise
    
    async def cancel_task(self, fastapi_task_id):
        """Cancel task in FastAPI service."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/agents/cancel-task",
                    json={'task_id': fastapi_task_id},
                    timeout=self.timeout
                )
                response.raise_for_status()
                return True
            except Exception as e:
                logger.error(f"Failed to cancel FastAPI task: {e}")
                raise
    
    async def health_check(self):
        """Check health of FastAPI service."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/health",
                    timeout=5.0
                )
                return response.status_code == 200
            except Exception:
                return False


class AIAgentService:
    """Service for direct communication with AI agents."""
    
    def __init__(self):
        self.base_url = settings.AI_AGENT_SERVICE_URL
    
    async def get_agent_status(self):
        """Get status of AI agents."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/status",
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Failed to get agent status: {e}")
                return None
