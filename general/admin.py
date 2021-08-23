# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from general.models import Slate, Game, Player, BaseGame, BasePlayer


@admin.register(Slate)
class SlateAdmin(admin.ModelAdmin):
    list_display = ('name', 'data_source')
    list_filter = ('data_source',)


@admin.register(BaseGame)
class BaseGameAdmin(admin.ModelAdmin):
    list_display = ['home_team', 'visit_team', 'ou', 'ml', 'time', 'data_source', 'updated_at']
    search_fields = ['home_team', 'visit_team']
    list_filter = ['data_source']


@admin.register(BasePlayer)
class BasePlayerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'team', 'uid', 'handedness', 'start', 'start_status', 'injury', 'data_source', 'updated_at']
    search_fields = ['first_name', 'last_name']
    list_filter = ['team', 'data_source']


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'rid', 'position', 'actual_position', 'team', 'opponent', 'salary',
                    'play_today', 'proj_points', 'proj_delta', 'updated_at']
    search_fields = ['first_name', 'last_name', 'team']
    list_filter = ['slate__data_source', 'team', 'position', 'play_today', 'slate__name']


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['slate', 'home_team', 'visit_team', 'ou', 'ml', 'time', 'updated_at']
    search_fields = ['home_team', 'visit_team']
    list_filter = ['slate__name', 'slate__data_source']
