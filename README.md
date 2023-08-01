# Сравниваем вакансии программистов

### Как это работает
Текущий скрипт проводит анализ данных: зарплат программистов по г.Москва за месяц, по средствам запросов - двух популярных сайтов:

*https://superjob.ru/*

*https://hh.ru/*

### Как запустить

Для запуска сайта вам понадобится Python третьей версии, версии от 10й.
Для работы статистики с сайта *https://api.superjob.ru/*
необходимо получить ключ

Скачайте код с GitHub. Затем установите зависимости

```sh
pip install -r requirements.txt
```

Запустите скрипт

```sh
python3 main.py
```

![img.png](img.png)

### Переменные окружения

Часть настроек проекта берётся из переменных окружения. Чтобы их определить, создайте файл `.env` рядом с `main.py` и запишите туда данные в таком формате: `ПЕРЕМЕННАЯ=значение`.

Доступны 3 переменные:
- `SECRET_KEY` — ключ для работы https://api.superjob.ru/
- `SEARCH_LOCATION_HH` — город поиска для HH, Москва = 1
- `SEARCH_LOCATION_SJ` — город поиска для SJ, Москва = 4

## Автор

* **Zatomis** - *Цель проекта* - Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [Devman](https://dvmn.org)
