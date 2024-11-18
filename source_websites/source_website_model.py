from sqlalchemy import Column, Integer, Text, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class SourceWebsite(Base):
    __tablename__ = 'source_websites'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Text, nullable=True)
    url = Column(Text, nullable=True)
    author = Column(Text, nullable=True)
    created_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    updated_date = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    full_text = Column(Text, nullable=True)
    found_urls = Column(Text, nullable=True)

    def __repr__(self):
        return f"<SourceWebsite(id={self.id}, title='{self.title}', url='{self.url}')>"

class ScrapingCriteria(Base):
    __tablename__ = 'scraping_criteria'
    id = Column(Integer, primary_key=True, autoincrement=True)
    text_contains = Column(Text, nullable=False)
    include_exclude = Column(Enum('include', 'exclude', name='include_exclude_enum'), nullable=False)
    def __repr__(self):
        return f"<ScrapingCriteria(id={self.id}, text_contains='{self.text_contains}', include_exclude='{self.include_exclude}')>"