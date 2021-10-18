# -*- coding: utf-8 -*-
# Copyright (C) 2021 Textualization Software Ltd.
# Distributed under the terms of the Apache Software License 2.0
# http://www.apache.org/licenses/LICENSE-2.0

import random

from .classes import BaseClass

class Player:

    # decisions
    INIT_ROLE                  =  0
    INIT_LOC                   =  1 #
    NEW_LOC                    =  2
    PILE_DRAW                  =  3
    START_PROJECT              =  4
    START_PROJECT_FIX_CAT      =  5
    START_PROJECT_FIX_NODE     =  6
    START_PROJECT_TRIGGER_NODE =  7
    PLAY_CARD                  =  8
    CONSULTANT                 =  9
    START_RESEARCH             = 10
    CARD_FOR_RESEARCH          = 11
    FUND_RESEARCH              = 12
    

    decision_names = [ 'Initial role',
                       'Initial location',
                       'New location',
                       'Pile to draw from',
                       'Project type to start',
                       'New project, fix category',
                       'New project, fix problem',
                       'New project, trade-off problem',
                       'Play a card',
                       'Add consultant fees',
                       'Teach to start researching',
                       'Card for research',
                       'Fund research',
                      ]
    
    def __init__(self, name: str, ordering: int, pclass=None):
        self.name = name
        self.ordering = ordering
        self.player_class = pclass

    def set_class(self, pclass: BaseClass):
        self.player_class = pclass

    def to_json(self):
        result = { 'name' : self.name,
                   'ordering' : self.ordering }
        if self.player_class:
            result['player_class'] = self.player_class.to_json()
        return result

    def pick(self, decision: int, decisions: list,
             # state: PlayerState
             # game: GameState
             rand: random.Random, state: object=None, game: object=None, context: dict=None):
        """Choose a decision among many"""
        return rand.choice(decisions)

    def roll(self, nemo, rand, num):
        return rand.randint(1, num)

class PlayerState:
    def __init__(self, player: Player, resources: dict, cards: list, location: str):
        self.player    = player
        self.resources = resources
        self.cards     = cards
        self.location  = location
        self.projects  = list()
        self.tech = list()

    def available_project_slots(self):
        return self.player.player_class.project_slots - len(self.projects)
    
    def available_research_slots(self):
        return self.player.player_class.research_slots - len(self.tech)

    def to_json(self):
        return { 'player'       : self.player.to_json(),
                 'resources'    : self.resources,
                 'cards'        : self.cards,
                 'location'     : self.location,
                 'projects'     : self.projects,
                 'technologies' : self.tech,
                }
    
    def copy(self):
        copy = PlayerState(self.player, dict(self.resources), list(self.cards), self.location)
        copy.projects = list(self.projects)
        copy.tech = list(self.tech)
        return copy
