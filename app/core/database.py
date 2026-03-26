import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import POSTGRES_URL

engine = create_engine(POSTGRES_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Main entry point for all database schema initializations"""
    # 1. Create tables defined in SQLAlchemy Models
    Base.metadata.create_all(bind=engine)
    
    # 2. Run the custom SQL script for constraints (Guest access, etc.)
    script_path = os.path.join(os.getcwd(), "init_db.sql")
    if os.path.exists(script_path):
        with SessionLocal() as db:
            try:
                with open(script_path, "r") as f:
                    sql = f.read()
                db.execute(text(sql))
                db.commit()
            except Exception as e:
                db.rollback()
                print(f"❌ Custom SQL Init Failed: {e}")