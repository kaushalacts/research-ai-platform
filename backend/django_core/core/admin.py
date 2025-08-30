"""Admin configuration for core app."""
from django.contrib import admin
from .models import ResearchProject, ResearchPaper, AIAnalysisTask, ServiceIntegration


@admin.register(ResearchProject)
class ResearchProjectAdmin(admin.ModelAdmin):
    """Admin interface for ResearchProject."""
    
    list_display = ('title', 'owner', 'status', 'research_area', 'created_at')
    list_filter = ('status', 'research_area', 'ai_analysis_enabled', 'created_at')
    search_fields = ('title', 'description', 'owner__email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {'fields': ('title', 'description', 'owner')}),
        ('Classification', {'fields': ('research_area', 'keywords', 'status')}),
        ('AI Settings', {'fields': ('ai_analysis_enabled', 'auto_discovery_enabled', 
                                   'preferred_databases')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(ResearchPaper)
class ResearchPaperAdmin(admin.ModelAdmin):
    """Admin interface for ResearchPaper."""
    
    list_display = ('title', 'project', 'journal', 'publication_date', 'processing_status')
    list_filter = ('processing_status', 'journal', 'publication_date', 'created_at')
    search_fields = ('title', 'authors', 'doi', 'arxiv_id')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(AIAnalysisTask)
class AIAnalysisTaskAdmin(admin.ModelAdmin):
    """Admin interface for AIAnalysisTask."""
    
    list_display = ('project', 'task_type', 'status', 'requested_by', 'created_at')
    list_filter = ('task_type', 'status', 'created_at')
    search_fields = ('project__title', 'requested_by__email')
    readonly_fields = ('created_at', 'updated_at', 'completed_at')


@admin.register(ServiceIntegration)
class ServiceIntegrationAdmin(admin.ModelAdmin):
    """Admin interface for ServiceIntegration."""
    
    list_display = ('service_name', 'service_url', 'is_active', 'is_healthy', 'last_health_check')
    list_filter = ('is_active', 'is_healthy')
    readonly_fields = ('last_health_check', 'total_requests', 'failed_requests', 
                      'created_at', 'updated_at')
