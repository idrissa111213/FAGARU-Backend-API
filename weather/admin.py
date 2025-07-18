from django.contrib import admin
from .models import WeatherData

@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ['city', 'temperature', 'alert_level', 'feels_like', 'humidity', 'recorded_at']
    list_filter = ['alert_level', 'city', 'recorded_at']
    search_fields = ['city']
    ordering = ['-recorded_at']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()