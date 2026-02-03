"""
Add PostgreSQL trigram extension and indexes for fuzzy search.
This enables typo-tolerant search while maintaining speed.
Only runs on PostgreSQL - skips other databases like SQLite.
"""
from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


def create_trigram_indexes(apps, schema_editor):
    """Create trigram indexes only on PostgreSQL."""
    if schema_editor.connection.vendor != 'postgresql':
        return  # Skip on SQLite, MySQL, etc.
    
    # Create GIN indexes for trigram search
    schema_editor.execute(
        "CREATE INDEX IF NOT EXISTS work_title_trgm_idx "
        "ON works USING gin(title gin_trgm_ops);"
    )
    schema_editor.execute(
        "CREATE INDEX IF NOT EXISTS work_title_norm_trgm_idx "
        "ON works USING gin(title_normalized gin_trgm_ops);"
    )
    schema_editor.execute(
        "CREATE INDEX IF NOT EXISTS composer_fullname_trgm_idx "
        "ON composers USING gin(full_name gin_trgm_ops);"
    )
    schema_editor.execute(
        "CREATE INDEX IF NOT EXISTS composer_lastname_trgm_idx "
        "ON composers USING gin(last_name gin_trgm_ops);"
    )


def drop_trigram_indexes(apps, schema_editor):
    """Drop trigram indexes only on PostgreSQL."""
    if schema_editor.connection.vendor != 'postgresql':
        return
    
    schema_editor.execute("DROP INDEX IF EXISTS work_title_trgm_idx;")
    schema_editor.execute("DROP INDEX IF EXISTS work_title_norm_trgm_idx;")
    schema_editor.execute("DROP INDEX IF EXISTS composer_fullname_trgm_idx;")
    schema_editor.execute("DROP INDEX IF EXISTS composer_lastname_trgm_idx;")


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0003_work_sheerpluck_url_alter_work_imslp_url_and_more'),
    ]

    # Run outside transaction to avoid issues with table creation
    atomic = False

    operations = [
        # Enable the pg_trgm extension (PostgreSQL only - automatically skipped on others)
        TrigramExtension(),
        
        # Add trigram indexes using RunPython to check database vendor
        migrations.RunPython(
            create_trigram_indexes,
            reverse_code=drop_trigram_indexes
        ),
    ]
