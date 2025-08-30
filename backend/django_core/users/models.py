"""
Custom User models for the Research AI Platform.
Designed to integrate with FastAPI services and AI agents.
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
import uuid


class ResearchUserManager(BaseUserManager):
    """Custom manager for ResearchUser model."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user."""
        if not email:
            raise ValueError('Users must have an email address')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class ResearchUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model for research platform.
    Integrates with AI agents and FastAPI services.
    """
    
    # Core identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, max_length=255, db_index=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    
    # Research-specific fields
    institution = models.CharField(max_length=200, blank=True)
    department = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=100, blank=True, 
                           help_text="Academic title (e.g., Professor, PhD Student)")
    research_interests = models.TextField(blank=True, 
                                        help_text="Areas of research interest")
    orcid = models.CharField(
        max_length=20, 
        blank=True, 
        validators=[RegexValidator(r'^\d{4}-\d{4}-\d{4}-\d{3}[0-9X]$')],
        help_text="ORCID identifier"
    )
    bio = models.TextField(max_length=500, blank=True)
    website = models.URLField(blank=True)
    
    # Status and permissions
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    # API usage and subscription
    subscription_type = models.CharField(
        max_length=20,
        choices=[
            ('free', 'Free'),
            ('premium', 'Premium'),
            ('institutional', 'Institutional'),
        ],
        default='free'
    )
    monthly_api_calls = models.PositiveIntegerField(default=0)
    api_limit = models.PositiveIntegerField(default=1000)
    
    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    
    # Profile completion
    profile_completion = models.PositiveSmallIntegerField(default=0)
    
    objects = ResearchUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        db_table = 'research_users'
        verbose_name = 'Research User'
        verbose_name_plural = 'Research Users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['institution']),
            models.Index(fields=['date_joined']),
        ]
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """Return full name."""
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        """Return short name."""
        return self.first_name or self.email.split('@')[0]
    
    def update_profile_completion(self):
        """Calculate and update profile completion percentage."""
        fields_to_check = [
            'first_name', 'last_name', 'institution', 'department', 
            'title', 'research_interests', 'bio'
        ]
        completed_fields = sum(1 for field in fields_to_check if getattr(self, field))
        self.profile_completion = int((completed_fields / len(fields_to_check)) * 100)
        self.save(update_fields=['profile_completion'])
    
    def can_make_api_call(self):
        """Check if user can make an API call."""
        return self.monthly_api_calls < self.api_limit
    
    def increment_api_calls(self):
        """Increment API call count."""
        self.monthly_api_calls += 1
        self.save(update_fields=['monthly_api_calls'])


class ResearchProfile(models.Model):
    """Extended profile for research users."""
    
    user = models.OneToOneField(ResearchUser, on_delete=models.CASCADE, related_name='profile')
    
    # Research metrics
    h_index = models.PositiveIntegerField(null=True, blank=True)
    citation_count = models.PositiveIntegerField(default=0)
    publication_count = models.PositiveIntegerField(default=0)
    
    # AI agent preferences
    preferred_research_areas = models.JSONField(default=list, blank=True)
    ai_agent_preferences = models.JSONField(default=dict, blank=True)
    notification_preferences = models.JSONField(default=dict, blank=True)
    
    # Privacy settings
    profile_visibility = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public'),
            ('institution', 'Institution Only'),
            ('private', 'Private'),
        ],
        default='public'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'research_profiles'
    
    def __str__(self):
        return f"Profile for {self.user.get_full_name()}"
