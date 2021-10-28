import sys
import math

from wicked21st.graph import load_graph, Graph


g = load_graph(sys.argv[1])

node_to_code = dict()
for catid in g.node_classes:
    nodes = g.node_classes[catid]
    
    for node in sorted(nodes, key=lambda x:g.ordering[x]):
        name = g.node_names[node].upper()
        if name[0] == '*':
            name
        code = name[:3]
        if code in node_to_code:
            code = name.split(" ")[1][:3]
            if code in node_to_code:
                raise Error(g.node_names[node]+ " " + str(node_to_code))
        node_to_code[node] = code

inflows = dict()
for node in g.node_names.keys():
    order = g.ordering[node]
    this_inflow = list()
    for other in g.node_names.keys():
        if other != node and node in g.outlinks[other]:
            this_inflow.append(other)
    inflows[node] = this_inflow

print("CAT\tNAME\tCODE\t#INF\t#OUTF\tINFLOWS\tOUTFLOWS")
for name, catid in Graph.CATEGORIES:
    print("{}\t{}\t{}\t{}\t{}\t{}\t{}".format(name, "", "", "", "","",""))
    nodes = g.node_classes[catid]

    for node in sorted(nodes, key=lambda x:g.ordering[x]):
        inf = ",".join(map(lambda x:node_to_code[x], inflows[node]))
        outf = ",".join(map(lambda x:node_to_code[x], g.outlinks[node]))
        print("{}\t{}\t{}\t{}\t{}\t{}\t{}".format("", g.node_names[node], node_to_code[node],
                                                  len(inflows[node]), len(g.outlinks[node]), inf, outf))
