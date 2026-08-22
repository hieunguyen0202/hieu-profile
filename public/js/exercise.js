(() => {
  const root = document.getElementById("passage");
  if (!root) return;

  const body = document.body;
  const togHighlight = document.getElementById("togHighlight");
  const togIpa = document.getElementById("togIpa");
  const togVi = document.getElementById("togVi");
  const voiceSelect = document.getElementById("voiceSelect");
  const rateRange = document.getElementById("rateRange");
  const rateVal = document.getElementById("rateVal");
  const btnPlay = document.getElementById("btnPlay");
  const btnStop = document.getElementById("btnStop");

  const applyToggles = () => {
    body.classList.toggle("ex-hide-hl", togHighlight && !togHighlight.checked);
    body.classList.toggle("ex-hide-ipa", togIpa && !togIpa.checked);
    body.classList.toggle("ex-show-vi", togVi && togVi.checked);
  };
  [togHighlight, togIpa, togVi].forEach((el) => el && el.addEventListener("change", applyToggles));
  applyToggles();

  /** Plain English from a sentence node — IPA is display-only, never spoken/copied. */
  const plainFromEn = (el) => {
    const clone = el.cloneNode(true);
    clone.querySelectorAll(".ipa").forEach((n) => n.remove());
    return clone.textContent.replace(/\s+/g, " ").trim();
  };

  const sentenceTexts = () =>
    [...root.querySelectorAll(".ex-en")].map(plainFromEn).filter(Boolean);

  const passageText = () => sentenceTexts().join(" ");

  /** One continuous paragraph for NaturalReader / external TTS paste. */
  const ensureContinuousBlock = () => {
    let section = document.getElementById("exContinuous");
    if (!section) {
      section = document.createElement("section");
      section.className = "ex-continuous";
      section.id = "exContinuous";
      section.innerHTML = `
        <div class="ex-continuous-head">
          <h2>Continuous paragraph</h2>
          <button type="button" class="ex-btn primary" id="btnCopyPara">Copy</button>
        </div>
        <p class="ex-continuous-hint">Plain English only (no IPA) — copy and paste into <a href="https://www.naturalreaders.com/online/" target="_blank" rel="noopener noreferrer">NaturalReader</a> or any TTS.</p>
        <textarea id="exParaText" class="ex-para" readonly rows="8" aria-label="Continuous paragraph for external TTS"></textarea>
      `;
      root.insertAdjacentElement("afterend", section);
    }
    const ta = document.getElementById("exParaText");
    if (ta) ta.value = passageText();

    const btn = document.getElementById("btnCopyPara");
    if (btn && !btn.dataset.bound) {
      btn.dataset.bound = "1";
      btn.addEventListener("click", async () => {
        const text = (ta && ta.value) || passageText();
        if (!text) return;
        try {
          await navigator.clipboard.writeText(text);
          const prev = btn.textContent;
          btn.textContent = "Copied";
          setTimeout(() => {
            btn.textContent = prev;
          }, 1400);
        } catch {
          if (ta) {
            ta.focus();
            ta.select();
          }
        }
      });
    }
  };
  ensureContinuousBlock();

  /* ── Match quiz (word ↔ nghĩa) ─────────────────────────────────────── */
  const PAIR_COUNT = 6;

  const shuffle = (arr) => {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  };

  const loadVocab = () => {
    const raw = document.getElementById("exVocabData");
    if (raw && raw.textContent.trim()) {
      try {
        const data = JSON.parse(raw.textContent);
        return data.filter((w) => w.form && (w.vi || w.word));
      } catch {
        /* fall through */
      }
    }
    return [...document.querySelectorAll(".ex-vocab-list li")]
      .map((li, i) => {
        const form = (li.querySelector("mark.vocab") || {}).textContent || "";
        const ipaEl = li.querySelector(".ipa");
        const ipa = ipaEl ? ipaEl.textContent.replace(/\//g, "").trim() : "";
        const parts = li.textContent.split("—");
        const vi = parts.length > 1 ? parts.slice(1).join("—").trim() : "";
        return { id: i, form: form.trim(), word: form.trim(), ipa, vi, pos: "" };
      })
      .filter((w) => w.form && w.vi);
  };

  const initMatchGame = () => {
    const vocab = loadVocab();
    let section = document.getElementById("exMatch");
    if (!vocab.length) {
      if (section) section.hidden = true;
      return;
    }

    if (!section) {
      section = document.createElement("section");
      section.className = "ex-match";
      section.id = "exMatch";
      section.setAttribute("aria-label", "Vocabulary match quiz");
      section.innerHTML = `
        <div class="ex-match-head">
          <div>
            <h2>Match quiz</h2>
            <p class="ex-match-hint">Ghép từ (EN + IPA) với nghĩa tiếng Việt — mỗi ván 6 cặp. Tính điểm, có thể Reset / New round.</p>
          </div>
          <div class="ex-match-controls">
            <div class="ex-match-stats" aria-live="polite">
              <span>Score <strong id="matchScore">0</strong></span>
              <span>Matched <strong id="matchDone">0</strong>/<strong id="matchTotal">0</strong></span>
              <span>Misses <strong id="matchMiss">0</strong></span>
            </div>
            <button type="button" class="ex-btn" id="btnMatchReset">Reset</button>
            <button type="button" class="ex-btn primary" id="btnMatchNew">New round</button>
          </div>
        </div>
        <div class="ex-match-grid" id="matchGrid"></div>
        <p class="ex-match-msg" id="matchMsg" hidden></p>
      `;
      const continuous = document.getElementById("exContinuous");
      const vocabSec = document.querySelector(".ex-vocab");
      if (continuous) continuous.insertAdjacentElement("afterend", section);
      else if (vocabSec) vocabSec.insertAdjacentElement("beforebegin", section);
      else root.insertAdjacentElement("afterend", section);
    }

    const grid = document.getElementById("matchGrid");
    const elScore = document.getElementById("matchScore");
    const elDone = document.getElementById("matchDone");
    const elTotal = document.getElementById("matchTotal");
    const elMiss = document.getElementById("matchMiss");
    const elMsg = document.getElementById("matchMsg");
    const btnReset = document.getElementById("btnMatchReset");
    const btnNew = document.getElementById("btnMatchNew");
    if (!grid) return;

    let score = 0;
    let misses = 0;
    let matched = 0;
    let total = 0;
    let selected = null;
    let locked = false;
    let roundPairs = [];
    let usedIds = new Set();

    const renderStats = () => {
      if (elScore) elScore.textContent = String(score);
      if (elDone) elDone.textContent = String(matched);
      if (elTotal) elTotal.textContent = String(total);
      if (elMiss) elMiss.textContent = String(misses);
    };

    const showMsg = (text, ok) => {
      if (!elMsg) return;
      elMsg.hidden = !text;
      elMsg.textContent = text || "";
      elMsg.classList.toggle("ok", !!ok);
    };

    const escapeHtml = (s) =>
      String(s)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");

    const pickRound = (freshPool) => {
      const pool = freshPool
        ? shuffle(vocab)
        : shuffle(vocab.filter((w) => !usedIds.has(w.id)));
      if (!pool.length || (pool.length < Math.min(PAIR_COUNT, vocab.length) && !freshPool)) {
        usedIds = new Set();
        return pickRound(true);
      }
      const n = Math.min(PAIR_COUNT, pool.length);
      roundPairs = pool.slice(0, n);
      roundPairs.forEach((w) => usedIds.add(w.id));
      return roundPairs;
    };

    const buildBoard = (pairs) => {
      matched = 0;
      total = pairs.length;
      selected = null;
      locked = false;
      showMsg("");
      renderStats();

      const cards = [];
      pairs.forEach((w) => {
        cards.push({
          key: String(w.id),
          kind: "word",
          label: w.form,
          ipa: w.ipa ? `/${w.ipa}/` : "",
        });
        cards.push({
          key: String(w.id),
          kind: "def",
          label: w.vi || w.form,
          meta: [w.pos, w.form].filter(Boolean).join(" · "),
        });
      });

      grid.innerHTML = "";
      shuffle(cards).forEach((c) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = `ex-match-card ex-match-card--${c.kind}`;
        btn.dataset.key = c.key;
        btn.dataset.kind = c.kind;
        if (c.kind === "word") {
          btn.innerHTML = `<span class="ex-match-term">${escapeHtml(c.label)}</span>${
            c.ipa ? `<span class="ex-match-ipa">${escapeHtml(c.ipa)}</span>` : ""
          }`;
        } else {
          btn.innerHTML = `<span class="ex-match-vi"><em>Nghĩa</em> ${escapeHtml(c.label)}</span>${
            c.meta ? `<span class="ex-match-meta">${escapeHtml(c.meta)}</span>` : ""
          }`;
        }
        btn.addEventListener("click", () => onCard(btn));
        grid.appendChild(btn);
      });
    };

    const clearSelection = () => {
      grid.querySelectorAll(".ex-match-card.is-selected").forEach((el) => {
        el.classList.remove("is-selected");
      });
      selected = null;
    };

    const onCard = (btn) => {
      if (locked || btn.classList.contains("is-matched") || btn.classList.contains("is-selected")) {
        return;
      }
      if (!selected) {
        selected = btn;
        btn.classList.add("is-selected");
        return;
      }
      if (selected.dataset.kind === btn.dataset.kind) {
        clearSelection();
        selected = btn;
        btn.classList.add("is-selected");
        return;
      }

      locked = true;
      btn.classList.add("is-selected");
      const a = selected;
      const b = btn;
      const ok = a.dataset.key === b.dataset.key;

      if (ok) {
        score += 10;
        matched += 1;
        a.classList.remove("is-selected");
        b.classList.remove("is-selected");
        a.classList.add("is-matched");
        b.classList.add("is-matched");
        a.disabled = true;
        b.disabled = true;
        selected = null;
        locked = false;
        renderStats();
        if (matched >= total) {
          const bonus = Math.max(0, 20 - misses * 2);
          score += bonus;
          renderStats();
          showMsg(
            `Round clear! +${bonus} bonus (misses: ${misses}). Score: ${score}. Bấm New round để chơi tiếp.`,
            true
          );
        }
      } else {
        misses += 1;
        score = Math.max(0, score - 2);
        a.classList.add("is-wrong");
        b.classList.add("is-wrong");
        renderStats();
        setTimeout(() => {
          a.classList.remove("is-selected", "is-wrong");
          b.classList.remove("is-selected", "is-wrong");
          selected = null;
          locked = false;
        }, 520);
      }
    };

    const startRound = (resetScore) => {
      if (resetScore) {
        score = 0;
        misses = 0;
        usedIds = new Set();
      }
      const pairs = pickRound(resetScore);
      buildBoard(pairs);
    };

    btnReset &&
      btnReset.addEventListener("click", () => {
        startRound(true);
      });
    btnNew &&
      btnNew.addEventListener("click", () => {
        misses = 0;
        startRound(false);
      });

    startRound(true);
  };
  initMatchGame();

  /* ── Browser TTS (skip IPA) ────────────────────────────────────────── */
  if (!window.speechSynthesis) return;

  let voices = [];
  const preferred = [
    /google us english/i,
    /google uk english/i,
    /microsoft aria/i,
    /microsoft jenny/i,
    /microsoft guy/i,
    /samantha/i,
    /karen/i,
    /daniel/i,
    /en-us/i,
    /en-gb/i,
  ];

  const scoreVoice = (v) => {
    const label = `${v.name} ${v.lang}`;
    if (!/^en/i.test(v.lang)) return 1000;
    for (let i = 0; i < preferred.length; i++) {
      if (preferred[i].test(label)) return i;
    }
    return 50;
  };

  const fillVoices = () => {
    voices = speechSynthesis.getVoices().filter((v) => /^en/i.test(v.lang));
    voices.sort((a, b) => scoreVoice(a) - scoreVoice(b));
    if (!voiceSelect) return;
    voiceSelect.innerHTML = "";
    voices.forEach((v, i) => {
      const opt = document.createElement("option");
      opt.value = String(i);
      opt.textContent = `${v.name} (${v.lang})`;
      voiceSelect.appendChild(opt);
    });
  };
  fillVoices();
  speechSynthesis.onvoiceschanged = fillVoices;

  if (rateRange && rateVal) {
    rateRange.addEventListener("input", () => {
      rateVal.textContent = Number(rateRange.value).toFixed(2);
    });
  }

  const stop = () => speechSynthesis.cancel();
  btnStop && btnStop.addEventListener("click", stop);

  btnPlay &&
    btnPlay.addEventListener("click", () => {
      stop();
      const text = passageText();
      if (!text) return;
      const u = new SpeechSynthesisUtterance(text);
      const idx = voiceSelect ? Number(voiceSelect.value || 0) : 0;
      if (voices[idx]) u.voice = voices[idx];
      u.rate = rateRange ? Number(rateRange.value) : 0.95;
      u.lang = (voices[idx] && voices[idx].lang) || "en-US";
      speechSynthesis.speak(u);
    });
})();
