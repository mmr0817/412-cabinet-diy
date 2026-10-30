# -*- coding: utf-8 -*-
"""
svgtool.py —— 极简 SVG 制图工具
所有坐标单位 = 纸面毫米(mm)，用于生成可直接 1:1 打印的施工图。
只依赖标准库。
"""
import math

INK = "#1b1b1b"
BLUE = "#0b5fa5"
RED = "#c0392b"
GRAY = "#808080"
LIGHT = "#c9c9c9"
PAPER = "#ffffff"
FONT = "'PingFang SC','Hiragino Sans GB','Microsoft YaHei','Noto Sans CJK SC',sans-serif"


def f(v):
    """数字格式化，去掉多余小数，避免 SVG 体积过大"""
    s = f"{v:.2f}"
    if s.endswith(".00"):
        s = s[:-3]
    elif s.endswith("0"):
        s = s[:-1]
    return s


def text_w(s, size):
    """粗估文字宽度（中文=1em，西文=0.56em）"""
    w = 0.0
    for ch in s:
        w += size * (1.0 if ord(ch) > 0x2E80 else 0.56)
    return w


def esc(s):
    """XML 转义，避免文字中的 < & 破坏 SVG"""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def fmt(v):
    """尺寸数值：整数就不带小数点"""
    if abs(v - round(v)) < 0.05:
        return f"{int(round(v))}"
    return f"{v:.1f}"


class Sheet(object):
    """一张图纸。子元素坐标均为纸面 mm，与 viewBox 一致，打印 100% 即为 1:1。"""

    def __init__(self, w, h, margin=8):
        self.w = w
        self.h = h
        self.m = margin
        self.items = []
        self.defs = []
        self._id = 0

    # ---------------- 基础图元 ----------------
    def add(self, s):
        self.items.append(s)

    def nid(self, pre="c"):
        self._id += 1
        return f"{pre}{self._id}"

    def line(self, p1, p2, w=0.25, color=INK, dash=None, cap="butt"):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(
            f'<line x1="{f(p1[0])}" y1="{f(p1[1])}" x2="{f(p2[0])}" y2="{f(p2[1])}" '
            f'stroke="{color}" stroke-width="{w}" stroke-linecap="{cap}"{d}/>'
        )

    def poly(self, pts, w=0.35, color=INK, fill="none", dash=None, close=True):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        p = " ".join(f"{f(x)},{f(y)}" for x, y in pts)
        tag = "polygon" if close else "polyline"
        self.add(
            f'<{tag} points="{p}" fill="{fill}" stroke="{color}" stroke-width="{w}" '
            f'stroke-linejoin="round"{d}/>'
        )

    def rect(self, x, y, w_, h_, sw=0.35, color=INK, fill="none", dash=None, rx=0):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(
            f'<rect x="{f(x)}" y="{f(y)}" width="{f(w_)}" height="{f(h_)}" rx="{f(rx)}" '
            f'fill="{fill}" stroke="{color}" stroke-width="{sw}"{d}/>'
        )

    def circle(self, c, r, sw=0.35, color=INK, fill="none", dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(
            f'<circle cx="{f(c[0])}" cy="{f(c[1])}" r="{f(r)}" fill="{fill}" '
            f'stroke="{color}" stroke-width="{sw}"{d}/>'
        )

    def dot(self, c, r=0.7, color=INK):
        self.add(f'<circle cx="{f(c[0])}" cy="{f(c[1])}" r="{f(r)}" fill="{color}"/>')

    def text(self, pos, s, size=3.2, anchor="start", color=INK, weight="normal",
             rotate=None, halo=False, dy=0.0):
        tr = f' transform="rotate({f(rotate)} {f(pos[0])} {f(pos[1])})"' if rotate else ""
        st = (f'font-family="{FONT}" font-size="{size}" fill="{color}" '
              f'text-anchor="{anchor}" font-weight="{weight}"')
        if halo:
            st += f' stroke="#ffffff" stroke-width="{size*0.28:.2f}" paint-order="stroke"'
        self.add(f'<text x="{f(pos[0])}" y="{f(pos[1]+dy)}" {st}{tr}>{esc(s)}</text>')

    def raw(self, s):
        self.add(s)

    # ---------------- 箭头 / 尺寸 ----------------
    def arrow(self, tip, d, size=2.2, color=INK):
        """tip: 箭头尖端; d: 指向尖端的单位向量"""
        px, py = -d[1], d[0]
        bx, by = tip[0] - d[0] * size, tip[1] - d[1] * size
        pts = [(tip[0], tip[1]),
               (bx + px * size * 0.3, by + py * size * 0.3),
               (bx - px * size * 0.3, by - py * size * 0.3)]
        p = " ".join(f"{f(x)},{f(y)}" for x, y in pts)
        self.add(f'<polygon points="{p}" fill="{color}"/>')

    def dim_h(self, x1, x2, y, label, ext=None, size=2.9, color=BLUE,
              above=True, out=False):
        """水平尺寸线。ext=(左端引出起点y, 右端引出起点y)，可省略。"""
        if x2 < x1:
            x1, x2 = x2, x1
            if ext:
                ext = (ext[1], ext[0])
        if ext:
            for xx, ya in ((x1, ext[0]), (x2, ext[1])):
                if ya is not None:
                    sgn = 1 if y > ya else -1
                    self.line((xx, ya + sgn * 1.0), (xx, y + sgn * 2.6), 0.16, color)
        self.line((x1, y), (x2, y), 0.22, color)
        if out:
            self.arrow((x1, y), (1, 0), 2.0, color)
            self.arrow((x2, y), (-1, 0), 2.0, color)
        else:
            self.arrow((x1, y), (-1, 0), 2.0, color)
            self.arrow((x2, y), (1, 0), 2.0, color)
        ly = y - 1.2 if above else y + size + 0.5
        self.text(((x1 + x2) / 2, ly), label, size, "middle", color)

    def dim_v(self, y1, y2, x, label, ext=None, size=2.9, color=BLUE, left=True):
        if y2 < y1:
            y1, y2 = y2, y1
            if ext:
                ext = (ext[1], ext[0])
        if ext:
            for yy, xa in ((y1, ext[0]), (y2, ext[1])):
                if xa is not None:
                    sgn = 1 if x > xa else -1
                    self.line((xa + sgn * 1.0, yy), (x + sgn * 2.6, yy), 0.16, color)
        self.line((x, y1), (x, y2), 0.22, color)
        self.arrow((x, y1), (0, -1), 2.0, color)
        self.arrow((x, y2), (0, 1), 2.0, color)
        tx = x - 1.4 if left else x + 3.0
        self.text((tx, (y1 + y2) / 2), label, size, "middle", color, rotate=-90)

    def dim_along(self, p1, p2, off, label, size=2.9, color=BLUE, ext=1.2):
        """倾斜尺寸线，off 为左法向偏移（纸面 mm）"""
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        L = math.hypot(dx, dy)
        if L < 1e-6:
            return
        ux, uy = dx / L, dy / L
        nx, ny = -uy, ux
        a = (p1[0] + nx * off, p1[1] + ny * off)
        b = (p2[0] + nx * off, p2[1] + ny * off)
        s = 1 if off > 0 else -1
        self.line((p1[0] + nx * s * ext, p1[1] + ny * s * ext), a, 0.16, color)
        self.line((p2[0] + nx * s * ext, p2[1] + ny * s * ext), b, 0.16, color)
        self.line(a, b, 0.22, color)
        self.arrow(a, (-ux, -uy), 2.0, color)
        self.arrow(b, (ux, uy), 2.0, color)
        ang = math.degrees(math.atan2(dy, dx))
        if ang > 90:
            ang -= 180
        if ang < -90:
            ang += 180
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        self.text((mx, my - 1.2), label, size, "middle", color, rotate=ang)

    def leader(self, at, to, label, size=3.0, color=INK):
        """引线标注: at=指向点, to=转折点"""
        self.dot(at, 0.5, color)
        self.line(at, to, 0.2, color)
        dx = 1 if to[0] >= at[0] else -1
        self.text((to[0] + dx * 0.8, to[1] - 1.0), label, size,
                  "start" if dx > 0 else "end", color)

    # ---------------- 剖面填充 ----------------
    def hatch(self, pts, angle=45, gap=1.8, color=GRAY, w=0.16):
        cid = self.nid("hp")
        p = " ".join(f"{f(x)},{f(y)}" for x, y in pts)
        self.defs.append(f'<clipPath id="{cid}"><polygon points="{p}"/></clipPath>')
        xs = [x for x, y in pts]
        ys = [y for x, y in pts]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        diag = math.hypot(x1 - x0, y1 - y0) + 6
        a = math.radians(angle)
        dx, dy = math.cos(a), math.sin(a)
        px, py = -dy, dx
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        n = int(diag / gap) + 2
        self.add(f'<g clip-path="url(#{cid})">')
        for i in range(-n, n + 1):
            ox, oy = cx + px * i * gap, cy + py * i * gap
            self.line((ox - dx * diag / 2, oy - dy * diag / 2),
                      (ox + dx * diag / 2, oy + dy * diag / 2), w, color)
        self.add("</g>")

    # ---------------- 图框 / 标题栏 ----------------
    def frame(self, title, no, scale_txt, sub="", note=""):
        m = self.m
        self.rect(m * 0.4, m * 0.4, self.w - m * 0.8, self.h - m * 0.8, 0.5, "#000")
        self.rect(m * 0.4 + 1.6, m * 0.4 + 1.6, self.w - m * 0.8 - 3.2,
                  self.h - m * 0.8 - 3.2, 0.22, "#000")
        bw, bh = 120, 25
        bx, by = self.w - m * 0.4 - bw, self.h - m * 0.4 - bh
        self.rect(bx, by, bw, bh, 0.35, "#000", PAPER)
        self.line((bx, by + 8.6), (bx + bw, by + 8.6), 0.28, "#000")
        self.line((bx, by + 17.0), (bx + bw, by + 17.0), 0.28, "#000")
        self.line((bx + 40, by + 8.6), (bx + 40, by + bh), 0.28, "#000")
        self.line((bx + 94, by + 17.0), (bx + 94, by + bh), 0.28, "#000")
        self.text((bx + 3, by + 6.2), "412 电吉他箱体 · DIY 施工图", 4.0, "start", "#000", "bold")
        self.text((bx + 2.5, by + 14.6), "图名", 2.4, "start", GRAY)
        self.text((bx + 3, by + 22.2), title, 3.5, "start", "#000", "bold")
        self.text((bx + 42.5, by + 14.6), "图号", 2.4, "start", GRAY)
        self.text((bx + 42.5, by + 22.0), no, 3.4, "start", "#000")
        self.text((bx + 96.5, by + 14.6), "比例", 2.4, "start", GRAY)
        self.text((bx + 96.5, by + 22.0), scale_txt, 3.2, "start", "#000")
        if sub:
            self.text((m * 0.4 + 6, m * 0.4 + 7.0), sub, 3.2, "start", GRAY)
        if note:
            self.text((m + 4, self.h - m - 3.5), note, 2.5, "start", GRAY)

    # ---------------- 输出 ----------------
    def svg(self):
        defs = f"<defs>{''.join(self.defs)}</defs>" if self.defs else ""
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{f(self.w)}mm" height="{f(self.h)}mm" '
            f'viewBox="0 0 {f(self.w)} {f(self.h)}">\n'
            f'<rect x="0" y="0" width="{f(self.w)}" height="{f(self.h)}" fill="{PAPER}"/>\n'
            f"{defs}\n" + "\n".join(self.items) + "\n</svg>\n"
        )

    def save(self, path):
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(self.svg())
        return path


def clip_poly(pts, rect):
    """Sutherland-Hodgman 矩形裁剪，用于节点详图只显示局部"""
    x0, y0, x1, y1 = rect

    def cut(poly, keep, inter):
        out = []
        n = len(poly)
        for i in range(n):
            a, b = poly[i], poly[(i + 1) % n]
            ka, kb = keep(a), keep(b)
            if ka:
                out.append(a)
            if ka != kb:
                out.append(inter(a, b))
        return out

    def ix(a, b, x):
        t = (x - a[0]) / (b[0] - a[0])
        return (x, a[1] + t * (b[1] - a[1]))

    def iy(a, b, y):
        t = (y - a[1]) / (b[1] - a[1])
        return (a[0] + t * (b[0] - a[0]), y)

    poly = list(pts)
    poly = cut(poly, lambda p: p[0] >= x0, lambda a, b: ix(a, b, x0))
    if not poly:
        return []
    poly = cut(poly, lambda p: p[0] <= x1, lambda a, b: ix(a, b, x1))
    if not poly:
        return []
    poly = cut(poly, lambda p: p[1] >= y0, lambda a, b: iy(a, b, y0))
    if not poly:
        return []
    poly = cut(poly, lambda p: p[1] <= y1, lambda a, b: iy(a, b, y1))
    return poly


class View(object):
    """模型坐标 -> 纸面坐标的视图变换。

    scale: 缩小倍数（5 即 1:5）；kx/ky 为模型坐标的符号（用于翻转轴向）
    """

    def __init__(self, s, kx, ky, ox, oy, scale=1.0):
        self.s = s
        self.kx = kx
        self.ky = ky
        self.ox = ox
        self.oy = oy
        self.k = s * scale        # 毫米 -> 图纸毫米 的除数（1:5 时 s=5）

    def p(self, a, b):
        return (self.ox + self.kx * a / self.k, self.oy + self.ky * b / self.k)

    def d(self, v):
        return v / self.k
