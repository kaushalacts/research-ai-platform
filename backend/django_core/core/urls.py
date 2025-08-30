"""URL configuration for core app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'core'

router = DefaultRouter()
router.register(r'projects', views.ResearchProjectViewSet, basename='projects')
router.register(r'papers', views.ResearchPaperViewSet, basename='papers')
router.register(r'tasks', views.AIAnalysisTaskViewSet, basename='tasks')

urlpatterns = [
    path('', include(router.urls)),
]
