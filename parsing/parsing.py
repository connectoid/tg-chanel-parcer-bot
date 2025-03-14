import requests
from bs4 import BeautifulSoup

from settings.settings import (slashdotcom_url, gamespot_url, gamespot_base_url, eurogamer_url, 
                               pcgamer_url, gamesradar_url)
from database.orm import get_article_by_header


article_structure = {
    'header': '',
    'text': '',
    'text_short': '',
    'tags': '',
    'source_url': '',
}


def get_articles(site):
    match site:
        case 'slashdotcom':
            articles = slashdotcom_parcer()
        case 'gamespot':
            articles = gamespot_parcer()
        case 'eurogamer':
            articles = eurogamer_parser()
        case 'pcgamer':
            articles = pcgamer_parser()
        case 'gamesradar':
            articles = gamesradar_parser()
    return articles


def slashdotcom_parcer():
    response = requests.get(slashdotcom_url)
    if response.status_code == 200:
        articles_list = []
        soup = BeautifulSoup(response.text, 'lxml')
        articles = soup.find_all('article', class_='fhitem')
        for article in articles:
            article_dict = {}
            article_dict['header'] = article.find('span', class_='story-title').text.strip()
            article_dict['text'] = article.find('div', class_='p').text.strip()
            article_dict['source_url'] = 'https:' + article.find('span', class_='story-title').find('a')['href']
            articles_list.append(article_dict)
        return articles_list
    else:
        print(f'Request error (slashdotcom_parcer): {response.status_code}')
        return None


def pcgamer_parser():
    print('Start PCGAMER parsing')

    def get_text(url):
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            text = soup.find('div', {"id": "article-body"}).text.strip()
            return text
        else:
            print(f'Request error: {response.status_code}')
            return None
    response = requests.get(pcgamer_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        articles_list = []
        article_links = soup.find_all('a', class_='article-link')
        article_links = article_links[3:]
        for article in article_links:
            article_dict = {}
            header = article.find('h3', class_='article-name').text.strip()
            source_url = article['href']
            text = get_text(source_url)
            image_url_set = article.find('div', class_='image').find('img')['srcset']
            image_url = image_url_set.split(', ')[-1].split(' ')[0]
            image_urls = []
            image_urls.append(image_url)
            article_dict['header'] = header
            article_dict['text'] = text
            article_dict['image_urls'] = image_urls
            article_dict['source_url'] = source_url
            articles_list.append(article_dict)
        return articles_list
    else:
        print(f'Request error: {response.status_code}')
        return None



def gamesradar_parser():
    print('Start GAMESRADAR parsing')

    def get_text(url):
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            text = soup.find('div', {"id": "article-body"}).text.strip()
            return text
        else:
            print(f'Request error: {response.status_code}')
            return None
        
    response = requests.get(gamesradar_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        articles_div = soup.find('div', {"data-analytics-id": "featured-article"})
        articles_divs = articles_div.find_all('div', class_='listingResult')
        articles_divs = [article_div for article_div in articles_divs if not article_div.find('div', class_='sponsored-post')]
        articles_list = []
        for article in articles_divs:
            article_dict = {}
            header = article.find('h3', class_='article-name').text
            source_url = article.find_all('a')[0]['href']
            text = get_text(source_url)
            image_url = article.find('picture').find('img')['src']
            image_urls = []
            image_urls.append(image_url)
            article_dict['header'] = header
            article_dict['text'] = text
            article_dict['image_urls'] = image_urls
            article_dict['source_url'] = source_url
            articles_list.append(article_dict)
        return articles_list
    else:
        print(f'Request error: {response.status_code}')
        return None



def eurogamer_parser():

    def get_text(url):
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            text = soup.find('div', class_='article_body_content').text.strip()
            return text
        else:
            print(f'Request error: {response.status_code}')
            return None
        
    print('Start EUROGAMER parsing')
    response = requests.get(eurogamer_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        articles_list = []
        article_divs = soup.find_all('div', class_='summary')
        for article in article_divs:
            article_dict = {}
            header = article.find('p', class_='title').find('a').text.strip()
            summary = article.find('div', class_='excerpt').find('p').text.strip()
            image_urls = []
            thumbnail = article.find('div', class_='thumbnail').find('img')['src'].split('?widt')[0]
            image_urls.append(thumbnail)
            source_url = article.find('p', class_='title').find('a')['href']
            text = get_text(source_url)
            article_dict['header'] = header
            article_dict['summary'] = summary
            article_dict['text'] = text
            article_dict['image_urls'] = image_urls
            article_dict['source_url'] = source_url
            articles_list.append(article_dict)
        return articles_list
    else:
        print(f'Request error: {response.status_code}')
        return None

def gamespot_parcer():
    print('Start GAMESPOT parsing')

    def get_text(url):
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            text_section = soup.find('section', class_='article-body')
            paragraphs = text_section.find_all('p', {"dir": "ltr"})
            if not paragraphs:
                print('Аттрибута dir нет, берем все теги <p>')
                paragraphs = text_section.find_all('p')
            paragraphs = [p.text for p in paragraphs]
            article_text = ' '.join(paragraphs)
            image_urls = []
            try:
                image_url = text_section.find('figure')['data-img-src']
                image_url_list = image_url.split(',')
                image_urls = image_urls + image_url_list
            except Exception as e:
                print(f'Exception in get_text(url: {e}')
                image_urls = []
            return article_text, image_urls
        else:
            print(f'Request error: {response.status_code}')
            return None

    response = requests.get(gamespot_url)
    if response.status_code == 200:
        count = 0
        articles_list = []
        soup = BeautifulSoup(response.text, 'lxml')
        articles = soup.find_all('div', class_='card-item')
        # articles = soup.find_all('a', class_='card-item__link')
        for article in articles:
            # image_urls = []
            article_dict = {}
            artilce_content = article.find('a', class_='card-item__link')
            header = artilce_content.text.strip()
            article_dict['header'] = header
            article_id = get_article_by_header(header)
            if article_id:
                print(f'Статья с заголовком {header} с id {article_id} уже есть в базе. Пропускаем')
                continue
            article_dict['source_url'] = gamespot_base_url + artilce_content['href']
            text, image_urls = get_text(article_dict['source_url'])
            thumb_image_url = article.find('div', class_='card-item__img').find('img')['src']
            thumb_image_url = thumb_image_url.replace('screen_petite', 'screen_kubrick')
            image_urls.append(thumb_image_url)
            article_dict['text'] = text
            article_dict['image_urls'] = image_urls
            articles_list.append(article_dict)
            count += 1
            # if count >= 3:
            #     break
        print(f'{count} статей добавлено')
        return articles_list
    else:
        print(f'Request error (gamespot_parcer): {response.status_code}')
        return None