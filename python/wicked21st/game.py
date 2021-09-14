# -*- coding: utf-8 -*-
# Copyright (C) 2021 Textualization Software Ltd.
# Distributed under the terms of the Apache Software License 2.0
# http://www.apache.org/licenses/LICENSE-2.0

import random
import copy

from .graph import Graph
from .player import Player
from .drawpiles import DrawPiles
from .definitions import GameDef
from .state import ProjectState
from .projects import Projects
from .policy import Policies

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
        self.phase_actions = None

    def roll_dice(self, rand, num, step):
        result = 0
        for _ in range(num):
            result += rand.randint(1,6)
        log.append( { 'phase' : Game.PHASES[self.state.phase],
                      'step' : Game.STEPS_PER_PHASE[self.state.phase][step],
                      'target' : result,
                      'memo' : 'dice roll {}D6'.format(num),
                      'state' : self.state.to_json() } )
        return result
        

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
            new_loc = self.game_def.players[self.state.player].pick(
                Player.NEW_LOC,
                self.game_def.board.locations,
                rand, self.state.players[self.state.player], self.phase_start_state)
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
            
            drawn = self.game_def.players[self.state.player].pick(
                Player.PILE_DRAW,
                accessible_piles,
                rand, self.state.players[self.state.player], self.phase_start_state)
            self.state.players[self.state.player].cards.append(drawn)
            log.append( { 'phase' : Game.PHASES[self.state.phase],
                          'step' : Game.STEPS_PER_PHASE[self.state.phase][3],
                          'target' : drawn,
                          'memo' : 'first',
                          'state' : self.state.to_json() } )
            accessible_piles = list(set(accessible_piles) - set([drawn]))
            drawn = self.game_def.players[self.state.player].pick(
                Player.PILE_DRAW,
                accessible_piles,
                rand, self.state.players[self.state.player], self.phase_start_state)
            self.state.players[self.state.player].cards.append(drawn)
            log.append( { 'phase' : Game.PHASES[self.state.phase],
                          'step' : Game.STEPS_PER_PHASE[self.state.phase][3],
                          'target' : drawn,
                          'memo' : 'second',
                          'state' : self.state.to_json() } )
            # crisis rising
            self.state.crisis_chips += 1
            log.append( { 'phase' : Game.PHASES[self.state.phase],
                          'step' : Game.STEPS_PER_PHASE[self.state.phase][4],
                          'state' : self.state.to_json() } )
        elif self.state.phase == 1: # activate
            if self.state.player == 0:
                self.phase_start_state = copy.deepcopy(self.state)
                self.phase_actions = list()
            
            # projects

            ## decide whether to start a new project?
            start = False
            if self.state.players[self.state.player].available_project_slots():
                start = self.game_def.players[self.state.player].pick(
                    Player.START_PROJECT_YN,
                    [ True, False ],
                    rand, self.state.players[self.state.player], self.phase_start_state)
                log.append( { 'phase' : Game.PHASES[self.state.phase],
                              'step' : Game.STEPS_PER_PHASE[self.state.phase][0],
                              'target' : start,
                              'memo' : 'start project?',
                              'state' : self.state.to_json() } )
                if start:
                    fix_cat = self.game_def.players[self.state.player].pick(
                        Player.START_PROJECT_FIX_CAT,
                        list(map(lambda x:x[0], Graph.CATEGORIES)),
                        rand, self.state.players[self.state.player], self.phase_start_state)
                    log.append( { 'phase' : Game.PHASES[self.state.phase],
                                  'step' : Game.STEPS_PER_PHASE[self.state.phase][0],
                                  'target' : fix_cat,
                                  'memo' : 'start project: fix category',
                                  'state' : self.state.to_json() } )
                    fix_cat_id = self.state.game_def.graph.category_for_name[fix_cat]
                    fix_node =  self.game_def.players[self.state.player].pick(
                        Player.START_PROJECT_FIX_NODE,
                        list(map(lambda x:self.state.game_def.graph.node_names[x], self.state.game_def.graph.node_classes[fix_cat_id])),
                        rand, self.state.players[self.state.player], self.phase_start_state)
                    log.append( { 'phase' : Game.PHASES[self.state.phase],
                                  'step' : Game.STEPS_PER_PHASE[self.state.phase][0],
                                  'target' : fix_node,
                                  'memo' : 'start project: fix node',
                                  'state' : self.state.to_json() } )
                    fix_node_id = self.state.game_def.graph.name_to_id[fix_node]

                    # type?
                    project_type = self.game_def.players[self.state.player].pick(
                        Player.START_PROJECT_TYPE,
                        Project.TYPES,
                        rand, self.state.players[self.state.player], self.phase_start_state)
                    log.append( { 'phase' : Game.PHASES[self.state.phase],
                                  'step' : Game.STEPS_PER_PHASE[self.state.phase][0],
                                  'target' : project_type,
                                  'memo' : 'start project: choose type',
                                  'state' : self.state.to_json() } )
                    project_type_ = Project.TYPES.index(project_type)

                    if project_type_ in set([Project.BASE, Project.A2]):
                        # trigger cat
                        for f, t, _, _ in Projects.BASE_TABLE:
                            if f[1] == fix_cat_id:
                                trigger_cat, trigger_cat_id = t
                                break
                        trigger_node =  self.game_def.players[self.state.player].pick(
                            Player.START_PROJECT_TRIGGER_NODE,
                            list(map(lambda x:self.state.game_def.graph.node_names[x], self.state.game_def.graph.node_classes[trigger_cat_id])),
                            rand, self.state.players[self.state.player], self.phase_start_state)
                        log.append( { 'phase' : Game.PHASES[self.state.phase],
                                      'step' : Game.STEPS_PER_PHASE[self.state.phase][0],
                                      'target' : trigger_node,
                                      'memo' : 'start project: trigger node',
                                      'state' : self.state.to_json() } )
                        trigger_node_id = self.state.game_def.graph.name_to_id[trigger_node]

                        if project_type_ == Project.BASE:
                            project = self.state.projects.find_project(Project.BASE, fix_node_id, trigger_node_id)
                        else:
                            protected_node =  self.game_def.players[self.state.player].pick(
                                Player.START_PROJECT_PROTECT_NODE,
                                list(map(lambda x:self.state.game_def.graph.node_names[x], self.state.game_def.graph.node_classes[fix_cat_id])),
                                rand, self.state.players[self.state.player], self.phase_start_state)
                            log.append( { 'phase' : Game.PHASES[self.state.phase],
                                          'step' : Game.STEPS_PER_PHASE[self.state.phase][0],
                                          'target' : protect_node,
                                          'memo' : 'start project: protect node',
                                          'state' : self.state.to_json() } )
                            protect_node_id = self.state.game_def.graph.name_to_id[protect_node]
                            project = self.state.projects.find_project(Project.A2, fix_node_id, trigger_node_id, protect_node_id)
                    else:
                        project = self.state.projects.find_project(Project.A1, fix_node_id)
                        
                    log.append( { 'phase' : Game.PHASES[self.state.phase],
                                  'step' : Game.STEPS_PER_PHASE[self.state.phase][0],
                                  'target' : project.name,
                                  'memo' : 'start project',
                                  'state' : self.state.to_json() } )
                    self.state.projects.player_starts(project, self.state.player, self.state.turn)
                    self.state.players[self.state.player].projects.append(project.name)
                    self.state.phase_actions( ( self.state.player, 'START_PROJECT', project ) )
                    started_project = project
            
            ## play cards for any projects
            in_progress = self.state.phase_start_state.projects.projects_for_status(ProjectState.IN_PROGRESS)
            if start:
                in_progress.append(started_project)

            card_choices = list()
            for idx, card in enumerate(self.state.players[self.state.player].cards):
                projects_for_card = list()
                for project in in_progress:
                    missing = set(self.state.projects[project.name]['missing'])
                    if card[1] == 14:
                        for s in missing:
                            projects_for_card.append( (project, s) )
                    elif card[0] in missing:
                        projects_for_card.append( (project, card[0]) )
                for project, suit in projects_for_card
                    card_choices.append( ( card, suit, idx, project.name ) )
                    
            while True:
                if not card_choices:
                    break
                
                if None not in card_choices:
                    card_choices.append( None )

                play_card = self.game_def.players[self.state.player].pick(
                    Player.PLAY_CARD,
                    card_choices,
                    rand, self.state.players[self.state.player], self.phase_start_state)
                if play_card is None:
                    log.append( { 'phase' : Game.PHASES[self.state.phase],
                                  'step' : Game.STEPS_PER_PHASE[self.state.phase][0],
                                  'target' : False,
                                  'memo' : 'play card',
                                  'state' : self.state.to_json() } )
                    break
                log.append( { 'phase' : Game.PHASES[self.state.phase],
                              'step' : Game.STEPS_PER_PHASE[self.state.phase][0],
                              'target' : play_card,
                              'memo' : 'play card',
                              'state' : self.state.to_json() } )

                succeeded = False
                if play_card[0][1] == 14: # joker
                    succeeded = True
                else:
                    value = min(10, play_card[0][1])
                    if self.state.players[self.state.player].resources['$'] > 0:
                        moneys = min(11 - value, self.state.players[self.state.player].resources['$'])
                    consultant = self.game_def.players[self.state.player].pick(
                        Player.CONSULTANT,
                        list(range(moneys + 1)),
                        rand, self.state.players[self.state.player], self.phase_start_state)
                    log.append( { 'phase' : Game.PHASES[self.state.phase],
                                  'step' : Game.STEPS_PER_PHASE[self.state.phase][0],
                                  'target' : consultant,
                                  'memo' : 'consultant fees',
                                  'state' : self.state.to_json() } )
                    self.state.players[self.state.player].resources['$'] -= consultant
                    value += consultant
                    roll = self.roll_dice(rand, 2, 0)
                    if roll <= value:
                        succeed = True
                    if roll == 12:
                        self.state.crisis_chips += 1
                        log.append( { 'phase' : Game.PHASES[self.state.phase],
                                      'step' : Game.STEPS_PER_PHASE[self.state.phase][0],
                                      'target' : self.state.crisis_chips,
                                      'memo' : 'crisis chip',
                                      'state' : self.state.to_json() } )

                if succeeded:
                    self.state.phase_actions( ( self.state.player, 'SUCCESS_SKILL', self.states.projects[play_card[3]], play_card[0] ) )
                else:
                    self.state.phase_actions( ( self.state.player, 'FAILED_SKILL', self.states.projects[play_card[3]], play_card[0]) )
                    
                # closing the project is left to the empathy phase
                self.state.drawpiles.return_card(play_card[0], play_card[1])
                del self.state.players[self.state.player].cards[play_card[2]]
                idx = 0
                while idx < len(card_choices):
                    if card_choices[idx] is None:
                        idx += 1
                    elif card_choices[idx][2] == play_card[2]:
                        del card_choices[idx]
                    else:
                        idx += 1

            
            # policies
            
            ## decide whether to start a new policy?
            start = False
            if self.state.players[self.state.player].available_policy_slots():
                start = self.game_def.players[self.state.player].pick(
                    Player.START_POLICY_YN,
                    [ True, False ],
                    rand, self.state.players[self.state.player], self.phase_start_state)
                log.append( { 'phase' : Game.PHASES[self.state.phase],
                              'step' : Game.STEPS_PER_PHASE[self.state.phase][1],
                              'target' : start,
                              'memo' : 'start policy?',
                              'state' : self.state.to_json() } )
                if start:
                    fix_cat = self.game_def.players[self.state.player].pick(
                        Player.START_POLICY_FIX_CAT,
                        list(map(lambda x:x[0], Graph.CATEGORIES)),
                        rand, self.state.players[self.state.player], self.phase_start_state)
                    log.append( { 'phase' : Game.PHASES[self.state.phase],
                                  'step' : Game.STEPS_PER_PHASE[self.state.phase][1],
                                  'target' : fix_cat,
                                  'memo' : 'start policy: fix category',
                                  'state' : self.state.to_json() } )
                    fix_cat_id = self.state.game_def.graph.category_for_name[fix_cat]
                    fix_node =  self.game_def.players[self.state.player].pick(
                        Player.START_POLICY_FIX_NODE,
                        list(map(lambda x:self.state.game_def.graph.node_names[x], self.state.game_def.graph.node_classes[fix_cat_id])),
                        rand, self.state.players[self.state.player], self.phase_start_state)
                    log.append( { 'phase' : Game.PHASES[self.state.phase],
                                  'step' : Game.STEPS_PER_PHASE[self.state.phase][1],
                                  'target' : fix_node,
                                  'memo' : 'start policy: fix node',
                                  'state' : self.state.to_json() } )
                    fix_node_id = self.state.game_def.graph.name_to_id[fix_node]

                    # type?
                    policy_type = self.game_def.players[self.state.player].pick(
                        Player.START_POLICY_TYPE,
                        Policy.TYPES,
                        rand, self.state.players[self.state.player], self.phase_start_state)
                    log.append( { 'phase' : Game.PHASES[self.state.phase],
                                  'step' : Game.STEPS_PER_PHASE[self.state.phase][1],
                                  'target' : policy_type,
                                  'memo' : 'start policy: choose type',
                                  'state' : self.state.to_json() } )
                    policy_type_ = Policy.TYPES.index(policy_type)

                    if policy_type_ == Policy.BASE:
                        # trigger cat
                        for f, t in Policies.BASE_TABLE:
                            if f[1] == fix_cat_id:
                                trigger_cat, trigger_cat_id = t
                                break
                        trigger_node =  self.game_def.players[self.state.player].pick(
                            Player.START_POLICY_TRIGGER_NODE,
                            list(map(lambda x:self.state.game_def.graph.node_names[x], self.state.game_def.graph.node_classes[trigger_cat_id])),
                            rand, self.state.players[self.state.player], self.phase_start_state)
                        log.append( { 'phase' : Game.PHASES[self.state.phase],
                                      'step' : Game.STEPS_PER_PHASE[self.state.phase][0],
                                      'target' : trigger_node,
                                      'memo' : 'start policy: trigger node',
                                      'state' : self.state.to_json() } )
                        trigger_node_id = self.state.game_def.graph.name_to_id[trigger_node]
                        policy = self.state.policies.find_policy(Policy.BASE, set([fix_node_id]), set([trigger_node_id]))
                    elif policy_type_ == Policy.A:
                        policy = self.state.policies.find_policy(Policy.A, set([fix_node_id]))
                    else:
                        protected_node =  self.game_def.players[self.state.player].pick(
                            Player.START_POLICY_PROTECT_NODE,
                            list(map(lambda x:self.state.game_def.graph.node_names[x], self.state.game_def.graph.node_classes[fix_cat_id])),
                            rand, self.state.players[self.state.player], self.phase_start_state)
                        log.append( { 'phase' : Game.PHASES[self.state.phase],
                                      'step' : Game.STEPS_PER_PHASE[self.state.phase][1],
                                      'target' : protect_node,
                                      'memo' : 'start policy: protect node in same category',
                                      'state' : self.state.to_json() } )
                        protect_node_id = self.state.game_def.graph.name_to_id[protect_node]

                        if policy_type_ == Policy.B:
                            policy = self.state.policies.find_policy(Policy.B, set([fix_node_id], None, set([protected_node_id])))
                        else:
                            all_nodes = list()
                            for node_name in graph.node_names.values():
                                if node_name != protected_node:
                                    all_nodes.append(node_name)
                            
                            protected_node2 =  self.game_def.players[self.state.player].pick(
                                Player.START_POLICY_PROTECT_NODE,
                                all_nodes,
                                rand, self.state.players[self.state.player], self.phase_start_state)
                            log.append( { 'phase' : Game.PHASES[self.state.phase],
                                          'step' : Game.STEPS_PER_PHASE[self.state.phase][1],
                                          'target' : protect_node2,
                                          'memo' : 'start policy: protect node in any category',
                                          'state' : self.state.to_json() } )
                            protect_node2_id = self.state.game_def.graph.name_to_id[protect_node2]
                            policy = self.state.policies.find_policy(Policy.C, set([fix_node_id], None, set([protected_node_id, protected_node2_id])))
                
                    log.append( { 'phase' : Game.PHASES[self.state.phase],
                                  'step' : Game.STEPS_PER_PHASE[self.state.phase][1],
                                  'target' : policy.name,
                                  'memo' : 'start policy',
                                  'state' : self.state.to_json() } )
                    self.state.policy.player_starts(policy, self.state.player, self.state.turn, self.state.quorum())
                    self.state.players[self.state.player].policies.append(policy.name)
                    self.state.phase_actions( ( self.state.player, 'START_POLICY', policy ) )
                    started_policy = policy

            ## pass power for any policies
            policy_choices = self.state.phase_start_state.policies.policies_for_status(ProjectState.IN_PROGRESS) + \
                self.state.phase_start_state.policies.policies_for_status(ProjectState.PASSED)
            if start:
                policy_choices.append(started_policy)

            policy_choices = list(map(lambda x:x.name, policy_choices))

            while True
                if self.state.players[self.state.player].resources['!'] == 0:
                    break

                if None not in policy_choices:
                    policy_choices.append( None )
                
                if len(policy_choices) <= 1:
                    break
                
                chosen_policy = self.game_def.players[self.state.player].pick(
                    Player.POLICY_TO_EMPOWER,
                    policy_choices,
                    rand, self.state.players[self.state.player], self.phase_start_state)
                if chosen_policy is None:
                    log.append( { 'phase' : Game.PHASES[self.state.phase],
                                  'step' : Game.STEPS_PER_PHASE[self.state.phase][1],
                                  'target' : False,
                                  'memo' : 'empower a policy',
                                  'state' : self.state.to_json() } )
                    break
                if chosen_policy == started_policy.name:
                    powers = min(self.state.players[self.state.player].resources['!'], self.state.policies[chosen_policy]['missing_power'])
                else:
                    powers = min(self.state.players[self.state.player].resources['!'], self.phase_start_state.policies[chosen_policy]['missing_power'])
                powers = list(range(1, powers + 1))
                chosen_power = self.game_def.players[self.state.player].pick(
                    Player.POWER_AMOUNT,
                    powers,
                    rand, self.state.players[self.state.player], self.phase_start_state)
                
                self.state.players[self.state.player].resources['!'] -= chosen_power
                self.state.policies[chosen_policy]['missing_power'] -=  chosen_power
                del policy_choices[policy_choices.index(chosen_policy)]
                self.state.phase_actions( ( self.state.player, 'EMPOWER_POLICY', self.state.policies[chosen_policy]['policy'], chosen_power ) )
                log.append( { 'phase' : Game.PHASES[self.state.phase],
                              'step' : Game.STEPS_PER_PHASE[self.state.phase][1],
                              'target' : chosen_power,
                              'memo' : 'empower policy "{}"'.format(chosen_policy),
                              'state' : self.state.to_json() } )
                # policy effects, etc are left for the end

            # research
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

