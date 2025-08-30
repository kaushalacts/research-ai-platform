"""
Signal handlers for the core app.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ResearchProject, AIAnalysisTask
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=ResearchProject)
def project_created(sender, instance, created, **kwargs):
    """Handle project creation."""
    if created:
        logger.info(f"New research project created: {instance.title} by {instance.owner.email}")


@receiver(post_save, sender=AIAnalysisTask)
def analysis_task_created(sender, instance, created, **kwargs):
    """Handle analysis task creation."""
    if created:
        logger.info(f"New AI analysis task created: {instance.task_type} for project {instance.project.title}")
