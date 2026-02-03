"""
Update title_sort_key for all existing works without re-importing.
"""
from django.core.management.base import BaseCommand
from music.models import Work
from music.utils import generate_title_sort_key


class Command(BaseCommand):
    help = 'Update title_sort_key for all works'

    def handle(self, *args, **options):
        self.stdout.write('Updating title_sort_key for all works...')
        
        works = Work.objects.all()
        total = works.count()
        
        batch_size = 1000
        updated = 0
        
        for i in range(0, total, batch_size):
            batch = list(works[i:i + batch_size])
            
            for work in batch:
                work.title_sort_key = generate_title_sort_key(work.title)
            
            Work.objects.bulk_update(batch, ['title_sort_key'], batch_size=batch_size)
            
            updated += len(batch)
            self.stdout.write(f'  Progress: {updated}/{total}')
        
        self.stdout.write(self.style.SUCCESS(f'Updated {total} works'))
