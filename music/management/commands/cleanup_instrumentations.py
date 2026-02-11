"""
Django management command to consolidate instrumentation categories.
Reduces 34K+ granular categories to ~30-50 broad categories using intelligent mapping.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from music.models import InstrumentationCategory, Work
from music.utils import get_instrumentation_variations


class Command(BaseCommand):
    help = 'Consolidate instrumentation categories from granular to broad categories'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making changes'
        )

    def categorize_instrumentation(self, raw_instrumentation):
        """Map raw instrumentation to a broad category."""
        if not raw_instrumentation:
            return 'Other'
        
        variations_map = get_instrumentation_variations()
        raw_lower = raw_instrumentation.lower()
        
        # Check each category's variations for matches
        for category, variations in variations_map.items():
            for variation in variations:
                if variation.lower() in raw_lower:
                    return category
        
        # Default fallback categories based on keywords
        if 'orchestra' in raw_lower or 'symphon' in raw_lower:
            return 'Guitar and Orchestra'
        elif 'ensemble' in raw_lower:
            return 'Ensemble'
        elif 'chamber' in raw_lower:
            return 'Chamber Music'
        elif 'concerto' in raw_lower:
            return 'Guitar and Orchestra'
        elif 'solo' in raw_lower:
            return 'Solo'
        elif 'duo' in raw_lower or 'duet' in raw_lower:
            return 'Duo'
        elif 'trio' in raw_lower:
            return 'Trio'
        elif 'quartet' in raw_lower:
            return 'Quartet'
        else:
            return 'Other'

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be saved'))
        
        self.stdout.write('Analyzing works and their instrumentations...')
        
        # Get all works with instrumentation details
        works = Work.objects.select_related('instrumentation_category').all()
        total_works = works.count()
        self.stdout.write(f'Found {total_works} works to process')
        
        # Track category mappings
        category_cache = {}
        updates = []
        stats = {'updated': 0, 'unchanged': 0}
        
        for i, work in enumerate(works, 1):
            if i % 1000 == 0:
                self.stdout.write(f'  Processed {i}/{total_works} works...')
            
            # Use instrumentation_detail (raw text) to determine category
            raw_inst = work.instrumentation_detail or ''
            if not raw_inst and work.instrumentation_category:
                raw_inst = work.instrumentation_category.name
            
            # Map to broad category
            broad_category = self.categorize_instrumentation(raw_inst)
            
            # Check if category needs updating
            current_category = work.instrumentation_category.name if work.instrumentation_category else None
            
            if current_category != broad_category:
                # Get or create broad category
                if broad_category not in category_cache:
                    if not dry_run:
                        cat, created = InstrumentationCategory.objects.get_or_create(name=broad_category)
                        category_cache[broad_category] = cat
                    else:
                        category_cache[broad_category] = broad_category
                
                if not dry_run:
                    work.instrumentation_category = category_cache[broad_category]
                    updates.append(work)
                
                stats['updated'] += 1
            else:
                stats['unchanged'] += 1
        
        # Bulk update works
        if updates and not dry_run:
            self.stdout.write(f'\nSaving {len(updates)} work updates...')
            Work.objects.bulk_update(updates, ['instrumentation_category'], batch_size=500)
        
        # Show statistics
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('CONSOLIDATION COMPLETE'))
        self.stdout.write('=' * 60)
        self.stdout.write(f'Works updated: {stats["updated"]}')
        self.stdout.write(f'Works unchanged: {stats["unchanged"]}')
        self.stdout.write(f'New broad categories: {len(category_cache)}')
        
        if not dry_run:
            # Show category breakdown
            self.stdout.write('\nCategory distribution:')
            from django.db.models import Count
            categories = InstrumentationCategory.objects.annotate(
                work_count=Count('work')
            ).filter(work_count__gt=0).order_by('-work_count')
            
            for cat in categories[:20]:
                self.stdout.write(f'  {cat.name}: {cat.work_count} works')
            
            # Delete unused categories
            unused = InstrumentationCategory.objects.annotate(
                work_count=Count('work')
            ).filter(work_count=0)
            unused_count = unused.count()
            if unused_count > 0:
                self.stdout.write(f'\nDeleting {unused_count} unused instrumentation categories...')
                unused.delete()
                self.stdout.write(self.style.SUCCESS('✓ Cleanup complete!'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nDRY RUN - No changes were made'))
            self.stdout.write('Run without --dry-run to apply changes')
