from django.db import models

class AppSettings(models.Model):
    """Configuration globale de l'application"""
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.CharField(max_length=200, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.key}: {self.value}"

class SenegalCity(models.Model):
    """Villes du Sénégal avec coordonnées"""
    name = models.CharField(max_length=100, unique=True)
    region = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    is_priority = models.BooleanField(default=False)  # Villes prioritaires (Matam, Podor, etc.)
    
    class Meta:
        verbose_name_plural = "Senegal Cities"
    
    def __str__(self):
        return f"{self.name} ({self.region})"