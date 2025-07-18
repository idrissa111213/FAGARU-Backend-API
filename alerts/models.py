from django.db import models
from django.contrib.auth.models import User

class Alert(models.Model):
    """Alertes de vagues de chaleur"""
    ALERT_TYPES = [
        ('heat_wave', 'Vague de chaleur'),
        ('extreme_heat', 'Chaleur extrême'),
        ('health_warning', 'Alerte sanitaire'),
    ]
    
    SEVERITY_LEVELS = [
        ('yellow', 'Vigilance jaune'),
        ('orange', 'Vigilance orange'),
        ('red', 'Vigilance rouge'),
    ]
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    affected_cities = models.JSONField(default=list)  # Liste des villes concernées
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.severity})"

class AlertNotification(models.Model):
    """Notifications d'alertes envoyées aux utilisateurs"""
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sent_via = models.CharField(max_length=20, choices=[
        ('push', 'Notification push'),
        ('sms', 'SMS'),
        ('email', 'Email'),
    ])
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Alert {self.alert.title} -> {self.user.username}"

class Recommendation(models.Model):
    """Recommandations personnalisées selon les profils"""
    profile_type = models.CharField(max_length=20, choices=[
        ('general', 'Population générale'),
        ('elderly', 'Personne âgée'),
        ('pregnant', 'Femme enceinte'),
        ('child', 'Enfant'),
        ('chronic', 'Malade chronique'),
        ('outdoor_worker', 'Travailleur extérieur'),
    ])
    alert_level = models.CharField(max_length=10, choices=[
        ('yellow', 'Jaune'),
        ('orange', 'Orange'),
        ('red', 'Rouge'),
    ])
    title = models.CharField(max_length=200)
    content = models.TextField()
    icon = models.CharField(max_length=50, blank=True)  # Nom de l'icône
    language = models.CharField(max_length=10, default='fr')
    order = models.IntegerField(default=0)  # Pour l'ordre d'affichage
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return f"{self.title} ({self.profile_type} - {self.alert_level})"

class CommunityReport(models.Model):
    """Signalements participatifs des citoyens"""
    SYMPTOM_CHOICES = [
        ('dehydration', 'Déshydratation'),
        ('heat_exhaustion', 'Épuisement thermique'),
        ('heat_stroke', 'Coup de chaleur'),
        ('breathing_issues', 'Difficultés respiratoires'),
        ('other', 'Autre'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    city = models.CharField(max_length=100)
    symptoms = models.CharField(max_length=50, choices=SYMPTOM_CHOICES)
    description = models.TextField(blank=True)
    temperature_felt = models.FloatField(help_text="Température ressentie")
    has_shade = models.BooleanField(default=False)
    has_water_access = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Signalement {self.city} - {self.get_symptoms_display()}"