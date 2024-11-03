import requests
import os
import json
import urllib3
import uuid

from dotenv import load_dotenv

urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

AUTH_KEY = os.getenv('AUTH_KEY')
RqUID = '6f0b1291-c7f3-43c6-bb2e-9f3efb2dc98e'
MIN_SHORT_VERSION_LENGTH = 60 # words
MAX_SHORT_VERSION_LENGTH = 100 # words


def generate_RqUUID():
    return str(uuid.uuid4())


RqUID = generate_RqUUID()
print(RqUID)


def get_accesss_token():
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    payload={
        'scope': 'GIGACHAT_API_PERS'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'Authorization': f'Basic {AUTH_KEY}',
        'RqUID': RqUID
    }
    try:
        response = requests.post(url, headers=headers, data=payload, verify=False)
        if response.status_code == 200:
            return response.json()['access_token']
        else:
            print(f'Request error: {response.status_code}')
            return None
    except Exception as e:
        print(f'Exception (get_accesss_token): {e}')
        return None


def get_models():
    url = "https://gigachat.devices.sberbank.ru/api/v1/models"
    access_token = get_accesss_token()
    payload={}
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}',
        'RqUID': RqUID
    }

    response = requests.get( url, headers=headers, data=payload, verify=False)
    print(response.text)


def get_answer(prompt_content, role_content):
    access_token = get_accesss_token()
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    payload = json.dumps({
        "model": "GigaChat-Pro",
        "messages": [
            {
                "role": "system",
                "content": role_content
            },
            {
                "role": "user",
                "content": prompt_content
            }
        ],
        "stream": False,
        "update_interval": 0
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}',
        'RqUID': RqUID
    }
    
    try:
        response = requests.post(url, headers=headers, data=payload, verify=False)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            print(f'Request error (get_answer): {response.status_code} {response.text}, prompt: {prompt_content}')
            return None
    except Exception as e:
        print(f'Exception (get_answer): {e}')
        return None


def get_translation(text):
    role_contnet = ('Ты профессиональный переводчик с английского на русский язык. Переведи стилистически правильно следующий текст. '
                    'Не переводи названия игр, фильмов, мультфильмов, книг и прочих названий в кавычках. Не пиши ничего от себя, только перевод текста.')
    translation = get_answer(text, role_contnet)
    return translation


def get_short_version(text):
    role_contnet = f'Ты профессиональный копирайтер. Сократи следующий текст до {MIN_SHORT_VERSION_LENGTH}-{MAX_SHORT_VERSION_LENGTH} слов. Старайся чтобы текст звучал не как машинный перевод, а как статья написання русскоязычным автором.'
    translation = get_answer(text, role_contnet)
    return translation


def get_tokens_count(prompt):
    access_token = get_accesss_token()
    url = "https://gigachat.devices.sberbank.ru/api/v1/tokens/count"
    payload = json.dumps({
        "model": "GigaChat",
        "input": [
            prompt
        ]
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.post(url, headers=headers, data=payload, verify=False)
    return response.json()
