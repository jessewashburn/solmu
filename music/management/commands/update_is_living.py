"""
Management command to update is_living field for all composers based on current logic.
"""
from django.core.management.base import BaseCommand
from music.models import Composer
from music.utils import is_living_composer


class Command(BaseCommand):
    help = 'Update is_living field for all composers based on birth/death years'

    def handle(self, *args, **options):
        composers = Composer.objects.all()
        updated_count = 0
        
        for composer in composers:
            calculated_living = is_living_composer(composer.birth_year, composer.death_year)
            
            if composer.is_living != calculated_living:
                composer.is_living = calculated_living
                composer.save(update_fields=['is_living'])
                updated_count += 1
                
                self.stdout.write(
                    f"Updated {composer.full_name} (born {composer.birth_year}, "
                    f"died {composer.death_year or 'N/A'}): is_living = {calculated_living}"
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully updated {updated_count} composers')
        )
