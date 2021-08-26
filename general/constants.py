DATA_SOURCE = (
    ('DraftKings', 'DraftKings'),
    ('FanDuel', 'FanDuel'),
    ('Yahoo', 'Yahoo'),
)


CSV_FIELDS = {
    'FanDuel': ['P', 'C1B', '2B', '3B', 'SS', 'OF', 'OF', 'OF', 'UTIL'],
    'DraftKings': ['P', 'P', 'C', '1B', '2B', '3B', 'SS', 'OF', 'OF', 'OF'],
}


SALARY_CAP = {
    'FanDuel': 35000,
    'DraftKings': 50000,
}


TEAM_MEMEBER_LIMIT = {
    'FanDuel': 4,
    'DraftKings': 5
}


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