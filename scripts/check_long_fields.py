import csv

with open('data/sheerpluck_guitar_data.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, quoting=csv.QUOTE_ALL)
    count = 0
    for i, row in enumerate(reader, start=2):
        title = row.get('Work', '')
        url = row.get('Link', '')
        instrumentation = row.get('Instrumentation', '')
        
        if len(title) > 500 or len(url) > 500:
            print(f'Row {i}: Title={len(title)} chars, URL={len(url)} chars')
            if len(title) > 500:
                print(f'  Title: {title[:200]}...')
            if len(url) > 500:
                print(f'  URL: {url[:200]}...')
            count += 1
            if count > 30:
                break
    
    if count == 0:
        print("No rows found with title or URL > 500 characters")
