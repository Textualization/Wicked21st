# -*- coding: utf-8 -*-
# Copyright (C) 2021 Textualization Software Ltd.
# Distributed under the terms of the Apache Software License 2.0
# http://www.apache.org/licenses/LICENSE-2.0

import random
import copy

import numpy as np


class BaseClass:
    def __init__(self, name, suit_a, suit_b, resource):
        self.name = name
        self.suit_a = suit_a
        self.suit_b = suit_b
        self.resource = resource
        self.project_slots = 1
        self.policy_slots = 1
        self.research_slots = 1

    def to_json(self):
        return { 'name' : self.name,
                 'suit_a' : self.suit_a,
                 'suit_b' : self.suit_b,
                 'resource' : self.resource,
                 'project_slots' : self.project_slots,
                 'policy_slots' : self.policy_slots,
                 'research_slots' : self.research_slots,
                }

# missing: special abilities

class EngineerClass(BaseClass):
    def __init__(self):
        super.__init__('Engineer', 'S', 'C', '!')
class InvestorClass(BaseClass):
    def __init__(self):
        super.__init__('Investor', 'S', 'C', '$')
class UnionRepClass(BaseClass):
    def __init__(self):
        super.__init__('Union Rep', 'S', 'H', '!')
class SocialWorkerClass(BaseClass):
    def __init__(self):
        super.__init__('Social Worker', 'S', 'H', '$')
class ArtistClass(BaseClass):
    def __init__(self):
        super.__init__('Artist', 'S', 'D', '!')
class ServiceWorkerClass(BaseClass):
    def __init__(self):
        super.__init__('Service Worker', 'S', 'D', '$')
class ResearcherClass(BaseClass):
    def __init__(self):
        super.__init__('Researcher', 'C', 'H', '!')
class ScientistClass(BaseClass):
    def __init__(self):
        super.__init__('Scientist', 'C', 'H', '$')
class JournalistClass(BaseClass):
    def __init__(self):
        super.__init__('Journalist', 'C', 'D', '$')
class CouncilorClass(BaseClass):
    def __init__(self):
        super.__init__('Councilor', 'C', 'D', '!')
class ActivistClass(BaseClass):
    def __init__(self):
        super.__init__('Activist', 'H', 'D', '!')
class LocalOrganizerClass(BaseClass):
    def __init__(self):
        super.__init__('Local Organizer', 'H', 'D', '$')

class Classes:
    def __init__(self):
        self.classes = [
            EngineerClass(),
            InvestorClass(),
            UnionRepClass(),
            SocialWorkerClass(),
            ArtistClass(),
            ServiceWorkerClass(),
            ResearcherClass(),
            ScientistClass(),
            JournalistClass(),
            CouncilorClass(),
            ActivistClass(),
            LocalOrganizerClass()
        ]

    def to_json(self):
        return { 'classes': [ x.to_json() for x in self.classes ] }

    def pick(self, rand: random.Random):
        return rand.choice(self.classes)

