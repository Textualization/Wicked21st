# -*- coding: utf-8 -*-
# Copyright (C) 2021 Textualization Software Ltd.
# Distributed under the terms of the Apache Software License 2.0
# http://www.apache.org/licenses/LICENSE-2.0

from .graph import Graph
from .drawpiles import DrawPiles


### Tech details:
###
###
### Technologies take a discard of a given suit plus a unit of money to make a research cycle in a turn. It takes 2 research cycles to research a technology.
###
### The tech tree is as follows: Base-<suit> can be researched right away and needs <suit> as the discard card. Once Base-<suit 1> and Base-<suit 2> have been researched, Auto-Protect-<problem-in-CAT> can be researched. It takes card of suit 2 for discard:


class Tech:

    BASE = 0
    PROTECT = 1

    TYPES = ["Base", "Auto-Protect"]

    def __init__(self, name, type_, suit, node=None, parents: set = None, turns=2):
        self.name = name
        self.type_ = type_
        self.suit = suit
        self.node = node
        self.parents = parents
        self.turns = turns

    def to_json(self):
        result = {"name": self.name, "type": Tech.TYPES[self.type_], "suit": self.suit}
        if self.node is not None:
            result["node"] = self.node
        if self.parents is not None:
            result["parents"] = list(self.parents)
        return result


class TechTree:
    ###
    ### |    CAT          | suits |
    ### |INDUSTRIAL       | S, C  |
    ### |ECONOMIC         | S, D  |
    ### |LIVING_STANDARDS | S, H  |
    ### |CLASS            | C, H  |
    ### |ENVIRONMENTAL    | C, D  |
    ### |SOCIAL           | H, D  |

    BASE_TABLE = [
        (Graph.INDUSTRIAL, "S", "C"),
        (Graph.ECONOMIC, "S", "D"),
        (Graph.LIVING_STANDARDS, "S", "H"),
        (Graph.CLASS, "C", "H"),
        (Graph.ENVIRONMENTAL, "C", "D"),
        (Graph.SOCIAL, "H", "D"),
    ]
    ###
    ###   At any given time, the "research boundary" (or "state of the art") are the techs that can be researched at a given point.
    ###
    ### For example, at the start of the game, Base-C, Base-H, Base-D, Base-S can be researched.
    ###
    ### Upon researching Base-D, the research boundary is Base-C, Base-H, Base-S
    ###
    ### Upon researching Base-H, according to the table above, any node in the category "SOCIAL" can be researched, so the boundary becomes:
    ###
    ### Base-C, Base-S, Auto-Protect-"Weak Political Voice", Auto-Protect-"Social Inequity", Auto-Protect-"Food Shortage", Auto-Protect-"Affordable Housing", Auto-Protect-"Clean Water Shortage"

    def __init__(self, graph: Graph):
        self.technologies = list()

        suit_to_base = dict()
        suit_to_expanded = dict()

        for suit in DrawPiles.SUITS:
            base = Tech("Base {}".format(suit), Tech.BASE, suit)
            self.technologies.append(base)
            suit_to_base[suit] = base

        for cat, suit_a, suit_b in TechTree.BASE_TABLE:
            for n in graph.node_classes[cat[1]]:
                nn = graph.node_names[n]

                base_a = suit_to_base[suit_a]
                base_b = suit_to_base[suit_b]

                protected = Tech(
                    'Protect "{}"'.format(nn),
                    Tech.PROTECT,
                    suit_b,
                    n,
                    parents=set([base_a.name, base_b.name]),
                )
                self.technologies.append(protected)

                protected = Tech(
                    'Protect "{}"'.format(nn),
                    Tech.PROTECT,
                    suit_a,
                    n,
                    parents=set([base_a.name, base_b.name]),
                )
                self.technologies.append(protected)

        self.names = sorted(list({tech.name for tech in self.technologies}))

    def to_json(self):
        return [tech.to_json() for tech in self.technologies]
