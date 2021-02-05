import sys
import io
import os

sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')


import requests
from bs4 import BeautifulSoup as bs


try:
    os.remove('team.csv')
except OSError:
    pass


def get_html(url):
    r = requests.get(url)
    return r.text


def get_data(html):
    soup = bs(html, 'lxml')

    tds = soup.find_all('div', class_='coupon-row')
    # for num, div in enumerate(tds):
    #     div_names = div.find('table', class_='member-area-content-table')
        # print(num, div_names, '\n')

    tuple_team_names = tuple()

    for div in tds:
        div_names = div.find('table', class_='member-area-content-table')
        team_names = div_names.find_all('span')
        print('1. ' + team_names[0].text, ' - ', '2. ' + team_names[1].text)
        with open('team.csv', 'a', encoding='utf-8') as f:
            line = team_names[0].text, ' - ', team_names[1].text + '\n'
            f.writelines(line)


def main():
    # url = 'https://www.marathonbet.ru/su/betting/Football/England/'
    url = 'https://www.marathonbet.ru/su/betting/Football/England?interval=ALL_TIME'
    get_data(get_html(url))
    # print(get_html(url))


if __name__ == '__main__':
    main()
