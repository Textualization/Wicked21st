# -*- coding: utf-8 -*-
# Copyright (C) 2021-2022 Textualization Software Ltd.
# Distributed under the terms of the MIT License
# https://mit-license.org/

from wicked21st.graph import load_graph
from wicked21st.techtree import TechTree

import graphviz

graph_def = load_graph("maps/map20210812.mm")

tech_def = TechTree(graph_def)

# print("\n".join(list(map(lambda x:str(x), tech_def.to_json()))))

digraph = graphviz.Digraph(
    graph_attr={
        "size": "30,500",
        "landscape": "portrait",
        "overlap": "false",
        "splines": "true",
    }
)

idx_for_name = {tech.name: str(idx) for idx, tech in enumerate(tech_def.technologies)}

for idx, tech in enumerate(tech_def.technologies):
    digraph.node(str(idx), tech.name)
    if tech.parents:
        for parent in tech.parents:
            digraph.edge(idx_for_name[parent], str(idx))

print(digraph.source)
