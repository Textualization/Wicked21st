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

    AVAILABLE   = 'available'
    IN_PROGRESS = 'in progress'
    FINISHED    = 'finished'
    
    def __init__(self, projects):
        super.__init__(self, projects.names)
        self.projects = projects

    def status(self, project_name):
        if project_name not in self:
            return ProjectState.AVAILABLE
        return self[project_name]['status']

    def player_starts(self, project, player: int, turn: int):
        self[project_name] = {
            'name':    project.name,
            'project': project,
            'status':  ProjectState.IN_PROGRESS,
            'player':  player,
            'turn':    turn,
            'missing': project.cost
            }
    def abandon(self, project_name):
        del self[project_name]

    def finish(self, project_name):
        self[project_name]['missing'] = []
        self[project_name]['status'] = ProjectState.FINISHED

    def projects_for_status(self, status: str):
        result = ()
        if status == ProjectState.AVAILABLE:
            for project in self.projects.projects:
                if project.name not in self:
                    result.append(project)
        else:
            for obj in self.items():
                if obj['status'] == status:
                    result.append(obj['project'])

    def find_project(self, type_, fix, trigger=None, protect=None):
        for project in self.projects.projects:
            if project.type_ == type_ and fix in project.fixes:
                if trigger is None:
                    if not project.triggers:
                        return project
                    # else, continue
                elif trigger in project.triggers:
                    if protect is None:
                        return project
                    if protect in project.protects:
                        return project
                # else, continue
        raise Exception("Not found: find_project({}, {}, {}, {})".format(type_, fix, trigger, protect))

class TechTreeState(ValidKeysDict):
    def __init__(self, tree):
        super.__init__(self, tree.technologies)

class PolicyState(ValidKeysDict):

    AVAILABLE   = 'available'
    IN_PROGRESS = 'in progress'
    PASSED      = 'passed'
    EXPIRED     = 'expired'
    
    def __init__(self, policies):
        super.__init__(self, policies.names)
        self.policies = policies

    def status(self, policy_name):
        if policy_name not in self:
            return PolicyState.AVAILABLE
        return self[policy_name]['status']

    def player_starts(self, policy, player: int, turn: int, quorum: int):
        self[policy_name] = {
            'name':    policy.name,
            'policy':  policy,
            'status':  PolicyState.IN_PROGRESS,
            'player':  player,
            'turn':    turn,
            'missing_power': policy.cost[0] + quorum,
            'missing_turns': policy.cost[1]
            }
    def abandon(self, policy_name):
        del self[policy_name]

    def finish(self, policy_name):
        self[policy_name]['missing'] = []
        self[policy_name]['status'] = PolicyState.FINISHED

    def policies_for_status(self, status: str):
        result = ()
        if status == PolicyState.AVAILABLE:
            for policy in self.policies.policies:
                if policy.name not in self:
                    result.append(policy)
        else:
            for obj in self.items():
                if obj['status'] == status:
                    result.append(obj['policy'])

    def find_policy(self, type_, fix: set, trigger: set=None, protect: set=None):
        for policy in self.policies.policies:
            if policy.type_ == type_ and fix == policy.fixes:
                if trigger is None:
                    if policy.triggers:
                        continue
                elif trigger == policy.triggers:
                    if protect is None:
                        return policy
                    if protect == policy.protects:
                        return policy
                # else, continue
        raise Exception("Not found: find_policy({}, {}, {}, {})".format(type_, fix, trigger, protect))


class GameState:
    def __init__(self,
                 turn: Int,
                 phase: Int,
                 player: Int,
                 game_def: GameDef,
                 players_state: list,
                 crisis_chips: int,
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
        self.crisis_chips = crisis_chips
        self.graph = graph_state
        self.board = board_state
        self.projects = project_state
        self.technologies = techtree_state
        self.policies = policy_state
        self.drawpiles = drawpiles_state

    def quorum(self):
        return len(self.players_state) // 2 + 1

    def to_json(self):
        return { 'game': self.game.to_json(),
                 'players' : to_json(self.players),
                 'crisis_chips' : crisis_chips,
                 'board' : self.board.to_json(),
                 'graph' : self.graph.to_json(),
                 'tech' : self.techtree.to_json(),
                 'policy' : self.policy.to_json(),
                 'piles' : self.drawpiles.to_json() }

