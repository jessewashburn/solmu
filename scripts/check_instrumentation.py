import csv

with open('data/sheerpluck_guitar_data.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, quoting=csv.QUOTE_ALL)
    max_len = 0
    long_rows = []
    
    for i, row in enumerate(reader, start=2):
        instrumentation = row.get('Instrumentation', '')
        if len(instrumentation) > max_len:
            max_len = len(instrumentation)
        
        if len(instrumentation) > 500:
            long_rows.append({
                'row': i,
                'id': row.get('ID'),
                'name': row.get('Name'),
                'length': len(instrumentation),
                'instrumentation': instrumentation
            })
    
    print(f"Maximum instrumentation length: {max_len} characters\n")
    
    if long_rows:
        print(f"Found {len(long_rows)} rows with instrumentation > 500 characters:\n")
        for r in long_rows[:20]:
            print(f"Row {r['row']} (ID {r['id']}): {r['length']} chars - {r['name']}")
            print(f"  {r['instrumentation'][:150]}...")
            print()
    else:
        print("No instrumentation fields exceed 500 characters")
