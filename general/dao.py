from fuzzywuzzy import fuzz
from fuzzywuzzy import process

from general.models import Slate, Game, Player, BaseGame, BasePlayer
from general.utils import parse_name, parse_game_info, get_delta


def get_slate(name, data_source):
    slate, _ = Slate.objects.update_or_create(name=name, data_source=data_source)
    return slate


def get_base_game(visit_team, home_team, data_source):
    game = BaseGame.objects.filter(visit_team=visit_team, home_team=home_team, data_source=data_source).first()

    return game


def get_base_player(name, player_names):
    match = process.extractOne(name, player_names, scorer=fuzz.token_sort_ratio)
    id = match[0].split('@#@')[1]
    player = BasePlayer.objects.get(pk=id)

    return player


def get_custom_projection(name, player_names):
    match = process.extractOne(name, player_names, scorer=fuzz.token_sort_ratio)
    proj = match[0].split('@#@')[1]
    proj = float(proj) + get_delta()

    return max(proj, 0)


def load_players(slate, players_info, projection_info):
    # prepare player match
    base_players = BasePlayer.objects.filter(data_source=slate.data_source)
    base_names = [f'{player.first_name} {player.last_name} @#@{player.id}' for player in base_players]

    players = []
    for player_info in players_info:
        if slate.data_source == 'DraftKings':
            rid = player_info['ID']
            name = player_info['Name']
            first_name, last_name = parse_name(name)
            game_info = player_info['Game Info']
            team = player_info['TeamAbbrev']
            # proj_points = player_info['AvgPointsPerGame'] or 0
            actual_position = player_info['Position']
            position = player_info['Roster Position']
            salary = player_info['Salary'] or 0
            injury = ''
        elif slate.data_source == 'FanDuel':
            rid = player_info['Id']
            name = player_info['Nickname']
            first_name = player_info['First Name']
            last_name = player_info['Last Name']
            game_info = player_info['Game']
            team = player_info['Team']
            # proj_points = player_info['FPPG'] or 0
            actual_position = player_info['Position']
            position = player_info['Roster Position']
            salary = player_info['Salary'] or 0
            injury = player_info['Injury Details']

        visit_team, home_team, _ = parse_game_info(slate.data_source, game_info)
        base_player = get_base_player(name, base_names)
        proj_points = get_custom_projection(name, projection_info)

        if base_player:
            if slate.data_source == 'FanDuel':  # put FD's injury
                base_player.injury = injury or ''
                base_player.save()
            else:
                injury = base_player.injury or ''

        handedness = base_player.handedness if base_player else ''
        start = base_player.start if base_player else ''
        opp_pitcher_id = base_player.opp_pitcher_id if base_player else None

        opponent = f'@{home_team}' if visit_team==team else visit_team
        player, _ = Player.objects.update_or_create(slate=slate,
                                                    rid=rid,
                                                    first_name=first_name,
                                                    last_name=last_name,
                                                    team=team,
                                                    opponent=opponent,
                                                    actual_position=actual_position,
                                                    position=position,
                                                    proj_points=proj_points,
                                                    salary=salary,
                                                    injury=injury,
                                                    handedness=handedness,
                                                    start=start,
                                                    opp_pitcher_id=opp_pitcher_id
                                                    )
        players.append(player)

    return players


def load_games(slate, players_info):
    # get unique texts
    if slate.data_source == 'DraftKings':
        games_data = set(player['Game Info'] for player in players_info)
    elif slate.data_source == 'FanDuel':
        games_data = set(player['Game'] for player in players_info)

    games = []
    for game_info in games_data:
        visit_team, home_team, time = parse_game_info(slate.data_source, game_info)
        base_game = get_base_game(visit_team, home_team, slate.data_source)
        ou = base_game.ou if base_game else 0

        game, _ = Game.objects.update_or_create(slate=slate,
                                                home_team=home_team,
                                                visit_team=visit_team,
                                                defaults={
                                                    'time': time,
                                                    'ou': ou
                                                })
        games.append(game)

    return games
