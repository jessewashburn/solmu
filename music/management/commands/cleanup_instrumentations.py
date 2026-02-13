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
        
        raw_lower = raw_instrumentation.lower()
        
        # Check for genre/structural categories FIRST (highest priority)
        # These are explicit genre markers that should ALWAYS override instrument detection
        if raw_instrumentation.startswith('Stage Work:'):
            return 'Stage Work'
        if raw_instrumentation.startswith('Opera:'):
            return 'Stage Work'
        if raw_instrumentation.startswith('Dance/Ballet:'):
            return 'Dance/Ballet'
        if raw_instrumentation.startswith('Installation/Sound Environment:'):
            return 'Installation/Sound Environment'
        
        # Note if it has Chamber Music, Ensemble, or Concerto prefix (but don't return yet)
        # We want to check for specific instruments first
        has_chamber_music_prefix = raw_instrumentation.startswith('Chamber Music:')
        has_ensemble_prefix = raw_instrumentation.startswith('Ensemble:')
        has_concerto_prefix = raw_instrumentation.startswith('Concerto:')
        
        # Check for large ensemble categories (orchestra, concerto)
        if 'orchestra' in raw_lower or 'symphon' in raw_lower or 'philharmonic' in raw_lower:
            return 'Guitar and Orchestra'
        # Only auto-categorize as concerto if it has both keywords (not just prefix)
        if 'concerto' in raw_lower and 'guitar' in raw_lower and not has_concerto_prefix:
            return 'Guitar and Orchestra'
        
        # Count commas to estimate number of instruments/players
        comma_count = raw_instrumentation.count(',')
        
        # If many instruments (5+ commas), it's likely an ensemble or chamber work
        if comma_count >= 5:
            if 'chamber' in raw_lower:
                return 'Chamber Music'
            elif 'ensemble' in raw_lower:
                return 'Ensemble'
            else:
                # Large group without specific label
                return 'Ensemble'
        
        # Check for explicit solo designation with pattern matching
        # Only consider it solo if "solo" appears early and no many other instruments
        if comma_count == 0:
            if 'solo' in raw_lower or raw_instrumentation.startswith('Solo:'):
                # For guitar repertoire database, assume "Solo" means guitar solo
                if 'electric' in raw_lower and 'guitar' in raw_lower:
                    return 'Electric Guitar'
                elif 'bass' in raw_lower and 'guitar' in raw_lower:
                    return 'Bass Guitar'
                else:
                    # Default to Solo for this guitar database
                    return 'Solo'
        
        # Check for voice/vocal works BEFORE checking ensemble sizes
        # First check unambiguous voice terms
        voice_terms = ['voice', 'soprano', 'mezzo-soprano', 'mezzo', 'contralto', 'countertenor', 'chorus', 'choir', 'vocal', 'song', 'singer', 'vocals']
        if any(word in raw_lower for word in voice_terms):
            return 'Guitar and Voice'
        
        # Comprehensive list of instrument types that can have alto/bass/baritone/tenor prefixes
        # These should NOT be treated as voices
        instrument_types = [
            'flute', 'piccolo', 'fife',
            'sax', 'saxophone', 
            'clarinet', 'basset',
            'oboe', 'cor anglais', 'english horn',
            'bassoon', 'contrabassoon',
            'recorder', 'flageolet',
            'trumpet', 'cornet', 'flugelhorn',
            'horn', 'french horn',
            'trombone', 'euphonium', 'tuba',
            'guitar', 'ukulele', 'banjo', 'mandolin',
            'violin', 'viola', 'viol', 'cello', 'violoncello',
            'drum', 'timpani', 'percussion',
            'shawm', 'crumhorn', 'dulcian',
            'double bass', 'contrabass', 'string bass', 'upright bass'  # Full bass instrument names
        ]
        
        # Check alto/tenor/baritone/bass as voice parts (not instruments)
        # Only treat as voice if NOT followed by instrument name
        voice_range_terms = ['alto', 'tenor', 'baritone', 'bass']
        for voice_term in voice_range_terms:
            # Check if the term appears in the string
            if f' {voice_term}' in raw_lower or raw_lower.startswith(voice_term):
                # Special case: check for "double bass" first (before checking "bass")
                if voice_term == 'bass' and ('double bass' in raw_lower or 'doublebass' in raw_lower or 'contrabass' in raw_lower):
                    continue  # Skip - it's an instrument
                
                # Check if it's followed by an instrument name
                is_instrument = False
                for inst in instrument_types:
                    # Check patterns like "alto flute", "alto-flute", "altoflute"
                    if f'{voice_term} {inst}' in raw_lower or f'{voice_term}-{inst}' in raw_lower or f'{voice_term}{inst}' in raw_lower:
                        is_instrument = True
                        break
                # If not an instrument, treat as voice
                if not is_instrument:
                    return 'Guitar and Voice'
        
        # Electronics
        if any(word in raw_lower for word in ['electronics', 'tape', 'fixed media', 'live electronics', 
                                               'sampler', 'synthesizer', 'computer']):
            return 'Guitar with Electronics'
        
        # Check for specific instrument pairings (only if duo - exactly 1 comma = 2 instruments)
        # Do this BEFORE checking generic ensemble sizes
        if comma_count == 1:
            if 'piano' in raw_lower or 'harpsichord' in raw_lower:
                return 'Guitar and Piano'
            if 'flute' in raw_lower:
                return 'Guitar and Flute'
            if 'violin' in raw_lower:
                return 'Guitar and Violin'
            if 'viola' in raw_lower:
                return 'Guitar and Viola'
            if 'cello' in raw_lower or 'violoncello' in raw_lower:
                return 'Guitar and Cello'
            if 'clarinet' in raw_lower:
                return 'Guitar and Clarinet'
            if 'saxophone' in raw_lower:
                return 'Guitar and Saxophone'
            if 'harp' in raw_lower:
                return 'Guitar and Harp'
            if 'percussion' in raw_lower or 'marimba' in raw_lower:
                return 'Guitar and Percussion'
            if 'trumpet' in raw_lower or 'horn' in raw_lower or 'trombone' in raw_lower:
                return 'Guitar and Trumpet'
            if 'oboe' in raw_lower or 'bassoon' in raw_lower:
                return 'Guitar and Oboe'
            if 'recorder' in raw_lower:
                return 'Guitar and Recorder'
            if 'mandolin' in raw_lower:
                return 'Guitar and Mandolin'
        
        # Check for specific ensemble sizes by looking for number patterns
        # Only check these AFTER specific instrument pairings
        if 'duo' in raw_lower or 'guitar (2)' in raw_lower or comma_count == 1:
            return 'Duo'
        if 'trio' in raw_lower or 'guitar (3)' in raw_lower or comma_count == 2:
            return 'Trio'
        if 'quartet' in raw_lower or 'guitar (4)' in raw_lower or comma_count == 3:
            return 'Quartet'
        if 'quintet' in raw_lower or 'guitar (5)' in raw_lower:
            return 'Quintet'
        if 'sextet' in raw_lower or 'guitar (6)' in raw_lower:
            return 'Sextet'
        if 'septet' in raw_lower or 'guitar (7)' in raw_lower:
            return 'Septet'
        if 'octet' in raw_lower or 'guitar (8)' in raw_lower:
            return 'Octet'
        
        # Plucked instruments (use word boundaries to avoid matching "flute" as "lute")
        plucked_words = ['mandolin', 'banjo', 'theorbo', 'vihuela', 'cittern', 'balalaika', 'sitar', 'koto']
        # Check for lute separately to avoid matching "flute"
        if any(word in raw_lower for word in plucked_words):
            return 'Plucked Instruments'
        if ' lute' in raw_lower or raw_lower.startswith('lute') or ',lute' in raw_lower:
            return 'Plucked Instruments'
        
        # If we didn't find a specific instrument pairing but it has a prefix, use that
        if has_concerto_prefix:
            return 'Guitar and Orchestra'
        if has_chamber_music_prefix:
            return 'Chamber Music'
        if has_ensemble_prefix:
            return 'Ensemble'
        
        # Default to Other if nothing matched
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
