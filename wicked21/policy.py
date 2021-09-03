# -*- coding: utf-8 -*-
# Copyright (C) 2021 Textualization Software Ltd.
# Distributed under the terms of the Apache Software License 2.0
# http://www.apache.org/licenses/LICENSE-2.0

class Policy:
    def __init__(self):
        self.names = [
            "Fund Emissions Filtration",
            "Emissions Regulations",
            "Local Zoning",
            "Regional Zoning/Greenbelt",
            "Chemical Bans",
            "Toxic Chemical Phaseout",
            "EV Subsidy",
            "Public Transit",
            "Fossil Fuel Phaseout",
            "Water use restrictions",
            "Greywater Recycling",
            "Saltwater Desalinization",
            "Public Zoos",
            "Species at Risk Protection",
            "Habitat Protection",
            "Ban Fertilizers",
            ]
    def to_json(self):
        return self.name
        
