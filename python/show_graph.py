from wicked21st.graph import load_graph, Graph

import graphviz

graph_def = load_graph("map20210812.mm")

for cat, catid in Graph.CATEGORIES:
    nodes = graph_def.node_classes[catid]
    print("cat: '{}' (len: {})".format(cat, len(nodes)))
    for node in nodes:
        print("\t" + graph_def.node_names[node])

print(graph_def.show().source)

