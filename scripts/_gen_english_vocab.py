#!/usr/bin/env python3
"""Build English vocab roadmap pages (topic → A1–B2) linking out to LanGeek."""
from __future__ import annotations

import html as htmlmod
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(__file__).with_name("english_vocab_data.json")
OUT = ROOT / "public" / "blog" / "english"


def esc(s: str) -> str:
    return htmlmod.escape(s, quote=True)


def wrap_chrome(*, title: str, desc: str, home: str, body: str, shell: str = "docs-shell-hub", english_href: str = "./") -> str:
    # Derive sibling series links from home depth
    # home is e.g. ../../ or ../../../
    blog = f"{home}blog/"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)} — Hieu Nguyen</title>
  <meta name="description" content="{esc(desc)}">
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
      <a href="{blog}web-security/">DevSecOps</a>
      <a href="{blog}kubestronaut/">Kubestronaut</a>
      <a class="active" href="{english_href}">English</a>
    </nav>
    <span class="docs-topbar-spacer"></span>
    <a class="docs-top-link" href="{home}#blogs">blogs</a>
  </header>
  <div class="{shell}">
{body}
  </div>
  <script src="{home}js/docs.js"></script>
</body>
</html>
"""


def build_hub(topics: list[dict]) -> str:
    cards = []
    for i, t in enumerate(topics, 1):
        levels = " · ".join(t["levels"])
        cards.append(
            f"""        <a class="vocab-topic-card" href="{esc(t["slug"])}/">
          <span class="vocab-topic-card__num">{i:02d}</span>
          <img class="vocab-topic-card__img" src="{esc(t["cover"])}" alt="" width="96" height="96" loading="lazy">
          <div class="vocab-topic-card__body">
            <h2>{esc(t["name"])}</h2>
            <p>{esc(t["desc"])}</p>
            <div class="vocab-topic-card__meta">
              <span>{t["count"]} lessons</span>
              <span>{esc(levels)}</span>
            </div>
            <span class="vocab-topic-card__cta">Open topic →</span>
          </div>
        </a>"""
        )
    body = f"""    <article class="docs-main">
      <div class="docs-breadcrumb">
        <a href="../../">Home</a>
        <span>›</span>
        <a href="../../#blogs">Blogs</a>
        <span>›</span>
        <span>English</span>
      </div>
      <h1>English Vocab Roadmap</h1>
      <p class="lede">Grouped by topic first — then climb <strong>A1 → B2</strong> inside each theme. Lessons open on <a href="https://langeek.co/en/vocab/level-based" target="_blank" rel="noopener noreferrer">LanGeek</a>. C1 / C2 coming later.</p>
      <div class="docs-meta">
        <span><strong>Topics:</strong> {len(topics)}</span>
        <span><strong>Lessons:</strong> {sum(t["count"] for t in topics)}</span>
        <span><strong>Levels:</strong> A1 · A2 · B1 · B2</span>
      </div>
      <div class="vocab-topic-grid">
{chr(10).join(cards)}
      </div>
    </article>"""
    return wrap_chrome(
        title="English Vocab Roadmap",
        desc="Topic-first English vocabulary roadmap (A1–B2) with links to LanGeek lessons.",
        home="../../",
        body=body,
        english_href="./",
    )


def build_topic(topic: dict, all_topics: list[dict]) -> str:
    slug = topic["slug"]
    nav_items = []
    for t in all_topics:
        cls = ' class="active"' if t["slug"] == slug else ""
        href = "../" if t["slug"] == slug else f'../{t["slug"]}/'
        if t["slug"] == slug:
            href = "./"
        else:
            href = f'../{t["slug"]}/'
        nav_items.append(f'        <li><a{cls} href="{href}">{esc(t["name"])}</a></li>')

    level_blocks = []
    for level in ["A1", "A2", "B1", "B2"]:
        lessons = [x for x in topic["lessons"] if x["level"] == level]
        if not lessons:
            continue
        cards = []
        for les in lessons:
            cards.append(
                f"""          <a class="vocab-lesson-card" href="{esc(les["url"])}" target="_blank" rel="noopener noreferrer">
            <img src="{esc(les["photo"])}" alt="" width="72" height="72" loading="lazy">
            <span>{esc(les["title"])}</span>
          </a>"""
            )
        level_blocks.append(
            f"""      <section class="vocab-level" id="{level.lower()}">
        <div class="vocab-level__head">
          <span class="vocab-level__badge">{level}</span>
          <h2>{level} · {len(lessons)} lesson{"s" if len(lessons) != 1 else ""}</h2>
        </div>
        <div class="vocab-lesson-grid">
{chr(10).join(cards)}
        </div>
      </section>"""
        )

    # prev / next topic
    idx = next(i for i, t in enumerate(all_topics) if t["slug"] == slug)
    prev_t = all_topics[idx - 1] if idx else None
    next_t = all_topics[idx + 1] if idx < len(all_topics) - 1 else None
    pager_l = (
        f'<a href="../{prev_t["slug"]}/">Previous · {esc(prev_t["name"])}</a>'
        if prev_t
        else '<a href="../">All topics</a>'
    )
    pager_r = (
        f'<a href="../{next_t["slug"]}/">Next · {esc(next_t["name"])}</a>'
        if next_t
        else '<a href="../">All topics</a>'
    )

    body = f"""    <aside class="docs-sidebar" id="docsSidebar" data-nav="english" data-docs-root="../" data-active="{esc(slug)}">
      <div class="docs-nav-label">English</div>
      <ul class="docs-nav" id="docsNav">
        <li><a href="../">All topics</a></li>
{chr(10).join(nav_items)}
      </ul>
    </aside>
    <article class="docs-main">
      <div class="docs-breadcrumb">
        <a href="../../../">Home</a>
        <span>›</span>
        <a href="../../../#blogs">Blogs</a>
        <span>›</span>
        <a href="../">English</a>
        <span>›</span>
        <span>{esc(topic["name"])}</span>
      </div>
      <div class="vocab-topic-hero">
        <img src="{esc(topic["cover"])}" alt="" width="112" height="112">
        <div>
          <h1>{esc(topic["name"])}</h1>
          <p class="lede">{esc(topic["desc"])}</p>
          <div class="docs-meta">
            <span><strong>Lessons:</strong> {topic["count"]}</span>
            <span><strong>Path:</strong> {" → ".join(topic["levels"])}</span>
          </div>
        </div>
      </div>
{chr(10).join(level_blocks)}
      <div class="docs-pager">
        {pager_l}
        {pager_r}
      </div>
    </article>"""
    return wrap_chrome(
        title=f'{topic["name"]} — English Vocab',
        desc=f'{topic["name"]} vocabulary path A1–B2 on LanGeek.',
        home="../../../",
        body=body,
        shell="docs-shell",
        english_href="../",
    )


def main() -> None:
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    topics = payload["topics"]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "index.html").write_text(build_hub(topics), encoding="utf-8")
    for t in topics:
        d = OUT / t["slug"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(build_topic(t, topics), encoding="utf-8")
    print(f"Wrote hub + {len(topics)} topics → {OUT}")


if __name__ == "__main__":
    main()
