"""
Django management command to create index on external_id for faster imports.
"""

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Create index on works.external_id for faster import lookups'

    def handle(self, *args, **options):
        self.stdout.write('Creating index on works(external_id, data_source_id)...')
        
        with connection.cursor() as cursor:
            # Check if index already exists
            cursor.execute("""
                SELECT indexname 
                FROM pg_indexes 
                WHERE tablename = 'works' 
                AND indexname = 'idx_work_external_id'
            """)
            
            if cursor.fetchone():
                self.stdout.write(self.style.WARNING('Index already exists!'))
                return
            
            # Create index without CONCURRENTLY for simplicity
            cursor.execute("""
                CREATE INDEX idx_work_external_id 
                ON works(external_id, data_source_id)
            """)
            
        self.stdout.write(self.style.SUCCESS('✓ Index created successfully!'))
        self.stdout.write('This will significantly speed up import lookups.')
