from django.core.management.base import BaseCommand
from core.models import SenegalCity
from alerts.models import Recommendation

class Command(BaseCommand):
    help = 'Populate initial data for FAGARU'

    def handle(self, *args, **options):
        # Villes prioritaires du Sénégal
        cities = [
            {'name': 'Matam', 'region': 'Matam', 'lat': 15.6558, 'lng': -13.2550, 'priority': True},
            {'name': 'Podor', 'region': 'Saint-Louis', 'lat': 16.6500, 'lng': -14.9667, 'priority': True},
            {'name': 'Kaffrine', 'region': 'Kaffrine', 'lat': 14.1056, 'lng': -15.5503, 'priority': True},
            {'name': 'Kaolack', 'region': 'Kaolack', 'lat': 14.1500, 'lng': -16.0833, 'priority': True},
            {'name': 'Dakar', 'region': 'Dakar', 'lat': 14.6937, 'lng': -17.4441, 'priority': True},
            {'name': 'Saint-Louis', 'region': 'Saint-Louis', 'lat': 16.0200, 'lng': -16.4800, 'priority': True},
        ]
        
        for city_data in cities:
            city, created = SenegalCity.objects.get_or_create(
                name=city_data['name'],
                defaults={
                    'region': city_data['region'],
                    'latitude': city_data['lat'],
                    'longitude': city_data['lng'],
                    'is_priority': city_data['priority'],
                }
            )
            if created:
                self.stdout.write(f"✅ Ville créée : {city.name}")

        # Recommandations de base
        recommendations = [
            {
                'profile': 'general', 'level': 'yellow', 'lang': 'fr',
                'title': 'Restez hydraté', 
                'content': 'Buvez de l\'eau régulièrement, même sans soif.',
                'icon': 'water_drop'
            },
            {
                'profile': 'elderly', 'level': 'orange', 'lang': 'fr',
                'title': 'Évitez les sorties',
                'content': 'Restez à l\'intérieur pendant les heures les plus chaudes.',
                'icon': 'home'
            },
            {
                'profile': 'pregnant', 'level': 'red', 'lang': 'fr',
                'title': 'Urgence médicale',
                'content': 'Consultez immédiatement un médecin en cas de malaise.',
                'icon': 'emergency'
            },
        ]
        
        for rec_data in recommendations:
            rec, created = Recommendation.objects.get_or_create(
                profile_type=rec_data['profile'],
                alert_level=rec_data['level'],
                language=rec_data['lang'],
                title=rec_data['title'],
                defaults={
                    'content': rec_data['content'],
                    'icon': rec_data['icon'],
                }
            )
            if created:
                self.stdout.write(f"✅ Recommandation créée : {rec.title}")

        self.stdout.write(self.style.SUCCESS('🎉 Données initiales chargées avec succès !'))