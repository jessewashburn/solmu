"""
Merge duplicate Work records based on a triaged CSV.

For each row with verdict=duplicate, copy any fields that are null on the
winner but populated on the loser, transfer work_tags, union URLs, then
delete the loser. Use --dry-run first.
"""

import csv

from django.core.management.base import BaseCommand
from django.db import transaction

from music.models import Work, WorkTag


# Fields to union (copy from loser to winner if winner's is empty/null)
UNION_FIELDS = (
    "subtitle",
    "opus_number",
    "catalog_number",
    "composition_year",
    "composition_year_approx",
    "duration_minutes",
    "instrumentation_detail",
    "difficulty_level",
    "description",
    "movements",
    "key_signature",
    "imslp_url",
    "sheerpluck_url",
    "youtube_url",
    "score_url",
    "external_id",
)

CONFIDENCE_ORDER = {"high": 0, "medium": 1, "low": 2}


def is_empty(val):
    if val is None:
        return True
    if isinstance(val, str) and not val.strip():
        return True
    return False


def union_fields(winner: Work, loser: Work) -> list:
    """Copy null-on-winner fields from loser. Return list of changed field names."""
    changed = []
    for f in UNION_FIELDS:
        w_val = getattr(winner, f)
        l_val = getattr(loser, f)
        if is_empty(w_val) and not is_empty(l_val):
            setattr(winner, f, l_val)
            changed.append(f)
    return changed


def transfer_tags(winner: Work, loser: Work) -> int:
    """Move work_tags from loser to winner, skipping duplicates. Returns count moved."""
    existing_tag_ids = set(
        WorkTag.objects.filter(work=winner).values_list("tag_id", flat=True)
    )
    loser_tags = WorkTag.objects.filter(work=loser)
    moved = 0
    for wt in loser_tags:
        if wt.tag_id in existing_tag_ids:
            wt.delete()
        else:
            wt.work = winner
            wt.save()
            moved += 1
    return moved


class Command(BaseCommand):
    help = "Merge duplicate works from a triaged CSV (winner keeps, loser deleted)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--input", default="duplicate_candidates_triaged.csv",
            help="Triaged CSV from triage_duplicate_candidates",
        )
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Report what would happen without changing the DB",
        )
        parser.add_argument(
            "--confidence", default="high",
            choices=["high", "medium", "low"],
            help="Minimum confidence to process (default: high). "
                 "high only, medium+ includes medium and high, low includes all.",
        )
        parser.add_argument(
            "--force-views", action="store_true",
            help="Allow merging even when the losing record has view_count > 0",
        )
        parser.add_argument(
            "--log", default="merge_log.csv",
            help="Path to write per-row merge log",
        )

    def handle(self, *args, **opts):
        input_path = opts["input"]
        dry_run = opts["dry_run"]
        min_conf_rank = CONFIDENCE_ORDER[opts["confidence"]]
        force_views = opts["force_views"]
        log_path = opts["log"]

        with open(input_path, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        # Filter to relevant rows
        eligible = [
            r for r in rows
            if r["verdict"] == "duplicate"
            and r["keep_id"]
            and CONFIDENCE_ORDER.get(r["confidence"], 99) <= min_conf_rank
        ]

        self.stdout.write(
            f"Input: {len(rows)} rows, {len(eligible)} eligible "
            f"(verdict=duplicate, confidence<={opts['confidence']})"
        )
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — no DB changes"))

        # Track merges so chains work: if A is merged into B, and B→C later,
        # we resolve "A" to B.
        merged_into = {}  # loser_id -> winner_id

        def resolve(wid: int) -> int:
            seen = set()
            while wid in merged_into and wid not in seen:
                seen.add(wid)
                wid = merged_into[wid]
            return wid

        log_rows = []
        stats = {
            "merged": 0,
            "skipped_views": 0,
            "skipped_missing": 0,
            "skipped_same": 0,
            "errors": 0,
        }

        for r in eligible:
            try:
                a_id = int(r["work_a_id"])
                b_id = int(r["work_b_id"])
                keep_id = int(r["keep_id"])
            except (ValueError, KeyError):
                stats["errors"] += 1
                continue

            loser_id = b_id if keep_id == a_id else a_id
            winner_id = resolve(keep_id)
            loser_id = resolve(loser_id)

            if winner_id == loser_id:
                stats["skipped_same"] += 1
                continue

            try:
                winner = Work.objects.get(id=winner_id)
                loser = Work.objects.get(id=loser_id)
            except Work.DoesNotExist:
                stats["skipped_missing"] += 1
                log_rows.append({
                    "winner_id": winner_id, "loser_id": loser_id,
                    "action": "skipped", "reason": "work missing",
                    "fields_unioned": "", "tags_moved": "",
                    "views_transferred": "",
                })
                continue

            if loser.view_count > 0 and not force_views:
                stats["skipped_views"] += 1
                log_rows.append({
                    "winner_id": winner_id, "loser_id": loser_id,
                    "action": "skipped",
                    "reason": f"loser has view_count={loser.view_count}",
                    "fields_unioned": "", "tags_moved": "",
                    "views_transferred": "",
                })
                continue

            if dry_run:
                # Just compute what would change, don't persist
                changed = []
                for f in UNION_FIELDS:
                    if is_empty(getattr(winner, f)) and not is_empty(getattr(loser, f)):
                        changed.append(f)
                log_rows.append({
                    "winner_id": winner_id, "loser_id": loser_id,
                    "action": "would-merge", "reason": "",
                    "fields_unioned": "|".join(changed),
                    "tags_moved": "(dry-run)",
                    "views_transferred": loser.view_count,
                })
                stats["merged"] += 1
                merged_into[loser_id] = winner_id
                continue

            try:
                with transaction.atomic():
                    changed = union_fields(winner, loser)
                    tags_moved = transfer_tags(winner, loser)
                    views_transferred = loser.view_count
                    if views_transferred and force_views:
                        winner.view_count = (winner.view_count or 0) + views_transferred
                    if changed or (views_transferred and force_views):
                        winner.save()
                    loser.delete()

                merged_into[loser_id] = winner_id
                stats["merged"] += 1
                log_rows.append({
                    "winner_id": winner_id, "loser_id": loser_id,
                    "action": "merged", "reason": "",
                    "fields_unioned": "|".join(changed),
                    "tags_moved": tags_moved,
                    "views_transferred": views_transferred,
                })

                if stats["merged"] % 200 == 0:
                    self.stdout.write(f"  merged {stats['merged']}...")
            except Exception as e:
                stats["errors"] += 1
                log_rows.append({
                    "winner_id": winner_id, "loser_id": loser_id,
                    "action": "error", "reason": str(e),
                    "fields_unioned": "", "tags_moved": "",
                    "views_transferred": "",
                })

        # Write log
        with open(log_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "winner_id", "loser_id", "action", "reason",
                "fields_unioned", "tags_moved", "views_transferred",
            ])
            writer.writeheader()
            writer.writerows(log_rows)

        self.stdout.write(self.style.SUCCESS(
            f"\n{'Would merge' if dry_run else 'Merged'}: {stats['merged']}"
        ))
        self.stdout.write(f"Skipped (view_count>0): {stats['skipped_views']}")
        self.stdout.write(f"Skipped (missing work): {stats['skipped_missing']}")
        self.stdout.write(f"Skipped (already merged): {stats['skipped_same']}")
        self.stdout.write(f"Errors: {stats['errors']}")
        self.stdout.write(f"Log: {log_path}")
