import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
# DEEPSEEK_API_KEY = 'sk-7df9a4c320d849a7b25a1d40b69516fe'

BASE_DEEPSEEK_URL = 'https://api.deepseek.com'
MIN_SHORT_VERSION_LENGTH = 60 # words
MAX_SHORT_VERSION_LENGTH = 80 # words



def get_answer(prompt):
    print(DEEPSEEK_API_KEY)
    print(f'Fetch data with prompt {prompt}...')
    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=BASE_DEEPSEEK_URL)

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": prompt},
        ],
        stream=False
    )
    response_json = response.json()
    print(f'Recived response: {response_json}')
    answer = response.choices[0].message.content
    print(answer)
    return answer


def get_short_version(text):
    prompt = f'Сократи следующий текст до {MIN_SHORT_VERSION_LENGTH}-{MAX_SHORT_VERSION_LENGTH} слов и переведи на русский язык, при этом не начинай текст с каких-то лишних фраз от себя, должен быть только переведенный сокращенный текст: {text}'
    short_version = get_answer(prompt)
    return short_version


# short_text = get_short_version('Five video games have been recognised for their outstanding soundtracks and nominated for a 2025 Grammy Award.')

# print(short_text)