import sys
import math

from wicked21st.graph import load_graph, Graph

import svgwrite

g = load_graph(sys.argv[1])
dwg = svgwrite.Drawing(sys.argv[2], height=1080, width=1080)

total_nodes = len(g.node_names)
rad_per_node = 2 * math.pi * 1.0 / total_nodes

current_rad = 0

node_edge_len = 400
cat_edge_len = 250

node_to_xy_rad = dict()

#print(g.node_classes)

for catid in g.node_classes:
    nodes = g.node_classes[catid]

    #print("category: '{}' (size: {})".format(cat, len(nodes)))
    for node in sorted(nodes, key=lambda x:g.node_names[x]):
        x = math.cos(current_rad) * node_edge_len + 540
        y = math.sin(current_rad) * node_edge_len + 540
        node_to_xy_rad[node] = (x,y, current_rad)
        current_rad += rad_per_node
        dwg.add(dwg.text(g.node_names[node], insert=(x, y), fill=catid))
        #print("\t" + graph_def.node_names[node])
        #print("\t\tLinks to: " + "; ".join(sorted(list(map(lambda x:graph_def.node_names[x], graph_def.outlinks[node])))))

marker = dwg.marker(insert=(5,5), size=(10,10))
marker.add(dwg.circle((5, 5), r=5, fill='red'))
dwg.defs.add(marker)

for node in g.node_names.keys():
    _, _, rad = node_to_xy_rad[node]
    x = math.cos(rad) * node_edge_len * 0.9 + 540
    y = math.sin(rad) * node_edge_len * 0.9 + 540
    for other in g.outlinks[node]:
        xo, yo, _ = node_to_xy_rad[other]
        line = dwg.add(dwg.line((x,y), (xo, yo), stroke=g.class_for_node[node]))
        line.set_markers((marker, False, None))

dwg.save()
