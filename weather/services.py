import requests
import os
from datetime import datetime
from django.utils import timezone
from django.conf import settings
from .models import WeatherData

class WeatherService:
    """Service pour récupérer et traiter les données météorologiques"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'OPENWEATHER_API_KEY', os.environ.get('OPENWEATHER_API_KEY'))
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
        # Villes prioritaires du Sénégal avec coordonnées
        self.priority_cities = {
            'Dakar': {'lat': 14.6937, 'lon': -17.4441},
            'Saint-Louis': {'lat': 16.0200, 'lon': -16.4800},
            'Matam': {'lat': 15.6558, 'lon': -13.2550},
            'Podor': {'lat': 16.6500, 'lon': -14.9667},
            'Kaffrine': {'lat': 14.1056, 'lon': -15.5503},
            'Kaolack': {'lat': 14.1500, 'lon': -16.0833},
            'Tambacounda': {'lat': 13.7667, 'lon': -13.6667},
            'Ziguinchor': {'lat': 12.5833, 'lon': -16.2833},
        }
    
    def get_current_weather(self, city_name=None, lat=None, lon=None):
        """
        Récupérer la météo actuelle pour une ville ou des coordonnées
        """
        if not self.api_key:
            raise Exception("Clé API OpenWeatherMap manquante")
        
        params = {
            'appid': self.api_key,
            'units': 'metric',  # Celsius
            'lang': 'fr'
        }
        
        if city_name and city_name in self.priority_cities:
            coords = self.priority_cities[city_name]
            params['lat'] = coords['lat']
            params['lon'] = coords['lon']
        elif lat and lon:
            params['lat'] = lat
            params['lon'] = lon
        else:
            raise Exception("Ville non supportée ou coordonnées manquantes")
        
        try:
            response = requests.get(f"{self.base_url}/weather", params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return self._process_weather_data(data, city_name)
            
        except requests.exceptions.RequestException as e:
            print(f"Erreur API OpenWeatherMap: {e}")
            return None
        except Exception as e:
            print(f"Erreur traitement données météo: {e}")
            return None
    
    def get_forecast(self, city_name=None, lat=None, lon=None, days=5):
        """
        Récupérer les prévisions météo (5 jours)
        """
        if not self.api_key:
            raise Exception("Clé API OpenWeatherMap manquante")
        
        params = {
            'appid': self.api_key,
            'units': 'metric',
            'lang': 'fr'
        }
        
        if city_name and city_name in self.priority_cities:
            coords = self.priority_cities[city_name]
            params['lat'] = coords['lat']
            params['lon'] = coords['lon']
        elif lat and lon:
            params['lat'] = lat
            params['lon'] = lon
        else:
            raise Exception("Ville non supportée ou coordonnées manquantes")
        
        try:
            response = requests.get(f"{self.base_url}/forecast", params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return self._process_forecast_data(data, city_name)
            
        except requests.exceptions.RequestException as e:
            print(f"Erreur API prévisions: {e}")
            return None
    
    def _process_weather_data(self, data, city_name=None):
        """
        Traiter les données météo et déterminer le niveau d'alerte
        """
        try:
            # Extraire les données importantes
            temp = data['main']['temp']
            temp_max = data['main']['temp_max']
            temp_min = data['main']['temp_min']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']
            
            # Déterminer le niveau d'alerte basé sur la température max
            alert_level = self._calculate_alert_level(temp_max)
            
            weather_data = {
                'city': city_name or data.get('name', 'Unknown'),
                'latitude': data['coord']['lat'],
                'longitude': data['coord']['lon'],
                'temperature': round(temp, 1),
                'temp_max': round(temp_max, 1),
                'temp_min': round(temp_min, 1),
                'feels_like': round(feels_like, 1),
                'humidity': humidity,
                'alert_level': alert_level,
                'source': 'openweathermap',
                'recorded_at': timezone.now(),
                'description': data['weather'][0]['description'] if data['weather'] else ''
            }
            
            return weather_data
            
        except KeyError as e:
            print(f"Données météo incomplètes: {e}")
            return None
    
    def _process_forecast_data(self, data, city_name=None):
        """
        Traiter les données de prévisions
        """
        forecasts = []
        
        try:
            for item in data['list'][:15]:  # 5 jours * 3 prévisions par jour
                temp_max = item['main']['temp_max']
                alert_level = self._calculate_alert_level(temp_max)
                
                forecast = {
                    'city': city_name or data['city']['name'],
                    'datetime': datetime.fromtimestamp(item['dt']),
                    'temp_max': round(temp_max, 1),
                    'temp_min': round(item['main']['temp_min'], 1),
                    'feels_like': round(item['main']['feels_like'], 1),
                    'humidity': item['main']['humidity'],
                    'alert_level': alert_level,
                    'description': item['weather'][0]['description']
                }
                
                forecasts.append(forecast)
            
            return forecasts
            
        except (KeyError, IndexError) as e:
            print(f"Erreur traitement prévisions: {e}")
            return []
    
    def _calculate_alert_level(self, temperature):
        """
        Calculer le niveau d'alerte basé sur la température
        Seuils adaptés au climat sénégalais
        """
        if temperature >= 45:
            return 'red'      # Très dangereux
        elif temperature >= 40:
            return 'orange'   # Dangereux
        elif temperature >= 35:
            return 'yellow'   # Très inconfortable
        else:
            return 'green'    # Normal
    
    def update_weather_for_all_cities(self):
        """
        Mettre à jour la météo pour toutes les villes prioritaires
        """
        updated_cities = []
        errors = []
        
        for city_name in self.priority_cities.keys():
            try:
                weather_data = self.get_current_weather(city_name)
                
                if weather_data:
                    # Sauvegarder en base de données
                    weather_obj, created = WeatherData.objects.update_or_create(
                        city=weather_data['city'],
                        recorded_at__date=timezone.now().date(),
                        defaults=weather_data
                    )
                    
                    updated_cities.append(city_name)
                    print(f"✅ Météo mise à jour pour {city_name}: {weather_data['temp_max']}°C ({weather_data['alert_level']})")
                else:
                    errors.append(f"Aucune donnée pour {city_name}")
                    
            except Exception as e:
                error_msg = f"Erreur {city_name}: {str(e)}"
                errors.append(error_msg)
                print(f"❌ {error_msg}")
        
        return {
            'updated_cities': updated_cities,
            'errors': errors,
            'total_updated': len(updated_cities)
        }
    
    def get_cities_in_alert(self, min_alert_level='yellow'):
        """
        Récupérer les villes en état d'alerte
        """
        alert_levels_priority = {
            'green': 0,
            'yellow': 1,
            'orange': 2,
            'red': 3
        }
        
        min_priority = alert_levels_priority.get(min_alert_level, 1)
        
        cities_in_alert = []
        
        for city_name in self.priority_cities.keys():
            try:
                latest_weather = WeatherData.objects.filter(
                    city=city_name
                ).latest('recorded_at')
                
                city_priority = alert_levels_priority.get(latest_weather.alert_level, 0)
                
                if city_priority >= min_priority:
                    cities_in_alert.append({
                        'city': city_name,
                        'temperature': latest_weather.temp_max,
                        'alert_level': latest_weather.alert_level,
                        'last_updated': latest_weather.recorded_at
                    })
                    
            except WeatherData.DoesNotExist:
                continue
        
        return sorted(cities_in_alert, 
                     key=lambda x: alert_levels_priority.get(x['alert_level'], 0), 
                     reverse=True)

# Instance globale du service
weather_service = WeatherService()