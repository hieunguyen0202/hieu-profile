(() => {
  const cursor = document.getElementById("cursor");
  const cursorRing = document.getElementById("cursorRing");
  let mx = 0;
  let my = 0;
  let rx = 0;
  let ry = 0;

  if (window.matchMedia("(pointer: fine)").matches) {
    document.addEventListener("mousemove", (e) => {
      mx = e.clientX;
      my = e.clientY;
    });
    const animCursor = () => {
      cursor.style.left = `${mx}px`;
      cursor.style.top = `${my}px`;
      rx += (mx - rx) * 0.12;
      ry += (my - ry) * 0.12;
      cursorRing.style.left = `${rx}px`;
      cursorRing.style.top = `${ry}px`;
      requestAnimationFrame(animCursor);
    };
    animCursor();
  }

  const canvas = document.getElementById("matrix-canvas");
  const ctx = canvas.getContext("2d");
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let drops = [];

  const resizeCanvas = () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    drops = Array(Math.floor(canvas.width / 18)).fill(1);
  };
  resizeCanvas();
  window.addEventListener("resize", resizeCanvas);

  const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<>[]{}|λΣ∞kubectlhelm";
  if (!reduceMotion) {
    setInterval(() => {
      ctx.fillStyle = "rgba(10,10,15,0.08)";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = "#22d3ee";
      ctx.font = "13px JetBrains Mono, monospace";
      drops.forEach((y, i) => {
        const c = chars[Math.floor(Math.random() * chars.length)];
        ctx.fillText(c, i * 18, y * 18);
        if (y * 18 > canvas.height && Math.random() > 0.975) drops[i] = 0;
        drops[i] += 1;
      });
    }, 55);
  }

  const bootLines = [
    { text: "BIOS v1.0.0 — Nguyen Xuan Hieu DevOps System", class: "info", delay: 80 },
    { text: "Loading kernel modules...", class: "ok", delay: 220 },
    { text: "Mounting cloud volumes (Azure, AWS, GCP)...", class: "ok", delay: 420 },
    { text: "Connecting to Kubernetes API server...", class: "ok", delay: 620 },
    { text: "Helm releases: healthy", class: "ok", delay: 820 },
    { text: "Jenkins: quality gates green", class: "ok", delay: 1000 },
    { text: "Trivy / Snyk / SonarQube: scanners online", class: "ok", delay: 1180 },
    { text: "Welcome, Hieu — System / DevOps Engineer", class: "info", delay: 1400 },
    { text: "System ready. Booting portfolio...", class: "warn", delay: 1600 },
  ];

  const bootContent = document.getElementById("boot-content");
  const bootScreen = document.getElementById("boot-screen");

  bootLines.forEach((line) => {
    setTimeout(() => {
      const el = document.createElement("div");
      el.className = `boot-line ${line.class}`;
      el.textContent = line.text;
      bootContent.appendChild(el);
    }, reduceMotion ? 0 : line.delay);
  });

  setTimeout(() => {
    const bar = document.createElement("div");
    bar.className = "boot-bar";
    bar.innerHTML = '<div class="boot-bar-fill"></div>';
    bootContent.appendChild(bar);
  }, reduceMotion ? 0 : 1750);

  const hideBoot = () => {
    bootScreen.style.transition = "opacity 0.45s";
    bootScreen.style.opacity = "0";
    setTimeout(() => {
      bootScreen.style.display = "none";
    }, 450);
  };
  setTimeout(hideBoot, reduceMotion ? 200 : 3200);

  const heroTermBody = document.getElementById("hero-terminal-body");
  const promptHtml = '<span class="prompt">$ </span>';

  const termLines = [
    { type: "cmd", text: "kubectl get certificates" },
    { type: "out", text: "NAME   CERTIFICATE                                EXPIRES", color: "cyan" },
    { type: "out", text: "cks    Certified Kubernetes Security Specialist   Aug-2028", color: "ok" },
    { type: "out", text: "ckad   Certified Kubernetes Application Developer Jun-2028", color: "ok" },
    { type: "out", text: "cka    Certified Kubernetes Administrator         Mar-2028", color: "ok" },
    { type: "cmd", text: "helm list -A | grep -v pending" },
    { type: "out", text: "argocd    Deployed ✓   synced", color: "ok" },
    { type: "out", text: "jenkins   Deployed ✓   2 releases/week", color: "ok" },
    { type: "out", text: "ingress   Deployed ✓   nginx", color: "ok" },
    { type: "cmd", text: "cat .identity" },
    { type: "out", text: "role:       System / DevOps Engineer", color: "" },
    { type: "out", text: "education:  HCMUT — VNU HCMC", color: "" },
    { type: "out", text: "languages:  VI / EN · TOEIC 855", color: "" },
  ];

  const buildTermLine = (line) => {
    const el = document.createElement("div");
    if (line.type === "cmd") {
      el.className = "term-line";
      el.innerHTML = `${promptHtml}<span style="color:var(--white)">${line.text}</span>`;
    } else {
      el.className = `term-output ${line.color || ""}`;
      el.textContent = line.text;
    }
    return el;
  };

  let tIdx = 0;
  const addTermLine = () => {
    if (tIdx >= termLines.length) {
      const el = document.createElement("div");
      el.className = "term-line";
      el.innerHTML = `${promptHtml}<span class="blink" style="color:var(--accent)">▊</span>`;
      heroTermBody.appendChild(el);
      return;
    }
    heroTermBody.appendChild(buildTermLine(termLines[tIdx]));
    tIdx += 1;
    setTimeout(addTermLine, tIdx % 4 === 0 ? 180 : 70);
  };
  setTimeout(addTermLine, reduceMotion ? 250 : 3400);

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) e.target.classList.add("visible");
      });
    },
    { threshold: 0.1 }
  );
  document.querySelectorAll(".reveal").forEach((el) => observer.observe(el));

  const skillObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          e.target.querySelectorAll(".skill-fill").forEach((fill) => {
            fill.style.width = `${fill.dataset.width}%`;
          });
        }
      });
    },
    { threshold: 0.3 }
  );
  document.querySelectorAll(".skills-section").forEach((el) => skillObserver.observe(el));

  const animateCount = (el) => {
    const target = Number(el.dataset.count);
    const suffix = el.dataset.suffix || "";
    const decimals = Number(el.dataset.decimals || 0);
    const duration = 1200;
    const start = performance.now();
    const tick = (now) => {
      const p = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - p, 3);
      const value = target * eased;
      el.textContent = `${value.toFixed(decimals)}${suffix}`;
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  };

  const statsObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          e.target.querySelectorAll(".stat-num").forEach(animateCount);
          statsObserver.unobserve(e.target);
        }
      });
    },
    { threshold: 0.4 }
  );
  const statsBar = document.querySelector(".stats-bar");
  if (statsBar) statsObserver.observe(statsBar);

  const navToggle = document.getElementById("navToggle");
  const navLinks = document.getElementById("navLinks");
  navToggle.addEventListener("click", () => navLinks.classList.toggle("open"));
  navLinks.querySelectorAll("a").forEach((a) => {
    a.addEventListener("click", () => navLinks.classList.remove("open"));
  });

  const navAnchors = [...navLinks.querySelectorAll("a")];
  const sections = navAnchors
    .map((a) => document.querySelector(a.getAttribute("href")))
    .filter(Boolean);
  const setActiveNav = () => {
    const y = window.scrollY + 120;
    let current = sections[0];
    sections.forEach((sec) => {
      if (sec.offsetTop <= y) current = sec;
    });
    navAnchors.forEach((a) => {
      a.classList.toggle("active", a.getAttribute("href") === `#${current.id}`);
    });
  };
  window.addEventListener("scroll", setActiveNav, { passive: true });
  setActiveNav();

  const form = document.getElementById("contactForm");
  const status = document.getElementById("formStatus");
  form.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    status.className = "form-status";
    status.textContent = "sending...";
    const payload = Object.fromEntries(new FormData(form).entries());
    try {
      const res = await fetch("/api/contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok || !data.ok) throw new Error(data.error || "failed");
      status.className = "form-status ok";
      status.textContent = "exit 0  —  message queued. I'll get back to you.";
      form.reset();
    } catch (err) {
      const to = "nguyenxxuanhieu.bd@gmail.com";
      const subject = encodeURIComponent(`Portfolio contact from ${payload.name || "visitor"}`);
      const body = encodeURIComponent(
        `${payload.message || ""}\n\n— ${payload.name || ""} <${payload.email || ""}>`
      );
      window.location.href = `mailto:${to}?subject=${subject}&body=${body}`;
      status.className = "form-status ok";
      status.textContent = "opening mail client → nguyenxxuanhieu.bd@gmail.com";
    }
  });
})();
