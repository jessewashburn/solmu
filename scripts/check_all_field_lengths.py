import csv

# Current model field limits
FIELD_LIMITS = {
    'ID': ('external_id', 100),
    'Name': ('full_name', 255),
    'Work': ('title', 1000),
    'Instrumentation': ('instrumentation (category name)', 1000),
    'Link': ('sheerpluck_url/imslp_url', 1000),
    'Country': ('country name', 100),
}

print("Checking all field lengths in CSV data...\n")
print("=" * 80)

max_lengths = {}
problem_rows = {}

with open('data/sheerpluck_guitar_data.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, quoting=csv.QUOTE_ALL)
    
    for i, row in enumerate(reader, start=2):
        for field_name, value in row.items():
            if field_name not in max_lengths:
                max_lengths[field_name] = {'max': 0, 'row': 0, 'value': ''}
            
            length = len(value) if value else 0
            if length > max_lengths[field_name]['max']:
                max_lengths[field_name] = {
                    'max': length,
                    'row': i,
                    'value': value
                }

print("\nFIELD LENGTH ANALYSIS:\n")

issues_found = False

for field_name, limits in FIELD_LIMITS.items():
    model_field, limit = limits
    actual_max = max_lengths.get(field_name, {}).get('max', 0)
    
    status = "✓ OK" if actual_max <= limit else "✗ PROBLEM"
    if actual_max > limit:
        issues_found = True
        
    print(f"{field_name:20} -> {model_field:35}")
    print(f"  Database limit: {limit:4} chars")
    print(f"  CSV maximum:    {actual_max:4} chars  {status}")
    
    if actual_max > limit:
        row_info = max_lengths[field_name]
        print(f"  ⚠ EXCEEDS LIMIT by {actual_max - limit} characters!")
        print(f"  Problem row: {row_info['row']}")
        print(f"  Value preview: {row_info['value'][:150]}...")
    
    print()

print("=" * 80)

if issues_found:
    print("\n⚠ ISSUES FOUND! Some fields exceed database limits.")
    print("Database schema needs to be updated before import will succeed.\n")
else:
    print("\n✓ ALL CHECKS PASSED! All CSV fields fit within database limits.\n")
