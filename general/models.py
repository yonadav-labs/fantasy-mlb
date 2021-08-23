# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from general.constants import DATA_SOURCE


class Slate(models.Model):
    data_source = models.CharField(max_length=30, choices=DATA_SOURCE)
    name = models.CharField(max_length=120)

    def __str__(self):
        return f'{self.name} - [{self.data_source}]'


class Game(models.Model):
    slate = models.ForeignKey(Slate, on_delete=models.CASCADE, related_name="games")
    home_team = models.CharField(max_length=20)
    visit_team = models.CharField(max_length=20)
    time = models.TimeField(null=True, blank=True)
    home_score = models.CharField(max_length=50, null=True, blank=True)
    visit_score = models.CharField(max_length=50, null=True, blank=True)
    ou = models.FloatField(null=True, blank=True)
    ml = models.CharField(max_length=20, null=True, blank=True)
    display = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.visit_team}@{self.home_team}'


class Player(models.Model):
    slate = models.ForeignKey(Slate, on_delete=models.CASCADE, related_name="players")
    rid = models.CharField(max_length=100)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    avatar = models.CharField(max_length=250, default="/static/img/nba.ico")
    injury = models.CharField(max_length=250, blank=True, null=True)
    opponent = models.CharField(max_length=50, blank=True, null=True)
    position = models.CharField(max_length=50)
    actual_position = models.CharField(max_length=50)
    proj_points = models.FloatField()
    proj_delta = models.FloatField(default=0)
    salary = models.FloatField()
    team = models.CharField(max_length=50)
    play_today = models.BooleanField(default=False)
    opp_pitcher_id = models.PositiveIntegerField(blank=True, null=True)
    handedness = models.CharField(max_length=5, blank=True, null=True)
    start = models.CharField(max_length=5, blank=True, null=True)
    start_status = models.CharField(max_length=5, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)


class BaseGame(models.Model):
    data_source = models.CharField(max_length=30, choices=DATA_SOURCE, default='FanDuel')
    time = models.TimeField()
    home_team = models.CharField(max_length=20)
    visit_team = models.CharField(max_length=20)
    home_score = models.CharField(max_length=50, null=True, blank=True)
    visit_score = models.CharField(max_length=50, null=True, blank=True)
    ou = models.FloatField()
    ml = models.CharField(max_length=20)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.home_team, self.visit_team)


class BasePlayer(models.Model):
    data_source = models.CharField(max_length=30, choices=DATA_SOURCE, default='FanDuel')
    uid = models.IntegerField()  # roto id
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    avatar = models.CharField(max_length=250, default="/static/img/nba.ico")
    team = models.CharField(max_length=50)
    injury = models.CharField(max_length=250, blank=True, null=True)  # from FD
    handedness = models.CharField(max_length=5, blank=True, null=True)
    start = models.CharField('Order', max_length=5, blank=True, null=True)
    start_status = models.CharField('Confirm', max_length=5, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)


# @receiver(post_save, sender=Player, dispatch_uid="sync_fanduel_proj")
# def sync_proj(sender, instance, **kwargs):
#     if instance.data_source == 'FanDuel':
#         Player.objects.filter(uid=instance.uid, data_source='Yahoo').update(proj_points=instance.proj_points)


class FavPlayer(models.Model):
    player = models.ForeignKey(Player)

    def __str__(self):
        return '{} {}'.format(self.player.first_name, self.player.last_name)
