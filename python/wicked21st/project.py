# -*- coding: utf-8 -*-
# Copyright (C) 2021 Textualization Software Ltd.
# Distributed under the terms of the Apache Software License 2.0
# http://www.apache.org/licenses/LICENSE-2.0

from .graph import Graph


###
### Project details:
###
### There are two types of projects: base projects, that have a trade-off and improved projects that do not have the trade-off (but need more resources).
###
### For base projects, use the following table:


class Project:

    BASE  = 0
    A     = 1

    TYPES = [ 'Base', 'Remove-Tradeoff' ]

    def __init__(self, name, type_, fixes: str, triggers: int, cost: list, parent):
        self.name = name
        self.type_ = type_
        self.fixes = fixes
        self.triggers = triggers
        self.cost = cost
        self.parent = parent

    def to_json(self):
        result = { 'name':     self.name,
                   'type':     Project.TYPES[ self.type_ ],
                   'fixes':    self.fixes,
                   'triggers': self.triggers,
                   'cost':     self.cost
                  }
        if self.parent is not None:
            result['parent'] = self.parent.name
        return result
   
class Projects:

### | fixed problem     | suits needed |
### | ENVIRONMENTAL     | C, D |
### | LIVING_STANDARDS  | H, C |
### | SOCIAL            | H, D |
### | CLASS             | H, S |
### | ECONOMIC          | S, D |
### | INDUSTRIAL        | S, C |
###
### Improved projects double its base requirements.
###
### Base projects add a crisis chip when completed.

    BASE_TABLE =  [ 
        ( Graph.ENVIRONMENTAL,	   'C', 'D' ),
        ( Graph.LIVING_STANDARDS,  'H', 'C' ),
        ( Graph.SOCIAL,	           'H', 'D' ),
        ( Graph.CLASS,	           'H', 'S' ),
        ( Graph.ECONOMIC,	   'S', 'D' ),
        ( Graph.INDUSTRIAL,	   'S', 'C' ),
    ]

    def __init__(self, graph: Graph):

        self.projects = list()
        for c1, s1, s2 in Projects.BASE_TABLE:
            
            for n1 in sorted(graph.node_classes[c1[1]], key=lambda x:graph.node_names[x]):
                nn1 = graph.node_names[n1]
                cost = [s1,s2]
                # base
                base = Project("Base fix '{}' ({}) triggers crisis".format(nn1, c1[0]), Project.BASE,
                               n1, 1, cost, None)
                self.projects.append(base)
                    
                # improv-A, no trade-off
                improvA = Project("Improved fix '{}' ({})".format(nn1, c1[0]),
                                      Project.A, n1, 0, cost + cost, base)
                self.projects.append(improvA)
        
        self.project_for_name = { project.name: project for project in self.projects }
        self.names = sorted(list(self.project_for_name.keys()))
        
    def to_json(self):
        return self.projects
        
