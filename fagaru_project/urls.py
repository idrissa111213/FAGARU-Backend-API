from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.conf import settings
from django.conf.urls.static import static

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def api_root(request):
    """Point d'entrée de l'API FAGARU"""
    return Response({
        'message': 'Bienvenue sur l\'API FAGARU - Plateforme d\'alerte vagues de chaleur',
        'version': '1.0.0',
        'description': 'API pour la gestion des alertes météo et recommandations de santé au Sénégal',
        'endpoints': {
            'authentication': {
                'register': '/api/users/register/',
                'login': '/api/users/login/',
                'logout': '/api/users/logout/',
                'profile': '/api/users/profile/'
            },
            'alerts': {
                'active': '/api/alerts/active/',
                'recommendations': '/api/alerts/recommendations/',
                'notifications': '/api/alerts/notifications/',
                'reports': '/api/alerts/reports/'
            },
            'weather': {
                'current': '/api/weather/current/',
                'cities': '/api/weather/cities/',
                'alerts': '/api/weather/alerts/',
                'statistics': '/api/weather/statistics/'
            },
            'admin': '/admin/',
            'documentation': '/api/'
        },
        'status': 'operational'
    })

urlpatterns = [
    # Administration Django
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', api_root, name='api_root'),
    path('api/users/', include('users.urls')),
    path('api/alerts/', include('alerts.urls')),
    path('api/weather/', include('weather.urls')),
]

# URLs de développement pour servir les fichiers statiques
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)