
# add_ducments_from_source.py

# This python function will loop through all of the Source Websites and add each URL that has been found to the documents database table. It will only populate the URL column of that table, and will not add the URL if the URL has already been added to the documents table.

# Here is a sample of how the URLs in the found_urls column will look:  "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/clm104c22pdf.pdf, https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/clm104c28.pdf, https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/clm104c14.pdf, https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/clm104c15.pdf, https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/clm104c38.pdf, https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/clm104c01.pdf, https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/clm104c18pdf.pdf, https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/clm104c05.pdf, https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/clm104c33.pdf, https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/clm104c27.pdf, https://www.cms.gov/files/document/medqtrlycompnlarchive072019003pdf, https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/clm104c09.pdf, https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/clm104c11.pdf, https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/clm104c34.pdf, https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/clm104c29pdf.pdf, https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/clm104c35.pdf,"

# This function will not have any parameters.

# This function will return a success message with the number of documents added to the database.

# add_documents_from_source.py

import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from source_websites.source_website_model import SourceWebsite
from documents.documents_model import Document

def add_documents_from_source_websites():
    # Set up database connection
    engine = create_engine(os.environ['DATABASE_URL'])
    Session = sessionmaker(bind=engine)
    session = Session()

    documents_added = 0

    try:
        # Query all SourceWebsite entries
        source_websites = session.query(SourceWebsite).all()

        for website in source_websites:
            if website.found_urls:
                # Split the found_urls string into a list of URLs
                urls = [url.strip() for url in website.found_urls.split(',')]

                for url in urls:
                    # Check if the URL already exists in the documents table
                    existing_document = session.query(Document).filter_by(url=url).first()

                    if not existing_document:
                        # Add a new Document entry with the URL
                        new_document = Document(url=url, source_website_id=website.id)
                        session.add(new_document)
                        documents_added += 1

        # Commit changes
        session.commit()
        return f"Success: {documents_added} documents added to the database."

    except Exception as e:
        session.rollback()
        return f"Error: {str(e)}"

    finally:
        session.close()

# You can call the function like this if you want to run it directly:
if __name__ == "__main__":
    result = add_documents_from_source_websites()
    print(result)