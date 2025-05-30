from parsing.parsing import get_articles
from database.orm import add_article
# from gpt.gpt import get_translation, get_short_version
from gpt.deepseek import get_short_version, translate


def parse(source, create_short_version=False):
    articles = get_articles(source)
    for article in articles:
        header = translate(article['header'])
        text = article['text']
        if create_short_version:
            summary = get_short_version(text)
        else:
            summary = article['summary']
        source_url = article['source_url']
        image_urls_list = article['image_urls']
        image_urls_string = ','.join(image_urls_list)
        add_article(
            header=header,
            summary=summary,
            text=text,
            source_url=source_url,
            image_urls=image_urls_string,
        )
        print(f'SUMMARY: {summary}')


def main():
    parse('gamespot', create_short_version=True)
    parse('eurogamer')
    parse('pcgamer', create_short_version=True)
    parse('gamesradar', create_short_version=True)



if __name__ == '__main__':
    main()

    # articles = get_articles('eurogamer')
    # for article in articles:
    #     print(article['header'])
    #     print(article['summary'])
    #     print(article['text'])
    #     print(article['image_urls'])
    #     print(article['source_url'])
        # print('\n')
