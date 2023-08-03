import requests
from terminaltables import DoubleTable
from dotenv import load_dotenv, find_dotenv
from datetime import datetime, timedelta
import time
import calendar
from environs import Env

POPULAR_LANGUAGES = ['JavaScript', 'Java', 'Python', 'Ruby', 'PHP', 'C++', 'CSS', 'C#', 'GO']


def predict_rub_salary(vacancy: str | dict) -> str:
    match vacancy:
        case {'currency' : currency, 'from': from_money, 'gross': gross, 'to':  to_money}:
            if currency != 'RUR':
                return None
            elif from_money is None:
                return int(to_money * 0.8)
            elif to_money is None:
                return int(from_money * 1.2)
            else:
                return int((from_money + to_money)/2)
        case _:
            return None


def get_wage_hh(location):
    """
    Получить зарплату HH
    """
    url = f"https://api.hh.ru/vacancies"
    past_dateTime = datetime.now()
    days_in_month = calendar.monthrange(past_dateTime.year, past_dateTime.month)[1]
    past_dateTime -= timedelta(days=days_in_month)
    wage = {}
    for language in POPULAR_LANGUAGES:
        payload = {'text': f"Программист {language}", 'area': location}
        response = requests.get(url, payload)
        response.raise_for_status()
        page = 0
        vacancies_processed = 0
        salary = 0
        vacancies_found = response.json()['found']
        jobs = response.json()['items']
        while page < response.json()['pages']:
            payload = {'page': page}
            url = f"https://api.hh.ru/vacancies"
            response = requests.get(url, payload)
            response.raise_for_status()
            for job in jobs:
                convert_datetime = str(job['published_at']).replace('T', ' ').partition('+')[0]
                if datetime.strptime(convert_datetime, '%Y-%m-%d %H:%M:%S') > datetime.strptime(
                        f"{past_dateTime.year}-{past_dateTime.month}-{past_dateTime.day}", '%Y-%m-%d'):
                    income = predict_rub_salary(job['salary'])
                    if income:
                        salary = salary + income
                        vacancies_processed += 1
            page += 1
        if vacancies_processed:
            salary = int(salary/vacancies_processed)
        statistics = {
            'vacancies_found': vacancies_found,
            'vacancies_processed': vacancies_processed,
            'average_salary': salary,
        }
        wage[language] = statistics
    return wage


def get_wage_sj(location):
    """
    Получить зарплату SJ
    """
    env = Env()
    url = "https://api.superjob.ru/2.0/vacancies/"
    search_time_from = datetime.now() - timedelta(days=30)
    unix_time = int(time.mktime(search_time_from.timetuple()))
    headers = {
                'Host': 'api.superjob.ru',
                'X-Api-App-Id': env.str('SECRET_KEY')
              }
    wage = {}
    for language in POPULAR_LANGUAGES:
        payload = {
            'keyword': f'Программист {language}',
            'date_published_from': unix_time,
            'catalogues': 48,
            'town': location,
            'no_agreement': 1,
            'page': 0
        }

        salary = 0
        vacancies_processed = 0
        while True:
            response = requests.get(url, headers=headers, params=payload)
            response.raise_for_status()
            page_data = response.json()
            page = payload['page']
            for job in page_data['objects']:
                pay_for_work = {'currency': str(job['currency']).upper().replace('RUB','RUR'), 'from': job['payment_from'], 'gross': '', 'to': job['payment_to']}
                get_salary = predict_rub_salary(pay_for_work)
                if get_salary:
                    salary = salary + get_salary
                    vacancies_processed += 1
            if not page_data['more']:
                break
            payload['page'] = page + 1
        if vacancies_processed:
            salary = int(salary/vacancies_processed)
        statistics = {
            'vacancies_found': response.json()['total'],
            'vacancies_processed': vacancies_processed,
            'average_salary': salary,
        }
        wage[language] = statistics
    return wage


def display_statistics_table(statistic_wage, title):
    table = [['Язык программирования','Вакансий найдено','Вакансий обработано','Средняя зарплата']]
    for item_language, element_structure in statistic_wage.items():
        found, processed, salary = element_structure.values()
        table_row = [item_language,found,processed,salary]
        table.append(table_row)
    table_instance = DoubleTable(table, ' ' + title + ' ')
    table_instance.justify_columns[2] = 'center'
    print(table_instance.table)


if __name__ == '__main__':
    env = Env()
    load_dotenv(find_dotenv())
    try:
        search_location = env.int('SEARCH_LOCATION_HH')
        display_statistics_table(get_wage_hh(search_location),'HeadHunter Moscow')
        search_location = env.int('SEARCH_LOCATION_SJ')
        display_statistics_table(get_wage_sj(search_location),'SuperJob Moscow')
    except requests.exceptions.HTTPError as error:
        print(f"Ошибка {error.response.text}")
