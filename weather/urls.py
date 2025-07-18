from django.urls import path
from . import views

app_name = 'weather'

urlpatterns = [
    # Météo actuelle
    path('current/', views.current_weather, name='current_weather'),
    path('city/<str:city_name>/', views.weather_by_city, name='weather_by_city'),
    path('city/<str:city_name>/history/', views.weather_history, name='weather_history'),
    
    # Alertes météo
    path('alerts/', views.weather_alerts, name='weather_alerts'),
    path('statistics/', views.weather_stats, name='weather_stats'),
    
    # Données météo
    path('data/', views.WeatherDataListView.as_view(), name='weather_data_list'),
    
    # Villes
    path('cities/', views.cities_list, name='cities_list'),
    
    # Mise à jour et test
    path('update/', views.update_weather_data, name='update_weather_data'),
    path('test/', views.test_weather_api, name='test_weather_api'),
]