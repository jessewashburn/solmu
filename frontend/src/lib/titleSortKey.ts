/**
 * Generate a sort key for intelligent alphabetical sorting of work titles.
 * Matches the backend Python implementation for consistent sorting.
 * 
 * Sort buckets (prefixes):
 *   1) Latin-letter titles      -> "1|<folded>"
 *   2) Numeric-leading titles   -> "2|<folded>"
 *   3) Other-letter titles      -> "3|<folded>"
 *   4) Symbol-only / empty      -> "4|<original-casefold>"
 */

// Extended Latin character mapping
const EXTENDED_LATIN_MAP: Record<string, string> = {
  'Æ': 'AE', 'æ': 'ae',
  'Œ': 'OE', 'œ': 'oe',
  'Ø': 'O',  'ø': 'o',
  'Ð': 'D',  'ð': 'd',
  'Þ': 'TH', 'þ': 'th',
  'ẞ': 'ss', 'ß': 'ss',
  'Ł': 'L',  'ł': 'l',
  'Đ': 'D',  'đ': 'd',
};

function stripLeadingJunk(s: string): string {
  /**
   * Remove leading chars that are not letters/digits using Unicode categories.
   */
  if (!s) return '';
  
  // Normalize to NFKC
  s = s.normalize('NFKC');
  
  let i = 0;
  while (i < s.length) {
    const ch = s[i];
    
    // Check if letter or number using Unicode categories
    // Letters: Unicode category L* (Lu, Ll, Lt, Lm, Lo)
    // Numbers: Unicode category N* (Nd, Nl, No)
    if (isLetter(ch) || isDigit(ch)) {
      break;
    }
    i++;
  }
  
  return s.slice(i).trim();
}

function isLetter(ch: string): boolean {
  // Check if character is a letter (any script)
  return /\p{L}/u.test(ch);
}

function isDigit(ch: string): boolean {
  // Check if character is a digit
  return /\p{N}/u.test(ch);
}

function removeCombiningMarks(s: string): string {
  /**
   * Remove diacritics by decomposing and dropping combining marks.
   */
  const decomposed = s.normalize('NFD');
  // Remove combining diacritical marks (Unicode category Mn)
  return decomposed.replace(/\p{Mn}/gu, '');
}

function isLatinLetter(ch: string): boolean {
  /**
   * Detect Latin script by checking if it's in the Latin Unicode blocks.
   * Latin blocks: 0000-007F (Basic Latin), 0080-00FF (Latin-1 Supplement),
   * 0100-017F (Latin Extended-A), 0180-024F (Latin Extended-B), etc.
   */
  const code = ch.charCodeAt(0);
  return (
    (code >= 0x0041 && code <= 0x005A) || // A-Z
    (code >= 0x0061 && code <= 0x007A) || // a-z
    (code >= 0x00C0 && code <= 0x00FF) || // Latin-1 Supplement (À-ÿ)
    (code >= 0x0100 && code <= 0x017F) || // Latin Extended-A
    (code >= 0x0180 && code <= 0x024F) || // Latin Extended-B
    (code >= 0x1E00 && code <= 0x1EFF)    // Latin Extended Additional
  );
}

function applyExtendedLatinMap(s: string): string {
  return s.split('').map(ch => EXTENDED_LATIN_MAP[ch] || ch).join('');
}

export function generateTitleSortKey(title: string): string {
  if (!title) {
    return "4|";
  }
  
  const original = title.normalize('NFKC').toLowerCase();
  const core = stripLeadingJunk(title);
  
  if (!core) {
    return `4|${original}`;
  }
  
  // Expand ligatures etc.
  const mapped = applyExtendedLatinMap(core);
  
  const first = mapped[0];
  
  // Bucket decision
  if (isDigit(first)) {
    // Keep digits but lowercase everything else
    return `2|${mapped.normalize('NFKC').toLowerCase()}`;
  }
  
  if (isLatinLetter(first)) {
    // For Latin titles: remove diacritics so É ~ E
    const folded = removeCombiningMarks(mapped);
    return `1|${folded.normalize('NFKC').toLowerCase()}`;
  }
  
  // Other scripts: keep them, but normalize + lowercase
  return `3|${mapped.normalize('NFKC').toLowerCase()}`;
}
