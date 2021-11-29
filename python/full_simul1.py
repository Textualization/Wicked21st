# -*- coding: utf-8 -*-
# Copyright (C) 2021 Textualization Software Ltd.
# Distributed under the terms of the Apache Software License 2.0
# http://www.apache.org/licenses/LICENSE-2.0

import random
import copy
import sys

import numpy as np

from wicked21st.graph import load_graph, Cascades
from wicked21st.classes import Classes
from wicked21st.project import Projects
from wicked21st.techtree import TechTree
from wicked21st.definitions import GameInit, GameDef
from wicked21st.player import Player
from wicked21st.state import GraphState
from wicked21st.game import Game
from wicked21st.exceptions import EmptyDrawPile
from wicked21st.ai import GreedyPlayer

import config

NUM_PLAYERS = 3

seed = config.SEED

if len(sys.argv) > 1:
    seed = int(sys.argv[1])

rand = random.Random(seed) 

# definitions
graph_def = load_graph(config.GRAPH)
cascade_def  = Cascades(graph_def, "cascading.tsv")
classes_def = Classes()
project_def = Projects(graph_def)
tree_def = TechTree(graph_def)

initial_graph = GraphState(graph_def)
for topic in config.IN_CRISIS:
    if topic not in set(graph_def.node_names.values()):
        print(topic)
    initial_graph.in_crisis(topic)

game_init = GameInit(initial_graph)
game_def = GameDef(game_init, NUM_PLAYERS, config.CRISIS_CHECK, classes_def, graph_def, cascade_def, tree_def, project_def)

# assemble random players

players = [ GreedyPlayer("Player{}".format(p+1), p) for p in range(NUM_PLAYERS) ]

game = Game(game_def, players)
game.start(rand)

exc = False
while not game.finished and game.state.turn < config.GAME_LENGTH:
    print('turn', game.state.turn, 'player', game.state.player, Game.PHASES[game.state.phase])
    #print("\t\t", ",".join(game.state.graph.are_in_crisis('ECONOMIC')))
    log0 = len(game.log)
    try:
        game.step(rand)
        for e in game.log[log0:]:
            line = "{}\t{}".format(e['phase'], e['step'])
            if 'target' in e:
                line = "{}\t{}".format(line, e['target'])
                if 'memo' in e:
                    memo = e['memo']
                    if 'args' in e:
                        args = e['args']
                        memo = memo.format(*args)
                line = "{}\t{}".format(line, memo)
            print(line)
        #print('Piles: ' + str(game.state.drawpiles.to_json()))
    except EmptyDrawPile as e:
        print("GAME ERROR: ran out of {}".format(e.suit))
        exc = True
        break

if not exc:
    if game.finished:
        print("GAME LOST")
    else:
        print("GAME WON")
