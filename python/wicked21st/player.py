# -*- coding: utf-8 -*-
# Copyright (C) 2021 Textualization Software Ltd.
# Distributed under the terms of the Apache Software License 2.0
# http://www.apache.org/licenses/LICENSE-2.0

import random

from .classes import BaseClass

class Player:

    # decisions
    INIT_LOC  = 0
    NEW_LOC   = 1
    PILE_DRAW = 2
    START_PROJECT_YN           = 3
    START_PROJECT_FIX_CAT      = 4
    START_PROJECT_FIX_NODE     = 5
    START_PROJECT_TYPE         = 6
    START_PROJECT_TRIGGER_NODE = 7
    START_PROJECT_PROTECT_NODE = 8
    PLAY_CARD       = 9
    CONSULTANT      = 10
    START_POLICY_YN           = 11
    START_POLICY_FIX_CAT      = 12
    START_POLICY_FIX_NODE     = 13
    START_POLICY_TYPE         = 14
    START_POLICY_TRIGGER_NODE = 15
    START_POLICY_PROTECT_NODE = 16
    POLICY_TO_EMPOWER = 17
    POWER_AMOUNT      = 18
    START_RESEARCH_YN   = 19
    START_RESEARCH_TECH = 20
    CARD_FOR_RESEARCH   = 21
    FUND_RESEARCH       = 22
    EMPATHIZE = 23
    

    decision_names = [ 'Initial location',
                       'New location',
                       'Pile draw',
                       'Start a new project?',
                      ]
    
    def __init__(self, name: str, ordering: int, pclass: BaseClass):
        self.name = name
        self.ordering = ordering
        self.player_class = pclass

    def to_json(self):
        return { 'name' : self.name,
                 'ordering' : self.ordering,
                 'player_class' : self.player_class.to_json() }

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
        self.policies  = list()
        self.tech = list()

    def available_project_slots(self):
        return self.player.player_class.project_slots - len(self.projects)
    
    def available_policy_slots(self):
        return self.player.player_class.policy_slots - len(self.policies)

    def available_research_slots(self):
        return self.player.player_class.research_slots - len(self.tech)

    def to_json(self):
        return { 'player'       : self.player.to_json(),
                 'resources'    : self.resources,
                 'cards'        : self.cards,
                 'location'     : self.location,
                 'projects'     : self.projects,
                 'policies'     : self.policies,
                 'technologies' : self.tech,
                }
    
