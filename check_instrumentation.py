import csv

lengths = []
max_sample = ""
max_len = 0

with open('data/sheerpluck_guitar_data.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        inst = row.get('Instrumentation', '')
        length = len(inst)
        lengths.append(length)
        if length > max_len:
            max_len = length
            max_sample = inst

print(f'Min length: {min(lengths)}')
print(f'Max length: {max(lengths)}')
print(f'Average: {sum(lengths)/len(lengths):.1f}')
print(f'Over 1000 chars: {sum(1 for l in lengths if l > 1000)}')
print(f'Over 500 chars: {sum(1 for l in lengths if l > 500)}')
print(f'\nLongest instrumentation value ({max_len} chars):')
print(max_sample[:200] + '...' if len(max_sample) > 200 else max_sample)
