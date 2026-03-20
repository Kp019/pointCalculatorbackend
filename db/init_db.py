from db.base import engine, Base
from db.models import User, Game, SavedRule  # Ensure all models are imported

def init_database():
    from db.base import SQLALCHEMY_DATABASE_URL
    print(f"Initializing database with URL: {SQLALCHEMY_DATABASE_URL}")
    print("Initializing database...")
    Base.metadata.create_all(bind=engine)
    print("Database initialization complete.")

if __name__ == "__main__":
    init_database()
