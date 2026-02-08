import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from parent directory
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD")

if not SUPABASE_URL or not SUPABASE_DB_PASSWORD:
    print("Error: Missing SUPABASE_URL or SUPABASE_DB_PASSWORD in .env")
    exit(1)

# Extract host from URL
# URL format: https://[project_ref].supabase.co
try:
    project_ref = SUPABASE_URL.split("://")[1].split(".")[0]
except IndexError:
    print(f"Error: Invalid SUPABASE_URL format: {SUPABASE_URL}")
    exit(1)

db_host = f"db.{project_ref}.supabase.co"
db_port = 5432
db_user = "postgres"
db_password = SUPABASE_DB_PASSWORD
db_name = "postgres"

def create_user():
    try:
        print(f"Connecting to database at {db_host}...")
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            dbname=db_name
        )
        conn.autocommit = True
        cur = conn.cursor()

        email = "bypass.user@example.com"
        password = "BypassPassword123!"
        username = "BypassUser"

        # Check if user exists
        cur.execute("SELECT id FROM auth.users WHERE email = %s", (email,))
        existing = cur.fetchone()
        
        if existing:
            print(f"User {email} already exists with ID: {existing[0]}")
            conn.close()
            return

        print("Creating user in auth.users...")
        # Insert user
        sql = """
        INSERT INTO auth.users (
            instance_id,
            id,
            aud,
            role,
            email,
            encrypted_password,
            email_confirmed_at,
            raw_app_meta_data,
            raw_user_meta_data,
            created_at,
            updated_at,
            confirmation_token,
            email_change,
            email_change_token_new,
            recovery_token
        ) VALUES (
            '00000000-0000-0000-0000-000000000000',
            gen_random_uuid(),
            'authenticated',
            'authenticated',
            %s,
            crypt(%s, gen_salt('bf')),
            now(),
            '{"provider": "email", "providers": ["email"]}',
            json_build_object('username', %s),
            now(),
            now(),
            '',
            '',
            '',
            ''
        ) RETURNING id;
        """
        
        cur.execute(sql, (email, password, username))
        user_id = cur.fetchone()[0]
        
        print(f"User created with ID: {user_id}")
        
        # Check if profile was created by trigger
        cur.execute("SELECT * FROM public.users WHERE id = %s", (user_id,))
        profile = cur.fetchone()
        
        if profile:
            print("Profile automatically created in public.users.")
        else:
            print("Profile NOT found in public.users. Creating manually...")
            cur.execute("""
                INSERT INTO public.users (id, email, username, created_at, updated_at)
                VALUES (%s, %s, %s, now(), now())
            """, (user_id, email, username))
            print("Profile created manually.")

        print(f"\nSUCCESS! You can now login with:\nEmail: {email}\nPassword: {password}")
        
        conn.close()

    except Exception as e:
        print(f"Error creating user: {e}")
        # Helpful message for connection errors
        if "could not translate host name" in str(e) or "connection refused" in str(e):
             print("\nNote: Database connection failed. Ensure your IP is allowed in Supabase settings or use the Transaction Pooler (port 6543) if direct connection (5432) is blocked.")

if __name__ == "__main__":
    create_user()
