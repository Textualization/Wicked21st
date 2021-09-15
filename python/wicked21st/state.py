# -*- coding: utf-8 -*-
# Copyright (C) 2021 Textualization Software Ltd.
# Distributed under the terms of the Apache Software License 2.0
# http://www.apache.org/licenses/LICENSE-2.0

import random
import copy

from .tojson import to_json


class ValidKeysDict(dict):
    def __init__(self, keys):
        super().__init__()
        self.valid_keys = set(keys)
    def __getitem__(self, key):
        assert key in self.valid_keys
        return super().__getitem__(key)
    def __setitem__(self, key, value):
        assert key in self.valid_keys
        return super().__setitem__(key, value)
    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            self[k] = v
    def get(self, key, value=None):
        assert key in self.valid_keys
        return super().get(key, value)

    def to_json(self):
        return { k: to_json(v) for k,v in self.items() }

class GraphState(ValidKeysDict):

    STABLE = 0
    IN_CRISIS = 1
    PROTECTED = 2
    
    def __init__(self, graph):
        super().__init__(graph.nodes())
        self.graph = graph
        for n in graph.nodes():
            id_ = graph.name_to_id[n]
            self[n] = { 'node': n,
                        'id': id_,
                        'status': GraphState.STABLE,
                        'category': graph.class_for_node[id_],
                        'auto-protected': False
                       }

    def in_crisis(self, node_name):
        self[node_name]['status'] = GraphState.IN_CRISIS

    def are_in_crisis(self, category=None):
        result = set()
        for k, v in self.items():
            if v['status']:
                if category is None or v['category'] == self.graph.category_for_name[category]:
                    result.add(k)
        return result

    def is_staturated(self, node_name):
        if self[node_name]['status'] != GraphState.IN_CRISIS:
            return False

        node = self[node_name]['id']
        for outlink in self.graph.outlinks[node]:
            outlinkn = self.game_def.graph.node_names[outlink]
            if not self.is_saturated(outlinkn):
                return False
            
        return True
        
    

class BoardState(ValidKeysDict):
    def __init__(self, board):
        super().__init__(board.locations)
        

# keys: object 'state' : 
class ProjectState(ValidKeysDict):

    AVAILABLE   = 'available'
    IN_PROGRESS = 'in progress'
    FINISHED    = 'finished'
    
    def __init__(self, projects):
        super().__init__(projects.names)
        self.projects = projects

    def status(self, project_name):
        if project_name not in self:
            return ProjectState.AVAILABLE
        return self[project_name]['status']

    def player_starts(self, project, player: int, turn: int):
        self[project.name] = {
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
        result = list()
        if status == ProjectState.AVAILABLE:
            for project in self.projects.projects:
                if project.name not in self:
                    result.append(project)
        else:
            for obj in self.items():
                if obj['status'] == status:
                    result.append(obj['project'])
        return result

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
    
    AVAILABLE   = 'available'
    IN_PROGRESS = 'in progress'
    RESEARCHED  = 'researched'
    
    def __init__(self, tree):
        super().__init__(tree.names)
        self.tree = tree
        for tech in tree.technologies:
            self[tech.name] = {
                'name':    tech.name,
                'tech':    tech,
                'status':  TechTreeState.AVAILABLE,
            }
            
    def status(self, tech_name):
        return self[tech_name]['status']

    def player_starts(self, tech, player: int, turn: int):
        self[tech.name] = {
            'name':    tech.name,
            'tech':    tech,
            'status':  TechTreeState.IN_PROGRESS,
            'player':  player,
            'turn':    turn,
            'suit':    tech.suit,
            'missing_turns': tech.turns,
            }
        
    def finish(self, tech_name):
        self[tech_name]['missing_turns'] = 0
        self[tech_name]['status'] = TechTreeState.RESEARCHED

    def techs_for_status(self, status: str):
        result = list()
        for obj in self.values():
            if obj['status'] == status:
                result.append(obj['tech'])
        return result

    def find_tech(self, type_, suit: str, node: str=None):
        for tech in self.tree.technologies:
            if tech.type_ == type_ and tech.suit == suit:
                if node is None:
                    if tech.node is None:
                        return tech
                # else, continue
                elif tech.node is not None:
                    if node == tech.node:
                        return tech
                # else, continue
            # else, continue
        raise Exception("Not found: find_policy({}, {}, {}, {})".format(type_, fix, trigger, protect))

    def research_boundary(self):
        result = list()
        researched = set(map(lambda t:t.name, self.techs_for_status(TechTreeState.RESEARCHED)))
        for tech in self.techs_for_status(TechTreeState.AVAILABLE):
            if tech.parents is None:
                result.append(tech)
            else:
                if tech.parents.intersection(researched) == tech.parents:
                    result.append(tech)
        return result

class PolicyState(ValidKeysDict):

    AVAILABLE   = 'available'
    IN_PROGRESS = 'in progress'
    PASSED      = 'passed'
    EXPIRED     = 'expired'
    
    def __init__(self, policies):
        super().__init__(policies.names)
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
        self[policy_name]['missing_turns'] = 0
        self[policy_name]['status'] = PolicyState.FINISHED

    def has_passed(self, policy_name):
        self[policy_name]['missing_power'] = 0
        self[policy_name]['status'] = PolicyState.PASSED

    def policies_for_status(self, status: str):
        result = list()
        if status == PolicyState.AVAILABLE:
            for policy in self.policies.policies:
                if policy.name not in self:
                    result.append(policy)
        else:
            for obj in self.items():
                if obj['status'] == status:
                    result.append(obj['policy'])
        return result

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

