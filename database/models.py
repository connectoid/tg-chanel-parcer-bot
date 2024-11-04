from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()

class Article(Base):
    __tablename__ = 'articles'
    id = Column(Integer, primary_key=True)
    parsing_date = Column(DateTime, default=datetime.now, nullable=False)
    header = Column(String, nullable=False)
    header_original = Column(String, nullable=False)
    text = Column(String, nullable=False)
    text_short = Column(String, nullable=False)
    tags = Column(String, nullable=True)
    is_favorite = Column(Boolean, default=False)
    new = Column(Boolean, default=True)
    source_url = Column(String, nullable=False)
    image_urls = Column(String, nullable=False)
    total_tokens = Column(Integer, nullable=True)

    def __repr__(self):
        return self.header
