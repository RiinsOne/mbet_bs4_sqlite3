import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')


import requests
from bs4 import BeautifulSoup as bs


def get_html(url):
    r = requests.get(url)
    return r.text


def get_data(html):
    soup = bs(html, 'lxml')

    # categories = soup.find_all('div', class_='category-container')
    category_headers = soup.find_all('table', class_='category-header')

    # for num, category in enumerate(categories, 1):
    #     name_spans = category.find('table', class_='category-header').find('td', class_='category-label-td').find('h2', class_='category-label').find_all('span')
    #     category_name = name_spans[0].text + name_spans[1].text
    #
    #     link = category.find('table', class_='category-header').find('td', class_='category-label-td').find('a', class_='category-label-link').get('href')
    #
    #     print(num, category_name, link)

    for num, category in enumerate(category_headers, 1):
        name_spans = category.find('td', class_='category-label-td').find('h2', class_='category-label').find_all('span')
        category_name = name_spans[0].text + name_spans[1].text

        link = category.find('td', class_='category-label-td').find('a', class_='category-label-link').get('href')

        print(num, category_name, link)


def main():
    url = 'https://www.marathonbet.ru/su/betting/Football/England?interval=ALL_TIME'
    # url = 'https://www.marathonbet.ru/su/betting/Football/England'
    get_data(get_html(url))


if __name__ == '__main__':
    main()
