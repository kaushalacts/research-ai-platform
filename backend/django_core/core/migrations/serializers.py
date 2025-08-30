"""Serializers for user management."""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import ResearchUser, ResearchProfile


class ResearchUserSerializer(serializers.ModelSerializer):
    """Serializer for ResearchUser model."""
    
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    short_name = serializers.CharField(source='get_short_name', read_only=True)
    can_make_api_calls = serializers.BooleanField(source='can_make_api_call', read_only=True)
    
    class Meta:
        model = ResearchUser
        fields = (
            'id', 'email', 'first_name', 'last_name', 'full_name', 'short_name',
            'institution', 'department', 'title', 'research_interests',
            'orcid', 'bio', 'website', 'subscription_type', 'profile_completion',
            'is_verified', 'monthly_api_calls', 'api_limit', 'can_make_api_calls',
            'date_joined', 'last_login'
        )
        read_only_fields = (
            'id', 'email', 'subscription_type', 'profile_completion',
            'is_verified', 'monthly_api_calls', 'api_limit',
            'date_joined', 'last_login'
        )


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = ResearchUser
        fields = (
            'email', 'first_name', 'last_name', 'password', 'password_confirm',
            'institution', 'department', 'title', 'research_interests'
        )
    
    def validate(self, data):
        """Validate password confirmation."""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        
        try:
            validate_password(data['password'])
        except DjangoValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})
        
        return data
    
    def create(self, validated_data):
        """Create user with validated data."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = ResearchUser.objects.create_user(
            password=password,
            **validated_data
        )
        
        return user


class ResearchProfileSerializer(serializers.ModelSerializer):
    """Serializer for ResearchProfile model."""
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = ResearchProfile
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')
