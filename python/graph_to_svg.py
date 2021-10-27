import sys
import math

from wicked21st.graph import load_graph, Graph

import svgwrite
import cairo

CARTOUCHE_SIZE = 72
NODE_EDGE_LEN = 500
CAT_EDGE_LEN = 250


def textwidth(text, font='Arial', fontsize=14):
    surface = cairo.SVGSurface('undefined.svg', 1080, 1080)
    cr = cairo.Context(surface)
    cr.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    cr.set_font_size(fontsize)
    xbearing, ybearing, width, height, xadvance, yadvance = cr.text_extents(text)
    return width

g = load_graph(sys.argv[1])
dwg = svgwrite.Drawing(sys.argv[2], size=(1080,1080))
dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), rx=None, ry=None, fill='white'))

total_nodes = len(g.node_names)
rad_per_node = 2 * math.pi * 1.0 / total_nodes

current_rad = 0



# draw cartouches
for catn, catid in enumerate(g.node_classes):
    node_count = len(g.node_classes[catid])

    carts = dwg.add(dwg.g(id='cartouches' + str(catn), fill=catid))
    for node in range(node_count):
        x = math.cos(current_rad) * NODE_EDGE_LEN * 0.97 + 540 - CARTOUCHE_SIZE / 2
        y = math.sin(current_rad) * NODE_EDGE_LEN * 0.97 + 540 - CARTOUCHE_SIZE / 2
        current_rad += rad_per_node
        r = dwg.rect(insert=(x,y), size=(CARTOUCHE_SIZE, CARTOUCHE_SIZE), rx=5, ry=5)
        r.rotate( (current_rad + math.pi) * 180 / math.pi, center = (x,y) )
        carts.add(r)


node_to_xy_rad = dict()

#print(g.node_classes)

current_rad = 0
for catid in g.node_classes:
    nodes = g.node_classes[catid]

    #print("category: '{}' (size: {})".format(cat, len(nodes)))
    for node in sorted(nodes, key=lambda x:g.node_names[x]):
        text = g.node_names[node]
        text = text.replace(' ', '\n')
        xt = math.cos(current_rad) * NODE_EDGE_LEN + 540
        yt = math.sin(current_rad) * NODE_EDGE_LEN + 540
        x = math.cos(current_rad) * NODE_EDGE_LEN * 0.97 + 540
        y = math.sin(current_rad) * NODE_EDGE_LEN * 0.97 + 540
        w = textwidth(g.node_names[node], 'Arial', 9)
        print(text, w)
        xt = xt - w
        node_to_xy_rad[node] = (x,y, current_rad)
        dwg.add(dwg.text(text, insert=(xt, yt), fill='black', style='font-family:Arial;font-weight:normal;font-style:normal;font-stretch:normal;font-variant:normal;font-size:9px;font-variant-ligatures:normal;font-variant-caps:normal;font-variant-numeric:normal;font-variant-east-asian:normal'))
        #dwg.add(dwg.text(g.node_names[node], insert=(x, y), fill=catid)) # , rotate=[ current_rad / math.pi * 180 ]))
        
        current_rad += rad_per_node
        #print("\t" + graph_def.node_names[node])
        #print("\t\tLinks to: " + "; ".join(sorted(list(map(lambda x:graph_def.node_names[x], graph_def.outlinks[node])))))

marker = dwg.marker(insert=(5,5), size=(10,10))
marker.add(dwg.circle((5, 5), r=5, fill='red'))
dwg.defs.add(marker)

def create_arrow_marker(dwg):
    #   <defs>
    #     <marker id="arrow" markerWidth="10" markerHeight="10" refX="0" refY="3" orient="auto" markerUnits="strokeWidth">
    #       <path d="M0,0 L0,6 L9,3 z" fill="#f00" />
    #     </marker>
    #   </defs>
    arrow = dwg.marker(id='arrow', insert=(0, 3), size=(10, 10), orient='auto', markerUnits='strokeWidth')
    arrow.add(dwg.path(d='M0,0 L0,6 L9,3 z', fill='#f00'))
    dwg.defs.add(arrow)
    return arrow

arrow = create_arrow_marker(dwg)

#dwg.add(dwg.path(ps, stroke=svgwrite.rgb(0+dc, 0+dc, 16, '%'), fill='none'))

for node in g.node_names.keys():
    _, _, rad = node_to_xy_rad[node]
    x = math.cos(rad) * NODE_EDGE_LEN * 0.9 + 540
    y = math.sin(rad) * NODE_EDGE_LEN * 0.9 + 540

    #p = Path('m0,0')
    #p.push_arc(target=(7,7), rotation=30, r=(2,4), large_arc=False, angle_dir='-', absolute=True)

    
    for other in g.outlinks[node]:
        if True: #g.class_for_node[node] != g.class_for_node[other]:
            xo, yo, _ = node_to_xy_rad[other]
            line = dwg.add(dwg.line((x,y), (xo, yo), stroke=g.class_for_node[node]))
            line.set_markers((marker, False, arrow))

dwg.save()
