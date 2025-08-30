"""Admin configuration for users app."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import ResearchUser, ResearchProfile


@admin.register(ResearchUser)
class ResearchUserAdmin(UserAdmin):
    """Admin interface for ResearchUser."""
    
    list_display = ('email', 'first_name', 'last_name', 'institution', 
                   'subscription_type', 'is_verified', 'date_joined')
    list_filter = ('subscription_type', 'is_verified', 'is_staff', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name', 'institution')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'bio')}),
        ('Research info', {'fields': ('institution', 'department', 'title', 
                                    'research_interests', 'orcid', 'website')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 
                                   'is_verified', 'groups', 'user_permissions')}),
        ('Subscription', {'fields': ('subscription_type', 'monthly_api_calls', 'api_limit')}),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'email_verified_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )


@admin.register(ResearchProfile)
class ResearchProfileAdmin(admin.ModelAdmin):
    """Admin interface for ResearchProfile."""
    
    list_display = ('user', 'h_index', 'citation_count', 'publication_count', 'profile_visibility')
    list_filter = ('profile_visibility', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at')
