# -*- coding: utf-8 -*-
# Copyright (C) 2021 Textualization Software Ltd.
# Distributed under the terms of the Apache Software License 2.0
# http://www.apache.org/licenses/LICENSE-2.0

import random

from .graph import Graph
from .player import Player, PlayerState
from .drawpiles import DrawPiles
from .definitions import GameDef
from .state import GraphState, ProjectState, TechTreeState
from .project import Projects, Project
from .techtree import Tech, TechTree
from .tojson import to_json


class GameState:
    def __init__(
        self,
        turn: int,
        phase: int,
        player: int,
        leader: int,
        game_def: GameDef,
        players_state: list,
        crisis_chips: int,
        graph_state: GraphState,
        techtree_state: TechTreeState,
        project_state: ProjectState,
        drawpiles_state: DrawPiles,
    ):
        self.turn = turn
        self.phase = phase
        self.player = player
        self.leader = leader
        self.game = game_def
        self.players = players_state
        self.crisis_chips = crisis_chips
        self.graph = graph_state
        self.projects = project_state
        self.tech = techtree_state
        self.drawpiles = drawpiles_state

    def to_json(self):
        return {
            "players": to_json(self.players),
            "player": self.player,
            "turn": self.turn,
            "phase": self.phase,
            "leader": self.leader,
            "crisis_chips": self.crisis_chips,
            "graph": self.graph.to_json(),
            "tech": self.tech.to_json(),
            "projects": self.projects.to_json(),
            "piles": self.drawpiles.to_json(),
        }

    def copy(self):
        return GameState(
            self.turn,
            self.phase,
            self.player,
            self.leader,
            self.game,
            list(map(lambda x: x.copy(), self.players)),
            self.crisis_chips,
            self.graph.copy(),
            self.tech.copy(),
            self.projects.copy(),
            self.drawpiles.copy(),
        )


class Game:

    PHASES = ["ENGAGE", "ACTIVATE", "END"]
    STEPS_PER_PHASE = {
        "ENGAGE": ["DRAWING MONEY", "DRAWING CARDS", "CRISIS RISING"],
        "ACTIVATE": ["ATTEMPTING PROJECTS", "DOING RESEARCH"],
        "END": ["FINALIZING", "CRISIS ROLLING"],
    }

    L_DICE_ROLL = "Dice roll {}D6: {}"
    L_MONEY_DRAWN = "Money drawn"
    L_CARD_DRAWN = "Card drawn: {}"
    L_PROJECT_TYPE = "Start project: type"
    L_PROJECT_CAT = "Start project: fix category"
    L_PROJECT_NODE = "Start project: fix problem"
    L_PROJECT_STARTED = "Project started"
    L_SKILL_PROJECT = "Skill for project"
    L_USING_TECH = 'Using tech "{}"'
    L_CONSULTANT_FEES = "Consultant fees"
    L_CHIP_ADDED = "Added a crisis chip"
    L_ROLL_SUCCEEDED = "Dice roll succeeded"
    L_ROLL_FAILED = "Dice roll failed"
    L_START_RESEARCH = "Start researching"
    L_SKILL_FOR_RESEARCH = "Skill for research"
    L_FUNDS_FOR_RESEARCH = "Funds for research"
    L_ABANDON_RESEARCH = "Removing repeated tech started by {}"
    L_OVERSKILLED = "Tech project overskilled by {}"
    L_OVERFUNDED = "Tech project overfunded by {}"
    L_RESEARCH_CYCLE = "Research cycle finished, remain: {}"
    L_RESEARCHED = "Tech researched"
    L_AUTO_PROTECTED = "Problem auto-protected"
    L_PROTECTED = "Problem protected"
    L_RESEARCH_SAVES_ROLL = 'New project finished boosts roll for project "{}"'
    L_FUNDED_NOT_SKILLED = "Tech funded but not skilled, ignoring"
    L_SKILLED_NOT_FUNDED = "Tech skilled but not funded, ignoring"
    L_PROJECT_ABANDONED = "Project abandoned"
    L_PROJECT_OVERSKILLED = 'Project overskilled for "{}"'
    L_PROJECT_FINISHED = "Project finished"
    L_CRISIS_FIX_PROJECT = "Crisis resolved (project: {})"
    L_CRISIS_CHIP_TRIGGERED = "Crisis chip added (trade-off from project: {})"
    L_CHIP_FULL_CAT = "Crisis chip: full category"
    L_CRISIS_CAT = "Category for crisis"
    L_CHIP_SATURATED = "Crisis chip: overwhelmed problem"
    L_CRISIS_NODE = "Problem for crisis"
    L_CRISIS_ROLL = 'Crisis roll for node "{}"'
    L_CRISIS_AVERTED = "Crisis averted"
    L_IN_CRISIS = "Now in crisis"
    L_PROT_LOSS = "Lost protection"
    L_IN_CRISIS_CASCADE = "Now in crisis (cascaded from: {})"
    L_PROT_LOSS_CASCADE = "Lost protection (cascaded from: {})"

    def __init__(self, game_def: GameDef, players: list):
        self.game_def = game_def
        self.players = players
        self.log = list()
        self.phase_start_state = None
        self.phase_actions = None

    def roll_dice(self, num, player, memo, rand, step):
        result = 0
        for idx in range(num):
            result += self.players[player].roll(
                "{}, {} of {}".format(memo, idx + 1, num), rand, 6
            )
        self.log.append(
            {
                "phase": Game.PHASES[self.state.phase],
                "step": Game.STEPS_PER_PHASE[Game.PHASES[self.state.phase]][step],
                "target": result,
                "memo": Game.L_DICE_ROLL,
                "args": [num, memo],
                "state": self.state.to_json(),
            }
        )
        return result

    ### GAME INIT
    ###
    ### Each player chooses a class (see table at the end).
    ###
    ###      Decision CLASS
    ###
    ### All players have 1 research slot and 1 project slot.
    ###
    ### The can contribute to research and projects from any other player but not in the turn the project or research is started.

    def start(self, rand):
        self.finished = False
        drawpiles = DrawPiles(rand)
        player_state = [PlayerState(p, {"!": 0, "$": 0}, list()) for p in self.players]
        graph_state = self.game_def.game_init.graph.copy()

        self.state = GameState(
            0,
            0,
            0,
            0,
            self.game_def,
            player_state,
            0,
            graph_state,
            TechTreeState(self.game_def.tech),
            ProjectState(self.game_def.projects),
            drawpiles,
        )
        self.log = list()
        self.phase_start_state = None
        self.phase_actions = None

        # ask players to pick roles
        classes_to_pick = sorted(self.game_def.classes.names())
        for idx in range(self.game_def.num_players):
            class_for_player = self.players[idx].pick(
                Player.INIT_ROLE,
                classes_to_pick,
                rand,
                self.state.players[idx],
                self.state,
                {"game_def": self.game_def},
            )
            self.players[idx].set_class(
                self.game_def.classes.class_for_name(class_for_player)
            )
            del classes_to_pick[classes_to_pick.index(class_for_player)]

    def advance(self):
        "Returns True is the game has ended"
        if self.finished or len(self.state.graph.are_in_crisis()) == len(
            self.game_def.graph
        ):
            self.finished = True
        else:
            self.state.player += 1
            if self.state.player == self.game_def.num_players:
                self.state.player = 0
                self.state.phase += 1
                if self.state.phase == len(Game.PHASES):
                    self.state.phase = 0
                    self.state.turn += 1
                    self.state.leader = (
                        self.state.leader + 1
                    ) % self.game_def.num_players
        return self.finished

    def cascade(self, node):
        "A node in crisis has been selected, deal with it. Returns the activated nodes."
        result = list()
        outlinks = list(self.game_def.graph.outlinks[node])
        for outlink in outlinks:
            outlinkn = self.game_def.graph.node_names[outlink]
            if self.state.graph[outlinkn]["status"] != GraphState.IN_CRISIS:
                result.append(outlink)
        if result:
            return result
        # use list
        for other in self.game_def.cascades.cascade[node]:
            othern = self.game_def.graph.node_names[other]
            if self.state.graph[othern]["status"] != GraphState.IN_CRISIS:
                return [other]
        raise Error("Cascading on saturated node: {}".format(node))

    ###
    ###
    ### TURN
    ###

    def step(self, rand):
        phase = Game.PHASES[self.state.phase]
        if self.state.phase == 0:  # engage
            if self.state.player == 0:
                self.phase_start_state = self.state.copy()

            ###   ENGAGE PHASE
            ###
            ###   	for each player in parallel, without knowing what the other players do, they do, in order:
            ###

            ###
            ###   	DRAWING MONEY
            ###         	The player draws a number of money units equals to
            ###             	5 - number of crisis in category 'ECONOMIC'
            drawn = max(0, 5 - len(self.state.graph.are_in_crisis("ECONOMIC")))
            self.state.players[self.state.player].resources["$"] += drawn
            self.log.append(
                {
                    "phase": phase,
                    "step": Game.STEPS_PER_PHASE[phase][0],
                    "target": drawn,
                    "memo": Game.L_MONEY_DRAWN,
                    "state": self.state.to_json(),
                }
            )
            ###
            ###   	DRAWING CARDS
            ###         	The player draws two cards. The first card can be from any pile. The second has to be from the two suits associated with the player's class:
            ###
            ###             	Decision PILE_DRAW: decide from which of the 4 piles to draw a card
            ###             	Decision PILE_DRAW: decide from which of the 2 piles to draw a card
            ###
            ###            If a suit pile is consumed, shuffle the discard pile and set it as the new pile for the suit.

            accessible_piles = sorted(list(DrawPiles.SUITS))

            draw_pile = self.players[self.state.player].pick(
                Player.PILE_DRAW,
                accessible_piles,
                rand,
                self.state.players[self.state.player],
                self.phase_start_state,
                {"game_def": self.game_def},
            )
            drawn = self.state.drawpiles.draw(draw_pile, rand)
            self.state.players[self.state.player].cards.append(drawn)
            self.log.append(
                {
                    "phase": phase,
                    "step": Game.STEPS_PER_PHASE[phase][1],
                    "target": drawn,
                    "memo": Game.L_CARD_DRAWN,
                    "args": [1],
                    "state": self.state.to_json(),
                }
            )
            accessible_piles = set(
                [
                    self.players[self.state.player].player_class.suit_a,
                    self.players[self.state.player].player_class.suit_b,
                ]
            )
            accessible_piles = sorted(list(accessible_piles))

            draw_pile = self.players[self.state.player].pick(
                Player.PILE_DRAW,
                accessible_piles,
                rand,
                self.state.players[self.state.player],
                self.phase_start_state,
                {"game_def": self.game_def},
            )
            drawn = self.state.drawpiles.draw(draw_pile, rand)
            self.state.players[self.state.player].cards.append(drawn)
            self.log.append(
                {
                    "phase": phase,
                    "step": Game.STEPS_PER_PHASE[phase][1],
                    "target": drawn,
                    "memo": Game.L_CARD_DRAWN,
                    "args": [2],
                    "state": self.state.to_json(),
                }
            )
            ###
            ###   	CRISIS RISING
            ###         	Two crisis chip are added per turn
            if self.state.player == 0:
                self.state.crisis_chips += (
                    self.game_def.crisis_rising
                )  # + len(self.state.players) - 3
                self.log.append(
                    {
                        "phase": phase,
                        "step": Game.STEPS_PER_PHASE[phase][2],
                        "state": self.state.to_json(),
                    }
                )
        elif self.state.phase == 1:  # activate
            if self.state.player == 0:
                self.phase_start_state = self.state.copy()
                self.phase_actions = list()
            ###
            ###   ACTIVATE PHASE
            ###
            ###  	Once the engage phase is completed by all players, the players can see what suits the players picked.
            ###
            ###  	Then the activate phase starts, again, parallel blind.
            ###
            ###  	The actions recorded separately by each player are presented in the next section
            ###
            ###        	Each player performs the actions described
            ###
            ###  	ATTEMPTING PROJECTS
            ###

            ## decide whether to start a new project?

            ###         	If the player has project slots available, the player has to decide whether to start a project of a given type or not start any project:
            ###
            ###         	Decision START_PROJECT: Choose between the two types of projects (base or remove-tradeoff) or nothing to not start a project this turn. Base projects add an extra crisis chip.
            ###
            ###         	If the player picked a project type to start, then the player decides which category of problem they want to fix with their project:
            ###
            ###             	Decision START_PROJECT_FIX_CAT: Choose among the six categories of problems.
            ###
            ###             	With the chosen category, the player can choose which problem to fix:
            ###
            ###             	Decision START_PROJECT_FIX_NODE: choose among all the problems in that category
            ###
            ###             	With the above decisions, the new project is created, added to the player project slot.
            ###
            ###             	Phase action recorded: START_PROJECT (project)

            start = False
            if self.state.players[self.state.player].available_project_slots():
                project_type = self.players[self.state.player].pick(
                    Player.START_PROJECT,
                    Project.TYPES + [None],
                    rand,
                    self.state.players[self.state.player],
                    self.phase_start_state,
                )
                self.log.append(
                    {
                        "phase": phase,
                        "step": Game.STEPS_PER_PHASE[phase][0],
                        "target": project_type,
                        "memo": Game.L_PROJECT_TYPE,
                        "state": self.state.to_json(),
                    }
                )
                start = project_type is not None
                if start:
                    fix_cat = self.players[self.state.player].pick(
                        Player.START_PROJECT_FIX_CAT,
                        sorted(list(map(lambda x: x[0], Graph.CATEGORIES))),
                        rand,
                        self.state.players[self.state.player],
                        self.phase_start_state,
                    )
                    self.log.append(
                        {
                            "phase": phase,
                            "step": Game.STEPS_PER_PHASE[phase][0],
                            "target": fix_cat,
                            "memo": Game.L_PROJECT_CAT,
                            "state": self.state.to_json(),
                        }
                    )
                    fix_cat_id = self.game_def.graph.category_for_name[fix_cat]
                    fix_node = self.players[self.state.player].pick(
                        Player.START_PROJECT_FIX_NODE,
                        sorted(
                            list(
                                map(
                                    lambda x: self.game_def.graph.node_names[x],
                                    self.game_def.graph.node_classes[fix_cat_id],
                                )
                            )
                        ),
                        rand,
                        self.state.players[self.state.player],
                        self.phase_start_state,
                    )
                    self.log.append(
                        {
                            "phase": phase,
                            "step": Game.STEPS_PER_PHASE[phase][0],
                            "target": fix_node,
                            "memo": Game.L_PROJECT_NODE,
                            "state": self.state.to_json(),
                        }
                    )
                    fix_node_id = self.game_def.graph.name_to_id[fix_node]

                    project_type_ = Project.TYPES.index(project_type)

                    project = self.state.projects.find_project(
                        project_type_, fix_node_id
                    )

                    self.log.append(
                        {
                            "phase": phase,
                            "step": Game.STEPS_PER_PHASE[phase][0],
                            "target": project.name,
                            "memo": Game.L_PROJECT_STARTED,
                            "state": self.state.to_json(),
                        }
                    )
                    self.state.projects.player_starts(
                        project, self.state.player, self.state.turn
                    )
                    self.state.players[self.state.player].projects.append(project.name)
                    self.phase_actions.append(
                        (self.state.player, Game.A_START_PROJECT, project)
                    )
                    started_project = project

            ## play cards for any projects

            ###
            ###         	After potentially creating a new project, the player can decide to play cards for any projects.
            ###
            ###         	That includes projects existing at the beginning of the phase or projects the player has created this turn (but not projects created by other players this phase).
            ###
            ###         	The player is then presented with a choice of playing a particular card for a particular project or nothing to stop playing cards.
            ###
            ###         	While the player does not choose to play nothing and there are cards that can be played against available projects:
            ###
            ###
            ###                 	Decision PLAY_CARD: Choose a card and a project to play it for
            ###
            ###                 	If the card is a joker, it automatically succeeds.
            ###
            ###                 	If the card is not a joker, the value of the card is its face value or 10 if the card is Ace, Knight, Queen or King.
            ###
            ###                      	To the value of the card, if the table has researched a base technology for the skill, the value is increased by 1. The value cannot exceed 11.
            ###
            ###                      	To the value of the card, if the table has researched an expanded technology for the skill, the value is further increased by 2. The value cannot exceed 11.
            ###
            ###                      	To this value, the player can decide to use money units (if the player has them) as consultant fees to further increase its value:
            ###
            ###                          	Decision CONSULTANT: Choose between 0 to the minimum between the amount of money the player has and the number that will take the current value to 11.
            ###
            ###                      	The final value to roll against (card value + research boost + consultant fees) is then rolled with 2D6:
            ###
            ###                      	Roll Skill Check: 2D6
            ###
            ###                      	If the roll is less or equal to the value, the check is successful:
            ###
            ###                         	Phase action recorded: SUCCESS_SKILL (project, card, value, roll)
            ###
            ###                      	If the roll is greater than value, the check failed:
            ###
            ###                         	Phase action recorded: FAILED_SKILL (project, card, value, roll)
            ###
            ###                      	If the roll equals 12, a crisis chip is added to the turn, immediately.
            ###
            ###                      	The cards used are thrown to the discard piles for each suit, with the jokers being returned to the pile of the suit they were used in replacement (not necessarily the suit they were taken from).

            in_progress = self.phase_start_state.projects.projects_for_status(
                ProjectState.IN_PROGRESS
            )
            if start:
                in_progress.append(started_project)

            card_choices = list()
            for idx, card in enumerate(self.state.players[self.state.player].cards):
                projects_for_card = list()
                for project in in_progress:
                    missing = set(self.state.projects[project.name]["missing"])
                    if card[1] == 14:
                        for s in missing:
                            projects_for_card.append((project, s))
                    elif card[0] in missing:
                        projects_for_card.append((project, card[0]))
                for project, suit in projects_for_card:
                    card_choices.append((card, suit, idx, project.name))
            card_choices = sorted(card_choices)

            while True:
                if None not in card_choices:
                    card_choices.append(None)
                if len(card_choices) <= 1:
                    break

                play_card = self.players[self.state.player].pick(
                    Player.PLAY_CARD,
                    card_choices,
                    rand,
                    self.state.players[self.state.player],
                    self.phase_start_state,
                    {"game_def": self.game_def},
                )
                self.log.append(
                    {
                        "phase": phase,
                        "step": Game.STEPS_PER_PHASE[phase][0],
                        "target": play_card,
                        "memo": Game.L_SKILL_PROJECT,
                        "state": self.state.to_json(),
                    }
                )
                if play_card is None:
                    break

                succeeded = False
                if play_card[0][1] == 14:  # joker
                    succeeded = True
                    roll = -1
                    value = -1
                else:
                    value = min(10, play_card[0][1] if play_card[0][1] > 1 else 10)
                    base_tech = self.state.tech.find_tech(Tech.BASE, play_card[0][0])
                    expanded_tech = self.state.tech.find_tech(Tech.A, play_card[0][0])

                    if (
                        self.state.tech.status(base_tech.name)
                        == TechTreeState.RESEARCHED
                    ):
                        value += 1
                        self.log.append(
                            {
                                "phase": phase,
                                "step": Game.STEPS_PER_PHASE[phase][0],
                                "target": 1,
                                "memo": Game.L_USING_TECH,
                                "args": [base_tech.name],
                                "state": self.state.to_json(),
                            }
                        )
                    if (
                        self.state.tech.status(expanded_tech.name)
                        == TechTreeState.RESEARCHED
                    ):
                        base = value
                        value = min(11, value + 2)
                        if base > value:
                            self.log.append(
                                {
                                    "phase": phase,
                                    "step": Game.STEPS_PER_PHASE[phase][0],
                                    "target": (value - base),
                                    "memo": Game.L_USING_TECH,
                                    "args": [expanded_tech.name],
                                    "state": self.state.to_json(),
                                }
                            )

                    if (
                        value < 11
                        and self.state.players[self.state.player].resources["$"] > 0
                    ):
                        moneys = min(
                            11 - value,
                            self.state.players[self.state.player].resources["$"],
                        )

                        consultant = self.players[self.state.player].pick(
                            Player.CONSULTANT,
                            list(range(moneys + 1)),
                            rand,
                            self.state.players[self.state.player],
                            self.phase_start_state,
                        )
                        self.log.append(
                            {
                                "phase": phase,
                                "step": Game.STEPS_PER_PHASE[phase][0],
                                "target": consultant,
                                "memo": Game.L_CONSULTANT_FEES,
                                "state": self.state.to_json(),
                            }
                        )
                        self.state.players[self.state.player].resources[
                            "$"
                        ] -= consultant
                        value += consultant

                    roll = self.roll_dice(2, self.state.player, "skill check", rand, 0)
                    if roll <= value:
                        succeeded = True
                    if roll == 12:
                        self.state.crisis_chips += 1
                        self.log.append(
                            {
                                "phase": phase,
                                "step": Game.STEPS_PER_PHASE[phase][0],
                                "target": 1,
                                "memo": Game.L_CHIP_ADDED,
                                "state": self.state.to_json(),
                            }
                        )

                if succeeded:
                    self.phase_actions.append(
                        (
                            self.state.player,
                            Game.A_SUCCESS_SKILL,
                            self.state.projects[play_card[3]]["project"],
                            play_card,
                            roll,
                            value,
                        )
                    )
                    self.log.append(
                        {
                            "phase": phase,
                            "step": Game.STEPS_PER_PHASE[phase][0],
                            "target": roll,
                            "memo": Game.L_ROLL_SUCCEEDED,
                            "state": self.state.to_json(),
                        }
                    )
                else:
                    self.phase_actions.append(
                        (
                            self.state.player,
                            Game.A_FAILED_SKILL,
                            self.state.projects[play_card[3]]["project"],
                            play_card,
                            roll,
                            value,
                        )
                    )
                    self.log.append(
                        {
                            "phase": phase,
                            "step": Game.STEPS_PER_PHASE[phase][0],
                            "target": roll,
                            "memo": Game.L_ROLL_FAILED,
                            "state": self.state.to_json(),
                        }
                    )

                # closing the project is left to the end phase
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

            ###
            ###  	DOING RESEARCH
            ###
            ###         	If the player has research slots available, the player has to decide whether to start research on a specific technology or not start researching at:
            ###
            ###         	Decision START_RESEARCH: Choose between the research boundary (tech that can be researched given what we know already) or not starting new research.
            ###            	If the player decided to start researching new technology, it is added to the player's research slot:
            ###
            ###                 	Phase action recorded: START_RESEARCH (tech)

            # research
            start = False
            if self.state.players[self.state.player].available_research_slots():
                boundary = self.phase_start_state.tech.research_boundary()
                chosen_tech = self.players[self.state.player].pick(
                    Player.START_RESEARCH,
                    sorted(list(map(lambda x: x.name, boundary))) + [None],
                    rand,
                    self.state.players[self.state.player],
                    self.phase_start_state,
                )
                self.log.append(
                    {
                        "phase": phase,
                        "step": Game.STEPS_PER_PHASE[phase][1],
                        "target": chosen_tech,
                        "memo": Game.L_START_RESEARCH,
                        "state": self.state.to_json(),
                    }
                )
                start = chosen_tech is not None
                if start:
                    tech = self.state.tech[chosen_tech]["tech"]
                    self.state.tech.player_starts(
                        tech, self.state.player, self.state.turn
                    )
                    self.state.players[self.state.player].tech.append(tech.name)
                    self.phase_actions.append(
                        (self.state.player, Game.A_START_RESEARCH, tech)
                    )
                    started_tech = tech

            researching = self.state.tech.techs_for_status(TechTreeState.IN_PROGRESS)
            if start:
                researching.append(started_tech)
            ###
            ###         	After potentially starting a new research, the player can decide to contribute skills or funds to any tech currently being researched either by the player itself or by others (but not new tech which research started by other players this phase).
            ###
            ###         	While the player has cards that can be contributed to techs being researched the player hasn't yet contributed to, or the player decides not to contribute cards to any further research:
            ###
            ###                 	Decision CARD_FOR_RESEARCH: Choose a card and a tech to contribute that card or nothing to stop contributing cards
            ###
            ###                 	If the player chose a card to contribute to a specific tech research efforts:
            ###
            ###                         	Phase action recorded: SKILL_RESEARCH (tech, card)
            ###
            ###
            ###                         	Discard the card to the suitable draw pile
            ###

            ## cards for research
            cards_for_tech = list()
            for idx, card in enumerate(self.state.players[self.state.player].cards):
                for tech in researching:
                    if card[0] == tech.suit or card[1] == 14:
                        cards_for_tech.append((tech.name, card, idx, tech.suit))
            cards_for_tech = sorted(cards_for_tech)

            while True:
                if None not in cards_for_tech:
                    cards_for_tech.append(None)

                if len(cards_for_tech) <= 1:
                    break

                chosen_card_for_tech = self.players[self.state.player].pick(
                    Player.CARD_FOR_RESEARCH,
                    cards_for_tech,
                    rand,
                    self.state.players[self.state.player],
                    self.phase_start_state,
                )
                self.log.append(
                    {
                        "phase": phase,
                        "step": Game.STEPS_PER_PHASE[phase][1],
                        "target": chosen_card_for_tech,
                        "memo": Game.L_SKILL_FOR_RESEARCH,
                        "state": self.state.to_json(),
                    }
                )
                if chosen_card_for_tech is None:
                    break
                self.phase_actions.append(
                    (
                        self.state.player,
                        Game.A_SKILL_RESEARCH,
                        chosen_card_for_tech[1],
                        self.state.tech[chosen_card_for_tech[0]]["tech"],
                    )
                )
                self.state.drawpiles.return_card(
                    chosen_card_for_tech[1], chosen_card_for_tech[3]
                )
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

            ###
            ###         	While the player has money units to contribute to any techs being researched the player hasn't yet contributed to, or the player decides not to contribute money units to any further research:
            ###
            ###                 	Decision FUND_RESEARCH: Choose a tech to contribute a money unit or nothing to stop contributing money units
            ###
            ###                 	If the player chose a card to contribute to a specific tech research efforts:
            ###
            ###                         	Phase action recorded: FUND_RESEARCH (tech)

            ## funds for research
            to_fund = sorted(researching, key=lambda x: x.name)

            while True:
                if self.state.players[self.state.player].resources["$"] == 0:
                    break
                if None not in to_fund:
                    to_fund.append(None)

                if len(to_fund) <= 1:
                    break

                chosen_to_fund = self.players[self.state.player].pick(
                    Player.FUND_RESEARCH,
                    list(map(lambda x: None if x is None else x.name, to_fund)),
                    rand,
                    self.state.players[self.state.player],
                    self.phase_start_state,
                )
                self.log.append(
                    {
                        "phase": phase,
                        "step": Game.STEPS_PER_PHASE[phase][1],
                        "target": chosen_to_fund,
                        "memo": Game.L_FUNDS_FOR_RESEARCH,
                        "state": self.state.to_json(),
                    }
                )
                if chosen_to_fund is None:
                    break
                self.phase_actions.append(
                    (
                        self.state.player,
                        Game.A_FUND_RESEARCH,
                        self.state.tech[chosen_to_fund]["tech"],
                    )
                )
                self.state.players[self.state.player].resources["$"] -= 1

                for idx, tech in enumerate(to_fund):
                    if tech is not None and tech.name == chosen_to_fund:
                        break
                del to_fund[idx]

        else:  # the end
            if self.state.player != self.state.leader:
                pass
            else:
                ###
                ###     END
                ###
                ###	FINALIZING
                ###
                ###         	Research
                ###
                ###         	See if many players started researching the same tech. Keep the one from the lower player (the resources are aggregated).
                ###
                ###         	Check for techs that were over-funded or over-skilled and report them. Techs that were fully (or over-) skilled and funded can count the turn as a research cycle.
                ###
                ###         	Techs that were under-funded or under-skilled do not get to count the turn as a research cycle.
                ###
                ###         	See if any of the techs was researched, for all techs that were researched, they clear the player's research slot and check whether a consultant bump in the FAILED_SKILL checks would change them. For auto-protect technologies, if the problem auto-protected is fixed, then it gets protected.

                ## see if two players started researching the same tech and close the one with less resources applied to it
                tech_started = [
                    (p[2], p[0])
                    for p in self.phase_actions
                    if p[1] == Game.A_START_RESEARCH
                ]
                counts = dict()
                for tech, player in tech_started:
                    counts[tech.name] = counts.get(tech.name, list()) + [player]
                for n, players in sorted(counts.items()):
                    players = sorted(players)
                    for p in players[1:]:
                        self.state.players[p].tech.remove(n)
                        self.log.append(
                            {
                                "phase": phase,
                                "step": Game.STEPS_PER_PHASE[phase][0],
                                "target": n,
                                "memo": Game.L_ABANDON_RESEARCH,
                                "args": [players[0]],
                                "state": self.state.to_json(),
                            }
                        )
                    self.state.tech[n]["player"] = players[0]

                ## see if any of the techs was researched and apply its actions
                for tech in self.state.tech.techs_for_status(TechTreeState.IN_PROGRESS):
                    # got skill and funds this turn?
                    skills = 0
                    funds = 0
                    for act in self.phase_actions:
                        if act[1] == Game.A_SKILL_RESEARCH and act[3] == tech:
                            skills += 1
                        elif act[1] == Game.A_FUND_RESEARCH and act[2] == tech:
                            funds += 1
                    if skills == 0 and funds == 0:
                        continue
                    if skills >= 1 and funds >= 1:
                        if skills >= 0:
                            self.log.append(
                                {
                                    "phase": phase,
                                    "step": Game.STEPS_PER_PHASE[phase][0],
                                    "target": tech.name,
                                    "memo": Game.L_OVERSKILLED,
                                    "args": [skills - 1],
                                    "state": self.state.to_json(),
                                }
                            )
                        if funds >= 0:
                            self.log.append(
                                {
                                    "phase": phase,
                                    "step": Game.STEPS_PER_PHASE[phase][0],
                                    "target": tech.name,
                                    "memo": Game.L_OVERFUNDED,
                                    "args": [funds - 1],
                                    "state": self.state.to_json(),
                                }
                            )
                        self.state.tech[tech.name]["missing_turns"] -= 1

                        if self.state.tech[tech.name]["missing_turns"] > 0:
                            self.log.append(
                                {
                                    "phase": phase,
                                    "step": Game.STEPS_PER_PHASE[phase][0],
                                    "target": tech.name,
                                    "memo": Game.L_RESEARCH_CYCLE,
                                    "args": [
                                        self.state.tech[tech.name]["missing_turns"]
                                    ],
                                    "state": self.state.to_json(),
                                }
                            )
                        else:
                            # finished!
                            self.state.tech.finish(tech.name)
                            tech_player = self.state.tech[tech.name]["player"]
                            del self.state.players[tech_player].tech[
                                self.state.players[tech_player].tech.index(tech.name)
                            ]

                            self.log.append(
                                {
                                    "phase": phase,
                                    "step": Game.STEPS_PER_PHASE[phase][0],
                                    "target": tech.name,
                                    "memo": Game.L_RESEARCHED,
                                    "state": self.state.to_json(),
                                }
                            )

                            if tech.type_ == Tech.BASE or tech.type_ == Tech.A:
                                # see if any failed roll would have succeeded with the extra boost
                                boost = 1 if tech.type_ == Tech.BASE else 2
                                for idx, act in enumerate(self.phase_actions):
                                    if (
                                        act[1] == Game.A_FAILED_SKILL
                                        and act[3][1] == tech.suit
                                        and act[-2] <= act[-1] + boost
                                    ):
                                        self.log.append(
                                            {
                                                "phase": phase,
                                                "step": Game.STEPS_PER_PHASE[phase][0],
                                                "target": act[2],
                                                "memo": Game.L_RESEARCH_SAVES_ROLL,
                                                "args": [act[2]],
                                                "state": self.state.to_json(),
                                            }
                                        )
                                        self.phase_actions[idx] = (
                                            act[0],
                                            Game.A_SUCCESS_SKILL,
                                            act[2],
                                            act[3],
                                            act[4],
                                            act[5] + boost,
                                        )
                            elif tech.type_ == Tech.B:
                                # auto-protect, apply protection
                                node = self.game_def.graph.node_names[tech.node]
                                self.state.graph[node]["auto-protected"] = True
                                self.log.append(
                                    {
                                        "phase": phase,
                                        "step": Game.STEPS_PER_PHASE[phase][0],
                                        "target": node,
                                        "memo": Game.L_AUTO_PROTECTED,
                                        "state": self.state.to_json(),
                                    }
                                )

                                if (
                                    self.state.graph[node]["status"]
                                    == GraphState.STABLE
                                ):
                                    self.state.graph[node][
                                        "status"
                                    ] = GraphState.PROTECTED
                                    self.log.append(
                                        {
                                            "phase": phase,
                                            "step": Game.STEPS_PER_PHASE[phase][0],
                                            "target": node,
                                            "memo": Game.L_PROTECTED,
                                            "state": self.state.to_json(),
                                        }
                                    )
                    else:
                        if skills == 0:
                            self.log.append(
                                {
                                    "phase": phase,
                                    "step": Game.STEPS_PER_PHASE[phase][0],
                                    "target": tech.name,
                                    "memo": Game.L_FUNDED_NOT_SKILLED,
                                    "state": self.state.to_json(),
                                }
                            )
                        elif funds == 0:
                            self.log.append(
                                {
                                    "phase": phase,
                                    "step": Game.STEPS_PER_PHASE[phase][0],
                                    "target": tech.name,
                                    "memo": Game.L_SKILLED_NOT_FUNDED,
                                    "state": self.state.to_json(),
                                }
                            )

                ###         	Projects
                ###
                ###         	See if many players started the same project. Keep the one from the lower player (the resources are aggregated).
                ###
                ###         	See if any of the projects had no skill applied to them and discard them. The projects are considered abandoned and the project slot from the player carrying the project is freed.
                ###
                ###         	See if any of the projects were finished and apply their actions. Check whether any of the projects got over-skilled and report.
                ###
                ###                 	To apply the actions, the problem fixed by the project is fixed. If the tech associated with auto-protecting that problem has been researched (even in this turn), it gets protected.
                ###
                ###                 	If the project has a trade-off associated, add the crisis chip.
                ###
                ###                 	The project slot associated with the project for the corresponding player is freed.

                ## see if any of the projects had no action and should be discarded
                for project in self.state.projects.projects_for_status(
                    ProjectState.IN_PROGRESS
                ):
                    # got skill this turn?

                    skilled = False
                    for act in self.phase_actions:
                        if (
                            act[1] in set([Game.A_SUCCESS_SKILL, Game.A_FAILED_SKILL])
                            and act[2] == project
                        ):
                            skilled = True
                            break
                    if not skilled:
                        proj_player = self.state.projects[project.name]["player"]
                        self.state.projects.abandon(project.name)
                        del self.state.players[proj_player].projects[
                            self.state.players[proj_player].projects.index(project.name)
                        ]

                        self.log.append(
                            {
                                "phase": phase,
                                "step": Game.STEPS_PER_PHASE[phase][0],
                                "target": project.name,
                                "memo": Game.L_PROJECT_ABANDONED,
                                "state": self.state.to_json(),
                            }
                        )

                ## see if any of the projects was finished and apply its actions
                # print("actions", "\n".join(map(str,self.phase_actions)))
                for project in self.state.projects.projects_for_status(
                    ProjectState.IN_PROGRESS
                ):
                    for act in self.phase_actions:
                        if act[1] == Game.A_SUCCESS_SKILL and act[2] == project:
                            missing = self.state.projects[project.name]["missing"]
                            if act[3][1] not in missing:
                                self.log.append(
                                    {
                                        "phase": phase,
                                        "step": Game.STEPS_PER_PHASE[phase][0],
                                        "target": project.name,
                                        "memo": Game.L_PROJECT_OVERSKILLED,
                                        "args": [act[3][0]],
                                        "state": self.state.to_json(),
                                    }
                                )
                            else:
                                del missing[missing.index(act[3][1])]
                                self.state.projects[project.name]["missing"] = missing
                    # print("ONGOING:", project.name, "missing", self.state.projects[project.name]['missing'])
                    if len(self.state.projects[project.name]["missing"]) == 0:
                        # finished
                        proj_player = self.state.projects[project.name]["player"]
                        self.state.projects.finish(project.name)
                        del self.state.players[proj_player].projects[
                            self.state.players[proj_player].projects.index(project.name)
                        ]

                        self.log.append(
                            {
                                "phase": phase,
                                "step": Game.STEPS_PER_PHASE[phase][0],
                                "target": project.name,
                                "memo": Game.L_PROJECT_FINISHED,
                                "state": self.state.to_json(),
                            }
                        )

                        # apply effects
                        fixn = self.game_def.graph.node_names[project.fixes]
                        if self.state.graph[fixn]["status"] == GraphState.IN_CRISIS:
                            if self.state.graph[fixn]["auto-protected"]:
                                self.state.graph[fixn]["status"] = GraphState.PROTECTED
                            else:
                                self.state.graph[fixn]["status"] = GraphState.STABLE

                            self.log.append(
                                {
                                    "phase": phase,
                                    "step": Game.STEPS_PER_PHASE[phase][0],
                                    "target": fixn,
                                    "memo": Game.L_CRISIS_FIX_PROJECT,
                                    "args": [project.name],
                                    "state": self.state.to_json(),
                                }
                            )

                        if project.triggers:
                            self.state.crisis_chips += 1
                            self.log.append(
                                {
                                    "phase": phase,
                                    "step": Game.STEPS_PER_PHASE[phase][0],
                                    "target": 1,
                                    "memo": Game.L_CRISIS_CHIP_TRIGGERED,
                                    "args": [project.name],
                                    "state": self.state.to_json(),
                                }
                            )

                ###  	CRISIS ROLLING
                ###
                ###             	Before the crisis rolling the players can talk with each other, strategize and discuss what to do depending on the different problems that will get in crisis. The crisis rolling is silent.
                ###
                ###             	Add crisis chip for each category fully in crisis.
                ###
                ###             	While the whole graph is not in crisis and there are still crisis chips:
                ###
                ###                 	Roll Category (1D6), if the category is fully in crisis, add a crisis chip and roll again
                ###
                ###                 	Roll Problem-in-category (1D6 using the numbers in the graph).
                ###
                ###                 	If the problem is saturated (it is in crisis and all its reachable problems are also in crisis), add a crisis chip and start again. If this happens ten times in a row, then the game is lost.
                ###
                ###                 	With the problem in hand, check whether the problem is already in crisis and all its direct outflows are already in crisis. If that is the case, use the list attached at the end of this document (one list per node) and mark in crisis or remove the protection if they were protected for as many nodes in the list as crisis chips remain. If there are more crisis chips than nodes that can be changed, keep the remaining crisis chips and continue (select another category, node, etc.). Otherwise (if the node is not in crisis or not all its outflows are in crisis), roll crisis chips until either the roll is successful or all the crisis chips are exhausted
                ###
                ###                 	While there are crisis chips or the problem is in crisis:
                ###
                ###                        	Roll Crisis (2D6), if crisis roll < 7, the node is in crisis
                ###
                ###                        	remove one crisis chip per roll (successful or otherwise)
                ###
                ###                 	If the problem should be marked in crisis:
                ###
                ###                        	If the problem was stable, set it as in crisis
                ###
                ###                        	If the problem was protected, it loses its protection
                ###
                ###                        	If the problem was already in crisis, it cascades as follows:
                ###
                ###                             	All outflows from the node in crisis are marked as in crisis.

                ## add crisis chip for each category fully in crisis
                for cat, catid in Graph.CATEGORIES:
                    if len(self.state.graph.are_in_crisis(cat)) == len(
                        self.game_def.graph.node_classes[catid]
                    ):
                        self.log.append(
                            {
                                "phase": phase,
                                "step": Game.STEPS_PER_PHASE[phase][1],
                                "target": cat,
                                "memo": Game.L_CHIP_FULL_CAT,
                                "state": self.state.to_json(),
                            }
                        )

                roll_over_counter = 0
                while (
                    self.state.crisis_chips
                    and len(self.state.graph.are_in_crisis()) < len(self.game_def.graph)
                    and roll_over_counter < 10
                ):
                    ## roll a category, if the category is fully in crisis, add a crisis chip and roll again
                    catnum = self.roll_dice(1, self.state.player, "crisis cat", rand, 1)
                    cat, catid = Graph.CATEGORIES[catnum - 1]
                    self.log.append(
                        {
                            "phase": phase,
                            "step": Game.STEPS_PER_PHASE[phase][1],
                            "target": cat,
                            "memo": Game.L_CRISIS_CAT,
                            "state": self.state.to_json(),
                        }
                    )

                    if len(self.state.graph.are_in_crisis(cat)) == len(
                        self.game_def.graph.node_classes[catid]
                    ):
                        self.log.append(
                            {
                                "phase": phase,
                                "step": Game.STEPS_PER_PHASE[phase][1],
                                "target": cat,
                                "memo": Game.L_CHIP_FULL_CAT,
                                "state": self.state.to_json(),
                            }
                        )
                        continue

                    ## roll a node in category, if in crisis and all its descendants are in crisis, add a crisis chip and roll again
                    nodes = []
                    for nid in self.game_def.graph.node_classes[catid]:
                        ordering = self.game_def.graph.ordering[nid]
                        if ordering < 99:
                            nodes.append(nid)
                    nodes = sorted(
                        nodes, key=lambda nid: self.game_def.graph.ordering[nid]
                    )
                    nodenum = 7
                    while nodenum >= len(nodes):
                        nodenum = self.roll_dice(
                            1, self.state.player, "node in " + cat, rand, 1
                        )
                    node = nodes[nodenum]
                    noden = self.game_def.graph.node_names[node]
                    if self.state.graph.is_saturated(noden):
                        self.log.append(
                            {
                                "phase": phase,
                                "step": Game.STEPS_PER_PHASE[phase][1],
                                "target": noden,
                                "memo": Game.L_CHIP_SATURATED,
                                "state": self.state.to_json(),
                            }
                        )
                        roll_over_counter += 1
                        continue

                    self.log.append(
                        {
                            "phase": phase,
                            "step": Game.STEPS_PER_PHASE[phase][1],
                            "target": noden,
                            "memo": Game.L_CRISIS_NODE,
                            "state": self.state.to_json(),
                        }
                    )

                    if self.state.graph.is_one_level_saturated(noden):
                        ## consume crisis_chips going through the cascade table
                        idx = 0
                        while (
                            idx < len(self.game_def.cascades.cascade[node])
                            and self.state.crisis_chips
                        ):
                            other = self.game_def.cascades.cascade[node][idx]
                            othern = self.game_def.graph.node_names[other]
                            if (
                                self.state.graph[othern]["status"]
                                != GraphState.IN_CRISIS
                            ):
                                ## if node was stable, set in crisis
                                if (
                                    self.state.graph[othern]["status"]
                                    == GraphState.STABLE
                                ):
                                    self.state.graph[othern][
                                        "status"
                                    ] = GraphState.IN_CRISIS
                                    self.log.append(
                                        {
                                            "phase": phase,
                                            "step": Game.STEPS_PER_PHASE[phase][1],
                                            "target": othern,
                                            "memo": Game.L_IN_CRISIS,
                                            "state": self.state.to_json(),
                                        }
                                    )

                                    ## if the node was protected, remove the protection
                                elif (
                                    self.state.graph[othern]["status"]
                                    == GraphState.PROTECTED
                                ):
                                    self.state.graph[othern][
                                        "status"
                                    ] = GraphState.STABLE
                                    self.log.append(
                                        {
                                            "phase": phase,
                                            "step": Game.STEPS_PER_PHASE[phase][0],
                                            "target": othern,
                                            "memo": Game.L_PROT_LOSS,
                                            "state": self.state.to_json(),
                                        }
                                    )
                                self.state.crisis_chips -= 1
                            idx += 1
                    else:
                        ## with a node in hand, roll crisis chips until either the roll is successful or all the crisis chips are exhausted
                        crisis_averted = True
                        while self.state.crisis_chips:
                            crisis_roll = self.roll_dice(
                                2,
                                self.state.player,
                                "crisis roll for " + noden,
                                rand,
                                1,
                            )
                            self.log.append(
                                {
                                    "phase": phase,
                                    "step": Game.STEPS_PER_PHASE[phase][1],
                                    "target": crisis_roll,
                                    "memo": Game.L_CRISIS_ROLL,
                                    "args": [noden],
                                    "state": self.state.to_json(),
                                }
                            )
                            self.state.crisis_chips -= 1
                            if crisis_roll < self.game_def.crisis_check:
                                crisis_averted = False
                                break

                        if crisis_averted:
                            self.log.append(
                                {
                                    "phase": phase,
                                    "step": Game.STEPS_PER_PHASE[phase][1],
                                    "target": noden,
                                    "memo": Game.L_CRISIS_AVERTED,
                                    "state": self.state.to_json(),
                                }
                            )
                        else:
                            ## if node was stable, set in crisis
                            if self.state.graph[noden]["status"] == GraphState.STABLE:
                                self.state.graph[noden]["status"] = GraphState.IN_CRISIS
                                self.log.append(
                                    {
                                        "phase": phase,
                                        "step": Game.STEPS_PER_PHASE[phase][1],
                                        "target": noden,
                                        "memo": Game.L_IN_CRISIS,
                                        "state": self.state.to_json(),
                                    }
                                )

                            ## if the node was protected, remove the protection
                            elif (
                                self.state.graph[noden]["status"]
                                == GraphState.PROTECTED
                            ):
                                self.state.graph[noden]["status"] = GraphState.STABLE
                                self.log.append(
                                    {
                                        "phase": phase,
                                        "step": Game.STEPS_PER_PHASE[phase][0],
                                        "target": noden,
                                        "memo": Game.L_PROT_LOSS,
                                        "state": self.state.to_json(),
                                    }
                                )
                            ## if the node was in crisis, activate all the nodes reachable from it and further cascade as needed
                            else:
                                cascaded = self.cascade(node)
                                for node2 in sorted(
                                    cascaded,
                                    key=lambda x: self.game_def.graph.node_names[x],
                                ):
                                    node2n = self.game_def.graph.node_names[node2]
                                    if (
                                        self.state.graph[node2n]["status"]
                                        == GraphState.STABLE
                                    ):
                                        self.state.graph[node2n][
                                            "status"
                                        ] = GraphState.IN_CRISIS
                                        self.log.append(
                                            {
                                                "phase": phase,
                                                "step": Game.STEPS_PER_PHASE[phase][1],
                                                "target": node2n,
                                                "memo": Game.L_IN_CRISIS_CASCADE,
                                                "args": [noden],
                                                "state": self.state.to_json(),
                                            }
                                        )
                                    elif (
                                        self.state.graph[node2n]["status"]
                                        == GraphState.PROTECTED
                                    ):
                                        self.state.graph[node2n][
                                            "status"
                                        ] = GraphState.STABLE
                                        self.log.append(
                                            {
                                                "phase": phase,
                                                "step": Game.STEPS_PER_PHASE[phase][1],
                                                "target": node2n,
                                                "memo": Game.L_PROT_LOSS_CASCADE,
                                                "args": [noden],
                                                "state": self.state.to_json(),
                                            }
                                        )

                    ## if there are more crisis chips, continue by selecting a new category
                if roll_over_counter >= 10:
                    self.finished = True
        return self.advance()

    ### ACTIVATION PHASE ACTIONS RECORDED:

    ###  	START_PROJECT  = The player started a specific project.
    A_START_PROJECT = "START_PROJECT"
    ###  	SUCCESS_SKILL  = The player performed a successful skill check for a given project, with a specific roll value against a specific card value.
    A_SUCCESS_SKILL = "SUCCESS_SKILL"
    ###  	FAILED_SKILL   = The player failed a skill check for a given project, with a specific roll value against a specific card value.
    A_FAILED_SKILL = "FAILED_SKILL"
    ###  	START_RESEARCH = The player started researching a specific technology.
    A_START_RESEARCH = "START_RESEARCH"
    ###  	SKILL_RESEARCH = The player contributed a skill card to a specific technology being researched.
    A_SKILL_RESEARCH = "SKILL_RESEARCH"
    ###  	FUND_RESEARCH  = The player contributed a money unit to a specific technology being researched.
    A_FUND_RESEARCH = "FUND_RESEARCH"
