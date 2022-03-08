# -*- coding: utf-8 -*-
# Copyright (C) 2021-2022 Textualization Software Ltd.
# Distributed under the terms of the MIT License
# https://mit-license.org/

import random
import sys
import multiprocessing

from collections import namedtuple

from wicked21st.graph import load_graph, Graph, save_graph, Cascades

import graphviz

DEBUG = False
rand = random.Random(42)

if len(sys.argv) > 1:
    graph_file = sys.argv[1]
else:
    import config

    graph_file = config.GRAPH

graph_def, _ = load_graph(graph_file)


node_list = list()

cats = sorted(Graph.CATEGORIES, key=lambda x: x[0])

for _, catid in cats:
    ncat = sorted(graph_def.node_classes[catid], key=lambda x: graph_def.ordering[x])
    node_list = node_list + ncat

node_to_idx = {n: idx for idx, n in enumerate(node_list)}
num_nodes = len(node_list)

node_to_code = dict()
if len(next(iter(graph_def.node_names.keys()))) == 3:
    node_to_code = {x: x for x in graph_def.node_names}
    code_to_node = node_to_code
else:
    for catid in graph_def.node_classes:
        nodes = graph_def.node_classes[catid]

        for node in sorted(nodes, key=lambda x: graph_def.ordering[x]):
            name = graph_def.node_names[node].upper()
            if name[0] == "*":
                name
            if name.startswith("LACK OF"):
                name = name[len("LACK OF ") :]
            code = name[:3]
            if code in node_to_code.values():
                code = name.split(" ")[1][:3]
                if code in node_to_code.values():
                    raise Error(graph_def.node_names[node] + " " + str(node_to_code))
            node_to_code[node] = code

    code_to_node = {c: n for n, c in node_to_code.items()}


def reachable(node, path):
    if node in path:
        return list()
    path = path + [node]
    result = [(node, path)]
    for outlink in sorted(graph_def.outlinks[node]):
        result = result + reachable(outlink, path)

    return result


cascade = dict()
buckets = dict()
for cnode in node_list:
    in_reach = reachable(cnode, [])
    shortest = dict()
    for node, path in in_reach:
        if node in shortest:
            existing = shortest[node]
            if len(existing[0]) > len(path):
                # replace
                shortest[node] = [path]
            elif len(existing[0]) == len(path):
                shortest[node].append(path)
        else:
            shortest[node] = [path]

    # sort by distance
    by_distance = dict()  # int -> list of (node, (list previous nodes) )
    for node, paths in shortest.items():
        dist = len(paths[0])
        if dist not in by_distance:
            by_distance[dist] = list()
        prev = [path[-1] for path in paths]
        by_distance[dist].append((node, prev))

    # randomize
    for dist in by_distance:
        rand.shuffle(by_distance[dist])

    # print
    dist_buckts = list()
    for dist in sorted(by_distance.keys()):
        if dist > 2:
            dist_buckts.append(list(map(lambda x: x[0], by_distance[dist])))
    flatten = [n for bckt in dist_buckts for n in bckt]
    cascade[cnode] = flatten
    buckets[cnode] = dist_buckts


if len(sys.argv) > 2:
    cascades = Cascades(graph_def)
    cascades.cascade = cascade
    save_graph(sys.argv[2], graph_def, cascades)
else:
    with open("cascading.tsv", "w") as tsv:
        for cnode in node_list:
            dist_buckts = buckets[cnode]
            print(
                "{} ({}): {}".format(
                    graph_def.node_names[cnode],
                    node_to_code[cnode],
                    "; ".join(
                        map(
                            lambda bckt: ", ".join(
                                map(lambda x: node_to_code[x], bckt)
                            ),
                            dist_buckts,
                        )
                    ),
                )
            )
            flatten = cascade[cnode]
            tsv.write("{}\t{}\n".format(cnode, "\t".join(flatten)))
