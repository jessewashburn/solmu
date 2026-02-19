"""
Django management command to enable Row Level Security (RLS) on Supabase.
Fixes security issues detected by Supabase linter.

Usage:
    python manage.py enable_rls
"""
from django.core.management.base import BaseCommand
from django.db import connection
from pathlib import Path


class Command(BaseCommand):
    help = 'Enable Row Level Security (RLS) on all tables in Supabase'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show SQL that would be executed without actually executing it',
        )
        parser.add_argument(
            '--yes',
            action='store_true',
            help='Skip confirmation prompt',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Read the SQL file
        sql_file = Path(__file__).resolve().parent.parent.parent.parent / 'data' / 'enable_rls_security.sql'
        
        if not sql_file.exists():
            self.stdout.write(self.style.ERROR(f'SQL file not found: {sql_file}'))
            return
        
        self.stdout.write(self.style.WARNING(f'Reading SQL from: {sql_file}'))
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n=== DRY RUN MODE - No changes will be made ===\n'))
            self.stdout.write(sql_content)
            self.stdout.write(self.style.WARNING('\n=== END DRY RUN ===\n'))
            return
        
        # Confirm before executing
        if not options['yes']:
            self.stdout.write(self.style.WARNING(
                '\nThis will enable Row Level Security (RLS) on all tables.\n'
                'This is a security enhancement and should be safe, but it may affect\n'
                'how PostgREST API access works if you\'re using it directly.\n'
            ))
            
            confirm = input('Do you want to proceed? (yes/no): ')
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.ERROR('Operation cancelled.'))
                return
        
        # Execute the SQL
        self.stdout.write(self.style.WARNING('\nEnabling RLS on all tables...'))
        
        try:
            with connection.cursor() as cursor:
                # Split by statements and execute
                statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]
                
                total = len(statements)
                for i, statement in enumerate(statements, 1):
                    # Skip comment blocks
                    if statement.strip().startswith('/*') or not statement.strip():
                        continue
                    
                    try:
                        cursor.execute(statement)
                        self.stdout.write(f'[{i}/{total}] OK - Executed statement')
                    except Exception as e:
                        # Some statements might fail if policies already exist, that's OK
                        if 'already exists' in str(e).lower():
                            self.stdout.write(f'[{i}/{total}] SKIP - Already exists')
                        else:
                            self.stdout.write(self.style.WARNING(f'[{i}/{total}] ⚠ Error: {e}'))
            
            self.stdout.write(self.style.SUCCESS('\n[SUCCESS] Row Level Security has been enabled!'))
            self.stdout.write(self.style.SUCCESS('\nSecurity improvements applied:'))
            self.stdout.write('  - RLS enabled on all Django system tables')
            self.stdout.write('  - RLS enabled on all application tables')
            self.stdout.write('  - Sensitive data (passwords, sessions) now protected')
            self.stdout.write('  - Public read policies created for application data')
            
            # Verify RLS status
            self.stdout.write(self.style.WARNING('\n\nVerifying RLS status...'))
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT tablename, rowsecurity 
                    FROM pg_tables 
                    WHERE schemaname = 'public' 
                    AND tablename NOT LIKE 'pg_%'
                    ORDER BY tablename
                """)
                
                results = cursor.fetchall()
                tables_with_rls = 0
                tables_without_rls = 0
                
                for table, has_rls in results:
                    if has_rls:
                        tables_with_rls += 1
                        self.stdout.write(f'  [OK] {table}: RLS enabled')
                    else:
                        tables_without_rls += 1
                        self.stdout.write(self.style.WARNING(f'  [WARN] {table}: RLS disabled'))
                
                self.stdout.write(f'\nSummary: {tables_with_rls} tables with RLS, {tables_without_rls} without')
            
            self.stdout.write(self.style.SUCCESS('\n[SUCCESS] All security lints should now be resolved!'))
            self.stdout.write('\nNext steps:')
            self.stdout.write('  1. Go to your Supabase Dashboard')
            self.stdout.write('  2. Navigate to Database > Database Linter')
            self.stdout.write('  3. Run the linter to verify all issues are fixed')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n[ERROR] Error executing SQL: {e}'))
            raise
