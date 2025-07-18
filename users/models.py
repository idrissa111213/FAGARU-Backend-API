from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    """Profil utilisateur étendu"""
    PROFILE_CHOICES = [
        ('general', 'Population générale'),
        ('elderly', 'Personne âgée (+65 ans)'),
        ('pregnant', 'Femme enceinte'),
        ('child', 'Enfant (-12 ans)'),
        ('chronic', 'Malade chronique'),
        ('outdoor_worker', 'Travailleur extérieur'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_type = models.CharField(max_length=20, choices=PROFILE_CHOICES, default='general')
    location_lat = models.FloatField(blank=True, null=True)
    location_lng = models.FloatField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    receive_sms = models.BooleanField(default=True)
    receive_push = models.BooleanField(default=True)
    language = models.CharField(max_length=10, default='fr', choices=[
        ('fr', 'Français'),
        ('wo', 'Wolof'),
        ('ff', 'Pulaar'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_profile_type_display()})"