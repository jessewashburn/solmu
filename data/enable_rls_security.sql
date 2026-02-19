-- ========================================
-- Enable Row Level Security (RLS) for Supabase
-- Fixes security lints from Supabase Performance & Security checks
-- ========================================

-- This script:
-- 1. Enables RLS on all public tables
-- 2. Creates policies for appropriate access control
-- 3. Protects sensitive data (passwords, session keys)

-- ========================================
-- DJANGO SYSTEM TABLES
-- These should NOT be accessed via PostgREST API
-- RLS enabled with NO policies = complete protection
-- ========================================

-- Django Migrations (internal only)
ALTER TABLE public.django_migrations ENABLE ROW LEVEL SECURITY;
-- No policies needed - Django backend handles this

-- Django Content Types (internal only)
ALTER TABLE public.django_content_type ENABLE ROW LEVEL SECURITY;

-- Django Permissions (internal only)
ALTER TABLE public.auth_permission ENABLE ROW LEVEL SECURITY;

-- Django Groups (internal only)
ALTER TABLE public.auth_group ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.auth_group_permissions ENABLE ROW LEVEL SECURITY;

-- Django User Permissions (internal only)
ALTER TABLE public.auth_user_groups ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.auth_user_user_permissions ENABLE ROW LEVEL SECURITY;

-- Django Admin Log (internal only)
ALTER TABLE public.django_admin_log ENABLE ROW LEVEL SECURITY;

-- ========================================
-- SENSITIVE AUTHENTICATION TABLES
-- Critical: Contains passwords and session keys
-- ========================================

-- Auth User table - NEVER allow direct API access
ALTER TABLE public.auth_user ENABLE ROW LEVEL SECURITY;
-- No policies = Django backend is the only way to access this

-- Django Session table - NEVER allow direct API access
ALTER TABLE public.django_session ENABLE ROW LEVEL SECURITY;
-- No policies = Django backend handles session management

-- ========================================
-- APPLICATION DATA TABLES
-- Public read access, controlled write access
-- ========================================

-- Countries - Public read access
ALTER TABLE public.countries ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Countries are publicly readable"
ON public.countries
FOR SELECT
USING (true);

-- Data Sources - Public read access
ALTER TABLE public.data_sources ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Data sources are publicly readable"
ON public.data_sources
FOR SELECT
USING (true);

-- Instrumentation Categories - Public read access
ALTER TABLE public.instrumentation_categories ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Instrumentation categories are publicly readable"
ON public.instrumentation_categories
FOR SELECT
USING (true);

-- Composers - Public read access
ALTER TABLE public.composers ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Composers are publicly readable"
ON public.composers
FOR SELECT
USING (true);

-- Composer Aliases - Public read access
ALTER TABLE public.composer_aliases ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Composer aliases are publicly readable"
ON public.composer_aliases
FOR SELECT
USING (true);

-- Works - Public read access
ALTER TABLE public.works ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Works are publicly readable"
ON public.works
FOR SELECT
USING (true);

-- Work Search Index - Public read access
ALTER TABLE public.work_search_index ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Work search index is publicly readable"
ON public.work_search_index
FOR SELECT
USING (true);

-- Tags - Public read access
ALTER TABLE public.tags ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Tags are publicly readable"
ON public.tags
FOR SELECT
USING (true);

-- Work Tags - Public read access
ALTER TABLE public.work_tags ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Work tags are publicly readable"
ON public.work_tags
FOR SELECT
USING (true);

-- ========================================
-- USER SUGGESTIONS TABLE
-- Users can create and read their own suggestions
-- Admins can see all (handled via Django backend)
-- ========================================

ALTER TABLE public.user_suggestions ENABLE ROW LEVEL SECURITY;

-- Public read for approved/pending suggestions (optional - adjust as needed)
CREATE POLICY "User suggestions are publicly readable"
ON public.user_suggestions
FOR SELECT
USING (true);

-- Users can insert their own suggestions (Django backend validates)
-- Note: Since auth is handled by Django, direct inserts via API should be disabled
-- All access should go through Django REST API endpoints

-- ========================================
-- VERIFICATION
-- ========================================

-- List all tables with RLS status
-- Run this to verify RLS is enabled:
-- SELECT schemaname, tablename, rowsecurity 
-- FROM pg_tables 
-- WHERE schemaname = 'public' 
-- ORDER BY tablename;

-- List all policies
-- Run this to see all policies:
-- SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
-- FROM pg_policies
-- WHERE schemaname = 'public'
-- ORDER BY tablename, policyname;

-- ========================================
-- IMPORTANT NOTES
-- ========================================

-- 1. Django authentication tables (auth_user, django_session) have RLS enabled
--    but NO policies, meaning they cannot be accessed via PostgREST API at all.
--    This protects passwords and session keys.

-- 2. All application data tables allow public SELECT access because this is
--    a public music catalog. Write operations should only happen through
--    the Django REST API which has proper authentication.

-- 3. If you need to disable PostgREST API access to specific tables entirely,
--    you can do this in Supabase Project Settings > API > Tables and toggle
--    off the tables you don't want exposed.

-- 4. For maximum security, consider configuring PostgREST to only expose
--    a specific schema (not 'public') and create views in that schema
--    that proxy to your tables.
