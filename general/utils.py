import csv
import random

from datetime import datetime


def csv_to_list(csv_reader):
    result = []
    for row in csv_reader:
        result.append(row)

    return result


def parse_players_csv(file, data_source):
    """
    :param file: stream
    :return: list
    """
    decoded_file = file.read().decode('utf-8').splitlines()
    net_data = []

    if data_source == 'DraftKings':
        row_start = 7
        col_start = 11
    elif data_source == 'FanDuel':
        row_start = 6
        col_start = 39

    for row in decoded_file[row_start:]:
        net_data.append(row[col_start:])

    reader = csv.DictReader(net_data)

    return csv_to_list(reader)


def parse_projection_csv(file):
    """
    :return: list
    """
    decoded_file = file.read().decode('utf-8').splitlines()
    reader = csv.DictReader(decoded_file)

    return csv_to_list(reader)


def parse_name(name):
    """
    get first and last name from name string after processing
    """
    name = name.strip().replace('.', '')
    name_ = name.split(' ')
    if len(name_) > 1:
        return name_[0], ' '.join(name_[1:])
    return name, ''


def parse_game_info(data_source, game_info):
    if data_source == 'DraftKings':
        parts = game_info.split(' ')
        visit_team, home_team = parts[0].split('@')
        time = parts[2]
    elif data_source == 'FanDuel':
        visit_team, home_team = game_info.split('@')
        time = ""

    return visit_team, home_team, time


def get_delta(ii, ds):
    factor = (-10, 10)
    sign = 1 if random.randrange(0, 2) else -1
    delta = random.randrange(factor[0], factor[1]) / 10.0

    return delta * sign

    if not float(ii['proj_points']):
        factor = (0, 1)
    elif 'P' in ii['position']:
        factor = (3, 20)
    else:
        factor = (1, 9)
    sign = 1 if random.randrange(0, 2) else -1
    delta = random.randrange(factor[0], factor[1]) / 10.0

    # if ds != 'DraftKings':
    #     player = BasePlayer.objects.filter(data_source='DraftKings', uid=ii['id']).first()
    #     sign = 1 if player and player.proj_delta > 0 else -1

    return delta * sign
