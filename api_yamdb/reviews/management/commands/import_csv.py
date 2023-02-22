import csv
import os

from django.core.management import BaseCommand
from django.db import IntegrityError

from api_yamdb.settings import CSV_DIR
from reviews.models import (
    Category,
    Comment,
    Genre,
    GenreTitle,
    Review,
    Title
)
from users.models import User

CONT = {
    'category': Category,
    'genre': Genre,
    'titles': Title,
    'genre_title': GenreTitle,
    'users': User,
    'review': Review,
    'comments': Comment,
}

CONT1 = {
    'category': ('category', Category),
    'title_id': ('title', Title),
    'genre_id': ('genre', Genre),
    'author': ('author', User),
    'review_id': ('review', Review),
}


def open_file(file_name):
    file = file_name + '.csv'
    path = os.path.join(CSV_DIR, file)
    try:
        with (open(path, encoding='utf-8')) as file:
            return list(csv.reader(file))
    except FileNotFoundError:
        print(f'Файл {file} не найден.')
        return


def change_values(data_csv):
    data_csv_copy = data_csv.copy()
    for field_key, field_value in data_csv.items():
        if field_key in CONT1.keys():
            field_key0 = CONT1[field_key][0]
            data_csv_copy[field_key0] = CONT1[field_key][1].objects.get(
                pk=field_value)
    return data_csv_copy


def load_csv(file_name, class_name):
    table_not_loaded = f'Таблица {class_name.__qualname__} не загружена.'
    table_loaded = f'Таблица {class_name.__qualname__} загружена.'
    data = open_file(file_name)
    rows = data[1:]
    for row in rows:
        data_csv = dict(zip(data[0], row))
        data_csv = change_values(data_csv)
        try:
            table = class_name(**data_csv)
            table.save()
        except (ValueError, IntegrityError) as error:
            print(f'Ошибка в загружаемых данных. {error}. '
                  f'{table_not_loaded}')
            break
    print(table_loaded)


class Command(BaseCommand):

    def handle(self, *args, **options):
        for key, value in CONT.items():
            print(f'Загрузка таблицы {value.__qualname__}')
            load_csv(key, value)
