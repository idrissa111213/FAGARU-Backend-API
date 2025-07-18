from rest_framework import serializers
from .models import WeatherData
from core.models import SenegalCity

class WeatherDataSerializer(serializers.ModelSerializer):
    """Serializer pour les données météorologiques"""
    alert_color = serializers.SerializerMethodField()
    alert_level_display = serializers.CharField(source='get_alert_level_display', read_only=True)
    
    class Meta:
        model = WeatherData
        fields = [
            'id', 'city', 'latitude', 'longitude', 'temperature', 'temp_max',
            'temp_min', 'feels_like', 'humidity', 'alert_level', 
            'alert_level_display', 'alert_color', 'source', 'recorded_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_alert_color(self, obj):
        return obj.get_alert_color()

class CurrentWeatherSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour la météo actuelle"""
    alert_color = serializers.SerializerMethodField()
    
    class Meta:
        model = WeatherData
        fields = [
            'city', 'temperature', 'feels_like', 'alert_level', 'alert_color', 'recorded_at'
        ]
    
    def get_alert_color(self, obj):
        return obj.get_alert_color()

class WeatherForecastSerializer(serializers.Serializer):
    """Serializer pour les prévisions météo (données externes)"""
    city = serializers.CharField()
    date = serializers.DateTimeField()
    temp_max = serializers.FloatField()
    temp_min = serializers.FloatField()
    description = serializers.CharField()
    alert_level = serializers.CharField()
    alert_color = serializers.CharField()

class SenegalCitySerializer(serializers.ModelSerializer):
    """Serializer pour les villes du Sénégal"""
    current_weather = serializers.SerializerMethodField()
    
    class Meta:
        model = SenegalCity
        fields = ['id', 'name', 'region', 'latitude', 'longitude', 'is_priority', 'current_weather']
    
    def get_current_weather(self, obj):
        # Récupérer la météo la plus récente pour cette ville
        try:
            latest_weather = WeatherData.objects.filter(city=obj.name).latest('recorded_at')
            return CurrentWeatherSerializer(latest_weather).data
        except WeatherData.DoesNotExist:
            return None

class WeatherAlertSerializer(serializers.Serializer):
    """Serializer pour les alertes météo basées sur la température"""
    city = serializers.CharField()
    current_temp = serializers.FloatField()
    max_temp = serializers.FloatField()
    alert_level = serializers.CharField()
    alert_message = serializers.CharField()
    recommendations = serializers.ListField(child=serializers.CharField())
    
class WeatherStatsSerializer(serializers.Serializer):
    """Serializer pour les statistiques météo"""
    total_cities = serializers.IntegerField()
    cities_in_alert = serializers.IntegerField()
    highest_temp = serializers.FloatField()
    hottest_city = serializers.CharField()
    last_updated = serializers.DateTimeField()