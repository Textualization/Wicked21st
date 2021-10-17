# -*- coding: utf-8 -*-
# Copyright (C) 2021 Textualization Software Ltd.
# Distributed under the terms of the Apache Software License 2.0
# http://www.apache.org/licenses/LICENSE-2.0

from .graph import Graph
from .drawpiles import DrawPiles


### Tech details:
###
###
### Technologies take a discard of a given suit plus a unit of money to make a research cycle in a turn. It takes 3 research cycles to research a technology.
###
### The tech tree is as follows: Base-<suit> can be researched right away and needs <suit> as the discard card. Expanded-<suit> can be researched once Base-<suit> has been researched. It also needs a <suit> discard. Finally, once Expanded-<suit 1> and Base-<suit 2> have been researched, Auto-Protect-<problem-in-CAT> can be researched. It takes card of suit 3 for discard:

class Tech:

    BASE = 0
    A = 1
    B = 2

    TYPES = [ 'Base', 'Expanded', 'Auto-Protect' ]

    def __init__(self, name, type_, suit, node=None, parents: set=None, turns=3):
        self.name = name
        self.type_ = type_
        self.suit = suit
        self.node = node
        self.parents = parents
        self.turns = turns

    def to_json(self):
        result = { 'name' : self.name,
                   'type' : Tech.TYPES[self.type_],
                   'suit' : self.suit }
        if self.node is not None:
            result['node'] = self.node
        if self.parents is not None:
            result['parents'] = list(self.parents)
        return result

class TechTree:
###
### |    CAT          |	suit 1| suit 2| suit 3|
### |ENVIRONMENTAL    |	C     | D     | H |
### |LIVING_STANDARDS | H     | C     | S |
### |SOCIAL           |	D     | H     | S |
### |CLASS            |	H     | S     | D |
### |ECONOMIC         | S     | D     | C |
### |INDUSTRIAL       | S     | C     | D |

    BASE_TABLE =  [ 
        ( Graph.ENVIRONMENTAL,    'C', 'D', 'H' ),
        ( Graph.LIVING_STANDARDS, 'H', 'C', 'S' ),
        ( Graph.SOCIAL,	          'D', 'H', 'S' ),
        ( Graph.CLASS,	          'H', 'S', 'D' ),
        ( Graph.ECONOMIC,	  'S', 'D', 'C' ),
        ( Graph.INDUSTRIAL,	  'S', 'C', 'D' ),
    ]
###
###   At any given time, the "research boundary" (or "state of the art") are the techs that can be researched at a given point.
###
### For example, at the start of the game, Base-C, Base-H, Base-D, Base-S can be researched.
###
### Upon researching Base-D, the research boundary is Base-C, Base-H, Expanded-D, Base-S
###
### Upon researching Expanded-D, the research boundary is Base-C, Base-H, Base-S
###
### Upon researching Base-H, according to the table above, any node in the category "SOCIAL" can be researched, so the boundary becomes:
###
### Base-C, Base-S, Expanded-H, Auto-Protect-"Weak Political Voice", Auto-Protect-"Social Inequity", Auto-Protect-"Food Shortage", Auto-Protect-"Affordable Housing", Auto-Protect-"Clean Water Shortage" 
    
    def __init__(self, graph: Graph):
        self.technologies = list()

        suit_to_base = dict()
        suit_to_expanded = dict()

        for suit in DrawPiles.SUITS:
            base = Tech('Base {}'.format(suit), Tech.BASE, suit)
            self.technologies.append(base)
            suit_to_base[suit] = base

            expanded = Tech('Expanded {}'.format(suit), Tech.A, suit, parents=set([base.name]))
            self.technologies.append(expanded)
            suit_to_expanded[suit] = expanded

        for cat, suit_a, suit_b, suit_c in TechTree.BASE_TABLE:
            expanded = suit_to_expanded[suit_a]
            base = suit_to_base[suit_b]

            for n in graph.node_classes[cat[1]]:
                nn = graph.node_names[n]

                protected = Tech('Protect "{}"'.format(nn), Tech.B, suit_c, n, parents=set([expanded.name, base.name]))
                self.technologies.append(protected)

        self.tech_for_name = { tech.name: tech for tech in self.technologies }
        self.names = list(self.tech_for_name.keys())
        
    def to_json(self):
        return [ tech.to_json() for tech in self.technologies ]
        
