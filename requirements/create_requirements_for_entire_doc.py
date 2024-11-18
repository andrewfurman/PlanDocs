# create_requirements_for_entire_doc

# this function will call the create_requirements(document section ID) function for all sections related to a document

# requirements/create_requirements_for_entire_doc.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from documents.documents_model import Document, DocumentSection
from requirements.create_requirements import create_requirements

def create_requirements_for_entire_doc(document_id: int):
    # Set up database connection
    engine = create_engine(os.environ['DATABASE_URL'])
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Retrieve the document
        document = session.query(Document).get(document_id)
        if not document:
            raise ValueError(f"No document found with id {document_id}")

        # Get all document sections for the given document
        document_sections = session.query(DocumentSection).filter_by(document_id=document_id).all()

        # Initialize counters
        total_sections = len(document_sections)
        processed_sections = 0
        successful_sections = 0

        # Process each section
        for section in document_sections:
            try:
                result = create_requirements(section.id)
                print(f"Processed section {section.id}: {result}")
                successful_sections += 1
            except Exception as e:
                print(f"Error processing section {section.id}: {str(e)}")
            finally:
                processed_sections += 1

        return f"Processed {processed_sections}/{total_sections} sections, {successful_sections} successful"

    except Exception as e:
        return f"Error: {str(e)}"

    finally:
        session.close()