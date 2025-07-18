from django.urls import path
from . import views

app_name = 'alerts'

urlpatterns = [
    # Alertes
    path('active/', views.active_alerts, name='active_alerts'),
    path('<int:pk>/', views.AlertDetailView.as_view(), name='alert_detail'),
    path('city/<str:city_name>/', views.alerts_by_city, name='alerts_by_city'),
    path('statistics/', views.alert_statistics, name='alert_statistics'),
    
    # Notifications utilisateur
    path('notifications/', views.user_notifications, name='user_notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    
    # Recommandations
    path('recommendations/', views.recommendations, name='recommendations'),
    path('recommendations/personalized/', views.personalized_recommendations, name='personalized_recommendations'),
    
    # Signalements communautaires
    path('reports/', views.CommunityReportListCreateView.as_view(), name='community_reports'),
    path('reports/my/', views.my_reports, name='my_reports'),
]