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


    
def add_article(header, summary, text, source_url, image_urls):
    session = Session()
    article = session.query(Article).filter_by(header=header).first()
    if article is None:
        new_article = Article(
            header=header,
            summary=summary,
            text=text,
            source_url=source_url,
            image_urls=image_urls,
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


def get_images_from_article(id):
    session = Session()
    article = session.query(Article).filter(Article.id == id).first()
    image_urls = article.image_urls
    return image_urls


def get_text_from_article(id):
    session = Session()
    article = session.query(Article).filter(Article.id == id).first()
    image_urls = article.text
    return image_urls


def get_source_url_from_article(id):
    session = Session()
    article = session.query(Article).filter(Article.id == id).first()
    source_url = article.source_url
    return source_url


def get_article_by_header(header):
    session = Session()
    article = session.query(Article).filter(Article.header == header).first()
    if article:
        article_id = article.id
        return article_id
    else:
        return None


def set_article_readed(id):
    session = Session()
    article = session.get(Article, id)
    article.new = False
    session.add(article)
    session.commit()


def get_new_articles():
    session = Session()
    new_articles = session.query(Article).filter(Article.new == True).all()
    return new_articles


def get_article_by_id(id):
    session = Session()
    article = session.get(Article, id)
    return article