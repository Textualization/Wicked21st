# -*- coding: utf-8 -*-
# Copyright (C) 2021 Textualization Software Ltd.
# Distributed under the terms of the Apache Software License 2.0
# http://www.apache.org/licenses/LICENSE-2.0

import random

from .graph import Graph
from .player import Player
from .techtree import Tech
from .project import Projects, Project
from .state import GraphState, ProjectState, TechTreeState
from .drawpiles import DrawPiles


class GreedyPlayer(Player):

    TOP_TIER = 0.0
    SECOND_TIER = 0.333

    RESEARCH_TIER = 0.166  # TOP_TIER

    DEBUG = False

    def __init__(self, name: str, ordering: int):
        super().__init__(name, ordering)
        self.rnd = random.Random(ordering * 7)

    def debug(self, *args):
        """Debug print-outs, if flag is activated"""
        if GreedyPlayer.DEBUG:
            print(*args)

    def pick(
        self,
        decision: int,
        decisions: list,
        rand: random.Random,
        state: object = None,  # state: PlayerState
        game: object = None,  # game: GameState
        context: dict = None,
    ):
        """Choose a decision among many"""
        dec = self._pick(decision, decisions, rand, state, game, context)
        if dec not in decisions:
            print(
                "For", Player.decision_names[decision], "valid:", decisions, "got:", dec
            )
            print(state.to_json())
        assert dec in decisions
        return dec

    def _pick(
        self,
        decision: int,
        decisions: list,
        rand: random.Random,
        state: object = None,  # state: PlayerState
        game: object = None,  # game: GameState
        context: dict = None,
    ):
        """Internal pick, this is the method that gets the job done."""
        if state is None:
            print("ai player pick: Missing state")
            return rand.choice(decisions)

        if decision == Player.INIT_ROLE:
            return self._pick_class(decisions, rand, state, game, context)
        if decision == Player.PILE_DRAW:
            return self._pick_pile(decisions, rand, state, game, context)

        actions = state.extra.phase_mem["actions"]

        if decision == Player.START_PROJECT:
            project = actions[Player.START_PROJECT]
            if project:
                return project["type"]
            return None
        if decision == Player.START_PROJECT_FIX_CAT:
            project = actions[Player.START_PROJECT]
            return project["category"]
        if decision == Player.START_PROJECT_FIX_NODE:
            project = actions[Player.START_PROJECT]
            return project["node"]

        if "card_analysis" not in state.extra.phase_mem:
            actions = self.analyze_cards(self.rnd, state, game, actions)
            self.debug("cards analyzed:", actions)
            state.extra.phase_mem["actions"] = actions
            state.extra.phase_mem["card_analysis"] = True

        if decision == Player.PLAY_CARD:
            return self._pick_card(decisions, rand, state, game, context, actions)
        if decision == Player.CONSULTANT:
            cards = actions[Player.PLAY_CARD]
            return cards[state.extra.phase_mem["play_card"] - 1][3]
        if decision == Player.START_RESEARCH:
            return actions[Player.START_RESEARCH]
        if decision == Player.CARD_FOR_RESEARCH:
            return self._pick_card_research(
                decisions, rand, state, game, context, actions
            )
        if decision == Player.FUND_RESEARCH:
            return self._pick_fund_research(
                decisions, rand, state, game, context, actions
            )

        print(
            "something went wrong: decision={}, decisions={}".format(
                decision, decisions
            )
        )
        return rand.choice(decisions)

    def _pick_class(
        self,
        decisions: list,
        rand: random.Random,
        state: object = None,  # state: PlayerState
        game: object = None,  # game: GameState
        context: dict = None,
    ):
        """Pick a class"""
        game_def = context["game_def"]
        if state.extra is None:
            state.extra = GreedyPlayerState(self.rnd, state, game, game_def)
        # pick role that cover most of the top categories
        scores = sorted(
            [
                (role_name, self.score_class(role_name, state, game, game_def))
                for role_name in decisions
            ],
            key=lambda x: x[1],
        )
        return scores[-1][0]

    def _pick_pile(
        self,
        decisions: list,
        rand: random.Random,
        state: object = None,  # state: PlayerState
        game: object = None,  # game: GameState
        context: dict = None,
    ):
        """Pick a pile to draw from"""
        if "drawn" not in state.extra.phase_mem or state.extra.phase_mem["drawn"] == 2:
            game_def = context["game_def"]
            actions, extra = self.analyze(self.rnd, state, game, game_def)
            state.extra.phase_mem = {"drawn": 0, "actions": actions}  # reset
            state.extra.phase_mem.update(extra)
        else:
            actions = state.extra.phase_mem["actions"]

        chosen = actions[Player.PILE_DRAW][state.extra.phase_mem["drawn"]]
        state.extra.phase_mem["drawn"] += 1
        return chosen

    def _pick_card(
        self,
        decisions: list,
        rand: random.Random,
        state: object = None,  # state: PlayerState
        game: object = None,  # game: GameState
        context: dict = None,
        actions: dict = None,
    ):
        """Pick a card to play"""
        cards = actions[Player.PLAY_CARD]
        cardno = state.extra.phase_mem.get("play_card", 0)
        state.extra.phase_mem["play_card"] = cardno + 1
        if cards:
            if cardno >= len(cards):
                return None
            for dec in decisions:
                card, suit, _, project_name = dec
                if (
                    cards[cardno][0] == card
                    and cards[cardno][1] == suit
                    and cards[cardno][2] == project_name
                ):
                    return dec
            print(
                "Card not found: cards={}, cardno={}, decisions={}".format(
                    cards, cardno, decisions
                )
            )
        return None

    def _pick_card_research(
        self,
        decisions: list,
        rand: random.Random,
        state: object = None,  # state: PlayerState
        game: object = None,  # game: GameState
        context: dict = None,
        actions: dict = None,
    ):
        """Pick a card for research"""
        cards = actions[Player.CARD_FOR_RESEARCH]
        cardno = state.extra.phase_mem.get("research_card", 0)
        state.extra.phase_mem["research_card"] = cardno + 1

        if cards:
            if cardno >= len(cards):
                return None
            for dec in decisions:
                tech_name, card, _, suit = dec
                if (
                    cards[cardno][0] == card
                    and cards[cardno][1] == suit
                    and cards[cardno][2] == tech_name
                ):
                    return dec
            print(
                "card for research not found: cards={}, cardno={}, decisions={}".format(
                    cards, cardno, decisions
                )
            )
        return None

    def _pick_fund_research(
        self,
        decisions: list,
        rand: random.Random,
        state: object = None,  # state: PlayerState
        game: object = None,  # game: GameState
        context: dict = None,
        actions: dict = None,
    ):
        """Pick funds for research"""
        to_fund = actions[Player.FUND_RESEARCH]
        fundno = state.extra.phase_mem.get("research_fund", 0)
        state.extra.phase_mem["research_fund"] = fundno + 1
        if to_fund:
            if fundno >= len(to_fund):
                return None
            return to_fund[fundno]
        return None

    def score_class(self, class_name, state, game, game_def):
        cat_importance = state.extra.cat_importance

        pclass = game_def.classes.class_for_name(class_name)
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
        """The core of the AI, analyze the state of the board and decide next actions"""

        target_tech = self._analyze_research(rnd, state, game, game_def)
        actions, extra = self._analyze_projects(rnd, state, game, game_def, target_tech)

        if actions is not None:
            return actions, extra

        print("something went wrong")
        return {
            Player.PILE_DRAW: None,
            Player.START_PROJECT: None,
            Player.PLAY_CARD: None,
            Player.START_RESEARCH: None,
            Player.CARD_FOR_RESEARCH: None,
            Player.FUND_RESEARCH: None,
        }, {}

    def _analyze_research(self, rnd, state, game, game_def):
        """Decide what research to tackle next"""

        researching = list(game.tech.techs_for_status(TechTreeState.IN_PROGRESS))
        self.rnd.shuffle(researching)
        available = list(game.tech.research_boundary())
        self.rnd.shuffle(available)

        target_tech = None

        # research protection for top tier, if available
        for idx, node in enumerate(state.extra.order):
            if idx > len(state.extra.order) * GreedyPlayer.RESEARCH_TIER:
                break
            catid = game_def.graph.class_for_node[node]
            needed = []
            for otherid, s1, s2 in Projects.BASE_TABLE:
                if otherid[1] == catid:
                    needed.append(s1)
                    needed.append(s2)

            for tech in researching + available:
                if tech.suit in needed and (tech.type_ == Tech.BASE):
                    target_tech = tech
                    break
            if target_tech:
                break

        if not target_tech:
            # research shortest path for top RESEARCH_TIER unprotected
            for idx, node in enumerate(state.extra.order):
                if idx > len(state.extra.order) * GreedyPlayer.RESEARCH_TIER:
                    break

                for tech in researching + available:
                    if tech.type_ == Tech.PROTECT and tech.node == node:
                        target_tech = tech
                        break
                if target_tech:
                    break

        self.debug("target_tech: ", target_tech.name if target_tech else None)

        # else: do not do any research

        return target_tech

    def _analyze_projects(self, rnd, state, game, game_def, target_tech):
        """Decide what project to tackle next"""

        crisis_top_tier = list()
        crisis_second_tier = list()
        crisis_third_tier = list()

        in_crisis = set(game.graph.are_in_crisis())

        order = state.extra.order

        for idx, node in enumerate(order):
            if game_def.graph.node_names[node] in in_crisis:
                if idx < len(order) * GreedyPlayer.TOP_TIER:
                    crisis_top_tier.append(node)
                elif idx < len(order) * GreedyPlayer.SECOND_TIER:
                    crisis_second_tier.append(node)
                elif idx < len(order) * 0.666:
                    crisis_third_tier.append(node)

        self.debug(
            "crisis_top_tier={}, crisis_second_tier={}, crisis_third_tier={}".format(
                len(crisis_top_tier),
                len(crisis_second_tier),
                len(crisis_third_tier),
            )
        )

        ongoing = game.projects.projects_for_status(ProjectState.IN_PROGRESS)
        own_project = (
            game.projects.project_for_name(state.projects[0])
            if state.projects
            else None
        )

        def do_project(project, start, research, prio, draw=None):
            needed = list(
                game.projects[project.name]["missing"]
                if project.name in game.projects
                else game.projects.project_for_name(project.name).cost
            )
            for in_hand in state.cards:
                if in_hand[1] in needed:
                    del needed[needed.index(in_hand[1])]

            # jokers
            for in_hand in state.cards:
                if in_hand[0] == 14 and needed:
                    del needed[0]

            if draw is None:
                draw = [None, None]

            if self.player_class.suit_a in needed and draw[1] is None:
                draw[1] = self.player_class.suit_a
                del needed[needed.index(self.player_class.suit_a)]
            elif self.player_class.suit_b in needed and draw[1] is None:
                draw[1] = self.player_class.suit_b
                del needed[needed.index(self.player_class.suit_b)]
            if needed and draw[0] is None:
                draw[0] = needed[0]
            elif draw[0] is None:
                if research:
                    draw[0] = research.suit
                else:
                    draw[0] = rnd.choice(DrawPiles.SUITS)

            if draw[1] is None:
                if research and research.suit in [
                    self.player_class.suit_a,
                    self.player_class.suit_b,
                ]:
                    draw[1] = research.suit
                else:
                    draw[1] = rnd.choice(
                        [self.player_class.suit_a, self.player_class.suit_b]
                    )

            return {
                Player.PILE_DRAW: draw,
                Player.START_PROJECT: start,
                Player.START_RESEARCH: research.name
                if research
                and game.tech[research.name]["status"] == TechTreeState.AVAILABLE
                else None,
            }, {"project": {"name": project.name, "priority": prio}}

        if own_project:  # steady as you go
            return do_project(
                own_project,
                None,
                None if own_project.fixes in crisis_top_tier else target_tech,
                "top" if own_project.fixes in crisis_top_tier else "medium",
            )

        # start a new project or contribute to existing one
        if crisis_top_tier:
            self.debug("crisis_top_tier")

            # there are projects for them?
            projects = list()
            for crisis_node in crisis_top_tier:
                for ongoingp in ongoing:
                    if ongoingp.fixes == crisis_node:
                        projects.append(ongoingp)

            if projects:
                project = projects[0]
                start = None
            else:
                project = game.projects.find_project(Project.BASE, crisis_top_tier[0])
                start = {
                    "name": project.name,
                    "type": Project.TYPES[project.type_],
                    "category": Graph.class_name(
                        game_def.graph.class_for_node[project.fixes]
                    ),
                    "node": game_def.graph.node_names[project.fixes],
                }
            return do_project(project, start, None, "top")

        if crisis_second_tier:
            self.debug("crisis_second_tier")
            # create a project for it, no tradeoffs
            found = None
            for project in crisis_second_tier:
                if game.projects.status(project) == ProjectState.AVAILABLE:
                    found = project
            if found:
                project = game.projects.find_project(Project.A, found)
                return do_project(
                    project,
                    {
                        "name": project.name,
                        "type": Project.TYPES[project.type_],
                        "category": Graph.class_name(
                            game_def.graph.class_for_node[project.fixes]
                        ),
                        "node": game_def.graph.node_names[project.fixes],
                    },
                    target_tech,
                    "medium",
                )
            # else, continue to third tier

        if crisis_third_tier:
            self.debug("crisis_third_tier")
            # same as before, but focus on research for top TOP_TIER%
            draw = [None, None]
            if target_tech.suit in [self.player_class.suit_a, self.player_class.suit_b]:
                draw[1] = target_tech.suit
            else:
                draw[0] = target_tech.suit

            # create a project for it, no tradeoffs
            found = None
            for project in crisis_third_tier:
                if game.projects.status(project) == ProjectState.AVAILABLE:
                    found = project
            if found:
                project = game.projects.find_project(Project.A, found)
                return do_project(
                    project,
                    {
                        "name": project.name,
                        "type": Project.TYPES[project.type_],
                        "category": Graph.class_name(
                            game_def.graph.class_for_node[project.fixes]
                        ),
                        "node": game_def.graph.node_names[project.fixes],
                    },
                    target_tech,
                    "low",
                    draw,
                )

        self.debug("crisis: other")
        # research and hoard cards for top TOP_TIER%
        draw = [None, None]
        if target_tech and target_tech.suit in [
            self.player_class.suit_a,
            self.player_class.suit_b,
        ]:
            draw[1] = target_tech.suit
        elif target_tech:
            draw[0] = target_tech.suit
        if draw[0] is None:
            draw[0] = rnd.choice(DrawPiles.SUITS)
        if draw[1] is None:
            draw[1] = rnd.choice([self.player_class.suit_a, self.player_class.suit_b])

        return {
            Player.PILE_DRAW: draw,
            Player.START_PROJECT: None,
            Player.START_RESEARCH: target_tech.name
            if target_tech
            and game.tech[target_tech.name]["status"] == TechTreeState.AVAILABLE
            else None,
        }, {}

    def analyze_cards(self, rnd, state, game, actions):
        """check the cards drawn and use them to fund project and tech using the priorities"""

        play_card = None
        in_hand = list(state.cards)
        money = state.resources["$"]
        if "project" in state.extra.phase_mem:
            project_prio = state.extra.phase_mem["project"]["priority"]
            project_name = state.extra.phase_mem["project"]["name"]

            needed = list(
                game.projects[project_name]["missing"]
                if project_name in game.projects
                else game.projects.project_for_name(project_name).cost
            )

            changes = True
            play_card = []
            while changes and needed:
                changes = False
                for idx, card in enumerate(in_hand):
                    if card[1] == 14:  # TODO smarter use of wildcards is possible
                        if project_prio in ["top", "medium"]:
                            changes = True
                            play_card.append((card, needed[0], project_name, 0))
                            del needed[0]
                            del in_hand[idx]
                            break
                        # else: keep it to myself
                    elif card[0] in needed:
                        changes = True
                        fee = 0  # TODO smarter allocation of money based on card values is possible
                        value = min(10, card[1] if card[1] > 1 else 10)
                        base_tech = game.tech.find_tech(Tech.BASE, card[0])
                        if game.tech.status(base_tech.name) == TechTreeState.RESEARCHED:
                            value += 1

                        if project_prio in ["top", "medium"]:
                            if money > 0 and value < 11:
                                fee = min(11 - value, money)
                        elif money > 1 and value < 10:
                            fee = min(10 - value, money - 1)  # leave one for research
                        money -= fee

                        play_card.append((card, card[0], project_name, fee))
                        del needed[needed.index(card[0])]
                        del in_hand[idx]
                        break
        # else: # all tech

        cards_for_research = []
        funds_for_research = []
        if state.tech:
            for idx, card in enumerate(in_hand):
                if card[0] == game.tech[state.tech[0]]["tech"].suit:
                    cards_for_research.append((card, card[0], state.tech[0]))
                    del in_hand[idx]
                    break
            if money > 0:
                funds_for_research.append(state.tech[0])
                money -= 1
        researching = list(game.tech.techs_for_status(TechTreeState.IN_PROGRESS))
        self.rnd.shuffle(researching)
        for tech in researching:
            if state.tech and tech.name == state.tech[0]:
                continue
            if len(in_hand) == 0 and money == 0:
                break
            if in_hand:
                for idx, card in enumerate(in_hand):
                    if card[0] == tech.suit:
                        cards_for_research.append((card, card[0], tech.name))
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
            self.order = list(game_def.graph.node_names)
            rnd.shuffle(self.order)
            self.importance = {name: idx for idx, name in enumerate(self.order)}

            self.cat_importance = {catid: 0 for (_, catid) in Graph.CATEGORIES}

            weight = 1.0
            for node in self.order:
                self.cat_importance[game_def.graph.class_for_node[node]] += weight
                weight *= GreedyPlayerState.CAT_DECAY

            self.phase_mem = {}

            self.debug("My top tier:")
            for idx, node in enumerate(self.order):
                if idx >= len(self.order) * GreedyPlayer.TOP_TIER:
                    break
                self.debug("\t" + game_def.graph.node_names[node])

    def debug(self, *args):
        """Debug print-outs, if flag is activated"""
        if GreedyPlayer.DEBUG:
            print(*args)

    def to_json(self):
        return {
            "order": self.order,
            "cat_importance": self.cat_importance,
            "phase_mem": self.phase_mem,
        }

    def copy(self):
        other = GreedyPlayerState()
        other.order = list(self.order)
        other.importance = dict(self.importance)
        other.cat_importance = dict(self.cat_importance)
        other.phase_mem = dict(self.phase_mem)
        return other
