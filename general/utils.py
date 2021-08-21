import csv
import random


def parse_players_csv(file, data_source):
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

    return reader


def parse_projection_csv(file):
    decoded_file = file.read().decode('utf-8').splitlines()
    reader = csv.DictReader(decoded_file)

    return reader


def parse_name(name):
    # get first and last name from name string after processing
    name = name.strip().replace('.', '')
    name_ = name.split(' ')
    if len(name_) > 1:
        return name_[0], ' '.join(name_[1:])
    return name, ''


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
