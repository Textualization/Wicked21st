# -*- coding: utf-8 -*-
# Copyright (C) 2021 Textualization Software Ltd.
# Distributed under the terms of the Apache Software License 2.0
# http://www.apache.org/licenses/LICENSE-2.0

import random
import copy

class Game:

    PHASES = [ 'ENGAGE', 'ACTIVATE', 'REFLECT', 'END' ]
    STEPS_PER_PHASE = { 'ENGAGE' : [ 'MOVING',
                                     'DRAWING POWER',
                                     'DRAWING MONEY',
                                     'DRAWING CARDS',
                                     'CRISIS RISING' ],
                        'ACTIVATE' : [ 'ATTEMPTING PROJECTS',
                                       'PASSING POLICY',
                                       'DOING RESEARCH'
                                      ],
                        'REFLECT' : [ 'EMPATHIZING',
                                      'STRATEGIZING' ],
                        'END': [ 'CRISIS ROLLING' ]
                       }
    
    def __init__(self, game_def: GameDef, players: list):
        self.game_def = game_def
        self.players = players
        self.log = list()
        self.phase_start_state = None
        self.activate_phase_checks = None

    def start(self, rand):
        drawpiles = DrawPiles(rand)
        player_state = [ PlayState(p, { '!': 0, '$': 0 }, list(),
                                   p.pick(Player.INIT_LOC, self.game_def.board.locations, rand)) for p in self.players ]
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
            if self.state.player == 0:
                self.phase_start_state = copy.deepcopy(self.state)

            # moving
            new_loc = self.game_def.players[self.state.player].pick(Player.NEW_LOC,
                                                                    self.game_def.board.locations, rand, self.state.players[self.state.player],
                                                                    self.phase_start_state)
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
                                                          self.phase_start_state)
            self.state.players[self.state.player].cards.append(drawn)
            log.append( { 'phase' : Game.PHASES[self.state.phase],
                          'step' : Game.STEPS_PER_PHASE[self.state.phase][3],
                          'target' : drawn,
                          'memo' : 'first',
                          'state' : self.state.to_json() } )
            accessible_piles = list(set(accessible_piles) - set([drawn]))
            drawn = self.game_def.players[self.state.player].pick(PILE_DRAW, accessible_piles, rand, self.state.players[self.state.player],
                                                          self.phase_start_state)
            self.state.players[self.state.player].cards.append(drawn)
            log.append( { 'phase' : Game.PHASES[self.state.phase],
                          'step' : Game.STEPS_PER_PHASE[self.state.phase][3],
                          'target' : drawn,
                          'memo' : 'second',
                          'state' : self.state.to_json() } )
            # crisis rising
            self.state.players[self.state.player].crisis_chips += 1
            log.append( { 'phase' : Game.PHASES[self.state.phase],
                          'step' : Game.STEPS_PER_PHASE[self.state.phase][4],
                          'state' : self.state.to_json() } )
        elif self.state.phase == 1: # activate
            if self.state.player == 0:
                self.phase_start_state = copy.deepcopy(self.state)
                self.activate_phase_checks = list()
            
            # projects
            
            ## decide whether to start a new project?
            ## play cards for any of its projects?
            ## if rolls fail, they go to the 'failed rolls in turn' for the emphasizing section
            ## if rolls fail 2d, crisis chips are added
            pass
            # policies
            pass
        elif self.state.phase == 2: # reflect
            #EMPATHIZING
            pass
            #STRATEGIZING
        else: # the end
            pass
            
            

        
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

