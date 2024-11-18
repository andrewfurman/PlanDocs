# requirements/requirements_model.py

from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from documents.documents_model import Base

class Requirement(Base):
    __tablename__ = 'requirements'

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_section_id = Column(Integer, ForeignKey('document_sections.id'), nullable=True)
    section_id = Column(Text, nullable=True)
    section_title = Column(Text, nullable=True)
    requirement_description = Column(Text, nullable=True)
    # detailed_business_logic = Column(Text, nullable=True)
    # system_user_story = Column(Text, nullable=True)
    # requirement_source_exact_quote = Column(Text, nullable=True)
    workstream = Column(Text, nullable=True)
    page_number = Column(Integer, nullable=True)
    custom_prompt = Column(Text, nullable=True)
    created_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    updated_date = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationship to DocumentSection
    document_section = relationship("DocumentSection", back_populates="requirements")

    def __repr__(self):
        return f"<Requirement(id={self.id}, section_id='{self.section_id}', section_title='{self.section_title}')>"