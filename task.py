import requests
import lxml.html as html
import os
import datetime

HOME_URL = 'https://nypost.com/'

X_CATEGORIES = '//div[@class="clearfix home-page-section A home-page-module" or @class="clearfix home-page-section B home-page-module"]/div/h2/a/text()'
X_NEWS_X_CAT = '//div[@class="clearfix home-page-section A home-page-module" or @class="clearfix home-page-section B home-page-module"][]/div[@class="featured-stories"]/article/div/div/a/@href'
X_TITLE = '//h1/text()'
X_BODY = '//div[@class="entry-content entry-content-read-more"]/p/text()'
X_IMAGES = '//div[@class="entry-content entry-content-read-more"]//img/@src'



def parse_home():
    try:
        response = requests.get(HOME_URL)

        if response.status_code != 200:
            raise ValueError(f'Server status code: {response.status_code}')

        categories = response.content.decode('utf-8')
        html_var = html.fromstring(categories)
        list_categories = enumerate(html_var.xpath(X_CATEGORIES))
        get_news(html_var, list_categories)
    except ValueError as ve:
        print(ve)


def create_dir(name):
    today = datetime.datetime.today().strftime('%Y-%m-%d')

    if not os.path.isdir(today):
        os.mkdir(today)

    new_dir = f'{today}/{name}'

    if os.path.isdir(new_dir):
        return(new_dir)

    os.mkdir(new_dir)

    return(new_dir)


def get_news(html_var, list_categories):

    for category in list_categories:
        category_id = category[0]+1
        category_name = category[1]

        cat_dir = create_dir(category_name)

        category_x = X_NEWS_X_CAT.replace('[]', f'[{category_id}]')
        links = html_var.xpath(category_x)

        for link in links:
            parce_notice(link, cat_dir)


def parce_notice(link, cat_dir):
    try:
        response = requests.get(link)

        if response.status_code != 200:
            raise ValueError(f'Server status code: {response.status_code}')

        notice = response.content.decode('utf-8')
        notice_page = html.fromstring(notice)

        title = notice_page.xpath(X_TITLE)[0].strip()

        title = title.replace('\"', '')
        title = title.replace(':', '')
        title = title.replace('?', '')
        title = title.replace('¿', '')
        title = title.replace('!', '')
        title = title.replace('¡', '')

        body = notice_page.xpath(X_BODY)
        with open(f'{cat_dir}/{title}.txt', 'w', encoding='utf-8') as f:
            f.write(title)
            f.write('\n\n')
            for p in body:
                f.write(p)
                f.write('\n')

    except ValueError as ve:
        print(ve)
    except OSError as ve:
        print(ve)


def run():
    parse_home()


if __name__ == '__main__':
    run()