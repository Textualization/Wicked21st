# -*- coding: utf-8 -*-
# Copyright (C) 2021 Textualization Software Ltd.
# Distributed under the terms of the Apache Software License 2.0
# http://www.apache.org/licenses/LICENSE-2.0

import random

class DrawPiles:
    SUITS = [ 'C', 'D', 'H', 'S' ]

    def __init__(self, rand):
        self.return_piles = { s: list() for s in DrawPiles.SUITS } # suit -> list
        self.draw_piles = dict() # suit -> list

        #suit_cards = ['a'] + list(range(2,11)) + ['j','q','k']
        suit_cards = list(range(1,14))
        for suit in SUITS:
            pile = suit_cards + suit_cards + [14,] # joker
            rand.shuffle(pile)
            self.draw_pile[suit] = pile

    def draw(self, suit, rand):
        pile =  self.draw_piles[suit]
        if pile:
            self.draw_piles[suit] = pile[1:]
            return ( suit, pile[0] )
        else: # reshuffle
            pile = self.return_piles[suit]
            assert pile
            rand.shuffle(pile)
            self.return_piles[suit] = list()
            self.draw_piles[suit] = pile
            return self.draw(suit, rand)

    def return_card(self, card, suit=None):
        if card[1] == 14:
            self.return_piles[suit].append(card[1])
        else:
            self.return_piles[card[0]].append(card[1])

    def to_json(self):
        return { 'draw' : { s: self.draw_piles[s] for s in SUITS },
                 'return' : { s: self.return_piles[s] for s in SUITS } }
