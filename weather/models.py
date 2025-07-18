from django.db import models

class WeatherData(models.Model):
    """Données météorologiques par ville"""
    ALERT_LEVELS = [
        ('green', 'Normal'),
        ('yellow', 'Très inconfortable'),
        ('orange', 'Dangereux'),
        ('red', 'Très dangereux'),
    ]
    
    city = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    temperature = models.FloatField()  # Température actuelle
    temp_max = models.FloatField()     # Température maximale
    temp_min = models.FloatField()     # Température minimale
    feels_like = models.FloatField()   # Ressenti
    humidity = models.FloatField()
    description = models.CharField(max_length=200, blank=True, default='')  # AJOUTÉ
    alert_level = models.CharField(max_length=10, choices=ALERT_LEVELS, default='green')
    source = models.CharField(max_length=50, default='openweathermap')  # anacim ou openweathermap
    recorded_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'weather'
        ordering = ['-recorded_at']
        unique_together = ['city', 'recorded_at']

    def __str__(self):
        return f"{self.city} - {self.temperature}°C ({self.alert_level})"

    def get_alert_color(self):
        """Retourne la couleur associée au niveau d'alerte"""
        colors = {
            'green': '#4CAF50',
            'yellow': '#FFC107',
            'orange': '#FF9800',
            'red': '#F44336'
        }
        return colors.get(self.alert_level, '#4CAF50')