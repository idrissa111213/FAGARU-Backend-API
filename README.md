# 🌡️ FAGARU Backend - API Alerte Vagues de Chaleur

Backend Django REST pour la plateforme FAGARU d'alerte et prévention santé face aux vagues de chaleur au Sénégal.

## 🚀 Fonctionnalités

- ✅ **API REST complète** (25+ endpoints)
- ✅ **Authentification** utilisateurs avec profils
- ✅ **Système d'alertes** automatiques par seuils
- ✅ **Intégration météo** OpenWeatherMap temps réel
- ✅ **Notifications** push/SMS (simulé)
- ✅ **Signalements** communautaires
- ✅ **Recommandations** personnalisées par profil

## 🏗️ Architecture

```
fagaru_backend/
├── users/          # Gestion utilisateurs et profils
├── alerts/         # Alertes, notifications, recommandations
├── weather/        # Données météorologiques
├── core/           # Configuration système
└── fagaru_project/ # Settings Django
```

## 🛠️ Installation

### Prérequis
- Python 3.8+
- pip

### Setup
```bash
# Cloner le projet
git clone https://github.com/votre-username/fagaru-backend.git
cd fagaru-backend

# Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installer dépendances
pip install -r requirements.txt

# Variables d'environnement
cp .env.example .env
# Ajouter votre clé OpenWeatherMap dans .env

# Migrations
python manage.py migrate

# Créer superuser
python manage.py createsuperuser

# Démarrer serveur
python manage.py runserver
```

## 🧪 Tests

```bash
# Mise à jour météo
python manage.py update_weather

# Test API
curl http://127.0.0.1:8000/api/

# Test inscription
curl -X POST http://127.0.0.1:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "email": "test@fagaru.sn", "password": "motdepasse123", "password_confirm": "motdepasse123", "city": "Dakar"}'
```

## 📡 API Endpoints

### Authentification
- `POST /api/users/register/` - Inscription
- `POST /api/users/login/` - Connexion
- `GET /api/users/profile/` - Profil utilisateur

### Météo
- `GET /api/weather/current/` - Météo actuelle toutes villes
- `GET /api/weather/city/{name}/` - Météo ville spécifique
- `GET /api/weather/alerts/` - Alertes météo

### Alertes
- `GET /api/alerts/active/` - Alertes en cours
- `GET /api/alerts/recommendations/` - Recommandations santé
- `POST /api/alerts/reports/` - Signalement citoyen

### Documentation complète
Voir `/api/` pour la liste complète des endpoints.

## ⚙️ Configuration

### Variables d'environnement (.env)
```env
SECRET_KEY=your-secret-key
DEBUG=True
OPENWEATHER_API_KEY=your-openweather-api-key
```

### Seuils d'alerte
- 🟡 **Jaune** : ≥ 35°C (Très inconfortable)
- 🟠 **Orange** : ≥ 40°C (Dangereux)
- 🔴 **Rouge** : ≥ 45°C (Très dangereux)

## 🎯 Profils utilisateur
- `general` - Population générale
- `elderly` - Personne âgée (+65 ans)
- `pregnant` - Femme enceinte
- `child` - Enfant (-12 ans)
- `chronic` - Malade chronique
- `outdoor_worker` - Travailleur extérieur

## 🌐 Multilingue
- **Français** (fr)
- **Wolof** (wo)
- **Pulaar** (ff)

## 🏙️ Villes prioritaires
Dakar, Saint-Louis, Matam, Podor, Kaffrine, Kaolack, Tambacounda, Ziguinchor

## 🤝 Contribution

Le frontend est en cours de développement :
- 📱 **Mobile PWA** (React) - App citoyens
- 💻 **Interface Admin** (React) - Professionnels santé

## 📄 Licence

MIT License

## 👨‍💻 Développé par

Équipe FAGARU - Projet de prévention santé Sénégal
