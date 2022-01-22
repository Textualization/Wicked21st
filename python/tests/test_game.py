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


def deterministic_run(seed, make_player):
    rand = random.Random(seed)

    # definitions
    graph_def, cascade_def = load_graph(config.GRAPH)
    classes_def = Classes()
    project_def = Projects(graph_def)
    tree_def = TechTree(graph_def)

    initial_graph = GraphState(graph_def)
    for topic in config.IN_CRISIS:
        if topic not in set(graph_def.node_names.values()):
            print(topic)
        initial_graph.in_crisis(topic)

    game_init = GameInit(initial_graph)
    game_def = GameDef(
        game_init,
        NUM_PLAYERS,
        config.CRISIS_CHECK,
        config.CRISIS_RISING,
        classes_def,
        graph_def,
        cascade_def,
        tree_def,
        project_def,
    )

    # assemble random players
    players = [make_player(p) for p in range(NUM_PLAYERS)]

    game = Game(game_def, players)
    game.start(rand)

    logs = list()

    exc = False
    while not game.finished and game.state.turn < config.GAME_LENGTH:
        logs.append(
            (
                "turn",
                game.state.turn,
                "player",
                game.state.player,
                Game.PHASES[game.state.phase],
            )
        )
        log0 = len(game.log)
        try:
            game.step(rand)
            for e in game.log[log0:]:
                line = "{}\t{}".format(e["phase"], e["step"])
                if "target" in e:
                    line = "{}\t{}".format(line, e["target"])
                    if "memo" in e:
                        memo = e["memo"]
                        if "args" in e:
                            args = e["args"]
                            memo = memo.format(*args)
                    line = "{}\t{}".format(line, memo)
                logs.append(line)
        except EmptyDrawPile as e:
            logs.append("GAME ERROR: ran out of {}".format(e.suit))
            exc = True
            break

    if not exc:
        if game.finished:
            logs.append("GAME LOST")
        else:
            logs.append("GAME WON")
    return logs


def test_determinism_random():
    def make_player(p):
        return Player("Player{}".format(p + 1), p)         

    base = deterministic_run(1, make_player)

    for idx in range(10):
        run = deterministic_run(1, make_player)

        assert base == run

def test_determinism_greedy():
    def make_player(p):
        return GreedyPlayer("GreedyPlayer{}".format(p + 1), p)         

    base = deterministic_run(1, make_player)

    for idx in range(10):
        run = deterministic_run(1, make_player)

        assert base == run
