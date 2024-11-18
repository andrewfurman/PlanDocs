# this function to create document sections takes the full content from the document, and then creates sections that contain subsets of the document.

# the function takes the following parameters: Document ID.

# the function returns a list of sections created.

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import re
from documents.documents_model import Document, DocumentSection

def create_document_sections(document_id):
    # Set up database connection
    engine = create_engine(os.environ['DATABASE_URL'])
    Session = sessionmaker(bind=engine)
    session = Session()

    created_sections = []

    try:
        # Retrieve the document
        document = session.query(Document).get(document_id)
        if not document:
            return f"Error: Document with ID {document_id} not found."

        # Delete existing requirements and document sections
        try:
            # First, delete requirements associated with the document sections
            session.query(Requirement).filter(
                Requirement.document_section_id.in_(
                    session.query(DocumentSection.id).filter(DocumentSection.document_id == document_id)
                )
            ).delete(synchronize_session=False)
            # Then, delete existing document sections
            session.query(DocumentSection).filter(DocumentSection.document_id == document_id).delete()

            session.commit()
        except Exception as e:
            session.rollback()
            return f"Error deleting existing requirements and sections: {str(e)}"

        # Split the full_contents into pages, separating markers and content
        parts = re.split(r'(🅿️ Start Page \d+)', document.full_contents)
        pages = []
        for i in range(1, len(parts), 2):
            # Add a new line after the page marker
            pages.append(f"{parts[i]}\n{parts[i+1].strip()}")
      
        # Group pages into sections of 20
        sections = [pages[i:i+20] for i in range(0, len(pages), 20)]

        for i, section_pages in enumerate(sections):
            start_page = i * 20 + 1
            end_page = start_page + len(section_pages) - 1

            # Join the pages for this section
            section_text = "\n".join(section_pages)

            # Create a new DocumentSection
            new_section = DocumentSection(
                document_id=document_id,
                start_page=start_page,
                end_page=end_page,
                document_text=section_text
            )

            session.add(new_section)
            created_sections.append(new_section)

        # Commit changes
        session.commit()
        return created_sections

    except Exception as e:
        session.rollback()
        return f"Error: {str(e)}"

    finally:
        session.close()