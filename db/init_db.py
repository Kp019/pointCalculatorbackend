"""Database initialization using direct PostgreSQL connection."""
import logging
from pathlib import Path
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)


def get_migration_sql() -> str:
    """Read all migration SQL files in order."""
    migrations_dir = Path(__file__).parent / "migrations"
    if not migrations_dir.exists():
        return ""
    
    # Get all .sql files and sort them
    migration_files = sorted(migrations_dir.glob("*.sql"))
    
    # Combine all migrations
    all_migrations = []
    for migration_file in migration_files:
        logger.info(f"Loading migration: {migration_file.name}")
        all_migrations.append(migration_file.read_text())
    
    return "\n\n".join(all_migrations)


def init_database_with_psycopg() -> None:
    """Initialize database tables using direct PostgreSQL connection."""
    try:
        import psycopg2
        from core.config import settings
        
        # Extract database connection details from Supabase URL
        # Supabase URL format: https://PROJECT_REF.supabase.co
        # Database URL format: postgresql://postgres:[PASSWORD]@db.PROJECT_REF.supabase.co:5432/postgres
        
        project_ref = settings.SUPABASE_URL.replace("https://", "").replace(".supabase.co", "")
        db_password = settings.SUPABASE_DB_PASSWORD
        
        if not db_password:
            logger.warning("SUPABASE_DB_PASSWORD not set. Cannot auto-create tables.")
            logger.warning("Please set SUPABASE_DB_PASSWORD in your .env file or run migrations manually.")
            return
        
        # URL-encode the password to handle special characters like @, #, etc.
        encoded_password = quote_plus(db_password)
        db_url = f"postgresql://postgres:{encoded_password}@db.{project_ref}.supabase.co:5432/postgres"
        
        logger.info("Connecting to PostgreSQL database...")
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Read and execute migration SQL
        migration_sql = get_migration_sql()
        if migration_sql:
            logger.info("Executing database migrations...")
            cursor.execute(migration_sql)
            logger.info("✓ Database tables created successfully")
        
        cursor.close()
        conn.close()
        
    except ImportError:
        logger.warning("psycopg2 not installed. Cannot auto-create tables.")
        logger.warning("Install with: uv add psycopg2-binary")
    except Exception as e:
        logger.warning(f"Could not auto-initialize database: {e}")
        logger.warning("Please run the SQL migrations manually in Supabase SQL Editor")


def init_database() -> None:
    """Initialize database - try psycopg2 method first."""
    from db.supabase import supabase
    from postgrest.exceptions import APIError
    
    # Check if all required tables exist
    tables_to_check = ["games", "rules", "users"]
    missing_tables = []
    
    try:
        for table_name in tables_to_check:
            try:
                supabase.table(table_name).select("id").limit(1).execute()
            except APIError as e:
                # APIError means we connected but got an error (e.g. table missing)
                if "PGRST205" in str(e) or "Could not find the table" in str(e):
                    missing_tables.append(table_name)
                else:
                    raise
    except Exception as e:
        # Catch network errors (ConnectError, etc.) and other unexpected issues
        logger.warning(f"Could not connect to Supabase to check tables: {e}")
        logger.warning("Skipping table creation. Application will start, but database features may fail.")
        return
    
    if not missing_tables:
        # Check if avatar_color column exists in users table
        try:
            supabase.table("users").select("avatar_color").limit(1).execute()
            logger.info("✓ All database tables and columns already exist")
            return
        except APIError as e:
            if "column" in str(e).lower() and "avatar_color" in str(e).lower():
                logger.info("Missing column 'avatar_color'. Attempting to update schema...")
            else:
                # Some other API error, log it and proceed
                logger.warning(f"Error checking for avatar_color column: {e}")
                return
    
    if missing_tables:
        logger.info(f"Missing tables: {', '.join(missing_tables)}. Attempting to create...")
    
    init_database_with_psycopg()
