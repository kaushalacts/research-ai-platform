from django.shortcuts import render

# Create your views here.
"""API Views for core functionality."""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Q
from .models import ResearchProject, ResearchPaper, AIAnalysisTask
from .serializers import (
    ResearchProjectSerializer, ResearchPaperSerializer, AIAnalysisTaskSerializer
)
from .services import FastAPIService
import logging

logger = logging.getLogger(__name__)


class ResearchProjectViewSet(viewsets.ModelViewSet):
    """ViewSet for research project management."""
    
    serializer_class = ResearchProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'research_area']
    search_fields = ['title', 'description']
    ordering = ['-updated_at']
    
    def get_queryset(self):
        """Return user's projects."""
        return ResearchProject.objects.filter(owner=self.request.user)
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get project analytics."""
        project = self.get_object()
        
        analytics = {
            'paper_count': project.papers.count(),
            'task_count': project.ai_tasks.count(),
            'completed_tasks': project.ai_tasks.filter(status='completed').count(),
            'recent_papers': project.papers.order_by('-created_at')[:5].values(
                'title', 'created_at', 'processing_status'
            ),
        }
        
        return Response(analytics)


class ResearchPaperViewSet(viewsets.ModelViewSet):
    """ViewSet for research paper management."""
    
    serializer_class = ResearchPaperSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['processing_status', 'project']
    search_fields = ['title', 'authors', 'abstract']
    
    def get_queryset(self):
        """Return papers from user's projects."""
        return ResearchPaper.objects.filter(project__owner=self.request.user)
    
    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        """Request AI analysis for paper."""
        paper = self.get_object()
        
        # Create analysis task
        task = AIAnalysisTask.objects.create(
            project=paper.project,
            requested_by=request.user,
            task_type='paper_analysis',
            parameters=request.data.get('parameters', {})
        )
        task.papers.add(paper)
        
        # Send to FastAPI service
        try:
            fastapi_service = FastAPIService()
            task_id = fastapi_service.analyze_paper(task.id, paper.id)
            task.fastapi_task_id = task_id
            task.status = 'processing'
            task.save()
            
            logger.info(f"Analysis task {task.id} sent to FastAPI service")
            
            return Response({
                'message': 'Analysis started',
                'task_id': str(task.id)
            })
        except Exception as e:
            task.status = 'failed'
            task.error_message = str(e)
            task.save()
            
            logger.error(f"Failed to start analysis: {e}")
            
            return Response({
                'error': 'Failed to start analysis'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AIAnalysisTaskViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for AI analysis task monitoring."""
    
    serializer_class = AIAnalysisTaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'task_type']
    
    def get_queryset(self):
        """Return user's analysis tasks."""
        return AIAnalysisTask.objects.filter(requested_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel running analysis task."""
        task = self.get_object()
        
        if task.status in ['queued', 'processing']:
            try:
                # Cancel in FastAPI service
                fastapi_service = FastAPIService()
                fastapi_service.cancel_task(task.fastapi_task_id)
                
                task.status = 'failed'
                task.error_message = 'Cancelled by user'
                task.save()
                
                return Response({'message': 'Task cancelled'})
            except Exception as e:
                logger.error(f"Failed to cancel task: {e}")
                return Response({
                    'error': 'Failed to cancel task'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({
                'error': 'Cannot cancel task in current state'
            }, status=status.HTTP_400_BAD_REQUEST)
