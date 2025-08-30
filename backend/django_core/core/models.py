"""
Core models for Research AI Platform.
Designed to communicate with FastAPI services and AI agents.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class ResearchProject(models.Model):
    """Model for research projects that integrate with AI agents."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    
    # Project details
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    research_area = models.CharField(max_length=100, blank=True)
    keywords = models.JSONField(default=list, blank=True)
    
    # Status management
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('completed', 'Completed'),
            ('archived', 'Archived'),
            ('draft', 'Draft'),
        ],
        default='draft'
    )
    
    # AI integration settings
    ai_analysis_enabled = models.BooleanField(default=True)
    auto_discovery_enabled = models.BooleanField(default=False)
    preferred_databases = models.JSONField(default=list, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'research_projects'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['owner', 'status']),
            models.Index(fields=['research_area']),
        ]
    
    def __str__(self):
        return self.title


class ResearchPaper(models.Model):
    """Model for academic papers with AI processing capabilities."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(ResearchProject, on_delete=models.CASCADE, related_name='papers')
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Paper identification
    title = models.CharField(max_length=500)
    authors = models.JSONField(default=list)
    abstract = models.TextField(blank=True)
    doi = models.CharField(max_length=100, blank=True, db_index=True)
    arxiv_id = models.CharField(max_length=50, blank=True, db_index=True)
    
    # Publication details
    journal = models.CharField(max_length=200, blank=True)
    publication_date = models.DateField(null=True, blank=True)
    
    # URLs and files
    pdf_url = models.URLField(blank=True)
    source_url = models.URLField(blank=True)
    
    # AI analysis results
    research_areas = models.JSONField(default=list, blank=True)
    keywords = models.JSONField(default=list, blank=True)
    citation_count = models.PositiveIntegerField(default=0)
    relevance_score = models.FloatField(null=True, blank=True)
    
    # Processing status for AI agents
    processing_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'research_papers'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['doi']),
            models.Index(fields=['arxiv_id']),
            models.Index(fields=['project', 'processing_status']),
        ]
    
    def __str__(self):
        return self.title[:100]


class AIAnalysisTask(models.Model):
    """Model for tracking AI analysis tasks sent to FastAPI services."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(ResearchProject, on_delete=models.CASCADE, related_name='ai_tasks')
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Task configuration
    task_type = models.CharField(
        max_length=30,
        choices=[
            ('literature_review', 'Literature Review'),
            ('trend_analysis', 'Trend Analysis'),
            ('gap_analysis', 'Gap Analysis'),
            ('paper_analysis', 'Paper Analysis'),
        ]
    )
    
    parameters = models.JSONField(default=dict)
    papers = models.ManyToManyField(ResearchPaper, blank=True)
    
    # Processing status
    status = models.CharField(
        max_length=20,
        choices=[
            ('queued', 'Queued'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='queued'
    )
    
    # Results from AI agents
    results = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)
    
    # Service tracking
    fastapi_task_id = models.CharField(max_length=100, blank=True, 
                                     help_text="Task ID from FastAPI service")
    agent_used = models.CharField(max_length=50, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'ai_analysis_tasks'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['task_type']),
        ]
    
    def __str__(self):
        return f"{self.get_task_type_display()} for {self.project.title}"
    
    def mark_completed(self):
        """Mark task as completed."""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])


class ServiceIntegration(models.Model):
    """Model for tracking integration with external services."""
    
    service_name = models.CharField(max_length=50, unique=True)
    service_url = models.URLField()
    is_active = models.BooleanField(default=True)
    api_key = models.CharField(max_length=200, blank=True)
    
    # Health check
    last_health_check = models.DateTimeField(null=True, blank=True)
    is_healthy = models.BooleanField(default=True)
    
    # Usage statistics
    total_requests = models.PositiveIntegerField(default=0)
    failed_requests = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'service_integrations'
    
    def __str__(self):
        return f"{self.service_name} ({'Active' if self.is_active else 'Inactive'})"
