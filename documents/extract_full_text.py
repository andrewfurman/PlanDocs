# extract_full_text.py

# The extract_full_text(int document_id) function extracts the full text of a document from the source website.  This function will delete the existing content of the full_content for the document and then call the get_url_text(url) function to extract the full text from the source website for this document.  This document will return an error saying "this document does not have a URL" if the url column for this document id is null.

# extract_full_text.py

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from documents.documents_model import Document
from documents.getPDFurl import get_url_text

def extract_full_text(document_id):
    # Set up database connection
    engine = create_engine(os.environ['DATABASE_URL'])
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Query the document from the database
        document = session.query(Document).filter(Document.id == document_id).first()

        if not document:
            return f"Error: Document with ID {document_id} not found."

        if not document.url:
            return "Error: This document does not have a URL."

        # Delete existing content
        document.full_contents = None

        # Extract new content
        text_content = get_url_text(document.url)

        # Update document's full_contents
        document.full_contents = text_content

        # Commit changes
        session.commit()

        return f"Success: Full text extracted for document ID {document_id}."

    except Exception as e:
        session.rollback()
        return f"Error: {str(e)}"

    finally:
        session.close()

# You can call the function like this if you want to run it directly:
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_full_text.py <document_id>")
    else:
        document_id = int(sys.argv[1])
        result = extract_full_text(document_id)
        print(result)