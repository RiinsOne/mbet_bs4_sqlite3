import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')


import requests
from bs4 import BeautifulSoup as bs
from time import time


def get_html(url):
    r = requests.get(url)
    return r.text


def get_matches_list(html):
    soup = bs(html, 'lxml')
    tables = soup.find_all('table', class_='member-area-content-table')

    links = []
    link_body = 'https://www.marathonbet.ru'
    for table in tables:
        link = table.find('a', class_='member-link').get('href')
        links.append(link_body + link)

    # for num, link in enumerate(links, 1):
    #     print(num, link)

    return links


def get_data(html):
    soup = bs(html, 'lxml')
    total_field = soup.find('div', {'data-block-type-id': '3'}).find_all('div', class_='market-inline-block-table-wrapper')[0]
    lines = total_field.find('table', class_='td-border').find_all('tr')[1:-2]
    # for num, line in enumerate(lines, 1):
    #     print(num, line)

    coeff_value_names = []

    # dict_value_names = {}
    # dict_key = 0

    for line in lines:
        coeff_value_name = line.find('div', class_='coeff-value').text.strip()
        coeff_value_names.append(coeff_value_name)
        # dict_value_names[dict_key] = coeff_value_name
        # dict_key += 1

    needed_index = '(2.5)'

    # better to use list to find needed index
    needed_index_value = coeff_value_names.index(needed_index)

    # needed_index_value = list(dict_value_names.values()).index(needed_index)

    needed_index_line = lines[needed_index_value].find_all('td')
    total_under_value = needed_index_line[0].find('div', class_='coeff-price').find('span').text.strip()
    total_over_value = needed_index_line[1].find('div', class_='coeff-price').find('span').text.strip()
    print(total_under_value, total_over_value)


def main():
    # url1 = 'https://www.marathonbet.ru/su/betting/Football/England/Premier+League/Fulham+vs+Leicester+City+-+10667675'
    url2 = 'https://www.marathonbet.ru/su/betting/Football/England/Premier+League+-+21520?interval=ALL_TIME'
    now = time()

    links = get_matches_list(get_html(url2))

    for match_url in links:
        get_data(get_html(match_url))
    print('spent time', time() - now)

if __name__ == '__main__':
    main()
