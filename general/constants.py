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
