# -*- coding: utf-8 -*-
# Copyright (C) 2021 Textualization Software Ltd.
# Distributed under the terms of the Apache Software License 2.0
# http://www.apache.org/licenses/LICENSE-2.0

import random
import copy
import json

import graphviz

import numpy as np
import xml.etree.ElementTree as ET


class Graph:

    INDUSTRIAL = ("INDUSTRIAL", "#3f7e44")
    ECONOMIC = ("ECONOMIC", "#26bde2")
    SOCIAL = ("SOCIAL", "#fd6925")
    CLASS = ("CLASS", "#fcc30b")
    ENVIRONMENTAL = ("ENVIRONMENTAL", "#56c02b")
    LIVING_STANDARDS = ("LIVING STANDARDS", "#dd1367")

    CATEGORIES = [INDUSTRIAL, ECONOMIC, SOCIAL, CLASS, ENVIRONMENTAL, LIVING_STANDARDS]

    def class_name(catid):
        for name, otherid in Graph.CATEGORIES:
            if otherid == catid:
                return name
        print("Unknown catid:", catid)
        assert False

    GRAPH_PRINT_SIZE = "20,20"

    # nodes: dict( id -> name ), class_for_node: dict( id -> clazz ), outlinks: dict( id -> set(id) )
    def __init__(self, nodes, class_for_node, outlinks, categories, ordering=None):
        class_for_node = {n: clazz.lower() for n, clazz in class_for_node.items()}
        self.node_names = {
            i: (
                (n if n[0] != "*" else n[1:]) if "." not in n else n[n.index(" ") + 1 :]
            )
            for i, n in nodes.items()
        }
        if ordering is None:
            self.ordering = {
                i: 100 + ord(n[1]) if "." not in n else int(n[: n.index(".")])
                for i, n in nodes.items()
            }
        else:
            self.ordering = ordering
        self.name_to_id = {n: i for i, n in self.node_names.items()}
        self.node_classes = dict()  # class to set of ids
        for _id, clazz in class_for_node.items():
            self.node_classes[clazz] = self.node_classes.get(clazz, set())
            self.node_classes[clazz].add(_id)
        self.class_for_node = class_for_node
        self.outlinks = outlinks
        self.categories = categories
        self.category_for_name = {c: i for i, c in categories.items()}

        # check orderings
        for catid, nodes_in_cat in self.node_classes.items():
            ordered = list()
            for nid in nodes_in_cat:
                if self.ordering[nid] < 99:
                    ordered.append(nid)
            if not ordered:
                print('Category "{}" missing order, using alphabetic'.format(catid))
                nodes = sorted(nodes_in_cat, key=lambda nid: self.ordering[nid])
                nodes = nodes[:6]
                for idx, nid in enumerate(nodes):
                    self.ordering[nid] = idx

    def __len__(self):
        return len(self.node_names)

    def __iter__(self):
        return self.node_names.values().__iter__()

    def nodes(self):
        """List of node names"""
        return list(self.node_names.values())

    def outlinks_for_node(node_name):
        return list(
            map(lambda x: self.node_names[x], self.outlinks[self.name_to_id[node_name]])
        )

    def make_singleton(self):
        self.outlinks = {_id: set() for _id in self.node_names}
        return self

    def make_line(self):
        _ids = list(nodes.keys())
        random.shuffle(_ids)
        self.outlinks = {_id: set() for _id in self.node_names}
        prev = None
        for _id in _ids:
            if prev is not None:
                self.outlinks[_id] = set([prev])
            prev = _id
        return self

    def make_radial(self):
        _ids = list(nodes.keys())
        center = random.choice(_ids)
        self.outlinks = {_id: set() for _id in self.node_names}
        for _id in _ids:
            if _id != center:
                self.outlinks[center].add(_id)
        return self

    def shuffle_links(self):
        total = len(self.outlinks)
        self.outlinks = {_id: set() for _id in self.node_names}
        current = 0
        _ids = list(nodes.keys())
        inreachable = {_id: set([_id]) for _id in _ids}  # node id to set of node id
        outreachable = {_id: set([_id]) for _id in _ids}  # node id to set of node id

        def add_link(source, target):
            self.outlinks[source] = self.outlinks.get(source, set())
            self.outlinks[source].add(target)
            for _in in inreachable[source]:
                outreachable[_in].update(outreachable[target])
            for _out in outreachable[target]:
                inreachable[_out].update(inreachable[source])

        while current < total:
            random.shuffle(_ids)
            source = _ids[0]
            target = _ids[1]
            if len(
                outreachable[target].intersection(inreachable[source])
            ) == 0 and target not in self.outlinks.get(source, set()):
                current += 1
                add_link(source, target)

        accounted = set()
        for k, v in self.outlinks.items():
            if len(v):
                accounted.add(k)
            accounted.update(v)

        missing = list(set(_ids) - accounted)
        while len(missing) > 0:
            is_source = random.random() > 0.5
            other = random.choice(list(accounted))
            source = missing[0] if is_source else other
            target = other if is_source else missing[0]
            add_link(source, target)
            accounted.add(missing[0])
            missing = missing[1:]

        return self

    def show(self):
        digraph = graphviz.Digraph(
            graph_attr={"size": Graph.GRAPH_PRINT_SIZE, "landscape": "portrait"}
        )

        for _id, name in self.node_names.items():
            digraph.node(
                name, shape="box", fillcolor=self.class_for_node[_id], style="filled"
            )
        for base, dests in self.outlinks.items():
            basetext = self.node_names[base]
            for dest in dests:
                digraph.edge(basetext, self.node_names[dest])
        return digraph

    def to_json(self):
        return {
            self.node_names[n]: [self.node_names[nn] for nn in self.outlinks[n]]
            for n in self.node_names
        }


def load_graph(graph_file, verbose=False):
    if graph_file.endswith(".mm"):
        graph_def = load_graph_mm(graph_file, verbose)
        cascade_def = Cascades(graph_def, graph_file[:-3] + ".cascading.tsv")
        return graph_def, cascade_def
    elif graph_file.endswith(".json"):
        return load_graph_json(graph_file, verbose)
    else:
        print("Unknown graph file type:", graph_file)
    assert False


def load_graph_json(graph_file, verbose=False):
    with open(graph_file, "rb") as j:
        jgraph = json.load(j)

        nodes = {code: obj["name"] for code, obj in jgraph.items()}
        class_for_node = {code: obj["category"]["code"] for code, obj in jgraph.items()}
        links = {code: obj["outlinks"] for code, obj in jgraph.items()}
        ordering = {code: obj["order"] for code, obj in jgraph.items()}

        graph = Graph(
            nodes,
            class_for_node,
            links,
            {p[1]: p[0] for p in Graph.CATEGORIES},
            ordering,
        )
        cascades = Cascades(jgraph)
        for n in sorted(jgraph.keys()):
            cascades.cascade[n] = jgraph[n]["cascading"]

        return graph, cascades


def load_graph_mm(graph_file, verbose=False):
    root = ET.parse(graph_file).getroot()

    nodes = dict()  # name to node dict
    node_classes = dict()  # bg color to set of names
    class_for_node = dict()

    for child in root[0]:
        # print(child.tag, child.attrib)
        if child.tag != "node":
            continue
        nodes[child.attrib["ID"]] = child
        clazz = child.attrib["BACKGROUND_COLOR"]
        if clazz not in node_classes:
            node_classes[clazz] = set()
        class_for_node[child.attrib["ID"]] = child.attrib["BACKGROUND_COLOR"]
        node_classes[clazz].add(child)

    if verbose:
        print("Found {} classes\n".format(len(node_classes)))
        for color, clazz in node_classes.items():
            print(color)
            for node in clazz:
                print("", node.attrib["TEXT"])

    links = dict()  # node id to set of node id
    for name, node in nodes.items():
        links[name] = set()
        for link in node:
            if link.tag != "arrowlink":
                continue
            # print(link.tag, link.attrib)
            links[name].add(link.attrib["DESTINATION"])

    return Graph(
        {_id: node.attrib["TEXT"] for _id, node in nodes.items()},
        class_for_node,
        links,
        {p[1]: p[0] for p in Graph.CATEGORIES},
    )


def save_graph(graph_json_file: str, graph: Graph, cascades=None):
    # compute codes
    node_to_code = dict()
    for catid in graph.node_classes:
        nodes = graph.node_classes[catid]

        for node in sorted(nodes, key=lambda x: graph.ordering[x]):
            name = graph.node_names[node].upper()
            if name[0] == "*":
                name
            if name.startswith("LACK OF"):
                name = name[len("LACK OF ") :]
            code = name[:3]
            if code in node_to_code.values():
                code = name.split(" ")[1][:3]
                if code in node_to_code.values():
                    raise Error(graph.node_names[node] + " " + str(node_to_code))
            node_to_code[node] = code

    code_to_node = {c: n for n, c in node_to_code.items()}

    j = dict()

    for code in sorted(code_to_node.keys()):
        node = code_to_node[code]

        j[code] = {
            "code": code,
            "name": graph.node_names[node],
            "order": graph.ordering[node],
            "category": {
                "name": Graph.class_name(graph.class_for_node[node]),
                "code": graph.class_for_node[node],
            },
            "outlinks": [node_to_code[outlink] for outlink in graph.outlinks[node]],
        }
        if cascades is not None:
            j[code]["cascading"] = [
                node_to_code[cascade] for cascade in cascades.cascade[node]
            ]

    with open(graph_json_file, "w") as jf:
        json.dump(j, jf, indent=2)


class Cascades:
    def __init__(self, graph, tsv=None):
        self.cascade = dict()  # node -> list of node
        if tsv:
            with open(tsv) as t:
                for line in t:
                    line = line[:-1]
                    if line[-1] == "\t":
                        line = line[:-1]
                    nodes = line.split("\t")
                    for n in nodes:
                        assert n in graph.node_names
                    self.cascade[nodes[0]] = nodes[1:]
