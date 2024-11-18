# extract_missing_full_text.py

# This file should have one function called extract missing full text from documents. This function should have no parameters.

# the function should loop through all of the documents in the document database table and if the full_contents column is empty, it should pass the url to that document to the get_url_text function and save the string returned to the full_contents column for that document.

# extract_missing_full_text.py

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from documents.documents_model import Document
from documents.getPDFurl import get_url_text

def extract_missing_full_text():
    # Set up database connection
    engine = create_engine(os.environ['DATABASE_URL'])
    Session = sessionmaker(bind=engine)
    session = Session()

    documents_updated = 0

    try:
        # Query documents with empty full_contents
        documents = session.query(Document).filter(Document.full_contents == None).all()

        for document in documents:
            if document.url:
                # Get text content from URL
                text_content = get_url_text(document.url)
                
                # Update document's full_contents
                document.full_contents = text_content
                
                # Commit changes for this document immediately
                try:
                    session.commit()
                    documents_updated += 1
                    print(f"Updated document ID {document.id}")
                except Exception as e:
                    session.rollback()
                    print(f"Error updating document ID {document.id}: {str(e)}")

        return f"Success: Full text extracted for {documents_updated} documents."

    except Exception as e:
        return f"Error: {str(e)}"

    finally:
        session.close()

# You can call the function like this if you want to run it directly:
if __name__ == "__main__":
    result = extract_missing_full_text()
    print(result)