import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from source_websites.source_website_model import Base, SourceWebsite
from documents.documents_model import Document


# Use the DATABASE_URL from environment variables
DATABASE_URL = os.environ['DATABASE_URL']

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")