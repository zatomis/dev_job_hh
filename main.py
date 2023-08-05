import requests
from terminaltables import DoubleTable
from dotenv import load_dotenv, find_dotenv
from datetime import datetime, timedelta
import time
from environs import Env

POPULAR_LANGUAGES = ['C++']
INDUSTRY = 48
# POPULAR_LANGUAGES = ['JavaScript', 'Java', 'Python', 'Ruby', 'PHP', 'C++', 'CSS', 'C#', 'GO']


def predict_rub_salary(vacancy: dict):
    if vacancy:
        if vacancy['currency'] != 'RUR':
            return None
        elif vacancy['from']:
            return int(vacancy['from'] * 1.2)
        elif vacancy['to']:
            return int(vacancy['to'] * 0.8)
        else:
            return int((vacancy['from'] * vacancy['to']) / 2)
    else:
        return None


def convert_to_unix_time():
    return int(time.mktime((datetime.now() - timedelta(days=30)).timetuple()))


def get_wage_hh(location):
    """
    Получить зарплату HH
    """
    url = f"https://api.hh.ru/vacancies"
    wage = {}
    unix_time = convert_to_unix_time()
    for language in POPULAR_LANGUAGES:
        payload = {'text': f"Программист {language}", 'area': location, 'date_published_from': unix_time}
        response = requests.get(url, payload)
        response.raise_for_status()
        page = 0
        vacancies_processed = 0
        salary = 0
        vacancies_found = response.json()['found']
        jobs = response.json()['items']
        total_pages = response.json()['pages']
        while page < total_pages:
            for job in jobs:
                pay = predict_rub_salary(job['salary'])
                if pay:
                    salary = salary + pay
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


def get_wage_sj(location, api_key):
    """
    Получить зарплату SJ
    """
    url = "https://api.superjob.ru/2.0/vacancies/"
    unix_time = convert_to_unix_time()
    headers = {
                'Host': 'api.superjob.ru',
                'X-Api-App-Id': api_key
              }
    wage = {}
    for language in POPULAR_LANGUAGES:
        payload = {
            'keyword': f'Программист {language}',
            'date_published_from': unix_time,
            'catalogues': INDUSTRY,
            'town': location,
            'page': 0
        }
        salary = 0
        vacancies_processed = 0
        while True:
            response = requests.get(url, headers=headers, params=payload)
            response.raise_for_status()
            salary_information = response.json()
            page = payload['page']
            for job in salary_information['objects']:
                pay_for_work = {
                                'currency': str(job['currency']).upper().replace('RUB', 'RUR'),
                                'from': job['payment_from'],
                                'gross': '',
                                'to': job['payment_to']
                                }
                pay = predict_rub_salary(pay_for_work)
                if pay:
                    salary = salary + int(pay)
                    vacancies_processed += 1
            if not salary_information['more']:
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
    table = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
    for item_language, element_structure in statistic_wage.items():
        found, processed, salary = element_structure.values()
        table_row = [item_language, found, processed, salary]
        table.append(table_row)
    table_instance = DoubleTable(table, ' ' + title + ' ')
    table_instance.justify_columns[2] = 'center'
    print(table_instance.table)


if __name__ == '__main__':
    env = Env()
    load_dotenv(find_dotenv())
    search_location = env.int('SEARCH_LOCATION_HH')
    display_statistics_table(get_wage_hh(search_location), 'HeadHunter Moscow')
    search_location = env.int('SEARCH_LOCATION_SJ')
    api_key = env.str('SECRET_KEY')
    display_statistics_table(get_wage_sj(search_location, api_key), 'SuperJob Moscow')
