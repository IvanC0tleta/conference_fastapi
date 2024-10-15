from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

postgres_username = os.getenv("POSTGRES_DB_USER")
postgres_password = os.getenv("POSTGRES_DB_PASSWORD")
postgres_host = os.getenv("POSTGRES_DB_HOST")
postgres_port = os.getenv("POSTGRES_DB_PORT")
postgres_database = os.getenv("POSTGRES_DB_NAME")
SQLALCHEMY_DATABASE_URL = \
    f"postgresql://{postgres_username}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_database}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
