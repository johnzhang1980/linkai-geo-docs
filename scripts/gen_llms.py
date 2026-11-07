#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_llms.py — MkDocs 构建后处理：为 AI 抓取生成 llms.txt / llms-full.txt 与逐页 Markdown 副本。

用法（在站点工程根目录执行，必须先 mkdocs build）：
    python3 scripts/gen_llms.py
    python3 scripts/gen_llms.py --site-url https://docs.example.com/
    python3 scripts/gen_llms.py --site-dir site --docs-dir docs --check

产出：
    site/llms.txt                     站点结构化索引（llms.txt 约定格式）
    site/llms-full.txt                全部页面正文合并（供一次性抓取）
    site/sitemap.xml                 站点地图（不依赖第三方 sitemap 插件）
    site/<page>.md                    每个页面同名 Markdown 副本
    site/<dir>/index.md               目录式 URL 页面在自身路径下的副本（/dir/index.md 亦可直取）

设计约束：
    - 仅依赖标准库，不引入 PyYAML；
    - 页面顺序与标题取自 mkdocs.yml 的 nav，缺失时回退到 docs 目录扫描；
    - 幂等：重复执行只覆盖生成物，不改动 docs 源文件。
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# 人工撰写的页面摘要（优先于自动抽取，保证 llms.txt 的条目可读、可用于 AI 定位）
DESCRIPTION_OVERRIDES = {
    "index.md": "面向 AI 从业者与企业数字化转型决策者的公开文档站：Token 计价与成本口径、"
                "GEO 实践方法、开源价格数据三部分，首屏提供 Link AI Token 服务试用入口。",
    "token-pricing.md": "按开源仓 price_table 呈现 Claude 与 DeepSeek 的输入/输出单价，"
                        "给出输入、输出、缓存四段成本公式与四个降本杠杆，每项价格标注来源与数据日期。",
    "geo-practice.md": "GEO（生成式引擎优化）的目标是被引用而非排名：发现、抽取、判用、引用四段链路，"
                       "可抽取的内容结构、站点侧必备技术项与三层效果度量方法。",
    "open-data.md": "价格数据全部开源：字段含义、null 值纪律、引用格式，以及把价格数据接入"
                    "内部成本模型的五步维护流程。",
}

YML_NAV_RE = re.compile(r"^\s*-\s*(?P<title>.+?):\s*(?P<path>[^\s#]+\.md)\s*$")
YML_SITE_URL_RE = re.compile(r"^site_url:\s*(?P<url>[^\s#]+)\s*$", re.MULTILINE)
YML_SITE_NAME_RE = re.compile(r"^site_name:\s*(?P<name>[^\n#]+)$", re.MULTILINE)
YML_SITE_DESC_RE = re.compile(r"^site_description:\s*(?P<desc>[^\n]+)$", re.MULTILINE)
YML_DOCS_DIR_RE = re.compile(r"^docs_dir:\s*(?P<d>[^\s#]+)\s*$", re.MULTILINE)
YML_SITE_DIR_RE = re.compile(r"^site_dir:\s*(?P<d>[^\s#]+)\s*$", re.MULTILINE)
H1_RE = re.compile(r"^#\s+(?P<h1>.+?)\s*$", re.MULTILINE)
LIST_RE = re.compile(r"^(?:[-*+]\s|\d+[.)]\s)")


def strip_md(text: str) -> str:
    """粗粒度去掉常见 Markdown 标记，用于生成摘要行。"""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[`*_>#]+", "", text)
    return re.sub(r"\s+", " ", text).strip()


def parse_config(config_path: Path) -> dict:
    meta: dict = {"site_url": "", "site_name": "", "site_description": "",
                  "docs_dir": "docs", "site_dir": "site", "nav": []}
    if not config_path.exists():
        print(f"[warn] 未找到 {config_path}，使用默认值")
        return meta
    raw = config_path.read_text(encoding="utf-8")

    for key, rx in (("site_url", YML_SITE_URL_RE), ("site_name", YML_SITE_NAME_RE),
                    ("site_description", YML_SITE_DESC_RE), ("docs_dir", YML_DOCS_DIR_RE),
                    ("site_dir", YML_SITE_DIR_RE)):
        m = rx.search(raw)
        if m:
            meta[key] = m.group(list(m.groupdict())[0]).strip().strip('"\'')

    nav_lines = [ln for ln in raw.splitlines() if YML_NAV_RE.match(ln)]
    for ln in nav_lines:
        m = YML_NAV_RE.match(ln)
        title = m.group("title").strip().strip('"\'')
        path = m.group("path").strip().strip('"\'')
        if not title.startswith("#"):
            meta["nav"].append((title, path))
    return meta


def first_paragraph(md_text: str, fallback: str = "") -> str:
    """取正文中第一段「适合做摘要」的文字：跳过标题、表格、引用块、代码块与引导句。"""
    blocks: list[str] = []
    is_list: list[bool] = []
    buf: list[str] = []
    in_fence = False
    for ln in md_text.splitlines():
        s = ln.strip()
        if s.startswith("```"):
            in_fence = not in_fence
            if buf:
                blocks.append(" ".join(buf)); is_list.append(False); buf = []
            continue
        if in_fence:
            continue
        if not s or s.startswith(("#", "|", ">", "<", "---", "!!!")):
            if buf:
                blocks.append(" ".join(buf)); is_list.append(False); buf = []
            continue
        if LIST_RE.match(s):
            if buf:
                blocks.append(" ".join(buf)); is_list.append(False); buf = []
            blocks.append(s); is_list.append(True)
            continue
        buf.append(s)
    if buf:
        blocks.append(" ".join(buf)); is_list.append(False)

    def accept(text: str) -> bool:
        if len(text) < 24:
            return False
        if text.endswith(("：", ":")) and len(text) < 60:
            return False
        return True

    # 第一轮只看普通段落（列表项常是半句话，不适合做摘要）
    for i, block in enumerate(blocks):
        if is_list[i]:
            continue
        text = strip_md(block)
        if accept(text):
            return text[:180]
    for block in blocks:
        text = strip_md(block)
        if accept(text):
            return text[:180]
    for block in blocks:
        text = strip_md(block)
        if len(text) >= 12:
            return text[:180]
    return fallback



def page_title(md_text: str, fallback: str) -> str:
    m = H1_RE.search(md_text)
    return strip_md(m.group("h1")) if m else fallback


def collect_pages(docs_dir: Path, nav: list[tuple[str, str]]) -> list[tuple[str, str, Path]]:
    pages: list[tuple[str, str, Path]] = []
    used: set[Path] = set()
    for title, rel in nav:
        p = docs_dir / rel
        if p.exists():
            pages.append((title, rel, p))
            used.add(p)
        else:
            print(f"[warn] nav 指向的文件不存在，已跳过：{rel}")
    # 补充 nav 之外的真实页面，保证不漏抓
    for p in sorted(docs_dir.rglob("*.md")):
        if p not in used:
            pages.append((p.stem, p.relative_to(docs_dir).as_posix(), p))
    return pages


def write_md_copies(site_dir: Path, rel: str, content: str) -> list[str]:
    """为页面生成 Markdown 副本，返回生成后的可访问相对路径列表。"""
    written: list[str] = []
    rel_path = Path(rel)
    stem = rel_path.stem

    # 1) 平铺副本：/token-pricing.md
    flat = site_dir / (stem + ".md")
    flat.parent.mkdir(parents=True, exist_ok=True)
    flat.write_text(content, encoding="utf-8")
    written.append(flat.relative_to(site_dir).as_posix())

    # 2) 目录式副本：/token-pricing/index.md（与页面 URL 路径对齐）
    if stem != "index":
        nested = site_dir / rel_path.parent / stem / "index.md"
    else:
        nested = site_dir / rel_path.parent / "index.md"
    nested.parent.mkdir(parents=True, exist_ok=True)
    nested.write_text(content, encoding="utf-8")
    rel_nested = nested.relative_to(site_dir).as_posix()
    if rel_nested not in written:
        written.append(rel_nested)
    return written


def page_url(base: str, rel: str) -> str:
    """把站点内相对路径映射为 use_directory_urls 下的页面 URL。"""
    rel = rel.replace("\\", "/")
    if rel.endswith("index.md"):
        return base + rel[: -len("index.md")]
    return base + rel[: -len(".md")] + "/"


def build_sitemap(pages: list[tuple[str, str, Path]], base: str, site_dir: Path) -> Path:
    """生成 sitemap.xml：与 llms.txt 共用同一份页面清单，lastmod 取源文件修改日期。"""
    from xml.sax.saxutils import escape

    rows: list[str] = []
    for nav_title, rel, src in pages:
        loc = escape(page_url(base, rel))
        try:
            mtime = datetime.fromtimestamp(src.stat().st_mtime, tz=timezone.utc)
            lastmod = mtime.strftime("%Y-%m-%d")
        except OSError:
            lastmod = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        priority = "1.0" if rel.endswith("index.md") else "0.8"
        rows.append(
            "  <url>\n"
            f"    <loc>{loc}</loc>\n"
            f"    <lastmod>{lastmod}</lastmod>\n"
            "    <changefreq>weekly</changefreq>\n"
            f"    <priority>{priority}</priority>\n"
            "  </url>"
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(rows)
        + "\n</urlset>\n"
    )
    out = site_dir / "sitemap.xml"
    out.write_text(xml, encoding="utf-8")
    # 同时写 gzip 版，避免与构建过程中生成的 sitemap.xml.gz 不一致
    import gzip
    with gzip.open(site_dir / "sitemap.xml.gz", "wb") as fh:
        fh.write(xml.encode("utf-8"))
    return out


def build(site_url: str, site_name: str, site_desc: str,
          pages: list[tuple[str, str, Path]], site_dir: Path) -> tuple[int, int]:
    base = site_url if site_url.endswith("/") else site_url + "/"
    index_items: list[tuple[str, str, str]] = []  # (title, url, desc)
    full_parts: list[str] = []

    for nav_title, rel, src in pages:
        content = src.read_text(encoding="utf-8")
        title = page_title(content, nav_title)
        override = DESCRIPTION_OVERRIDES.get(rel.replace("\\", "/"))
        desc = override or first_paragraph(content, site_desc or nav_title)
        copies = write_md_copies(site_dir, rel, content)
        # 主链接指向与该页面 URL 路径对齐的 Markdown 副本
        primary = next((c for c in copies if c.endswith("/index.md")), copies[0])
        index_items.append((title, base + primary, desc))
        full_parts.append(
            f"\n\n<!-- ===== {title} | {base + primary} ===== -->\n\n{content.strip()}\n"
        )

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    llms = [f"# {site_name}", f"> {site_desc}",
            "> 本文件为 AI 抓取索引：每个条目指向该页面的 Markdown 原文副本，"
            "内容与站点页面一致。", "",
            f"站点首页: {base}", f"生成日期(UTC): {stamp}", "", "## 页面", ""]
    for title, url, desc in index_items:
        line = f"- [{title}]({url})"
        if desc:
            line += f": {desc}"
        llms.append(line)
    llms.append("")
    (site_dir / "llms.txt").write_text("\n".join(llms), encoding="utf-8")

    header = [
        f"# {site_name} — 全文合并版",
        "",
        f"> {site_desc}",
        f"> 站点: {base}",
        f"> 生成日期(UTC): {stamp}",
        "> 本文件拼接了全部页面的 Markdown 原文，供一次性抓取；单页请取 llms.txt 中的链接。",
    ]
    (site_dir / "llms-full.txt").write_text("\n".join(header) + "".join(full_parts),
                                           encoding="utf-8")
    build_sitemap(pages, base, site_dir)
    return len(index_items), len(index_items)


def main() -> int:
    ap = argparse.ArgumentParser(description="生成 llms.txt / llms-full.txt 与逐页 Markdown 副本")
    ap.add_argument("--config", default="mkdocs.yml", help="配置文件路径，默认 mkdocs.yml")
    ap.add_argument("--docs-dir", default=None, help="源目录，默认取配置中的 docs_dir")
    ap.add_argument("--site-dir", default=None, help="构建输出目录，默认取配置中的 site_dir")
    ap.add_argument("--site-url", default=None, help="覆盖配置中的 site_url")
    ap.add_argument("--check", action="store_true", help="仅校验产物是否存在，不重新生成")
    args = ap.parse_args()

    config_path = Path(args.config)
    meta = parse_config(config_path)
    root = config_path.parent if config_path.parent.name else Path(".")
    docs_dir = Path(args.docs_dir or meta["docs_dir"])
    site_dir = Path(args.site_dir or meta["site_dir"])
    if not docs_dir.is_absolute():
        docs_dir = root / docs_dir
    if not site_dir.is_absolute():
        site_dir = root / site_dir
    site_url = args.site_url or meta["site_url"] or "http://localhost:8000/"

    if not docs_dir.is_dir():
        print(f"[error] 源目录不存在：{docs_dir}", file=sys.stderr)
        return 2
    if not site_dir.is_dir():
        print(f"[error] 构建目录不存在：{site_dir}，请先执行 mkdocs build", file=sys.stderr)
        return 2

    pages = collect_pages(docs_dir, meta["nav"])

    if args.check:
        missing = [n for n in ("llms.txt", "llms-full.txt", "sitemap.xml")
                   if not (site_dir / n).exists()]
        md_copies = list(site_dir.rglob("*.md"))
        print(f"页面源文件: {len(pages)}")
        print(f"Markdown 副本: {len(md_copies)}")
        print(f"缺失产物: {missing or '无'}")
        return 1 if missing else 0

    n_pages, _ = build(site_url, meta["site_name"] or "Docs",
                       meta["site_description"] or "", pages, site_dir)
    print(f"[ok] 页面 {n_pages} 个 | site_url={site_url}")
    print(f"[ok] 已生成 {site_dir / 'llms.txt'}")
    print(f"[ok] 已生成 {site_dir / 'llms-full.txt'}")
    print(f"[ok] 已生成 {site_dir / 'sitemap.xml'}")
    print(f"[ok] 已生成每页 Markdown 副本（平铺 + 目录式两份）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
