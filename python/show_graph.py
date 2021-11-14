# -*- coding: utf-8 -*-
# Copyright (C) 2021 Textualization Software Ltd.
# Distributed under the terms of the Apache Software License 2.0
# http://www.apache.org/licenses/LICENSE-2.0

import sys

from wicked21st.graph import load_graph, Graph

import graphviz

if len(sys.argv) > 1:
    graph_file = sys.argv[1]
else:
    import config
    graph_file = config.GRAPH

graph_def = load_graph(graph_file)

if len(sys.argv) > 2:
    print(graph_def.show().source)
else:
    for cat, catid in Graph.CATEGORIES:
        nodes = graph_def.node_classes[catid]
        print("category: '{}' (size: {})".format(cat, len(nodes)))
        for node in sorted(nodes, key=lambda x:graph_def.node_names[x]):
            print("\t" + graph_def.node_names[node])
            print("\t\tLinks to: " + "; ".join(sorted(list(map(lambda x:graph_def.node_names[x], graph_def.outlinks[node])))))

