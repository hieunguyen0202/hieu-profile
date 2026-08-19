(() => {
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
