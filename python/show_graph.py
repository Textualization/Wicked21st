import sys

from wicked21st.graph import load_graph, Graph

import graphviz

graph_def = load_graph(sys.argv[1])

if len(sys.argv) > 2:
    print(graph_def.show().source)
else:
    for cat, catid in Graph.CATEGORIES:
        nodes = graph_def.node_classes[catid]
        print("category: '{}' (size: {})".format(cat, len(nodes)))
        for node in sorted(nodes, key=lambda x:graph_def.node_names[x]):
            print("\t" + graph_def.node_names[node])
            print("\t\tLinks to: " + "; ".join(sorted(list(map(lambda x:graph_def.node_names[x], graph_def.outlinks[node])))))

