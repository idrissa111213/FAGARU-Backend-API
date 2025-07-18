from django.core.management.base import BaseCommand
from django.utils import timezone
from weather.services import weather_service
from alerts.models import Alert
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Met à jour les données météorologiques et génère les alertes automatiques'

    def add_arguments(self, parser):
        parser.add_argument(
            '--city',
            type=str,
            help='Mettre à jour une ville spécifique seulement',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forcer la mise à jour même si déjà fait récemment',
        )

    def handle(self, *args, **options):
        start_time = timezone.now()
        self.stdout.write(f"🌡️ Début mise à jour météo - {start_time}")

        try:
            # Mise à jour des données météo
            if options['city']:
                result = self._update_single_city(options['city'])
            else:
                result = weather_service.update_weather_for_all_cities()

            # Afficher les résultats
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Mise à jour terminée en {(timezone.now() - start_time).seconds}s"
                )
            )
            self.stdout.write(f"   - Villes mises à jour: {result['total_updated']}")
            self.stdout.write(f"   - Succès: {', '.join(result['updated_cities'])}")
            
            if result['errors']:
                self.stdout.write(
                    self.style.WARNING(f"   - Erreurs: {len(result['errors'])}")
                )
                for error in result['errors']:
                    self.stdout.write(f"     ⚠️ {error}")

            # Générer les alertes après mise à jour météo
            self._generate_automatic_alerts(result['updated_cities'])

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Erreur lors de la mise à jour: {str(e)}")
            )
            logger.error(f"Erreur update_weather: {e}")

    def _update_single_city(self, city_name):
        """Mettre à jour une seule ville"""
        try:
            weather_data = weather_service.get_current_weather(city_name)
            if weather_data:
                return {
                    'updated_cities': [city_name],
                    'errors': [],
                    'total_updated': 1
                }
            else:
                return {
                    'updated_cities': [],
                    'errors': [f"Aucune donnée pour {city_name}"],
                    'total_updated': 0
                }
        except Exception as e:
            return {
                'updated_cities': [],
                'errors': [f"Erreur {city_name}: {str(e)}"],
                'total_updated': 0
            }

    def _generate_automatic_alerts(self, updated_cities):
        """Générer des alertes automatiques basées sur la météo"""
        from alerts.services import alert_service
        
        try:
            alerts_created = alert_service.generate_weather_alerts(updated_cities)
            if alerts_created:
                self.stdout.write(
                    self.style.SUCCESS(f"🚨 {len(alerts_created)} nouvelles alertes générées")
                )
                for alert in alerts_created:
                    self.stdout.write(f"   - {alert.title} ({alert.severity})")
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Erreur génération alertes: {e}")
            )