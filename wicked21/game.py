# -*- coding: utf-8 -*-
# Copyright (C) 2021 Textualization Software Ltd.
# Distributed under the terms of the Apache Software License 2.0
# http://www.apache.org/licenses/LICENSE-2.0

import random
import copy

import numpy as np

def to_json(v):
    if v is Int:
        return v
    if v is string:
        return v
    if v is list:
        return [ to_json(_) for _ in v ]
    if v is dict:
        return { k: to_json(vv) for k, vv in v.items() }
    return v.to_json()
        
class GameInit:
    def __init__(self, graph_init: GraphState):
        self.graph = graph_init

    def to_json(self):
        return { 'graph' : self.graph.to_json() }

class GameDef:
    def __init__(self, game_init: GameInit,
                 num_players: Int,
                 classes_def: Classes,
                 graph_def: Graph,
                 board_def: Board,
                 techtree_def: TechTree):
        self.game_init = game_init
        self.num_players = num_players
        self.classes = classes_def
        self.graph = graph_def
        self.board = board_def
        self.tree = techtree_def
        
    def to_json(self):
        return { 'num_players' : self.num_players,
                 'game_init' : self.game_init.to_json(),
                 'classes' : self.classes_def.to_json(),
                 'graph' : self.graph.to_json(),
                 'tree' : self.tree.to_json(),
                 'board': self.board.to_json() }

class ValidKeysDict(dict):
    def __init__(self, keys):
        super.__init__(self)
        self.valid_keys = set(keys)
    def __getitem__(self, key):
        assert key in self.valid_keys
        return super.__getitem__(key)
    def __setitem__(self, key, value):
        assert key in self.valid_keys
        return super.__setitem__(key, value)
    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            self[k] = v
    def get(self, key, value=None):
        assert key in self.valid_keys
        return super.get(key, value)

    def to_json(self):
        return to_json(self)

class GraphState(ValidKeysDict):
    def __init__(self, graph):
        super.__init__(self, graph.nodes())
        self.graph = graph

    def in_crisis(self, category=None):
        result = set()
        for k, v in self.items():
            if v:
                if categoy is None or k in self.graph.class_for_node[self.graph.name_to_id[k]] == self.graph.category_for_name[category]:
                    result.add(k)
        return k

class BoardState(ValidKeysDict):
    def __init__(self, board):
        super.__init__(self, board.locations)

class TechTreeState(ValidKeysDict):
    def __init__(self, tree):
        super.__init__(self, tree.technologies)

class PolicyState(ValidKeysDict):
    def __init__(self, policies):
        super.__init__(self, policies.names)

class GameState:
    def __init__(self,
                 turn: Int,
                 phase: Int,
                 player: Int,
                 game_def: GameDef,
                 players_state: list,
                 graph_state: GraphState,
                 board_state: BoardState,
                 techtree_state: TechtreeState,
                 policy_state: PolicyState,
                 drawpiles_state: DrawPiles):
        self.turn = turn
        self.phase = phase
        self.player = player
        self.game = game_def
        self.players = players_state
        self.graph = graph_state
        self.board = board_state
        self.techtree = techtree_state
        self.policy = policy_state
        self.drawpiles = drawpiles_state

    def to_json(self):
        return { 'game': self.game.to_json(),
                 'players' : to_json(self.players),
                 'board' : self.board.to_json(),
                 'graph' : self.graph.to_json(),
                 'tech' : self.techtree.to_json(),
                 'policy' : self.policy.to_json(),
                 'piles' : self.drawpiles.to_json() }

class Game:

    PHASES = [ 'ENGAGE', 'ACTIVATE', 'REFLECT', 'END' ]
    STEPS_PER_PHASE = { 'ENGAGE' : [ 'MOVING',
                                     'DRAWING POWER',
                                     'DRAWING MONEY',
                                     'DRAWING CARDS',
                                     'CRISIS RISING' ],
                        'ACTIVATE' : [ 'ATTEMPTING PROJECTS',
                                       'PASSING POWER' ],
                        'REFLECT' : [ 'VISIONING',
                                      'EMPATHIZING',
                                      'STRATEGIZING' ],
                        'END': [ 'CRISIS ROLLING',
                                 'FINALIZING',
                                 'SCENARIO CONCLUDING' ]
                       }
    
    def __init__(self, game_def: GameDef, players: list):
        self.game_def = game_def
        self.players = players
        self.log = list()

    def start(self, rand):
        drawpiles = DrawPiles(rand)
        player_state = [ PlayState(p, { '!': 0, '$': 0 }, list(), p.pick(Player.INIT_LOC, self.game_def.board.locations, rand)) for p in self.players ]
        graph_state = copy.deepcopy(self.game_def.game_init.graph)
        board_state = BoardState(self.game_def.board)
        for p in player_state:
            board_state[p.location] = board_state.get(p.location, set()) + set([ p.ordering ])
            self.state = GameState(0, 0, 0,
                                   self.game_def,
                                   player_state, graph_state, board_state,
                                   TechTreeState(self.game_def.techtree),
                                   PolicyState(self.game_def.policy),
                                   drawpiles)

    def advance(self):
        "Returns True is the game has ended"
        if len(self.state.graph.in_crisis()) == len(self.game_def.graph):
            self.finished = True
        else:
            self.state.player += 1
            if self.state.player == self.game_def.num_players:
                self.state.player = 0
                self.state.phase += 1
                if self.state.phase == len(Game.PHASES)
                    self.state.phase = 0
                    self.turn += 1
        return self.finished

    def cascade(self, node):
        "A node in crisis has been selected, deal with it. Returns the activated nodes."
        # follow a link
        outlinks = list(self.graph.outlinks[node])
        random.shuffle(outlinks)
        for outlink in outlinks:
            if outlink in self.good:
                self.good.remove(outlink)
                self.crisis.add(outlink)
                return [ outlink ]
        return []

    def step(self, rand):
        if self.state.phase == 0: # engage
            # moving
            new_loc = self.game_def.players[self.state.player].pick(Player.NEW_LOC, self.game_def.board.locations, rand, self.state.players[self.state.player],
                                                                    self.state)
            self.state.players[self.state.player].location = new_loc
            log.append( { 'phase' : Game.PHASES[self.state.phase],
                          'step' : Game.STEPS_PER_PHASE[self.state.phase][0],
                          'target' : new_loc,
                          'state' : self.state.to_json() } )
            # drawing power
            drawn = 1 + \
                (1 if self.game_def.board.resources[new_loc] == '!' else 0) + \
                (1 if self.game_def.players[self.state.player].player_class.resource == '!')
            self.state.players[self.state.player].resources['!'] += drawn
            log.append( { 'phase' : Game.PHASES[self.state.phase],
                          'step' : Game.STEPS_PER_PHASE[self.state.phase][1],
                          'target' : drawn,
                          'state' : self.state.to_json() } )
            # drawing money
            drawn = 5 - len(self.state.graph.in_crisis('ECONOMIC')) + 2 *  (
                (1 if self.game_def.board.resources[new_loc] == '$' else 0) + \
                (1 if self.game_def.players[self.state.player].player_class.resource == '$'))
            self.state.players[self.state.player].resources['$'] += drawn
            log.append( { 'phase' : Game.PHASES[self.state.phase],
                          'step' : Game.STEPS_PER_PHASE[self.state.phase][2],
                          'target' : drawn,
                          'state' : self.state.to_json() } )
            # draw cards
            accessible_piles = set([self.game_def.players[self.state.player].suit_a, self.players[self.state.player].suit_b ])
            accessible_piles.add(self.game_def.board.suits[new_loc])
            accessible_piles = list(accessible_piles)
            
            drawn = self.game_def.players[self.state.player].pick(PILE_DRAW, accessible_piles, rand, self.state.players[self.state.player],
                                                          self.state)
            self.state.players[self.state.player].cards.append(drawn)
            log.append( { 'phase' : Game.PHASES[self.state.phase],
                          'step' : Game.STEPS_PER_PHASE[self.state.phase][3],
                          'target' : drawn,
                          'memo' : 'first',
                          'state' : self.state.to_json() } )
            accessible_piles = list(set(accessible_piles) - set([drawn]))
            drawn = self.game_def.players[self.state.player].pick(PILE_DRAW, accessible_piles, rand, self.state.players[self.state.player],
                                                          self.state)
            self.state.players[self.state.player].cards.append(drawn)
            log.append( { 'phase' : Game.PHASES[self.state.phase],
                          'step' : Game.STEPS_PER_PHASE[self.state.phase][3],
                          'target' : drawn,
                          'memo' : 'second',
                          'state' : self.state.to_json() } )
            # crisis rising
            
            
            

        
    if random.random() < creation_prob:
      # we got ourselves a crisis!
      done = False
      while not done:
        in_crisis = random.choice(list(self.graph.node_names.keys())) # any problem, in crisis or otherwise
        if in_crisis in self.crisis: # been there, done that
          done = len(self.cascade(in_crisis)) > 0
        else:
          self.good.remove(in_crisis)
          self.crisis.add(in_crisis)
          done = True
    if random.random() < resolution_prob:
      # don't just stand there, fix something!
      # here reinforcement learning would be handy    
      if len(self.crisis) > 0:
        to_solve = random.choice(list(self.crisis))
        self.crisis.remove(to_solve)
        self.good.add(to_solve)
    return super().step()

GAMES['BaseGame'] = BaseGame()

