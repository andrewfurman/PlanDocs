# create_sections_using_flags.py

#The create_sections_using_flags(document id) function will read in the conmpressed_document field for the document ID given and then create an array of sections with section_start_page_number, section_end_page_number.

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
import os
from documents.documents_model import Document, DocumentSection

def identify_initial_sections(summaries):
    """Group pages into initial sections based on flags."""
    sections = []
    current_section = []
    
    for page in summaries:
        if page['start_of_new_section']:
            if page['content_continued_from_previous_page'] and current_section:
                current_section.append(page)
            else:
                if current_section:
                    sections.append(current_section)
                current_section = [page]
        else:
            current_section.append(page)
    
    if current_section:
        sections.append(current_section)
    
    return sections

def merge_with_adjacent_sections(adjusted_sections, section):
    """Merge small sections with adjacent ones if possible."""
    if adjusted_sections:
        if len(adjusted_sections[-1]) + len(section) <= 15:
            adjusted_sections[-1].extend(section)
        else:
            adjusted_sections.append(section)
    else:
        adjusted_sections.append(section)
    return adjusted_sections

def split_section_with_continuity(section, min_pages, max_pages):
    """Split large sections while maintaining content continuity."""
    split_sections = []
    current_split = []
    
    for idx, page in enumerate(section):
        current_split.append(page)
        if len(current_split) >= max_pages:
            if idx + 1 < len(section) and section[idx + 1]['content_continued_from_previous_page']:
                continue
            else:
                split_sections.append(current_split)
                current_split = []
    
    if current_split:
        split_sections.append(current_split)
    
    return split_sections

def adjust_sections(sections, min_pages=2, max_pages=15):
    """Adjust sections to meet size requirements."""
    adjusted_sections = []
    
    for section in sections:
        section_length = len(section)
        if section_length < min_pages:
            adjusted_sections = merge_with_adjacent_sections(adjusted_sections, section)
        elif section_length > max_pages:
            split_sections = split_section_with_continuity(section, min_pages, max_pages)
            adjusted_sections.extend(split_sections)
        else:
            adjusted_sections.append(section)
    
    return adjusted_sections

def create_sections_using_flags(document_id: int):
    """Create document sections based on page flags from compressed document."""
    engine = create_engine(os.environ['DATABASE_URL'])
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        document = session.query(Document).get(document_id)
        if not document:
            raise ValueError(f"No document found with id {document_id}")
        
        doc_data = json.loads(document.compressed_document)
        summaries = doc_data['summaries']
        
        initial_sections = identify_initial_sections(summaries)
        adjusted_sections = adjust_sections(initial_sections)

        # First delete requirements linked to existing sections
        existing_sections = session.query(DocumentSection).filter_by(document_id=document_id).all()
        for section in existing_sections:
            # Delete requirements for this section
            session.query(Requirement).filter_by(document_section_id=section.id).delete()
        
        # Delete existing sections for the document
        session.query(DocumentSection).filter_by(document_id=document_id).delete()
        
        for section in adjusted_sections:
            start_page = min(page['page_number'] for page in section)
            end_page = max(page['page_number'] for page in section)
            
            # Use the first non-TOC page's summary as the section title
            title_page = next((page for page in section if not page['table_of_contents']), section[0])
            
            # Create summary from all page summaries in the section
            section_summary = "\n".join(f"Page {page['page_number']}: {page['page_summary']}" 
                                      for page in section)
            
            new_section = DocumentSection(
                document_id=document_id,
                # title=title_page['page_summary'][:255],
                # summary=section_summary,
                start_page=start_page,
                end_page=end_page,
                # document_text="\n".join(page['page_summary'] for page in section),
                # custom_prompt, created_date, and updated_date will be handled automatically
            )
            session.add(new_section)
        
        session.commit()
        return f"Created {len(adjusted_sections)} sections for document {document_id}"
    
    except Exception as e:
        session.rollback()
        raise e
    
    finally:
        session.close()