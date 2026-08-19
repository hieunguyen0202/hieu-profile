(() => {
  const cursor = document.getElementById("cursor");
  const cursorRing = document.getElementById("cursorRing");
  if (cursor && cursorRing && window.matchMedia("(pointer: fine)").matches) {
    let mx = 0;
    let my = 0;
    let rx = 0;
    let ry = 0;
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
  if (canvas) {
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
  }

  const sidebar = document.getElementById("docsSidebar");
  const navEl = document.getElementById("docsNav");
  const root = sidebar?.dataset.docsRoot || "./";
  const active = sidebar?.dataset.active || "overview";

  const published = new Set(["overview", "01-gioi-thieu", "02-http", "03-burp"]);

  const item = (id, label) => {
    if (id === active) return `<li><a class="active" href="${root}${id === "overview" ? "" : `${id}/`}">${label}</a></li>`;
    if (published.has(id)) {
      return `<li><a href="${root}${id === "overview" ? "" : `${id}/`}">${label}</a></li>`;
    }
    return `<li><span class="soon">${label}</span></li>`;
  };

  const group = (title, open, children) => `
    <li class="group${open ? " open" : ""}">
      <button type="button">${title} <span class="chevron">▸</span></button>
      <ul class="nested">${children}</ul>
    </li>`;

  if (navEl) {
    const partIOpen = ["overview", "01-gioi-thieu", "02-http", "03-burp"].includes(active);
    navEl.innerHTML = [
      item("overview", "Overview"),
      group("Part I: Fundamentals", partIOpen, [
        item("01-gioi-thieu", "01. Giới thiệu"),
        item("02-http", "02. HTTP Fundamentals"),
        item("03-burp", "03. Burp Suite"),
      ].join("")),
      group("Part II: Auth &amp; Authorization", false, [
        item("04", "04. Authentication"),
        item("05", "05. Session Management"),
        item("06", "06. Access Control"),
        item("07", "07. OAuth 2.0"),
        item("08", "08. JWT"),
      ].join("")),
      group("Part III: Client-Side", false, [
        item("09", "09. CORS"),
        item("10", "10. CSRF"),
        item("11", "11. XSS"),
        item("22", "22. Clickjacking"),
      ].join("")),
      group("Part IV: Injection", false, [
        item("12", "12. SQL Injection"),
        item("13", "13. NoSQL Injection"),
        item("14", "14. Command Injection"),
        item("16", "16. XXE"),
        item("25", "25. SSTI"),
      ].join("")),
      group("Part V: Server-Side", false, [
        item("15", "15. SSRF"),
        item("17", "17. File Upload"),
        item("18", "18. Path Traversal"),
        item("19", "19. Open Redirect"),
        item("20", "20. Race Condition"),
        item("21", "21. Business Logic"),
        item("26", "26. Insecure Deserialization"),
      ].join("")),
      group("Part VI: Infra &amp; Protocols", false, [
        item("23", "23. Web Cache Poisoning"),
        item("24", "24. HTTP Request Smuggling"),
      ].join("")),
      group("Part VII: API &amp; Architecture", false, [
        item("27", "27. GraphQL Security"),
        item("28", "28. API Security"),
      ].join("")),
      group("Part VIII: DevOps Security", false, [
        item("29", "29. Kubernetes Security"),
        item("30", "30. CI/CD Security"),
        item("31", "31. Secrets Management"),
        item("32", "32. Cloud Security"),
        item("33", "33. Logging &amp; Detection"),
        item("34", "34. Incident Response"),
        item("35", "35. Checklist cho DevOps"),
      ].join("")),
      `<li><span class="soon">Appendix</span></li>`,
    ].join("");
  }

  const menuBtn = document.getElementById("docsMenuBtn");
  if (menuBtn && sidebar) {
    menuBtn.addEventListener("click", () => {
      sidebar.classList.toggle("open");
    });
  }

  document.querySelectorAll(".docs-nav .group > button").forEach((btn) => {
    btn.addEventListener("click", () => {
      btn.parentElement.classList.toggle("open");
    });
  });

  const tocLinks = [...document.querySelectorAll(".docs-toc nav a")];
  const headings = tocLinks
    .map((a) => document.querySelector(a.getAttribute("href")))
    .filter(Boolean);

  const setActiveToc = () => {
    const y = window.scrollY + 90;
    let current = headings[0];
    headings.forEach((h) => {
      if (h.offsetTop <= y) current = h;
    });
    tocLinks.forEach((a) => {
      a.classList.toggle("active", a.getAttribute("href") === `#${current.id}`);
    });
  };

  if (headings.length) {
    window.addEventListener("scroll", setActiveToc, { passive: true });
    setActiveToc();
  }
})();
