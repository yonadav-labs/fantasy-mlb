import operator as op
from ortools.linear_solver import pywraplp
from .models import *

import pdb
class Roster:
    POSITION_ORDER = {
        "P": 0,
        "C": 1,
        "1B": 2,
        "2B": 3,
        "3B": 4,
        "SS": 5,
        "OF": 6
    }

    def __init__(self, ds):
        self.players = []
        self.ds = ds
        self.drop = None

    def add_player(self, player):
        self.players.append(player)

    def get_num_teams(self):
        teams = set([ii.team for ii in self.players])
        return len(teams)

    def is_member(self, player):
        return player.id in [ii.id for ii in self.players]

    def spent(self):
        return sum(map(lambda x: getattr(x, 'salary'), self.players))

    def projected(self):
        return sum(map(lambda x: getattr(x, 'proj_points'), self.players))

    def position_order(self, player):
        return self.POSITION_ORDER[player.position]

    def sorted_players(self):
        return sorted(self.players, key=self.position_order)

    def get_players(self):
        if self.ds == 'DraftKings': 
            return self.sorted_players()
        else:
            pos = ['P', 'C', '2B', '3B', 'SS', 'OF', 'OF', 'OF']
            players = list(self.players)
            players_ = []

            for ii in pos:
                for jj in players:
                    if jj.position in ii:
                        players_.append(jj)
                        players.remove(jj)
                        break
            return players_ + players

    def __repr__(self):
        s = '\n'.join(str(x) for x in self.sorted_players())
        s += "\n\nProjected Score: %s" % self.projected()
        s += "\tCost: $%s" % self.spent()
        return s


POSITION_LIMITS = {
    'FanDuel': [
        ["P", 1, 1],
        ["C", 1, 2],
        ["2B", 1, 2],
        ["3B", 1, 2],
        ["SS", 1, 2],
        ["OF", 3, 4]
    ],
    'DraftKings': [
        ["P", 2, 2],
        ["C", 1, 1],
        ["1B", 1, 1],
        ["2B", 1, 1],
        ["3B", 1, 1],
        ["SS", 1, 1],
        ["OF", 3, 3]
    ]
}

ROSTER_SIZE = {
    'FanDuel': 9,
    'DraftKings': 10,
}

TEAM_LIMIT = {
    'FanDuel': 2,
    'DraftKings': 2
}

def get_lineup(ds, players, locked, ban, max_point, con_mul, min_salary, max_salary, _team_stack):
    solver = pywraplp.Solver('mlb-lineup', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

    variables = []

    for i, player in enumerate(players):
        if player.id in locked and ds != 'DraftKings':
            variables.append(solver.IntVar(1, 1, str(player)+str(i)))
        elif player.id in ban:
            variables.append(solver.IntVar(0, 0, str(player)+str(i)))
        else:
            variables.append(solver.IntVar(0, 1, str(player)+str(i)))

    objective = solver.Objective()
    objective.SetMaximization()

    for i, player in enumerate(players):
        objective.SetCoefficient(variables[i], player.proj_points)

    salary_cap = solver.Constraint(min_salary, max_salary)
    for i, player in enumerate(players):
        salary_cap.SetCoefficient(variables[i], player.salary)

    point_cap = solver.Constraint(0, max_point)
    for i, player in enumerate(players):
        point_cap.SetCoefficient(variables[i], player.proj_points)

    position_limits = POSITION_LIMITS[ds]
    for position, min_limit, max_limit in position_limits:
        position_cap = solver.Constraint(min_limit, max_limit)

        for i, player in enumerate(players):
            if player.position in position:
                position_cap.SetCoefficient(variables[i], 1)

    # no more than n players from one team (team stack - only for hitters)
    teams = _team_stack.keys()
    for team in teams:
        team_cap = solver.Constraint(_team_stack[team]['min'], _team_stack[team]['max'])
        for i, player in enumerate(players):
            if team == player.team and player.position != 'P':
                team_cap.SetCoefficient(variables[i], 1)

    if ds == 'DraftKings':    # multi positional constraints
        for ii in con_mul:
            if players[ii[0]].id in locked:
                mul_pos_cap = solver.Constraint(1, 1)
            else:
                mul_pos_cap = solver.Constraint(0, 1)

            for jj in ii:
                mul_pos_cap.SetCoefficient(variables[jj], 1)

    size_cap = solver.Constraint(ROSTER_SIZE[ds], ROSTER_SIZE[ds])
    for variable in variables:
        size_cap.SetCoefficient(variable, 1)

    solution = solver.Solve()

    if solution == solver.OPTIMAL:
        roster = Roster(ds)

        for i, player in enumerate(players):
            if variables[i].solution_value() == 1:
                roster.add_player(player)

        return roster


def get_num_lineups(player, lineups):
    num = 0
    for ii in lineups:
        if ii.is_member(player):
            num = num + 1
    return num

def get_exposure(players, lineups):
    return { ii.id: get_num_lineups(ii, lineups) for ii in players }

def get_percent_team(lineups, team):
    num = 0
    for lineup in lineups:
        for ii in lineup.players:
            if ii.team == team:
                num += 1
                break
    return num

def check_batter_vs_pitcher(roster):
    opp_pitcher_ids = [ii.opp_pitcher_id for ii in roster.players if ii.opp_pitcher_id]
    for ii in roster.players:
        if ii.position == 'P' and ii.uid in opp_pitcher_ids:
            return False
    return True

def calc_lineups(players, num_lineups, locked, ds, min_salary, max_salary, _team_stack, exposure, cus_proj, no_batter_vs_pitcher):
    result = []
    max_point = 10000
    exposure_d = { ii['id']: ii for ii in exposure }

    con_mul = []
    players_ = []
    idx = 0
    for ii in players:
        p = vars(ii)
        p.pop('_state')
        p['proj_points'] = float(cus_proj.get(str(ii.id), ii.proj_points))
        ci_ = []

        for jj in ii.actual_position.split('/'):
            ci_.append(idx)
            p['position'] = 'P' if 'P' in jj else jj
            players_.append(Player(**p))
            idx += 1
        con_mul.append(ci_)
    players = players_

    ban = []
    _ban = []   # temp ban
    # for min exposure
    for ii in exposure:
        if ii['min']:
            _locked = [ii['id']]
            while True:
                # check and update all users' status
                cur_exps = get_exposure(players, result)
                for pid, exp in cur_exps.items():
                    if exp >= exposure_d[pid]['max'] and pid not in ban:
                        ban.append(pid)
                    elif exp >= exposure_d[pid]['min'] > 0 and pid not in _ban:
                        _ban.append(pid)

                if cur_exps[ii['id']] >= ii['min']:
                    break
                    
                for team in _team_stack:
                    percent_team = get_percent_team(result, team) 
                    if percent_team >= _team_stack[team]['percent']:
                        _team_stack[team]['percent'] = num_lineups
                        _team_stack[team]['max'] = max(_team_stack[team]['min'] -1, 0)
                        _team_stack[team]['min'] = 0

                roster = get_lineup(ds, players, locked+_locked, ban+_ban, max_point, con_mul, min_salary, 
                                    max_salary, _team_stack)

                if not roster:
                    return result

                max_point = float(roster.projected()) - 0.001
                if roster.get_num_teams() >= TEAM_LIMIT[ds]:
                    if not no_batter_vs_pitcher or check_batter_vs_pitcher(roster):
                        result.append(roster)
                        if len(result) == num_lineups:
                            return result

    # for max exposure -> focus on getting optimized lineups
    while True:
        cur_exps = get_exposure(players, result)
        for pid, exp in cur_exps.items():
            if exp >= exposure_d[pid]['max'] and pid not in ban:
                ban.append(pid)

        # pdb.set_trace()
        for team in _team_stack:
            percent_team = get_percent_team(result, team) 
            if percent_team >= _team_stack[team]['percent']:
                _team_stack[team]['percent'] = num_lineups
                _team_stack[team]['max'] = max(_team_stack[team]['min'] -1, 0)
                _team_stack[team]['min'] = 0

        roster = get_lineup(ds, players, locked, ban, max_point, con_mul, min_salary, max_salary, _team_stack)

        if not roster:
            return result

        max_point = float(roster.projected()) - 0.001
        if roster.get_num_teams() >= TEAM_LIMIT[ds]:
            if not no_batter_vs_pitcher or check_batter_vs_pitcher(roster):
                result.append(roster)
                if len(result) == num_lineups:
                    return result
