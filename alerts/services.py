from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta
from .models import Alert, AlertNotification, Recommendation
from weather.models import WeatherData
from users.models import UserProfile
import logging

logger = logging.getLogger(__name__)

class AlertService:
    """Service pour gérer les alertes automatiques"""
    
    def __init__(self):
        # Seuils de température pour le Sénégal
        self.temperature_thresholds = {
            'yellow': 35,  # Très inconfortable
            'orange': 40,  # Dangereux  
            'red': 45      # Très dangereux
        }
        
        # Messages d'alerte par niveau
        self.alert_messages = {
            'yellow': {
                'title': 'Vigilance Jaune - Forte Chaleur',
                'message': 'Températures élevées prévues. Restez hydraté et évitez l\'exposition prolongée au soleil.'
            },
            'orange': {
                'title': 'Vigilance Orange - Danger Chaleur',
                'message': 'Danger de vague de chaleur. Limitez les sorties aux heures les plus chaudes. Surveillez les personnes vulnérables.'
            },
            'red': {
                'title': 'Vigilance Rouge - Danger Extrême',
                'message': 'Danger extrême de canicule. Évitez absolument les sorties. Restez dans un endroit frais. Consultez un médecin en cas de malaise.'
            }
        }

    def generate_weather_alerts(self, cities_list=None):
        """
        Générer des alertes automatiques basées sur les données météo récentes
        """
        generated_alerts = []
        now = timezone.now()
        
        # Récupérer les données météo récentes (dernières 2 heures)
        recent_weather = WeatherData.objects.filter(
            recorded_at__gte=now - timedelta(hours=2)
        )
        
        if cities_list:
            recent_weather = recent_weather.filter(city__in=cities_list)
        
        # Grouper par ville et prendre la plus récente
        cities_weather = {}
        for weather in recent_weather:
            if weather.city not in cities_weather:
                cities_weather[weather.city] = weather
            elif weather.recorded_at > cities_weather[weather.city].recorded_at:
                cities_weather[weather.city] = weather
        
        # Générer les alertes pour chaque ville
        for city, weather_data in cities_weather.items():
            alert = self._create_alert_if_needed(weather_data)
            if alert:
                generated_alerts.append(alert)
        
        return generated_alerts

    def _create_alert_if_needed(self, weather_data):
        """
        Créer une alerte si les seuils sont dépassés et qu'aucune alerte similaire n'existe
        """
        temp_max = weather_data.temp_max
        alert_level = self._determine_alert_level(temp_max)
        
        if alert_level == 'green':
            return None  # Pas d'alerte nécessaire
        
        # Vérifier s'il existe déjà une alerte active similaire
        existing_alert = Alert.objects.filter(
            severity=alert_level,
            affected_cities__icontains=weather_data.city,
            is_active=True,
            start_time__date=timezone.now().date()
        ).first()
        
        if existing_alert:
            logger.info(f"Alerte {alert_level} déjà active pour {weather_data.city}")
            return None
        
        # Créer la nouvelle alerte
        alert_info = self.alert_messages[alert_level]
        
        alert = Alert.objects.create(
            title=f"{alert_info['title']} - {weather_data.city}",
            message=f"{alert_info['message']} Température maximale prévue: {temp_max}°C",
            alert_type='heat_wave',
            severity=alert_level,
            affected_cities=[weather_data.city],
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=24),  # Alerte valable 24h
            is_active=True
        )
        
        logger.info(f"✅ Alerte {alert_level} créée pour {weather_data.city} ({temp_max}°C)")
        
        # Programmer l'envoi de notifications
        self._schedule_notifications(alert)
        
        return alert

    def _determine_alert_level(self, temperature):
        """Déterminer le niveau d'alerte basé sur la température"""
        if temperature >= self.temperature_thresholds['red']:
            return 'red'
        elif temperature >= self.temperature_thresholds['orange']:
            return 'orange'
        elif temperature >= self.temperature_thresholds['yellow']:
            return 'yellow'
        else:
            return 'green'

    def _schedule_notifications(self, alert):
        """
        Programmer l'envoi de notifications pour une alerte
        """
        try:
            # Pour le MVP, envoi synchrone direct
            self.send_alert_notifications_sync(alert)
            logger.info(f"Notifications envoyées pour l'alerte {alert.id}")
        except Exception as e:
            logger.error(f"Erreur programmation notifications: {e}")

    def send_alert_notifications_sync(self, alert):
        """
        Envoyer les notifications de manière synchrone
        """
        # Récupérer les utilisateurs concernés par cette alerte
        affected_users = self._get_affected_users(alert)
        
        notifications_sent = 0
        for user in affected_users:
            try:
                # Créer l'enregistrement de notification
                notification = AlertNotification.objects.create(
                    alert=alert,
                    user=user,
                    sent_via='push',  # Type par défaut
                    is_read=False
                )
                
                # Pour le MVP, on simule l'envoi
                logger.info(f"📱 Notification simulée pour {user.username}")
                notifications_sent += 1
                
            except Exception as e:
                logger.error(f"Erreur envoi notification user {user.id}: {e}")
        
        logger.info(f"📱 {notifications_sent} notifications envoyées pour l'alerte {alert.id}")
        return notifications_sent

    def _get_affected_users(self, alert):
        """
        Récupérer les utilisateurs affectés par une alerte
        """
        affected_users = []
        
        for city in alert.affected_cities:
            # Utilisateurs dans la ville concernée
            try:
                city_users = UserProfile.objects.filter(
                    city__icontains=city,
                    receive_push=True
                ).select_related('user')
                
                affected_users.extend([profile.user for profile in city_users])
            except Exception as e:
                logger.error(f"Erreur récupération users pour {city}: {e}")
        
        # Supprimer les doublons
        return list(set(affected_users))

    def deactivate_expired_alerts(self):
        """
        Désactiver les alertes expirées
        """
        now = timezone.now()
        expired_alerts = Alert.objects.filter(
            is_active=True,
            end_time__lt=now
        )
        
        count = expired_alerts.count()
        expired_alerts.update(is_active=False)
        
        logger.info(f"🔄 {count} alertes expirées désactivées")
        return count

    def get_personalized_recommendations(self, user, alert_level):
        """
        Récupérer les recommandations personnalisées pour un utilisateur
        """
        try:
            profile = user.profile
            profile_type = profile.profile_type
            language = profile.language
        except:
            profile_type = 'general'
            language = 'fr'
        
        recommendations = Recommendation.objects.filter(
            profile_type=profile_type,
            alert_level=alert_level,
            language=language,
            is_active=True
        ).order_by('order')
        
        return recommendations

    def get_active_alerts_for_city(self, city_name):
        """
        Récupérer les alertes actives pour une ville
        """
        now = timezone.now()
        return Alert.objects.filter(
            affected_cities__icontains=city_name,
            is_active=True,
            start_time__lte=now
        ).filter(
            Q(end_time__isnull=True) | Q(end_time__gte=now)
        ).order_by('-created_at')

    def get_alerts_statistics(self):
        """
        Récupérer les statistiques des alertes
        """
        now = timezone.now()
        today = now.date()
        
        stats = {
            'total_alerts_today': Alert.objects.filter(created_at__date=today).count(),
            'active_alerts': Alert.objects.filter(is_active=True).count(),
            'red_alerts': Alert.objects.filter(severity='red', is_active=True).count(),
            'orange_alerts': Alert.objects.filter(severity='orange', is_active=True).count(),
            'yellow_alerts': Alert.objects.filter(severity='yellow', is_active=True).count(),
            'total_notifications': AlertNotification.objects.filter(sent_at__date=today).count(),
        }
        
        return stats

# Instance globale du service
alert_service = AlertService()