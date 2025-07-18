from django.contrib import admin
from .models import Alert, AlertNotification, Recommendation

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['title', 'severity', 'alert_type', 'is_active', 'start_time', 'created_at']
    list_filter = ['severity', 'alert_type', 'is_active']
    search_fields = ['title', 'message']
    date_hierarchy = 'created_at'

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['title', 'profile_type', 'alert_level', 'language', 'order', 'is_active']
    list_filter = ['profile_type', 'alert_level', 'language', 'is_active']
    search_fields = ['title', 'content']
    ordering = ['profile_type', 'alert_level', 'order']

@admin.register(AlertNotification)
class AlertNotificationAdmin(admin.ModelAdmin):
    list_display = ['alert', 'user', 'sent_via', 'sent_at', 'is_read']
    list_filter = ['sent_via', 'is_read', 'sent_at']
    search_fields = ['user__username', 'alert__title']