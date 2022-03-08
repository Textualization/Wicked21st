# -*- coding: utf-8 -*-
# Copyright (C) 2021 Textualization Software Ltd.
# Distributed under the terms of the Apache Software License 2.0
# http://www.apache.org/licenses/LICENSE-2.0


class EmptyDrawPile(Exception):
    def __init__(self, suit):
        self.suit = suit

        super(EmptyDrawPile, self).__init__("suit: {}".format(suit))

    def __reduce__(self):
        return (EmptyDrawPile, (self.suit,))
