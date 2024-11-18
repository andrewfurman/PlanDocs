# documents/documents_model.py

from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import sys, os


# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from source_websites.source_website_model import Base
from requirements.requirements_model import Requirement

class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_website_id = Column(Integer, ForeignKey('source_websites.id'), nullable=True)
    title = Column(Text, nullable=True)
    author = Column(Text, nullable=True)
    full_contents = Column(Text, nullable=True)
    compressed_document = Column(Text, nullable=True)
    url = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    table_of_contents = Column(Text, nullable=True)
    extended_summary = Column(Text, nullable=True)
    word_count = Column(Integer, nullable=True)
    page_count = Column(Integer, nullable=True)
    chapter = Column(Text, nullable=True)
    created_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_date = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Add relationship to DocumentSection
    sections = relationship("DocumentSection", back_populates="document")

    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}', url='{self.url}')>"

class DocumentSection(Base):
    __tablename__ = 'document_sections'

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False)
    title = Column(Text, nullable=True)  # New optional title field
    summary = Column(Text, nullable=True)  # New optional summary field
    start_page = Column(Integer, nullable=False)
    end_page = Column(Integer, nullable=False)
    document_text = Column(Text, nullable=True)
    custom_prompt = Column(Text, nullable=True)
    created_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_date = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Add relationship to Document
    document = relationship("Document", back_populates="sections")

    # Add relationship to Requirement
    requirements = relationship("Requirement", back_populates="document_section")

    def __repr__(self):
        return f"<DocumentSection(id={self.id}, document_id={self.document_id}, start_page={self.start_page}, end_page={self.end_page})>"