# -*- coding: utf-8 -*-
# Copyright (C) 2021 Textualization Software Ltd.
# Distributed under the terms of the Apache Software License 2.0
# http://www.apache.org/licenses/LICENSE-2.0

import random
import copy

import numpy as np

from wicked21st.graph import load_graph
from wicked21st.board import Board
from wicked21st.classes import Classes
from wicked21st.project import Projects
from wicked21st.policy import Policies
from wicked21st.techtree import TechTree
from wicked21st.definitions import GameInit, GameDef
from wicked21st.player import Player
from wicked21st.state import GraphState
from wicked21st.game import Game

SEED = 43
NUM_PLAYERS = 3

rand = random.Random(SEED)

# definitions
graph_def = load_graph("map20210812.mm")
board_def = Board()
classes_def = Classes()
project_def = Projects(graph_def)
policy_def = Policies(graph_def)
tree_def = TechTree(graph_def)

initial_graph = GraphState(graph_def)
initial_graph.in_crisis('Social Inequity')
initial_graph.in_crisis('Affordable Housing')
initial_graph.in_crisis('Community Networks Breakdown')
initial_graph.in_crisis('Systemic Corruption')
initial_graph.in_crisis('Monopoly')
initial_graph.in_crisis('Unsustainable Harvesting')
initial_graph.in_crisis('Polluting Industry')
initial_graph.in_crisis('Fossil Fuel Dependency')

game_init = GameInit(initial_graph)
game_def = GameDef(game_init, NUM_PLAYERS, classes_def, graph_def, board_def, tree_def, policy_def, project_def)

# assemble random players

players = [ Player("Player{}".format(p+1), p, classes_def.pick(rand)) for p in range(NUM_PLAYERS) ]

game = Game(game_def, players)
game.start(rand)

while not game.finished and game.state.turn < 12:
    print('turn', game.state.turn, 'player', game.state.player, Game.PHASES[game.state.phase])
    #print("\t\t", ",".join(game.state.graph.are_in_crisis('ECONOMIC')))
    log0 = len(game.log)
    game.step(rand)
    for e in game.log[log0:]:
        print("{}\t{}\t{}\t\t{}".format(e['phase'], e['step'], e.get('target', "-"), e.get('memo', "-")))

if game.finished:
    print("GAME LOST")
else:
    print("GAME WON")
