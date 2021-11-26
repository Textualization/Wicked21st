# -*- coding: utf-8 -*-
# Copyright (C) 2021 Textualization Software Ltd.
# Distributed under the terms of the Apache Software License 2.0
# http://www.apache.org/licenses/LICENSE-2.0

import random

from .player import Player

class GreedyPlayer(Player):

    def __init__(self, name: str, ordering: int):
        super().__init__(name, ordering)
        self.rnd = random.Random(ordering * 7)

    def pick(self, decision: int, decisions: list,
             # state: PlayerState
             # game: GameState
             rand: random.Random, state: object=None, game: object=None, context: dict=None):
        """Choose a decision among many"""

        if state is None:
            print("ai player pick: Missing state")
            return rand.choice(decisions)
        if state.extra is None:
            state.extra = GreedyPlayerState(self.rnd, state, game)

        # now get to work
        if decision == Player.INIT_ROLE:
            # pick role that cover most of the top categories
            pass
        
        if decision == Player.PILE_DRAW:
            # if I have projects, make sure I draw cards I can use for them
            # if I have research, make sure I draw cards I can use for it
            # if I don't have them, decide what I'll do, then draw cards accordingly
            pass
        elif decision == Player.START_PROJECT:
            # if I don't have a project, start one using the orderings
            # decide type of project randomly 50%
            pass
        elif decision == Player.START_PROJECT_FIX_CAT:
            # follow with the picked node
            pass
        elif decision == Player.START_PROJECT_FIX_NODE:
            # follow with the picked node
            pass
        elif decision == Player.PLAY_CARD:
            # send high cards to projects, low cards to tech
            pass
        elif decision == Player.CONSULTANT:
            # pay consultant enough depending on whether 1 card or 2 cards
            pass
        elif decision == Player.START_RESEARCH:
            # always start research, going for top node in crisis category, then node for protection
            # (accounting for existing tech and other players ongoing tech)
            pass
        elif decision == Player.CARD_FOR_RESEARCH:
            # play a card for research, always
            pass
        elif decision == Player.FUND_RESEARCH:
            # fund research, always
            pass

    def analyze(self, state, game):
        pass
        

            
class GreedyPlayerState:

    def __init__(self, rnd, state, game):
        if rnd is not None:
            self.order = self.rnd.shuffle(list(game.graph.node_names))
            self.importance = { name: idx for idx, name in enumerate(self.order) }

    def to_json(self):
        return { 'order' : self.order }

    def copy(self):
        other = GreedyPlayerState(None,None,None)
        other.order = list(self.order)
        other.importance = dict(self.importance)
        return other

    


