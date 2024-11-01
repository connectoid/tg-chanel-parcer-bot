import requests
from bs4 import BeautifulSoup

from settings.settings import slashdotcom_url, gamespot_url, gamespot_base_url

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


def gamespot_parcer():

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
            try:
                image_url = text_section.find('figure')['data-img-src']
            except Exception as e:
                image_url = ''
            return article_text, image_url
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
            count += 1
            article_dict = {}
            artilce_content = article.find('a', class_='card-item__link')
            article_dict['header'] = artilce_content.text.strip()
            article_dict['source_url'] = gamespot_base_url + artilce_content['href']
            text, image_url = get_text(article_dict['source_url'])
            thumb_image_url = article.find('div', class_='card-item__img').find('img')['src']
            thumb_image_url = thumb_image_url.replace('screen_petite', 'original')
            article_dict['text'] = text
            article_dict['image_url'] = image_url
            article_dict['image_thumb_url'] = thumb_image_url
            articles_list.append(article_dict)
            if count >= 5:
                break
        return articles_list
    else:
        print(f'Request error (gamespot_parcer): {response.status_code}')
        return None