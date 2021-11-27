# -*- coding: utf-8 -*-
# Copyright (C) 2021 Textualization Software Ltd.
# Distributed under the terms of the Apache Software License 2.0
# http://www.apache.org/licenses/LICENSE-2.0

import random
import copy
import sys
import multiprocessing

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

import config

num_players = int(sys.argv[1])

mainrand = random.Random(config.SEED)
seeds = list()
for _ in range(config.NUM_RUNS):
    n = mainrand.randbytes(8)
    s = 0
    for b in n:
        s = s*256 + b
    seeds.append(s)

# definitions
graph_def = load_graph(config.GRAPH)
cascade_def  = Cascades(graph_def, "cascading.tsv")
classes_def = Classes()
project_def = Projects(graph_def)
tree_def = TechTree(graph_def)

initial_graph = GraphState(graph_def)
for topic in config.IN_CRISIS:
    initial_graph.in_crisis(topic)

def simulate_one(seed):
    rand = random.Random(seed)
    
    game_init = GameInit(initial_graph)
    game_def = GameDef(game_init, num_players, config.CRISIS_CHECK, classes_def, graph_def, cascade_def, tree_def, project_def)

    # assemble random players
    players = [ Player("Player{}".format(p+1), p) for p in range(num_players) ]

    game = Game(game_def, players)

    game.start(rand)
    exc = False
    try:
        while not game.finished and game.state.turn < config.GAME_LENGTH:
            log0 = len(game.log)
            game.step(rand)
            if config.VERBOSE:
                for e in game.log[log0:]:
                    line = "{}\t{}\t{}\t{}".format(run, game.state.turn, e['phase'], e['step'])
                    if 'target' in e:
                        line = "{}\t{}".format(line, e['target'])
                        if 'memo' in e:
                            memo = e['memo']
                            if 'args' in e:
                                args = e['args']
                                memo = memo.format(*args)
                        line = "{}\t{}".format(line, memo)
                    print(line)
    except EmptyDrawPile as e:
        return -1, True
    return not game.finished, False

pool = multiprocessing.Pool(20)
results = pool.map(simulate_one, seeds)
won = sum(map(lambda x: 0 if x[1] else x[0], results))
errors = sum(map(lambda x: x[1], results))

print("players=", num_players, "crisis<", config.CRISIS_CHECK, "runs=", config.NUM_RUNS, "won=", won, int(won * 1.0 / config.NUM_RUNS * 1000) / 10, "%", "errors=", errors )
