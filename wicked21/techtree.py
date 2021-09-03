# -*- coding: utf-8 -*-
# Copyright (C) 2021 Textualization Software Ltd.
# Distributed under the terms of the Apache Software License 2.0
# http://www.apache.org/licenses/LICENSE-2.0

class TechTree:
    def __init__(self):
        self.technologies = [
            'High Capacity Batteries',
            'Low Waste Construction',
            'Wasteless Nuclear',
            'Quantum Computing',
            'Complete Wireless Communications',
            'Labour Automation'
            ]
    def to_json(self):
        return self.technologies
        
