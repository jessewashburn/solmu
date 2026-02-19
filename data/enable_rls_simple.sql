-- Quick RLS Enable Script for Supabase
-- Run this in Supabase Dashboard > SQL Editor
-- This enables Row Level Security (RLS) on all tables

-- Enable RLS on all Django system tables (no policies = complete protection)
ALTER TABLE IF EXISTS public.django_migrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.django_content_type ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.auth_permission ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.auth_group ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.auth_group_permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.auth_user_groups ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.auth_user_user_permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.django_admin_log ENABLE ROW LEVEL SECURITY;

-- Enable RLS on sensitive tables (passwords & sessions)
ALTER TABLE IF EXISTS public.auth_user ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.django_session ENABLE ROW LEVEL SECURITY;

-- Enable RLS on application data tables
ALTER TABLE IF EXISTS public.countries ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.data_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.instrumentation_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.composers ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.composer_aliases ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.works ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.work_search_index ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.work_tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.user_suggestions ENABLE ROW LEVEL SECURITY;

-- Create public read policies for application data
-- (Django backend handles all writes via authenticated API)

DO $$
BEGIN
    -- Countries
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'countries' AND policyname = 'Countries are publicly readable') THEN
        CREATE POLICY "Countries are publicly readable" ON public.countries FOR SELECT USING (true);
    END IF;

    -- Data Sources
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'data_sources' AND policyname = 'Data sources are publicly readable') THEN
        CREATE POLICY "Data sources are publicly readable" ON public.data_sources FOR SELECT USING (true);
    END IF;

    -- Instrumentation Categories
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'instrumentation_categories' AND policyname = 'Instrumentation categories are publicly readable') THEN
        CREATE POLICY "Instrumentation categories are publicly readable" ON public.instrumentation_categories FOR SELECT USING (true);
    END IF;

    -- Composers
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'composers' AND policyname = 'Composers are publicly readable') THEN
        CREATE POLICY "Composers are publicly readable" ON public.composers FOR SELECT USING (true);
    END IF;

    -- Composer Aliases
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'composer_aliases' AND policyname = 'Composer aliases are publicly readable') THEN
        CREATE POLICY "Composer aliases are publicly readable" ON public.composer_aliases FOR SELECT USING (true);
    END IF;

    -- Works
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'works' AND policyname = 'Works are publicly readable') THEN
        CREATE POLICY "Works are publicly readable" ON public.works FOR SELECT USING (true);
    END IF;

    -- Work Search Index
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'work_search_index' AND policyname = 'Work search index is publicly readable') THEN
        CREATE POLICY "Work search index is publicly readable" ON public.work_search_index FOR SELECT USING (true);
    END IF;

    -- Tags
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'tags' AND policyname = 'Tags are publicly readable') THEN
        CREATE POLICY "Tags are publicly readable" ON public.tags FOR SELECT USING (true);
    END IF;

    -- Work Tags
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'work_tags' AND policyname = 'Work tags are publicly readable') THEN
        CREATE POLICY "Work tags are publicly readable" ON public.work_tags FOR SELECT USING (true);
    END IF;

    -- User Suggestions
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'user_suggestions' AND policyname = 'User suggestions are publicly readable') THEN
        CREATE POLICY "User suggestions are publicly readable" ON public.user_suggestions FOR SELECT USING (true);
    END IF;
END $$;

-- Verify RLS is enabled
SELECT 
    tablename,
    CASE WHEN rowsecurity THEN 'ENABLED' ELSE 'DISABLED' END as rls_status
FROM pg_tables 
WHERE schemaname = 'public' 
    AND tablename NOT LIKE 'pg_%'
ORDER BY tablename;
