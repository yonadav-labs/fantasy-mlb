from general.models import Slate, Game, Player
from general.utils import parse_name, parse_game_info


def get_slate(name, data_source):
    slate, _ = Slate.objects.update_or_create(name=name, data_source=data_source)
    return slate


def load_players(slate, players_info, projection_info):
    # TODO: take care of projection_info
    players = []
    for player_info in players_info:
        if slate.data_source == 'DraftKings':
            first_name, last_name = parse_name(player_info['Name'])
            visit_team, home_team, _ = parse_game_info(slate.data_source, player_info['Game Info'])
            opponent = f'@{home_team}' if visit_team==player_info['TeamAbbrev'] else visit_team

            player, _ = Player.objects.update_or_create(slate=slate,
                                                        rid=player_info['ID'],
                                                        first_name=first_name,
                                                        last_name=last_name,
                                                        team=player_info['TeamAbbrev'],
                                                        opponent=opponent,
                                                        actual_position=player_info['Position'],
                                                        position=player_info['Roster Position'],
                                                        proj_points=player_info['AvgPointsPerGame'],
                                                        salary=player_info['Salary'] or 0
                                                        )
        elif slate.data_source == 'FanDuel':
            visit_team, home_team, _ = parse_game_info(slate.data_source, player_info['Game'])
            opponent = f'@{home_team}' if visit_team==player_info['Team'] else visit_team
            proj_points = player_info['FPPG'] or 0
            player, _ = Player.objects.update_or_create(slate=slate,
                                                        rid=player_info['Id'],
                                                        first_name=player_info['First Name'],
                                                        last_name=player_info['Last Name'],
                                                        team=player_info['Team'],
                                                        opponent=opponent,
                                                        actual_position=player_info['Position'],
                                                        position=player_info['Roster Position'],
                                                        proj_points=proj_points,
                                                        salary=player_info['Salary'] or 0,
                                                        injury=player_info['Injury Details']
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

        game, _ = Game.objects.update_or_create(slate=slate,
                                                home_team=home_team,
                                                visit_team=visit_team,
                                                defaults={
                                                    'time': time
                                                })
        games.append(game)

    return games
