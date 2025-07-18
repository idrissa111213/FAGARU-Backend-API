from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Authentification
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    
    # Profil utilisateur
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/location/', views.update_location, name='update_location'),
    
    # Statistiques utilisateur
    path('stats/', views.user_stats, name='user_stats'),
]