import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')


import requests
from bs4 import BeautifulSoup as bs
from collections import namedtuple
import datetime as dt
import match_dbcore as match_db


MatchBlock = namedtuple('Block', 'title, date, result_1, draw_X, result_2, dc_1X, dc_12, dc_X2, total_under, total_over')


class Match(MatchBlock):

    def __str__(self):
        return '{title}, {date}, {result_1}, {draw_X}, {result_2}, {dc_1X}, {dc_12}, {dc_X2}, {total_under}, {total_over}'.format(
            title=self.title,
            date=self.date,
            result_1=self.result_1,
            draw_X=self.draw_X,
            result_2=self.result_2,
            dc_1X=self.dc_1X,
            dc_12=self.dc_12,
            dc_X2=self.dc_X2,
            total_under=self.total_under,
            total_over=self.total_over
        )


BASE_URL = {
    'APL': 'https://www.marathonbet.ru/su/betting/Football/England?interval=ALL_TIME',
    'RPL': ''
}


class MatchParser:
    url_body = 'https://www.marathonbet.ru'
    # base_url = {
    #     'APL': 'https://www.marathonbet.ru/su/betting/Football/England?interval=ALL_TIME',
    #     'RPL': ''
    # }
    leagues_urls = list()
    matches_urls = list()
    match_collections = list()

    def __init__(self, base_league):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3'
        }
        self.base_league = base_league
        self.get_leagues_urls()
        self.get_matches_urls()

    @staticmethod
    def month_to_num(month):
        switcher = {
            'янв': 1, 'фев': 2, 'мар': 3, 'апр': 4, 'мая': 5, 'июн': 6, 'июл': 7, 'авг': 8, 'сен': 9, 'окт': 10, 'ноя': 11, 'дек': 12
        }
        return switcher[month]

    def get_html(self, url):
        r = self.session.get(url)
        return r.text

    def get_leagues_urls(self):
        self.leagues_urls.clear()
        # text = self.get_html(self.base_url['APL'])
        text = self.get_html(self.base_league)
        soup = bs(text, 'lxml')

        main_words = ['Premier+League', 'Championship']
        main_leagues = set(main_words)

        container = soup.find_all('div', class_='category-container')
        for div in container:
            href = div.find('a', class_='category-label-link').get('href').strip()
            for main_word in main_leagues:
                if main_word in href:
                    self.leagues_urls.append(self.url_body + href)

    def get_matches_urls(self):
        self.matches_urls.clear()

        for url in self.leagues_urls:
            text = self.get_html(url)
            soup = bs(text, 'lxml')

            container = soup.find_all('table', class_='member-area-content-table')
            # change container slices
            for div in container:
                href = div.find('a', class_='member-link').get('href').strip()
                self.matches_urls.append(self.url_body + href)

    def print_leagues_urls(self):
        for num, url in enumerate(self.leagues_urls, 1):
            print(num, url)

    def print_matches_urls(self):
        for num, url in enumerate(self.matches_urls, 1):
            print(num, url)

    def save_match_to_db(self):
        self.get_match_data()
        match_db.save_to_db(self.match_collections)

    def print_all_data(self):
        match_db.select_all()

    def delete_all_data(self):
        match_db.delete_all()

    def get_match_data(self):
        self.match_collections.clear()

        for match in self.matches_urls:
            text = self.get_html(match)
            soup = bs(text, 'lxml')

            values_dict = {
                'title': None,
                'date': None,
                'result_1': None,
                'draw_X': None,
                'result_2': None,
                'dc_1X': None,
                'dc_12': None,
                'dc_X2': None,
                'total_under': None,
                'total_over': None
            }

            # ---------------------------------------------
            # Match team names
            name_container = soup.find('table', class_='member-area-content-table').find_all('span')
            values_dict['title'] = '{first_team} - {second_team}'.format(
                first_team=name_container[0].text.strip(),
                second_team=name_container[1].text.strip()
            )
            # ---------------------------------------------

            # ---------------------------------------------
            # Match date
            raw_date = soup.find('table', class_='member-area-content-table').find('td', class_='date').text.strip()
            raw_date = raw_date.split(' ')
            # print(raw_date)

            if len(raw_date) == 1:
                date = dt.date.today()
                time = dt.datetime.strptime(raw_date[0], '%H:%M').time()
                values_dict['date'] = dt.datetime.combine(date, time).strftime('%d.%m.%Y %H:%M')

            if len(raw_date) == 3:
                date = dt.datetime(
                    dt.date.today().year,
                    self.month_to_num(raw_date[1]),
                    int(raw_date[0]),
                )
                time = dt.datetime.strptime(raw_date[2], '%H:%M').time()
                values_dict['date'] = dt.datetime.combine(date, time).strftime('%d.%m.%Y %H:%M')

            # print(values_dict[date].strftime('%d.%m.%Y %H:%M'))
            # ---------------------------------------------

            # ---------------------------------------------
            # Matches main results
            result_list = ['price', 'height-column-with-price', 'first-in-main-row', 'coupone-width-1']
            result_container = soup.find_all('td', {'class': result_list})[:6]

            rc_index = 0
            for key in list(values_dict.keys())[2:8]:
                values_dict[key] = float(result_container[rc_index].find('span').text.strip())
                rc_index += 1
            # print(values_dict)
            # ---------------------------------------------

            # ---------------------------------------------
            # Matches under and over totals
            total_field = soup.find('div', {'data-block-type-id': '3'}).find_all('div', class_='market-inline-block-table-wrapper')[0]
            lines = total_field.find('table', class_='td-border').find_all('tr')[1:-2]

            coeff_value_names = []
            main_index = '(2.5)'

            for line in lines:
                coeff_value_name = line.find('div', class_='coeff-value').text.strip()
                coeff_value_names.append(coeff_value_name)

            coeff_index = coeff_value_names.index(main_index)
            index_line = lines[coeff_index].find_all('td')

            values_dict['total_under'] = float(index_line[0].find('div', class_='coeff-price').find('span').text.strip())
            values_dict['total_over'] = float(index_line[1].find('div', class_='coeff-price').find('span').text.strip())
            # print(values_dict['total_under'], values_dict['total_over'])
            # ---------------------------------------------

            # match_data = Match(**values_dict)
            match_data = MatchBlock(**values_dict)
            self.match_collections.append(match_data)


def main():
    apl = MatchParser(BASE_URL['APL'])
    # apl.print_leagues_urls()
    # apl.print_matches_urls()
    apl.delete_all_data()
    apl.save_match_to_db()
    apl.print_all_data()


if __name__ == '__main__':
    main()
