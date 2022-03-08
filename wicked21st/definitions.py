# -*- coding: utf-8 -*-
# Copyright (C) 2021 Textualization Software Ltd.
# Distributed under the terms of the Apache Software License 2.0
# http://www.apache.org/licenses/LICENSE-2.0

import random
import copy

import numpy as np

from .state import GraphState
from .classes import Classes
from .graph import Graph, Cascades
from .techtree import TechTree
from .project import Projects


class GameInit:
    def __init__(self, graph_init: GraphState):
        self.graph = graph_init

    def to_json(self):
        return {"graph": self.graph.to_json()}


class GameDef:
    def __init__(
        self,
        game_init: GameInit,
        num_players: int,
        crisis_check: int,
        crisis_rising: int,
        classes_def: Classes,
        graph_def: Graph,
        cascade_def: Cascades,
        techtree_def: TechTree,
        project_def: Projects,
    ):
        self.game_init = game_init
        self.num_players = num_players
        self.crisis_check = crisis_check
        self.crisis_rising = crisis_rising
        self.classes = classes_def
        self.graph = graph_def
        self.cascades = cascade_def
        self.projects = project_def
        self.tech = techtree_def
        self.tojson_memo = None

    def to_json(self):
        if self.tojson_memo is None:
            self.tojson_memo = {
                "num_players": self.num_players,
                "crisis_check": self.crisis_check,
                "crisis_rising": self.crisis_rising,
                "game_init": self.game_init.to_json(),
                "classes": self.classes_def.to_json(),
                "graph": self.graph.to_json(),
                "tech": self.tech.to_json(),
                "projects": self.projects.to_json(),
            }
        return self.tojson_memo
