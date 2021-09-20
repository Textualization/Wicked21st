# -*- coding: utf-8 -*-
# Copyright (C) 2021 Textualization Software Ltd.
# Distributed under the terms of the Apache Software License 2.0
# http://www.apache.org/licenses/LICENSE-2.0

import random

from .graph import Graph
from .player import Player, PlayerState
from .drawpiles import DrawPiles
from .definitions import GameDef
from .state import GraphState, ProjectState, PolicyState, TechTreeState, BoardState
from .project import Projects, Project
from .policy import Policies, Policy
from .techtree import Tech, TechTree
from .tojson import to_json

class GameState:
    def __init__(self,
                 turn: int,
                 phase: int,
                 player: int,
                 leader: int,
                 game_def: GameDef,
                 players_state: list,
                 crisis_chips: int,
                 graph_state: GraphState,
                 board_state: BoardState,
                 techtree_state: TechTreeState,
                 project_state: ProjectState,
                 policy_state: PolicyState,
                 drawpiles_state: DrawPiles):
        self.turn = turn
        self.phase = phase
        self.player = player
        self.leader = leader
        self.game = game_def
        self.players = players_state
        self.crisis_chips = crisis_chips
        self.graph = graph_state
        self.board = board_state
        self.projects = project_state
        self.tech = techtree_state
        self.policies = policy_state
        self.drawpiles = drawpiles_state

    def quorum(self):
        return len(self.players) // 2 + 1

    def to_json(self):
        return { 'players' : to_json(self.players),
                 'player' : self.player,
                 'turn' : self.turn,
                 'phase' : self.phase,
                 'leader': self.leader,
                 'crisis_chips' : self.crisis_chips,
                 'board' : self.board.to_json(),
                 'graph' : self.graph.to_json(),
                 'tech' : self.tech.to_json(),
                 'projects' : self.projects.to_json(),
                 'policy' : self.policies.to_json(),
                 'piles' : self.drawpiles.to_json() }

    def copy(self):
        return GameState(self.turn, self.phase, self.player, self.leader,
                         self.game, list(map(lambda x:x.copy(), self.players)),  self.crisis_chips,
                         self.graph.copy(), self.board.copy(),
                         self.tech.copy(), self.projects.copy(), self.policies.copy(),
                         self.drawpiles.copy())

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
                        'REFLECT' : [ 'EMPATHIZING' ],
                        'END': [ 'FINALIZING',
                                 'CRISIS ROLLING' ]
                       }

    A_START_PROJECT  = 'START_PROJECT'
    A_SUCCESS_SKILL  = 'SUCCESS_SKILL'
    A_FAILED_SKILL   = 'FAILED_SKILL'
    A_START_POLICY   = 'START_POLICY'
    A_EMPOWER_POLICY = 'EMPOWER_POLICY'
    A_START_RESEARCH = 'START_RESEARCH'
    A_SKILL_RESEARCH = 'SKILL_RESEARCH'
    A_FUND_RESEARCH  = 'FUND_RESEARCH'

    L_DICE_ROLL           = 'Dice roll {}D6: {}'
    L_MOVED               = 'Moved'
    L_POWER_DRAWN         = 'Power drawn'
    L_MONEY_DRAWN         = 'Money drawn'
    L_CARD_DRAWN          = 'Card drawn: {}'
    L_PROJECT_TYPE        = 'Start project: type'
    L_PROJECT_CAT         = 'Start project: fix category'
    L_PROJECT_NODE        = 'Start project: fix problem'
    L_PROJECT_TRIGGER     = 'Start project: trade-off problem'
    L_PROJECT_STARTED     = 'Project started'
    L_SKILL_PROJECT       = 'Skill for project'
    L_USING_TECH          = 'Using tech "{}"'
    L_CONSULTANT_FEES     = 'Consultant fees'
    L_CHIP_ADDED          = 'Added a crisis chip'
    L_POLICY_TYPE         = 'Start policy: type'
    L_POLICY_CAT          = 'Start policy: fix category'
    L_POLICY_NODE         = 'Start policy: fix problem'
    L_POLICY_PROTECT_SAME = 'Start policy: protect node in same category'
    L_POLICY_PROTECT_ANY  = 'Start policy: protect node in any category'
    L_POLICY_STARTED      = 'Policy started'
    L_POLICY_TO_EMPOWER   = 'Chosen policy to empower'
    L_EMPOWER_POLICY      = 'Empower policy "{}"'
    L_START_RESEARCH      = 'Start researching'
    L_SKILL_FOR_RESEARCH  = 'Skill for research'
    L_FUNDS_FOR_RESEARCH  = 'Funds for research'
    L_EMPATHIZE           = 'Empathize'
    L_OVERSKILLED         = 'Tech project overskilled by {}'
    L_OVERFUNDED          = 'Tech project overfunded by {}'
    L_RESEARCH_CYCLE      = 'Research cycle finished, remain: {}'
    L_RESEARCHED          = 'Tech researched'
    L_AUTO_PROTECTED      = 'Problem auto-protected'
    L_PROTECTED           = 'Problem protected'
    L_FUNDED_NOT_SKILLED  = 'Tech funded but not skilled, ignoring'
    L_SKILLED_NOT_FUNDED  = 'Tech skilled but not funded, ignoring'
    L_PROJECT_ABANDONED   = 'Project abandoned'
    L_PROJECT_OVERSKILLED = 'Project overskilled for "{}"'
    L_PROJECT_FINISHED    = 'Project finished'
    L_CRISIS_FIX_PROJECT  = 'Crisis resolved (project: {})'
    L_CRISIS_TRIGGERED    = 'Now in crisis (trade-off from project: {})'
    L_PROT_LOSS_PROJECT   = 'Lost protection (trade-off from project: {})'
    L_CHIP_PROJECT = 'Crisis chip (trade-off from project: {})'
    L_POLICY_ABANDONED    = 'Policy abandoned'
    L_POLICY_OVERPOWERED  = 'Policy overpowered by {}'
    L_POLICY_PASSED       = 'Policy passed'
    L_POLICY_IN_ACTION    = 'Policy  in action'
    L_CRISIS_FIX_POLICY   = 'Crisis resolved (policy: {})'
    L_POLICY_PROTECT      = 'Problem protected (policy: {})'
    L_CHIP_FULL_CAT       = 'Crisis chip: full category'
    L_CRISIS_CAT          = 'Category for crisis'
    L_CHIP_SATURATED      = 'Crisis chip: overwhelmed problem'
    L_CRISIS_NODE         = 'Problem for crisis'
    L_CRISIS_ROLL         = 'Crisis roll for node "{}"'
    L_CRISIS_AVERTED      = 'Crisis averted'
    L_IN_CRISIS           = 'Now in crisis'
    L_PROT_LOSS           = 'Lost protection'
    L_IN_CRISIS_CASCADE   = 'Now in crisis (cascaded from: {})'
    L_PROT_LOSS_CASCADE   = 'Lost protection (cascaded from: {})'
    
    
    def __init__(self, game_def: GameDef, players: list):
        self.game_def = game_def
        self.players = players
        self.log = list()
        self.phase_start_state = None
        self.phase_actions = None

    def roll_dice(self, num, player, memo, rand, step):
        result = 0
        for idx in range(num):
            result += self.players[player].roll("{}, {} of {}".format(memo, idx+1, num), rand, 6)
        self.log.append( { 'phase' : Game.PHASES[self.state.phase],
                           'step' : Game.STEPS_PER_PHASE[Game.PHASES[self.state.phase]][step],
                           'target' : result,
                           'memo' : Game.L_DICE_ROLL, 'args' : [ num, memo ],
                           'state' : self.state.to_json() } )
        return result
        

    def start(self, rand):
        self.finished = False
        drawpiles = DrawPiles(rand)
        player_state = [ PlayerState(p, { '!': 0, '$': 0 }, list(),
                                     p.pick(Player.INIT_LOC, self.game_def.board.locations, rand)) for p in self.players ]
        graph_state = self.game_def.game_init.graph.copy()
        board_state = BoardState(self.game_def.board)
        for idx, p in enumerate(player_state):
            board_state[p.location] = board_state.get(p.location, set()).union(set([ self.players[idx].ordering ]))
            
        self.state = GameState(0, 0, 0, 0,
                               self.game_def,
                               player_state, 0, graph_state, board_state,
                               TechTreeState(self.game_def.tech),
                               ProjectState(self.game_def.projects),
                               PolicyState(self.game_def.policies),
                               drawpiles)

    def advance(self):
        "Returns True is the game has ended"
        if len(self.state.graph.are_in_crisis()) == len(self.game_def.graph):
            self.finished = True
        else:
            self.state.player += 1
            if self.state.player == self.game_def.num_players:
                self.state.player = 0
                self.state.phase += 1
                if self.state.phase == len(Game.PHASES):
                    self.state.phase = 0
                    self.state.turn += 1
                    self.state.leader = (self.state.leader + 1) % self.game_def.num_players
        return self.finished

    def cascade(self, node, visited=None):
        "A node in crisis has been selected, deal with it. Returns the activated nodes."
        if visited is None:
            visited = list()
        if node in visited:
            return list()
        visited.append(node)
        result = list()
        outlinks = list(self.game_def.graph.outlinks[node])
        for outlink in outlinks:
            outlinkn = self.game_def.graph.node_names[outlink]
            if self.state.graph[outlinkn]['status'] != GraphState.IN_CRISIS:
                result.append(outlink)
        if result:
            return result
        # recurse
        for outlink in outlinks:
            result = result + self.cascade(outlink, list(visited))
            
        return result

    def step(self, rand):
        phase = Game.PHASES[self.state.phase]
        if self.state.phase == 0: # engage
            if self.state.player == 0:
                self.phase_start_state = self.state.copy()

            # moving
            new_loc = self.players[self.state.player].pick(
                Player.NEW_LOC,
                self.game_def.board.locations,
                rand, self.state.players[self.state.player], self.phase_start_state)
            self.state.board[self.state.players[self.state.player].location] -= set([self.state.player])
            self.state.players[self.state.player].location = new_loc
            self.state.board[new_loc] = self.state.board.get(new_loc, set()).union(set([self.state.player]))
            
            self.log.append( { 'phase' : phase,
                               'step' : Game.STEPS_PER_PHASE[phase][0],
                               'target' : new_loc,
                               'memo' : Game.L_MOVED,
                               'state' : self.state.to_json() } )
            # drawing power
            drawn = 1 + \
                (1 if self.game_def.board.resources[new_loc] == '!' else 0) + \
                (1 if self.players[self.state.player].player_class.resource == '!' else 0)
            self.state.players[self.state.player].resources['!'] += drawn
            self.log.append( { 'phase' : phase,
                               'step' : Game.STEPS_PER_PHASE[phase][1],
                               'target' : drawn,
                               'memo' : Game.L_POWER_DRAWN,
                               'state' : self.state.to_json() } )
            # drawing money
            drawn = max(0, 5 - len(self.state.graph.are_in_crisis('ECONOMIC'))) + 2 *  (
                (1 if self.game_def.board.resources[new_loc] == '$' else 0) + \
                (1 if self.players[self.state.player].player_class.resource == '$' else 0))
            self.state.players[self.state.player].resources['$'] += drawn
            self.log.append( { 'phase' : phase,
                               'step' : Game.STEPS_PER_PHASE[phase][2],
                               'target' : drawn,
                               'memo' : Game.L_MONEY_DRAWN,
                               'state' : self.state.to_json() } )
            # draw cards
            accessible_piles = set([self.players[self.state.player].player_class.suit_a, self.players[self.state.player].player_class.suit_b ])
            accessible_piles.add(self.game_def.board.suits[new_loc])
            accessible_piles = list(accessible_piles)
            
            draw_pile = self.players[self.state.player].pick(
                Player.PILE_DRAW,
                accessible_piles,
                rand, self.state.players[self.state.player], self.phase_start_state)
            drawn = self.state.drawpiles.draw(draw_pile, rand)
            self.state.players[self.state.player].cards.append(drawn)
            self.log.append( { 'phase' : phase,
                               'step' : Game.STEPS_PER_PHASE[phase][3],
                               'target' : drawn,
                               'memo' : Game.L_CARD_DRAWN, 'args' : [ 1 ],
                               'state' : self.state.to_json() } )
            accessible_piles = list(set(accessible_piles) - set([draw_pile]))
            draw_pile = self.players[self.state.player].pick(
                Player.PILE_DRAW,
                accessible_piles,
                rand, self.state.players[self.state.player], self.phase_start_state)
            drawn = self.state.drawpiles.draw(draw_pile, rand)
            self.state.players[self.state.player].cards.append(drawn)
            self.log.append( { 'phase' : phase,
                          'step' : Game.STEPS_PER_PHASE[phase][3],
                          'target' : drawn,
                          'memo' : Game.L_CARD_DRAWN, 'args' : [ 2 ],
                          'state' : self.state.to_json() } )
            # crisis rising
            self.state.crisis_chips += 1
            self.log.append( { 'phase' : phase,
                               'step' : Game.STEPS_PER_PHASE[phase][4],
                               'state' : self.state.to_json() } )
        elif self.state.phase == 1: # activate
            if self.state.player == 0:
                self.phase_start_state = self.state.copy()
                self.phase_actions = list()
            
            # projects

            ## decide whether to start a new project?
            start = False
            if self.state.players[self.state.player].available_project_slots():
                project_type = self.players[self.state.player].pick(
                    Player.START_PROJECT,
                    Project.TYPES + [ None ],
                    rand, self.state.players[self.state.player], self.phase_start_state)
                self.log.append( { 'phase' : phase,
                                   'step' : Game.STEPS_PER_PHASE[phase][0],
                                   'target' : project_type,
                                   'memo' : Game.L_PROJECT_TYPE,
                                   'state' : self.state.to_json() } )
                start = project_type is not None
                if start:
                    fix_cat = self.players[self.state.player].pick(
                        Player.START_PROJECT_FIX_CAT,
                        list(map(lambda x:x[0], Graph.CATEGORIES)),
                        rand, self.state.players[self.state.player], self.phase_start_state)
                    self.log.append( { 'phase' : phase,
                                  'step' : Game.STEPS_PER_PHASE[phase][0],
                                  'target' : fix_cat,
                                  'memo' : Game.L_PROJECT_CAT,
                                  'state' : self.state.to_json() } )
                    fix_cat_id = self.game_def.graph.category_for_name[fix_cat]
                    fix_node =  self.players[self.state.player].pick(
                        Player.START_PROJECT_FIX_NODE,
                        list(map(lambda x:self.game_def.graph.node_names[x], self.game_def.graph.node_classes[fix_cat_id])),
                        rand, self.state.players[self.state.player], self.phase_start_state)
                    self.log.append( { 'phase' : phase,
                                       'step' : Game.STEPS_PER_PHASE[phase][0],
                                       'target' : fix_node,
                                       'memo' : Game.L_PROJECT_NODE,
                                       'state' : self.state.to_json() } )
                    fix_node_id = self.game_def.graph.name_to_id[fix_node]

                    project_type_ = Project.TYPES.index(project_type)

                    if project_type_ == Project.BASE:
                        # trigger cat
                        for f, t, _, _ in Projects.BASE_TABLE:
                            if f[1] == fix_cat_id:
                                trigger_cat, trigger_cat_id = t
                                break
                        trigger_node =  self.players[self.state.player].pick(
                            Player.START_PROJECT_TRIGGER_NODE,
                            list(map(lambda x:self.game_def.graph.node_names[x], self.game_def.graph.node_classes[trigger_cat_id])),
                            rand, self.state.players[self.state.player], self.phase_start_state)
                        self.log.append( { 'phase' : phase,
                                           'step' : Game.STEPS_PER_PHASE[phase][0],
                                           'target' : trigger_node,
                                           'memo' : Game.L_PROJECT_TRIGGER,
                                           'state' : self.state.to_json() } )
                        trigger_node_id = self.game_def.graph.name_to_id[trigger_node]

                        project = self.state.projects.find_project(Project.BASE, fix_node_id, trigger_node_id)
                    else:
                        project = self.state.projects.find_project(Project.A, fix_node_id)
                        
                    self.log.append( { 'phase' : phase,
                                       'step' : Game.STEPS_PER_PHASE[phase][0],
                                       'target' : project.name,
                                       'memo' : Game.L_PROJECT_STARTED,
                                       'state' : self.state.to_json() } )
                    self.state.projects.player_starts(project, self.state.player, self.state.turn)
                    self.state.players[self.state.player].projects.append(project.name)
                    self.phase_actions.append( ( self.state.player, Game.A_START_PROJECT, project ) )
                    started_project = project
            
            ## play cards for any projects
            in_progress = self.phase_start_state.projects.projects_for_status(ProjectState.IN_PROGRESS)
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
                for project, suit in projects_for_card:
                    card_choices.append( ( card, suit, idx, project.name ) )
                    
            while True:
                if None not in card_choices:
                    card_choices.append( None )
                if len(card_choices) <= 1:
                    break

                play_card = self.players[self.state.player].pick(
                    Player.PLAY_CARD,
                    card_choices,
                    rand, self.state.players[self.state.player], self.phase_start_state)
                self.log.append( { 'phase' : phase,
                                   'step' : Game.STEPS_PER_PHASE[phase][0],
                                   'target' : play_card,
                                   'memo' : Game.L_SKILL_PROJECT,
                                   'state' : self.state.to_json() } )
                if play_card is None:
                    break

                succeeded = False
                if play_card[0][1] == 14: # joker
                    succeeded = True
                    roll  = -1
                    value = -1
                else:
                    value = min(10, play_card[0][1])
                    base_tech = self.state.tech.find_tech(Tech.BASE, play_card[0][0])
                    expanded_tech = self.state.tech.find_tech(Tech.A, play_card[0][0])
                    
                    if self.state.tech.status(base_tech.name) == TechTreeState.RESEARCHED:
                        value += 1
                        self.log.append( { 'phase' : phase,
                                           'step' : Game.STEPS_PER_PHASE[phase][0],
                                           'target' : 1,
                                           'memo' : Game.L_USING_TECH, 'args': [ base_tech.name ],
                                           'state' : self.state.to_json() } )
                    if self.state.tech.status(expanded_tech.name) == TechTreeState.RESEARCHED:
                        base = value
                        value = min(11, value + 2)
                        if base > value:
                            self.log.append( { 'phase' : phase,
                                               'step' : Game.STEPS_PER_PHASE[phase][0],
                                               'target' : (value - base),
                                               'memo' : Game.L_USING_TECH, 'args': [ expanded_tech.name ],
                                               'state' : self.state.to_json() } )
                        
                    if value < 11 and self.state.players[self.state.player].resources['$'] > 0:
                        moneys = min(11 - value, self.state.players[self.state.player].resources['$'])
                        
                        consultant = self.players[self.state.player].pick(
                            Player.CONSULTANT,
                            list(range(moneys + 1)),
                            rand, self.state.players[self.state.player], self.phase_start_state)
                        self.log.append( { 'phase' : phase,
                                           'step' : Game.STEPS_PER_PHASE[phase][0],
                                           'target' : consultant,
                                           'memo' : Game.L_CONSULTANT_FEES,
                                           'state' : self.state.to_json() } )
                        self.state.players[self.state.player].resources['$'] -= consultant
                        value += consultant
                        
                    roll = self.roll_dice(2, self.state.player, 'skill check', rand, 0)
                    if roll <= value:
                        succeed = True
                    if roll == 12:
                        self.state.crisis_chips += 1
                        self.log.append( { 'phase' : phase,
                                           'step' : Game.STEPS_PER_PHASE[phase][0],
                                           'target' : 1,
                                           'memo' : Game.L_CHIP_ADDED,
                                           'state' : self.state.to_json() } )

                if succeeded:
                    self.phase_actions.append( ( self.state.player, Game.A_SUCCESS_SKILL,
                                                 self.state.projects[play_card[3]]['project'], play_card[0], roll, value ) )
                else:
                    self.phase_actions.append( ( self.state.player, Game.A_FAILED_SKILL,
                                                 self.state.projects[play_card[3]]['project'], play_card[0], roll, value ) )
                    
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
                        if card_choices[idx][2] > play_card[2]:
                            l = list(card_choices[idx])
                            l[2] -= 1
                            card_choices[idx] = tuple(l)
                        idx += 1

            
            # policies
            
            ## decide whether to start a new policy?
            start = False
            if self.state.players[self.state.player].available_policy_slots():
                policy_type = self.players[self.state.player].pick(
                    Player.START_POLICY,
                    Policy.TYPES + [ None ],
                    rand, self.state.players[self.state.player], self.phase_start_state)
                self.log.append( { 'phase' : phase,
                                   'step' : Game.STEPS_PER_PHASE[phase][1],
                                   'target' : policy_type,
                                   'memo' : Game.L_POLICY_TYPE,
                                   'state' : self.state.to_json() } )
                start = policy_type is not None
                if start:
                    fix_cat = self.players[self.state.player].pick(
                        Player.START_POLICY_FIX_CAT,
                        list(map(lambda x:x[0], Graph.CATEGORIES)),
                        rand, self.state.players[self.state.player], self.phase_start_state)
                    self.log.append( { 'phase' : phase,
                                       'step' : Game.STEPS_PER_PHASE[phase][1],
                                       'target' : fix_cat,
                                       'memo' : Game.L_POLICY_CAT,
                                       'state' : self.state.to_json() } )
                    fix_cat_id = self.game_def.graph.category_for_name[fix_cat]
                    fix_node =  self.players[self.state.player].pick(
                        Player.START_POLICY_FIX_NODE,
                        list(map(lambda x:self.game_def.graph.node_names[x], self.game_def.graph.node_classes[fix_cat_id])),
                        rand, self.state.players[self.state.player], self.phase_start_state)
                    self.log.append( { 'phase' : phase,
                                       'step' : Game.STEPS_PER_PHASE[phase][1],
                                       'target' : fix_node,
                                       'memo' : Game.L_POLICY_NODE,
                                       'state' : self.state.to_json() } )
                    fix_node_id = self.game_def.graph.name_to_id[fix_node]

                    policy_type_ = Policy.TYPES.index(policy_type)

                    if policy_type_ == Policy.A: # remove-tradeoff
                        policy = self.state.policies.find_policy(Policy.A, set([fix_node_id]))
                    else:
                        protected_node =  self.players[self.state.player].pick(
                            Player.START_POLICY_PROTECT_NODE,
                            list(map(lambda x:self.game_def.graph.node_names[x], self.game_def.graph.node_classes[fix_cat_id])),
                            rand, self.state.players[self.state.player], self.phase_start_state)
                        self.log.append( { 'phase' : phase,
                                           'step' : Game.STEPS_PER_PHASE[phase][1],
                                           'target' : protected_node,
                                           'memo' : Game.L_POLICY_PROTECT_SAME,
                                           'state' : self.state.to_json() } )
                        protected_node_id = self.game_def.graph.name_to_id[protected_node]

                        if policy_type_ == Policy.B:
                            policy = self.state.policies.find_policy(Policy.B, set([fix_node_id]), None, set([protected_node_id]))
                        else:
                            all_nodes = list()
                            for node_name in self.game_def.graph.node_names.values():
                                if node_name != protected_node:
                                    all_nodes.append(node_name)
                            
                            protected_node2 =  self.players[self.state.player].pick(
                                Player.START_POLICY_PROTECT_NODE,
                                all_nodes,
                                rand, self.state.players[self.state.player], self.phase_start_state)
                            self.log.append( { 'phase' : phase,
                                               'step' : Game.STEPS_PER_PHASE[phase][1],
                                               'target' : protected_node2,
                                               'memo' : Game.L_POLICY_PROTECT_ANY,
                                               'state' : self.state.to_json() } )
                            protected_node2_id = self.game_def.graph.name_to_id[protected_node2]
                            policy = self.state.policies.find_policy(Policy.C, set([fix_node_id]), None, set([protected_node_id, protected_node2_id]))
                
                    self.log.append( { 'phase' : phase,
                                       'step' : Game.STEPS_PER_PHASE[phase][1],
                                       'target' : policy.name,
                                       'memo' : Game.L_POLICY_STARTED,
                                       'state' : self.state.to_json() } )
                    self.state.policies.player_starts(policy, self.state.player, self.state.turn, self.state.quorum())
                    self.state.players[self.state.player].policies.append(policy.name)
                    self.phase_actions.append( ( self.state.player, Game.A_START_POLICY, policy ) )
                    started_policy = policy

            ## pass power for any policies
            policy_choices = self.phase_start_state.policies.policies_for_status(PolicyState.IN_PROGRESS) + \
                self.phase_start_state.policies.policies_for_status(PolicyState.PASSED)
            if start:
                policy_choices.append(started_policy)

            policy_choices = list(map(lambda x:x.name, policy_choices))

            while True:
                if self.state.players[self.state.player].resources['!'] == 0:
                    break

                if None not in policy_choices:
                    policy_choices.append( None )
                
                if len(policy_choices) <= 1:
                    break
                
                chosen_policy = self.players[self.state.player].pick(
                    Player.POLICY_TO_EMPOWER,
                    policy_choices,
                    rand, self.state.players[self.state.player], self.phase_start_state)
                if chosen_policy is None:
                    self.log.append( { 'phase' : phase,
                                       'step' : Game.STEPS_PER_PHASE[phase][1],
                                       'target' : None,
                                       'memo' : Game.L_POLICY_TO_EMPOWER,
                                       'state' : self.state.to_json() } )
                    break
                chosen_power = None
                
                if start and chosen_policy == started_policy.name:
                    powers = min(self.state.players[self.state.player].resources['!'],
                                 self.state.policies[chosen_policy]['missing_power'])
                else:
                    if self.phase_start_state.policies.status(chosen_policy) == PolicyState.PASSED:
                        chosen_power = 1
                    else:
                        powers = min(self.state.players[self.state.player].resources['!'],
                                     self.phase_start_state.policies[chosen_policy]['missing_power'])
                if chosen_power is None:
                    if powers == 1:
                        chosen_power = 1
                    else:
                        powers = list(range(1, powers + 1))
                        chosen_power = self.players[self.state.player].pick(
                            Player.POWER_AMOUNT,
                            powers,
                            rand, self.state.players[self.state.player], self.phase_start_state)
                    
                self.log.append( { 'phase' : phase,
                                   'step' : Game.STEPS_PER_PHASE[phase][1],
                                   'target' : chosen_power,
                                   'memo' : Game.L_EMPOWER_POLICY, 'args': [ chosen_policy ],
                                   'state' : self.state.to_json() } )
                
                self.state.players[self.state.player].resources['!'] -= chosen_power
                self.state.policies[chosen_policy]['missing_power'] -=  chosen_power
                del policy_choices[policy_choices.index(chosen_policy)]
                self.phase_actions.append( ( self.state.player, Game.A_EMPOWER_POLICY,
                                             self.state.policies[chosen_policy]['policy'], chosen_power ) )
                # policy effects, etc are left for the end

            # research
            start = False
            if self.state.players[self.state.player].available_research_slots():
                boundary = self.state.tech.research_boundary()
                chosen_tech = self.players[self.state.player].pick(
                    Player.START_RESEARCH,
                    list(map(lambda x:x.name, boundary)) + [ None ],
                    rand, self.state.players[self.state.player], self.phase_start_state)
                self.log.append( { 'phase' : phase,
                                   'step' : Game.STEPS_PER_PHASE[phase][2],
                                   'target' : chosen_tech,
                                   'memo' : Game.L_START_RESEARCH,
                                   'state' : self.state.to_json() } )
                start = chosen_tech is not None
                if start:
                    tech = self.state.tech[chosen_tech]['tech']
                    self.state.tech.player_starts(tech, self.state.player, self.state.turn)
                    self.state.players[self.state.player].tech.append(tech.name)
                    self.phase_actions.append( ( self.state.player, Game.A_START_RESEARCH, tech ) )
                    started_tech = tech

            researching = self.state.tech.techs_for_status(TechTreeState.IN_PROGRESS)
            if start:
                researching.append(started_tech)

            ## cards for research
            cards_for_tech = list()
            for idx, card in enumerate(self.state.players[self.state.player].cards):
                for tech in researching:
                    if card[0] == tech.suit or card[1] == 14:
                        cards_for_tech.append( (tech.name, card, idx, tech.suit) )
                        
            while True:
                if None not in cards_for_tech:
                    cards_for_tech.append( None )
                
                if len(cards_for_tech) <= 1:
                    break
                
                chosen_card_for_tech = self.players[self.state.player].pick(
                    Player.CARD_FOR_RESEARCH,
                    cards_for_tech,
                    rand, self.state.players[self.state.player], self.phase_start_state)
                self.log.append( { 'phase' : phase,
                                   'step' : Game.STEPS_PER_PHASE[phase][0],
                                   'target' : chosen_card_for_tech,
                                   'memo' : Game.L_SKILL_FOR_RESEARCH,
                                   'state' : self.state.to_json() } )
                if chosen_card_for_tech is None:
                    break
                self.phase_actions.append( ( self.state.player, Game.A_SKILL_RESEARCH,
                                             chosen_card_for_tech[1], self.state.tech[chosen_card_for_tech[0]] ) )
                self.state.drawpiles.return_card(chosen_card_for_tech[1], chosen_card_for_tech[3])
                del self.state.players[self.state.player].cards[chosen_card_for_tech[2]]
                
                idx = 0
                while idx < len(cards_for_tech):
                    if cards_for_tech[idx] is None:
                        idx += 1
                    elif cards_for_tech[idx][2] == chosen_card_for_tech[2]:
                        del cards_for_tech[idx]
                    else:
                        if cards_for_tech[idx][2] > chosen_card_for_tech[2]:
                            l = list(cards_for_tech[idx])
                            l[2] -= 1
                            cards_for_tech[idx] = tuple(l)
                        idx += 1
                
            ## funds for research
            to_fund = researching

            while True:
                if self.state.players[self.state.player].resources['$'] == 0:
                    break
                if None not in to_fund:
                    to_fund.append( None )

                if len(to_fund) <= 1:
                    break

                chosen_to_fund = self.players[self.state.player].pick(
                    Player.FUND_RESEARCH,
                    list(map(lambda x:None if x is None else x.name, to_fund)),
                    rand, self.state.players[self.state.player], self.phase_start_state)
                self.log.append( { 'phase' : phase,
                                   'step' : Game.STEPS_PER_PHASE[phase][0],
                                   'target' : chosen_to_fund,
                                   'memo' : Game.L_FUNDS_FOR_RESEARCH,
                                   'state' : self.state.to_json() } )
                if chosen_to_fund is None:
                    break
                self.phase_actions.append( ( self.state.player, Game.A_FUND_RESEARCH, self.state.tech[chosen_to_fund] ) )
                self.state.players[self.state.player].resources['$'] -= 1
                
                for idx, tech in enumerate(to_fund):
                    if tech is not None and tech.name == chosen_to_fund:
                        break
                del to_fund[idx]

        elif self.state.phase == 2: # reflect
            #EMPATHIZING
            succeeded = [ (p[2], p[3], idx, p[4], p[5])       for idx, p in enumerate(self.phase_actions)
                          if p[0] == self.state.player and p[1] == Game.A_SUCCESS_SKILL ]
            failed    = [ (p[0], p[2], p[3], idx, p[4], p[5]) for idx, p in enumerate(self.phase_actions)
                          if p[0] != self.state.player and p[1] == Game.A_FAILED_SKILL ]
            empath_pairs = list()
            for sproject, scard, sidx, sroll, svalue in succeeded:
                if sroll < 0: # joker
                    continue
                for player, fproject, fcard, fidx, froll, fvalue in failed:
                    if scard[0] == fcard[0] and sroll <= fvalue and froll <= svalue: # potential empath
                        empath_pairs.append( ( sproject.name, fproject.name, player,
                                               self.players[player].name, scard, fcard, sidx, fidx, sroll, froll ) )
            while True:
                if None not in empath_pairs:
                    empath_pairs.append( None )
                if len(empath_pairs) <= 1:
                    break
                empathize = self.players[self.state.player].pick(
                    Player.EMPATHIZE,
                    empath_pairs,
                    rand, self.state.players[self.state.player], self.phase_start_state)
                self.log.append( { 'phase' : phase,
                                   'step' : Game.STEPS_PER_PHASE[phase][0],
                                   'target' : empathize,
                                   'memo' : Game.L_EMPATHIZE,
                                   'state' : self.state.to_json() } )
                if empathize is None:
                    break
                l = list(self.phase_actions[empathize[6]])
                l[4] = empathize[9]
                self.phase_actions[empathize[6]] = tuple(l)
                l = list(self.phase_actions[empathize[7]])
                l[1] = Game.A_SUCCESS_SKILL
                l[4] = empathize[8]
                self.phase_actions[empathize[7]] = tuple(l)
                
                idx = 0
                while idx < len(empath_pairs):
                    if empath_pairs[idx] is None:
                        idx += 1
                    elif empath_pairs[idx][6] == empathize[6] or empath_pairs[idx][7] == empathize[7]:
                        del empath_pairs[idx]
                    else:
                        idx += 1

        else: # the end
            if self.state.player != self.state.leader:
                pass
            else:
                # FINALIZING

                ## see if any of the techs was researched and apply its actions
                for tech in self.state.tech.techs_for_status(TechTreeState.IN_PROGRESS):
                    # got skill and funds this turn?
                    skills = 0
                    funds  = 0
                    for act in self.phase_actions:
                        if act[1] == Game.A_SKILL_RESEARCH and act[2] == tech:
                            skills += 1
                        elif act[1] == Game.A_FUND_RESEARCH and act[2] == tech:
                            funds  += 1
                    if skills == 0 and funds == 0:
                        continue
                    if skills >= 1 and funds >= 1:
                        if skills >= 0:
                            self.log.append( { 'phase' : phase,
                                               'step' : Game.STEPS_PER_PHASE[phase][0],
                                               'target' : tech.name,
                                               'memo' : Game.L_OVERSKILLED, 'args' : [ skills - 1],
                                               'state' : self.state.to_json() } )
                        if funds >= 0:
                            self.log.append( { 'phase' : phase,
                                               'step' : Game.STEPS_PER_PHASE[phase][0],
                                               'target' : tech.name,
                                               'memo' : Game.L_OVERFUNDED, 'args' : [ funds - 1],
                                               'state' : self.state.to_json() } )
                        self.state.tech[tech.name]['missing_turns'] -= 1
                        
                        if self.state.tech[tech.name]['missing_turns'] > 0:
                            self.log.append( { 'phase' : phase,
                                               'step' : Game.STEPS_PER_PHASE[phase][0],
                                               'target' : tech.name,
                                               'memo' : Game.L_RESEARCH_CYCLE, 'args' : [ self.state.tech[tech.name]['missing_turns'] ],
                                               'state' : self.state.to_json() } )
                        else:
                            # finished!
                            self.state.tech.finish(tech.name)
                            tech_player = self.state.tech[tech.name]['player']
                            del self.state.players[tech_player].tech[self.state.players[tech_player].tech.index(tech.name)]
                            
                            self.log.append( { 'phase' : phase,
                                               'step' : Game.STEPS_PER_PHASE[phase][0],
                                               'target' : tech.name,
                                               'memo' : Game.L_RESEARCHED,
                                               'state' : self.state.to_json() } )

                            if tech.type_ == Tech.B:
                                # auto-protect, apply protection
                                node = self.game_def.graph.node_names[tech.node]
                                self.state.graph[node]['auto-protected'] = True
                                self.log.append( { 'phase' : phase,
                                                   'step' : Game.STEPS_PER_PHASE[phase][0],
                                                   'target' : node,
                                                   'memo' : Game.L_AUTO_PROTECTED,
                                                   'state' : self.state.to_json() } )
                                
                                if self.state.graph[node]['status'] == GraphState.STABLE:
                                    self.state.graph[node]['status'] = GraphState.PROTECTED
                                    self.log.append( { 'phase' : phase,
                                                       'step' : Game.STEPS_PER_PHASE[phase][0],
                                                       'target' : node,
                                                       'memo' : Game.L_PROTECTED,
                                                       'state' : self.state.to_json() } )
                    else:
                        if skills == 0:
                            self.log.append( { 'phase' : phase,
                                               'step' : Game.STEPS_PER_PHASE[phase][0],
                                               'target' : tech.name,
                                               'memo' : Game.L_FUNDED_NOT_SKILLED,
                                               'state' : self.state.to_json() } )
                        elif funds == 0:
                            self.log.append( { 'phase' : phase,
                                               'step' : Game.STEPS_PER_PHASE[phase][0],
                                               'target' : tech.name,
                                               'memo' : Game.L_SKILLED_NOT_FUNDED,
                                               'state' : self.state.to_json() } )
                            

                ## see if any of the projects had no action and should be discarded
                for project in self.state.projects.projects_for_status(ProjectState.IN_PROGRESS):
                    # got skill this turn?

                    skilled = False
                    for act in self.phase_actions:
                        if act[1] in set([Game.A_SUCCESS_SKILL, Game.A_FAILED_SKILL]) and act[2] == project:
                            skilled = True
                            break
                    if not skilled:
                        proj_player = self.state.projects[project.name]['player']
                        self.state.projects.abandon(project.name)
                        del self.state.players[proj_player].projects[self.state.players[proj_player].projects.index(project.name)]
                
                        self.log.append( { 'phase' : phase,
                                           'step' : Game.STEPS_PER_PHASE[phase][0],
                                           'target' : project.name,
                                           'memo' : Game.L_PROJECT_ABANDONED,
                                           'state' : self.state.to_json() } )

                ## see if any of the projects was finished and apply its actions
                for project in self.state.projects.projects_for_status(ProjectState.IN_PROGRESS):
                    for act in self.phase_actions:
                        if act[1] == Game.A_SUCCESS_SKILL and act[2] == project:
                            missing = self.state.projects[project.name]['missing']
                            if act[3][0] not in missing:
                                self.log.append( { 'phase' : phase,
                                                   'step' : Game.STEPS_PER_PHASE[phase][0],
                                                   'target' : project.name,
                                                   'memo' : Game.L_PROJECT_OVERSKILLED, 'args' : [ act[3][0] ],
                                                   'state' : self.state.to_json() } )
                            else:
                                del missing[missing.index(act[3][0])]
                                self.state.projects[project.name]['missing'] = missing
                    if len(self.state.projects[project.name]['missing']) == 0:
                        # finished
                        proj_player = self.state.projects[project.name]['player']
                        self.state.projects.finish(project.name)
                        del self.state.players[proj_player].projects[self.state.players[proj_player].projects.index(project.name)]

                        self.log.append( { 'phase' : phase,
                                           'step' : Game.STEPS_PER_PHASE[phase][0],
                                           'target' : project.name,
                                           'memo' : Game.L_PROJECT_FINISHED,
                                           'state' : self.state.to_json() } )
                        
                        # apply effects
                        for fix in project.fixes:
                            fixn = self.game_def.graph.node_names[fix]
                            if self.state.graph[fixn]['status'] == GraphState.IN_CRISIS:
                                if self.state.graph[fixn]['auto-protected']:
                                    self.state.graph[fixn]['status'] = GraphState.PROTECTED
                                else:
                                    self.state.graph[fixn]['status'] = GraphState.STABLE
                                    
                                self.log.append( { 'phase' : phase,
                                                   'step' : Game.STEPS_PER_PHASE[phase][0],
                                                   'target' : fixn,
                                                   'memo' : Game.L_CRISIS_FIX_PROJECT, 'args' : [ project.name ],
                                                   'state' : self.state.to_json() } )
                                    
                        for trigger in project.triggers:
                            triggern = self.game_def.graph.node_names[trigger]
                            if self.state.graph[triggern]['status'] == GraphState.STABLE:
                                self.state.graph[triggern]['status'] = GraphState.IN_CRISIS
                                self.log.append( { 'phase' : phase,
                                                   'step' : Game.STEPS_PER_PHASE[phase][0],
                                                   'target' : triggern,
                                                   'memo' : Game.L_CRISIS_TRIGGERED, 'args' : [ project.name ],
                                                   'state' : self.state.to_json() } )
                            elif self.state.graph[triggern]['status'] == GraphState.PROTECTED:
                                self.state.graph[triggern]['status'] = GraphState.STABLE
                                self.log.append( { 'phase' : phase,
                                                   'step' : Game.STEPS_PER_PHASE[phase][0],
                                                   'target' : triggern,
                                                   'memo' : Game.L_PROT_LOSS_PROJECT, 'args' : [ project.name ],
                                                   'state' : self.state.to_json() } )
                            else: # in crisis, cascade
                                cascaded = self.cascade(trigger)
                                if cascaded:
                                    for trigger2 in cascaded:
                                        trigger2n = self.game_def.graph.node_names[trigger2]
                                        if self.state.graph[trigger2n]['status'] == GraphState.STABLE:
                                            self.state.graph[trigger2n]['status'] = GraphState.IN_CRISIS
                                            self.log.append( { 'phase' : phase,
                                                               'step' : Game.STEPS_PER_PHASE[phase][0],
                                                               'target' : trigger2n,
                                                               'memo' : Game.L_CRISIS_TRIGGERED, 'args' : [ project.name ],
                                                               'state' : self.state.to_json() } )
                                        elif self.state.graph[trigger2n]['status'] == GraphState.PROTECTED:
                                            self.state.graph[trigger2n]['status'] = GraphState.STABLE
                                            self.log.append( { 'phase' : phase,
                                                               'step' : Game.STEPS_PER_PHASE[phase][0],
                                                               'target' : trigger2n,
                                                               'memo' : Game.L_PROT_LOSS_PROJECT, 'args' : [ project.name ],
                                                               'state' : self.state.to_json() } )
                                else:
                                    self.state.crisis_chips += 1
                                    self.log.append( { 'phase' : phase,
                                                       'step' : Game.STEPS_PER_PHASE[phase][0],
                                                       'target' : triggern,
                                                       'memo' : Game.L_CHIP_PROJECT, 'args' : [ project.name ],
                                                       'state' : self.state.to_json() } )
                                    
                ## see if any of the policies had no action and should be discarded
                for policy in self.state.policies.policies_for_status(PolicyState.IN_PROGRESS) + \
                    self.state.policies.policies_for_status(PolicyState.PASSED):
                    # got power this turn?

                    empowered = False
                    for act in self.phase_actions:
                        if act[1] == Game.A_EMPOWER_POLICY:
                            empowered = True
                            break
                    if not empowered:
                        pol_player = self.state.policies[policy.name]['player']
                        self.state.policies.abandon(policy.name)
                        del self.state.players[pol_player].policies[self.state.players[pol_player].policies.index(policy.name)]
                
                        self.log.append( { 'phase' : phase,
                                           'step' : Game.STEPS_PER_PHASE[phase][0],
                                           'target' : policy.name,
                                           'memo' : Game.L_POLICY_ABANDONED,
                                           'state' : self.state.to_json() } )
                        
                ## see if any of the policies was passed
                for policy in self.state.policies.policies_for_status(PolicyState.IN_PROGRESS):
                    if self.state.policies[policy.name]['missing_power'] <= 0:

                        if self.state.policies[policy.name]['missing_power'] < 0:
                            self.log.append( { 'phase' : phase,
                                               'step' : Game.STEPS_PER_PHASE[phase][0],
                                               'target' : policy.name,
                                               'memo' : Game.L_POLICY_OVERPOWERED, 'args' : [ abs(self.state.policies[policy.name]['missing_power']) ],
                                               'state' : self.state.to_json() } )

                        self.state.policies.has_passed(policy.name)
                       
                        self.log.append( { 'phase' : phase,
                                           'step' : Game.STEPS_PER_PHASE[phase][0],
                                           'target' : policy.name,
                                           'memo' : Game.L_POLICY_PASSED,
                                           'state' : self.state.to_json() } )
                
                ## see if any of the passed policies started and apply its actions
                for policy in self.state.policies.policies_for_status(PolicyState.PASSED):
                    self.state.policies[policy.name]['missing_turns'] -= 1
                    if self.state.policies[policy.name]['missing_turns'] == 0:
                        self.state.policies.finish(policy.name)
                        pol_player = self.state.policies[policy.name]['player']
                        del self.state.players[pol_player].policies[self.state.players[pol_player].policies.index(policy.name)]
                       
                        self.log.append( { 'phase' : phase,
                                           'step' : Game.STEPS_PER_PHASE[phase][0],
                                           'target' : policy.name,
                                           'memo' : Game.L_POLICY_IN_ACTION,
                                           'state' : self.state.to_json() } )

                        for fix in policy.fixes:
                            fixn = self.game_def.graph.node_names[fix]
                            if self.state.graph[fixn]['status'] == GraphState.IN_CRISIS:
                                if self.state.graph[fixn]['auto-protected']:
                                    self.state.graph[fixn]['status'] = GraphState.PROTECTED
                                else:
                                    self.state.graph[fixn]['status'] = GraphState.STABLE
                                    
                                self.log.append( { 'phase' : phase,
                                                   'step' : Game.STEPS_PER_PHASE[phase][0],
                                                   'target' : fixn,
                                                   'memo' : Game.L_CRISIS_FIX_POLICY, 'args' : [ policy.name ],
                                                   'state' : self.state.to_json() } )
                                                                        
                        for protect in policy.protects:
                            protectn = self.game_def.graph.node_names[protect]
                            if self.state.graph[protectn]['status'] == GraphState.STABLE:
                                self.state.graph[protectn]['status'] = GraphState.PROTECTED
                                    
                                self.log.append( { 'phase' : phase,
                                                   'step' : Game.STEPS_PER_PHASE[phase][0],
                                                   'target' : protectn,
                                                   'memo' : Game.L_POLICY_PROTECT, 'args' : [ policy.name ],
                                                   'state' : self.state.to_json() } )

                # CRISIS ROLLING

                ## add crisis chip for each category fully in crisis
                for cat, catid in Graph.CATEGORIES:
                    if len(self.state.graph.are_in_crisis(cat)) == len(self.game_def.graph.node_classes[catid]):
                        self.log.append( { 'phase' : phase,
                                           'step' : Game.STEPS_PER_PHASE[phase][1],
                                           'target' : cat,
                                           'memo' : Game.L_CHIP_FULL_CAT,
                                           'state' : self.state.to_json() } )

                while self.state.crisis_chips and len(self.state.graph.are_in_crisis()) < len(self.game_def.graph):
                    ## roll a category, if the category is fully in crisis, add a crisis chip and roll again
                    catnum = self.roll_dice(1, self.state.player, 'crisis cat', rand, 1)
                    cat, catid = Graph.CATEGORIES[catnum - 1]
                    self.log.append( { 'phase' : phase,
                                       'step' : Game.STEPS_PER_PHASE[phase][1],
                                       'target' : cat,
                                       'memo' : Game.L_CRISIS_CAT,
                                       'state' : self.state.to_json() } )

                    if len(self.state.graph.are_in_crisis(cat)) == len(self.game_def.graph.node_classes[catid]):
                        self.log.append( { 'phase' : phase,
                                      'step' : Game.STEPS_PER_PHASE[phase][1],
                                      'target' : cat,
                                      'memo' : Game.L_CHIP_FULL_CAT,
                                      'state' : self.state.to_json() } )
                        continue

                    ## roll a node in category, if in crisis and all its descendants are in crisis, add a crisis chip and roll again
                    nodes = list(self.game_def.graph.node_classes[catid])
                    dice = 1
                    if len(nodes) > 6:
                        dice += 1
                    nodenum = (self.roll_dice(dice, self.state.player, 'node in ' + cat, rand, 1) - 1) % len(nodes)
                    node = nodes[nodenum]
                    noden = self.game_def.graph.node_names[node]
                    if self.state.graph.is_saturated(noden):
                        self.log.append( { 'phase' : phase,
                                           'step' : Game.STEPS_PER_PHASE[phase][1],
                                           'target' : noden,
                                           'memo' : Game.L_CHIP_SATURATED,
                                           'state' : self.state.to_json() } )
                        continue
                    
                    self.log.append( { 'phase' : phase,
                                       'step' : Game.STEPS_PER_PHASE[phase][1],
                                       'target' : noden,
                                       'memo' : Game.L_CRISIS_NODE,
                                       'state' : self.state.to_json() } )
                        
                    ## with a node in hand, roll crisis chips until either the roll is successful or all the crisis chips are exhausted
                    crisis_averted = True
                    while self.state.crisis_chips:
                        crisis_roll = self.roll_dice(2, self.state.player, 'crisis roll for ' + noden, rand, 1)
                        self.log.append( { 'phase' : phase,
                                           'step' : Game.STEPS_PER_PHASE[phase][1],
                                           'target' : crisis_roll,
                                           'memo' : Game.L_CRISIS_ROLL, 'args' : [ noden ],
                                           'state' : self.state.to_json() } )
                        self.state.crisis_chips -= 1
                        if crisis_roll > 6:
                            crisis_averted = False
                            break

                    if crisis_averted:
                        self.log.append( { 'phase' : phase,
                                           'step' : Game.STEPS_PER_PHASE[phase][1],
                                           'target' : noden,
                                           'memo' : Game.L_CRISIS_AVERTED,
                                           'state' : self.state.to_json() } )
                    else:
                        ## if node was stable, set in crisis
                        if self.state.graph[noden]['status'] == GraphState.STABLE:
                            self.state.graph[noden]['status'] = GraphState.IN_CRISIS
                            self.log.append( { 'phase' : phase,
                                               'step' : Game.STEPS_PER_PHASE[phase][1],
                                               'target' : noden,
                                               'memo' : Game.L_IN_CRISIS,
                                               'state' : self.state.to_json() } )
                            
                        ## if the node was protected, remove the protection
                        elif self.state.graph[noden]['status'] == GraphState.PROTECTED:
                            self.state.graph[noden]['status'] = GraphState.STABLE
                            self.log.append( { 'phase' : phase,
                                               'step' : Game.STEPS_PER_PHASE[phase][0],
                                               'target' : noden,
                                               'memo' : L_PROT_LOSS,
                                               'state' : self.state.to_json() } )
                        ## if the node was in crisis, activate all the nodes reachable from it and further cascade as needed
                        else: 
                            cascaded = self.cascade(node)
                            for node2 in cascaded:
                                node2n = self.game_def.graph.node_names[node2]
                                if self.state.graph[node2n]['status'] == GraphState.STABLE:
                                    self.state.graph[node2n]['status'] = GraphState.IN_CRISIS
                                    self.log.append( { 'phase' : phase,
                                                       'step' : Game.STEPS_PER_PHASE[phase][1],
                                                       'target' : node2n,
                                                       'memo' : Game.L_IN_CRISIS_CASCADE, 'args': [ noden ],
                                                       'state' : self.state.to_json() } )
                                elif self.state.graph[node2n]['status'] == GraphState.PROTECTED:
                                    self.state.graph[node2n]['status'] = GraphState.STABLE
                                    self.log.append( { 'phase' : phase,
                                                       'step' : Game.STEPS_PER_PHASE[phase][1],
                                                       'target' : node2n,
                                                       'memo' : Game.L_PROT_LOSS_CASCADE, 'args': [ noden ],
                                                       'state' : self.state.to_json() } )
                        

                    ## if there are more crisis chips, continue by selecting a new category
        return self.advance()


