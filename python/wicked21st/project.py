# -*- coding: utf-8 -*-
# Copyright (C) 2021 Textualization Software Ltd.
# Distributed under the terms of the Apache Software License 2.0
# http://www.apache.org/licenses/LICENSE-2.0

class Project:

    BASE = 0
    A    = 1
    B    = 2

    TYPES = [ 'Base', 'Improvement-A', 'Improvement-B' ]

    def __init__(self, name, type_, fixes: set, triggers: set, protects: set, cost: list, parent: Project):
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
        if parent is not None:
            result['parent'] = self.parent.name
   
class Projects:

    BASE_TABLE =  [ 
        ( Graph.ENVIRONMENTAL,          Graph.LIVING_STANDARDS,	'C', 'D' )
        ( Graph.LIVING_STANDARDS,	Graph.CLASS,	        'H', 'C' )
        ( Graph.SOCIAL,	                Graph.INDUSTRIAL,	'H', 'D' )
        ( Graph.CLASS,	                Graph.SOCIAL,	        'H', 'S' )
        ( Graph.ECONOMIC,	        Graph.ENVIRONMENTAL,	'S', 'D' )
        ( Graph.INDUSTRIAL,	        Graph.ECONOMIC,	        'S', 'C' )
    ]
    
    def __init__(self, graph: Graph):

        self.projects = list()
        for c1, c2, s1, s2 in BASE_TABLE:
            
            for n1 in graph.node_classes[c1[1]]:
                for n2 in graph.node_classes[c2[1]]:
                    cost = [s1,s2]
                    # base
                    base = Project("Base {} ({}) x {} ({})".format(n1, c1[0], n2, c2[0]), Project.BASE,
                                                 set([n1]), set([n2]), set([]),
                                                 cost, None)
                    self.projects.append(base)
                    
                    # improv-A, no trade-off
                    improvA = Project("Improv-A {} ({})".format(n1, c1[0]), Project.A
                                      set([n1]), set(), set(),
                                      cost + [ 'H', 'D' ], base)
                    self.projects.append(improvA)
                    # improv-B
                    for other in graph.node_classes[c1[1]]:
                        if other != n1:
                            self.projects.append(Project("Improv-B {}+{} ({})".format(n1, other, c1[0]), Project.B,
                                                         set([n1, other]), set(), set(),
                                                         cost + [ 'H', 'D', 'C', 'H' ], improvA))
                    for other in graph.node_names:
                        self.projects.append(Project("Improv-B {} ({}) +prot {}".format(n1, c1[0], other), Project.B,
                                                     set([n1]), set(), set([other]),
                                                     cost + [ 'H', 'D', 'D', 'S' ], improvA))
                                
                    # improv-A, protect
                    for other in graph.node_classes[c1[1]]:
                        improvA = Project("Improv-A {}+prot {} ({}) x {} ({})".format(n1, other, c1[0], n2, c2[0]), Project.A,
                                                     set([n1]), set([n2]), set([other]),
                                                     cost + [ 'S', 'C' ], base)
                        self.projects.append(improvA)

                        # improv-B
                        for other2 in graph.node_classes[c1[1]]:
                            if other2 != n1:
                                self.projects.append(
                                    Project("Improv-B {}+{}+prot {} ({}) x {} ({})".format(n1, other2, other, c1[0], n2, c2[0]), Project.B,
                                            set([n1, other2]), set([n2]), set([other]),
                                            cost + [ 'S', 'C', 'C', 'H' ], improvA))
                        for other2 in graph.node_names:
                            if other2 != other:
                                self.projects.append(
                                    Project("Improv-B {}+prot {} ({}) +prot {} x {} ({})".format(n1, other, c1[0], other2, n2, c2[0]), Project.B,
                                            set([n1]), set([n2]), set([other, other2]),
                                            cost + [ 'S', 'C', 'D', 'S' ], improvA))
        
        self.project_for_name = { project.name: project for project in self.projects }
        self.names = list(project_for_name.keys())
        
    def to_json(self):
        return self.projects
        
