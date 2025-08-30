"""
Celery configuration for async task processing with AI agents.
"""
import os
from celery import Celery

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_core.settings')

app = Celery('research_ai_platform')

# Load config from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery."""
    print(f'Request: {self.request!r}')


# Task routing for different AI services
app.conf.task_routes = {
    'core.tasks.analyze_paper': {'queue': 'paper_processing'},
    'core.tasks.generate_literature_review': {'queue': 'literature_review'},
    'core.tasks.agent_communication': {'queue': 'agent_processing'},
}

print("🔄 Celery configured for Research AI Platform")
