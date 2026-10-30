# -*- coding: utf-8 -*-
"""
render3d.py —— 极简三维渲染器（画家算法 + 平面着色），输出到 SVG
用于在施工图中生成轴测/爆炸图，并校验几何模型。
"""
import math

import geom


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def _norm(a):
    l = math.sqrt(_dot(a, a)) or 1.0
    return (a[0] / l, a[1] / l, a[2] / l)


def _centroid(ring):
    n = len(ring)
    return (sum(p[0] for p in ring) / n, sum(p[1] for p in ring) / n,
            sum(p[2] for p in ring) / n)


def _normal(ring):
    """前三点法向（环为凸/近似平面）"""
    a, b, c = ring[0], ring[1 % len(ring)], ring[2 % len(ring)]
    return _norm(_cross(_sub(b, a), _sub(c, a)))


def shade(hexcolor, k):
    hexcolor = hexcolor.lstrip("#")
    r, g, b = int(hexcolor[0:2], 16), int(hexcolor[2:4], 16), int(hexcolor[4:6], 16)
    r = max(0, min(255, int(r * k)))
    g = max(0, min(255, int(g * k)))
    b = max(0, min(255, int(b * k)))
    return "#%02x%02x%02x" % (r, g, b)


LIGHT = _norm((-0.45, 0.85, -0.35))


def render(sheet, parts, box, az=36.0, el=20.0, explode=0.0,
           only=None, ambient=0.52, edge="#4a3524", edge_w=0.16,
           cull=True, pad=4.0):
    """把 parts 自动缩放投影到纸面矩形 box=(x0,y0,x1,y1) 内。
    az: 绕 y 轴方位角(度)，el: 仰角(度)；cull: 背面剔除（组装视图开启）"""
    a = math.radians(az)
    e = math.radians(el)
    d = (math.cos(e) * math.sin(a), math.sin(e), math.cos(e) * math.cos(a))
    r = _norm(_cross((-d[0], 0.0, -d[2]), (0, 1, 0)))
    if abs(r[0]) + abs(r[2]) < 1e-6:
        r = (1.0, 0.0, 0.0)
    u = _norm(_cross(d, r))
    c0 = (geom.W / 2.0, geom.H / 2.0, geom.D / 2.0)

    items = []
    xs, ys = [], []
    for p in parts:
        if only and p["id"] not in only:
            continue
        ex = p.get("explode", (0, 0, 0))
        lay = p.get("layer", 0)
        off = (ex[0] * explode, ex[1] * explode, ex[2] * explode)
        for face in p["faces"]:
            rings = []
            for ring in face:
                rings.append([(q[0] + off[0] - c0[0], q[1] + off[1] - c0[1],
                               q[2] + off[2] - c0[2]) for q in ring])
            n = _normal(rings[0])
            if cull and _dot(n, d) <= 0.0:
                continue
            c = _centroid(rings[0])
            items.append((lay, _dot(c, d), rings, p["color"], n))
            for q in rings[0]:
                px, py = _dot(q, r), _dot(q, u)
                xs.append(px)
                ys.append(py)

    items.sort(key=lambda t: (t[0], t[1]))
    if not xs:
        return
    x0, y0, x1, y1 = box
    pw = max(4.0, x1 - x0 - 2 * pad)
    ph = max(4.0, y1 - y0 - 2 * pad)
    k = max((max(xs) - min(xs)) / pw, (max(ys) - min(ys)) / ph)   # 毫米/图纸毫米
    ox = (x0 + x1) / 2 - (max(xs) + min(xs)) / 2 / k
    oy = (y0 + y1) / 2 + (max(ys) + min(ys)) / 2 / k
    # 纸面 y 向下：图纸 y = oy - cam_y/k

    def prj(q):
        return (ox + _dot(q, r) / k, oy - _dot(q, u) / k)

    for _lay, depth, rings, color, n in items:
        lam = max(0.0, _dot(n, LIGHT))
        fill = shade(color, ambient + (1 - ambient) * lam)
        path = []
        for ring in rings:
            pts = [prj(q) for q in ring]
            path.append("M " + " L ".join("%.2f,%.2f" % (x, y) for x, y in pts) + " Z")
        sheet.add('<path d="%s" fill="%s" fill-rule="evenodd" stroke="%s" '
                  'stroke-width="%.2f" stroke-linejoin="round"/>'
                  % (" ".join(path), fill, edge, edge_w))
    return k



def bbox(parts):
    xs, ys, zs = [], [], []
    for p in parts:
        for f in p["faces"]:
            for rg in f:
                for q in rg:
                    xs.append(q[0])
                    ys.append(q[1])
                    zs.append(q[2])
    return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))
