# -*- coding: utf-8 -*-
# Copyright (C) 2021-2022 Textualization Software Ltd.
# Distributed under the terms of the MIT License
# https://mit-license.org/

from wicked21st.graph import load_graph
from wicked21st.project import Projects

graph_def = load_graph("maps/map20210812.mm")

projects_def = Projects(graph_def)

print("\n".join(projects_def.names))
