#!/usr/bin/env python3
"""Import Web Security chapters verbatim from docs.huynhthientung.com."""
from __future__ import annotations

import html as htmlmod
import json
import re
import time
import urllib.request
from pathlib import Path
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1] / "public" / "blog" / "web-security"
CACHE = Path("/tmp/ws-src")
ASSET = "https://docs.huynhthientung.com"

# local slug -> (crumb, source path)
PAGES: list[tuple[str, str, str]] = [
    ("overview", "Overview", "/web-security/intro"),
    ("01-gioi-thieu", "01. Giới thiệu", "/web-security/part1-fundamentals/01-intro"),
    ("02-http", "02. HTTP", "/web-security/part1-fundamentals/02-http"),
    ("03-burp", "03. Burp Suite", "/web-security/part1-fundamentals/03-burp-suite"),
    ("04", "04. Authentication", "/web-security/part2-auth/04-authentication"),
    ("05", "05. Session", "/web-security/part2-auth/05-session-management"),
    ("06", "06. Access Control", "/web-security/part2-auth/06-access-control"),
    ("07", "07. OAuth", "/web-security/part2-auth/07-oauth"),
    ("08", "08. JWT", "/web-security/part2-auth/08-jwt"),
    ("09", "09. CORS", "/web-security/part3-client/09-cors"),
    ("10", "10. CSRF", "/web-security/part3-client/10-csrf"),
    ("11", "11. XSS", "/web-security/part3-client/11-xss"),
    ("22", "22. Clickjacking", "/web-security/part3-client/22-clickjacking"),
    ("12", "12. SQLi", "/web-security/part4-injection/12-sql-injection"),
    ("13", "13. NoSQLi", "/web-security/part4-injection/13-nosql-injection"),
    ("14", "14. Command Injection", "/web-security/part4-injection/14-command-injection"),
    ("16", "16. XXE", "/web-security/part4-injection/16-xxe"),
    ("25", "25. SSTI", "/web-security/part4-injection/25-ssti"),
    ("15", "15. SSRF", "/web-security/part5-server/15-ssrf"),
    ("17", "17. File Upload", "/web-security/part5-server/17-file-upload"),
    ("18", "18. Path Traversal", "/web-security/part5-server/18-path-traversal"),
    ("19", "19. Open Redirect", "/web-security/part5-server/19-open-redirect"),
    ("20", "20. Race Condition", "/web-security/part5-server/20-race-condition"),
    ("21", "21. Business Logic", "/web-security/part5-server/21-business-logic"),
    ("26", "26. Deserialization", "/web-security/part5-server/26-deserialization"),
    ("23", "23. Cache Poisoning", "/web-security/part6-infra/23-cache-poisoning"),
    ("24", "24. HTTP Smuggling", "/web-security/part6-infra/24-http-smuggling"),
    ("27", "27. GraphQL", "/web-security/part7-api/27-graphql"),
    ("28", "28. API Security", "/web-security/part7-api/28-api-security"),
    ("29", "29. Kubernetes", "/web-security/part8-devops/29-kubernetes"),
    ("30", "30. CI/CD", "/web-security/part8-devops/30-cicd"),
    ("31", "31. Secrets", "/web-security/part8-devops/31-secrets"),
    ("32", "32. Cloud", "/web-security/part8-devops/32-cloud"),
    ("33", "33. Logging", "/web-security/part8-devops/33-logging"),
    ("34", "34. Incident Response", "/web-security/part8-devops/34-incident-response"),
    ("35", "35. Checklist", "/web-security/part8-devops/35-checklist"),
    ("appendix", "Appendix", "/web-security/appendix/30-day-roadmap"),
]

# Source URL last segment -> local slug (for rewriting in-page links)
SRC_TO_LOCAL: dict[str, str] = {}
for slug, _crumb, path in PAGES:
    SRC_TO_LOCAL[path.rstrip("/")] = slug
    SRC_TO_LOCAL[path.split("/")[-1]] = slug

NAV = [(slug, crumb) for slug, crumb, _ in PAGES]


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; docs-import/1.0)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def extract_markdown(html: str) -> str:
    m = re.search(
        r'<div class="theme-doc-markdown markdown"[^>]*>(.*?)</div>\s*(?:<nav class="pagination-nav"|<footer )',
        html,
        re.S,
    )
    if not m:
        raise ValueError("markdown body not found")
    return m.group(1)


def flatten_code_blocks(body: str) -> str:
    def one(m: re.Match) -> str:
        block = m.group(0)
        lang_m = re.search(r"language-([a-zA-Z0-9_+-]+)", block)
        lang = lang_m.group(1) if lang_m else ""
        pre_m = re.search(r"<pre[^>]*>(.*?)</pre>", block, re.S)
        inner = pre_m.group(1) if pre_m else block
        inner = inner.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
        inner = re.sub(r"</span>", "", inner)
        inner = re.sub(r"<span[^>]*>", "", inner)
        inner = re.sub(r"<code[^>]*>", "", inner)
        inner = inner.replace("</code>", "")
        text = htmlmod.unescape(re.sub(r"<[^>]+>", "", inner))
        text = text.replace("\xa0", " ").rstrip() + "\n"
        cls = f' class="language-{lang}"' if lang else ""
        return f"<pre><code{cls}>{htmlmod.escape(text)}</code></pre>"

    return re.sub(
        r'<div class="language-[^"]*codeBlockContainer[^"]*"[\s\S]*?</div>\s*</div>',
        one,
        body,
    )


def clean(body: str, slug: str) -> str:
    body = re.sub(r'<a\b[^>]*class="hash-link"[^>]*>.*?</a>', "", body)
    body = re.sub(r' translate="no"', "", body)
    body = body.replace("<!-- -->", "")
    body = re.sub(r' class="anchor[^"]*"', "", body)
    body = re.sub(r' class=""', "", body)
    body = flatten_code_blocks(body)
    body = re.sub(r'src="(/[^"]+)"', rf'src="{ASSET}\1"', body)
    nested = slug != "overview"

    def rel(m: re.Match) -> str:
        path = m.group(1).split("#")[0].rstrip("/")
        frag = ""
        if "#" in m.group(1):
            frag = "#" + m.group(1).split("#", 1)[1]
        local = SRC_TO_LOCAL.get(path) or SRC_TO_LOCAL.get(path.split("/")[-1])
        if not local:
            return f'href="{ASSET}{path}{frag}"'
        if local == "overview":
            href = "./" if not nested else "../"
        else:
            href = f"{local}/" if not nested else f"../{local}/"
        return f'href="{href}{frag}"'

    body = re.sub(r'href="(/web-security/[^"]+)"', rel, body)
    return body


def toc(body: str) -> str:
    items = []
    for m in re.finditer(r"<h([23])[^>]*id=\"([^\"]+)\"[^>]*>(.*?)</h\1>", body, re.S):
        depth, hid, title = m.group(1), m.group(2), re.sub("<[^>]+>", "", m.group(3)).strip()
        title = htmlmod.unescape(title).replace("\u200b", "").strip()
        if not title:
            continue
        cls = ' class="depth-3"' if depth == "3" else ""
        items.append(f'        <a{cls} href="#{hid}">{htmlmod.escape(title)}</a>')
    return "\n".join(items) if items else '        <a href="#top">On this page</a>'


def wrap(slug: str, crumb: str, title: str, body: str) -> str:
    nested = slug != "overview"
    home = "../../../" if nested else "../../"
    ids = [x[0] for x in NAV]
    i = ids.index(slug)

    def href(other: str) -> str:
        if other == "overview":
            return "../" if nested else "./"
        if not nested:
            return f"{other}/"
        return f"../{other}/"

    prev = NAV[i - 1] if i else None
    nxt = NAV[i + 1] if i < len(NAV) - 1 else None
    pager_l = (
        f'<a href="{href(prev[0])}">Previous · {prev[1]}</a>'
        if prev
        else f'<a href="{home}#blogs">All blogs</a>'
    )
    pager_r = (
        f'<a href="{href(nxt[0])}">Next · {nxt[1]}</a>'
        if nxt
        else f'<a href="{home}#blogs">All blogs</a>'
    )
    if not re.search(r"<h1[\s>]", body):
        body = f"<h1>{htmlmod.escape(title)}</h1>\n{body}"
    body = f'<div id="top"></div>\n{body}'
    desc = htmlmod.escape(title) + " — Web Security notes."
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{htmlmod.escape(title)} — Hieu Nguyen</title>
  <meta name="description" content="{desc}">
  <link rel="icon" href="{home}favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{home}css/docs.css">
</head>
<body class="docs">
  <div class="cursor" id="cursor"></div>
  <div class="cursor-ring" id="cursorRing"></div>
  <canvas id="matrix-canvas"></canvas>
  <div class="grid-bg"></div>
  <header class="docs-topbar">
    <button class="docs-menu-btn" id="docsMenuBtn" type="button">menu</button>
    <a class="docs-brand" href="{home}">i'm<span>.hieu</span></a>
    <nav class="docs-series">
      <a class="active" href="{href("overview")}">Web Security</a>
      <a href="{'../../cks-exam/' if nested else '../cks-exam/'}">CKS exam</a>
    </nav>
    <span class="docs-topbar-spacer"></span>
    <a class="docs-top-link" href="{home}#blogs">blogs</a>
  </header>
  <div class="docs-shell">
    <aside class="docs-sidebar" id="docsSidebar" data-docs-root="{'../' if nested else './'}" data-active="{'overview' if slug == 'overview' else slug}">
      <div class="docs-nav-label">Web Security</div>
      <ul class="docs-nav" id="docsNav"></ul>
    </aside>
    <article class="docs-main">
      <div class="docs-breadcrumb">
        <a href="{home}">Home</a>
        <span>›</span>
        <a href="{home}#blogs">Blogs</a>
        <span>›</span>
        <a href="{href("overview")}">Overview</a>
        <span>›</span>
        <span>{htmlmod.escape(crumb)}</span>
      </div>
      {body}
      <div class="docs-pager">
        {pager_l}
        {pager_r}
      </div>
    </article>
    <aside class="docs-toc">
      <div class="docs-toc-title">On this page</div>
      <nav>
{toc(body)}
      </nav>
    </aside>
  </div>
  <script src="{home}js/docs.js"></script>
</body>
</html>
"""


def download_all() -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    meta = []
    for slug, crumb, path in PAGES:
        url = ASSET + path
        dest = CACHE / f"{slug}.html"
        try:
            html = fetch(url)
        except HTTPError as e:
            print("FAIL", slug, url, e.code)
            continue
        body = extract_markdown(html)
        dest.write_text(body, encoding="utf-8")
        title_m = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
        title = re.sub(r"<[^>]+>", "", title_m.group(1)).strip() if title_m else crumb
        meta.append({"slug": slug, "title": title, "url": url, "chars": len(body)})
        print(f"{slug:16} {len(body):7}  {title[:70]}")
        time.sleep(0.12)
    (CACHE / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")


def build() -> None:
    meta = {m["slug"]: m for m in json.loads((CACHE / "meta.json").read_text())}
    ROOT.mkdir(parents=True, exist_ok=True)
    for slug, crumb, _path in PAGES:
        raw = (CACHE / f"{slug}.html").read_text(encoding="utf-8")
        body = clean(raw, slug)
        title = meta[slug]["title"]
        page = wrap(slug, crumb, title, body)
        if slug == "overview":
            (ROOT / "index.html").write_text(page, encoding="utf-8")
        else:
            d = ROOT / slug
            d.mkdir(exist_ok=True)
            (d / "index.html").write_text(page, encoding="utf-8")
        print("wrote", slug, len(page))


if __name__ == "__main__":
    import sys
    if "--build-only" not in sys.argv:
        download_all()
    build()
