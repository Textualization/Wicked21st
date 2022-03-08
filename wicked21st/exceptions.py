# -*- coding: utf-8 -*-
# Copyright (C) 2021-2022 Textualization Software Ltd.
# Distributed under the terms of the MIT License
# https://mit-license.org/


class EmptyDrawPile(Exception):
    def __init__(self, suit):
        self.suit = suit

        super(EmptyDrawPile, self).__init__("suit: {}".format(suit))

    def __reduce__(self):
        return (EmptyDrawPile, (self.suit,))
