import csv
import os

from django.core.management import BaseCommand
from django.db import IntegrityError
from reviews import models
from users.models import User

from api_yamdb.settings import CSV_DIR

CONT = {
    'category': models.Category,
    'genre': models.Genre,
    'titles': models.Title,
    'genre_title': models.GenreTitle,
    'users': User,
    'review': models.Review,
    'comments': models.Comment,
}

CONT1 = {
    'category': ('category', models.Category),
    'title_id': ('title', models.Title),
    'genre_id': ('genre', models.Genre),
    'author': ('author', User),
    'review_id': ('review', models.Review),
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
