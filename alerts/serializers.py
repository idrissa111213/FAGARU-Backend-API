from rest_framework import serializers
from .models import Alert, AlertNotification, Recommendation, CommunityReport
from django.contrib.auth.models import User

class AlertSerializer(serializers.ModelSerializer):
    """Serializer pour les alertes"""
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    alert_type_display = serializers.CharField(source='get_alert_type_display', read_only=True)
    
    class Meta:
        model = Alert
        fields = [
            'id', 'title', 'message', 'alert_type', 'alert_type_display',
            'severity', 'severity_display', 'affected_cities', 'start_time',
            'end_time', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class AlertNotificationSerializer(serializers.ModelSerializer):
    """Serializer pour les notifications d'alertes"""
    alert_title = serializers.CharField(source='alert.title', read_only=True)
    alert_severity = serializers.CharField(source='alert.severity', read_only=True)
    
    class Meta:
        model = AlertNotification
        fields = [
            'id', 'alert', 'alert_title', 'alert_severity', 'sent_via',
            'sent_at', 'is_read'
        ]
        read_only_fields = ['id', 'sent_at']

class RecommendationSerializer(serializers.ModelSerializer):
    """Serializer pour les recommandations"""
    profile_type_display = serializers.CharField(source='get_profile_type_display', read_only=True)
    
    class Meta:
        model = Recommendation
        fields = [
            'id', 'profile_type', 'profile_type_display', 'alert_level',
            'title', 'content', 'icon', 'language', 'order', 'is_active'
        ]

class CommunityReportSerializer(serializers.ModelSerializer):
    """Serializer pour les signalements communautaires"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    symptoms_display = serializers.CharField(source='get_symptoms_display', read_only=True)
    
    class Meta:
        model = CommunityReport
        fields = [
            'id', 'user', 'user_name', 'latitude', 'longitude', 'city',
            'symptoms', 'symptoms_display', 'description', 'temperature_felt',
            'has_shade', 'has_water_access', 'is_verified', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'is_verified']

class CommunityReportCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer un signalement"""
    
    class Meta:
        model = CommunityReport
        fields = [
            'latitude', 'longitude', 'city', 'symptoms', 'description',
            'temperature_felt', 'has_shade', 'has_water_access'
        ]
    
    def create(self, validated_data):
        # Ajouter l'utilisateur depuis le contexte de la request
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class ActiveAlertsSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour les alertes actives"""
    
    class Meta:
        model = Alert
        fields = ['id', 'title', 'severity', 'affected_cities', 'start_time']
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Ajouter des informations utiles pour le frontend
        data['severity_color'] = {
            'yellow': '#FFC107',
            'orange': '#FF9800', 
            'red': '#F44336'
        }.get(instance.severity, '#4CAF50')
        return data