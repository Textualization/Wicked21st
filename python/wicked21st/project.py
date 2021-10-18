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

    def __init__(self, name, type_, fixes: set, triggers: set, protects: set, cost: list, parent):
        self.name = name
        self.type_ = type_
        self.fixes = fixes
        self.triggers = triggers
        self.protects = protects
        self.cost = cost
        self.parent = parent

    def to_json(self):
        result = { 'name':     self.name,
                   'type':     Project.TYPES[ self.type_ ],
                   'fixes':    list(self.fixes),
                   'triggers': list(self.triggers),
                   'protects': list(self.protects),
                   'cost':     self.cost
                  }
        if self.parent is not None:
            result['parent'] = self.parent.name
   
class Projects:

### | fixed problem    | trade-off         | suits needed |
### | ENVIRONMENTAL    | LIVING_STANDARDS  | C, D |
### | LIVING_STANDARDS | CLASS             | H, C |
### | SOCIAL           | INDUSTRIAL        | H, D |
### | CLASS            | SOCIAL            | H, S |
### | ECONOMIC         | ENVIRONMENTAL     | S, D |
### | INDUSTRIAL       | ECONOMIC          | S, C |
###
### Improved projects double its base requirements.
###
### Note that the problems (fix and, if needed, tradeoff) are decided when the project is created. Over time that problem might no longer be relevant and thus the project might be abandoned.

    BASE_TABLE =  [ 
        ( Graph.ENVIRONMENTAL,          Graph.LIVING_STANDARDS,	'C', 'D' ),
        ( Graph.LIVING_STANDARDS,	Graph.CLASS,	        'H', 'C' ),
        ( Graph.SOCIAL,	                Graph.INDUSTRIAL,	'H', 'D' ),
        ( Graph.CLASS,	                Graph.SOCIAL,	        'H', 'S' ),
        ( Graph.ECONOMIC,	        Graph.ENVIRONMENTAL,	'S', 'D' ),
        ( Graph.INDUSTRIAL,	        Graph.ECONOMIC,	        'S', 'C' ),
    ]


    
    def __init__(self, graph: Graph):

        self.projects = list()
        for c1, c2, s1, s2 in Projects.BASE_TABLE:
            
            for n1 in sorted(graph.node_classes[c1[1]], key=lambda x:graph.node_names[x]):
                nn1 = graph.node_names[n1]
                for n2 in sorted(graph.node_classes[c2[1]], key=lambda x:graph.node_names[x]):
                    nn2 = graph.node_names[n2]
                    cost = [s1,s2]
                    # base
                    base = Project("Base fix '{}' ({}) triggers '{}' ({})".format(nn1, c1[0], nn2, c2[0]), Project.BASE,
                                                 set([n1]), set([n2]), set([]),
                                                 cost, None)
                    self.projects.append(base)
                    
                    # improv-A, no trade-off
                    improvA = Project("Improved fix '{}' ({})".format(nn1, c1[0]),
                                      Project.A, set([n1]), set(), set(),
                                      cost + cost, base)
                    self.projects.append(improvA)
        
        self.project_for_name = { project.name: project for project in self.projects }
        self.names = sorted(list(self.project_for_name.keys()))
        
    def to_json(self):
        return self.projects
        
