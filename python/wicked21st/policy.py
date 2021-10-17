# -*- coding: utf-8 -*-
# Copyright (C) 2021 Textualization Software Ltd.
# Distributed under the terms of the Apache Software License 2.0
# http://www.apache.org/licenses/LICENSE-2.0

from .graph import Graph


### Policy details
###
### Policies require a number of power units to "pass" and a number of turns to get in action. After they have passed, they need one power unit in each of the waiting turns.
###
###
### The policies need power units based on the number of players divided by 2, rounded to the lowest number. This is called "quorum".
###
### There are three types of policies:
###
### Base, which fixes a problem. It takes quorum + 2 power units and 1 turn to get in action.


Protect-Category, which fixes a problem, also protects a problem in the same category as the original problem (it can protect the original problem). It costs quorum +4 and takes 2 turns to get into action.


Protect-Any, which fixes a problem, protects a problem in the same category and additionally protects any other problem in any category. It costs quorum+6 and takes 3 turns to get into action.


Note that the problems (to fix and protect) are decided when the policy is created. Over time that problem might no longer be relevant and thus the policy might be abandoned.



class Policy:

    A = 0
    B = 1
    C = 2

    TYPES = [ 'Base', 'Protect-Extra', 'Protect-Any' ]

    # cost is 'quorum': int, 'turns': int
    # added value on top of quorum and turns is the number of turns to wait after it passes
    def __init__(self, name, type_, fixes: set, triggers: set, protects: set, cost: list, parent):
        self.name = name
        self.type_ = type_
        self.fixes = fixes
        self.triggers = triggers
        self.protects = protects
        self.cost = cost
        self.parent = parent
        self.tojson_memo = None

    def to_json(self):
        if self.tojson_memo is None:
            self.tojson_memo = {
                'name':     self.name,
                'type':     Policy.TYPES[ self.type_ ],
                'fixes':    list(self.fixes),
                'triggers': list(self.triggers),
                'protects': list(self.protects),
                'cost':     self.cost
            }
            if self.parent is not None:
                self.tojson_memo['parent'] = self.parent.name
        return self.tojson_memo
   
class Policies:

    # this is different from projects, watch out
    BASE_TABLE =  [ 
        ( Graph.ENVIRONMENTAL,          Graph.LIVING_STANDARDS ),
        ( Graph.LIVING_STANDARDS,	Graph.CLASS ),
        ( Graph.SOCIAL,	                Graph.ECONOMIC ),
        ( Graph.CLASS,	                Graph.SOCIAL ),
        ( Graph.ECONOMIC,	        Graph.INDUSTRIAL ),
        ( Graph.INDUSTRIAL,	        Graph.ENVIRONMENTAL ),
    ]
    
    def __init__(self, graph: Graph):

        self.policies = list()
        for c1, c2 in Policies.BASE_TABLE:
            
            for n1 in sorted(graph.node_classes[c1[1]], key=lambda x:graph.node_names[x]):
                    nn1 = graph.node_names[n1]
                #for n2 in graph.node_classes[c2[1]]:
                    #nn2 = graph.node_names[n2]
                    #cost = ( 0, 0 )
                    # base
                    #base = Policy("Base fix '{}' ({}) triggers '{}' ({})".format(nn1, c1[0], nn2, c2[0]), Policy.BASE,
                    #                             set([n1]), set([n2]), set([]),
                    #                             cost, None)
                    #self.policies.append(base)
                    
                    # improv-A, no trade-off
                    cost = ( 2, 2 )
                    improvA = Policy("Policy-A fix '{}' ({})".format(nn1, c1[0]), Policy.A,
                                      set([n1]), set(), set(),
                                      cost, None)
                    self.policies.append(improvA)

                    # improv-B, protect another in same cat
                    for other in sorted(graph.node_classes[c1[1]], key=lambda x:graph.node_names[x]):
                        othern = graph.node_names[other]
                        cost = ( 4, 4 )
                        improvB = Policy("Policy-B fix '{}' protect '{}' ({})".format(nn1, othern, c1[0]), Policy.B,
                                         set([n1]), set(), set([other]),
                                         cost, improvA)
                        self.policies.append(improvB)

                        # improv-C, protect any other
                        for other2, other2n in graph.node_names.items():
                            if other2 != other:
                                cost = ( 6, 6 )
                                improvC = Policy("Policy-C fix '{}' protect '{}' ({}) protect '{}'".format(nn1, othern, c1[0], other2n), Policy.C,
                                                 set([n1]), set(), set([other, other2]),
                                                 cost, improvB)
                                self.policies.append(improvC)
        
        self.policy_for_name = { policy.name: policy for policy in self.policies }
        self.names = sorted(list(self.policy_for_name.keys()))
        
    def to_json(self):
        return self.policies
        
