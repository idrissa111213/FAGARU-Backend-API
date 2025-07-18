from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer pour le profil utilisateur"""
    
    class Meta:
        model = UserProfile
        fields = [
            'phone', 'profile_type', 'location_lat', 'location_lng', 
            'city', 'receive_sms', 'receive_push', 'language', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class UserSerializer(serializers.ModelSerializer):
    """Serializer pour l'utilisateur avec profil"""
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']
        read_only_fields = ['id']

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer pour l'inscription"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    profile_type = serializers.ChoiceField(
        choices=UserProfile.PROFILE_CHOICES, 
        default='general'
    )
    phone = serializers.CharField(max_length=20, required=False)
    city = serializers.CharField(max_length=100, required=False)
    language = serializers.ChoiceField(
        choices=[('fr', 'Français'), ('wo', 'Wolof'), ('ff', 'Pulaar')],
        default='fr'
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'profile_type', 'phone', 'city', 'language'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return attrs
    
    def create(self, validated_data):
        # Récupérer les données du profil
        profile_data = {
            'profile_type': validated_data.pop('profile_type', 'general'),
            'phone': validated_data.pop('phone', ''),
            'city': validated_data.pop('city', ''),
            'language': validated_data.pop('language', 'fr'),
        }
        
        # Supprimer password_confirm
        validated_data.pop('password_confirm')
        
        # Créer l'utilisateur
        user = User.objects.create_user(**validated_data)
        
        # Créer le profil
        UserProfile.objects.create(user=user, **profile_data)
        
        return user

class LoginSerializer(serializers.Serializer):
    """Serializer pour la connexion"""
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Identifiants invalides.')
            if not user.is_active:
                raise serializers.ValidationError('Compte désactivé.')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Username et password requis.')
        
        return attrs

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour mettre à jour le profil"""
    
    class Meta:
        model = UserProfile
        fields = [
            'phone', 'profile_type', 'location_lat', 'location_lng',
            'city', 'receive_sms', 'receive_push', 'language'
        ]
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance