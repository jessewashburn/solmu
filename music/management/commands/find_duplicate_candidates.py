"""
Find candidate duplicate works (fuzzy match, per composer) and write a CSV
for manual review. Combines title similarity with cross-source hints (one
work has imslp_url, another has sheerpluck_url) and shared metadata.
"""

import csv
import re
import unicodedata
from difflib import SequenceMatcher

from django.core.management.base import BaseCommand
from django.db.models import Count

from music.models import Work


PARENS_RE = re.compile(r"\s*\([^)]*\)")
CATALOG_RE = re.compile(
    r"\b(?:op|opus|w|ww|bwv|kv|k|hob|d|rv|s|woo|mwv|b)\.?\s*\d+[a-z0-9/\-]*",
    re.IGNORECASE,
)
NONALNUM_RE = re.compile(r"[^a-z0-9]+")


def normalize_title(title: str) -> str:
    if not title:
        return ""
    t = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    t = t.lower()
    t = PARENS_RE.sub(" ", t)
    t = CATALOG_RE.sub(" ", t)
    t = NONALNUM_RE.sub(" ", t)
    return " ".join(t.split())


def title_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def score_pair(w1, w2, norm1, norm2):
    """Return (score, reasons) for a candidate pair. Score 0..1-ish."""
    reasons = []
    sim = title_similarity(norm1, norm2)

    if norm1 and norm2 and (norm1 in norm2 or norm2 in norm1):
        substring_bonus = 0.15
        reasons.append("substring")
    else:
        substring_bonus = 0.0

    score = sim + substring_bonus

    # Cross-source hint: one has imslp, other has sheerpluck
    w1_imslp = bool(w1.imslp_url)
    w1_sp = bool(w1.sheerpluck_url)
    w2_imslp = bool(w2.imslp_url)
    w2_sp = bool(w2.sheerpluck_url)
    if (w1_imslp and not w1_sp and w2_sp and not w2_imslp) or (
        w2_imslp and not w2_sp and w1_sp and not w1_imslp
    ):
        score += 0.15
        reasons.append("cross-source")

    if (
        w1.instrumentation_category_id
        and w1.instrumentation_category_id == w2.instrumentation_category_id
    ):
        score += 0.05
        reasons.append("same-instrumentation")

    if (
        w1.composition_year
        and w2.composition_year
        and w1.composition_year == w2.composition_year
    ):
        score += 0.05
        reasons.append("same-year")

    if (
        w1.opus_number
        and w2.opus_number
        and w1.opus_number.strip().lower() == w2.opus_number.strip().lower()
    ):
        score += 0.05
        reasons.append("same-opus")

    return score, reasons


def sources_label(w):
    parts = []
    if w.imslp_url:
        parts.append("imslp")
    if w.sheerpluck_url:
        parts.append("sheerpluck")
    if w.data_source_id:
        parts.append(f"ds={w.data_source_id}")
    return "|".join(parts) or "-"


class Command(BaseCommand):
    help = "Find candidate duplicate works per composer and write a CSV for review."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            default="duplicate_candidates.csv",
            help="Output CSV path (default: duplicate_candidates.csv)",
        )
        parser.add_argument(
            "--threshold",
            type=float,
            default=0.75,
            help="Minimum score to include a pair (default: 0.75)",
        )
        parser.add_argument(
            "--min-works",
            type=int,
            default=2,
            help="Only scan composers with at least N works (default: 2)",
        )
        parser.add_argument(
            "--limit-composers",
            type=int,
            default=None,
            help="Cap number of composers scanned (for testing)",
        )

    def handle(self, *args, **opts):
        threshold = opts["threshold"]
        output = opts["output"]

        composer_ids = (
            Work.objects.values("composer_id")
            .annotate(n=Count("id"))
            .filter(n__gte=opts["min_works"])
            .order_by("composer_id")
            .values_list("composer_id", flat=True)
        )
        if opts["limit_composers"]:
            composer_ids = list(composer_ids[: opts["limit_composers"]])
        else:
            composer_ids = list(composer_ids)

        self.stdout.write(
            f"Scanning {len(composer_ids)} composers (threshold={threshold})..."
        )

        rows = []
        for i, cid in enumerate(composer_ids, 1):
            works = list(
                Work.objects.filter(composer_id=cid).select_related("composer")
            )
            if len(works) < 2:
                continue

            norms = [normalize_title(w.title) for w in works]

            for a in range(len(works)):
                for b in range(a + 1, len(works)):
                    w1, w2 = works[a], works[b]
                    score, reasons = score_pair(w1, w2, norms[a], norms[b])
                    if score >= threshold:
                        rows.append(
                            {
                                "score": round(score, 3),
                                "reasons": ",".join(reasons),
                                "composer": w1.composer.full_name,
                                "work_a_id": w1.id,
                                "work_a_title": w1.title,
                                "work_a_sources": sources_label(w1),
                                "work_b_id": w2.id,
                                "work_b_title": w2.title,
                                "work_b_sources": sources_label(w2),
                            }
                        )

            if i % 100 == 0:
                self.stdout.write(
                    f"  {i}/{len(composer_ids)} composers scanned, "
                    f"{len(rows)} candidates so far"
                )

        rows.sort(key=lambda r: r["score"], reverse=True)

        with open(output, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "score",
                    "reasons",
                    "composer",
                    "work_a_id",
                    "work_a_title",
                    "work_a_sources",
                    "work_b_id",
                    "work_b_title",
                    "work_b_sources",
                ],
            )
            writer.writeheader()
            writer.writerows(rows)

        self.stdout.write(
            self.style.SUCCESS(
                f"Wrote {len(rows)} candidate pairs to {output}"
            )
        )
