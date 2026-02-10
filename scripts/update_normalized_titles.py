#!/usr/bin/env python
"""Update title_normalized for all works to strip leading symbols"""
import os
import django
import re
import unicodedata

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgmd_backend.settings')
django.setup()

from music.models import Work

def normalize_string(text):
    """Normalize string for search (lowercase, remove accents, strip leading symbols)"""
    if not text:
        return ''
    # Remove accents
    nfkd = unicodedata.normalize('NFKD', text)
    ascii_text = nfkd.encode('ASCII', 'ignore').decode('UTF-8')
    normalized = ascii_text.lower()
    
    # Strip leading non-alphanumeric characters for better alphabetical sorting
    normalized = re.sub(r'^[^a-z0-9]+', '', normalized)
    
    # If the result is empty (all non-ASCII), keep the original lowercased
    if not normalized:
        normalized = text.lower()
    
    return normalized

def main():
    print("Updating title_normalized for all works...")
    
    works = Work.objects.all()
    total = works.count()
    updated = 0
    
    for i, work in enumerate(works, 1):
        old_normalized = work.title_normalized
        new_normalized = normalize_string(work.title)
        
        if old_normalized != new_normalized:
            work.title_normalized = new_normalized
            work.save(update_fields=['title_normalized'])
            updated += 1
        
        if i % 1000 == 0:
            print(f"Processed {i}/{total} works...")
    
    print(f"\nDone! Updated {updated} out of {total} works.")
    
    # Show some examples
    print("\nFirst 10 works alphabetically:")
    for work in Work.objects.order_by('title_normalized')[:10]:
        print(f"  {work.title} -> {work.title_normalized}")

if __name__ == '__main__':
    main()
