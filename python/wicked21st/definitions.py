# -*- coding: utf-8 -*-
# Copyright (C) 2021 Textualization Software Ltd.
# Distributed under the terms of the Apache Software License 2.0
# http://www.apache.org/licenses/LICENSE-2.0

import random
import copy

import numpy as np

from .state import GraphState
from .classes import Classes
from .graph import Graph
from .board import Board
from .techtree import TechTree
from .policy import Policies
from .project import Projects

class GameInit:
    def __init__(self, graph_init: GraphState):
        self.graph = graph_init

    def to_json(self):
        return { 'graph' : self.graph.to_json() }

class GameDef:
    def __init__(self, game_init: GameInit,
                 num_players: int,
                 classes_def: Classes,
                 graph_def: Graph,
                 board_def: Board,
                 techtree_def: TechTree,
                 policy_def: Policies,
                 project_def: Projects):
        self.game_init = game_init
        self.num_players = num_players
        self.classes = classes_def
        self.graph = graph_def
        self.board = board_def
        self.projects = project_def
        self.policies = policy_def
        self.tech = techtree_def
        
    def to_json(self):
        return { 'num_players' : self.num_players,
                 'game_init' : self.game_init.to_json(),
                 'classes' : self.classes_def.to_json(),
                 'graph' : self.graph.to_json(),
                 'tech' : self.tech.to_json(),
                 'projects' : self.projects.to_json(),
                 'policies' : self.policies.to_json(),
                 'board': self.board.to_json() }

