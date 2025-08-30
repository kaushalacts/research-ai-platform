"""Signal handlers for user-related events."""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ResearchUser, ResearchProfile


@receiver(post_save, sender=ResearchUser)
def create_research_profile(sender, instance, created, **kwargs):
    """Create ResearchProfile when ResearchUser is created."""
    if created:
        ResearchProfile.objects.create(user=instance)


@receiver(post_save, sender=ResearchUser)
def save_research_profile(sender, instance, **kwargs):
    """Save ResearchProfile when ResearchUser is saved."""
    if hasattr(instance, 'profile'):
        instance.profile.save()
