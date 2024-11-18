# add_section_document_text.py

# The add_section_document_text(int document_id) function will loop through the existing document_sections related to a document and add the document_text to each section.  Each section full text is a subset of the document full_contents. This function should parse the document full_contents and extract the text for each section using the page delimiters "🅿️ Start Page 1" "🅿️ Start Page 2" and so on. Each of those delimiters "🅿️ Start Page 1" "🅿️ Start Page 2" should also appear in the Document Text field of the document_section.

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import re
from documents.documents_model import Document, DocumentSection

def add_section_document_text(document_id):
    # Set up database connection
    engine = create_engine(os.environ['DATABASE_URL'])
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Get document and its sections
        document = session.query(Document).get(document_id)
        if not document:
            return f"Error: Document with ID {document_id} not found."

        # Split full contents into pages
        parts = re.split(r'(🅿️ Start Page \d+)', document.full_contents)
        pages = []
        for i in range(1, len(parts), 2):
            pages.append(f"{parts[i]}\n{parts[i+1].strip()}")

        # Get all sections for this document
        sections = session.query(DocumentSection)\
            .filter(DocumentSection.document_id == document_id)\
            .order_by(DocumentSection.start_page)\
            .all()

        # Update each section's document_text
        for section in sections:
            start_idx = section.start_page - 1  # Convert to 0-based index
            end_idx = section.end_page
            section_pages = pages[start_idx:end_idx]
            section.document_text = "\n".join(section_pages)

        session.commit()
        return f"Successfully updated {len(sections)} sections"

    except Exception as e:
        session.rollback()
        return f"Error: {str(e)}"
    
    finally:
        session.close()