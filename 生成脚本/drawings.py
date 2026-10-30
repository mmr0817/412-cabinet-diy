# -*- coding: utf-8 -*-
"""
drawings.py —— 生成全部施工图（SVG）
01 总装三视图 / 02 侧板 / 03 平板件 / 04 障板 / 05 网罩框
06 下料清单与排板 / 07 接线图与五金 / 08 剖面详图
"""
import math

import geom as g
import render3d
import svgtool
from svgtool import Sheet, View, fmt, INK, BLUE, RED, GRAY, LIGHT

LINE = 0.55      # 轮廓线宽
THIN = 0.25      # 细线
DASH = "3,2"


def notes(s, x, y, lines, size=2.9, lh=4.5, title=None):
    if title:
        s.text((x, y), title, size + 0.8, "start", INK, "bold")
        y += lh + 1.2
    for t in lines:
        s.text((x, y), t, size, "start", INK)
        y += lh
    return y


def centre_marks(s, c, r, color=LIGHT, dash="8,2,1.5,2"):
    s.line((c[0] - r, c[1]), (c[0] + r, c[1]), 0.18, color, dash)
    s.line((c[0], c[1] - r), (c[0], c[1] + r), 0.18, color, dash)


def callout(s, at, n, dx=6.0, dy=-6.0, color=INK):
    """序号标注气泡"""
    s.dot(at, 0.45, color)
    s.line(at, (at[0] + dx * 0.55, at[1] + dy * 0.55), 0.2, color)
    c = (at[0] + dx, at[1] + dy)
    s.circle(c, 2.2, 0.3, color, "#ffffff")
    s.text((c[0], c[1] + 1.15), str(n), 3.0, "middle", color)


# ======================================================================
def sheet01():
    k = 5.0
    s = Sheet(420, 297)
    s.frame("总装三视图", "01 / 08", "1:5", sub="412 箱体 · 外形 760 × 760 × 355 · 单位 mm")

    # ---------------- 正视图 ----------------
    V = View(k, 1, -1, 34, 178)
    P = V.p
    s.poly([P(0, 0), P(g.W, 0), P(g.W, g.H), P(0, g.H)], LINE)
    s.poly([P(20, 20), P(g.W - 20, 20), P(g.W - 20, g.H - 20), P(20, g.H - 20)], THIN)
    for cy in g.SPK_CY:
        for cx in g.SPK_CX:
            c = P(cx, cy)
            s.circle(c, (g.SPK_OD + 6) / 2 / k, 0.45)
            s.circle(c, g.SPK_CUT / 2 / k, 0.22, GRAY, dash=DASH)
            centre_marks(s, c, 172 / k)
    s.text((P(g.W / 2, 0)[0], 185), "正视图（前）", 3.4, "middle", INK, "bold")
    s.dim_h(P(0, 0)[0], P(g.W, 0)[0], 192, "760", ext=(178, 178))
    s.dim_v(178, 26, 27, "760", ext=(34, 34))
    s.dim_h(P(g.SPK_CX[0], g.H)[0], P(g.SPK_CX[1], g.H)[0], 21, "340", ext=(26, 26))
    s.text((P(380, 0)[0], 197), "喇叭中心 210 / 550，间距 340", 2.6, "middle", GRAY)

    # ---------------- 侧视图 ----------------
    V2 = View(k, 1, -1, 216, 178)
    Q = V2.p
    s.poly([Q(0, 0), Q(g.D, 0), Q(g.D, g.H), Q(g.SLANT, g.H)], LINE)
    s.line(Q(g.zf(g.H - g.T), g.H - g.T), Q(g.D, g.H - g.T), 0.3)      # 顶板下皮
    s.line(Q(0, g.T), Q(g.D, g.T), 0.3)                               # 底板上皮
    s.line(Q(g.D - g.T, g.T), Q(g.D - g.T, g.H - g.T), 0.3)           # 后板前面
    s.line(Q(g.zb(g.T), g.T), Q(g.zb(g.H - g.T), g.H - g.T), 0.45)    # 障板前面
    s.line(Q(g.zb(g.T) + g.T, g.T), Q(g.zb(g.H - g.T) + g.T, g.H - g.T), 0.25, GRAY)
    s.line(Q(g.zg(g.T), g.T), Q(g.zg(g.H - g.T), g.H - g.T), 0.45)    # 网罩框前面
    s.text((Q(g.D / 2, 0)[0], 185), "侧视图（左）", 3.4, "middle", INK, "bold")
    s.dim_h(Q(0, 0)[0], Q(g.D, 0)[0], 192, "355", ext=(178, 178))
    s.dim_h(Q(0, g.H)[0], Q(g.SLANT, g.H)[0], 21, "60", ext=(26, 26))
    s.dim_h(Q(g.SLANT, g.H)[0], Q(g.D, g.H)[0], 21, "295", ext=(26, 26))
    s.dim_v(178, 26, 293, "760", ext=(287, 287))
    # 角度
    c0 = Q(g.SLANT, g.H)
    s.line(c0, (c0[0], c0[1] + 16), 0.2, BLUE, dash="2,1.5")
    s.raw('<path d="M %.1f,%.1f A 12,12 0 0 0 %.1f,%.1f" fill="none" stroke="%s" '
          'stroke-width="0.22"/>' % (c0[0], c0[1] + 12, c0[0] - 12 * math.sin(g.A),
                                     c0[1] + 12 * math.cos(g.A), BLUE))
    s.text((c0[0] - 11, c0[1] + 24), "4.51°", 2.7, "middle", BLUE)
    # 内部引线标注
    s.leader(Q(210, 700), Q(150, 700), "顶板 18", 2.5, GRAY)
    s.leader(Q(85, 560), Q(150, 560), "障板 18（斜置）", 2.5, GRAY)
    s.leader(Q(60, 440), Q(150, 440), "网罩框 18", 2.5, GRAY)
    s.leader(Q(16, 300), Q(150, 300), "前唇 18", 2.5, GRAY)
    s.leader(Q(300, 120), Q(346, 120), "后板 18", 2.5, GRAY)
    s.leader(Q(210, 44), Q(150, 44), "底板 18", 2.5, GRAY)

    # ---------------- 俯视图 ----------------
    V3 = View(k, 1, -1, 34, 283)
    R = V3.p
    s.poly([R(0, 0), R(g.W, 0), R(g.W, g.D), R(0, g.D)], LINE)
    s.line(R(0, g.SLANT), R(g.W, g.SLANT), 0.3)
    s.line(R(g.T, 0), R(g.T, g.D), 0.18, GRAY, dash="2,2")
    s.line(R(g.W - g.T, 0), R(g.W - g.T, g.D), 0.18, GRAY, dash="2,2")
    s.line(R(0, g.D - g.T), R(g.W, g.D - g.T), 0.18, GRAY, dash="2,2")
    s.text((R(g.W / 2, 0)[0], 207), "俯视图（上）", 3.4, "middle", INK, "bold")
    s.dim_h(R(0, 0)[0], R(g.W, 0)[0], 289, "760", ext=(283, 283))
    s.dim_v(212, 283, 194, "355", ext=(186, 186), left=False)
    s.leader(R(240, g.SLANT), R(150, g.SLANT), "顶板前边", 2.5, GRAY)

    # ---------------- 说明 ----------------
    notes(s, 300, 26, [
        "1. 单位 mm，未注公差 ±1，对角线误差 < 2。",
        "2. 板材 18mm 桦木多层板（桦木胶合板）。",
        "3. 外形参考 Marshall 1960A：760×760×355。",
        "4. 前脸后倾 4.51°，顶面比底面窄 60。",
        "5. 障板前面比外前脸后退 36（法向），",
        "　 网罩框厚 18，形成 18 前唇（喷漆后为黑色凹边）。",
        "6. 障板斜置，喇叭轴线上仰 4.51°。",
        "7. 内角接缝必须打胶密封（气密=低频）。",
        "8. 组装后量对角线，误差 < 2 再批灰喷漆。",
        "9. 外棱 R6 圆角、提手/脚轮位置见图 09；未计漆膜厚度。",
    ], 2.8, 4.4, "说明")

    parts = [p for p in g.build_parts() if p["id"] != "cloth"]
    render3d.render(s, parts, (300, 118, 410, 232), az=146, el=20, cull=True)
    s.text((300, 236), "轴测示意（不含网布与漆面）", 2.6, "start", GRAY)
    return s



def sheet02():
    k = 4.0
    s = Sheet(420, 297)
    s.frame("侧板（2 件）", "02 / 08", "1:4", sub="18mm 桦木多层板 · 前边斜切 4.51°")
    V = View(k, 1, -1, 55, 212)
    P = V.p
    s.poly([P(0, 0), P(g.D, 0), P(g.D, g.H), P(g.SLANT, g.H)], LINE)
    # 提手安装位（表面式拉手，孔距 152）
    hz0 = g.D / 2 - g.HANDLE_L / 2
    s.rect(P(hz0, g.HANDLE_Y + g.HANDLE_H / 2)[0], P(hz0, g.HANDLE_Y + g.HANDLE_H / 2)[1],
           g.HANDLE_L / k, g.HANDLE_H / k, 0.3, GRAY, dash="3,2")
    for zz in (g.D / 2 - 76, g.D / 2 + 76):
        s.circle(P(zz, g.HANDLE_Y), 1.3, 0.3, INK, "#ffffff")
    s.text((P(g.D / 2, g.HANDLE_Y - 116)[0], P(g.D / 2, g.HANDLE_Y - 116)[1]),
           "提手 180×60，孔距 152", 2.5, "middle", GRAY)
    # 尺寸
    s.dim_h(P(0, 0)[0], P(g.D, 0)[0], 221, "355", ext=(212, 212))
    s.dim_h(P(0, g.H)[0], P(g.SLANT, g.H)[0], 18, "60", ext=(24, 24))
    s.dim_h(P(g.SLANT, g.H)[0], P(g.D, g.H)[0], 18, "295", ext=(24, 24))
    s.dim_v(212, 22, 152, "760", ext=(139, 139))
    s.dim_along(P(g.SLANT, g.H), P(0, 0), 11, "762.4", 2.8, BLUE)
    c0 = P(g.SLANT, g.H)
    s.line(c0, (c0[0], c0[1] + 26), 0.2, BLUE, dash="2,1.5")
    s.raw('<path d="M %.1f,%.1f A 18,18 0 0 0 %.1f,%.1f" fill="none" stroke="%s" '
          'stroke-width="0.22"/>' % (c0[0], c0[1] + 18, c0[0] - 18 * math.sin(g.A),
                                     c0[1] + 18 * math.cos(g.A), BLUE))
    s.text((c0[0] - 16, c0[1] + 32), "4.51°", 2.7, "middle", BLUE)
    s.text((P(g.D / 2, 0)[0], 232), "侧板（左右各 1，形状相同）", 3.4, "middle", INK, "bold")

    notes(s, 200, 40, [
        "• 共 2 件，左右完全一样，不用分左右。",
        "• 前边（长边）斜切 4.51°：底部长 355，",
        "　顶部长 295，即顶面比底面内收 60。",
        "• 斜边长度 762.4（=760 / cos4.51°）。",
        "• 下料时留 1~2mm 余量，组装前再修到位。",
        "• 纹理方向：长边顺纹，强度更好。",
        "• 提手：表面式金属拉手（中心距 152），",
        "　在板上钻 2 个 Ø6.5 通孔，用 M5 螺栓对穿；",
        "　内侧可垫 30mm 垫片分散受力。",
        "• 板面若翘曲，以凹面朝内、凸面朝外。",
        "• 侧板前缘是箱体的外轮廓，必须与顶/底板",
        "　前缘对齐，误差控制在 1mm 内。",
        "• 组装后外棱全部 R6 倒角（见 09 图）。",
    ], 2.9, 4.7, "加工要点")

    notes(s, 200, 120, [
        "1) 先切出 760 × 355 的矩形；",
        "2) 从底边前角沿后边量 760（全高）；",
        "3) 沿顶边向内量 60 得一点；",
        "4) 两点连线即为前斜边，沿线锯切、刨平。",
        "　 也可以按 1 : 12.67 的斜度尺画线。",
        "",
        "两块板切完叠在一起对一下，斜边应完全重合；",
        "有一点不齐，组装后就会变成箱体的扭斜。",
    ], 2.8, 4.6, "画线方法")
    return s



def sheet03():
    k = 5.0
    s = Sheet(420, 297)
    s.frame("顶板 / 底板 / 后板", "03 / 08", "1:5", sub="18mm 桦木多层板")

    # ---- 后板 ----
    V = View(k, 1, -1, 30, 175)
    P = V.p
    s.poly([P(0, 0), P(g.WIN, 0), P(g.WIN, g.WIN), P(0, g.WIN)], LINE)
    s.rect(P(312, 140)[0], P(312, 140)[1], 100 / k, 40 / k, 0.35, INK, "#eeeeee")
    s.text((P(362, 132)[0], P(362, 132)[1]), "插孔板", 2.2, "middle", INK)
    s.text((P(g.WIN / 2, 0)[0], 182), "后板（可拆）", 3.4, "middle", INK, "bold")
    s.dim_h(P(0, 0)[0], P(g.WIN, 0)[0], 189, "724", ext=(175, 175))
    s.dim_v(175, 30.2, 24, "724", ext=(30, 30))
    s.leader(P(362, 160), P(230, 160), "100×40 插孔板开孔", 2.5, GRAY)

    # ---- 顶板 ----
    V2 = View(k, 1, -1, 200, 94)
    Q = V2.p
    s.poly([Q(0, 0), Q(g.WIN, 0), Q(g.WIN, g.DTOP), Q(0, g.DTOP)], LINE)
    s.text((Q(g.WIN / 2, 0)[0], 101), "顶板", 3.4, "middle", INK, "bold")
    s.dim_h(Q(0, 0)[0], Q(g.WIN, 0)[0], 108, "724", ext=(94, 94))
    s.dim_v(94, 35, 194, "295", ext=(200, 200))
    s.text((Q(g.WIN / 2, g.DTOP / 2)[0], Q(g.WIN / 2, g.DTOP / 2)[1] + 2.5),
           "前口倒 1.4mm 斜口", 2.4, "middle", GRAY)

    # ---- 底板 ----
    V3 = View(k, 1, -1, 200, 186)
    R = V3.p
    s.poly([R(0, 0), R(g.WIN, 0), R(g.WIN, g.D), R(0, g.D)], LINE)
    for cx in (80, g.WIN - 80):
        for cz in (80, g.D - 80):
            s.circle(R(cx, cz), 2.4, 0.3, INK, "#ffffff")
            s.dot(R(cx, cz), 0.3)
    s.text((R(g.WIN / 2, 0)[0], 193), "底板", 3.4, "middle", INK, "bold")
    s.dim_h(R(0, 0)[0], R(g.WIN, 0)[0], 200, "724", ext=(186, 186))
    s.dim_v(186, 115, 194, "355", ext=(200, 200))
    s.leader(R(80, 275), R(150, 250), "脚轮 M8 ×4（T 母）", 2.5, GRAY)

    notes(s, 20, 200, [
        "后板：四周用 4×35 木螺丝拧入 18×18 托条（间距约 150），建议加 3mm 泡棉密封条；",
        "　　　插孔板开孔位置可按自己习惯上下移动。",
        "顶板：前口与斜置障板相接，需倒 4.51° 斜口，倒角量约 1.4mm（刨或砂盘修）。",
        "底板：脚轮 2 万向装后侧、2 定向装前侧；家用也可只装 4 个橡胶脚垫。",
        "通用：所有板件切好后先试装（含障板、网罩框），确认无误再包皮。",
    ], 2.85, 5.2, "加工说明")
    return s


def sheet04():
    k = 4.0
    s = Sheet(420, 297)
    s.frame("喇叭障板", "04 / 08", "1:4 / 1:2", sub="18mm 桦木多层板 · 斜置 4.51°")
    V = View(k, 1, -1, 42, 200)
    P = V.p
    s.poly([P(0, 0), P(g.BAFFLE_W, 0), P(g.BAFFLE_W, g.BAFFLE_H), P(0, g.BAFFLE_H)], LINE)
    for cy in g.SPK_CY:
        for cx in g.SPK_CX:
            u, v = g.uv(cx, cy)
            c = P(u, v)
            s.circle(c, g.SPK_CUT / 2 / k, 0.5)
            s.circle(c, g.SPK_BCD / 2 / k, 0.2, GRAY, dash="4,1.5")
            for i in range(g.SPK_N):
                a = math.radians(90 + i * 360.0 / g.SPK_N)
                hp = P(u + g.SPK_BCD / 2 * math.cos(a), v + g.SPK_BCD / 2 * math.sin(a))
                s.circle(hp, g.SPK_HOLE / 2 / k + 0.15, 0.3, INK, "#ffffff")
            centre_marks(s, c, 160 / k)
    for u in (340, 384):
        s.circle(P(u, 363.1), 5 / k, 0.35, RED, "#ffffff")
    # 网罩磁吸点（8 处，对应网罩框上的钕磁铁）
    mags = []
    for dx in (-330, 0, 330):
        for dy in (-330, 330):
            if dx == 0 and dy == 0:
                continue
            mags.append((362 + dx, 363.1 + dy))
    for dx, dy in ((-330, 0), (330, 0)):
        mags.append((362 + dx, 363.1 + dy))
    for u, v in mags:
        c = P(u, v)
        s.circle(c, 2.0, 0.3, BLUE)
        s.line((c[0] - 3, c[1]), (c[0] + 3, c[1]), 0.2, BLUE)
        s.line((c[0], c[1] - 3), (c[0], c[1] + 3), 0.2, BLUE)
    s.text((P(g.BAFFLE_W / 2, 0)[0], 208), "喇叭障板（展开图，按平面下料）", 3.4, "middle", INK, "bold")
    # 尺寸
    u1, u2 = g.uv(g.SPK_CX[0], 0)[0], g.uv(g.SPK_CX[1], 0)[0]
    v1 = g.uv(0, g.SPK_CY[0])[1]
    v2 = g.uv(0, g.SPK_CY[1])[1]
    s.dim_h(P(0, g.BAFFLE_H)[0], P(u1, g.BAFFLE_H)[0], 24, "192", ext=(28, 28))
    s.dim_h(P(u1, g.BAFFLE_H)[0], P(u2, g.BAFFLE_H)[0], 24, "340", ext=(28, 28))
    s.dim_h(P(u2, g.BAFFLE_H)[0], P(g.BAFFLE_W, g.BAFFLE_H)[0], 24, "192", ext=(28, 28))
    s.dim_h(P(0, 0)[0], P(g.BAFFLE_W, 0)[0], 215, "724", ext=(200, 200))
    s.dim_v(200, P(0, v1)[1], 33, "192.6", ext=(42, 42))
    s.dim_v(P(0, v1)[1], P(0, v2)[1], 33, "341.1", ext=(42, 42))
    s.dim_v(P(0, v2)[1], 28, 33, "192.6", ext=(42, 42))
    s.dim_v(200, 28, 230, "726.3", ext=(222, 222), left=False)
    s.text((18, 228), "开孔：4 × Ø283 喇叭孔　·　Ø297 螺孔圆上 8 × Ø6.5（共 32）　·　2 × Ø10 过线孔（红）",
           2.6, "start", GRAY)
    s.text((18, 235), "端面：上下两端倒 4.51° 斜口（约 1.4mm），保证与顶板/底板贴合。", 2.6, "start", GRAY)

    # ---- 喇叭孔细节 1:2.5 ----
    kk = 2.5
    V2 = View(kk, 1, -1, 330, 170)
    W = V2.p
    s.circle(W(0, 0), (g.SPK_OD + 6) / 2 / kk, 0.3, GRAY, dash="4,2")
    s.circle(W(0, 0), g.SPK_CUT / 2 / kk, 0.5)
    s.circle(W(0, 0), g.SPK_BCD / 2 / kk, 0.25, GRAY, dash="4,1.5")
    for i in range(g.SPK_N):
        a = math.radians(90 + i * 360.0 / g.SPK_N)
        hp = W(g.SPK_BCD / 2 * math.cos(a), g.SPK_BCD / 2 * math.sin(a))
        s.circle(hp, g.SPK_HOLE / 2 / kk + 0.1, 0.35, INK, "#ffffff")
    centre_marks(s, W(0, 0), 180 / kk)
    s.leader(W(-104.9, 104.9), (262, 112), "8 × Ø6.5", 2.5, INK)
    s.leader(W(-70.8, -122.5), (250, 232), "Ø283", 2.8, INK)
    s.leader(W(79.1, 136.9), (362, 96), "Ø316", 2.6, GRAY)
    s.text((330, 88), "喇叭孔详图 1:2.5", 3.2, "middle", INK, "bold")

    notes(s, 248, 26, [
        "• 平板下料 724 × 726.3；装入箱体后因",
        "　4.51° 斜置，垂直方向占高 724。",
        "• 上下端面倒 4.51° 斜口（约 1.4mm），",
        "　否则会顶到顶板 / 底板。",
        "• 螺孔角度务必按到手喇叭实物核对：",
        "　先用纸板做纸样套在喇叭背面比孔位。",
        "• T 型螺母从背面敲入（M5 或 10-32），",
        "　便于反复拆装喇叭。",
        "• 障板与侧板、顶底板接缝必须打胶密封。",
    ], 2.75, 4.4, "加工说明")
    return s



def sheet05():
    k = 4.0
    s = Sheet(420, 297)
    s.frame("网罩框", "05 / 08", "1:4", sub="18mm 桦木多层板 · 撑喇叭网布")
    V = View(k, 1, -1, 45, 205)
    P = V.p
    s.poly([P(0, 0), P(g.GR_W, 0), P(g.GR_W, g.GR_H), P(0, g.GR_H)], LINE)
    for cy in g.SPK_CY:
        for cx in g.SPK_CX:
            u, v = g.uv(cx, cy)
            u -= g.GR_CLEAR
            v -= g.GR_CLEAR
            c = P(u, v)
            s.circle(c, (g.SPK_OD + 6) / 2 / k, 0.5)
            centre_marks(s, c, 168 / k)
    hw, hh = g.GR_W / 2 - 30, g.GR_H / 2 - 30
    for sx in (-hw, 0, hw):
        for sy in (-hh, hh):
            c = P(g.GR_W / 2 + sx, g.GR_H / 2 + sy)
            s.circle(c, g.MAG_D / 2 / k + 0.5, 0.3, BLUE)
            s.dot(c, 0.35, BLUE)
    for sx in (-hw, hw):
        c = P(g.GR_W / 2 + sx, g.GR_H / 2)
        s.circle(c, g.MAG_D / 2 / k + 0.5, 0.3, BLUE)
        s.dot(c, 0.35, BLUE)
    s.text((P(g.GR_W / 2, 0)[0], 213), "网罩框（贴布前）", 3.4, "middle", INK, "bold")
    s.dim_h(P(0, 0)[0], P(g.GR_W, 0)[0], 220, "720", ext=(205, 205))
    s.dim_v(205, 24.4, 232, "722.3", ext=(226, 226), left=False)
    s.dim_h(P(190 - 158, 0)[0], P(190 + 158, 0)[0], 16, "Ø316", ext=(29, 29), size=2.6)

    notes(s, 268, 40, [
        "• 外框 720 × 722.3，比障板四周小 2mm。",
        "• 4 个 Ø316 孔：喇叭法兰 Ø310 从孔中穿出，",
        "　孔边与喇叭留 3mm 间隙，不能接触。",
        "• 8 个 Ø10 磁铁位（蓝圈）：在框**背面**钻",
        "　Ø12 × 深 3.5 浅坑，环氧胶粘 Ø10×3 钕磁铁，",
        "　磁极方向统一；障板正面同位置拧 M4 铁螺丝。",
        "　这样网罩正面无螺丝，喷涂后外观干净。",
        "• 贴布：网布从中心向外拉紧贴在框正面，",
        "　四边回包 15mm，白乳胶/喷胶固定，吹风机收边。",
        "• 布纹方向保持竖直，斜纹会显歪。",
        "• 网罩框外沿做 R3 小圆角，喷同色漆。",
    ], 2.85, 4.6, "加工说明")

    # 正面示意
    V2 = View(8.0, 1, -1, 280, 200)
    Q = V2.p
    s.poly([Q(0, 0), Q(g.GR_W, 0), Q(g.GR_W, g.GR_H), Q(0, g.GR_H)], 0.3, GRAY)
    for cy in g.SPK_CY:
        for cx in g.SPK_CX:
            u, v = g.uv(cx, cy)
            s.circle(Q(u - g.GR_CLEAR, v - g.GR_CLEAR), (g.SPK_OD + 6) / 2 / 8.0, 0.2, GRAY)
    s.text((Q(g.GR_W / 2, 0)[0], 206), "装好后正面示意（网布已绷好）", 2.4, "middle", GRAY)
    return s
def table(s, x, y, cols, rows, widths, rh=8.6, size=2.7, head_fill="#eeeeee"):
    """简易表格：cols=list[str], rows=list[list[str]], widths=list[mm]"""
    xs = [x]
    for w in widths:
        xs.append(xs[-1] + w)
    tw = xs[-1] - x
    n = len(rows) + 1
    s.rect(x, y, tw, rh * n, 0.35, INK, "#ffffff")
    s.rect(x, y, tw, rh, 0.35, INK, head_fill)
    for i in range(1, n):
        s.line((x, y + rh * i), (x + tw, y + rh * i), 0.2, GRAY)
    for xv in xs[1:-1]:
        s.line((xv, y), (xv, y + rh * n), 0.2, GRAY)
    for i, c in enumerate(cols):
        s.text((xs[i] + 1.6, y + rh - 2.6), c, size, "start", INK, "bold")
    for r, row in enumerate(rows):
        yy = y + rh * (r + 1) + rh - 2.6
        for i, cell in enumerate(row):
            s.text((xs[i] + 1.6, yy), cell, size, "start", INK)
    return y + rh * n


def sheet06():
    s = Sheet(420, 297)
    s.frame("下料清单与排板", "06 / 08", "1:14", sub="全部板件尺寸（单位 mm）· 直接发给板材商家")
    cols = ["#", "名称", "数量", "材料", "尺寸 (mm)", "加工备注"]
    widths = [9, 40, 12, 40, 78, 62]
    rows = []
    for i, (n, q, m, sz, note) in enumerate(g.bom()):
        rows.append([str(i + 1), n, str(q), m, sz, note])
    ybot = table(s, 18, 30, cols, rows, widths)

    notes(s, 18, ybot + 8, [
        "净用料约 2.6 m²（含托条 2.7 m²）；因板件多为 724 宽，",
        "单张 1220×2440 排不下，建议买 2 张（第二张余料开托条/做靠模）。",
        "",
        "下单话术（可直接复制给商家）：",
        "“18mm 桦木多层板（E0 级），按尺寸开料，公差 ±1mm，",
        "  侧板 2 件为梯形：760 高，底边 355，顶边 295，前边斜切，”",
        "  其余为矩形，四角切 90°，不要开孔。”",
        "",
        "托条可用边角料自己开：18×18 木条共 6 根（长 688 四根、724 两根）。",
    ], 2.8, 4.6, "说明")

    # ---- 排板 ----
    k = 14.0
    V = View(k, 1, 1, 300, 40)
    P = V.p
    W_, H_ = 1220, 2440
    s.poly([P(0, 0), P(W_, 0), P(W_, H_), P(0, H_)], 0.5)
    pieces = [
        ("后板", 0, 0, 724, 724, "#e8d3b4"),
        ("障板", 0, 724, 724, 1454, "#dcb488"),
        ("网罩框", 0, 1454, 724, 2176, "#e8cdaa"),
        ("侧板", 724, 0, 1079, 760, "#c99a68"),
        ("侧板", 724, 760, 1079, 1520, "#c99a68"),
        ("顶板", 724, 1520, 1019, 2244, "#d3a97a"),
    ]
    for name, a, b, c, d, col in pieces:
        s.poly([P(a, b), P(c, b), P(c, d), P(a, d)], 0.35, INK, col)
        s.text((P((a + c) / 2, (b + d) / 2)[0], P((a + c) / 2, (b + d) / 2)[1] + 1.2),
               name, 2.5, "middle", INK)
    s.text((P(W_ / 2, H_)[0], 217), "第 1 张 1220 × 2440（1:14）", 2.6, "middle", GRAY)
    s.text((292, 224), "第 2 张：底板 724×355 + 6 根托条", 2.5, "start", GRAY)
    s.text((292, 230), "（余料可做靠模/加强条）", 2.5, "start", GRAY)
    return s


def sheet07():
    s = Sheet(420, 297)
    s.frame("接线图与五金清单", "07 / 08", "—", sub="4×12 阻抗与配线 · 五金采购")
    # ---- 喇叭布置 ----
    SP = [(80, 82), (170, 82), (80, 158), (170, 158)]
    R = 24
    for i, (cx, cy) in enumerate(SP):
        s.circle((cx, cy), R, 0.45)
        s.circle((cx, cy), R * 0.55, 0.2, GRAY)
        s.text((cx, cy + 1.2), f"S{i + 1}", 3.4, "middle", INK, "bold")
        s.text((cx + R * 0.72, cy - R * 0.62), "+", 4.0, "middle", RED, "bold")
        s.text((cx + R * 0.72, cy + R * 0.72), "−", 4.0, "middle", BLUE, "bold")
    # 母线
    s.line((70, 46), (196, 46), 0.5, RED)          # A
    s.line((75, 118), (175, 118), 0.5, INK)        # B
    s.line((70, 194), (196, 194), 0.5, BLUE)       # C
    for cx, cy in SP[:2]:
        s.line((cx, cy - R), (cx, 46), 0.4, RED)
        s.line((cx, cy + R), (cx, 118), 0.4, INK)
    for cx, cy in SP[2:]:
        s.line((cx, cy - R), (cx, 118), 0.4, INK)
        s.line((cx, cy + R), (cx, 194), 0.4, BLUE)
    # 插孔
    s.rect(196, 96, 22, 30, 0.45, INK, "#ffffff")
    s.text((207, 108), "JACK", 2.4, "middle", INK, "bold")
    s.text((207, 114), "16Ω", 2.6, "middle", INK)
    s.text((207, 121), "MONO", 2.2, "middle", GRAY)
    s.line((196, 46), (196, 46), 0.4, RED)
    s.line((196, 46), (210, 46), 0.4, RED)
    s.line((210, 46), (210, 96), 0.4, RED)
    s.line((196, 194), (218, 194), 0.4, BLUE)
    s.line((218, 194), (218, 126), 0.4, BLUE)
    s.text((60, 42), "A（+）", 2.8, "end", RED)
    s.text((60, 192), "C（−）", 2.8, "end", BLUE)
    s.text((180, 114), "B 串联节点", 2.6, "start", GRAY)

    notes(s, 20, 208, [
        "4 只 16Ω 喇叭：上排并联=8Ω，下排并联=8Ω，两组串联=16Ω。",
        "4 只 8Ω 喇叭：同样接法得到 8Ω；4 只 4Ω 喇叭得到 4Ω。",
        "★ 相位一致：四只喇叭的 + 端子必须接在同一路（红线统一接 +），",
        "   接反会低频抵消、声音发虚。",
        "立体声改法：上排两只并联接 JACK A（8Ω），下排两只接 JACK B（8Ω）。",
    ], 2.8, 4.6, "接线说明")
    s.text((140, 34), "16Ω 单声道接线（并联-串联）", 3.4, "middle", INK, "bold")

    # ---- 五金表 ----
    cols = ["品名", "数量", "规格 / 建议", "备注"]
    widths = [36, 15, 70, 39]
    rows = [[a, b, c, d] for a, b, c, d in g.hardware()]
    table(s, 230, 40, cols, rows, widths, rh=8.2, size=2.4)
    return s


def _section_faces():
    """纵剖面（x=中线）内的被切构件，返回 (名称, 多边形(z,y))"""
    t, c = g.T, g.CLEAT
    z_bot = g.BAFFLE_END + g.TANA * (t + c)      # 下前托条前面（取靠后值）
    z_top = g.BAFFLE_END + g.TANA * (g.H - t)    # 上前托条前面
    z0 = g.D - t - c                             # 后板托条
    return [
        ("顶板", [(g.zf(g.H - t), g.H - t), (g.D, g.H - t), (g.D, g.H), (g.zf(g.H), g.H)]),
        ("底板", [(0, 0), (g.D, 0), (g.D, t), (0, t)]),
        ("后板", [(g.D - t, t), (g.D, t), (g.D, g.H - t), (g.D - t, g.H - t)]),
        ("障板", [(g.zb(t), t), (g.zb(g.H - t), g.H - t),
                 (g.zb(g.H - t) + t, g.H - t), (g.zb(t) + t, t)]),
        ("网罩框", [(g.zg(t), t), (g.zg(g.H - t), g.H - t),
                  (g.zb(g.H - t), g.H - t), (g.zb(t), t)]),
        ("托条", [(z_bot, t), (z_bot + c, t), (z_bot + c, t + c), (z_bot, t + c)]),
        ("托条", [(z_top, g.H - t - c), (z_top + c, g.H - t - c),
                 (z_top + c, g.H - t), (z_top, g.H - t)]),
        ("托条", [(z0, t), (z0 + c, t), (z0 + c, g.H - t), (z0, g.H - t)]),
    ]



def _detail(s, Vp, rect_model, gap=0.9):
    for name, poly in _section_faces():
        cp = svgtool.clip_poly(poly, rect_model)
        if len(cp) < 3:
            continue
        pts = [Vp(a, b) for a, b in cp]
        s.poly(pts, 0.3, INK, "#ffffff")
        s.hatch(pts, 45, gap, "#b9a893", 0.12)


def mkv(ox, oy, k, x0, y0):
    """局部视图：模型 (x0,y0) 映射到纸面 (ox,oy)，比例 1:k"""
    def p(a, b):
        return (ox + (a - x0) / k, oy - (b - y0) / k)
    return p


def sheet08():
    s = Sheet(420, 297)
    s.frame("纵剖面与节点详图", "08 / 08", "1:6 / 1:2", sub="前框构造 · 包皮走向 · 装配层次")
    # ---- 纵剖面 1:6 ----
    V = View(6.0, 1, -1, 30, 170)
    P = V.p
    for name, poly in _section_faces():
        pts = [P(a, b) for a, b in poly]
        s.poly(pts, 0.35, INK, "#fdf8f1")
        s.hatch(pts, 45, 0.9, "#b9a893", 0.13)
    sy = g.SPK_CY[0]
    s.poly([P(g.zb(sy) - 10, sy - 155), P(g.zb(sy) + 130, sy - 155),
            P(g.zb(sy) + 130, sy + 155), P(g.zb(sy) - 10, sy + 155)],
           0.2, GRAY, dash="2,2")
    s.text((P(g.D / 2, -18)[0], 176), "A-A 纵剖面（1:6）", 3.2, "middle", INK, "bold")
    s.dim_h(P(0, 0)[0], P(g.D, 0)[0], 182, "355", ext=(172, 172))
    s.dim_v(170, 43.3, 24, "760", ext=(30, 30))
    s.circle(P(g.zf(g.H - g.T) - 3, g.H - g.T - 8), 7.0, 0.35, BLUE)
    s.circle(P(g.zf(g.T) + 3, g.T + 8), 7.0, 0.35, BLUE)

    # ---- 详图 A：顶部前角 1:2 ----
    A = mkv(102, 112, 2.0, 0, 600)
    _detail(s, A, (0, 600, 150, 760))
    s.add('<path d="M %.2f,%.2f L %.2f,%.2f L %.2f,%.2f L %.2f,%.2f" fill="none" '
          'stroke="#1b1b1b" stroke-width="0.9" stroke-linejoin="round"/>'
          % (A(148, g.H)[0], A(148, g.H)[1], A(g.zf(g.H), g.H)[0], A(g.zf(g.H), g.H)[1],
             A(g.zf(g.H - g.T), g.H - g.T)[0], A(g.zf(g.H - g.T), g.H - g.T)[1],
             A(g.zf(g.H - g.T) + 18, g.H - g.T)[0], A(g.zf(g.H - g.T) + 18, g.H - g.T)[1]))
    s.text((A(40, 594)[0], 124), "详图 A  顶部前角 1:2", 3.0, "middle", INK, "bold")
    s.leader(A(g.zf(g.H - g.T) + 17, g.H - g.T - 2), (186, 44), "漆膜包到前唇 18", 2.5, INK)
    s.leader(A(g.zg(660) + 9, 660), (186, 70), "网罩框 18", 2.5, GRAY)
    s.leader(A(130, g.H - 4), (186, 30), "顶板 18", 2.5, GRAY)

    # ---- 详图 B：底部前角 1:2 ----
    B = mkv(102, 212, 2.0, 0, 0)
    _detail(s, B, (0, 0, 150, 160))
    s.add('<path d="M %.2f,%.2f L %.2f,%.2f L %.2f,%.2f L %.2f,%.2f" fill="none" '
          'stroke="#1b1b1b" stroke-width="0.9" stroke-linejoin="round"/>'
          % (B(148, 0)[0], B(148, 0)[1], B(g.zf(0), 0)[0], B(g.zf(0), 0)[1],
             B(g.zf(g.T), g.T)[0], B(g.zf(g.T), g.T)[1],
             B(g.zf(g.T) + 18, g.T)[0], B(g.zf(g.T) + 18, g.T)[1]))
    s.text((B(40, -20)[0], 228), "详图 B  底部前角 1:2", 3.0, "middle", INK, "bold")
    s.leader(B(g.zb(g.T) + 34, g.T + 34), (186, 172), "障板 18", 2.5, GRAY)
    s.leader(B(120, 4), (186, 200), "底板 18", 2.5, GRAY)



    notes(s, 224, 40, [
        "装配层次（从外到内）：",
        "　漆膜 → 前唇 18 → 网罩框 18 → 障板 18",
        "",
        "1. 侧板/顶板/底板先用胶 + 4×50 螺丝组箱，",
        "　　量对角线校正，保持 90°（决定是否方正）。",
        "2. 从前方装入障板，四边与侧板内侧、顶底板",
        "　　端面涂胶；内侧沿接缝打一圈密封胶。",
        "3. 从背面把 18×18 托条贴到障板背面并拧紧，",
        "　　这一步把障板“夹死”，消除共振。",
        "4. 粘后板托条，试装后板（螺丝 + 密封条）。",
        "5. 外棱 R6 倒角 → 批灰 → 打磨 → 喷底漆 →",
        "　　喷黑色面漆 2~3 道（详见 09 图）。",
        "　　前唇 18 的凹边一起喷黑，网罩扣上后自然形成阴影线。",
        "6. 装提手、脚轮、插孔板；焊线、装喇叭；",
        "　　最后把绷好布的网罩磁吸上去。",
        "",
        "★ 检查：蒙住喇叭孔推障板不应松动；",
        "　　从插孔往箱内吹气，应基本不漏。",
        "　　（气密 = 低频紧、不发闷）",
    ], 2.75, 4.4, "装配顺序")
    return s



def sheet09():
    s = Sheet(420, 297)
    s.frame("表面工艺与五金布置", "09 / 09", "1:1 / 1:8",
            sub="R6 圆边倒角 · 黑色喷涂 · 提手与脚轮")

    # ---------- (a) 圆角剖面 1:1 ----------
    ex, ey = 92, 78          # 外角点
    R = g.EDGE_R
    s.raw('<path d="M 30,140 L 30,%.1f L %.1f,%.1f A %.1f,%.1f 0 0 1 %.1f,%.1f L 92,140 Z" '
          'fill="#fdf8f1" stroke="%s" stroke-width="0.4"/>'
          % (ey, ex - R, ey, R, R, ex, ey + R, INK))
    s.hatch([(30, 140), (30, ey), (ex - R, ey), (ex, ey + R), (92, 140)], 45, 1.0, "#b9a893", 0.12)
    s.raw('<path d="M 30,%.1f L %.1f,%.1f A %.1f,%.1f 0 0 1 %.1f,%.1f L %.1f,140" fill="none" '
          'stroke="#1b1b1b" stroke-width="1.1" stroke-linejoin="round"/>'
          % (ey - 0.6, ex - R, ey - 0.6, R + 0.6, R + 0.6, ex + 0.6, ey + R, ex + 0.6))
    s.dim_h(30, ex - R, ey - 14, "刨到此处", ext=(ey, ey))
    s.dim_v(ey, 140, 104, "18", ext=(ex, 92), left=False)
    s.leader((ex - R * 0.3, ey + R * 0.3), (58, 52), "R6", 3.4, BLUE)
    s.leader((ex - 2, ey - 1), (34, ey - 26), "漆膜 0.3~0.4", 2.5, GRAY)
    s.text((60, 154), "详图 a  外棱 R6（1:1）", 3.0, "middle", INK, "bold")

    # ---------- (b) 漆层放大 ----------
    bx, by, bw = 115, 30, 86
    layers = [(g.T, "18mm 桦木多层板", "#e8d3b4"),
              (0.4, "原子灰 补平木纹/钉眼", "#cfc6b8"),
              (0.15, "环氧封闭底漆", "#b9b2a6"),
              (0.12, "黑色面漆 第 1 道", "#2b2b2b"),
              (0.12, "黑色面漆 第 2 道", "#141414")]
    y = by
    for th, name, col in layers:
        h = 4.4 if th < 1 else 6.5
        s.rect(bx, y, bw, h, 0.3, INK, col)
        s.text((bx + bw + 3, y + h * 0.5 + 1.0), name, 2.5, "start", INK)
        y += h
    s.text((bx, by - 6), "详图 b  漆层结构（厚度放大，非比例）", 3.0, "start", INK, "bold")

    # ---------- (c) 侧视：提手 ----------
    k = 8.0
    V = View(k, 1, -1, 30, 250)
    P = V.p
    s.poly([P(0, 0), P(g.D, 0), P(g.D, g.H), P(g.SLANT, g.H)], LINE)
    hz0 = g.D / 2 - g.HANDLE_L / 2
    s.rect(P(hz0, g.HANDLE_Y + g.HANDLE_H / 2)[0], P(hz0, g.HANDLE_Y + g.HANDLE_H / 2)[1],
           g.HANDLE_L / k, g.HANDLE_H / k, 0.4, INK, "#eeeeee")
    for zz in (g.D / 2 - 76, g.D / 2 + 76):
        s.circle(P(zz, g.HANDLE_Y), 1.3, 0.35, INK, "#ffffff")
    s.text((P(g.D / 2, 0)[0], 258), "侧视：提手位置（1:8）", 3.0, "middle", INK, "bold")
    s.dim_v(250, P(0, g.HANDLE_Y)[1], 24, "520", ext=(30, 30))
    s.dim_h(P(hz0, 0)[0], P(hz0 + g.HANDLE_L, 0)[0], 264, "180", ext=(254, 254))
    s.leader(P(g.D / 2 + 76, g.HANDLE_Y), (74, 186), "Ø6.5×2 孔距 152", 2.5, GRAY)

    # ---------- (d) 仰视：脚轮 ----------
    V2 = View(k, 1, 1, 200, 168)
    Q = V2.p
    s.poly([Q(g.T, 0), Q(g.W - g.T, 0), Q(g.W - g.T, g.D), Q(g.T, g.D)], LINE)
    for cxx in (g.CASTER_INSET, g.WIN - g.CASTER_INSET):
        for czz in (g.CASTER_INSET, g.D - g.CASTER_INSET):
            s.circle(Q(cxx, czz), g.CASTER_R / k, 0.35, INK, "#eeeeee")
            s.dot(Q(cxx, czz), 0.4)
    s.text((Q(g.WIN / 2, g.D)[0], 218), "仰视：脚轮位置（1:8）", 3.0, "middle", INK, "bold")
    s.dim_h(Q(g.T, 0)[0], Q(g.T + g.CASTER_INSET, 0)[0], 160, "80", ext=(168, 168))
    s.dim_v(168, 168 + g.D / k, 294, "355", ext=(290, 290), left=False)

    notes(s, 248, 26, [
        "圆边倒角（R6）",
        "1. 顺序：组装 → 开孔 → 倒角 → 批灰。倒角放在",
        "　 组装之后，棱边才能一次走通、转角不接刀。",
        "2. 修边机 + R6 圆底刀（或 R6 圆角刨），一次走",
        "　 到底，走慢一点，避免木皮撕裂。",
        "3. 8 个三面交汇的箱角是难点：到角上轻抬收刀，",
        "　 再用砂纸手工过渡，不要硬拐。",
        "4. 前唇（障板凹陷 18mm 处）**不倒角**，保持直角，",
        "　 否则网罩会露出缝隙。",
        "5. 倒完用 180 目轻磨棱边，手感圆润即可。",
        "",
        "喷涂工艺",
        "1. 批灰：原子灰薄刮 2 遍，填平木纹、钉眼、接缝；",
        "　 干透后 180→320 目砂纸磨平，吹净粉尘。",
        "2. 底漆：环氧/硝基封闭底漆 1~2 遍，封住木材吸水，",
        "　 干后 320 目轻磨。",
        "3. 面漆：黑色哑光聚氨酯 2~3 遍，每遍薄喷，",
        "　 间隔 20~30 分钟，最后一道稍湿出膜。",
        "4. 想要 Marshall 那种细砂纹：面漆加 3~5% 哑光粉，",
        "　 或用「喷点漆」远距离点喷。",
        "5. 完全固化 24~48 小时后再装喇叭、拧五金，",
        "　 否则螺丝会把漆面挤裂。",
        "6. 环境 15~30℃、无风无尘；自喷漆要少量多次。",
    ], 2.55, 4.25, "工艺说明")
    return s


def build_all():
    return [sheet01(), sheet02(), sheet03(), sheet04(),
            sheet05(), sheet06(), sheet07(), sheet08(), sheet09()]








