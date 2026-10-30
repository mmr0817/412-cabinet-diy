# -*- coding: utf-8 -*-
"""
geom.py —— 412 箱体参数化几何模型
参考 Marshall 1960A(斜面 4x12) 外形，按 DIY 可施工性重排内部结构。
坐标约定：x 向右(宽)，y 向上(高)，z 向箱内(深)；原点在箱体左下前角。
"""
import math

# ==================== 可调参数 ====================
W = 760.0          # 外形宽度
H = 760.0          # 外形高度
D = 355.0          # 底部（最大）深度
SLANT = 60.0       # 前脸倾斜量：顶面比底面窄 60mm
T = 18.0           # 板材厚度（桦木多层板）
BAFFLE_OFF = 36.0  # 障板前面相对外前脸的水平退让
GR_T = 18.0        # 网罩框厚度
CLEAT = 18.0       # 加强托条截面 18x18
GR_CLEAR = 2.0     # 网罩框四周间隙
SPK_OD = 310.0     # 12 寸喇叭法兰外径
SPK_CUT = 283.0    # 障板开孔直径
SPK_BCD = 297.0    # 安装螺丝圆直径
SPK_HOLE = 6.5     # 螺丝孔直径
SPK_N = 8          # 每只喇叭螺丝数
SPK_DX = 170.0     # 喇叭中心到中线的水平距离
SPK_DY = 170.0     # 喇叭中心到中线的垂直距离

# ===== 表面工艺参数（喷涂方案）=====
EDGE_R = 6.0       # 外露棱边圆角半径（R6；想更柔可用 R8/R10）
PAINT_LAYER = 0.35 # 漆层总厚度（原子灰+底漆+面漆），仅用于示意
CLOTH_T = 1.2      # 网布厚度（3D 示意用）

# ===== 五金参数 =====
HANDLE_L = 180.0   # 表面式提手底板长（沿 z）
HANDLE_H = 60.0    # 提手底板高（沿 y）
HANDLE_Y = 520.0   # 提手中心高度
HANDLE_OUT = 26.0  # 提手凸出侧板的厚度
CASTER_R = 25.0    # 2 寸脚轮半径
CASTER_INSET = 80.0  # 脚轮距边距离
MAG_D = 10.0       # 网罩磁铁直径
MAG_N = 8          # 磁铁数量


# ==================== 派生尺寸 ====================
A = math.atan2(SLANT, H)                # 前脸倾角(弧度)
A_DEG = math.degrees(A)                 # ≈4.515°
COSA, SINA, TANA = math.cos(A), math.sin(A), math.tan(A)
WIN = W - 2 * T                         # 内宽 724
HIN = H - 2 * T                         # 内高 724
DTOP = D - SLANT                        # 顶板深度 295
LIP = BAFFLE_OFF - GR_T                 # 前唇(包边)深度 18
BAFFLE_H = HIN / COSA                   # 障板顺斜面长度 726.3
BAFFLE_W = WIN                          # 障板宽 724
GR_W = BAFFLE_W - 2 * GR_CLEAR          # 网罩框 720
GR_H = BAFFLE_H - 2 * GR_CLEAR          # 网罩框 722.3
SPK_CX = (W / 2 - SPK_DX, W / 2 + SPK_DX)   # 210 / 550
SPK_CY = (H / 2 - SPK_DY, H / 2 + SPK_DY)   # 210 / 550
BAFFLE_END = BAFFLE_OFF + T                 # 障板背面(水平)退让 54
CLEAT_LEN_TB = WIN - 2 * CLEAT              # 上下托条长 688


def zf(y):
    """外前脸(含包皮基准)在高度 y 处的 z"""
    return TANA * y


def zb(y):
    """障板前面在高度 y 处的 z"""
    return BAFFLE_OFF + TANA * y


def zg(y):
    """网罩框前面在高度 y 处的 z"""
    return (BAFFLE_OFF - GR_T) + TANA * y


def uv(x, y):
    """实际空间点 -> 障板/网罩框平面内的展开坐标 (u 沿宽, v 沿斜面)"""
    return (x - T, (y - T) / COSA)


def vol_weight(area_m2, t=T, rho=680.0):
    """板材重量估算 kg（桦木多层板密度约 680kg/m3）"""
    return area_m2 * (t / 1000.0) * rho


# ==================== 3D 实体构建 ====================
def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _mul(a, k):
    return (a[0] * k, a[1] * k, a[2] * k)


def _pt(o, u, v, a, b):
    return _add(o, _add(_mul(u, a), _mul(v, b)))


def _rh(u, v, n):
    """u×v 是否与 n 同向"""
    return _dot(_cross(u, v), n) >= 0


def plate(rings2d, o, u, v, n, th):
    """把若干 2D 环（第 0 环为外轮廓，其余为孔）沿 n 拉伸 th，返回面列表。
    每个面 = [环1, 环2...]；缠绕方向保证法线朝实体外。"""
    if not _rh(u, v, n):
        rings2d = [list(reversed(r)) for r in rings2d]
    faces = []
    front = [[_pt(o, u, v, a, b) for a, b in ring] for ring in rings2d]
    back = [[_add(p, _mul(n, th)) for p in ring] for ring in front]
    faces.append([list(reversed(r)) for r in front])   # 前面 -> 法线 -n
    faces.append([list(r) for r in back])              # 后面 -> 法线 +n
    for ring in rings2d:
        m = len(ring)
        for i in range(m):
            j = (i + 1) % m
            a = _pt(o, u, v, *ring[i])
            b = _pt(o, u, v, *ring[j])
            c = _add(b, _mul(n, th))
            d = _add(a, _mul(n, th))
            faces.append([[a, b, c, d]])
    return faces


def poly_rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def circle_ring(cx, cy, r, n=36, reverse=False):
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    if reverse:
        pts.reverse()
    return pts


def solid_box(x0, y0, z0, x1, y1, z1):
    """轴对齐长方体"""
    return plate([poly_rect(x0, y0, x1, y1)], (0.0, 0.0, z0), (1, 0, 0), (0, 1, 0),
                 (0, 0, 1), z1 - z0)


def cyl(o, u, v, n, r, h0, h1, segs=24, cap0=True, cap1=True):
    """以 o 为圆心、沿 n 从 h0 到 h1 的圆柱"""
    if not _rh(u, v, n):
        u = _mul(u, -1)
    faces = []
    ring0 = [_add(_add(o, _mul(n, h0)),
                  _add(_mul(u, r * math.cos(2 * math.pi * i / segs)),
                       _mul(v, r * math.sin(2 * math.pi * i / segs)))) for i in range(segs)]
    ring1 = [_add(p, _mul(n, h1 - h0)) for p in ring0]
    for i in range(segs):
        j = (i + 1) % segs
        faces.append([[ring0[i], ring0[j], ring1[j], ring1[i]]])
    if cap0:
        faces.append([list(reversed(ring0))])
    if cap1:
        faces.append([ring1])
    return faces


def frustum(o, u, v, n, r0, h0, r1, h1, segs=24, cap0=False, cap1=False):
    if not _rh(u, v, n):
        u = _mul(u, -1)
    faces = []
    a0 = [_add(_add(o, _mul(n, h0)),
               _add(_mul(u, r0 * math.cos(2 * math.pi * i / segs)),
                    _mul(v, r0 * math.sin(2 * math.pi * i / segs)))) for i in range(segs)]
    a1 = [_add(_add(o, _mul(n, h1)),
               _add(_mul(u, r1 * math.cos(2 * math.pi * i / segs)),
                    _mul(v, r1 * math.sin(2 * math.pi * i / segs)))) for i in range(segs)]
    for i in range(segs):
        j = (i + 1) % segs
        faces.append([[a0[i], a0[j], a1[j], a1[i]]])
    if cap0:
        faces.append([list(reversed(a0))])
    if cap1:
        faces.append([a1])
    return faces


def _annulus(o, u, v, n, r_out, r_in, h=0.0, segs=28, reverse=False):
    """平面圆环；reverse=True 时法线朝 -n"""
    if not _rh(u, v, n):
        u = _mul(u, -1)
    ring_o = [_add(_add(o, _mul(n, h)),
                   _add(_mul(u, r_out * math.cos(2 * math.pi * i / segs)),
                        _mul(v, r_out * math.sin(2 * math.pi * i / segs)))) for i in range(segs)]
    ring_i = [_add(_add(o, _mul(n, h)),
                   _add(_mul(u, r_in * math.cos(2 * math.pi * i / segs)),
                        _mul(v, r_in * math.sin(2 * math.pi * i / segs)))) for i in range(segs)]
    if reverse:
        ring_o.reverse()
        ring_i.reverse()
    else:
        ring_i.reverse()
    return [[ring_o, ring_i]]


# ==================== 零件表 ====================
U_X = (1, 0, 0)              # 障板平面内：宽度方向
U_V = (0, COSA, SINA)        # 障板平面内：沿斜面向上
U_N = (0, -SINA, COSA)       # 障板法向（喇叭轴线，指向箱内）
U_Z = (0, 0, 1)              # 板件拉伸方向：沿 z（保证上下端面水平，不顶到顶底板）


def speaker_solid(cx, cy, segs=24):
    """一只 12 寸喇叭（简化、封闭朝外，便于背面剔除）：
    法兰环 + 锥盆浅盘 + 防尘罩 + 磁体（藏在内侧）"""
    u_c, v_c = uv(cx, cy)
    o = _pt((T, T, zb(T)), U_X, U_V, u_c, v_c)
    rc = SPK_CUT / 2 - 2.0          # 锥盆略小于开孔，避免与孔壁共面
    f = []
    f += cyl(o, U_X, U_V, U_N, SPK_OD / 2, -10, 0, segs, cap0=False, cap1=False)
    f += _annulus(o, U_X, U_V, U_N, SPK_OD / 2, SPK_CUT / 2, -10, segs, reverse=True)
    f += _annulus(o, U_X, U_V, U_N, SPK_OD / 2, SPK_CUT / 2, 0, segs)
    f += cyl(o, U_X, U_V, U_N, rc, 0, 8, segs, cap0=True, cap1=False)
    f += annulus_disc(o, U_X, U_V, U_N, rc, 8, segs, reverse=True)
    f += cyl(o, U_X, U_V, U_N, 52, 4, 12, segs, cap0=False, cap1=False)
    f += annulus_disc(o, U_X, U_V, U_N, 52, 12, segs, reverse=True)
    f += cyl(o, U_X, U_V, U_N, 56, 12, 56, segs, cap0=False, cap1=True)
    return f


def annulus_disc(o, u, v, n, r, h, segs=24, reverse=False):
    """实心圆盘"""
    if not _rh(u, v, n):
        u = _mul(u, -1)
    ring = [_add(_add(o, _mul(n, h)),
                 _add(_mul(u, r * math.cos(2 * math.pi * i / segs)),
                      _mul(v, r * math.sin(2 * math.pi * i / segs)))) for i in range(segs)]
    if reverse:
        ring.reverse()
    return [[ring]]



def build_parts():
    P = []

    # --- 左右侧板（梯形）---
    prof = [(0, 0), (D, 0), (D, H), (SLANT, H)]
    P.append(dict(id="side_l", name="侧板 左", color="#c99a68", explode=(-1, 0, 0),
                  mat="18mm 桦木多层板", size="760 × 355(底)/295(顶) 梯形",
                  faces=plate([prof], (0, 0, 0), (0, 0, 1), (0, 1, 0), (1, 0, 0), T)))
    P.append(dict(id="side_r", name="侧板 右", color="#c99a68", explode=(1, 0, 0),
                  mat="18mm 桦木多层板", size="760 × 355(底)/295(顶) 梯形",
                  faces=plate([prof], (W - T, 0, 0), (0, 0, 1), (0, 1, 0), (1, 0, 0), T)))

    # --- 底板 / 顶板 / 后板 ---
    P.append(dict(id="bottom", name="底板", color="#bd8d5c", explode=(0, -1, 0),
                  mat="18mm 桦木多层板", size="724 × 355",
                  faces=plate([poly_rect(T, 0, W - T, D)], (0, 0, 0), (1, 0, 0), (0, 0, 1),
                              (0, 1, 0), T)))
    P.append(dict(id="top", name="顶板", color="#d3a97a", explode=(0, 1, 0),
                  mat="18mm 桦木多层板", size="724 × 295",
                  faces=plate([poly_rect(T, SLANT, W - T, D)], (0, H - T, 0), (1, 0, 0), (0, 0, 1),
                              (0, 1, 0), T)))
    P.append(dict(id="back", name="后板（可拆）", color="#b08252", explode=(0, 0, 1),
                  mat="18mm 桦木多层板", size="724 × 724",
                  faces=plate([poly_rect(T, T, W - T, H - T)], (0, 0, D - T), (1, 0, 0), (0, 1, 0),
                              (0, 0, 1), T)))

    # --- 喇叭障板（斜置，开 4 个 Ø283）---
    rings = [poly_rect(0, 0, BAFFLE_W, BAFFLE_H)]
    for cy in SPK_CY:
        for cx in SPK_CX:
            u_c, v_c = uv(cx, cy)
            rings.append(circle_ring(u_c, v_c, SPK_CUT / 2, 40, reverse=True))
    P.append(dict(id="baffle", name="喇叭障板", color="#dcb488", explode=(0, 0, -1),
                  mat="18mm 桦木多层板", size="724 × 726.3，开 4×Ø283",
                  faces=plate(rings, (T, T, zb(T)), U_X, U_V, U_Z, T)))

    # --- 网罩框（斜置，开 4 个 Ø316）---
    grings = [poly_rect(GR_CLEAR, GR_CLEAR, GR_CLEAR + GR_W, GR_CLEAR + GR_H)]
    for cy in SPK_CY:
        for cx in SPK_CX:
            u_c, v_c = uv(cx, cy)
            grings.append(circle_ring(u_c, v_c, (SPK_OD + 6) / 2, 40, reverse=True))
    P.append(dict(id="grille", name="网罩框", color="#e8cdaa", explode=(0, 0, -1),
                  mat="18mm 桦木多层板", size="720 × 722.3，开 4×Ø316",
                  faces=plate(grings, (T, T, zg(T)), U_X, U_V, U_Z, GR_T)))
    # --- 障板上下托条 18×18×688 ---
    for i, yy in enumerate((T, H - T - CLEAT)):
        zc = BAFFLE_OFF + T + TANA * (yy + CLEAT / 2)
        P.append(dict(id=f"cleat_f{i}", name=f"障板托条 {'下' if i == 0 else '上'}",
                      color="#a87f52", explode=(0, 0, -0.35),
                      mat="18×18 木条（边角料开条）", size=f"18 × 18 × {CLEAT_LEN_TB:.0f}",
                      faces=solid_box(T + CLEAT, yy, zc, W - T - CLEAT, yy + CLEAT, zc + CLEAT)))

    # --- 后板托条 4 根 ---
    z0 = D - T - CLEAT
    for i, xx in enumerate((T, W - T - CLEAT)):
        P.append(dict(id=f"cleat_b{i}", name="后板托条 竖", color="#a87f52",
                      explode=(0, 0, 0.7), mat="18×18 木条", size="18 × 18 × 724",
                      faces=solid_box(xx, T, z0, xx + CLEAT, H - T, z0 + CLEAT)))
    for i, yy in enumerate((T, H - T - CLEAT)):
        P.append(dict(id=f"cleat_c{i}", name="后板托条 横", color="#a87f52",
                      explode=(0, 0, 0.7), mat="18×18 木条",
                      size=f"18 × 18 × {CLEAT_LEN_TB:.0f}",
                      faces=solid_box(T + CLEAT, yy, z0, W - T - CLEAT, yy + CLEAT, z0 + CLEAT)))

    # --- 4 只喇叭 ---
    for i, cy in enumerate(SPK_CY):
        for j, cx in enumerate(SPK_CX):
            P.append(dict(id=f"spk{i}{j}", name="12 寸喇叭（共 4 只）",
                          color="#43474d", explode=(0, 0, -0.15),
                          mat="4×12 喇叭", size="Ø310，障板开孔 Ø283",
                          faces=speaker_solid(cx, cy)))
    # --- 侧装提手（左右各 1）---
    hz0 = g_center_z = (D / 2) - HANDLE_L / 2
    for i, xs in enumerate((0.0, W)):
        sgn = -1 if i == 0 else 1
        P.append(dict(id=f"handle_{'l' if i == 0 else 'r'}", name="提手（表面式）",
                      color="#2b2b2e", explode=(sgn, 0, 0),
                      mat="金属拉手 中心距 152", size=f"{HANDLE_L:.0f} × {HANDLE_H:.0f}",
                      faces=solid_box(min(xs, xs + sgn * HANDLE_OUT * 0.25),
                                      HANDLE_Y - HANDLE_H / 2, hz0,
                                      max(xs, xs + sgn * HANDLE_OUT * 0.25),
                                      HANDLE_Y + HANDLE_H / 2, hz0 + HANDLE_L)
                      + solid_box(min(xs, xs + sgn * HANDLE_OUT), HANDLE_Y - 18, hz0 + 20,
                                  max(xs, xs + sgn * HANDLE_OUT), HANDLE_Y + 18,
                                  hz0 + HANDLE_L - 20)))

    # --- 脚轮 ×4 ---
    for i, cx in enumerate((CASTER_INSET, W - CASTER_INSET)):
        for j, cz in enumerate((CASTER_INSET, D - CASTER_INSET)):
            f = solid_box(cx - 20, -9, cz - 20, cx + 20, 0, cz + 20)
            f += cyl((cx, -30, cz - 12), (1, 0, 0), (0, 1, 0), (0, 0, 1),
                     CASTER_R, 0, 24, 20, cap0=True, cap1=True)
            P.append(dict(id=f"wheel{i}{j}", name="脚轮 2 寸（2 万向 + 2 定向）",
                          color="#1f1f22", explode=(0, -1, 0),
                          mat="2 寸脚轮 M8", size="Ø50",
                          faces=f))

    # --- 网布（示意，可显隐）---
    P.append(dict(id="cloth", name="喇叭网布（可拆网罩）", color="#26262a",
                  explode=(0, 0, -1.25), mat="黑白编织网布", size="716 × 718",
                  layer=10,
                  faces=plate([poly_rect(2, 2, 2 + 716, 2 + 718)],
                              (T, T, zg(T) - CLOTH_T), U_X, U_V, U_Z, CLOTH_T)))
    return P


def bom():
    """下料清单（发给板材商家）"""
    return [
        ("侧板", 2, "18mm 桦木多层板", f"{H:.0f} × {D:.0f}（底）/ {DTOP:.0f}（顶）梯形",
         f"前边斜切 {A_DEG:.2f}°"),
        ("顶板", 1, "18mm 桦木多层板", f"{WIN:.0f} × {DTOP:.0f}", "前口可倒 1.4mm 斜口"),
        ("底板", 1, "18mm 桦木多层板", f"{WIN:.0f} × {D:.0f}", ""),
        ("后板", 1, "18mm 桦木多层板", f"{WIN:.0f} × {WIN:.0f}", "开插孔板孔"),
        ("喇叭障板", 1, "18mm 桦木多层板", f"{BAFFLE_W:.0f} × {BAFFLE_H:.1f}",
         "自开 4×Ø283 + 32×Ø6.5 + 2×Ø10"),
        ("网罩框", 1, "18mm 桦木多层板", f"{GR_W:.0f} × {GR_H:.1f}", "自开 4×Ø316"),
        ("障板托条", 2, "18mm 边角料开条", f"{CLEAT:.0f} × {CLEAT:.0f} × {CLEAT_LEN_TB:.0f}", ""),
        ("后板托条", 2, "18mm 边角料开条", f"{CLEAT:.0f} × {CLEAT:.0f} × {WIN:.0f}", "竖"),
        ("后板托条", 2, "18mm 边角料开条", f"{CLEAT:.0f} × {CLEAT:.0f} × {CLEAT_LEN_TB:.0f}", "横"),
    ]


def cost():
    """整箱预算（不含喇叭），单位：元（2025 年国内参考价）"""
    return [
        ("18mm 桦木多层板 1220×2440", "2 张", "260~320/张", "520~640",
         "开料后余料可开托条"),
        ("板材开料 + 侧板斜切", "1 单", "50~80", "50~80", "拼多多/本地加工店"),
        ("原子灰 + 砂纸（80/180/320/600）", "1 套", "40", "40", "批灰用"),
        ("环氧底漆 / 封闭底漆", "1 kg", "40", "40", "防吸水、增加附着力"),
        ("黑色纹理音箱漆（面漆）", "1~1.5 kg", "60~110", "60~110",
         "双组份聚氨酯最佳；自喷漆约 8 罐"),
        ("哑光罩光漆（可选）", "0.5 kg", "30", "30", "耐擦洗"),
        ("提手（中心距 152）", "2 个", "20/个", "40", ""),
        ("2 寸脚轮（2 万向 + 2 定向）", "4 个", "15/个", "60", "M8 螺纹"),
        ("M8 T 型螺母 + M5 T 母", "4 + 32", "—", "35", ""),
        ("木螺丝 4×35 / 4×50", "各 1 盒", "—", "35", ""),
        ("白乳胶 + 密封胶", "各 1", "—", "40", ""),
        ("喇叭网布（黑白编织）", "1×1 m", "40", "40", ""),
        ("钕磁铁 Ø10×3 + 铁片", "8 套", "—", "25", "网罩磁吸"),
        ("后置插孔板 + 喇叭线", "1 套", "—", "45", ""),
        ("包角（可选，R6 圆角专用）", "8 个", "—", "40", "不装也好看"),
    ]


def hardware():
    """五金 / 辅料清单"""
    return [
        ("喇叭", "4 只", "12 寸 8Ω 或 16Ω，建议四只同型号", "决定总阻抗"),
        ("喇叭螺丝 + T 母", "32 套", "M5×25 内六角 + M5 T 型螺母", "按实物孔距核孔位"),
        ("木螺丝", "约 130 颗", "4×35 沉头；4×50 装箱用", ""),
        ("白乳胶", "1 kg", "组装用", "不要用 502"),
        ("密封胶", "1 支", "中性硅酮 / 聚氨酯", "障板后板打胶，气密关键"),
        ("原子灰 + 砂纸", "1 套", "80/180/320/600 目", "批灰打磨"),
        ("底漆", "1 kg", "环氧/硝基封闭底漆", "封住木纹吸水"),
        ("黑色纹理音箱漆", "1~1.5 kg", "双组份聚氨酯哑光黑（喷枪）", "也可 8 罐哑光自喷漆"),
        ("喇叭网布", "1.0 × 1.0 m", "Marshall 黑白编织网布", "留 15cm 余量"),
        ("网罩磁铁", "8 套", "Ø10×3 钕磁铁 + M4 铁螺丝", "网罩可拆无螺丝"),
        ("提手", "2 个", "表面式金属拉手，中心距 152", "侧装"),
        ("脚轮", "4 个", "2 寸，2 万向 + 2 定向，M8 螺纹", "配 M8 T 母"),
        ("插孔板", "1 套", "后置双 1/4\" 插孔板", "16Ω 单声道"),
        ("喇叭线", "2 m", "2×0.75mm² 或 18AWG", ""),
        ("包角", "选配", "R6 圆角专用包角 8 个", "圆角后普通包角不合"),
        ("吸音棉", "选配", "10mm 聚酯棉，贴后板内侧", "不要塞满"),
    ]


