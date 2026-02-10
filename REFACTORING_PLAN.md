# Refactoring Plan - Low Hanging Fruit

## Phase 1: Backend Cleanup ✅ COMPLETED
**Priority: High | Effort: Low | Impact: Code cleanliness**
**Completed: 2026-02-09 | Commit: 123896b**

- [x] Remove commented-out database configurations in `settings.py`
  - Lines 105-120: Commented MySQL/SQLite configs
  - **Why**: Dead code that confuses developers
  - **Risk**: None (already using PostgreSQL)
  - **Result**: Removed 18 lines of commented code
  
- [x] Fix duplicate `STATIC_ROOT` definition in `settings.py`
  - Line 159 and 225 both define `STATIC_ROOT`
  - **Why**: Duplicate configuration is confusing
  - **Risk**: Low (second definition overrides first)
  - **Result**: Removed early definition, kept production version at line 225

## Phase 2: Frontend Type Consolidation ✅ COMPLETED
**Priority: Medium | Effort: Low | Impact: Type safety & maintainability**
**Completed: 2026-02-09 | Commit: e2c9633**

- [x] Consolidate duplicate interface definitions
  - `Work` interface defined in: WorkListPage, ComposerListPage, ExpandableComposerRow, HomePage
  - `Composer` interface defined in: AdminComposers, ComposerListPage, ExpandableComposerRow
  - **Why**: Single source of truth for types, import from `types/index.ts`
  - **Risk**: Low (just imports, but need to verify field compatibility)
  - **Result**: 
    - Fixed `year_composed` → `composition_year` bug in types/index.ts
    - Created `ComposerListItem` and `WorkListItem` for list endpoints
    - Removed 58 lines of duplicate type definitions
    - All components now import from centralized types
  - **Files updated**: 
    - ✅ `frontend/src/pages/WorkListPage.tsx`
    - ✅ `frontend/src/pages/ComposerListPage.tsx`
    - ✅ `frontend/src/pages/AdminComposers.tsx`
    - ✅ `frontend/src/components/features/composers/ExpandableComposerRow/ExpandableComposerRow.tsx`
    - ✅ `frontend/src/types/index.ts`

## Phase 3: Component Extraction
**Priority: Medium | Effort: Medium | Impact: Reusability**

- [ ] Extract `ExternalLinks` component
  - Duplicate code in `HomePage.tsx` and `WorkDetailPage.tsx` for rendering IMSLP/YouTube/SheerPluck/Score links
  - **Why**: DRY principle, consistent styling
  - **Risk**: Low (UI component only)
  - **Pattern**: 
    ```tsx
    <ExternalLinks 
      imslpUrl={work.imslp_url}
      sheerpluckUrl={work.sheerpluck_url}
      youtubeUrl={work.youtube_url}
      scoreUrl={work.score_url}
    />
    ```

## Phase 4: Configuration Improvements
**Priority: Low | Effort: Low | Impact: Developer experience**

- [ ] Add `.env.example` files
  - Backend: Document all required environment variables
  - Frontend: Document VITE_API_URL
  - **Why**: New developers need to know what env vars are required
  - **Risk**: None

- [ ] Centralize API endpoint URLs
  - Multiple doc files reference endpoints (API_DOCUMENTATION.md, QUICK_REFERENCE.md, README.md)
  - **Why**: Single source of truth for API contract
  - **Risk**: None (documentation only)

## Phase 5: Documentation Consolidation
**Priority: Low | Effort: Medium | Impact: Documentation clarity**

- [ ] Consolidate API endpoint documentation
  - `docs/API_DOCUMENTATION.md`, `frontend/QUICK_REFERENCE.md`, `README.md` all document endpoints
  - **Why**: Avoid documentation drift
  - **Risk**: None

- [ ] Update outdated README sections
  - Frontend README references template boilerplate
  - **Why**: Professional appearance
  - **Risk**: None

## Phase 6: Testing Infrastructure
**Priority: High | Effort: High | Impact: Code quality**

- [ ] Add basic test setup
  - No test files found in project
  - **Why**: Prevent regressions, enable confident refactoring
  - **Risk**: Medium (requires learning testing frameworks)
  - **Scope**: Start with model tests, then API endpoint tests

## Phase 7: Code Organization
**Priority: Low | Effort: Medium | Impact: Maintainability**

- [ ] Extract utility functions
  - `is_living` logic in multiple places (models.py, admin_views.py, utils.py)
  - Date formatting patterns
  - **Why**: Consistency and reusability
  - **Risk**: Low

- [ ] Create constants file
  - Hardcoded values like "Solo", period choices, difficulty levels
  - **Why**: Easy to modify, prevents typos
  - **Risk**: Low

## Notes
- Start with Phase 1 (lowest risk, immediate impact)
- Each phase can be committed separately
- Test thoroughly after Phase 2 (type changes)
- Phases 3+ can be done in any order based on priority

## Completion Tracking
- ✅ = Completed
- 🚧 = In Progress
- ⏳ = Blocked
- ❌ = Cancelled
