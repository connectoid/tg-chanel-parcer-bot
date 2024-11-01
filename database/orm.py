import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from .models import Base, Article

load_dotenv()
DATABASE = os.getenv('DATABASE')
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

database_url = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DATABASE}'


engine = create_engine(database_url, echo=False, pool_size=20, max_overflow=0)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


    
def add_article(header, header_original, text, text_short, tags, source_url, image_url, image_thumb_url):
    session = Session()
    article = session.query(Article).filter_by(header_original=header_original).first()
    if article is None:
        new_article = Article(
            header=header,
            header_original=header_original,
            text=text,
            text_short=text_short,
            tags=tags,
            source_url=source_url,
            image_url=image_url,
            image_thumb_url=image_thumb_url,
        )
        session.add(new_article)
        session.commit()
        print(f'Статья {header} добавлена')
        return True
    else:
        print(f'Статья {header} уже есть в Базе данных, пропускаем')
        return False


def delete_article(id):
    session = Session()
    article = session.get(Article, id)
    session.delete(article)
    session.commit()


def get_article_by_id(id):
    session = Session()
    ticket = session.get(Article, id)
    return ticket


def get_new_articles():
    session = Session()
    new_articles = session.query(Article).filter(Article.new == True).all()
    return new_articles
