# -*- coding: utf-8 -*-
# Copyright (C) 2021 Textualization Software Ltd.
# Distributed under the terms of the Apache Software License 2.0
# http://www.apache.org/licenses/LICENSE-2.0

import random


class Player:

    # decisions
    INIT_LOC = 0
    NEW_LOC = 1
    PILE_DRAW = 2

    decision_names = [ 'Initial Location',
                       'New Location',
                       'Pile Draw' ]
    
    def __init__(self, name: string, ordering: Int, pclass: BaseClass):
        self.name = name
        self.ordering = ordering
        self.player_class = pclass

    def to_json(self):
        return { 'name' : self.name,
                 'ordering' : self.ordering,
                 'player_class' : self.player_class.to_json() }

    def pick(self, decision: int, decisions: list, rand: random.Random, state: PlayerState=None, game: GameState=None):
        """Choose a decision among many"""
        return rand.choice(decisions)

class PlayerState:
    def __init__(self, player: Player, resources: dict, cards: list, location: string, crisis_chips: int):
        self.player = player
        self.resources = resources
        self.cards = cards
        self.location = location
        self.crisis_chips = crisis_chips
        self.projects = list()
        self.policies = list()
        self.technologies = list()

    def to_json(self):
        return { 'player' : self.player.to_json(),
                 'resources' : self.resources,
                 'cards' : self.cards,
                 'location' : self.location,
                 'crisis_chips' : self.crisis_chips
                }
    
