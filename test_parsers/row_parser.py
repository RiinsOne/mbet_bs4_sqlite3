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

    categories = soup.find_all('div', class_='category-container')
    with open('row_tds_data.txt', 'w', encoding='utf-8') as f:
        f.write(str(categories[0:2]))


def main():
    # url = 'https://www.marathonbet.ru/su/betting/Football/England?interval=ALL_TIME'
    # url = 'https://www.marathonbet.ru/su/betting/Football/England/EFL+Trophy/'
    url = 'https://www.marathonbet.ru/su/betting/Football/England/'
    get_data(get_html(url))


if __name__ == '__main__':
    main()
