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
    text = Column(String, nullable=False)
    new = Column(Boolean, default=True)
    source_url = Column(String, nullable=False)
    image_urls = Column(String, nullable=False)

    def __repr__(self):
        return self.header
