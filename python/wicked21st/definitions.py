# -*- coding: utf-8 -*-
# Copyright (C) 2021 Textualization Software Ltd.
# Distributed under the terms of the Apache Software License 2.0
# http://www.apache.org/licenses/LICENSE-2.0

import random
import copy

import numpy as np

from .state import GraphState

class GameInit:
    def __init__(self, graph_init: GraphState):
        self.graph = graph_init

    def to_json(self):
        return { 'graph' : self.graph.to_json() }

class GameDef:
    def __init__(self, game_init: GameInit,
                 num_players: Int,
                 classes_def: Classes,
                 graph_def: Graph,
                 board_def: Board,
                 techtree_def: TechTree):
        self.game_init = game_init
        self.num_players = num_players
        self.classes = classes_def
        self.graph = graph_def
        self.board = board_def
        self.tree = techtree_def
        
    def to_json(self):
        return { 'num_players' : self.num_players,
                 'game_init' : self.game_init.to_json(),
                 'classes' : self.classes_def.to_json(),
                 'graph' : self.graph.to_json(),
                 'tree' : self.tree.to_json(),
                 'board': self.board.to_json() }

