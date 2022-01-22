import sys
import multiprocessing

from collections import namedtuple

from wicked21st.graph import load_graph, Graph

import graphviz

DEBUG = False

if len(sys.argv) > 1:
    graph_file = sys.argv[1]
else:
    import config

    graph_file = config.GRAPH

graph_def = load_graph(graph_file)

node_list = list()

cats = sorted(Graph.CATEGORIES, key=lambda x: x[0])

for _, catid in cats:
    ncat = sorted(graph_def.node_classes[catid], key=lambda x: graph_def.ordering[x])
    node_list = node_list + ncat

node_to_idx = {n: idx for idx, n in enumerate(node_list)}
num_nodes = len(node_list)

node_to_code = dict()
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


def cascade0(node, graph, visited=None):
    "A node in crisis has been selected, deal with it. Returns the activated nodes."
    if visited is None:
        visited = list()
    if node in visited:
        return list()
    visited.append(node)
    result = list()
    for outlink in graph_def.outlinks[node]:
        if graph & (1 << node_to_idx[outlink]) == 0:
            result.append(outlink)
    if result:
        return result
    # recurse
    for outlink in graph_def.outlinks[node]:
        result = result + cascade0(outlink, graph, list(visited))

    return result


def cascade1(node, graph, visited=None):
    "A node in crisis has been selected, deal with it. Returns the activated nodes."
    if visited is None:
        visited = list()
    if node in visited:
        return list()
    visited.append(node)
    result = list()
    for outlink in graph_def.outlinks[node]:
        if graph & (1 << node_to_idx[outlink]) == 0:
            result.append(outlink)
        else:
            result = result + cascade1(outlink, graph, list(visited))

    return result


def reachable(node, visited=None):
    if visited is None:
        visited = list()
    if node in visited:
        return list()
    visited.append(node)
    result = list()
    for outlink in graph_def.outlinks[node]:
        result = result + [outlink] + reachable(outlink, list(visited))

    return result


Instruction = namedtuple("Instruction", ["condition", "actions"])


def make_instructions0(node):

    # remove cycles in subgraph...?

    # find nodes reachable through multiple paths
    nodereach = reachable(node)
    all_reachable = dict()
    for other in all_reachable:
        if other != node:
            nodereach[other] = reachable(other)
            if node in nodereach[other]:
                del nodereach[other][nodereach[other].index(node)]

    result = list()

    cond = []
    acts = []

    for outlink in graph_def.outlinks[node]:
        outreach = nodereach[outlink]
        acts.append(("TESTSET", outlink))


def make_base_instructions(node, visited=None):

    if visited is None:
        visited = []
    if node in visited:
        return []

    visited.append(node)

    result = list()

    for outlink in graph_def.outlinks[node]:

        recinstr = make_base_instructions(outlink, list(visited))
        if recinstr:
            result = result + [("IF", outlink, recinstr)]
        result += [("IFNOTSET", outlink)]

    return result


def pp_instructions(instructions, indent=""):
    for ins in instructions:
        print("{}{} {}".format(indent, ins[0], graph_def.node_names[ins[1]]))
        if len(ins) > 2:
            pp_instructions(ins[2], indent + "  ")


def pp_node_instructions(instructions):
    for n, instr in instructions:
        if len(instr) == 1:
            print(
                "{} [{}]: {}".format(
                    graph_def.node_names[n], node_to_code[n], " ^ ".join(instr[0])
                )
            )
        else:
            print("{} [{}]:".format(graph_def.node_names[n], node_to_code[n]))
            for ins in sorted(instr, key=lambda x: len(x)):
                print("  {}".format(" ^ ".join(ins)))


def simplify(conds):
    conds = sorted(conds, key=lambda x: len(x))
    result = list()
    while conds:
        cond0 = conds[0]
        result.append(cond0)
        old = conds[1:]
        conds = list()
        for cond in old:
            subsumed = True
            for c in cond0:
                if c not in cond:
                    subsumed = False
                    break
            if not subsumed:
                conds.append(cond)
    return result


def simplify_rec(conds):
    conds = sorted(conds, key=lambda x: len(x))
    if conds:
        cond0 = conds[0]

        rest = list()
        for cond in conds[1:]:
            subsumed = True
            for c in cond0:
                if c not in cond:
                    subsumed = False
                    break
            if not subsumed:
                rest.append(cond)

            conds = [cond0] + simplify_rec(rest)
    return conds


def process_state(t):
    node, state, in_reach, node_to_idx = t
    graph = 1 << node_to_idx[node]
    for idx in range(len(in_reach)):
        if 1 << idx & state:
            graph += 1 << node_to_idx[in_reach[idx]]

    reached = cascade0(node, graph)
    return reached, graph


def make_conds(t):
    n, graphs, in_reach, node_to_idx = t
    if DEBUG:
        print("Node {}, graphs: {:,}".format(node_to_code[n], len(graphs)))

    relevant = []
    for other in in_reach:
        if other == n:
            continue
        idx = node_to_idx[other]

        yes = list()
        no = list()

        for g in graphs:
            if 1 << idx & g:
                yes.append(g - 1 << idx)
            else:
                no.append(g)
        if len(yes) != len(no):
            relevant.append(idx)
        else:
            if sorted(yes) != sorted(no):
                relevant.append(idx)
    conds = list()
    covered = set()
    for g in graphs:
        this_instr = list()
        for r in relevant:
            name = node_to_code[node_list[r]]
            if 1 << r & g:
                this_instr.append(name)
            # else:
            #    this_instr.append('!' + name)
        instr_str = " ^ ".join(this_instr)
        if instr_str not in covered:
            conds.append(this_instr)
            covered.add(instr_str)

    # simplify, find smaller set and remove the rest
    if DEBUG:
        print("Node {} conds: {:,}".format(node_to_code[n], len(conds)))
    conds = simplify(conds)

    if DEBUG:
        print("Node {} DONE".format(node_to_code[n]))
    return (n, conds)


pool = multiprocessing.Pool(20)


def node_instructions(node):

    in_reach = set(reachable(node))
    in_reach.discard(node)
    in_reach = sorted(list(in_reach), key=lambda x: graph_def.ordering[x])

    node_cascade_cond = {n: list() for n in in_reach}
    this_node_to_idx = {n: idx for n, idx in enumerate(in_reach)}

    if False:
        for state in range(1 << len(in_reach)):

            graph = 1 << node_to_idx[node]
            for idx in range(len(in_reach)):
                if 1 << idx & state:
                    graph += 1 << node_to_idx[in_reach[idx]]

            reached = cascade1(node, graph)
            for n in reached:
                node_cascade_cond[n].append(graph)
    else:
        for reached, graph in pool.map(
            process_state,
            map(lambda x: (node, x, in_reach, node_to_idx), range(1 << len(in_reach))),
        ):
            for n in reached:
                node_cascade_cond[n].append(graph)

    # simplify conditions
    if False:
        for n, graphs in node_cascade_cond.items():
            relevant = []
            for other in in_reach:
                if other == n:
                    continue
                idx = node_to_idx[other]

                yes = list()
                no = list()

                for g in graphs:
                    if 1 << idx & g:
                        yes.append(g - 1 << idx)
                    else:
                        no.append(g)
                if len(yes) != len(no):
                    relevant.append(idx)
                else:
                    if sorted(yes) != sorted(no):
                        relevant.append(idx)
            conds = list()
            covered = set()
            for g in graphs:
                this_instr = list()
                for r in relevant:
                    name = node_to_code[node_list[r]]
                    if 1 << r & g:
                        this_instr.append(name)
                    # else:
                    #    this_instr.append('!' + name)
                instr_str = " ^ ".join(this_instr)
                if instr_str not in covered:
                    conds.append(this_instr)
                    covered.add(instr_str)

            # simplify, find smaller set and remove the rest
            conds = simplify(conds)

            result.append((n, conds))
    else:
        result = pool.map(
            make_conds,
            map(
                lambda x: (x[0], x[1], in_reach, node_to_idx), node_cascade_cond.items()
            ),
        )
    return result


#    all_graphs = list()
#    for


# all_graphs = list()
# all_graphs = list(range(1 << num_nodes))

if False:
    for node in node_list:
        in_reach = list(set([node] + reachable(node)))
        print("***", graph_def.node_names[node], len(in_reach), "***")
        pp_instructions(make_base_instructions(node))
else:
    for node in node_list:
        in_reach = list(set([node] + reachable(node)))
        print(
            "*** {} [{}]: {} ***".format(
                graph_def.node_names[node], node_to_code[node], len(in_reach)
            )
        )
        instr = node_instructions(node)
        recorded = set()
        for _, inss in instr:
            for ins in inss:
                recorded.update(set(ins))
        recorded = set([code_to_node[c] for c in recorded])
        r = list()
        for n in node_list:
            if n in recorded:
                r.append(node_to_code[n])
        print("    record ({}): {}".format(len(r), ", ".join(r)))
        if len(in_reach) < 30:
            pp_node_instructions(instr)
        else:
            print("  SKIPPED")
        print()
