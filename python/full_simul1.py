# -*- coding: utf-8 -*-
# Copyright (C) 2021 Textualization Software Ltd.
# Distributed under the terms of the Apache Software License 2.0
# http://www.apache.org/licenses/LICENSE-2.0

import random
import copy

import numpy as np

SEED = 42
NUM_PLAYERS = 4

rand = random.Random(SEED)

# definitions
graph_def = load_graph("map20210812.mm")
board_def = Board()
tree_def = TechTree()
classes_def = Classes()

initial_graph = GraphState(graph_def)
initial_graph['Social Inequity'] = 1
initial_graph['Affordable Housing'] = 1
initial_graph['Community Networks Breakdown'] = 1
initial_graph['Systemic Corruption'] = 1
initial_graph['Monopoly'] = 1
initial_graph['Unsustainable Harvesting'] = 1
initial_graph['Polluting Industry'] = 1
initial_graph['Fossil Fuel Dependency'] = 1

game_init = GameInit(initial_graph)

game_def = GameDef(game_init, NUM_PLAYERS, graph_def, board_def, tree_def)

# assemble random players

players = [ Player("Player{}".format(p+1), p, classes_def.pick(rand)) for p in range(NUM_PLAYERS) ]

