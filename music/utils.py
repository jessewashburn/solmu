"""
Data cleaning and validation utilities for the Classical Guitar Music Database.
"""

import re
import unicodedata
from typing import Optional, Tuple


def normalize_name(name: str) -> str:
    """
    Normalize a name for search and comparison.
    Removes accents, converts to lowercase.
    """
    if not name:
        return ''
    # Normalize unicode (decompose accented characters)
    nfkd = unicodedata.normalize('NFKD', name)
    # Remove non-ASCII characters (accents)
    ascii_text = nfkd.encode('ASCII', 'ignore').decode('UTF-8')
    # Convert to lowercase
    return ascii_text.lower().strip()


def parse_composer_name(full_name: str) -> Tuple[str, str, str]:
    """
    Parse a composer's full name into first, last, and normalized form.
    
    Handles formats like:
    - "Last, First" (Sheerpluck format)
    - "First Last"
    - "First Middle Last"
    
    Returns: (first_name, last_name, full_name)
    """
    if not full_name:
        return ('', '', '')
    
    full_name = full_name.strip()
    
    # Handle "Last, First" format
    if ',' in full_name:
        parts = full_name.split(',', 1)
        last_name = parts[0].strip()
        first_name = parts[1].strip() if len(parts) > 1 else ''
        # Reconstruct as "First Last"
        reconstructed = f"{first_name} {last_name}".strip()
        return (first_name, last_name, reconstructed)
    
    # Handle "First Last" or "First Middle Last" format
    name_parts = full_name.rsplit(' ', 1)
    if len(name_parts) == 2:
        first_name = name_parts[0].strip()
        last_name = name_parts[1].strip()
        return (first_name, last_name, full_name)
    
    # Single name (e.g., "Sting", "Prince")
    return ('', full_name, full_name)


def clean_year(year_value: any) -> Optional[int]:
    """
    Clean and validate a year value.
    Returns None if invalid, otherwise returns integer year.
    """
    if year_value is None or year_value == '':
        return None
    
    try:
        # Convert to string and clean
        year_str = str(year_value).strip()
        
        # Handle "ca. 1500" or "c. 1500"
        year_str = re.sub(r'^(ca?\.?\s*)', '', year_str, flags=re.IGNORECASE)
        
        # Handle "1500?" or "1500*"
        year_str = re.sub(r'[?*]$', '', year_str)
        
        # Extract first 4-digit number
        match = re.search(r'\d{4}', year_str)
        if match:
            year = int(match.group())
            # Validate year range (reasonable historical range)
            if 1000 <= year <= 2100:
                return year
        
        return None
    except (ValueError, AttributeError):
        return None


def clean_title(title: str) -> str:
    """
    Clean a work title by removing extra whitespace and normalizing.
    """
    if not title:
        return ''
    
    # Remove extra whitespace
    title = ' '.join(title.split())
    
    # Remove leading/trailing punctuation (except parentheses)
    title = title.strip(' .,;:')
    
    return title


def deduplicate_composer_key(full_name: str, birth_year: Optional[int]) -> str:
    """
    Generate a deduplication key for a composer.
    Used to check if a composer already exists in the database.
    """
    normalized = normalize_name(full_name)
    year_str = str(birth_year) if birth_year else 'unknown'
    return f"{normalized}_{year_str}"


def is_living_composer(birth_year: Optional[int], death_year: Optional[int]) -> bool:
    """
    Determine if a composer is likely still living based on birth/death years.
    """
    from datetime import datetime
    
    if death_year:
        return False
    
    if not birth_year:
        return False
    
    # If born after 1900 and no death year, likely living
    # (unless they're over 100 years old)
    current_year = datetime.now().year
    age = current_year - birth_year
    
    return birth_year > 1900 and age < 100


def parse_opus_number(opus_str: str) -> Optional[str]:
    """
    Parse and normalize opus number from various formats.
    Examples: "Op. 12", "op.12", "Opus 12", "BWV 1004"
    """
    if not opus_str:
        return None
    
    opus_str = opus_str.strip()
    
    # Normalize "Op." or "Opus" prefix
    opus_str = re.sub(r'^(op\.?|opus)\s*', 'Op. ', opus_str, flags=re.IGNORECASE)
    
    return opus_str if opus_str else None


def clean_instrumentation(instrumentation: str) -> str:
    """
    Clean and normalize instrumentation string.
    """
    if not instrumentation:
        return ''
    
    # Remove extra whitespace
    instrumentation = ' '.join(instrumentation.split())
    
    # Capitalize first letter of each word
    instrumentation = instrumentation.title()
    
    return instrumentation


def extract_duration_minutes(duration_str: str) -> Optional[int]:
    """
    Extract duration in minutes from various string formats.
    Examples: "10 min", "10'", "10:00", "10-12 minutes"
    """
    if not duration_str:
        return None
    
    duration_str = str(duration_str).strip().lower()
    
    # Match "X min" or "X minutes"
    match = re.search(r'(\d+)\s*(min|minutes?)', duration_str)
    if match:
        return int(match.group(1))
    
    # Match "X'" (minutes notation)
    match = re.search(r"(\d+)'", duration_str)
    if match:
        return int(match.group(1))
    
    # Match "MM:SS" format
    match = re.search(r'(\d+):(\d+)', duration_str)
    if match:
        minutes = int(match.group(1))
        seconds = int(match.group(2))
        return minutes + (1 if seconds >= 30 else 0)  # Round up if >= 30 seconds
    
    # Match "X-Y minutes" (take average)
    match = re.search(r'(\d+)\s*-\s*(\d+)', duration_str)
    if match:
        min_duration = int(match.group(1))
        max_duration = int(match.group(2))
        return (min_duration + max_duration) // 2
    
    return None


def validate_url(url: str) -> bool:
    """
    Validate if a string is a valid URL.
    """
    if not url:
        return False
    
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(url_pattern.match(url))


def clean_country_name(country: str) -> str:
    """
    Clean and normalize country names.
    Handle common variations and misspellings.
    """
    if not country:
        return ''
    
    country = country.strip()
    
    # Country name mappings for common variations
    country_mappings = {
        'USA': 'United States',
        'U.S.A.': 'United States',
        'United States of America': 'United States',
        'UK': 'United Kingdom',
        'U.K.': 'United Kingdom',
        'Great Britain': 'United Kingdom',
        'The Netherlands': 'Netherlands',
        'Holland': 'Netherlands',
    }
    
    return country_mappings.get(country, country)


def split_movements(movements_str: str) -> list:
    """
    Split a movements string into a list.
    Handles various delimiters: semicolon, newline, numbered lists.
    """
    if not movements_str:
        return []
    
    # Split by semicolon or newline
    movements = re.split(r'[;\n]', movements_str)
    
    # Clean each movement
    movements = [m.strip() for m in movements if m.strip()]
    
    # Remove numbering (1., I., etc.)
    movements = [re.sub(r'^\d+\.?\s*|^[IVX]+\.?\s*', '', m) for m in movements]
    
    return movements


def get_instrumentation_variations() -> dict:
    """
    Returns a dictionary mapping clean instrumentation category names to their variations.
    Used for matching user search terms to actual database entries.
    
    Handles complex patterns including:
    - Parenthetical numbers: guitar (2), electric guitar (2)
    - Equivalency notation: clarinet (=bass clarinet), saxophone (=soprano, tenor)
    - Alternative notation: flute (or violin), guitar (or lute)  
    - Genre prefixes: Chamber Music:, Orchestra:, Dance/Ballet:, Stage Work:
    - Electronics terminology: electronics, live electronics, tape, sampler
    - Amplification: amplified clarinet, amplified guitar
    - Multimedia: sound and video, live electronics, light system
    - Complex orchestra notation: 3.2.4.sax.2, egtr, strgs
    - Microtonal instruments: quarter-tone guitar
    
    Returns:
        dict: Mapping of normalized category names to list of variations
    """
    return {
        # Solo patterns
        'Solo': ['Solo Guitar', 'Guitar Solo', 'solo', 'Solo', 'Solo:', 'Solo: retuned steelstring guitar', 'Solo: detuned semi-acoustic guitar'],
        
        # Duo patterns with numbers and variations
        'Duo': ['Guitar Duo', 'Duo for Guitar', 'Two Guitars', '2 Guitars', '2 guitars', 'duo', 'guitar (2)', 
               'acoustic guitar (2)', 'electric guitar (2)', 'Duo', 'Duo:', 'Duo: electric guitar (2)',
               'guitar and', 'guitar,'],
        
        # Trio patterns  
        'Trio': ['Guitar Trio', 'Trio for Guitar', 'Three Guitars', '3 Guitars', '3 guitars', 'trio', 
                'guitar (3)', 'acoustic guitar (3)', 'electric guitar (3)', 'Trio', 
                'guitar, violin, viola', 'flute, guitar, harp', 'piano, guitar, violin',
                'Trio: guitar (3) - live electronics'],
        
        # Quartet patterns
        'Quartet': ['Guitar Quartet', 'Quartet for Guitar', 'Four Guitars', '4 Guitars', '4 guitars', 
                   'quartet', 'guitar (4)', 'acoustic guitar (4)', 'electric guitar (4)', 'Quartet',
                   'string quartet with guitar', 'guitar, violin (2), viola'],
        
        # Higher ensemble sizes
        'Quintet': ['quintet', 'guitar (5)', 'acoustic guitar (5)', 'electric guitar (5)', 'Quintet',
                   'wind quintet with guitar', 'flute, clarinet, percussion, melodica, guitar'],
        'Sextet': ['sextet', 'guitar (6)', 'acoustic guitar (6)', 'electric guitar (6)', 'Sextet',
                  'flute, clarinet (=bass clarinet), guitar (=electric guitar)'],
        'Septet': ['septet', 'guitar (7)', 'acoustic guitar (7)', 'electric guitar (7)', 'Septet'],
        'Octet': ['octet', 'guitar (8)', 'acoustic guitar (8)', 'electric guitar (8)', 'Octet'],
        
        # Ensemble patterns
        'Ensemble': ['Guitar Ensemble', 'Mixed Ensemble', 'ensemble', 'Ensemble', 'Ensemble:',
                    'chamber ensemble', 'instrumental ensemble', 'contemporary ensemble',
                    'jazz guitar, gamelan ensemble'],
        
        # Orchestra and concerto patterns with complex notation
        'Guitar and Orchestra': ['Guitar and Orchestra', 'Guitar with Orchestra', 'Concerto', 'concerto', 
                                'Orchestra:', 'Orchestra', 'orchestra', 'symphonic orchestra', 
                                'Concerto:', 'egtr', 'bgtr', 'strgs', 'hrp', 'pft', 'perc', 'timp',
                                'guitar - orchestra', 'guitar - string orchestra',
                                '2.2.2.2', '3.2.4.sax.2', '1.1.1.1', '4.3.3.1', '6perc-bgtr - strgs',
                                'picc.1.1.1.1.dbn', '3(II=afl,III=picc)', '4perc-hrp-pft-gtr',
                                '3(II=afl,III=picc).3(III=corA).3(III=bcl).asax.3(III=dbn)',
                                '15.13.11.9.7', 'corA', 'dbn', '(49 players)', 'string orchestra',
                                'chamber orchestra', 'philharmonic', 'symphony'],
        
        # Guitar ensemble patterns
        'Guitar Orchestra': ['Guitar Orchestra', 'guitar orchestra', 'guitar orchestra (2)', 
                            'guitar orchestra (4)', 'guitar orchestra (8)', 'Guitar Ensemble:',
                            '24 (or 8) guitars', 'multiple guitars', 'guitar ensemble'],
        
        # Voice and chorus patterns with specific types
        'Guitar and Voice': ['Voice and Guitar', 'Guitar and Vocal', 'Vocal and Guitar', 
                            'voice', 'vocal', 'song', 'soprano', 'alto', 'tenor', 'bass', 
                            'baritone', 'mezzo-soprano', 'chorus', 'voice - guitar',
                            'soprano - guitar', 'tenor - guitar', 'mezzo-soprano - guitar',
                            'SATB chorus', 'SATB chorus - guitar', 'Chorus and Guitar:',
                            'soprano - mandolin, guitar', 'Chamber Music: soprano - guitar',
                            'Chamber Music: tenor - guitar', 'Chamber Music: voice - guitar'],
        
        # Chamber music patterns with genre prefixes
        'Chamber Music': ['Chamber', 'chamber', 'Chamber Music:', 'Chamber Music',
                         'chamber music', 'small ensemble', 'mixed ensemble',
                         'Chamber Music: flute, clarinet', 'Chamber Music: soprano - guitar',
                         'Chamber Music: guitar, violoncello', 'Chamber Music: piano, guitar',
                         'Chamber Music: flute, guitar', 'Chamber Music: guitar, harp'],
        
        # Stage works, multimedia, and theatrical productions
        'Stage Work': ['Stage Work:', 'Stage Work', 'stage work', 'theatrical work',
                      'Opera:', 'Opera', 'opera', 'musical theater', 'musical theatre',
                      'operetta', 'singspiel', 'music theatre', 'Opera: stage work',
                      'stage production', 'dramatic work', 'theatrical production'],
        
        # Electronics patterns with live/fixed media and multimedia
        'Guitar with Electronics': ['Electronics', 'Electronic', 'Tape', 'Fixed Media', 
                                   'Guitar with Electronics:', 'Guitar with Fixed Media:',
                                   'electronics', 'live electronics', 'electronics (ad lib.)',
                                   'synthesizer', 'synthesizers', 'effects processor',
                                   'guitar - electronics', 'guitar - live electronics', 
                                   'guitar - tape', 'electric guitar - electronics',
                                   'electric guitar - live electronics', '- tape', '- electronics',
                                   'sound and video', 'multimedia', 'light system',
                                   'interactive electronics', 'computer-generated sounds',
                                   'sampler', 'sequencer', 'midi controller'],
        
        # Amplified instruments category
        'Amplified Instruments': ['amplified guitar', 'amplified clarinet', 'amplified piano',
                                 'amplified violin', 'amplified cello', 'amplified flute',
                                 'amplified accordion', 'amplified percussion', 'amplified harp',
                                 'guitar (ampl.)', 'ampl.', 'amplified', 'electric guitar',
                                 'electronic guitar', 'processed guitar'],
        
        # Electric guitar patterns
        'Electric Guitar': ['Electric Guitar Solo', 'electric', 'Electric Guitar:', 'electric guitar', 
                           'guitar (=electric guitar)', 'guitar (electric)',
                           'egtr', 'e-guitar'],
        
        # Bass guitar patterns
        'Bass Guitar': ['Bass Guitar Solo', 'bass guitar', 'Electric Bass', 'electric bass guitar',
                       'bgtr', 'electric bass', 'bass guitar solo'],
        
        # Specialized guitar types and microtonal instruments
        '12-String Guitar': ['12-string guitar', '12-string', 'twelve-string'],
        
        'Special Guitar Types': ['quarter-tone guitar', 'prepared guitar', 'scordatura guitar',
                               'retuned guitar', 'detuned guitar', 'microtonal guitar',
                               'DADGAD guitar', 'open tuning guitar', 'altered tuning'],
        
        # Plucked instruments category
        'Plucked Instruments': ['Plucked Instruments:', 'Plucked Instruments', 'plucked instruments',
                              'mandolin', 'mandola', 'banjo', 'lute', 'theorbo', 'archlute',
                              'chitarrone', 'vihuela', 'cittern', 'balalaika', 'sitar',
                              'koto', 'pipa', 'oud', 'shamisen', 'charango', 'cuatro',
                              'tiple', 'requinto', 'guitarrón', 'vina', 'sarod',
                              'guitar (or lute)', 'lute (or guitar)', 'renaissance lute',
                              'baroque lute', '13-course lute', '14-course lute'],
        
        # Flute family with alternatives and equivalencies
        'Guitar and Flute': ['Flute and Guitar', 'Guitar with Flute', 'Flute with Guitar', 
                            'flute', 'piccolo', 'alto flute', 'bass flute', 'pan flute',
                            'flute (2)', 'flute (or violin)', 'flute (or clarinet)',
                            'afl', 'picc', 'Chamber Music: flute, guitar',
                            'alto flute, guitar'],
        
        # Clarinet family with equivalencies and amplification
        'Guitar and Clarinet': ['clarinet', 'bass clarinet', 'clarinet (=bass clarinet)',
                               'clarinet (2)', 'bcl', 'bass clarinet (=clarinet)',
                               'Clarinet', 'Bass Clarinet', 'flute, clarinet',
                               'amplified clarinet', 'clarinet (amplified)'],
        
        # Saxophone family
        'Guitar and Saxophone': ['saxophone', 'alto saxophone', 'tenor saxophone', 
                                'baritone saxophone', 'soprano saxophone', 'sax', 
                                'asax', 'tsax', 'barsax', 'alt sax', 'tenor sax',
                                'baritone saxophone (=soprano saxophone)'],
        
        # String instruments with variations
        'Guitar and Violin': ['Violin and Guitar', 'Guitar with Violin', 'Violin with Guitar', 
                             'violin', 'violin (2)', 'violins', 'vln', 'violin solo',
                             'electric violin', 'guitar, violin', 'piano, guitar, violin'],
        
        'Guitar and Viola': ['Viola and Guitar', 'Guitar with Viola', 'viola', 'violas', 
                            'vla', 'guitar, viola', 'flute, guitar, viola'],
        
        'Guitar and Cello': ['Cello and Guitar', 'Guitar with Cello', 'Cello with Guitar', 
                            'cello', 'violoncello', 'violoncello,', 'cellos', 'vc', 'vlc',
                            'guitar, violoncello', 'electric violoncello'],
        
        'Guitar and Strings': ['String Ensemble', 'Guitar with Strings', 'strings', 'strgs', 
                              'double bass', 'contrabass', 'string bass', 'db', 'cb',
                              'electric bass', 'piano, guitar, double bass'],
        
        # Keyboard instruments with alternatives  
        'Guitar and Piano': ['Piano and Guitar', 'Guitar with Piano', 'Piano with Guitar', 
                            'piano', 'prepared piano', 'harpsichord', 'keyboards', 'keyboard',
                            'pft', 'pf', 'grand piano', 'fender rhodes', 'electric piano',
                            'hammerklavier', 'harpsichord (or hammerklavier)', 'hpsd',
                            'fender rhodes or grand piano', 'keyboard (fender rhodes or grand piano)',
                            'Chamber Music: piano, guitar'],
        
        # Harp patterns
        'Guitar and Harp': ['Harp and Guitar', 'harp', 'harps', 'hrp', 'harp (amplified)',
                           'guitar, harp', 'Chamber Music: guitar, harp', 'flute, guitar, harp'],
        
        # Percussion with qualifiers
        'Guitar and Percussion': ['Percussion and Guitar', 'Guitar with Percussion', 
                                 'percussion', 'timpani', 'vibraphone', 'marimba', 'xylophone',
                                 'drum kit', 'drums', 'timp', 'perc', 'vib', 'xyl',
                                 'percussion (2)', 'percussion (3)', '2perc', '3perc', '4perc', '6perc',
                                 'percussion (solo plus 2 other players)', 'steel drum', 'drkit'],
        
        'Guitar and Marimba': ['Marimba and Guitar', 'marimba'],
        
        # Mandolin patterns (also in Plucked Instruments)
        'Guitar and Mandolin': ['Mandolin and Guitar', 'mandolin', 'mandolin (2)', 'mandola',
                               'soprano - mandolin, guitar'],
        
        # Brass instruments
        'Guitar and Trumpet': ['trumpet', 'french horn', 'trombone', 'tuba', 'contrabass tuba',
                              'trumpet (2)', 'trumpets', 'tpt', 'cornet', 'horn', 'Horn',
                              'horn (2)', 'horns', 'hn', 'trombones', 'tbn', 'bass trombone'],
        
        # Woodwind instruments  
        'Guitar and Recorder': ['recorder', 'recorder (5)', 'alto recorder', 'recorder consort'],
        
        'Guitar and Oboe': ['oboe', 'bassoon', 'cor anglais', 'corA', 'oboe (or flute)',
                           'oboe, guitar', 'double bassoon', 'dbn'],
        
        # Special instruments
        'Guitar and Other': ['theremin', 'accordion', 'melodica', 'organ', 'hammond organ', 
                           'horg', 'B3', 'celesta', 'cel'],
        
        # Gamelan and world music
        'Guitar and Gamelan': ['gamelan', 'Gamelan', 'kantil', 'pemade', 'jublag', 'jegog', 
                              'reyong', 'kemong', 'kempur', 'gong', 'kempli', 'cengceng'],
        
        # Genre categories
        'Dance/Ballet': ['Dance/Ballet:', 'Ballet', 'dance', 'ballet', 'choreographic'],
        
        'Incidental and Film': ['Incidental and Film:', 'Film', 'film music', 'Incidental',
                               'incidental music', 'theater music', 'stage music'],
        
        # Special categories
        'Installation/Sound Environment': ['Installation/Sound Environment:', 'Installation', 
                                          'Sound Environment']
    }


def generate_title_sort_key(title: str) -> str:
    """
    Generate a sort key for intelligent alphabetical sorting of work titles.
    
    Sort buckets (prefixes):
      1) Latin-letter titles      -> "1|<folded>"
      2) Numeric-leading titles   -> "2|<folded>"
      3) Other-letter titles      -> "3|<folded>"
      4) Symbol-only / empty      -> "4|<original-casefold>"
    
    Examples:
    - "Cadenza" -> 1|cadenza
    - À bout portant -> 1|a bout portant
    - 10 Studies -> 2|10 studies
    - Ιθάκη (Greek) -> 3|ιθάκη
    - _____ -> 4|_____
    """
    # Small, targeted expansions that stdlib normalization won't turn into ASCII sequences
    EXTENDED_LATIN_MAP = str.maketrans({
        'Æ': 'AE', 'æ': 'ae',
        'Œ': 'OE', 'œ': 'oe',
        'Ø': 'O',  'ø': 'o',
        'Ð': 'D',  'ð': 'd',
        'Þ': 'TH', 'þ': 'th',
        'ẞ': 'ss', 'ß': 'ss',
        'Ł': 'L',  'ł': 'l',
        'Đ': 'D',  'đ': 'd',
    })
    
    def strip_leading_junk(s: str) -> str:
        """Remove leading chars that are not letters/digits using Unicode categories."""
        if not s:
            return ''
        
        s = unicodedata.normalize('NFKC', s)
        
        i = 0
        while i < len(s):
            ch = s[i]
            cat = unicodedata.category(ch)
            # Keep if letter or number
            if cat[0] in ('L', 'N'):
                break
            # Otherwise drop punctuation, symbols, marks, separators, format chars
            i += 1
        
        return s[i:].strip()
    
    def remove_combining_marks(s: str) -> str:
        """Remove diacritics by decomposing and dropping combining marks."""
        decomp = unicodedata.normalize('NFKD', s)
        return ''.join(c for c in decomp if unicodedata.category(c) != 'Mn')
    
    def is_latin_letter(ch: str) -> bool:
        """Detect Latin script by Unicode name."""
        try:
            return unicodedata.category(ch).startswith('L') and 'LATIN' in unicodedata.name(ch)
        except ValueError:
            return False
    
    if not title:
        return "4|"
    
    original = unicodedata.normalize('NFKC', title).casefold()
    core = strip_leading_junk(title)
    
    if not core:
        return f"4|{original}"
    
    # Expand ligatures etc.
    core = core.translate(EXTENDED_LATIN_MAP)
    
    first = core[0]
    
    # Bucket decision
    if first.isdigit():
        # Keep digits but casefold everything else
        return f"2|{unicodedata.normalize('NFKC', core).casefold()}"
    
    if is_latin_letter(first):
        # For Latin titles: remove diacritics so É ~ E
        folded = remove_combining_marks(core)
        folded = unicodedata.normalize('NFKC', folded).casefold()
        return f"1|{folded}"
    
    # Other scripts: keep them, but normalize + casefold
    return f"3|{unicodedata.normalize('NFKC', core).casefold()}"
