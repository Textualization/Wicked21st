# -*- coding: utf-8 -*-
# Copyright (C) 2021-2022 Textualization Software Ltd.
# Distributed under the terms of the MIT License
# https://mit-license.org/

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
from wicked21st.ai import GreedyPlayer

import config

num_players = int(sys.argv[1])

mainrand = random.Random(config.SEED)
seeds = list()
for _ in range(config.NUM_RUNS):
    s = mainrand.getrandbits(8 * 8)
    seeds.append(s)

# definitions
graph_def, cascade_def = load_graph(config.GRAPH)
classes_def = Classes()
project_def = Projects(graph_def)
tree_def = TechTree(graph_def)


def simulate_one(arg):
    run, seed = arg
    rand = random.Random(seed)

    initial_graph = GraphState(graph_def)
    if type(config.IN_CRISIS) is int:
        all_nodes = list(graph_def.node_names.values())
        rand.shuffle(all_nodes)
        for topic in all_nodes[: config.IN_CRISIS]:
            initial_graph.in_crisis(topic)
    else:
        for topic in config.IN_CRISIS:
            initial_graph.in_crisis(topic)

    game_init = GameInit(initial_graph)
    game_def = GameDef(
        game_init,
        num_players,
        config.CRISIS_CHECK,
        config.CRISIS_RISING,
        classes_def,
        graph_def,
        cascade_def,
        tree_def,
        project_def,
    )

    # assemble random players
    players = [GreedyPlayer("Player{}".format(p + 1), p) for p in range(num_players)]

    game = Game(game_def, players)

    game.start(rand)
    exc = False
    try:
        while not game.finished and game.state.turn < config.GAME_LENGTH:
            log0 = len(game.log)
            game.step(rand)
            if config.VERBOSE:
                for e in game.log[log0:]:
                    line = "{}\t{}\t{}\t{}".format(
                        run, game.state.turn, e["phase"], e["step"]
                    )
                    if "target" in e:
                        line = "{}\t{}".format(line, e["target"])
                        if "memo" in e:
                            memo = e["memo"]
                            if "args" in e:
                                args = e["args"]
                                memo = memo.format(*args)
                        line = "{}\t{}".format(line, memo)
                    print(line)
    except EmptyDrawPile as e:
        return -1, True
    return not game.finished, False


pool = multiprocessing.Pool(20)
results = pool.map(simulate_one, enumerate(seeds))
won = sum(map(lambda x: 0 if x[1] else x[0], results))
errors = sum(map(lambda x: x[1], results))

print(
    "\n\n\n\n\n\nplayers=",
    num_players,
    "crisis<",
    config.CRISIS_CHECK,
    "rising=",
    config.CRISIS_RISING,
    "runs=",
    config.NUM_RUNS,
    "won=",
    won,
    int(won * 1.0 / config.NUM_RUNS * 1000) / 10,
    "%",
    "errors=",
    errors,
)
