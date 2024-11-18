from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from source_websites.source_website_model import SourceWebsite
from source_websites.scrape_website import scrape_website

def scrape_missing_data():
    # Create database connection
    engine = create_engine(os.environ['DATABASE_URL'])
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Fetch all source websites
        websites = session.query(SourceWebsite).all()

        for website in websites:
            if website.title is None:
                print(f"Scraping website with ID {website.id}")
                scrape_website(website.id)

        print("Finished scraping missing data.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        session.rollback()

    finally:
        session.close()