# -*- coding: utf-8 -*-
# Copyright (C) 2021 Textualization Software Ltd.
# Distributed under the terms of the Apache Software License 2.0
# http://www.apache.org/licenses/LICENSE-2.0

import random

from .graph import Graph
from .player import Player
from .project import Projects
from .state import GraphState, ProjectState, TechTreeState
from .drawpiles import DrawPiles

class GreedyPlayer(Player):

    def __init__(self, name: str, ordering: int):
        super().__init__(name, ordering)
        self.rnd = random.Random(ordering * 7)

    def pick(self, decision: int, decisions: list,
             # state: PlayerState
             # game: GameState
             rand: random.Random, state: object=None, game: object=None, context: dict=None):
        """Choose a decision among many"""
        
        if state is None:
            print("ai player pick: Missing state")
            return rand.choice(decisions)

        
        if decision == Player.INIT_ROLE:
            game_def = context['game_def']
            if state.extra is None:
                state.extra = GreedyPlayerState(self.rnd, state, game, game_def)
            # pick role that cover most of the top categories
            scores = sorted([ (role_name, self.score_class(role_name, game, game_def)) for role_name in decisions ],
                            key=lambda x:x[1])
            return scores[-1]

        # now get to work       
        if decision == Player.PILE_DRAW:
            if 'drawn' not in state.extra.phase_mem or state.extra.phase_mem['drawn'] == 2:
                actions, extra = self.analyze(self.rnd, state, game, game_def)
                state.extra.phase_mem = { # reset
                    'drawn':  1,
                    'actions': actions
                }
                state.extra.phase_mem.update(extra)
            else:
                actions = state.extra.phase_mem['actions'] 
            
            chosen = actions[Player.PILE_DRAW][state.extra.phase_mem['drawn']]
            state.extra.phase_mem['drawn'] += 1
            return chosen
        
        actions = state.extra.phase_mem['actions'] 
        if decision == Player.START_PROJECT:
            project = actions[Player.START_PROJECT]
            if project:
                return project['type']
            return None
        elif decision == Player.START_PROJECT_FIX_CAT:
            project = actions[Player.START_PROJECT]
            return project['category']
        elif decision == Player.START_PROJECT_FIX_NODE:
            project = actions[Player.START_PROJECT]
            return project['node']
        elif decision == Player.PLAY_CARD:
            actions = self.analyze_cards(self.rnd, state, game, game_def, actions)
            state.extra.phase_mem['actions'] = actions
            
            cards = actions[Player.PLAY_CARD]
            cardno = state.extra.phase_mem.get('play_card', 0)
            state.extra.phase_mem.get['play_card'] = cardno + 1
            if cards:
                if cardno >= len(cards):
                    return None
                for dec in decisions:
                    card, suit, _, project_name = dec
                    if cards[cardno][0] == card and cards[cardno][1] == suit and cards[cardno][2] == project_name:
                        return dec
                print("Card not found: cards={}, cardno={}, decisions={}".format(cards, cardno, decisions))
            return None
        elif decision == Player.CONSULTANT:
            cards = actions[Player.PLAY_CARD]
            return cards[state.extra.phase_mem.get['play_card'] - 1][3]
        elif decision == Player.START_RESEARCH:
            return actions[Player.START_RESEARCH]
        elif decision == Player.CARD_FOR_RESEARCH:
            cards = actions[Player.CARD_FOR_RESEARCH]
            cardno = state.extra.phase_mem.get('research_card', 0)
            state.extra.phase_mem.get['research_card'] = cardno + 1
            
            if cards:
                for dec in decisions:
                    tech_name, card, _, suit = dec
                    if cards[cardno][0] == card and cards[cardno][1] == suit and cards[cardno][2] == tech_name:
                        return dec
                print("card for research not found: cards={}, cardno={}, decisions={}".format(cards, cardno, decisions))
            return None
        elif decision == Player.FUND_RESEARCH:
            to_fund = actions[Player.FUND_RESEARCH]
            if to_fund:
                return to_fund
            return None

        print("something went wrong: decision={}, decisions={}".format(decision, decisions))
        return rand.choice(decisions)
        

    def score_class(self, class_name, state, game, game_def):
        cat_importance = state.extra.cat_importance

        pclass = game_def.classes.class_for_name(class_for_player)
        class_suits = set([pclass.suit_a, pclass.suit_b])

        score = 0.0
        for catid, cat_score in cat_importance.items():
            for c, s1, s2 in Projects.BASE_TABLE:
                if c[1] == catid:
                    multiplier = len(class_suits.intersection([s1, s2]))
                    if multiplier:
                        score += multiplier * cat_importance[catid]
        return score


    
    def analyze(self, rnd, state, game, game_def):

        # choose research
        researching = self.rnd.shuffle(list(game.tech.techs_for_status(TechTreeState.IN_PROGRESS)))
        available   = self.rnd.shuffle(list(game.tech.techs_for_status(TechTreeState.AVAILABLE)))

        target_tech = None

        # research protection for 16%, if available
        for idx, node in enumerate(order):
            if idx > len(order) * 0.166:
                break
            catid = game_def.graph.class_for_node[node]
            needed = []
            for _, otherid, s1, s2 in Projects.BASE_TABLE:
                if otherid == catid:
                    needed.append(s1, s2)
                    
            for tech in researching + available:
                if tech.suit in needed and (tech.type_ == Tech.BASE or tech.type_ == Tech.A):
                    target_tech = tech
                    break
            if target_tech:
                break

        if not target_tech:
            # research shortest path for top 16% unprotected
            for idx, node in enumerate(order):
                if idx > len(order) * 0.166:
                    break
                    
                for tech in researching + available:
                    if tech.type_ == Tech.B and tech.node == node:
                        target_tech = tech
                        break
            if target_tech:
                break
            
        # else: do not do any research
        
        crisis_top_16perc = list()
        crisis_top_33perc = list()
        crisis_top_66perc = list()

        in_crisis = set(game.graph.are_in_crisis())

        order = state.extra.order
        
        for idx, node in enumerate(order):
            if node in in_crisis:
                if idx < len(order) * 0.166:
                    crisis_top_16perc.append(node)
                elif idx < len(order) * 0.333:
                    crisis_top_33perc.append(node)
                elif idx < len(order) * 0.666:
                    crisis_top_66perc.append(node)

        # choose project
        ongoing = game.projects.projects_for_status(Projects.IN_PROGRESS)
        
        if crisis_top_16perc:

            # there are projects for them?
            project = None
            for crisis_node in crisis_top_16perc:
                for ongoingp in ongoing:
                    if ongoingp.fixes == crisis_node:
                        project = ongoingp
                        break
            if project:
                # all resources to it
                missing = list(game.projects[project.name].missing)
                for in_hand in state.cards:
                    if in_hand[1] in missing:
                        del missing[missing.index(in_hand[1])]
                        # TODO handle jokers
                        
                if self.player_class.suit_a in missing:
                    del missing[missing.index(self.player_class.suit_a)]
                    if self.player_class.suit_b in missing:
                        draw = [ self.player_class.suit_a, self.player_class.suit_b ]
                    elif self.player_class.suit_a in missing: # appears twice
                        draw = [ self.player_class.suit_a, self.player_class.suit_a ]
                    elif missing:
                        draw = [ missing[0], self.player_class.suit_a ]
                    else: # some redundancy
                        draw = [ self.player_class.suit_a, self.player_class.suit_a ]
                elif self.player_class.suit_b in missing:
                    del missing[missing.index(self.player_class.suit_b)]
                    if self.player_class.suit_b in missing: # appears twice
                        draw = [ self.player_class.suit_b, self.player_class.suit_b ]
                    elif missing:
                        draw = [ missing[0], self.player_class.suit_b ]
                    else: # some redundancy
                        draw = [ self.player_class.suit_b, self.player_class.suit_b ]
                elif missing:
                    draw = [ missing[0], rnd.choice([ self.player_class.suit_a, self.player_class.suit_b ]) ]
                else:
                    draw = [ rnd.choice( DrawPiles.SUITS ), rnd.choice([ self.player_class.suit_a, self.player_class.suit_b ]) ]

                    return {
                        Player.PILE_DRAW: draw,
                        Player.START_PROJECT: None,
                        Player.START_RESEARCH: None,
                        Player.CARD_FOR_RESEARCH: None,
                        Player.FUND_RESEARCH: None
                    }, {
                        'project': {
                            'name'     : project.name,
                            'priority' : 'top'
                        }
                    }

            else: # there are none, need to start one
                if state.projects: # do I have a project?
                    # drop it and gather cards for a project for the top node

                    cards = []
                    in_hand = [ card[1] for card in state.cards ]
                    
                    for crisis_node in crisis_top_16perc:
                        if len(draw) == 2:
                            break
                        
                        catid = game_def.graph.class_for_node[crisis_node]
                        suits = None
                        for c, s1, s2 in Projects.BASE_TABLE:
                            if c[1] == catid:
                                suits = [ s1, s2 ]

                        if suits[1] in in_hand:
                            del in_hand[in_hand.index(suits[1])]
                            del suits[1]
                        if suits[0] in in_hand:
                            del in_hand[in_hand.index(suits[0])]
                            del suits[0]
                        if suits:
                            if len(draw) > 1:
                                if suits[0] == self.player_class.suit_a:
                                    draw.append(self.player_class.suit_a)
                                elif suits[0] == self.player_class.suit_b:
                                    draw.append(self.player_class.suit_b)
                                elif len(suits) > 1:
                                    if suits[1] == self.player_class.suit_a:
                                        draw.append(self.player_class.suit_a)
                                    elif suits[1] == self.player_class.suit_b:
                                        draw.append(self.player_class.suit_b)

                    if len(draw) == 0:
                        draw = [ rnd.choice( DrawPiles.SUITS ), rnd.choice([ self.player_class.suit_a, self.player_class.suit_b ]) ]
                    elif len(draw) == 1:
                        draw.append(rnd.choice([ self.player_class.suit_a, self.player_class.suit_b ]))
                    
                    return {
                        Player.PILE_DRAW: draw,
                        Player.START_PROJECT: None,
                        Player.START_RESEARCH: None,
                        Player.CARD_FOR_RESEARCH: None,
                        Player.FUND_RESEARCH: None
                    }, {}                    
                else:                    
                    # start project for it, with tradeoff
                    project = game.projects.find_project(Projects.BASE, crisis_top_16perc[0])
                    needed  = game.projects[project.name]['missing']
                    draw = [ None, None ]
                    if self.player_class.suit_a in needed:
                        draw[1] = self.player_class.suit_a
                        del needed[needed.index(self.player_class.suit_a)]
                    elif self.player_class.suit_b in needed:
                        draw[1] = self.player_class.suit_b
                        del needed[needed.index(self.player_class.suit_b)]
                    if needed:
                        draw[0] = needed[0]
                    else:
                        draw[0] = rnd.choice( DrawPiles.SUITS )
                    if draw[1] is None:
                        draw[1] = rnd.choice([ self.player_class.suit_a, self.player_class.suit_b ])
                    
                    return {
                        Player.PILE_DRAW: draw,
                        Player.START_PROJECT: project.name,
                        Player.START_RESEARCH: None,
                        Player.CARD_FOR_RESEARCH: None,
                        Player.FUND_RESEARCH: None
                    }, {
                        'project': {
                            'name'     : project.name,
                            'priority' : 'top'
                        }
                    }
        elif crisis_top_33perc:
            if state.projects: # do I have a project?
                # finish it
                needed = game.projects[state.projects[0]]['missing']
                draw = [ None, None ]
                if self.player_class.suit_a in needed:
                    draw[1] = self.player_class.suit_a
                    del needed[needed.index(self.player_class.suit_a)]
                elif self.player_class.suit_b in needed:
                    draw[1] = self.player_class.suit_b
                    del needed[needed.index(self.player_class.suit_b)]
                if needed:
                    draw[0] = needed[0]
                else:
                    if target_tech:
                        draw[0] = target_tech.suit
                    
                if draw[1] is None:
                    if target_tech.suit in [ self.player_class.suit_a, self.player_class.suit_b ]:
                        draw[1] = target_tech.suit
                    else:
                        draw[1] = rnd.choice([ self.player_class.suit_a, self.player_class.suit_b ])

                return {
                    Player.PILE_DRAW: draw,
                    Player.START_PROJECT: None,
                    Player.START_RESEARCH: target_tech.name if game.tech[target_tech.name]['status'] == TechTreeState.AVAILABLE else None,
                    Player.CARD_FOR_RESEARCH: None,
                    Player.FUND_RESEARCH: None
                }, {
                    'project': {
                        'name'     : project.name,
                        'priority' : 'medium'
                    }
                }
            else: # create a project for it, no tradeoffs
                project = game.projects.find_project(Projects.A, crisis_top_33perc[0])
                needed  = game.projects[project.name]['missing']
                draw = [ None, None ]
                if self.player_class.suit_a in needed:
                    draw[1] = self.player_class.suit_a
                    del needed[needed.index(self.player_class.suit_a)]
                elif self.player_class.suit_b in needed:
                    draw[1] = self.player_class.suit_b
                    del needed[needed.index(self.player_class.suit_b)]
                if needed:
                    draw[0] = needed[0]
                else:
                    draw[0] = rnd.choice( DrawPiles.SUITS )
                if draw[1] is None:
                    draw[1] = rnd.choice([ self.player_class.suit_a, self.player_class.suit_b ])
                    
                return {
                    Player.PILE_DRAW: draw,
                    Player.START_PROJECT: project.name if game.projects[project.name]['status'] == ProjectState.AVAILABLE else None,
                    Player.START_RESEARCH: target_tech.name if game.tech[target_tech.name]['status'] == TechTreeState.AVAILABLE else None,
                    Player.CARD_FOR_RESEARCH: None,
                    Player.FUND_RESEARCH: None
                }, {
                    'project': {
                        'name'     : project.name,
                        'priority' : 'medium'
                    }
                }
        elif crisis_top_66perc:
            # same as before, but focus on research for top 16%
            draw = [ None, None ]
            if target_tech.suit in [ self.player_class.suit_a, self.player_class.suit_b ]:
                draw[1] = target_tech.suit
            else:
                draw[0] = target_tech.suit
            
            if state.projects: # do I have a project?
                # finish it
                needed = game.projects[state.projects[0]]['missing']
                if draw[1] is None:
                    if self.player_class.suit_a in needed:
                        draw[1] = self.player_class.suit_a
                        del needed[needed.index(self.player_class.suit_a)]
                    elif self.player_class.suit_b in needed:
                        draw[1] = self.player_class.suit_b
                        del needed[needed.index(self.player_class.suit_b)]
                if draw[0] is None:
                    if needed:
                        draw[0] = needed[0]
                    else:
                        draw[0] = rnd.choice( DrawPiles.SUITS )
                    
                if draw[1] is None:
                    draw[1] = rnd.choice([ self.player_class.suit_a, self.player_class.suit_b ])

                return {
                    Player.PILE_DRAW: draw,
                    Player.START_PROJECT: None,
                    Player.START_RESEARCH: target_tech.name if game.tech[target_tech.name]['status'] == TechTreeState.AVAILABLE else None,
                }, {
                    'project': {
                        'name'     : project.name,
                        'priority' : 'low'
                    }
                }
            else: # create a project for it, no tradeoffs
                project = game.projects.find_project(Projects.A, crisis_top_66perc[0])
                needed  = game.projects[project.name]['missing']
                if self.player_class.suit_a in needed:
                    draw[1] = self.player_class.suit_a
                    del needed[needed.index(self.player_class.suit_a)]
                elif self.player_class.suit_b in needed:
                    draw[1] = self.player_class.suit_b
                    del needed[needed.index(self.player_class.suit_b)]
                if draw[0] is None:
                    if needed:
                        draw[0] = needed[0]
                    else:
                        draw[0] = rnd.choice( DrawPiles.SUITS )
                    
                if draw[1] is None:
                    draw[1] = rnd.choice([ self.player_class.suit_a, self.player_class.suit_b ])
                    
                return {
                    Player.PILE_DRAW: draw,
                    Player.START_PROJECT: project.name if game.projects[project.name]['status'] == ProjectState.AVAILABLE else None,
                    Player.START_RESEARCH: target_tech.name if game.tech[target_tech.name]['status'] == TechTreeState.AVAILABLE else None,
                }, {
                    'project': {
                        'name'     : project.name,
                        'priority' : 'low'
                    }
                }
        else:
            # research and hoard cards for top 16%
            draw = [ None, None ]
            if target_tech.suit in [ self.player_class.suit_a, self.player_class.suit_b ]:
                draw[1] = target_tech.suit
            else:
                draw[0] = target_tech.suit
            if draw[0] is None:
                draw[0] = rnd.choice( DrawPiles.SUITS )
            if draw[1] is None:
                draw[1] = rnd.choice([ self.player_class.suit_a, self.player_class.suit_b ])

            return {
                Player.PILE_DRAW: draw,
                Player.START_PROJECT: project.name if game.projects[project.name]['status'] == ProjectState.AVAILABLE else None,
                Player.START_RESEARCH: target_tech.name if game.tech[target_tech.name]['status'] == TechTreeState.AVAILABLE else None,
            }, {}

        print("something went wrong")

        return {
            Player.PILE_DRAW: None,
            Player.START_PROJECT: None,
            Player.PLAY_CARD: None,
            Player.START_RESEARCH: None,
            Player.CARD_FOR_RESEARCH: None,
            Player.FUND_RESEARCH: None
        }, {}
        
    def analyze_cards(self, rnd, state, game, actions):
        # check the cards drawn and use them to fund project and tech using the priorities
        play_card = None
        in_hand = list(state.cards)
        money = state.resources['$']
        if 'project' in state.extra.phase_mem:
            project_prio = state.extra.phase_mem['project']['priority']
            project_name = state.extra.phase_mem['project']['name']

            needed  = list(game.projects[project_name]['missing'])

            changes = True
            play_card = []
            while changes and needed:
                changes = False
                for idx, card in enumerate(in_hand):
                    if card[1] == 14: # TODO smarter use of wildcards is possible
                        if project_prio in [ 'top', 'medium' ]:
                            changes = True
                            play_card.append( (card, needed[0], project_name, 0) )
                            del needed[0]
                            del in_hand[idx]
                            break
                        #else: keep it to myself
                    elif card[0] in needed:
                        changes = True
                        fee = 0 # TODO smarter allocation of money based on card values is possible
                        value = card[1]
                        base_tech = game.tech.find_tech(Tech.BASE, card[0])
                        expanded_tech = game.tech.find_tech(Tech.A, card[0])
                        if game.tech.status(base_tech.name) == TechTreeState.RESEARCHED:
                            value += 1
                        if game.tech.status(expanded_tech.name) == TechTreeState.RESEARCHED:
                            value = min(11, value + 2)
                        
                        if project_prio in [ 'top', 'medium' ]:
                            if money > 0 and value < 11:
                                fee = min(value - 11, money)
                        elif money > 1 and value < 10:
                            fee = min(value - 10, money - 1) # leave one for research
                        money -= fee
                            
                        play_card.append( (card, card[0], project_name, fee) )
                        del needed[needed.index(card[0])]
                        del in_hand[idx]
                        break
        #else: # all tech
        
        cards_for_research = []
        funds_for_research = []
        if state.tech:
            for idx, card in enumerate(in_hand):
                if card[0] == state.tech[0].suit:
                    cards_for_research.append(card, card[0], state.tech[0])
                    del in_hand[idx]
                    break
            if money > 0:
                funds_for_research.append(state.tech[0])
                money -= 1
        researching = self.rnd.shuffle(list(game.tech.techs_for_status(TechTreeState.IN_PROGRESS)))
        for tech in researching:
            if tech.name == state.tech[0]:
                continue
            if len(in_hand) == 0 and money == 0:
                break
            if in_hand:
                for idx, card in enumerate(in_hand):
                    if card[0] == tech.suit:
                        cards_for_research.append(card, card[0], tech.name)
                        del in_hand[idx]
                        break
            if money > 0:
                funds_for_research.append(tech.name)
                money -= 1

        actions[Player.PLAY_CARD] = play_card
        actions[Player.CARD_FOR_RESEARCH] = cards_for_research
        actions[Player.FUND_RESEARCH] = funds_for_research

        return actions

            
class GreedyPlayerState:

    CAT_DECAY = 0.9

    def __init__(self, rnd=None, state=None, game=None, game_def=None):
        if rnd is not None:
            self.order = self.rnd.shuffle(list(game_def.graph.node_names))
            self.importance = { name: idx for idx, name in enumerate(self.order) }

            self.cat_importance = { catid: 0 for (_, catid) in Graph.CATEGRORIES }

            weight = 1.0
            for node in self.order:
                self.cat_importance[game_def.graph.class_for_node[node]] += weight
                weight *= CAT_DECAY

            self.phase_mem = {}

    def to_json(self):
        return {
            'order' : self.order,
            'cat_importance' : self.cat_importance,
            'phase_mem' : self.phase_mem
        }

    def copy(self):
        other = GreedyPlayerState()
        other.order = list(self.order)
        other.importance = dict(self.importance)
        other.cat_importance = dict(self.cat_importance)
        other.phase_mem = dict(self.phase_mem)
        return other
