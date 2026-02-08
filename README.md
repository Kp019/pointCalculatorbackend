# Point Calculator Backend

FastAPI backend for the Point Calculator application with Supabase integration.

## Setup

### 1. Prerequisites

- Python 3.10+
- uv (Python package manager)
- Supabase account

### 2. Environment Variables

Copy `.env.example` to `.env` and fill in your Supabase credentials:

```bash
cp .env.example .env
```

### 2. Environment Variables

Copy `.env.example` to `.env` and fill in your Supabase credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_DB_PASSWORD=your_database_password  # For auto table creation
```

**Get your database password:**

1. Go to Supabase Dashboard → Settings → Database
2. Find "Connection String" section
3. Copy the password from the URI connection string

### 3. Install Dependencies

```bash
uv sync
```

### 4. Run the Server

```bash
uv run uvicorn main:app --reload --port=9000
```

**The backend will automatically create database tables on first startup!**

Alternatively, you can manually run the SQL migration (see below).
Run the SQL migration in your Supabase SQL Editor:

1. Go to your Supabase project dashboard
2. Navigate to SQL Editor
3. Copy and paste the contents of `db/migrations/001_create_games_table.sql`
4. Run the query

### 4. Install Dependencies

```bash
uv sync
```

### 5. Run the Server

```bash
uv run uvicorn main:app --reload --port=9000
```

The API will be available at `http://localhost:9000`

## API Documentation

Once running, visit:

- Swagger UI: `http://localhost:9000/docs`
- ReDoc: `http://localhost:9000/redoc`

## Project Structure

```
.
├── api/
│   └── endpoints/      # API route handlers
├── core/               # Core configuration
├── db/                 # Database connection and migrations
├── schemas/            # Pydantic models
└── main.py            # Application entry point
```
