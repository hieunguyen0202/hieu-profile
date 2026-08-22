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
