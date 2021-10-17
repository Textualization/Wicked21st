# -*- coding: utf-8 -*-
# Copyright (C) 2021 Textualization Software Ltd.
# Distributed under the terms of the Apache Software License 2.0
# http://www.apache.org/licenses/LICENSE-2.0


###
### Locations
###
### resources
###
###         	University: !,
###         	Industry Assoc: !,
###         	NGO Offices: !,
###         	Downtown Centre: !,
###         	Patent Office: $,
###         	Industrial Park: $,
###         	Hospital: $,
###         	Cultural District: $
###
### suits
###
###         	University: S,
###         	Industry Assoc: C,
###         	NGO Offices: H,
###         	Downtown Centre: D,
###         	Patent Office: S,
###         	Industrial Park: C,
###         	Hospital: H,
###         	Cultural District: D
###

class Board:
    def __init__(self):
        self.locations = [
            'University',
            'Industry Assoc',
            'NGO Offices',
            'Downtown Centre',
            'Patent Office',
            'Industrial Park',
            'Hospital',
            'Cultural District' ]
        self.resources = {
            'University': '!',
            'Industry Assoc': '!',
            'NGO Offices': '!',
            'Downtown Centre': '!',
            'Patent Office': '$',
            'Industrial Park': '$',
            'Hospital': '$',
            'Cultural District': '$' }
        self.suits = {
            'University': 'S',
            'Industry Assoc': 'C',
            'NGO Offices': 'H',
            'Downtown Centre': 'D',
            'Patent Office': 'S',
            'Industrial Park': 'C',
            'Hospital': 'H',
            'Cultural District': 'D' }
        self.special = {'Industry Assoc': 'Engineer',
                        'Hospital': 'Doctor' }

    def to_json(self):
        return { 'locations' : self.locations,
                 'resources' : self.resources,
                 'suits' : self.suits,
                 'special' : self.special }
