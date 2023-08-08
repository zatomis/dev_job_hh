import requests
from terminaltables import DoubleTable
from dotenv import load_dotenv, find_dotenv
from datetime import datetime, timedelta
import time
import os

INDUSTRY = 48
POPULAR_LANGUAGES = ['JavaScript', 'Java', 'Python', 'Ruby', 'PHP', 'C++', 'CSS', 'C#', 'GO']


def predict_rub_salary(vacancy: dict):
    if vacancy:
        if vacancy['currency'] != 'RUR':
            return None
        if vacancy['from'] and vacancy['to']:
            return int((vacancy['from'] + vacancy['to']) / 2)
        if not vacancy['from']:
            return int(vacancy['to'] * 0.8)
        if not vacancy['to']:
            return int(vacancy['from'] * 1.2)
        if not vacancy['from'] and not vacancy['to']:
            return None
    else:
        return None


def convert_to_unix_time():
    return int(time.mktime((datetime.now() - timedelta(days=30)).timetuple()))


def get_salary_statistics_hh(location):
    url = f"https://api.hh.ru/vacancies"
    wage = {}
    unix_time = convert_to_unix_time()
    for language in POPULAR_LANGUAGES:
        page = 0
        payload = {
                    'text': f"Программист {language}",
                    'area': location,
                    'date_published_from': unix_time,
                    'page': page
                    }
        vacancies_processed = 0
        amount_of_salaries = 0
        total_pages = 1
        while page < total_pages:
            response = requests.get(url, payload)
            response.raise_for_status()
            job_list = response.json()
            page = payload['page']
            vacancies_found = job_list['found']
            jobs = job_list['items']
            total_pages = job_list['pages']
            for job in jobs:
                salary = predict_rub_salary(job['salary'])
                if salary:
                    amount_of_salaries = amount_of_salaries + salary
                    vacancies_processed += 1
            page += 1
            payload['page'] = page
        if vacancies_processed:
            average_salary = int(amount_of_salaries/vacancies_processed)
        statistics = {
            'vacancies_found': vacancies_found,
            'vacancies_processed': vacancies_processed,
            'average_salary': average_salary,
        }
        wage[language] = statistics
    return wage


def get_salary_statistics_sj(location, api_key):
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
        amount_of_salaries = 0
        vacancies_processed = 0
        while True:
            response = requests.get(url, headers=headers, params=payload)
            response.raise_for_status()
            work_options = response.json()
            page = payload['page']
            total_vacancies = response.json()['total']
            for job in work_options['objects']:
                job_salary = {
                                'currency': str(job['currency']).upper().replace('RUB', 'RUR'),
                                'from': job['payment_from'],
                                'to': job['payment_to']
                                }
                salary_js = predict_rub_salary(job_salary)
                if salary_js:
                    amount_of_salaries = amount_of_salaries + int(salary_js)
                    vacancies_processed += 1
            if not work_options['more']:
                break
            payload['page'] = page + 1
        if vacancies_processed:
            average_salary = int(amount_of_salaries/vacancies_processed)
        statistics = {
            'vacancies_found': total_vacancies,
            'vacancies_processed': vacancies_processed,
            'average_salary': average_salary,
        }
        wage[language] = statistics
    return wage


def display_statistics_table(statistic_wage, title):
    table = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
    for language, element_structure in statistic_wage.items():
        found, processed, salary = element_structure.values()
        table_row = [language, found, processed, salary]
        table.append(table_row)
    table_instance = DoubleTable(table, ' ' + title + ' ')
    table_instance.justify_columns[2] = 'center'
    print(table_instance.table)


if __name__ == '__main__':
    load_dotenv(find_dotenv())
    search_location = os.environ.get('SEARCH_LOCATION_HH')
    display_statistics_table(get_salary_statistics_hh(search_location), 'HeadHunter Moscow')
    search_location = os.environ.get('SEARCH_LOCATION_SJ')
    api_key = os.environ.get('SECRET_KEY_SJ')
    display_statistics_table(get_salary_statistics_sj(search_location, api_key), 'SuperJob Moscow')
