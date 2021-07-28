import random
import datetime
import requests

import os
from os import sys, path
import django

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fantasy_mlb.settings")
django.setup()

from general.models import *
from general import html2text
from scripts.get_slate import get_slate


def get_delta(ii, ds):
    if not float(ii['proj_points']):
        factor = (0, 1)
    elif 'P' in ii['position']:
        factor = (3, 20)
    else:
        factor = (1, 9)
    sign = 1 if random.randrange(0, 2) else -1
    delta = random.randrange(factor[0], factor[1]) / 10.0

    if ds != 'DraftKings':
        player = Player.objects.filter(data_source='DraftKings', uid=ii['id']).first()
        sign = 1 if player and player.proj_delta > 0 else -1
    return delta * sign


def get_players(data_source, data_source_id):
    try:
        slate_id = get_slate(data_source)

        url = 'https://www.rotowire.com/daily/tables/optimizer-mlb.php' + \
              '?siteID={}&slateID={}&projSource=RotoWire&rst=RotoWire'.format(data_source_id, slate_id)
        print (url)

        players = requests.get(url).json()

        fields = ['money_line', 'position', 'opponent', 'actual_position', 
                  'salary', 'team', 'opp_pitcher_id']

        print (data_source, len(players))
        if len(players) > 20:
            Player.objects.filter(data_source=data_source, lock_update=False).update(play_today=False)

            for ii in players:
                ii['position'] = ii['position'].replace('C1', 'C')
                ii['actual_position'] = ii['actual_position'].replace('C1', 'C')

                defaults = { key: str(ii[key]).replace(',', '') for key in fields }
                defaults['play_today'] = True

                defaults['start'] = '-' if ii['lineup_status'] == 'Yes' else ii['lineup_status']
                defaults['handedness'] = html2text.html2text(ii['handedness']).strip().replace('B', 'S')
                defaults['start_status'] = html2text.html2text(ii['team_lineup_status']).strip().replace('E', 'P')
                defaults['injury'] = html2text.html2text(ii['injury']).strip()

                player = Player.objects.filter(uid=ii['id'], data_source=data_source).first()
                if not player:
                    defaults['uid'] = ii['id']
                    defaults['data_source'] = data_source
                    defaults['first_name'] = ii['first_name'].replace('.', '')
                    defaults['last_name'] = ii['last_name'].replace('.', '')

                    defaults['proj_delta'] = get_delta(ii, data_source)
                    defaults['proj_points'] = float(ii['proj_points']) + defaults['proj_delta']
        
                    Player.objects.create(**defaults)
                else:
                    if player.lock_update:
                        player.play_today = True
                    else:
                        criteria = datetime.datetime.combine(datetime.date.today(), datetime.time(22, 30, 0)) # utc time - 5:30 pm EST
                        if player.updated_at.replace(tzinfo=None) < criteria:
                            defaults['proj_delta'] = get_delta(ii, data_source)
                            defaults['proj_points'] = float(ii['proj_points']) + defaults['proj_delta']

                        for attr, value in defaults.items():
                            setattr(player, attr, value)
                    player.save()
    except:
        print("*** some thing is wrong ***")


if __name__ == "__main__":
    for id, ds in enumerate(['DraftKings', 'FanDuel'], 1):
        get_players(ds, id)
