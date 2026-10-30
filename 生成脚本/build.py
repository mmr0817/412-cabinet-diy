# -*- coding: utf-8 -*-
"""
build.py —— 一键生成全套成果
  python3 build.py
输出：
  图纸/*.svg、图纸/412箱体全套图纸.pdf
  3D模型/412箱体_3D.html
  数据/*.csv
"""
import csv
import json
import os
import subprocess

import drawings
import geom as g

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DWG = os.path.join(ROOT, "图纸")
MDL = os.path.join(ROOT, "3D模型")
DAT = os.path.join(ROOT, "数据")

NAMES = ["01_总装三视图", "02_侧板", "03_顶板底板后板", "04_喇叭障板",
         "05_网罩框", "06_下料清单与排板", "07_接线图与五金",
         "08_纵剖面与节点详图", "09_表面工艺与五金布置"]

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def ensure_dirs():
    for d in (DWG, MDL, DAT):
        os.makedirs(d, exist_ok=True)


def write_csv(path, header, rows):
    with open(path, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)
    return path


def make_csv():
    write_csv(os.path.join(DAT, "01_下料清单.csv"),
              ["序号", "名称", "数量", "材料", "尺寸(mm)", "加工备注"],
              [[i + 1] + list(r) for i, r in enumerate(g.bom())])
    write_csv(os.path.join(DAT, "02_五金采购清单.csv"),
              ["品名", "数量", "规格/建议", "备注"],
              [list(r) for r in g.hardware()])
    rows = [
        ("外形 宽", f"{g.W:.0f}", "mm"),
        ("外形 高", f"{g.H:.0f}", "mm"),
        ("外形 深(底)", f"{g.D:.0f}", "mm"),
        ("外形 深(顶)", f"{g.DTOP:.0f}", "mm"),
        ("板厚", f"{g.T:.0f}", "mm"),
        ("前脸倾角", f"{g.A_DEG:.2f}", "°"),
        ("内宽 × 内高", f"{g.WIN:.0f} × {g.HIN:.0f}", "mm"),
        ("障板平面尺寸", f"{g.BAFFLE_W:.0f} × {g.BAFFLE_H:.1f}", "mm"),
        ("网罩框", f"{g.GR_W:.0f} × {g.GR_H:.1f}", "mm"),
        ("障板前退(法向)", f"{g.BAFFLE_OFF:.0f}", "mm"),
        ("前唇", f"{g.LIP:.0f}", "mm"),
        ("喇叭中心 X", f"{g.SPK_CX[0]:.0f} / {g.SPK_CX[1]:.0f}", "mm"),
        ("喇叭中心 Y", f"{g.SPK_CY[0]:.0f} / {g.SPK_CY[1]:.0f}", "mm"),
        ("喇叭开孔", f"Ø{g.SPK_CUT:.0f}", "mm"),
        ("喇叭螺孔圆", f"Ø{g.SPK_BCD:.0f} × {g.SPK_N}", "mm"),
        ("喇叭外径", f"Ø{g.SPK_OD:.0f}", "mm"),
    ]
    write_csv(os.path.join(DAT, "03_关键尺寸.csv"), ["项目", "数值", "单位"], rows)
    write_csv(os.path.join(DAT, "04_预算清单.csv"),
              ["项目", "数量", "单价参考(元)", "小计(元)", "备注"],
              [list(r) for r in g.cost()])


def make_previews():
    """生成 GitHub 预览图（PNG）"""
    import render3d
    import svgtool
    img = os.path.join(ROOT, "images")
    os.makedirs(img, exist_ok=True)
    parts = g.build_parts()
    no_cloth = [p for p in parts if p["id"] != "cloth"]
    no_front = [p for p in parts if p["id"] not in ("cloth", "grille", "baffle")]
    jobs = [
        ("preview_01_front", no_cloth, dict(az=160, el=16, cull=True)),
        ("preview_02_finished", parts, dict(az=158, el=13, cull=True)),
        ("preview_03_explode", parts, dict(az=150, el=16, explode=430, cull=False)),
        ("preview_04_inside", no_front, dict(az=165, el=12, cull=False)),
    ]
    if not os.path.exists(CHROME):
        return 0
    n = 0
    for name, ps, kw in jobs:
        s = svgtool.Sheet(200, 200)
        render3d.render(s, ps, (6, 6, 194, 194), **kw)
        svg = "/tmp/_%s.svg" % name
        s.save(svg)
        out = os.path.join(img, name + ".png")
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        "--force-device-scale-factor=2",
                        "--screenshot=" + out, "--window-size=800,800",
                        "file://" + svg], capture_output=True, timeout=120)
        if os.path.exists(out):
            n += 1
    return n


def part_json():
    out = []
    for p in g.build_parts():
        faces = []
        for face in p["faces"]:
            faces.append([[[round(q[0], 1), round(q[1], 1), round(q[2], 1)] for q in ring]
                          for ring in face])
        out.append(dict(id=p["id"], name=p["name"], size=p["size"], color=p["color"],
                        layer=p.get("layer", 0),
                        explode=[round(v, 2) for v in p["explode"]], faces=faces))
    return out


HTML_HEAD = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>412 箱体 3D 模型</title>
<style>
  *{box-sizing:border-box}
  html,body{margin:0;height:100%;overflow:hidden;
    font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;
    background:#efece5;color:#241f18}
  #app{display:flex;height:100%}
  aside{width:268px;flex:0 0 268px;background:#fff;border-right:1px solid #ddd6c9;
    padding:16px 14px;overflow-y:auto}
  h1{font-size:16px;margin:0 0 2px}
  h1 small{font-weight:400;color:#8a7f6d;font-size:11px}
  .hint{font-size:11.5px;color:#8a7f6d;line-height:1.6;margin:6px 0 12px}
  .grp{margin:12px 0 4px;font-size:11px;color:#9a8f7d;letter-spacing:.08em}
  button{font:inherit;font-size:12px;padding:6px 9px;margin:0 4px 6px 0;cursor:pointer;
    border:1px solid #d8d1c3;background:#fbf9f5;border-radius:7px;color:#3a3227}
  button:hover{background:#f2ece0}
  input[type=range]{width:100%;margin:4px 0 8px}
  .item{display:flex;align-items:center;gap:7px;padding:4px 5px;border-radius:6px;font-size:12px}
  .item:hover{background:#f5f0e6}
  .item b{font-weight:600;white-space:nowrap}
  .item i{font-style:normal;color:#9a8f7d;font-size:11px;margin-left:auto;
    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:118px}
  .sw{width:11px;height:11px;border-radius:3px;border:1px solid rgba(0,0,0,.15);flex:0 0 11px}
  main{flex:1;position:relative}
  canvas{width:100%;height:100%;display:block;touch-action:none;cursor:grab}
  canvas:active{cursor:grabbing}
  .foot{position:absolute;left:14px;bottom:12px;font-size:11.5px;color:#8a7f6d;
    background:rgba(255,255,255,.82);padding:5px 9px;border-radius:8px}
  kbd{font:inherit;background:#f2ece0;border:1px solid #d8d1c3;border-radius:4px;padding:0 4px}
</style>
</head>
<body>
<div id="app">
  <aside>
    <h1>412 箱体 <small>3D 结构模型</small></h1>
    <div class="hint">参考 Marshall 1960A · 760×760×355 · 18mm 桦木多层板</div>
    <div class="grp">视图</div>
    <button id="bIso">等轴</button><button id="bFront">正视</button>
    <button id="bSide">侧视</button><button id="bTop">俯视</button>
    <button id="bSpin">自动旋转</button><button id="bDim">尺寸标注</button>
    <div class="grp">分解</div>
    <input id="exp" type="range" min="0" max="100" value="0">
    <div class="grp">显隐</div>
    <button id="bGrille">网罩框</button>
    <button id="bBaffle">障板</button>
    <button id="bSpk">喇叭</button>
    <button id="bCloth">网布</button>
    <div class="grp">零件（悬停高亮）</div>
    <div id="list"></div>
  </aside>
  <main>
    <canvas id="cv"></canvas>
    <div class="foot">拖动旋转 · 滚轮缩放 · 拉「分解」滑杆看内部结构</div>
  </main>
</div>
<script>window.__CAB__ = __DATA__;</script>
<script>__VIEWER__</script>
</body>
</html>
"""


def make_html():
    data = dict(W=g.W, H=g.H, D=g.D, parts=part_json())
    with open(os.path.join(HERE, "viewer.js"), encoding="utf-8") as fh:
        js = fh.read()
    html = HTML_HEAD.replace("__DATA__", json.dumps(data, ensure_ascii=False,
                                                     separators=(",", ":")))
    html = html.replace("__VIEWER__", js)
    path = os.path.join(MDL, "412箱体_3D.html")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    return path


def make_print_shell(svg_paths):
    body = []
    for p in svg_paths:
        with open(p, encoding="utf-8") as fh:
            s = fh.read()
        s = s.split("?>", 1)[-1]
        body.append('<div class="page">' + s + "</div>")
    html = """<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<title>412 箱体图纸 A3</title>
<style>
@page{size:A3 landscape;margin:0}
html,body{margin:0;padding:0;background:#fff}
.page{width:420mm;height:297mm;page-break-after:always;overflow:hidden}
.page:last-child{page-break-after:auto}
svg{display:block}
</style></head><body>""" + "\n".join(body) + "</body></html>"
    path = os.path.join(DWG, "_打印页.html")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    return path


def make_pdf(html_path):
    if not os.path.exists(CHROME):
        return None
    out = os.path.join(DWG, "412箱体全套图纸.pdf")
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
           "--virtual-time-budget=8000", "--print-to-pdf=" + out,
           "file://" + html_path]
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=240)
        return out if os.path.exists(out) else None
    except Exception as e:
        print("PDF 生成失败：", e)
        return None


def main():
    ensure_dirs()
    sheets = drawings.build_all()
    paths = []
    for name, sh in zip(NAMES, sheets):
        p = sh.save(os.path.join(DWG, name + ".svg"))
        paths.append(p)
        print("SVG  %-28s %5.0f KB" % (os.path.basename(p), os.path.getsize(p) / 1024))
    make_csv()
    print("CSV  已生成 4 个")
    print("HTML", os.path.basename(make_html()))
    print("PNG  预览图 %d 张" % make_previews())
    ph = make_print_shell(paths)
    pdf = make_pdf(ph)
    print("PDF ", os.path.basename(pdf) if pdf else "（跳过：未找到 Chrome）")


if __name__ == "__main__":
    main()


