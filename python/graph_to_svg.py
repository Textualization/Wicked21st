import sys
import math

from wicked21st.graph import load_graph, Graph

import svgwrite
import cairo

CARTOUCHE_SIZE = 100
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

## RADS

current_rad = 0
node_to_rad = dict()
node_to_code = dict()
for catid in g.node_classes:
    nodes = g.node_classes[catid]
    
    for node in sorted(nodes, key=lambda x:g.ordering[x]):
        code = g.node_names[node].upper()[:3]
        if code in node_to_code:
            g.node_names[node].upper().split(" ")[1][:3]
            if code in node_to_code:
                raise Error(g.node_names[node]+ " " + str(node_to_code))
        node_to_code[node] = code
        node_to_rad[node] = current_rad
        current_rad += rad_per_node

## STATS
node_to_stats = dict()
for node in g.node_names.keys():
    rad = node_to_rad[node]
    order = g.ordering[node]
    total_out = len(g.outlinks[node])
    cat_out = 0
    for other in g.outlinks[node]:
        if g.class_for_node[other] == g.class_for_node[node]:
            cat_out += 1
    total_in = 0
    cat_in = 0
    for other in g.node_names.keys():
        if other != node and node in g.outlinks[other]:
            total_in += 1
            if g.class_for_node[other] == g.class_for_node[node]:
                cat_in += 1
    node_to_stats[node] = { 'out' : (total_out, cat_out), 'in' : (total_in, cat_in) }

## ARROWS
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
    rad = node_to_rad[node]

    cx = math.cos(rad) * NODE_EDGE_LEN + 540
    cy = math.sin(rad) * NODE_EDGE_LEN + 540
    
    #p = Path('m0,0')
    #p.push_arc(target=(7,7), rotation=30, r=(2,4), large_arc=False, angle_dir='-', absolute=True)
    
    for other in g.outlinks[node]:
        rado = node_to_rad[other]
        if g.class_for_node[node] != g.class_for_node[other]:
            xo = math.cos(rado) * (NODE_EDGE_LEN - (CARTOUCHE_SIZE / 2) * 1.1) + 540
            yo = math.sin(rado) * (NODE_EDGE_LEN - (CARTOUCHE_SIZE / 2) * 1.1) + 540
            
            line = dwg.add(dwg.line((cx,cy), (xo, yo), stroke=g.class_for_node[node], style="stroke-width:3;stroke-miterlimit:4;stroke-dasharray:none"))
            line.set_markers((None, False, arrow))
        else:
            radm = min(rad,rado) + (max(rad,rado) - min(rad,rado)) / 1.3
            mult = 1.0 if min(rad,rado) == rad else 1.1
            xm = math.cos(radm) * (NODE_EDGE_LEN + CARTOUCHE_SIZE * mult) + 540
            ym = math.sin(radm) * (NODE_EDGE_LEN + CARTOUCHE_SIZE * mult) + 540
            
            xo = math.cos(rado) * (NODE_EDGE_LEN + (CARTOUCHE_SIZE / 2) * 1.1) + 540
            yo = math.sin(rado) * (NODE_EDGE_LEN + (CARTOUCHE_SIZE / 2) * 1.1) + 540
            line1 = dwg.add(dwg.line((cx,cy), (xm, ym), stroke="black"))
            line2 = dwg.add(dwg.line((xm,ym), (xo, yo), stroke="black"))
            line2.set_markers((None, False, arrow))

## CARTOUCHES
for node in g.node_names.keys():
    rad = node_to_rad[node]
    catid = g.class_for_node[node]
    
    x = math.cos(rad) * NODE_EDGE_LEN + 540 - CARTOUCHE_SIZE / 2
    y = math.sin(rad) * NODE_EDGE_LEN + 540 - CARTOUCHE_SIZE / 2
    cx = math.cos(rad) * NODE_EDGE_LEN + 540 
    cy = math.sin(rad) * NODE_EDGE_LEN + 540
    cart = dwg.add(dwg.g(id='cartouche' + node, fill=catid))
    r = dwg.rect(insert=(x,y), size=(CARTOUCHE_SIZE, CARTOUCHE_SIZE), rx=5, ry=5, style="stroke:#000000;stroke-opacity:1;stroke-width:2;stroke-miterlimit:4;stroke-dasharray:none")
    cart.add(r)

    text = g.node_names[node]
    words = text.split(" ")
    lines = [ "" ]
    for word in words:
        w = textwidth(lines[-1] + " " + word, 'Arial', 9)
        if w > CARTOUCHE_SIZE * 0.8:
            lines.append(word)
        else:
            if lines[-1] != "":
                lines[-1] += " "
            lines[-1] += word
            
    yt = y + CARTOUCHE_SIZE * 0.66
    title = dwg.g(id='title' + node, fill='black')
    for line in lines:
        w = textwidth(line, 'Arial', 9)
        xt = x + CARTOUCHE_SIZE / 2 - w / 2
        t = dwg.text(line, insert=(xt, yt), fill='black', style='font-family:Arial;font-weight:normal;font-style:normal;font-stretch:normal;font-variant:normal;font-size:9px;font-variant-ligatures:normal;font-variant-caps:normal;font-variant-numeric:normal;font-variant-east-asian:normal')
        title.add(t)
        yt += 12

    title.rotate( 90, center=(cx,cy) )
    cart.add(title)

    yt = y + CARTOUCHE_SIZE * 0.66
    title = dwg.g(id='title2' + node, fill='black')
    for line in lines:
        w = textwidth(line, 'Arial', 9)
        xt = x + CARTOUCHE_SIZE / 2 - w / 2
        t = dwg.text(line, insert=(xt, yt), fill='black', style='font-family:Arial;font-weight:normal;font-style:normal;font-stretch:normal;font-variant:normal;font-size:9px;font-variant-ligatures:normal;font-variant-caps:normal;font-variant-numeric:normal;font-variant-east-asian:normal')
        title.add(t)
        yt += 12
    title.rotate( 270, center=(cx,cy) )
    cart.add(title)

    codet = node_to_code[node]
    code = dwg.g(id='code' + node, fill='black')
    yt = y + CARTOUCHE_SIZE / 2 + 7
    xt = x + CARTOUCHE_SIZE / 2 + 14
    t = dwg.text(codet, insert=(xt, yt), fill='white', style='font-family:Arial;font-weight:normal;font-style:normal;font-stretch:normal;font-variant:normal;font-size:14px;font-variant-ligatures:normal;font-variant-caps:normal;font-variant-numeric:normal;font-variant-east-asian:normal')
    code.add(t)
    code.rotate( 90, center=(cx,cy) )
    cart.add(code)

    code = dwg.g(id='code2' + node, fill='black')
    yt = y + CARTOUCHE_SIZE / 2 + 7
    xt = x + CARTOUCHE_SIZE / 2 + 14
    t = dwg.text(codet, insert=(xt, yt), fill='white', style='font-family:Arial;font-weight:normal;font-style:normal;font-stretch:normal;font-variant:normal;font-size:14px;font-variant-ligatures:normal;font-variant-caps:normal;font-variant-numeric:normal;font-variant-east-asian:normal')
    code.add(t)
    code.rotate( 270, center=(cx,cy) )
    cart.add(code)

    stats = dwg.g(id='stats' + node, fill='black')
    s = node_to_stats[node]
    t = dwg.text("<" + str(s['out'][1]), insert=(x+10, y+20), fill="white", style='font-family:Arial;font-weight:normal;font-style:normal;font-stretch:normal;font-variant:normal;font-size:16px;font-variant-ligatures:normal;font-variant-caps:normal;font-variant-numeric:normal;font-variant-east-asian:normal')
    stats.add(t)
    t = dwg.text("<" + str(s['out'][0]), insert=(x+CARTOUCHE_SIZE - 20, y+20), fill="white", style='font-family:Arial;font-weight:normal;font-style:normal;font-stretch:normal;font-variant:normal;font-size:16px;font-variant-ligatures:normal;font-variant-caps:normal;font-variant-numeric:normal;font-variant-east-asian:normal')
    stats.add(t)
    t = dwg.text(">" + str(s['in'][1]), insert=(x+10, y+CARTOUCHE_SIZE - 10), fill="white", style='font-family:Arial;font-weight:normal;font-style:normal;font-stretch:normal;font-variant:normal;font-size:16px;font-variant-ligatures:normal;font-variant-caps:normal;font-variant-numeric:normal;font-variant-east-asian:normal')
    stats.add(t)
    t = dwg.text(">" + str(s['in'][0]), insert=(x+CARTOUCHE_SIZE - 20, y+CARTOUCHE_SIZE - 10), fill="white", style='font-family:Arial;font-weight:normal;font-style:normal;font-stretch:normal;font-variant:normal;font-size:16px;font-variant-ligatures:normal;font-variant-caps:normal;font-variant-numeric:normal;font-variant-east-asian:normal')
    stats.add(t)
    #print(g.node_names[node], s)   
    cart.add(stats)
    
    cart.rotate( (rad + math.pi) * 180 / math.pi, center = (cx,cy) )


dwg.save()
