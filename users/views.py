from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import UserProfile
from .serializers import (
    UserSerializer, UserRegistrationSerializer, LoginSerializer,
    UserProfileSerializer, UserProfileUpdateSerializer
)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    """Inscription d'un nouvel utilisateur"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'message': 'Compte créé avec succès',
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login(request):
    """Connexion utilisateur"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'message': 'Connexion réussie',
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout(request):
    """Déconnexion utilisateur"""
    try:
        request.user.auth_token.delete()
        return Response({
            'message': 'Déconnexion réussie'
        }, status=status.HTTP_200_OK)
    except:
        return Response({
            'error': 'Erreur lors de la déconnexion'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def profile(request):
    """Récupérer le profil de l'utilisateur connecté"""
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data)

@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_profile(request):
    """Mettre à jour le profil utilisateur"""
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        # Créer le profil s'il n'existe pas
        profile = UserProfile.objects.create(user=request.user)
    
    serializer = UserProfileUpdateSerializer(profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Profil mis à jour avec succès',
            'profile': serializer.data
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_location(request):
    """Mettre à jour la géolocalisation de l'utilisateur"""
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    city = request.data.get('city', '')
    
    if not latitude or not longitude:
        return Response({
            'error': 'Latitude et longitude requises'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        profile = request.user.profile
        profile.location_lat = float(latitude)
        profile.location_lng = float(longitude)
        profile.city = city
        profile.save()
        
        return Response({
            'message': 'Localisation mise à jour',
            'location': {
                'latitude': profile.location_lat,
                'longitude': profile.location_lng,
                'city': profile.city
            }
        })
    except UserProfile.DoesNotExist:
        return Response({
            'error': 'Profil utilisateur non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)
    except ValueError:
        return Response({
            'error': 'Coordonnées invalides'
        }, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.RetrieveUpdateAPIView):
    """Vue générique pour récupérer et modifier le profil"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_stats(request):
    """Statistiques de l'utilisateur"""
    user = request.user
    
    # Compter les notifications reçues
    from alerts.models import AlertNotification
    notifications_count = AlertNotification.objects.filter(user=user).count()
    unread_count = AlertNotification.objects.filter(user=user, is_read=False).count()
    
    # Compter les signalements effectués
    from alerts.models import CommunityReport
    reports_count = CommunityReport.objects.filter(user=user).count()
    
    return Response({
        'notifications_received': notifications_count,
        'unread_notifications': unread_count,
        'community_reports': reports_count,
        'member_since': user.date_joined,
        'profile_type': user.profile.profile_type if hasattr(user, 'profile') else 'general'
    })