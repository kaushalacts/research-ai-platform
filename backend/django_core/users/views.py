"""API Views for user management."""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db import transaction
from .models import ResearchUser, ResearchProfile
from .serializers import (
    ResearchUserSerializer, ResearchProfileSerializer, 
    UserRegistrationSerializer
)
import logging

logger = logging.getLogger(__name__)


class UserRegistrationView(generics.CreateAPIView):
    """API endpoint for user registration."""
    
    queryset = ResearchUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Create new user account."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        logger.info(f"New user registered: {user.email}")
        
        return Response({
            'user': ResearchUserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Account created successfully'
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """API endpoint for user login."""
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response({
            'error': 'Email and password required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(request, username=email, password=password)
    
    if user and user.is_active:
        refresh = RefreshToken.for_user(user)
        user.update_profile_completion()
        
        logger.info(f"User logged in: {user.email}")
        
        return Response({
            'user': ResearchUserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Login successful'
        })
    else:
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """API endpoint for user profile management."""
    
    serializer_class = ResearchUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        """Update user profile."""
        response = super().update(request, *args, **kwargs)
        if response.status_code == 200:
            request.user.update_profile_completion()
        return response


class ResearchProfileView(generics.RetrieveUpdateAPIView):
    """API endpoint for research profile management."""
    
    serializer_class = ResearchProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        profile, created = ResearchProfile.objects.get_or_create(user=self.request.user)
        return profile


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_stats(request):
    """Get user statistics for dashboard."""
    user = request.user
    
    stats = {
        'profile_completion': user.profile_completion,
        'api_calls_this_month': user.monthly_api_calls,
        'api_limit': user.api_limit,
        'subscription_type': user.subscription_type,
        'member_since': user.date_joined,
        'can_make_api_calls': user.can_make_api_call(),
    }
    
    return Response(stats)
