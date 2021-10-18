# -*- coding: utf-8 -*-
# Copyright (C) 2021 Textualization Software Ltd.
# Distributed under the terms of the Apache Software License 2.0
# http://www.apache.org/licenses/LICENSE-2.0


###
### Locations
###
### suits
###
###         	University: S,
###         	Industry Assoc: C,
###         	NGO Offices: H,
###         	Downtown Centre: D,
###

class Board:
    def __init__(self):
        self.locations = [
            'University',
            'Industry Assoc',
            'NGO Offices',
            'Downtown Centre',
#            'Patent Office',
#            'Industrial Park',
#            'Hospital',
#            'Cultural District'
        ]
        self.suits = {
            'University': 'S',
            'Industry Assoc': 'C',
            'NGO Offices': 'H',
            'Downtown Centre': 'D',
            }

    def to_json(self):
        return { 'locations' : self.locations,
                 'suits' : self.suits,
                }
