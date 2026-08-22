#!/usr/bin/env python3
"""Generate per-topic / per-level Exercise reading pages for English vocab roadmap.

Each exercise page:
- reading passage that includes every LanGeek word for that topic+level
- IPA + highlight toggles
- sentence-level bilingual (VI) toggle
- browser TTS (prefer natural English voices)
"""
from __future__ import annotations

import html as htmlmod
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOPICS = json.loads((Path(__file__).with_name("english_vocab_data.json")).read_text(encoding="utf-8"))
WORDS = json.loads((Path(__file__).with_name("english_words_by_lesson.json")).read_text(encoding="utf-8"))
OUT = ROOT / "public" / "blog" / "english"

LEVELS = ["A1", "A2", "B1", "B2"]

EXERCISE_ICON = (
    "data:image/svg+xml,"
    + "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 72 72' fill='none'%3E"
    "%3Crect width='72' height='72' rx='14' fill='%230b1220'/%3E"
    "%3Crect x='16' y='14' width='40' height='46' rx='6' stroke='%2322d3ee' stroke-width='2.5'/%3E"
    "%3Cpath d='M24 28h24M24 36h24M24 44h16' stroke='%23e4e4e7' stroke-width='2.5' stroke-linecap='round'/%3E"
    "%3Cpath d='M48 48l6 2-2 6-8-8 4 0z' fill='%2322d3ee'/%3E"
    "%3C/svg%3E"
)


def esc(s: str) -> str:
    return htmlmod.escape(s or "", quote=True)


def norm_key(w: str) -> str:
    return re.sub(r"\s+", " ", (w or "").strip().lower())


def display_form(word: str) -> str:
    w = (word or "").strip()
    if w.lower().startswith("to ") and len(w) > 3:
        return w[3:].strip()
    return w


def collect_words(lesson_ids: list[int]) -> list[dict]:
    seen = set()
    out = []
    for lid in lesson_ids:
        for item in WORDS.get(str(lid), []):
            key = norm_key(item.get("word", ""))
            if not key or key in seen:
                continue
            seen.add(key)
            out.append(
                {
                    "word": item["word"].strip(),
                    "form": display_form(item["word"]),
                    "ipa": (item.get("ipa") or "").strip().strip("/"),
                    "vi": (item.get("vi") or "").strip(),
                    "pos": item.get("pos") or "",
                }
            )
    return out


def mark_sentence(en: str, used: list[dict]) -> str:
    """Wrap vocabulary forms in mark+ipa, longest forms first.

    Skips matches inside an existing <mark>...</mark>.
    Also accepts light inflections (plural / -ed / -ing) so blog prose can stay natural.
    """

    def safe_subn(pattern: re.Pattern, repl, text: str, count: int = 1) -> tuple[str, int]:
        out: list[str] = []
        last = 0
        n = 0
        for m in pattern.finditer(text):
            if n >= count:
                break
            before = text[: m.start()]
            if before.rfind("<mark") > before.rfind("</mark>"):
                continue
            lt = before.rfind("<")
            gt = before.rfind(">")
            if lt > gt:
                continue
            piece = repl(m) if callable(repl) else repl
            out.append(text[last : m.start()])
            out.append(piece)
            last = m.end()
            n += 1
        out.append(text[last:])
        return "".join(out), n

    def patterns_for(form: str, word: str) -> list[re.Pattern]:
        f = form
        fl = form.lower()
        variants = [f]
        # Plural -s (avoid treating short words like "wing" as already "-ing")
        if not fl.endswith("s"):
            variants.append(f + "s")
            if fl.endswith(("ch", "sh", "x", "z", "o")):
                variants.append(f + "es")
            elif fl.endswith("y") and len(f) > 1 and fl[-2] not in "aeiou":
                variants.append(f[:-1] + "ies")
        # Past / gerund only for longer bases (so wing/ring/king still get plurals)
        if len(fl) >= 5 and not fl.endswith("ed"):
            variants.append(f + "ed")
            if fl.endswith("e"):
                variants.append(f + "d")
        if len(fl) >= 6 and not fl.endswith("ing"):
            variants.append(f + "ing")
        # original lemma with leading "to "
        if word.lower().startswith("to ") and word.lower() != fl:
            variants.append(word)
        # unique, longest first
        seen: set[str] = set()
        ordered: list[str] = []
        for v in sorted(variants, key=len, reverse=True):
            key = v.lower()
            if key in seen or not v:
                continue
            seen.add(key)
            ordered.append(v)
        return [re.compile(rf"(?<![A-Za-z]){re.escape(v)}(?![A-Za-z])", re.I) for v in ordered]

    result = en
    for item in sorted(used, key=lambda x: len(x["form"]), reverse=True):
        form = item["form"]
        if not form:
            continue
        ipa = item["ipa"]
        ipa_html = f'<span class="ipa" aria-hidden="true">/{esc(ipa)}/</span>' if ipa else ""

        def repl(m, _w=item["word"], _ipa=ipa_html):
            return f'<mark class="vocab" data-word="{esc(_w)}">{esc(m.group(0))}</mark>{_ipa}'

        n = 0
        for pattern in patterns_for(form, item["word"]):
            result, n = safe_subn(pattern, repl, result, count=1)
            if n:
                break
    return result


def vi_gloss(item: dict) -> str:
    return item["vi"] if item["vi"] else item["form"]


def compose_chunk(chunk: list[dict], topic: str, level: str, idx: int) -> tuple[str, str]:
    """Build one EN sentence + one VI sentence that use every word in the chunk."""
    nouns = [w for w in chunk if w["pos"] in ("noun", "adjective", "") or not str(w["pos"]).startswith("verb")]
    verbs = [w for w in chunk if "verb" in str(w["pos"]).lower() or w["word"].lower().startswith("to ")]
    # fallback: treat all as content words
    if not nouns and not verbs:
        nouns = chunk[:]

    forms = [w["form"] for w in chunk]
    vi_bits = [vi_gloss(w) for w in chunk]

    # Rotate narrative frames so the passage feels like a story, not a list
    frames = [
        (
            "On a typical day around {topic}, you notice {a}, then {b}, and later {c}.",
            "Trong một ngày bình thường về {topic}, bạn để ý {a}, rồi {b}, và sau đó {c}.",
        ),
        (
            "Someone is learning {level} words like {a}, {b}, and {c} through real situations.",
            "Ai đó đang học từ {level} như {a}, {b}, và {c} qua tình huống thật.",
        ),
        (
            "In conversation, people mention {a}; they also talk about {b} and {c}.",
            "Trong hội thoại, mọi người nhắc tới {a}; họ cũng nói về {b} và {c}.",
        ),
        (
            "At home and outside, {a} appears first, followed by {b}, with {c} at the end of the story.",
            "Ở nhà và ngoài đường, {a} xuất hiện trước, tiếp theo là {b}, và {c} ở cuối câu chuyện.",
        ),
        (
            "If you want natural English, practice {a}, then reuse {b}, and finally remember {c}.",
            "Nếu muốn tiếng Anh tự nhiên, hãy luyện {a}, rồi dùng lại {b}, và cuối cùng nhớ {c}.",
        ),
    ]
    # Expand for chunks of size 1–6
    n = len(chunk)
    if n == 1:
        en = f"You should learn the word {forms[0]} because it appears often in {topic} topics."
        vi = f"Bạn nên học từ {vi_bits[0]} vì nó thường xuất hiện trong chủ đề {topic}."
    elif n == 2:
        en = f"In daily life you meet {forms[0]} and {forms[1]} when the topic is {topic}."
        vi = f"Trong đời sống hằng ngày bạn gặp {vi_bits[0]} và {vi_bits[1]} khi nói về {topic}."
    elif n == 3:
        frame = frames[idx % len(frames)]
        en = frame[0].format(topic=topic, level=level, a=forms[0], b=forms[1], c=forms[2])
        vi = frame[1].format(topic=topic, level=level, a=vi_bits[0], b=vi_bits[1], c=vi_bits[2])
    elif n == 4:
        en = (
            f"Around {topic}, learners first study {forms[0]} and {forms[1]}, "
            f"then connect them with {forms[2]} and {forms[3]}."
        )
        vi = (
            f"Với chủ đề {topic}, người học bắt đầu với {vi_bits[0]} và {vi_bits[1]}, "
            f"rồi nối với {vi_bits[2]} và {vi_bits[3]}."
        )
    elif n == 5:
        en = (
            f"This {level} scene includes {forms[0]}, {forms[1]}, and {forms[2]}; "
            f"soon after, {forms[3]} and {forms[4]} complete the picture."
        )
        vi = (
            f"Bối cảnh {level} này có {vi_bits[0]}, {vi_bits[1]}, và {vi_bits[2]}; "
            f"ngay sau đó, {vi_bits[3]} và {vi_bits[4]} hoàn thiện bức tranh."
        )
    else:
        mid = ", ".join(forms[:-1])
        mid_vi = ", ".join(vi_bits[:-1])
        en = f"In one connected story about {topic}, you will hear {mid}, and finally {forms[-1]}."
        vi = f"Trong một câu chuyện liền mạch về {topic}, bạn sẽ nghe {mid_vi}, và cuối cùng là {vi_bits[-1]}."

    # Prefer verb frames when chunk is mostly verbs
    if len(verbs) >= max(2, n - 1) and n >= 2:
        vforms = [w["form"] for w in chunk]
        vvi = [vi_gloss(w) for w in chunk]
        if n == 2:
            en = f"Today she tries to {vforms[0]} and then to {vforms[1]}."
            vi = f"Hôm nay cô ấy cố {vvi[0]} rồi {vvi[1]}."
        elif n >= 3:
            en = f"They learn to {vforms[0]}, to {vforms[1]}, and also to {vforms[2]}" + (
                f", before they {vforms[3]}" if n > 3 else ""
            ) + "."
            vi = f"Họ học cách {vvi[0]}, {vvi[1]}, và cả {vvi[2]}" + (
                f", trước khi {vvi[3]}" if n > 3 else ""
            ) + "."

    return en, vi


def build_sentences(words: list[dict], topic_name: str, level: str) -> list[dict]:
    """Return list of {en_html, vi, words} covering every vocabulary item."""
    chunks: list[list[dict]] = []
    size = 4
    for i in range(0, len(words), size):
        chunks.append(words[i : i + size])

    sentences = []
    for idx, chunk in enumerate(chunks):
        en, vi = compose_chunk(chunk, topic_name, level, idx)
        # Ensure every form appears; if missing, append a short clause
        missing = [w for w in chunk if not re.search(rf"(?i)(?<![A-Za-z]){re.escape(w['form'])}(?![A-Za-z])", en)]
        if missing:
            extra = ", ".join(w["form"] for w in missing)
            en = en.rstrip(".") + f" — especially {extra}."
            extra_vi = ", ".join(vi_gloss(w) for w in missing)
            vi = vi.rstrip(".") + f" — đặc biệt là {extra_vi}."
        en_html = mark_sentence(en, chunk)
        sentences.append({"en_html": en_html, "vi": vi, "words": [w["word"] for w in chunk]})
    return sentences


def verify_coverage(words: list[dict], sentences: list[dict]) -> list[str]:
    blob = " ".join(s["en_html"] for s in sentences).lower()
    missing = []
    for w in words:
        form = w["form"].lower()
        lemma = w["word"].lower()
        if form not in blob and lemma not in blob:
            missing.append(w["word"])
    return missing


BRAND = '<span>✦</span> The Quiet Corner <span>✦</span>'


def wrap_exercise(topic: dict, level: str, words: list[dict], sentences: list[dict], lesson_titles: list[str]) -> str:
    slug = topic["slug"]
    name = topic["name"]
    home = "../../../../"
    missing = verify_coverage(words, sentences)
    sent_html = []
    for i, s in enumerate(sentences, 1):
        sent_html.append(
            f"""          <p class="ex-sent" data-sent="{i}">
            <span class="ex-en">{s["en_html"]}</span>
            <span class="ex-vi">{esc(s["vi"])}</span>
          </p>"""
        )

    vocab_chips = []
    for w in words:
        ipa = f' <span class="ipa">/{esc(w["ipa"])}/</span>' if w["ipa"] else ""
        vi = f' — {esc(w["vi"])}' if w["vi"] else ""
        vocab_chips.append(
            f'<li><mark class="vocab">{esc(w["form"])}</mark>{ipa}{vi}</li>'
        )

    lessons_line = " · ".join(esc(t) for t in lesson_titles)
    warn = ""
    if missing:
        warn = (
            f'<p class="ex-warn">Coverage check: {len(missing)} word(s) need review — '
            + esc(", ".join(missing[:12]))
            + ("…" if len(missing) > 12 else "")
            + "</p>"
        )

    body = f"""    <aside class="docs-sidebar" id="docsSidebar" data-nav="english" data-docs-root="../../" data-active="{esc(slug)}">
      <div class="docs-nav-label">English</div>
      <ul class="docs-nav" id="docsNav">
        <li><a href="../../">All topics</a></li>
        <li><a href="../">{esc(name)}</a></li>
        <li><a class="active" href="./">{esc(level)} Exercise</a></li>
      </ul>
    </aside>
    <article class="docs-main">
      <div class="docs-breadcrumb">
        <a href="{home}">Home</a>
        <span>›</span>
        <a href="{home}#blogs">Blogs</a>
        <span>›</span>
        <a href="../../">English</a>
        <span>›</span>
        <a href="../">{esc(name)}</a>
        <span>›</span>
        <span>{esc(level)} Exercise</span>
      </div>

      <div class="vocab-topic-hero">
        <img src="{EXERCISE_ICON}" alt="" width="112" height="112">
        <div>
          <h1>{esc(level)} Exercise · {esc(name)}</h1>
          <p class="lede">Reading passage with every new word from this level’s LanGeek lessons — IPA, highlights, sentence translation, and free TTS.</p>
          <div class="docs-meta">
            <span><strong>Words:</strong> {len(words)}</span>
            <span><strong>Lessons:</strong> {lessons_line}</span>
          </div>
        </div>
      </div>

      <div class="ex-toolbar" id="exToolbar">
        <label class="ex-toggle"><input type="checkbox" id="togHighlight" checked> Highlights</label>
        <label class="ex-toggle"><input type="checkbox" id="togIpa" checked> IPA</label>
        <label class="ex-toggle"><input type="checkbox" id="togVi"> Dịch câu (VI)</label>
        <span class="ex-sep"></span>
        <label class="ex-voice">Voice
          <select id="voiceSelect" aria-label="TTS voice"></select>
        </label>
        <label class="ex-voice">Speed
          <input id="rateRange" type="range" min="0.7" max="1.15" step="0.05" value="0.95">
          <span id="rateVal">0.95</span>
        </label>
        <button type="button" class="ex-btn primary" id="btnPlay">▶ Read passage</button>
        <button type="button" class="ex-btn" id="btnStop">Stop</button>
      </div>
      {warn}
      <section class="ex-passage" id="passage" data-tts-root>
{chr(10).join(sent_html)}
      </section>
      <!-- Continuous paragraph (no IPA) is filled by public/js/exercise.js for NaturalReader paste -->

      <section class="ex-vocab">
        <h2>Word checklist · {len(words)}</h2>
        <ul class="ex-vocab-list">
{chr(10).join("          " + c for c in vocab_chips)}
        </ul>
      </section>

      <div class="docs-pager">
        <a href="../">← {esc(name)}</a>
        <a href="../../">All topics →</a>
      </div>
    </article>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(level)} Exercise · {esc(name)} — The Quiet Corner</title>
  <meta name="description" content="{esc(level)} reading exercise for {esc(name)} vocabulary with IPA and bilingual sentences.">
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
    <a class="docs-brand" href="{home}">{BRAND}</a>
    <nav class="docs-series">
      <a href="{home}blog/web-security/">DevSecOps</a>
      <a href="{home}blog/kubestronaut/">Kubestronaut</a>
      <a class="active" href="../../">English</a>
    </nav>
    <span class="docs-topbar-spacer"></span>
    <a class="docs-top-link" href="{home}#blogs">blogs</a>
  </header>
  <div class="docs-shell">
{body}
  </div>
  <script src="{home}js/docs.js"></script>
  <script src="{home}js/exercise.js"></script>
</body>
</html>
"""


def exercise_card(level: str) -> str:
    return f"""          <a class="vocab-lesson-card vocab-lesson-card--exercise" href="{level.lower()}-exercise/">
            <img src="{EXERCISE_ICON}" alt="" width="72" height="72" loading="lazy">
            <span>{esc(level)} Exercise</span>
          </a>"""


def main() -> None:
    report = []
    for topic in TOPICS["topics"]:
        slug = topic["slug"]
        for level in LEVELS:
            lessons = [l for l in topic["lessons"] if l["level"] == level]
            if not lessons:
                continue
            words = collect_words([l["id"] for l in lessons])
            sentences = build_sentences(words, topic["name"], level)
            missing = verify_coverage(words, sentences)
            # Repair pass: append dedicated sentences for any missing words
            if missing:
                miss_items = [w for w in words if w["word"] in missing]
                for i in range(0, len(miss_items), 3):
                    chunk = miss_items[i : i + 3]
                    en, vi = compose_chunk(chunk, topic["name"], level, 99 + i)
                    for w in chunk:
                        if w["form"].lower() not in en.lower():
                            en += f" ({w['form']})"
                    sentences.append(
                        {
                            "en_html": mark_sentence(en, chunk),
                            "vi": vi,
                            "words": [w["word"] for w in chunk],
                        }
                    )
                missing = verify_coverage(words, sentences)

            page = wrap_exercise(
                topic,
                level,
                words,
                sentences,
                [l["title"] for l in lessons],
            )
            out_dir = OUT / slug / f"{level.lower()}-exercise"
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / "index.html").write_text(page, encoding="utf-8")
            report.append(f"{slug}/{level}: {len(words)} words, {len(sentences)} sents, missing={len(missing)}")
            if missing:
                print("WARN", slug, level, missing[:8])

    # Patch topic pages: inject exercise card into each level grid
    for topic in TOPICS["topics"]:
        path = OUT / topic["slug"] / "index.html"
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for level in LEVELS:
            lessons = [l for l in topic["lessons"] if l["level"] == level]
            if not lessons:
                continue
            card = exercise_card(level)
            # Insert exercise card as first card in that level's grid if missing
            if f'{level.lower()}-exercise/' in text:
                continue
            pattern = rf'(<section class="vocab-level" id="{level.lower()}">.*?<div class="vocab-lesson-grid">\s*)'
            text2, n = re.subn(pattern, rf"\1{card}\n", text, count=1, flags=re.S)
            if n:
                text = text2
            else:
                print("no grid inject", topic["slug"], level)
        path.write_text(text, encoding="utf-8")

    print("exercises written:")
    for line in report:
        print(" ", line)
    print("total", len(report))


if __name__ == "__main__":
    main()
