#!/usr/bin/env python3
"""Build the offline interactive CSS course site from docs/course/*.md.

Run from anywhere: python3 course-site/build_site.py
Output: course-site/index.html
"""

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COURSE = ROOT / "docs" / "course"
FIGDIR = COURSE / "figures"
OUT = ROOT / "course-site" / "index.html"

CHAPTERS = [
    ("01-pipeline", "从规则到像素"),
    ("02-selectors", "选择器：如何精准找到元素"),
    ("03-cascade", "谁说了算"),
    ("04-inheritance", "值从哪里来"),
    ("05-box-model", "元素到底占多大"),
    ("06-containing-block", "百分比是谁的百分比"),
    ("07-bfc", "为什么布局会塌"),
    ("08-stacking-context", "谁盖住谁"),
    ("09-typography", "文字如何排版"),
    ("10-color", "颜色如何表达"),
    ("11-background-border", "盒子的表面"),
    ("12-display-overflow", "看见与看不见"),
    ("13-transform", "视觉变形"),
    ("14-animation", "状态的变化"),
    ("15-flex", "一维空间怎么分"),
    ("16-grid", "二维空间怎么画"),
    ("17-container-query", "组件自己的断点"),
    ("18-units", "长度以谁为参照"),
    ("19-responsive", "从视口到组件"),
    ("20-forms", "表单控件与状态"),
    ("21-tables", "表格、列表与计数"),
    ("22-native-ui", "原生弹层"),
    ("23-architecture", "样式架构与设计令牌"),
    ("24-accessibility", "无障碍与兼容性"),
    ("25-rendering", "变化如何发生"),
    ("26-scope-nesting", "嵌套、@scope 与 :has"),
    ("27-modern-features", "新交互平台"),
    ("28-print", "打印与分页媒体"),
    ("29-shapes-mix", "多列、形状与混合"),
    ("30-component-boundary", "交互状态与组件边界"),
    ("appendix-a-cheatsheet", "附录 A · 属性速查表"),
    ("appendix-b-recipes", "附录 B · 常见布局配方"),
    ("appendix-c-exercises", "附录 C · 练习与参考答案"),
    ("appendix-d-pitfalls", "附录 D · 常见问题速查"),
    ("appendix-e-glossary", "附录 E · 术语表"),
]


def inline(text: str) -> str:
    """Render inline Markdown in a controlled subset."""
    s = html.escape(text, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    return s


def slugify(text: str, used: set) -> str:
    base = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", text.lower()).strip("-") or "sec"
    name = base
    n = 2
    while name in used:
        name = f"{base}-{n}"
        n += 1
    used.add(name)
    return name


def render_figure(slug: str, title: str, body: list[str]) -> str:
    svg_path = FIGDIR / f"{slug}.svg"
    if not svg_path.exists():
        return f'<div class="missing">缺少图示：{html.escape(slug)}.svg</div>'
    svg = svg_path.read_text(encoding="utf-8").strip()
    svg = re.sub(r"<\?xml[^>]*\?>", "", svg)
    caption = " ".join(x.strip() for x in body if x.strip())
    return (
        '<figure class="concept-figure">'
        '<div class="figure-canvas">' + svg + "</div>"
        f"<figcaption><strong>{html.escape(title)}</strong>"
        + (f"<span>{inline(caption)}</span>" if caption else "")
        + "</figcaption></figure>"
    )


def render_demo(slug: str, title: str, body: list[str]) -> str:
    demo_path = ROOT / "examples" / "minimal" / f"{slug}.html"
    if not demo_path.exists():
        return f'<div class="missing">缺少 demo：{html.escape(slug)}.html</div>'
    text = " ".join(x.strip() for x in body if x.strip())
    blocks = re.split(r"(?<=[。？！])", text)
    predict = ""
    verify = ""
    for b in blocks:
        if b.strip().startswith("先预测"):
            predict += b.strip()
        elif b.strip().startswith("验证"):
            verify += b.strip()
    rel = f"../examples/minimal/{slug}.html"
    return (
        '<div class="demo-block">'
        f'<div class="demo-head"><span class="demo-tag">动手验证</span><strong>{html.escape(title)}</strong></div>'
        + (f'<p class="predict"><span>先预测</span>{inline(predict[3:])}</p>' if predict else "")
        + f'<iframe src="{rel}" title="{html.escape(title)}" loading="lazy"></iframe>'
        + f'<details class="demo-answer"><summary>揭晓 / 核对</summary><div>{inline(verify) if verify else inline(text)}'
        + '<p class="hint">打开上面的 demo 调节参数，用页面上的实测数值核对你的预测。</p></div></details>'
        + "</div>"
    )


def render_markdown(text: str) -> tuple[str, str, dict[str, str]]:
    lines = text.splitlines()
    out: list[str] = []
    headings: dict[str, str] = {}
    used: set[str] = set()
    title = ""
    lead = ""
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            i += 1
            continue
        if line.startswith("```"):
            lang = line[3:].strip()
            i += 1
            code: list[str] = []
            while i < len(lines) and not lines[i].startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1
            out.append(
                '<div class="code-wrap">'
                + (f'<span class="code-lang">{html.escape(lang)}</span>' if lang else "")
                + "<pre><code>" + html.escape("\n".join(code)) + "</code></pre></div>"
            )
            continue
        if line.startswith(":::figure ") or line.startswith(":::demo "):
            kind, rest = line[3:].strip().split(None, 1)
            slug, _, label = rest.partition("|")
            i += 1
            body: list[str] = []
            while i < len(lines) and lines[i].strip() != ":::":
                body.append(lines[i])
                i += 1
            i += 1
            out.append(render_figure(slug.strip(), label.strip() or slug, body) if kind == "figure"
                       else render_demo(slug.strip(), label.strip() or slug, body))
            continue
        if line.startswith("# "):
            title = line[2:].strip()
            i += 1
            continue
        if line.startswith("## "):
            t = line[3:].strip()
            hid = slugify(t, used)
            headings[hid] = t
            out.append(f'<h2 id="{hid}">{inline(t)}</h2>')
            i += 1
            continue
        if line.startswith("### "):
            out.append(f"<h3>{inline(line[4:].strip())}</h3>")
            i += 1
            continue
        if line.startswith("> "):
            quote: list[str] = []
            while i < len(lines) and lines[i].startswith("> "):
                quote.append(lines[i][2:].strip())
                i += 1
            q = " ".join(quote)
            cls = "model" if q.startswith("一句话模型") else "note"
            out.append(f'<blockquote class="{cls}">{inline(q)}</blockquote>')
            continue
        if line.startswith("| ") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i + 1].strip()):
            rows: list[list[str]] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            head, body_rows = rows[0], rows[2:]
            out.append('<div class="table-wrap"><table><thead><tr>'
                       + "".join(f"<th>{inline(c)}</th>" for c in head)
                       + "</tr></thead><tbody>"
                       + "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body_rows)
                       + "</tbody></table></div>")
            continue
        if re.match(r"^\d+\. ", line):
            items: list[str] = []
            while i < len(lines) and re.match(r"^\d+\. ", lines[i]):
                items.append(re.sub(r"^\d+\. ", "", lines[i]))
                i += 1
            out.append("<ol>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ol>")
            continue
        if line.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(lines[i][2:])
                i += 1
            out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ul>")
            continue
        para: list[str] = []
        while i < len(lines) and lines[i].strip() and not re.match(r"^(```|:::|#|> |\| |\d+\. |- )", lines[i]):
            para.append(lines[i].strip())
            i += 1
        if para:
            joined = " ".join(para)
            if not title and not lead and joined.startswith("> "):
                lead = joined
            out.append(f"<p>{inline(joined)}</p>")
        else:
            i += 1
    return title, "\n".join(out), headings


CSS = """
:root{--paper:#f6f4ec;--card:#fffdf7;--ink:#20281d;--muted:#5d6857;--green:#3f6b2a;--green-soft:#e6efda;--amber:#a7631d;--line:#d8d3c5;--shadow:0 8px 28px rgb(50 58 40 / 7%)}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.75 system-ui,-apple-system,"PingFang SC","Microsoft YaHei",sans-serif}
a{color:var(--green);text-underline-offset:.2em}a:hover{color:var(--amber)}
.layout{display:grid;grid-template-columns:272px minmax(0,1fr);min-height:100vh}
.sidebar{position:sticky;top:0;height:100vh;overflow:auto;padding:28px 20px;background:#eff0e6;border-right:1px solid var(--line)}
.brand{font-size:15px;font-weight:700;line-height:1.4;margin:0 0 4px}.brand small{display:block;color:var(--muted);font-size:12px;font-weight:400}
.nav{display:grid;gap:2px;margin:22px 0}.nav a{display:flex;gap:10px;padding:7px 9px;border-radius:8px;color:var(--ink);text-decoration:none;font-size:13px}
.nav a span{color:var(--muted);font-variant-numeric:tabular-nums}.nav a:hover{background:#e4e8d8}.nav a.active{background:var(--green);color:#fff}.nav a.active span{color:#dceccb}
.side-foot{font-size:12px;color:var(--muted);border-top:1px solid var(--line);padding-top:14px}
main{min-width:0;padding:40px clamp(20px,5vw,72px) 90px}.paper{max-width:880px;margin:0 auto}
.chapter{display:none}.chapter.active{display:block}
.crumb{color:var(--muted);font-size:13px;margin-bottom:6px}h1{font-size:clamp(28px,4vw,42px);line-height:1.2;margin:0 0 20px;letter-spacing:-.02em}
h2{font-size:22px;line-height:1.4;margin:42px 0 12px;padding-bottom:8px;border-bottom:1px solid var(--line)}
h3{font-size:17px;margin:26px 0 8px}p{margin:12px 0}
blockquote{margin:20px 0;padding:14px 18px;border-left:4px solid var(--green);background:var(--green-soft);border-radius:0 10px 10px 0}
blockquote.model{font-size:17px;line-height:1.7}blockquote.note{border-color:var(--amber);background:#f8ecd9}
code{font:.9em ui-monospace,SFMono-Regular,Consolas,monospace;background:#e9eddf;padding:.12em .35em;border-radius:4px}
.code-wrap{position:relative;margin:18px 0}.code-lang{position:absolute;top:6px;right:12px;color:#a9bda3;font:11px ui-monospace,monospace}
pre{margin:0;padding:18px;overflow:auto;border-radius:12px;background:#263021;color:#edf2e5;font:13px/1.7 ui-monospace,SFMono-Regular,Consolas,monospace}
pre code{background:none;padding:0;color:inherit}
ul,ol{padding-left:24px}li{margin:7px 0}
.table-wrap{overflow:auto;margin:18px 0}table{border-collapse:collapse;width:100%;font-size:14px;background:var(--card);border-radius:10px;overflow:hidden}
th,td{padding:10px 12px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}th{background:#e9eddf;font-weight:600}
.concept-figure{margin:26px 0;padding:0;background:var(--card);border:1px solid var(--line);border-radius:14px;overflow:hidden;box-shadow:var(--shadow)}
.figure-canvas{padding:12px;background:#fff}.figure-canvas svg{display:block;width:100%;height:auto}
figcaption{padding:14px 18px;border-top:1px solid var(--line);font-size:14px;color:var(--muted)}figcaption strong{display:block;color:var(--ink);font-size:15px;margin-bottom:4px}
.demo-block{margin:26px 0;border:1px solid var(--line);border-radius:14px;overflow:hidden;background:var(--card);box-shadow:var(--shadow)}
.demo-head{display:flex;gap:10px;align-items:center;padding:14px 18px;background:#eef2e5;font-size:15px}.demo-tag{font-size:11px;letter-spacing:.08em;color:#fff;background:var(--green);padding:3px 7px;border-radius:99px}
.predict{margin:0;padding:12px 18px;font-size:14px;background:#fbf4e4}.predict span{display:inline-block;margin-right:8px;padding:2px 7px;border-radius:99px;background:var(--amber);color:#fff;font-size:11px}
.demo-block iframe{display:block;width:100%;height:620px;border:0;background:#fff}
.demo-answer{padding:12px 18px;font-size:14px;color:var(--muted)}.demo-answer summary{cursor:pointer;color:var(--green);font-weight:600}.demo-answer[open] summary{margin-bottom:8px}.hint{margin-top:10px;font-size:13px}
.missing{padding:16px;background:#fce8e8;border-radius:10px;color:#8b2424}
.pager{display:flex;justify-content:space-between;gap:12px;margin:50px 0 0;padding-top:20px;border-top:1px solid var(--line);font-size:14px}
.pager a{padding:8px 14px;border:1px solid var(--line);border-radius:99px;background:var(--card);text-decoration:none}
.topbar{display:none}
@media(max-width:820px){.layout{display:block}.sidebar{position:static;height:auto;border-right:0;border-bottom:1px solid var(--line)}.nav{grid-auto-flow:column;grid-auto-columns:max-content;overflow:auto;padding-bottom:4px}.side-foot{display:none}main{padding:24px 16px 60px}.demo-block iframe{height:560px}}
@media print{.layout{display:block}.sidebar{display:none}main{padding:0}.chapter{display:block!important;page-break-before:always}.demo-block iframe{height:520px}.pager{display:none}}
"""


def main() -> None:
    chapters_html = []
    nav = []
    for idx, (slug, label) in enumerate(CHAPTERS):
        path = COURSE / f"{slug}.md"
        if not path.exists():
            raise SystemExit(f"missing chapter: {path}")
        title, body, _ = render_markdown(path.read_text(encoding="utf-8"))
        prev = (f'<a href="#{CHAPTERS[idx-1][0]}">← {CHAPTERS[idx-1][1]}</a>' if idx else "<span></span>")
        nxt = (f'<a href="#{CHAPTERS[idx+1][0]}">{CHAPTERS[idx+1][1]} →</a>' if idx + 1 < len(CHAPTERS) else "<span></span>")
        chapters_html.append(
            f'<section class="chapter" id="{slug}" data-index="{idx}">'
            f'<div class="crumb">CSS 概念课 · {idx+1:02d} / {len(CHAPTERS):02d}</div>'
            f"<h1>{html.escape(title)}</h1>{body}"
            f'<div class="pager">{prev}{nxt}</div></section>'
        )
        nav.append(f'<a href="#{slug}" data-target="{slug}"><span>{idx+1:02d}</span>{html.escape(label)}</a>')

    doc = """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CSS 概念课 · 把样式从试出来变成推出来</title>
<link rel="icon" href="data:,">
<style>""" + CSS + """</style></head><body>
<div class="layout"><aside class="sidebar">
<p class="brand">CSS 概念课<small>把样式从「试出来」变成「推出来」</small></p>
<nav class="nav">""" + "".join(nav) + """</nav>
<p class="side-foot">12 篇 · 每篇一张图一个 demo<br>图与示例均可离线使用<br>浏览器打印可导出全书</p>
</aside><main><div class="paper">""" + "".join(chapters_html) + """</div></main></div>
<script>
const links=[...document.querySelectorAll('.nav a')];
const chapters=[...document.querySelectorAll('.chapter')];
function show(id){
  const target=chapters.find(c=>c.id===id)||chapters[0];
  chapters.forEach(c=>c.classList.toggle('active',c===target));
  links.forEach(a=>a.classList.toggle('active',a.dataset.target===target.id));
  history.replaceState(null,'','#'+target.id);
  window.scrollTo({top:0,behavior:'instant'});
}
links.forEach(a=>a.addEventListener('click',e=>{e.preventDefault();show(a.dataset.target)}));
window.addEventListener('hashchange',()=>show(location.hash.slice(1)));
show(location.hash.slice(1));
</script></body></html>"""
    OUT.write_text(doc, encoding="utf-8")
    print(f"wrote {OUT} ({len(doc):,} chars)")


if __name__ == "__main__":
    main()
