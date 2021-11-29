# -*- coding: utf-8 -*-
# Copyright (C) 2021 Textualization Software Ltd.
# Distributed under the terms of the Apache Software License 2.0
# http://www.apache.org/licenses/LICENSE-2.0

import random

import graphviz

from .tojson   import to_json
from .project  import Project
from .techtree import Tech
from .graph    import Graph


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

    def is_saturated(self, node_name, visited=None):
        if visited is None:
            visited = list()
        elif node_name in visited:
            return True
            #raise Exception("Graph has a cycle! {} - {}".format(node_name, list(map(lambda x: self[x], visited))))
        if self[node_name]['status'] != GraphState.IN_CRISIS:
            return False
        visited.append(node_name)

        node = self[node_name]['id']
        for outlink in self.graph.outlinks[node]:
            outlinkn = self.graph.node_names[outlink]
            if not self.is_saturated(outlinkn, list(visited)):
                return False
            
        return True
        
    def is_one_level_saturated(self, node_name):
        if self[node_name]['status'] != GraphState.IN_CRISIS:
            return False

        node = self[node_name]['id']
        for outlink in self.graph.outlinks[node]:
            outlinkn = self.graph.node_names[outlink]
            if not self[outlinkn]['status'] != GraphState.IN_CRISIS:
                return False
            
        return True
        
    def copy(self):
        copy = GraphState(self.graph)
        for n, obj in self.items():
            st =  obj['status']
            if st != GraphState.STABLE:
                copy[n]['status'] = st
            if obj['auto-protected']:
                copy[n]['auto-protected'] = True
        return copy

    def show(self, size=Graph.GRAPH_PRINT_SIZE):
        digraph = graphviz.Digraph(graph_attr={"size": size, "landscape":"portrait"})

        for _id, name in self.graph.node_names.items():
            shape = "box"
            if self[name]['status'] == GraphState.PROTECTED:
                shape = "box3d"
            elif self[name]['status'] == GraphState.IN_CRISIS:
                shape = "diamond"
            color = "#707070"
            if self[name]['auto-protected']:
                color = '#000000'
            digraph.node(name, shape=shape, color=color, fillcolor=self.graph.class_for_node[_id], style='filled')
        for base, dests in self.graph.outlinks.items():
            basetext = self.graph.node_names[base]
            for dest in dests:
                digraph.edge(basetext, self.graph.node_names[dest])
        return digraph
    

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
            for obj in self.values():
                if obj['status'] == status:
                    result.append(obj['project'])
        return result

    def find_project(self, type_, fix):
        for project in self.projects.projects:
            if project.type_ == type_ and fix == project.fixes:
                return project
            # else, continue
        raise Exception("Not found: find_project({}, {})".format(type_, fix))

    def project_for_name(self, project_name):
        for project in self.projects.projects:
            if project.name == project_name:
                return project
            # else, continue
        raise Exception("Not found: project_for_name({})".format(project_name))
        

    def copy(self):
        copy = ProjectState(self.projects)
        for n, obj in self.items():
            copy[n] = dict(obj)
        return copy
    

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
        for tech in self.tree.technologies:
            if self[tech.name]['status'] == status:
                result.append(tech)
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
        raise Exception("Not found: find_tech({} [{}], {}, {})".format(Tech.TYPES[type_], type_, suit, node))

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
    
    def copy(self):
        copy = TechTreeState(self.tree)
        for n, obj in self.items():
            copy[n] = dict(obj)
        return copy

