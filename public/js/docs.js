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
