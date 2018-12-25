from newsapi import NewsApiClient


def get_news_from_API():
    newsapi = NewsApiClient(api_key='d26bc5cb82af4a4dbe8f0813d5cdd878')

    # /v2/top-headlines
    top_headlines = newsapi.get_top_headlines(q='stock market',
                                              # sources='bbc-news,the-verge',
                                              category='business',
                                              language='en',
                                              country='us'
                                              )

    print(type(top_headlines))

    return top_headlines




get_news_from_API()