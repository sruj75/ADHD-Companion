from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import Base
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL - supports both SQLite (development) and PostgreSQL (production)
DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    "sqlite:///./adhd_companion.db"
)

# For SQLite, we need to enable foreign key constraints
connect_args = {}
if "sqlite" in DATABASE_URL:
    connect_args = {"check_same_thread": False}

# Create the database engine
# echo=True prints SQL statements (helpful for learning and debugging)
engine = create_engine(
    DATABASE_URL, 
    echo=True,  # Set to False in production
    connect_args=connect_args
)

# Create a session factory
# Sessions are how we interact with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """
    Creates all database tables based on our models.
    This should be called when the app starts up for the first time.
    """
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

def get_db():
    """
    Dependency function that provides database sessions to our API endpoints.
    FastAPI will automatically handle opening and closing the database connection.
    
    This is a generator function that yields a database session,
    ensures it gets closed after use, even if an error occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def reset_database():
    """
    Drops all tables and recreates them. 
    USE WITH CAUTION - this will delete all data!
    Only use during development.
    """
    print("⚠️  RESETTING DATABASE - ALL DATA WILL BE LOST!")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database reset complete!")

# Test database connection
def test_connection():
    """
    Tests if we can connect to the database.
    """
    try:
        db = SessionLocal()
        # Use SQLAlchemy's text() function for raw SQL
        db.execute(text("SELECT 1"))
        db.close()
        print("✅ Database connection successful!")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False 