# -*- coding: utf-8 -*-
# Copyright (C) 2021-2022 Textualization Software Ltd.
# Distributed under the terms of the MIT License
# https://mit-license.org/

import random
import copy

import numpy as np


### Roles
###
###
### These are the roles with their associated suits:
###
### |Investor       | S| C|
### |Social Worker  | S| D|
### |Educator       | S| H|
### |Scientist      | C| H|
### |Journalist     | C| D|
### |Councilor      | H| D|
###


class BaseClass:
    def __init__(self, name, suit_a, suit_b):
        self.name = name
        self.suit_a = suit_a
        self.suit_b = suit_b
        self.project_slots = 1
        self.research_slots = 1
        self.json_memo = None

    def to_json(self):
        if self.json_memo is None:
            self.json_memo = {
                "name": self.name,
                "suit_a": self.suit_a,
                "suit_b": self.suit_b,
                "project_slots": self.project_slots,
                "research_slots": self.research_slots,
            }
        return self.json_memo


# missing: special abilities


class InvestorClass(BaseClass):
    def __init__(self):
        super().__init__("Investor", "S", "C")


class SocialWorkerClass(BaseClass):
    def __init__(self):
        super().__init__("Social Worker", "S", "D")


class EducatorClass(BaseClass):
    def __init__(self):
        super().__init__("Educator", "S", "H")


class ScientistClass(BaseClass):
    def __init__(self):
        super().__init__("Scientist", "C", "H")


class JournalistClass(BaseClass):
    def __init__(self):
        super().__init__("Journalist", "C", "D")


class CouncilorClass(BaseClass):
    def __init__(self):
        super().__init__("Councilor", "H", "D")


class Classes:
    def __init__(self):
        self.classes = [
            InvestorClass(),
            SocialWorkerClass(),
            EducatorClass(),
            ScientistClass(),
            JournalistClass(),
            CouncilorClass(),
        ]

    def to_json(self):
        return {"classes": [x.to_json() for x in self.classes]}

    def pick(self, rand: random.Random):
        return rand.choice(self.classes)

    def names(self):
        return [clazz.name for clazz in self.classes]

    def class_for_name(self, name: str):
        for clazz in self.classes:
            if clazz.name == name:
                return clazz
        raise Exception("Not found '{}'".format(name))
