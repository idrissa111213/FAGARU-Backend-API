from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q, Max
from datetime import datetime, timedelta
from .models import WeatherData
from core.models import SenegalCity
from .serializers import (
    WeatherDataSerializer, CurrentWeatherSerializer, SenegalCitySerializer,
    WeatherAlertSerializer, WeatherStatsSerializer
)
from .services import weather_service

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def current_weather(request):
    """Météo actuelle pour toutes les villes prioritaires"""
    cities = SenegalCity.objects.filter(is_priority=True)
    serializer = SenegalCitySerializer(cities, many=True)
    
    return Response({
        'cities': serializer.data,
        'last_updated': timezone.now()
    })

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def weather_by_city(request, city_name):
    """Météo pour une ville spécifique"""
    try:
        # Récupérer la météo la plus récente pour cette ville
        latest_weather = WeatherData.objects.filter(
            city__iexact=city_name
        ).latest('recorded_at')
        
        serializer = WeatherDataSerializer(latest_weather)
        
        # Récupérer l'historique des 7 derniers jours
        week_ago = timezone.now() - timedelta(days=7)
        history = WeatherData.objects.filter(
            city__iexact=city_name,
            recorded_at__gte=week_ago
        ).order_by('-recorded_at')[:24]  # Dernières 24 entrées
        
        history_serializer = WeatherDataSerializer(history, many=True)
        
        return Response({
            'current': serializer.data,
            'history': history_serializer.data
        })
        
    except WeatherData.DoesNotExist:
        return Response({
            'error': f'Aucune donnée météo trouvée pour {city_name}'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def weather_alerts(request):
    """Alertes météo basées sur les températures"""
    # Définir les seuils de température
    TEMP_THRESHOLDS = {
        'yellow': 35,  # Très inconfortable
        'orange': 40,  # Dangereux
        'red': 45      # Très dangereux
    }
    
    # Récupérer les dernières données météo par ville
    latest_weather = WeatherData.objects.values('city').annotate(
        latest_time=Max('recorded_at')
    )
    
    alerts = []
    for item in latest_weather:
        try:
            weather = WeatherData.objects.get(
                city=item['city'],
                recorded_at=item['latest_time']
            )
            
            # Déterminer le niveau d'alerte
            max_temp = weather.temp_max
            alert_level = 'green'
            alert_message = 'Conditions normales'
            
            if max_temp >= TEMP_THRESHOLDS['red']:
                alert_level = 'red'
                alert_message = 'Danger extrême - Évitez toute exposition'
            elif max_temp >= TEMP_THRESHOLDS['orange']:
                alert_level = 'orange'
                alert_message = 'Danger élevé - Limitez les sorties'
            elif max_temp >= TEMP_THRESHOLDS['yellow']:
                alert_level = 'yellow'
                alert_message = 'Vigilance requise - Restez hydraté'
            
            if alert_level != 'green':
                alerts.append({
                    'city': weather.city,
                    'current_temp': weather.temperature,
                    'max_temp': max_temp,
                    'alert_level': alert_level,
                    'alert_message': alert_message,
                    'recommendations': get_weather_recommendations(alert_level)
                })
                
        except WeatherData.DoesNotExist:
            continue
    
    # Trier par niveau de danger (rouge > orange > jaune)
    severity_order = {'red': 3, 'orange': 2, 'yellow': 1}
    alerts.sort(key=lambda x: severity_order.get(x['alert_level'], 0), reverse=True)
    
    return Response({
        'alerts': alerts,
        'total_cities_in_alert': len(alerts),
        'last_updated': timezone.now()
    })

def get_weather_recommendations(alert_level):
    """Récupérer les recommandations selon le niveau d'alerte"""
    recommendations = {
        'yellow': [
            'Buvez de l\'eau régulièrement',
            'Portez des vêtements légers',
            'Évitez l\'exposition directe au soleil'
        ],
        'orange': [
            'Restez à l\'intérieur aux heures chaudes',
            'Hydratez-vous toutes les 15 minutes',
            'Portez un chapeau si vous sortez',
            'Surveillez les signes de déshydratation'
        ],
        'red': [
            'Évitez absolument de sortir',
            'Restez dans un endroit climatisé',
            'Hydratation constante nécessaire',
            'Consultez un médecin en cas de malaise',
            'Surveillez les personnes vulnérables'
        ]
    }
    return recommendations.get(alert_level, [])

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def weather_stats(request):
    """Statistiques météorologiques globales"""
    now = timezone.now()
    today = now.date()
    
    # Données d'aujourd'hui
    today_data = WeatherData.objects.filter(
        recorded_at__date=today
    )
    
    if not today_data.exists():
        return Response({
            'error': 'Aucune donnée météo disponible pour aujourd\'hui'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Trouver la température la plus élevée
    hottest = today_data.order_by('-temp_max').first()
    
    # Compter les villes en alerte
    cities_in_alert = today_data.exclude(alert_level='green').values('city').distinct().count()
    
    stats = {
        'total_cities': today_data.values('city').distinct().count(),
        'cities_in_alert': cities_in_alert,
        'highest_temp': hottest.temp_max if hottest else 0,
        'hottest_city': hottest.city if hottest else '',
        'last_updated': today_data.latest('recorded_at').recorded_at
    }
    
    serializer = WeatherStatsSerializer(stats)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def cities_list(request):
    """Liste des villes du Sénégal avec météo"""
    cities = SenegalCity.objects.all().order_by('name')
    
    # Filtrer par région si spécifiée
    region = request.query_params.get('region')
    if region:
        cities = cities.filter(region__icontains=region)
    
    # Prioritaires uniquement
    priority_only = request.query_params.get('priority')
    if priority_only == 'true':
        cities = cities.filter(is_priority=True)
    
    serializer = SenegalCitySerializer(cities, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def weather_history(request, city_name):
    """Historique météo pour une ville (7 derniers jours)"""
    days = int(request.query_params.get('days', 7))
    start_date = timezone.now() - timedelta(days=days)
    
    history = WeatherData.objects.filter(
        city__iexact=city_name,
        recorded_at__gte=start_date
    ).order_by('recorded_at')
    
    if not history.exists():
        return Response({
            'error': f'Aucun historique trouvé pour {city_name}'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = WeatherDataSerializer(history, many=True)
    return Response({
        'city': city_name,
        'period_days': days,
        'data_points': history.count(),
        'history': serializer.data
    })

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def update_weather_data(request):
    """Mettre à jour les données météo pour toutes les villes"""
    try:
        result = weather_service.update_weather_for_all_cities()
        return Response({
            'message': 'Mise à jour météo terminée',
            'updated_cities': result['updated_cities'],
            'errors': result['errors'],
            'total_updated': result['total_updated']
        })
    except Exception as e:
        return Response({
            'error': f'Erreur lors de la mise à jour: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def test_weather_api(request):
    """Tester l'API météo pour une ville"""
    city = request.query_params.get('city', 'Dakar')
    
    try:
        weather_data = weather_service.get_current_weather(city)
        if weather_data:
            return Response({
                'success': True,
                'city': city,
                'weather': weather_data
            })
        else:
            return Response({
                'error': f'Impossible de récupérer la météo pour {city}'
            }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class WeatherDataListView(generics.ListAPIView):
    """Vue générique pour lister les données météo"""
    serializer_class = WeatherDataSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = WeatherData.objects.all()
        city = self.request.query_params.get('city')
        alert_level = self.request.query_params.get('alert_level')
        
        if city:
            queryset = queryset.filter(city__icontains=city)
        if alert_level:
            queryset = queryset.filter(alert_level=alert_level)
            
        return queryset.order_by('-recorded_at')