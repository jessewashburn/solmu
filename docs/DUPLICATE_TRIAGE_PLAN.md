# Duplicate Triage & Merge — Plan and Results

## Overview

Three management commands form a pipeline to find, triage, and merge duplicate
works that arose from scraping both IMSLP and Sheerpluck for overlapping composers.

| Step | Command | Status |
|------|---------|--------|
| 1. Find candidates | `find_duplicate_candidates` | Done — 11,412 pairs |
| 2. Triage | `triage_duplicate_candidates` | Done — 1,989 duplicate/high, 1,000 duplicate/low |
| 3. Merge | `merge_duplicate_works` | Done (high confidence) — 1,173 merged |

## Commands

### 1. find_duplicate_candidates

[music/management/commands/find_duplicate_candidates.py](../music/management/commands/find_duplicate_candidates.py)

Scans all composers with 2+ works (9,357 of 15,082). For each composer,
compares every pair of works using:

- `difflib.SequenceMatcher` on normalized titles (accents stripped, parentheticals
  and catalog refs removed)
- +0.15 substring bonus (one normalized title contained in the other)
- +0.15 cross-source bonus (one has only `imslp_url`, other only `sheerpluck_url`)
- +0.05 each for matching instrumentation, year, or opus

```
python manage.py find_duplicate_candidates --threshold 0.75 --output duplicate_candidates.csv
```

### 2. triage_duplicate_candidates

[music/management/commands/triage_duplicate_candidates.py](../music/management/commands/triage_duplicate_candidates.py)

Reads the candidate CSV, fetches both Works, applies deterministic rules in order
(first match wins), and writes a triaged CSV.

```
python manage.py triage_duplicate_candidates \
    --input duplicate_candidates.csv \
    --output duplicate_candidates_triaged.csv
```

**Triage rules (applied in order):**

1. **Movement number / opus / key mismatch → distinct (high)**
   Both titles contain a number (No., Nr., Roman numeral after a noun, ordinal)
   and the numbers differ. Or opus_number fields differ. Or key signatures differ
   ("in A major" vs "in D minor").

2. **Annotated-form match → duplicate (high)**
   Normalized titles are equal or one is a substring of the other, and
   instrumentation categories are compatible (same or one is null).
   Example: `Chôros No.1` vs `Chôros No.1, W161 (Villa-Lobos, Heitor)`.

3. **Cross-source + normalized equality → duplicate (high)**
   One work has only `imslp_url`, the other only `sheerpluck_url`, and normalized
   titles match exactly.

4. **Instrumentation mismatch → distinct (medium)**
   Both have non-null `instrumentation_category_id` and they differ.

5. **Year conflict → distinct (medium)**
   Both have `composition_year` and differ by >2 years.

6. **Fall-through → low confidence**
   Score ≥ 0.9 → duplicate/low, else distinct/low.

**Winner selection (`keep_id`):** count non-null fields across `subtitle`,
`composition_year`, `opus_number`, `catalog_number`, `description`, `imslp_url`,
`sheerpluck_url`, `youtube_url`, `instrumentation_detail`. Higher count wins.
Lower ID breaks ties.

### 3. merge_duplicate_works

[music/management/commands/merge_duplicate_works.py](../music/management/commands/merge_duplicate_works.py)

Reads the triaged CSV, filters to `verdict=duplicate` rows at or above a
confidence threshold, and for each pair:

1. Unions null-on-winner fields from the loser (URLs, subtitle, description,
   opus, catalog number, year, instrumentation detail, movements, key, etc.)
2. Transfers `work_tags` from loser to winner (deduplicates by tag_id)
3. Sums `view_count` if `--force-views` is set
4. Deletes the loser — all inside a single transaction

```
python manage.py merge_duplicate_works --dry-run                  # preview
python manage.py merge_duplicate_works --confidence high          # real run
python manage.py merge_duplicate_works --confidence low --force-views  # all
```

**Safety:**
- Skips pairs where the loser has `view_count > 0` unless `--force-views`
- Handles chains (A→B merged, then B→C appears later → resolves correctly)
- Writes `merge_log.csv` with per-row action, fields unioned, tags moved

## Results — 2026-04-15 high-confidence merge

**Input:** 11,412 candidate pairs across 9,357 composers

**Triage breakdown:**

| Verdict | Confidence | Count |
|---------|-----------|-------|
| duplicate | high | 1,989 |
| duplicate | low | 1,000 |
| distinct | high | 3,733 |
| distinct | medium | 2,715 |
| distinct | low | 1,975 |

**High-confidence merge results:**

| Metric | Count |
|--------|-------|
| Merged | 1,173 |
| Skipped (chain / already merged) | 813 |
| Skipped (view_count > 0) | 3 |
| Skipped (missing work) | 0 |
| Errors | 1 (transient connection drop — pair actually merged) |

## Remaining work

- **3 pairs skipped for view_count > 0** — review manually, merge with `--force-views` if appropriate
- **1,000 duplicate/low rows** — need manual review before merging. These are fuzzy matches (similarity ≥ 0.9) where no strong deterministic rule fired. Run with `--confidence low` after review.
- **Regenerate CSVs if re-running** — after merging, `duplicate_candidates.csv` is stale (loser IDs are gone). Re-run `find_duplicate_candidates` to pick up any remaining duplicates below the original threshold or missed by normalization.
