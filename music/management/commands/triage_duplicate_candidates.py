"""
Triage duplicate candidate pairs into duplicate / related / distinct verdicts.
See docs/DUPLICATE_TRIAGE_PLAN.md for the rule definitions.
"""

import csv
import re
import unicodedata
from difflib import SequenceMatcher

from django.core.management.base import BaseCommand

from music.models import Work


PARENS_RE = re.compile(r"\s*\([^)]*\)")
CATALOG_RE = re.compile(
    r"\b(?:op|opus|w|ww|bwv|kv|k|hob|d|rv|s|woo|mwv|b)\.?\s*\d+[a-z0-9/\-]*",
    re.IGNORECASE,
)
NONALNUM_RE = re.compile(r"[^a-z0-9]+")
TRAILING_INSTRUMENT_RE = re.compile(
    r"\b(for\s+guitar|guitar\s+solo|\(guitar\))\b", re.IGNORECASE
)

NO_NUM_RE = re.compile(
    r"(?:no\.?|nr\.?|num\.?|n°|#)\s*(\d+)", re.IGNORECASE
)
ORDINAL_RE = re.compile(r"\b(\d+)(?:st|nd|rd|th)\b", re.IGNORECASE)
ROMAN_AFTER_NOUN_RE = re.compile(
    r"\b(?:prelude|preludio|etude|estudio|study|sonata|sonatina|fugue|fuga|"
    r"choros|chôros|danza|variation|variations|movement|mvt|part|piece|"
    r"suite|nocturne|intermezzo|caprice|capriccio|waltz|vals|minuet|minuetto|"
    r"scherzo|impromptu|rondo|canzona|canzone|fantasia|tango)\s+([ivx]+)\b",
    re.IGNORECASE,
)
KEY_RE = re.compile(
    r"\bin\s+([a-g](?:\s*[#b♯♭])?)\s*(major|minor|maj|min|m)\b",
    re.IGNORECASE,
)

ROMAN_MAP = {
    "i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6, "vii": 7,
    "viii": 8, "ix": 9, "x": 10, "xi": 11, "xii": 12, "xiii": 13,
    "xiv": 14, "xv": 15, "xvi": 16, "xvii": 17, "xviii": 18, "xix": 19,
    "xx": 20,
}

NON_NULL_BONUS_FIELDS = (
    "subtitle", "composition_year", "opus_number", "catalog_number",
    "description", "imslp_url", "sheerpluck_url", "youtube_url",
    "instrumentation_detail",
)


def strip_accents(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")


def normalize_title(title: str, composer_last: str = "") -> str:
    if not title:
        return ""
    t = strip_accents(title).lower()
    t = PARENS_RE.sub(" ", t)
    t = CATALOG_RE.sub(" ", t)
    t = TRAILING_INSTRUMENT_RE.sub(" ", t)
    if composer_last:
        last_norm = strip_accents(composer_last).lower()
        t = re.sub(rf"\b{re.escape(last_norm)}\b", " ", t)
    t = NONALNUM_RE.sub(" ", t)
    return " ".join(t.split())


def extract_movement_numbers(title: str) -> set:
    """Return set of integer movement numbers implied by the title."""
    if not title:
        return set()
    t = strip_accents(title)
    nums = set()
    for m in NO_NUM_RE.finditer(t):
        nums.add(int(m.group(1)))
    for m in ORDINAL_RE.finditer(t):
        nums.add(int(m.group(1)))
    for m in ROMAN_AFTER_NOUN_RE.finditer(t):
        roman = m.group(1).lower()
        if roman in ROMAN_MAP:
            nums.add(ROMAN_MAP[roman])
    return nums


def extract_key(title: str) -> str:
    if not title:
        return ""
    m = KEY_RE.search(strip_accents(title))
    if not m:
        return ""
    note = re.sub(r"\s+", "", m.group(1)).lower()
    mode = m.group(2).lower()
    mode = "major" if mode.startswith("maj") else "minor"
    return f"{note}-{mode}"


def non_null_score(w: Work) -> int:
    return sum(1 for f in NON_NULL_BONUS_FIELDS if getattr(w, f, None))


def pick_winner(w1: Work, w2: Work) -> int:
    s1, s2 = non_null_score(w1), non_null_score(w2)
    if s1 != s2:
        return w1.id if s1 > s2 else w2.id
    return min(w1.id, w2.id)


def triage(w1: Work, w2: Work, score: float) -> tuple:
    """Return (verdict, confidence, keep_id_or_None, rationale)."""
    t1, t2 = w1.title or "", w2.title or ""
    last = w1.composer.last_name if w1.composer else ""
    n1 = normalize_title(t1, last)
    n2 = normalize_title(t2, last)

    nums1 = extract_movement_numbers(t1)
    nums2 = extract_movement_numbers(t2)

    # Rule 1: movement / opus / key mismatch → DISTINCT
    if nums1 and nums2 and not (nums1 & nums2):
        return ("distinct", "high", None,
                f"movement-number mismatch {sorted(nums1)} vs {sorted(nums2)}")

    if w1.opus_number and w2.opus_number:
        o1 = w1.opus_number.strip().lower()
        o2 = w2.opus_number.strip().lower()
        if o1 and o2 and o1 != o2:
            return ("distinct", "high", None,
                    f"opus mismatch {w1.opus_number} vs {w2.opus_number}")

    key1, key2 = extract_key(t1), extract_key(t2)
    if key1 and key2 and key1 != key2:
        return ("distinct", "high", None,
                f"key mismatch {key1} vs {key2}")

    # Rule 2: annotated-form match → DUPLICATE
    same_inst = (
        w1.instrumentation_category_id == w2.instrumentation_category_id
        or not w1.instrumentation_category_id
        or not w2.instrumentation_category_id
    )
    if same_inst and n1 and n2 and (n1 == n2 or n1 in n2 or n2 in n1):
        return ("duplicate", "high", pick_winner(w1, w2),
                "normalized-title match + compatible instrumentation")

    # Rule 3: cross-source + normalized equality → DUPLICATE
    w1_imslp, w1_sp = bool(w1.imslp_url), bool(w1.sheerpluck_url)
    w2_imslp, w2_sp = bool(w2.imslp_url), bool(w2.sheerpluck_url)
    cross_source = (
        (w1_imslp and not w1_sp and w2_sp and not w2_imslp)
        or (w2_imslp and not w2_sp and w1_sp and not w1_imslp)
    )
    if cross_source and n1 and n1 == n2:
        return ("duplicate", "high", pick_winner(w1, w2),
                "cross-source + normalized-title equality")

    # Rule 4: instrumentation mismatch → DISTINCT
    if (
        w1.instrumentation_category_id
        and w2.instrumentation_category_id
        and w1.instrumentation_category_id != w2.instrumentation_category_id
    ):
        return ("distinct", "medium", None, "instrumentation category differs")

    # Rule 5: year conflict → DISTINCT
    if (
        w1.composition_year
        and w2.composition_year
        and abs(w1.composition_year - w2.composition_year) > 2
    ):
        return ("distinct", "medium", None,
                f"year mismatch {w1.composition_year} vs {w2.composition_year}")

    # Rule 6: fall-through
    sim = SequenceMatcher(None, n1, n2).ratio() if n1 and n2 else 0.0
    if score >= 0.9 or sim >= 0.9:
        return ("duplicate", "low", pick_winner(w1, w2),
                f"fall-through, fuzzy sim={sim:.2f}")
    return ("distinct", "low", None, f"fall-through, fuzzy sim={sim:.2f}")


class Command(BaseCommand):
    help = "Triage duplicate candidate pairs from a CSV into verdicts."

    def add_arguments(self, parser):
        parser.add_argument(
            "--input", default="duplicate_candidates.csv",
            help="Input CSV produced by find_duplicate_candidates",
        )
        parser.add_argument(
            "--output", default="duplicate_candidates_triaged.csv",
            help="Output triaged CSV path",
        )

    def handle(self, *args, **opts):
        input_path = opts["input"]
        output_path = opts["output"]

        with open(input_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        self.stdout.write(f"Loaded {len(rows)} candidate rows from {input_path}")

        ids = set()
        for r in rows:
            ids.add(int(r["work_a_id"]))
            ids.add(int(r["work_b_id"]))

        self.stdout.write(f"Fetching {len(ids)} works...")
        works = (
            Work.objects
            .filter(id__in=ids)
            .select_related("composer", "instrumentation_category")
        )
        work_by_id = {w.id: w for w in works}

        counts = {"duplicate": 0, "distinct": 0, "related": 0}
        conf_counts = {"high": 0, "medium": 0, "low": 0}

        out_rows = []
        missing = 0
        for r in rows:
            a = work_by_id.get(int(r["work_a_id"]))
            b = work_by_id.get(int(r["work_b_id"]))
            if not a or not b:
                missing += 1
                continue

            verdict, confidence, keep_id, rationale = triage(
                a, b, float(r["score"])
            )
            counts[verdict] += 1
            conf_counts[confidence] += 1

            out = dict(r)
            out["verdict"] = verdict
            out["confidence"] = confidence
            out["keep_id"] = keep_id if keep_id is not None else ""
            out["rationale"] = rationale
            out_rows.append(out)

        # Sort by verdict then confidence then score desc for easy review
        conf_rank = {"high": 0, "medium": 1, "low": 2}
        verdict_rank = {"duplicate": 0, "related": 1, "distinct": 2}
        out_rows.sort(key=lambda r: (
            verdict_rank.get(r["verdict"], 3),
            conf_rank.get(r["confidence"], 3),
            -float(r["score"]),
        ))

        fieldnames = list(rows[0].keys()) + [
            "verdict", "confidence", "keep_id", "rationale"
        ]
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(out_rows)

        self.stdout.write(self.style.SUCCESS(
            f"\nWrote {len(out_rows)} triaged rows to {output_path}"
        ))
        if missing:
            self.stdout.write(self.style.WARNING(
                f"Skipped {missing} rows referencing missing work IDs"
            ))
        self.stdout.write(f"Verdicts: {counts}")
        self.stdout.write(f"Confidence: {conf_counts}")
