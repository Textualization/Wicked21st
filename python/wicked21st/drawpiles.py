# -*- coding: utf-8 -*-
# Copyright (C) 2021 Textualization Software Ltd.
# Distributed under the terms of the Apache Software License 2.0
# http://www.apache.org/licenses/LICENSE-2.0

import random

from .exceptions import EmptyDrawPile

class DrawPiles:
    SUITS = [ 'C', 'D', 'H', 'S' ]

    def __init__(self, rand=None, copy=None):
        if copy is not None:
            self.return_piles = { s: list(v) for s, v in copy.return_piles.items() }
            self.draw_piles =   { s: list(v) for s, v in copy.draw_piles.items() }
        else:
            self.return_piles = { s: list() for s in DrawPiles.SUITS } # suit -> list
            self.draw_piles = dict() # suit -> list

            #suit_cards = ['a'] + list(range(2,11)) + ['j','q','k']
            suit_cards = list(range(1,14))
            for suit in DrawPiles.SUITS:
                pile = suit_cards + suit_cards + [14,] # joker
                rand.shuffle(pile)
                self.draw_piles[suit] = pile

    def draw(self, suit, rand):
        pile =  self.draw_piles[suit]
        if pile:
            self.draw_piles[suit] = pile[1:]
            return ( suit, pile[0] )
        # reshuffle
        pile = self.return_piles[suit]
        if pile:
            rand.shuffle(pile)
            self.return_piles[suit] = list()
            self.draw_piles[suit] = pile
            return self.draw(suit, rand)
        raise EmptyDrawPile(suit)

    def return_card(self, card, suit=None):
        if card[1] == 14:
            self.return_piles[suit].append(card[1])
        else:
            self.return_piles[card[0]].append(card[1])

    def to_json(self):
        return { 'draw' : { s: self.draw_piles[s] for s in DrawPiles.SUITS },
                 'return' : { s: self.return_piles[s] for s in DrawPiles.SUITS } }

    def copy(self):
        return DrawPiles(copy=self)
