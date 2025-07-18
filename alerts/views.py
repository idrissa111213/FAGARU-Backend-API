from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.db.models import Q
from .models import Alert, AlertNotification, Recommendation, CommunityReport
from .serializers import (
    AlertSerializer, AlertNotificationSerializer, RecommendationSerializer,
    CommunityReportSerializer, CommunityReportCreateSerializer, ActiveAlertsSerializer
)

class StandardResultsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def active_alerts(request):
    """Récupérer les alertes actives"""
    city = request.query_params.get('city', None)
    
    # Filtrer les alertes actives
    alerts = Alert.objects.filter(
        is_active=True,
        start_time__lte=timezone.now()
    ).filter(
        Q(end_time__isnull=True) | Q(end_time__gte=timezone.now())
    )
    
    # Filtrer par ville si spécifiée
    if city:
        alerts = alerts.filter(
            Q(affected_cities__icontains=city) | Q(affected_cities=[])
        )
    
    serializer = ActiveAlertsSerializer(alerts, many=True)
    return Response({
        'count': alerts.count(),
        'alerts': serializer.data
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_notifications(request):
    """Notifications de l'utilisateur connecté"""
    notifications = AlertNotification.objects.filter(
        user=request.user
    ).select_related('alert').order_by('-sent_at')
    
    paginator = StandardResultsPagination()
    paginated_notifications = paginator.paginate_queryset(notifications, request)
    serializer = AlertNotificationSerializer(paginated_notifications, many=True)
    
    return paginator.get_paginated_response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_read(request, notification_id):
    """Marquer une notification comme lue"""
    try:
        notification = AlertNotification.objects.get(
            id=notification_id, 
            user=request.user
        )
        notification.is_read = True
        notification.save()
        
        return Response({
            'message': 'Notification marquée comme lue'
        })
    except AlertNotification.DoesNotExist:
        return Response({
            'error': 'Notification non trouvée'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def recommendations(request):
    """Récupérer les recommandations"""
    profile_type = request.query_params.get('profile_type', 'general')
    alert_level = request.query_params.get('alert_level', 'yellow')
    language = request.query_params.get('language', 'fr')
    
    recommendations = Recommendation.objects.filter(
        profile_type=profile_type,
        alert_level=alert_level,
        language=language,
        is_active=True
    ).order_by('order', 'title')
    
    serializer = RecommendationSerializer(recommendations, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def personalized_recommendations(request):
    """Recommandations personnalisées pour l'utilisateur connecté"""
    user = request.user
    alert_level = request.query_params.get('alert_level', 'yellow')
    
    # Récupérer le profil utilisateur
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
    ).order_by('order', 'title')
    
    serializer = RecommendationSerializer(recommendations, many=True)
    return Response({
        'profile_type': profile_type,
        'alert_level': alert_level,
        'recommendations': serializer.data
    })

class CommunityReportListCreateView(generics.ListCreateAPIView):
    """Lister et créer des signalements communautaires"""
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsPagination
    
    def get_queryset(self):
        queryset = CommunityReport.objects.all()
        city = self.request.query_params.get('city', None)
        verified_only = self.request.query_params.get('verified', None)
        
        if city:
            queryset = queryset.filter(city__icontains=city)
        if verified_only == 'true':
            queryset = queryset.filter(is_verified=True)
            
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CommunityReportCreateSerializer
        return CommunityReportSerializer

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_reports(request):
    """Signalements de l'utilisateur connecté"""
    reports = CommunityReport.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    paginator = StandardResultsPagination()
    paginated_reports = paginator.paginate_queryset(reports, request)
    serializer = CommunityReportSerializer(paginated_reports, many=True)
    
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def alert_statistics(request):
    """Statistiques des alertes"""
    now = timezone.now()
    
    # Compter les alertes par niveau
    active_alerts = Alert.objects.filter(
        is_active=True,
        start_time__lte=now
    ).filter(
        Q(end_time__isnull=True) | Q(end_time__gte=now)
    )
    
    stats = {
        'total_active_alerts': active_alerts.count(),
        'yellow_alerts': active_alerts.filter(severity='yellow').count(),
        'orange_alerts': active_alerts.filter(severity='orange').count(),
        'red_alerts': active_alerts.filter(severity='red').count(),
        'total_reports': CommunityReport.objects.count(),
        'verified_reports': CommunityReport.objects.filter(is_verified=True).count(),
    }
    
    return Response(stats)

class AlertDetailView(generics.RetrieveAPIView):
    """Détails d'une alerte spécifique"""
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    permission_classes = [permissions.AllowAny]

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def alerts_by_city(request, city_name):
    """Alertes spécifiques à une ville"""
    alerts = Alert.objects.filter(
        is_active=True,
        affected_cities__icontains=city_name
    ).order_by('-created_at')
    
    serializer = AlertSerializer(alerts, many=True)
    return Response({
        'city': city_name,
        'alerts': serializer.data
    })