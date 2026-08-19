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

  const published = new Set([
    "overview", "01-gioi-thieu", "02-http", "03-burp",
    "04", "05", "06", "07", "08",
    "09", "10", "11", "22",
    "12", "13", "14", "16", "25",
    "15", "17", "18", "19", "20", "21", "26",
    "23", "24",
    "27", "28",
    "29", "30", "31", "32", "33", "34", "35",
    "appendix",
  ]);

  const PARTS = {
    I: ["overview", "01-gioi-thieu", "02-http", "03-burp"],
    II: ["04", "05", "06", "07", "08"],
    III: ["09", "10", "11", "22"],
    IV: ["12", "13", "14", "16", "25"],
    V: ["15", "17", "18", "19", "20", "21", "26"],
    VI: ["23", "24"],
    VII: ["27", "28"],
    VIII: ["29", "30", "31", "32", "33", "34", "35"],
  };

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

  if (navEl && sidebar?.dataset.nav === "cks") {
    const r = root;
    const cksItem = (id, label) => {
      const href = id === "exam" ? r : `${r}${id}/`;
      const cls = id === active || (id === "exam" && (active === "exam" || active === "overview")) ? "active" : "";
      return `<li><a class="${cls}" href="${href}">${label}</a></li>`;
    };
    const open = (ids) => ids.includes(active);
    navEl.innerHTML = [
      cksItem("exam", "CKS Exam"),
      group("Introduction", open(["introduction", "study-environment", "review-kubernetes", "review-containers"]), [
        cksItem("introduction", "Introduction"),
        cksItem("study-environment", "Study Environment"),
        cksItem("review-kubernetes", "Review Kubernetes"),
        cksItem("review-containers", "Review Containers"),
      ].join("")),
      group("Network", open(["network-security-policies", "ingress", "mtls", "cloud-platform-node-metadata", "control-access-gui-elements"]), [
        cksItem("network-security-policies", "Network Policies"),
        cksItem("ingress", "Ingress"),
        cksItem("mtls", "mTLS"),
        cksItem("cloud-platform-node-metadata", "Node metadata"),
        cksItem("control-access-gui-elements", "GUI access"),
      ].join("")),
      group("Hardening &amp; Security", open(["cis-benchmark", "attack-surface-reduction", "hash-verification"]), [
        cksItem("cis-benchmark", "CIS Benchmark"),
        cksItem("attack-surface-reduction", "Attack surface"),
        cksItem("hash-verification", "Hash verification"),
      ].join("")),
      group("RBAC", open(["rbac", "rbac-users", "service-accounts"]), [
        cksItem("rbac", "RBAC"),
        cksItem("rbac-users", "Users"),
        cksItem("service-accounts", "Service accounts"),
      ].join("")),
      group("API", open(["restrict-access", "secrets", "update-process"]), [
        cksItem("restrict-access", "Restrict API access"),
        cksItem("secrets", "Secrets"),
        cksItem("update-process", "Update process"),
      ].join("")),
      group("Container Runtime", open(["runtime-classes", "sandboxes", "security-context"]), [
        cksItem("runtime-classes", "RuntimeClasses"),
        cksItem("sandboxes", "Sandboxes"),
        cksItem("security-context", "Security context"),
      ].join("")),
      group("Supply Chain", open(["container-registries", "images-vulnerabilities", "security-images", "static-analysis-conftest", "static-analysis-kubesec", "pod-security-standards", "open-policy-agent"]), [
        cksItem("container-registries", "Registries"),
        cksItem("images-vulnerabilities", "Image vulnerabilities"),
        cksItem("security-images", "Secure images"),
        cksItem("static-analysis-conftest", "Conftest"),
        cksItem("static-analysis-kubesec", "Kubesec"),
        cksItem("pod-security-standards", "Pod Security Standards"),
        cksItem("open-policy-agent", "OPA"),
      ].join("")),
      group("Behavioral Analysis", open(["kernel-space-security", "falco-runtime-security", "container-immutability", "kubernetes-auditing"]), [
        cksItem("kernel-space-security", "Kernel space security"),
        cksItem("falco-runtime-security", "Falco runtime security"),
        cksItem("container-immutability", "Container immutability"),
        cksItem("kubernetes-auditing", "Kubernetes auditing"),
      ].join("")),
      cksItem("solved-questions", "CKS: Solved Questions"),
      cksItem("tips", "CKS Tips"),
    ].join("");
  } else if (navEl) {
    navEl.innerHTML = [
      item("overview", "Overview"),
      group("Part I: Fundamentals", PARTS.I.includes(active), [
        item("01-gioi-thieu", "01. Giới thiệu"),
        item("02-http", "02. HTTP Fundamentals"),
        item("03-burp", "03. Burp Suite"),
      ].join("")),
      group("Part II: Auth &amp; Authorization", PARTS.II.includes(active), [
        item("04", "04. Authentication"),
        item("05", "05. Session Management"),
        item("06", "06. Access Control"),
        item("07", "07. OAuth 2.0"),
        item("08", "08. JWT"),
      ].join("")),
      group("Part III: Client-Side", PARTS.III.includes(active), [
        item("09", "09. CORS"),
        item("10", "10. CSRF"),
        item("11", "11. XSS"),
        item("22", "22. Clickjacking"),
      ].join("")),
      group("Part IV: Injection", PARTS.IV.includes(active), [
        item("12", "12. SQL Injection"),
        item("13", "13. NoSQL Injection"),
        item("14", "14. Command Injection"),
        item("16", "16. XXE"),
        item("25", "25. SSTI"),
      ].join("")),
      group("Part V: Server-Side", PARTS.V.includes(active), [
        item("15", "15. SSRF"),
        item("17", "17. File Upload"),
        item("18", "18. Path Traversal"),
        item("19", "19. Open Redirect"),
        item("20", "20. Race Condition"),
        item("21", "21. Business Logic"),
        item("26", "26. Insecure Deserialization"),
      ].join("")),
      group("Part VI: Infra &amp; Protocols", PARTS.VI.includes(active), [
        item("23", "23. Web Cache Poisoning"),
        item("24", "24. HTTP Request Smuggling"),
      ].join("")),
      group("Part VII: API &amp; Architecture", PARTS.VII.includes(active), [
        item("27", "27. GraphQL Security"),
        item("28", "28. API Security"),
      ].join("")),
      group("Part VIII: DevOps Security", PARTS.VIII.includes(active), [
        item("29", "29. Kubernetes Security"),
        item("30", "30. CI/CD Security"),
        item("31", "31. Secrets Management"),
        item("32", "32. Cloud Security"),
        item("33", "33. Logging &amp; Detection"),
        item("34", "34. Incident Response"),
        item("35", "35. Checklist cho DevOps"),
      ].join("")),
      item("appendix", "Appendix"),
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
