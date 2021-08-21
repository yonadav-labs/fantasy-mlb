import random

def parse_name(name):
    # get first and last name from name string after processing
    name = name.strip().replace('.', '')
    name_ = name.split(' ')
    if len(name_) > 1:
        return name_[0], ' '.join(name_[1:])
    return name, ''


def get_delta(ii, ds):
    return 0

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
