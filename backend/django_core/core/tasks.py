"""
Celery tasks for AI agent communication and processing.
"""
from celery import shared_task
from django.conf import settings
import httpx
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def analyze_paper_task(self, task_id, paper_id):
    """
    Async task to analyze a research paper using AI agents.
    Communicates with FastAPI services.
    """
    try:
        from .models import AIAnalysisTask, ResearchPaper
        
        # Get the task and paper
        task = AIAnalysisTask.objects.get(id=task_id)
        paper = ResearchPaper.objects.get(id=paper_id)
        
        # Send request to FastAPI service
        with httpx.Client() as client:
            response = client.post(
                f"{settings.FASTAPI_SERVICE_URL}/api/agents/analyze-paper",
                json={
                    'task_id': str(task_id),
                    'paper_id': str(paper_id),
                    'paper_data': {
                        'title': paper.title,
                        'abstract': paper.abstract,
                        'authors': paper.authors,
                        'doi': paper.doi,
                    }
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Update task with results
                task.results = result.get('analysis', {})
                task.status = 'completed'
                task.agent_used = result.get('agent_used', 'unknown')
                task.save()
                
                # Update paper with analysis results
                if 'keywords' in result:
                    paper.keywords = result['keywords']
                if 'research_areas' in result:
                    paper.research_areas = result['research_areas']
                if 'relevance_score' in result:
                    paper.relevance_score = result['relevance_score']
                paper.processing_status = 'completed'
                paper.save()
                
                logger.info(f"Paper analysis completed for task {task_id}")
                return result
            else:
                raise Exception(f"FastAPI service error: {response.status_code}")
                
    except Exception as exc:
        logger.error(f"Paper analysis failed for task {task_id}: {exc}")
        
        # Update task status
        try:
            task = AIAnalysisTask.objects.get(id=task_id)
            task.status = 'failed'
            task.error_message = str(exc)
            task.save()
        except:
            pass
        
        # Retry the task
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying paper analysis task {task_id}")
            raise self.retry(countdown=60, exc=exc)
        else:
            logger.error(f"Paper analysis task {task_id} failed after all retries")
            raise exc


@shared_task
def generate_literature_review_task(project_id, parameters):
    """
    Task to generate literature review for a project.
    """
    try:
        from .models import ResearchProject, AIAnalysisTask
        
        project = ResearchProject.objects.get(id=project_id)
        
        # Create analysis task
        task = AIAnalysisTask.objects.create(
            project=project,
            task_type='literature_review',
            parameters=parameters,
            status='processing'
        )
        
        # Send to FastAPI service
        with httpx.Client() as client:
            response = client.post(
                f"{settings.FASTAPI_SERVICE_URL}/api/agents/generate-review",
                json={
                    'project_id': str(project_id),
                    'parameters': parameters,
                    'papers': list(project.papers.values(
                        'id', 'title', 'abstract', 'authors', 'doi'
                    ))
                },
                timeout=300.0  # 5 minutes for literature review
            )
            
            if response.status_code == 200:
                result = response.json()
                task.results = result
                task.status = 'completed'
                task.save()
                
                logger.info(f"Literature review generated for project {project_id}")
                return result
            else:
                raise Exception(f"FastAPI service error: {response.status_code}")
                
    except Exception as exc:
        logger.error(f"Literature review generation failed: {exc}")
        task.status = 'failed'
        task.error_message = str(exc)
        task.save()
        raise exc


@shared_task
def health_check_services():
    """
    Periodic task to check health of external services.
    """
    from .models import ServiceIntegration
    from django.utils import timezone
    
    services = ServiceIntegration.objects.filter(is_active=True)
    
    for service in services:
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{service.service_url}/health",
                    timeout=10.0
                )
                
                service.is_healthy = response.status_code == 200
                service.last_health_check = timezone.now()
                
                if not service.is_healthy:
                    logger.warning(f"Service {service.service_name} is unhealthy")
                
        except Exception as e:
            service.is_healthy = False
            service.last_health_check = timezone.now()
            logger.error(f"Health check failed for {service.service_name}: {e}")
        
        service.save()
    
    logger.info("Service health check completed")
