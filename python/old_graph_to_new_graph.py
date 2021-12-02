# -*- coding: utf-8 -*-
# Copyright (C) 2021 Textualization Software Ltd.
# Distributed under the terms of the Apache Software License 2.0
# http://www.apache.org/licenses/LICENSE-2.0


import sys

from wicked21st.graph import load_graph, Graph, Cascades, save_graph

graph, cascades = load_graph(sys.argv[1])
save_graph(sys.argv[2], graph, cascades)



