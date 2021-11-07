import sys
import math

import graphviz


import config

from wicked21st.graph import load_graph, Graph


g = load_graph(config.GRAPH)

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

# category graph

digraph = graphviz.Digraph(graph_attr={"size": "20,20", "nodesep":"2.0", "landscape":"portrait"})

cat_flows = dict()
for _, catid in Graph.CATEGORIES:
    cat_flows[catid] = { other: 0.0 for _, other in Graph.CATEGORIES }

for _id, catid in g.class_for_node.items():

    for out in g.outlinks[_id]:
        cat_flows[catid][g.class_for_node[out]] += 1.0

catid_to_name = { catid: catname for catname, catid in Graph.CATEGORIES }
catid_to_num = { catid: "N{}".format(idx) for idx, catid in enumerate(map(lambda x:x[1], Graph.CATEGORIES)) }

for catname, catid in Graph.CATEGORIES:
    digraph.node(catid_to_num[catid], catname, shape="oval", fillcolor=catid, style='filled', fontsize="20")

for catname, catid in Graph.CATEGORIES:
    for outcat, v in cat_flows[catid].items():
        if v:
            if v < 3:
                style = "dotted"
            elif v < 5:
                style = "dashed"
            elif v < 7:
                style = "solid"
            else:
                style = "bold"
            digraph.edge(catid_to_num[catid], catid_to_num[outcat], label=" " + str(int(v)), style=style)

with open("board_categories.dot", "w") as b:
    b.write(digraph.source)

for catname, catid in Graph.CATEGORIES:
    digraph = graphviz.Digraph(graph_attr={"size": "20,20", "nodesep":"2.0", "landscape":"portrait"})
    fname = catname.lower()
    if ' ' in catname:
        fname = "_".join(fname.split(" "))

    node_id_to_num = dict()
    cloud_nodes = set()
    for n in g.node_classes[catid]:
        digraph.node("N{}".format(len(node_id_to_num)), "{}\n{}".format(g.node_names[n],
                                                                        node_to_code[n]),
                     shape="oval", fillcolor=catid, style='filled', fontsize="20")
        node_id_to_num[n] = len(node_id_to_num)

        for out in g.outlinks[n]:
            cloud_nodes.add(out)

    for n in g.node_names:
        if g.class_for_node[out] == catid:
            continue
        for out in g.outlinks[n]:
            if g.class_for_node[out] == catid:
                cloud_nodes.add(n)

    for n in cloud_nodes:
        if n in node_id_to_num:
            continue
        digraph.node("N{}".format(len(node_id_to_num)), node_to_code[n], shape="plaintext", fontcolor=g.class_for_node[n],
                     fontsize="20")
        node_id_to_num[n] = len(node_id_to_num)

    for n in g.node_classes[catid]:
        for out in g.outlinks[n]:
            color = "black"
            style = "bold"
            if g.class_for_node[out] != catid:
                color = g.class_for_node[out]
                style="solid"
            digraph.edge("N{}".format(node_id_to_num[n]), "N{}".format(node_id_to_num[out]), color=color, style=style)
            
    for n in g.node_names:
        if g.class_for_node[out] == catid:
            continue
        color = g.class_for_node[n]
        for out in g.outlinks[n]:
            if g.class_for_node[out] == catid:
                digraph.edge("N{}".format(node_id_to_num[n]), "N{}".format(node_id_to_num[out]), color=color)
                
    with open("board_{}.dot".format(fname), "w") as b:
        b.write(digraph.source)
