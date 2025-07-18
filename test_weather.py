#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fagaru_project.settings')
django.setup()

def test_multiple_cities():
    import requests
    from django.conf import settings
    from weather.models import WeatherData
    from django.utils import timezone
    
    api_key = settings.OPENWEATHER_API_KEY
    cities = {
        'Dakar': {'lat': 14.6928, 'lon': -17.4467},
        'Saint-Louis': {'lat': 16.0366, 'lon': -16.4894},
        'Thiès': {'lat': 14.7886, 'lon': -16.9263},
        'Kaolack': {'lat': 14.1515, 'lon': -16.0721},
    }
    
    print(f"🌡️ Récupération des données météo pour {len(cities)} villes...")
    
    for city_name, coords in cities.items():
        try:
            url = "https://api.openweathermap.org/data/2.5/weather"
            params = {
                'lat': coords['lat'],
                'lon': coords['lon'],
                'appid': api_key,
                'units': 'metric',
                'lang': 'fr'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            
            # Calculer le niveau d'alerte
            if feels_like >= 45 or temp >= 42:
                alert_level = 'red'
            elif feels_like >= 40 or temp >= 38:
                alert_level = 'orange'
            elif feels_like >= 35 or temp >= 35:
                alert_level = 'yellow'
            else:
                alert_level = 'green'
            
            # Sauvegarder en base
            weather_obj, created = WeatherData.objects.update_or_create(
                city=city_name,
                recorded_at__date=timezone.now().date(),
                defaults={
                    'city': city_name,
                    'latitude': coords['lat'],
                    'longitude': coords['lon'],
                    'temperature': temp,
                    'temp_max': data['main']['temp_max'],
                    'temp_min': data['main']['temp_min'],
                    'feels_like': feels_like,
                    'humidity': data['main']['humidity'],
                    'alert_level': alert_level,
                    'recorded_at': timezone.now(),
                }
            )
            
            status = "✓ Créé" if created else "↻ Mis à jour"
            color_map = {'green': '🟢', 'yellow': '🟡', 'orange': '🟠', 'red': '🔴'}
            print(f"{status} {city_name}: {temp}°C {color_map.get(alert_level, '')} {alert_level}")
            
        except Exception as e:
            print(f"❌ Erreur pour {city_name}: {e}")

if __name__ == '__main__':
    test_multiple_cities()