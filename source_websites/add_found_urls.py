from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from source_websites.source_website_model import SourceWebsite
from urllib.parse import urlparse

def add_found_html_urls():
    # Create database connection
    engine = create_engine(os.environ['DATABASE_URL'])
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Fetch all source websites
        websites = session.query(SourceWebsite).all()

        for website in websites:
            if website.found_urls:
                # Split the found_urls string into a list
                urls = website.found_urls.split(', ')
                
                for url in urls:
                    # Check if the URL ends with .html or has no file extension (assuming it's an HTML page)
                    parsed_url = urlparse(url)
                    path = parsed_url.path
                    if path.endswith('.html') or '.' not in path.split('/')[-1]:
                        # Check if this URL already exists in the database
                        existing_url = session.query(SourceWebsite).filter_by(url=url).first()
                        
                        if not existing_url:
                            # Create a new SourceWebsite entry
                            new_website = SourceWebsite(url=url)
                            session.add(new_website)
                            print(f"Added new URL: {url}")

        # Commit the changes
        session.commit()
        print("Finished adding found HTML URLs to the database.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        session.rollback()

    finally:
        session.close()