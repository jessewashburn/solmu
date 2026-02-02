# CSV Import Improvements - Data Quality Protection

## Problem
Discovered CSV parsing issues causing database corruption:
1. **Unicode character issues**: Right double quote (U+201D) vs ASCII quote
2. **CSV parsing errors**: Malformed rows concatenating multiple records into single fields
3. **Silent failures**: Corrupt data imported without detection

## Examples Found
- Work ID 25309: Title was 65,535 chars (max field length) containing ~500 CSV rows
- Work ID 121715: Title was 38,743 chars containing ~200 CSV rows
- CSV line 29562: Unicode quote character breaking parser

## Solutions Implemented

### 1. Robust CSV Parsing
**File**: `music/management/commands/import_sheerpluck.py`

#### Encoding Error Handling
```python
# Before:
open(file, 'r', encoding='utf-8')

# After:
open(file, 'r', encoding='utf-8', errors='replace')
```
- Replaces invalid UTF-8 sequences with replacement character
- Prevents parser crashes on encoding issues

#### Proper CSV Quoting
```python
# Before:
reader = csv.DictReader(f)

# After:
reader = csv.DictReader(f, quoting=csv.QUOTE_ALL, skipinitialspace=True)
```
- `QUOTE_ALL`: Treats all fields as quoted, handles triple-quote patterns correctly
- `skipinitialspace`: Removes leading whitespace after delimiters

### 2. Row-Level Validation
New `_validate_csv_row()` method checks:

#### Field Presence
- Ensures all expected columns exist (ID, Name, Work, Instrumentation, Link)
- Reports missing fields with line number

#### Data Corruption Detection
```python
# Title length check (catches concatenated rows)
if len(work_title) > 200:
    # Skip - likely CSV parsing error

# Double-comma check (catches unparsed CSV)
if ',,' in work_title:
    # Skip - raw CSV data in field

# Required data check
if not composer_name or not work_title:
    # Skip - incomplete record
```

#### Unicode Issue Detection
```python
# Check for replacement characters indicating encoding errors
if '\ufffd' in work_title:
    # Warning - encoding problem
```

### 3. Error Reporting & Tracking
- **Line numbers**: Track source file line for each row
- **Detailed errors**: Report specific issue, file, and line number
- **Statistics**: Count malformed rows skipped
- **Continue on error**: Skip bad rows, don't crash entire import

#### Example Output
```
Sheerpluck line 25309: Work title suspiciously long (65535 chars) - possible CSV parsing error
Sheerpluck line 121715: Work title contains ",," - possible CSV parsing error
...
==================================================
IMPORT COMPLETE
==================================================
Sheerpluck rows: 67,611
Malformed rows skipped: 2
Works created: 67,611
Errors: 2
==================================================
```

### 4. Prevention Strategy
The improvements prevent corruption by:

1. **Early Detection**: Validate before database insertion
2. **Fail-Safe**: Skip bad rows rather than importing corrupt data
3. **Visibility**: Report all issues with context for investigation
4. **Recovery**: Clean imports can proceed even with problematic source data

## Testing Recommendations

### Dry Run Before Import
```bash
python manage.py import_sheerpluck --dry-run
```
- Validates CSV structure without database changes
- Reports all issues found
- Safe to run anytime

### After CSV Updates
1. Run dry-run to check for new issues
2. Review error output for patterns
3. Fix source CSV if needed (like Unicode quote fix)
4. Run actual import

### Monitoring
Watch for these warnings in import output:
- "Work title suspiciously long" - CSV parsing failure
- "Work title contains ,," - Raw CSV in field
- "replacement character" - Encoding issue

## Related Files
- `music/management/commands/import_sheerpluck.py` - Import script with validation
- `delete_corrupted_works.py` - One-time cleanup script (identifies works > 200 chars)
- `fix_unicode_quote.py` - Example: Fix specific Unicode issues in CSV
- `fix_sheerpluck_urls.py` - Re-match works with CSV data to correct external_ids

## Lessons Learned
1. **CSV is tricky**: Even standard library can fail on edge cases
2. **Validate early**: Catch corruption before database insertion
3. **Length checks work**: Suspiciously long fields indicate parsing errors
4. **UTF-8 isn't enough**: Need error handling for invalid sequences
5. **Track provenance**: Line numbers essential for debugging
