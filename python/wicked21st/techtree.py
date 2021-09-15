# -*- coding: utf-8 -*-
# Copyright (C) 2021 Textualization Software Ltd.
# Distributed under the terms of the Apache Software License 2.0
# http://www.apache.org/licenses/LICENSE-2.0

from .graph import Graph
from .drawpiles import DrawPiles

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

    BASE_TABLE =  [ 
        ( Graph.ENVIRONMENTAL,    'C', 'D', 'H' ),
        ( Graph.LIVING_STANDARDS, 'H', 'C', 'S' ),
        ( Graph.SOCIAL,	          'D', 'H', 'S' ),
        ( Graph.CLASS,	          'H', 'S', 'D' ),
        ( Graph.ECONOMIC,	  'S', 'D', 'C' ),
        ( Graph.INDUSTRIAL,	  'S', 'C', 'D' ),
    ]

    
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
        
