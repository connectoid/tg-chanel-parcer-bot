from parsing.parsing import get_articles
from database.orm import add_article
from gpt.gpt import get_translation, get_short_version


def main():
    articles = get_articles('gamespot')
    # articles = articles[:3]
    for article in articles:
        header = get_translation(article['header'])
        header_original = article['header']
        text = get_translation(article['text'])
        text_short = get_short_version(text)
        add_article(
            header=header,
            header_original=header_original,
            text=text,
            text_short=text_short,
            tags='it, dev, web',
            source_url=article['source_url'],
            image_url=article['image_url'],
            image_thumb_url=article['image_thumb_url'],
        )


if __name__ == '__main__':
    main()
    # articles = get_articles('gamespot')
    # for article in articles:
    #     print(article['header'])
    #     print(article['text'])
    #     # print(article['text_short'])
    #     print(article['image_url'])
    #     print(article['source_url'])