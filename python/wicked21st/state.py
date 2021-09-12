# -*- coding: utf-8 -*-
# Copyright (C) 2021 Textualization Software Ltd.
# Distributed under the terms of the Apache Software License 2.0
# http://www.apache.org/licenses/LICENSE-2.0

import random
import copy

class ValidKeysDict(dict):
    def __init__(self, keys):
        super.__init__(self)
        self.valid_keys = set(keys)
    def __getitem__(self, key):
        assert key in self.valid_keys
        return super.__getitem__(key)
    def __setitem__(self, key, value):
        assert key in self.valid_keys
        return super.__setitem__(key, value)
    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            self[k] = v
    def get(self, key, value=None):
        assert key in self.valid_keys
        return super.get(key, value)

    def to_json(self):
        return to_json(self)

class GraphState(ValidKeysDict):
    def __init__(self, graph):
        super.__init__(self, graph.nodes())
        self.graph = graph

    def in_crisis(self, category=None):
        result = set()
        for k, v in self.items():
            if v:
                if categoy is None or k in self.graph.class_for_node[self.graph.name_to_id[k]] == self.graph.category_for_name[category]:
                    result.add(k)
        return k

class BoardState(ValidKeysDict):
    def __init__(self, board):
        super.__init__(self, board.locations)

# keys: object 'state' : 
class ProjectState(ValidKeysDict):

    AVAILABLE = 'available'
    IN_PROGRESS = 'in progress'
    FINISHED = 'finished'
    
    def __init__(self, projects):
        super.__init__(self, projects.names)
        self.projects = projects

    def status(self, project_name):
        if project_name not in self:
            return ProjectState.AVAILABLE
        return self[project_name]['status']

    def player_starts(self, project_name, player: int, turn: int):
        self[project_name] = {
            'name':    project_name,
            'project': self.projects[project_name],
            'status':  ProjectState.IN_PROGRESS,
            'player':  player,
            'turn':    turn
            }
    def abandoned(self, project_name):
        del self[project_name]

    def finished(self, project_name):
        self[project_name]['status'] = ProjectState.FINISHED

class TechTreeState(ValidKeysDict):
    def __init__(self, tree):
        super.__init__(self, tree.technologies)

class PolicyState(ValidKeysDict):
    def __init__(self, policies):
        super.__init__(self, policies.names)

class GameState:
    def __init__(self,
                 turn: Int,
                 phase: Int,
                 player: Int,
                 game_def: GameDef,
                 players_state: list,
                 graph_state: GraphState,
                 board_state: BoardState,
                 techtree_state: TechtreeState,
                 policy_state: PolicyState,
                 drawpiles_state: DrawPiles):
        self.turn = turn
        self.phase = phase
        self.player = player
        self.game = game_def
        self.players = players_state
        self.graph = graph_state
        self.board = board_state
        self.projects = project_state
        self.technologies = techtree_state
        self.policies = policy_state
        self.drawpiles = drawpiles_state

    def to_json(self):
        return { 'game': self.game.to_json(),
                 'players' : to_json(self.players),
                 'board' : self.board.to_json(),
                 'graph' : self.graph.to_json(),
                 'tech' : self.techtree.to_json(),
                 'policy' : self.policy.to_json(),
                 'piles' : self.drawpiles.to_json() }

