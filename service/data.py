import os
import pandas as pd
import json

LEGISLATURE_SEPARATOR = '.'
DATA_DIR = 'data'


def data_index():
    result = {}
    dir_content = os.scandir(DATA_DIR)
    for file in dir_content:
        if file.is_file() and file.name.endswith('.json'):
            filename = file.name[:-5]  # Rimuovi l'estensione .json
            filename_parts = filename.rsplit(LEGISLATURE_SEPARATOR, 1)  # Divide solo all'ultima occorrenza di '.'

            bot_name = filename_parts[0]  # Prende la parte principale
            legislature = int(filename_parts[1])  # Prende l'ultima parte come numero

            if bot_name not in result:
                result[bot_name] = []
            result[bot_name].append(legislature)

    # sort legislature
    for bot_name in result:
        result[bot_name].sort(reverse=True)

    return result


def get_filepath(bot_name, legislature):
    filepath = f'{DATA_DIR}/{bot_name}{LEGISLATURE_SEPARATOR}{legislature}.json'
    return filepath


def get_data(name: str, legislature: int):
    filepath = get_filepath(name, legislature)
    with open(filepath) as file:
        return json.load(file)


def get_dataframe(name: str, legislature: int):
    filepath = get_filepath(name, legislature)
    return pd.read_json(filepath)
