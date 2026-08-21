#!/usr/bin/env python3
"""Build CKS docs pages from fetched source HTML in /tmp/cks-src."""
from __future__ import annotations
import html as htmlmod
import json
import re
from pathlib import Path

SRC = Path("/tmp/cks-src")
DST = Path(__file__).resolve().parents[1] / "public" / "blog" / "kubestronaut" / "cks"

ORDER = [
    "exam",
    "introduction",
    "study-environment",
    "review-kubernetes",
    "review-containers",
    "network-security-policies",
    "ingress",
    "mtls",
    "cloud-platform-node-metadata",
    "control-access-gui-elements",
    "cis-benchmark",
    "attack-surface-reduction",
    "hash-verification",
    "rbac",
    "rbac-users",
    "service-accounts",
    "restrict-access",
    "secrets",
    "update-process",
    "runtime-classes",
    "sandboxes",
    "security-context",
    "container-registries",
    "images-vulnerabilities",
    "security-images",
    "static-analysis-conftest",
    "static-analysis-kubesec",
    "pod-security-standards",
    "open-policy-agent",
    "kernel-space-security",
    "falco-runtime-security",
    "container-immutability",
    "kubernetes-auditing",
    "solved-questions",
    "tips",
    "real-world-exam",
]

CRUMB = {
    "exam": "CKS Exam",
    "introduction": "Introduction",
    "study-environment": "Study Environment",
    "review-kubernetes": "Review Kubernetes",
    "review-containers": "Review Containers",
    "network-security-policies": "Network Policies",
    "ingress": "Ingress",
    "mtls": "mTLS",
    "cloud-platform-node-metadata": "Node metadata",
    "control-access-gui-elements": "GUI access",
    "cis-benchmark": "CIS Benchmark",
    "attack-surface-reduction": "Attack surface",
    "hash-verification": "Hash verification",
    "rbac": "RBAC",
    "rbac-users": "RBAC users",
    "service-accounts": "Service accounts",
    "restrict-access": "Restrict API",
    "secrets": "Secrets",
    "update-process": "Update process",
    "runtime-classes": "RuntimeClasses",
    "sandboxes": "Sandboxes",
    "security-context": "Security context",
    "container-registries": "Registries",
    "images-vulnerabilities": "Image vulns",
    "security-images": "Secure images",
    "static-analysis-conftest": "Conftest",
    "static-analysis-kubesec": "Kubesec",
    "pod-security-standards": "PSS",
    "open-policy-agent": "OPA",
    "kernel-space-security": "Kernel space",
    "falco-runtime-security": "Falco",
    "container-immutability": "Immutability",
    "kubernetes-auditing": "Auditing",
    "solved-questions": "Solved questions",
    "tips": "CKS Tips",
    "real-world-exam": "CKS Real World exam",
}

ASSET = "https://devsecops.puziol.com.br"


def strip_tail(body: str) -> str:
    """Remove Docusaurus pagination / TOC leftovers that break our layout."""
    body = re.sub(r"</div></article>.*", "", body, flags=re.S)
    body = re.sub(r'<nav class="(?:docusaurus-mt-lg )?pagination-nav".*', "", body, flags=re.S)
    body = re.sub(r'<div class="tableOfContents[^"]*".*', "", body, flags=re.S)
    body = re.sub(r"</main>.*", "", body, flags=re.S)
    return body.strip()


def clean(body: str, slug: str) -> str:
    body = strip_tail(body)
    body = re.sub(r'<a\b[^>]*class="hash-link"[^>]*>.*?</a>', "", body)
    body = re.sub(
        r'<a href="#[^"]*"[^>]*aria-label="Direct link[^"]*"[^>]*>\s*​?\s*</a>',
        "",
        body,
    )
    body = re.sub(r' translate="no"', "", body)
    body = body.replace('<!-- -->', "")
    body = re.sub(r' class="anchor[^"]*"', "", body)
    body = re.sub(r' class=""', "", body)
    body = re.sub(r'src="(/en/assets/[^"]+)"', rf'src="{ASSET}\1"', body)
    body = re.sub(r'src="(/assets/[^"]+)"', rf'src="{ASSET}\1"', body)

    def rel(m):
        path = m.group(1).rstrip("/")
        if path.startswith("solved-questions/"):
            return f'href="{ASSET}/en/kubernetes/cks/{path}" target="_blank" rel="noopener noreferrer"'
        last = path.split("/")[-1]
        if last in ("cks", "exam"):
            target = "exam"
        else:
            target = last
        if slug == "exam":
            return 'href="./"' if target == "exam" else f'href="{target}/"'
        return 'href="../"' if target == "exam" else f'href="../{target}/"'

    body = re.sub(r'href="(?:https://devsecops\.puziol\.com\.br)?/en/kubernetes/cks/([^"]+)"', rel, body)
    body = re.sub(r'href="/kubernetes/cks/([^"]+)"', rel, body)
    return body


def toc(body: str) -> str:
    items = []
    for m in re.finditer(r'<h([23])[^>]*id="([^"]+)"[^>]*>(.*?)</h\1>', body, re.S):
        depth, hid, title = m.group(1), m.group(2), re.sub("<[^>]+>", "", m.group(3)).strip()
        title = htmlmod.unescape(title).replace("​", "").strip()
        if not title:
            continue
        cls = ' class="depth-3"' if depth == "3" else ""
        items.append(f'        <a{cls} href="#{hid}">{title}</a>')
    return "\n".join(items) if items else '        <a href="#top">On this page</a>'


def wrap(slug: str, title: str, body: str) -> str:
    nested = slug != "exam"
    depth = 0
    if nested:
        depth = slug.count("/") + 1  # flat slugs only
    home = "../" * (depth + 3)
    css = f"{home}css/docs.css"
    js = f"{home}js/docs.js"
    fav = f"{home}favicon.svg"
    root = "../" * depth if depth else "./"
    roadmap = "../" * (depth + 1)
    i = ORDER.index(slug)
    prev = ORDER[i - 1] if i else None
    nxt = ORDER[i + 1] if i < len(ORDER) - 1 else None

    def href(other):
        if not nested:
            return "./" if other == "exam" else f"{other}/"
        return "../" if other == "exam" else f"../{other}/"

    pager_l = (
        f'<a href="{href(prev)}">Previous · {CRUMB[prev]}</a>'
        if prev
        else '<a href="../">← Kubestronaut</a>'
    )
    pager_r = (
        f'<a href="{href(nxt)}">Next · {CRUMB[nxt]}</a>'
        if nxt
        else '<a href="../">Kubestronaut →</a>'
    )
    crumb = CRUMB[slug]
    body = f'<div id="top"></div>\n{body}'
    tabs = [("cka", "CKA"), ("ckad", "CKAD"), ("cks", "CKS")]
    tab_html = "".join(
        f'<a href="{roadmap}{cid}/" class="{"active" if cid == "cks" else ""}">{label}</a>'
        for cid, label in tabs
    )
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{htmlmod.escape(title)} — Hieu Nguyen</title>
  <meta name="description" content="{htmlmod.escape(title)} — Kubestronaut roadmap.">
  <link rel="icon" href="{fav}" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{css}">
</head>
<body class="docs">
  <div class="cursor" id="cursor"></div>
  <div class="cursor-ring" id="cursorRing"></div>
  <canvas id="matrix-canvas"></canvas>
  <div class="grid-bg"></div>
  <header class="docs-topbar">
    <button class="docs-menu-btn" id="docsMenuBtn" type="button">menu</button>
    <a class="docs-brand" href="{home}"><span>✦</span> The Quiet Corner <span>✦</span></a>
    <nav class="docs-series">
      <a href="{home}blog/web-security/">DevSecOps</a>
      <a class="active" href="{roadmap}">Kubestronaut</a>
      <a href="{home}blog/english/">English</a>
    </nav>
    <nav class="docs-cert-tabs">{tab_html}</nav>
    <span class="docs-topbar-spacer"></span>
    <a class="docs-top-link" href="{home}#blogs">blogs</a>
  </header>
  <div class="docs-shell">
    <aside class="docs-sidebar" id="docsSidebar" data-nav="kubestronaut" data-cert="cks" data-docs-root="{root}" data-active="{slug}">
      <div class="docs-nav-label">CKS</div>
      <ul class="docs-nav" id="docsNav"></ul>
    </aside>
    <article class="docs-main">
      <div class="docs-breadcrumb">
        <a href="{home}">Home</a>
        <span>›</span>
        <a href="{home}#blogs">Blogs</a>
        <span>›</span>
        <a href="{roadmap}">Kubestronaut</a>
        <span>›</span>
        <a href="{href("exam")}">CKS</a>
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
  <script src="{js}"></script>
</body>
</html>
'''


SOLVED = [
    ("question-1-contexts", "Q1 — Contexts"),
    ("question-2-runtime-security-falco", "Q2 — Falco"),
    ("question-3-apiserver-security", "Q3 — API server"),
    ("question-4-pod-security-standard", "Q4 — Pod Security Standard"),
    ("question-5-cis-benchmark", "Q5 — CIS benchmark"),
    ("question-6-verify-platform-binaries", "Q6 — Verify binaries"),
    ("question-7-open-policy-agent", "Q7 — OPA"),
    ("question-8-secure-kubernetes-dashboard", "Q8 — Dashboard"),
    ("question-9-apparmor-profile", "Q9 — AppArmor"),
    ("question-10-gvisor-runtime-sandbox", "Q10 — gVisor"),
    ("question-11-secrets-in-etcd", "Q11 — Secrets in etcd"),
    ("question-12-hack-secrets", "Q12 — Secret access"),
    ("question-13-restrict-access-metadata-server", "Q13 — Metadata server"),
    ("question-14-syscall-activity", "Q14 — Syscall activity"),
    ("question-15-configure-tls-ingress", "Q15 — TLS Ingress"),
    ("question-16-docker-image-attack-surface", "Q16 — Image attack surface"),
    ("question-17-audit-log-policy", "Q17 — Audit policy"),
    ("question-18-investigate-break-in-audit-log", "Q18 — Investigate audit log"),
    ("question-19-immutable-root-filesystem", "Q19 — Immutable rootfs"),
    ("question-20-update-kubernetes", "Q20 — Update Kubernetes"),
    ("question-21-image-vulnerability-scanning", "Q21 — Image scanning"),
    ("question-22-manual-static-security-analysis", "Q22 — Static analysis"),
    ("question-23-rbac-security-configuration", "Q23 — RBAC"),
    ("question-24-opa-gatekeeper-policy-extension", "Q24 — Gatekeeper"),
    ("question-25-malicious-process-investigation", "Q25 — Malicious process"),
    ("question-31-critical-vulnerabilities-trivy", "Q31 — Trivy"),
    ("question-32-rbac-serviceaccount-configuration", "Q32 — ServiceAccount RBAC"),
    ("question-33-secret-volume-mount-configuration", "Q33 — Secret volume"),
    ("question-34-seccomp-profile-configuration", "Q34 — seccomp"),
    ("question-35-kube-bench-security-hardening", "Q35 — kube-bench"),
    ("question-36-kubernetes-audit-configuration", "Q36 — Audit config"),
    ("question-37-imagepolicywebhook-admission-controller", "Q37 — ImagePolicyWebhook"),
    ("question-38-pod-security-policy-configuration", "Q38 — PSS/PSP"),
    ("question-41-cks-challenge-1-complete-security-setup", "Challenge 1"),
    ("question-42-cks-challenge-2-multi-environment-security", "Challenge 2"),
    ("question-43-cks-challenge-3-kube-bench-cluster-hardening", "Challenge 3"),
    ("question-44-cks-challenge-4-security-monitoring-incident-response", "Challenge 4"),
]


def solved_body() -> str:
    lis = "\n".join(
        f'<li><a href="https://devsecops.puziol.com.br/en/kubernetes/cks/solved-questions/{slug}/" target="_blank" rel="noopener">{htmlmod.escape(label)}</a></li>'
        for slug, label in SOLVED
    )
    return f"""<h1>CKS: Solved Questions</h1>
<p>Practice tasks from the same CKS track (Killer Shell–style labs). Work them on <strong>your</strong> lab cluster — not on production.</p>
<p>Full write-ups live on the source pages (open in a new tab):</p>
<ul>
{lis}
</ul>
<p>Map each task back to the notes in this series (NetworkPolicy, Falco, audit, Trivy, PSS, OPA, AppArmor, gVisor, Ingress TLS).</p>
"""


def main():
    DST.mkdir(parents=True, exist_ok=True)
    meta = {m["slug"]: m for m in json.loads((SRC / "meta.json").read_text())}
    for slug in ORDER:
        raw = (SRC / f"{slug}.html").read_text(encoding="utf-8")
        body = clean(raw, slug)
        title = meta[slug]["title"]
        if slug == "solved-questions" and "<h1" not in body:
            title = "CKS: Solved Questions"
            body = "<h1>CKS: Solved Questions</h1>\n" + body
        page = wrap(slug, title, body)
        if slug == "exam":
            (DST / "index.html").write_text(page, encoding="utf-8")
        else:
            d = DST / slug
            d.mkdir(exist_ok=True)
            (d / "index.html").write_text(page, encoding="utf-8")
        print("wrote", slug, len(page))


if __name__ == "__main__":
    main()
