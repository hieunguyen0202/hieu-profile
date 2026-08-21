#!/usr/bin/env python3
"""Fetch and build CKA / CKAD pages verbatim from devsecops.puziol.com.br."""
from __future__ import annotations

import html as htmlmod
import json
import re
import time
import urllib.request
from pathlib import Path
from urllib.error import HTTPError

ASSET = "https://devsecops.puziol.com.br"
ROOT = Path(__file__).resolve().parents[1] / "public" / "blog" / "kubestronaut"

# (local path under cert dir, source URL path after /en/kubernetes/{cert}/)
# empty path = exam index at /en/kubernetes/{cert}

CKA_PAGES: list[tuple[str, str]] = [
    ("", "exam"),  # /en/kubernetes/cka
    ("review", "review"),
    ("cluster-architecture", "cluster-architecture"),
    ("design-cluster", "design-cluster"),
    ("etcd", "etcd"),
    ("etcd-ha", "etcd-ha"),
    ("kube-api-server", "kube-api-server"),
    ("kube-controller-manager", "kube-controller-manager"),
    ("kube-scheduler", "kube-scheduler"),
    ("kube-proxy", "kube-proxy"),
    ("static-pods", "static-pods"),
    ("labels-selectors", "labels-selectors"),
    ("manual-scheduling", "manual-scheduling"),
    ("multiple-schedulers", "multiple-schedulers"),
    ("node-selector-affinity", "node-selector-affinity"),
    ("taint-tolerations", "taint-tolerations"),
    ("resource-requirements-limits", "resource-requirements-limits"),
    ("kubernetes-logs", "kubernetes-logs"),
    ("monitoring-cluster", "monitoring-cluster"),
    ("init-containers-multi-containers", "init-containers-multi-containers"),
    ("liveness-readiness-startup-probes", "liveness-readiness-startup-probes"),
    ("rolling-updates-rollbacks", "rolling-updates-rollbacks"),
    ("configmap-envs", "configmap-envs"),
    ("secrets", "secrets"),
    ("container-entrypoint-command", "container-entrypoint-command"),
    ("kubeadm-installation", "kubeadm-installation"),
    ("download-kubernetes-binaries", "download-kubernetes-binaries"),
    ("cluster-maintenance/backup-restore", "cluster-maintenance/backup-restore"),
    ("cluster-maintenance/cluster-update-process", "cluster-maintenance/cluster-update-process"),
    ("cluster-maintenance/create-cluster-kubeadm", "cluster-maintenance/create-cluster-kubeadm"),
    ("cluster-maintenance/os-upgrade", "cluster-maintenance/os-upgrade"),
    ("cluster-maintenance/releases", "cluster-maintenance/releases"),
    ("security-primitives", "security-primitives"),
    ("authentication", "authentication"),
    ("authorization", "authorization"),
    ("api-groups", "api-groups"),
    ("api-certificates", "api-certificates"),
    ("service-accounts", "service-accounts"),
    ("kubeconfig", "kubeconfig"),
    ("kubectx-kubens", "kubectx-kubens"),
    ("tls-fundamentals", "tls-fundamentals"),
    ("kubernetes-tls", "kubernetes-tls"),
    ("network-policies", "network-policies"),
    ("security-context", "security-context"),
    ("image-security", "image-security"),
    ("storage/conceitos-armazenamento", "storage/conceitos-armazenamento"),
    ("storage/volumes", "storage/volumes"),
    ("storage/persistent-volume", "storage/persistent-volume"),
    ("storage/storage-class", "storage/storage-class"),
    ("storage/container-storage-interface", "storage/container-storage-interface"),
    ("networking-pre-requisites", "networking-pre-requisites"),
    ("network-namespaces", "network-namespaces"),
    ("docker-networking", "docker-networking"),
    ("cluster-network", "cluster-network"),
    ("pod-network-interface", "pod-network-interface"),
    ("container-network-interface", "container-network-interface"),
    ("coredns", "coredns"),
    ("dns-basics", "dns-basics"),
    ("dns-kubernetes", "dns-kubernetes"),
    ("service-network", "service-network"),
    ("ingress", "ingress"),
    ("troubleshooting/sequence-check-failure-application", "troubleshooting/sequence-check-failure-application"),
    ("troubleshooting/sequence-check-failure-control-plane", "troubleshooting/sequence-check-failure-control-plane"),
    ("troubleshooting/sequence-check-failure-nodes", "troubleshooting/sequence-check-failure-nodes"),
    ("troubleshooting/network-troubleshooting", "troubleshooting/network-troubleshooting"),
    ("troubleshooting/kubectl-advanced-commands", "troubleshooting/kubectl-advanced-commands"),
    ("hardway-install/proposal", "hardway-install/proposal"),
    ("hardway-install/preparing-required-files", "hardway-install/preparing-required-files"),
    ("hardway-install/bootstraps", "hardway-install/bootstraps"),
    ("tips", "tips"),
    ("cheats", "cheats"),
    ("solved-questions", "category/cka-questões-resolvidas"),
]

CKAD_PAGES: list[tuple[str, str]] = [
    ("", "exam"),
    ("recap-kubernetes", "recap-kubernetes"),
    ("configuration-from-cka", "configuration-from-cka"),
    ("containers-images", "containers-images"),
    ("deployments", "deployments"),
    ("jobs-cronjobs", "jobs-cronjobs"),
    ("multi-containers-pods", "multi-containers-pods"),
    ("readiness-liveness-startup-probes", "readiness-liveness-startup-probes"),
    ("logs-and-monitoring", "logs-and-monitoring"),
    ("services-networking", "services-networking"),
    ("volumes", "volumes"),
    ("statefulset", "statefulset"),
    ("custom-resources", "custom-resources"),
    ("api-version", "api-version"),
    ("api-depreciations", "api-depreciations"),
    ("admission-controllers", "admission-controllers"),
    ("security-roadmap", "security-roadmap"),
    ("helm-basics", "helm-basics"),
]

CKA_NAV = [
    ("exam", "Exam"),
    ("group:concepts", "CKA: Conceitos principais", [
        "review", "cluster-architecture", "design-cluster", "etcd", "etcd-ha",
        "kube-api-server", "kube-controller-manager", "kube-scheduler", "kube-proxy",
        "static-pods", "labels-selectors",
    ]),
    ("group:scheduling", "Scheduling", [
        "manual-scheduling", "multiple-schedulers", "node-selector-affinity",
        "taint-tolerations", "resource-requirements-limits",
    ]),
    ("group:logging", "Logging Monitoring", [
        "kubernetes-logs", "monitoring-cluster",
    ]),
    ("group:alm", "Application Lifecycle Management", [
        "init-containers-multi-containers", "liveness-readiness-startup-probes",
        "rolling-updates-rollbacks", "configmap-envs", "secrets", "container-entrypoint-command",
    ]),
    ("group:maintenance", "Cluster Maintenance", [
        "cluster-maintenance/backup-restore", "cluster-maintenance/cluster-update-process",
        "cluster-maintenance/create-cluster-kubeadm", "cluster-maintenance/os-upgrade",
        "cluster-maintenance/releases",
    ]),
    ("group:security", "CKA: Security", [
        "security-primitives", "authentication", "authorization", "api-groups",
        "api-certificates", "service-accounts", "kubeconfig", "kubectx-kubens",
        "tls-fundamentals", "kubernetes-tls", "network-policies", "security-context",
        "image-security",
    ]),
    ("group:storage", "Storage", [
        "storage/conceitos-armazenamento", "storage/volumes", "storage/persistent-volume",
        "storage/storage-class", "storage/container-storage-interface",
    ]),
    ("group:networking", "Networking", [
        "networking-pre-requisites", "network-namespaces", "docker-networking",
        "cluster-network", "pod-network-interface", "container-network-interface",
        "coredns", "dns-basics", "dns-kubernetes", "service-network", "ingress",
    ]),
    ("group:install", "Installation Configuration Validation", [
        "kubeadm-installation", "download-kubernetes-binaries",
    ]),
    ("group:troubleshoot", "Troubleshooting", [
        "troubleshooting/sequence-check-failure-application",
        "troubleshooting/sequence-check-failure-control-plane",
        "troubleshooting/sequence-check-failure-nodes",
        "troubleshooting/network-troubleshooting",
        "troubleshooting/kubectl-advanced-commands",
    ]),
    ("group:hardway", "Hardway Installation", [
        "hardway-install/proposal", "hardway-install/preparing-required-files",
        "hardway-install/bootstraps",
    ]),
    ("tips", "Tips"),
    ("cheats", "Cheats"),
    ("solved-questions", "CKA: Solved Questions"),
]

CKAD_NAV = [
    ("exam", "CKAD Exam"),
    ("group:concepts", "CKAD: Conceitos principais", [
        "recap-kubernetes", "configuration-from-cka", "containers-images",
    ]),
    ("group:config", "Configuration", [
        "deployments", "jobs-cronjobs", "configmap-envs" if False else "configuration-from-cka",
    ]),
    ("group:multi", "Multi Containers Pods", ["multi-containers-pods"]),
    ("group:obs", "Observability", [
        "readiness-liveness-startup-probes", "logs-and-monitoring",
    ]),
    ("group:pod", "Pod Design", ["statefulset", "custom-resources"]),
    ("group:net", "Services & Networking", ["services-networking"]),
    ("group:vol", "Volumes", ["volumes"]),
    ("group:sec", "CKAD: Security", [
        "api-version", "api-depreciations", "admission-controllers", "security-roadmap",
    ]),
    ("group:helm", "CKAD: Helm", ["helm-basics"]),
]

# fix CKAD config group - remove duplicate
CKAD_NAV = [
    ("exam", "CKAD Exam"),
    ("group:concepts", "CKAD: Conceitos principais", [
        "recap-kubernetes", "configuration-from-cka", "containers-images",
    ]),
    ("group:config", "Configuration", ["deployments", "jobs-cronjobs"]),
    ("group:multi", "Multi Containers Pods", ["multi-containers-pods"]),
    ("group:obs", "Observability", [
        "readiness-liveness-startup-probes", "logs-and-monitoring",
    ]),
    ("group:pod", "Pod Design", ["statefulset", "custom-resources"]),
    ("group:net", "Services & Networking", ["services-networking"]),
    ("group:vol", "Volumes", ["volumes"]),
    ("group:sec", "CKAD: Security", [
        "api-version", "api-depreciations", "admission-controllers", "security-roadmap",
    ]),
    ("group:helm", "CKAD: Helm", ["helm-basics"]),
]


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; docs-import/1.0)"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read().decode("utf-8", "replace")


def extract_body(html: str) -> str:
    m = re.search(
        r'<div class="theme-doc-markdown markdown"[^>]*>(.*?)(?=<nav class="pagination-nav"|<footer )',
        html,
        re.S,
    )
    if m:
        return m.group(1)
    m = re.search(r'<section class="row">(.*)</section>', html, re.S)
    if m:
        return m.group(1)
    m = re.search(r'<main[^>]*>(.*?)</main>', html, re.S)
    return m.group(1) if m else ""


def strip_tail(body: str) -> str:
    body = re.sub(r"</div></article>.*", "", body, flags=re.S)
    body = re.sub(r'<nav class="pagination-nav".*', "", body, flags=re.S)
    body = re.sub(r'<div class="tableOfContents[^"]*".*', "", body, flags=re.S)
    return body.strip()


def flatten_code(body: str) -> str:
    def one(m: re.Match) -> str:
        block = m.group(0)
        lang_m = re.search(r"language-([a-zA-Z0-9_+-]+)", block)
        lang = lang_m.group(1) if lang_m else ""
        pre_m = re.search(r"<pre[^>]*>(.*?)</pre>", block, re.S)
        inner = pre_m.group(1) if pre_m else block
        inner = inner.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
        inner = re.sub(r"</?span[^>]*>", "", inner)
        inner = re.sub(r"</?code[^>]*>", "", inner)
        text = htmlmod.unescape(re.sub(r"<[^>]+>", "", inner)).replace("\xa0", " ")
        cls = f' class="language-{lang}"' if lang else ""
        return f"<pre><code{cls}>{htmlmod.escape(text.rstrip())}\n</code></pre>"

    return re.sub(
        r'<div class="language-[^"]*codeBlockContainer[^"]*"[\s\S]*?</div>\s*</div>',
        one,
        body,
    )


def clean(body: str, cert: str, local_path: str) -> str:
    body = re.sub(r'<a\b[^>]*class="hash-link"[^>]*>.*?</a>', "", body)
    body = re.sub(r' translate="no"', "", body)
    body = body.replace("<!-- -->", "")
    body = re.sub(r' class="anchor[^"]*"', "", body)
    body = re.sub(r' class=""', "", body)
    body = flatten_code(body)
    body = re.sub(r'src="(/en/assets/[^"]+)"', rf'src="{ASSET}\1"', body)
    body = re.sub(r'src="(/assets/[^"]+)"', rf'src="{ASSET}\1"', body)

    depth = len(local_path.split("/")) if local_path else 0
    prefix = "../" * (depth + 1) if depth else "./"

    def rel(m: re.Match) -> str:
        raw = m.group(1)
        frag = ""
        if "#" in raw:
            raw, frag = raw.split("#", 1)
            frag = "#" + frag
        raw = raw.rstrip("/")
        if raw.startswith("solved-questions/") or raw.startswith("question"):
            return f'href="{ASSET}/en/kubernetes/{cert}/{raw}{frag}" target="_blank" rel="noopener noreferrer"'
        if raw.endswith(f"/{cert}") or raw == f"/en/kubernetes/{cert}":
            return f'href="{prefix if depth else "./"}{frag}"'
        if f"/kubernetes/{cert}/" in raw or raw.startswith(cert + "/"):
            sub = raw.split(f"/{cert}/", 1)[-1] if f"/{cert}/" in raw else raw.replace(cert + "/", "")
            if not sub:
                return f'href="{prefix if depth else "./"}{frag}"'
            href = f"{'../' * depth}{sub}/" if depth else f"{sub}/"
            return f'href="{href}{frag}"'
        return f'href="{ASSET}{raw}{frag}"'

    body = re.sub(r'href="(?:https://devsecops\.puziol\.com\.br)?(/en/kubernetes/[^"]+)"', rel, body)
    body = re.sub(rf'href="/kubernetes/{cert}/([^"]+)"', rel, body)
    return body


def toc(body: str) -> str:
    items = []
    for m in re.finditer(r"<h([23])[^>]*id=\"([^\"]+)\"[^>]*>(.*?)</h\1>", body, re.S):
        depth, hid, title = m.group(1), m.group(2), re.sub("<[^>]+>", "", m.group(3)).strip()
        title = htmlmod.unescape(title).replace("\u200b", "").strip()
        if not title:
            continue
        cls = ' class="depth-3"' if depth == "3" else ""
        items.append(f'        <a{cls} href="#{hid}">{htmlmod.escape(title)}</a>')
    return "\n".join(items) if items else '        <a href="#top">On this page</a>'


def home_prefix(local_path: str) -> str:
    depth = len(local_path.split("/")) if local_path else 0
    return "../" * (depth + 3)


def cert_prefix(local_path: str) -> str:
    depth = len(local_path.split("/")) if local_path else 0
    return "../" * depth if depth else "./"


def sibling_cert_href(local_path: str, target: str) -> str:
    depth = len(local_path.split("/")) if local_path else 0
    return "../" * (depth + 1) + target + "/"


def page_href(from_path: str, to_path: str) -> str:
    """Relative href between two pages under the same cert root."""
    import os

    cur = from_path if from_path else "."
    tgt = to_path if to_path else "."
    rel = os.path.relpath(tgt, start=cur).replace("\\", "/")
    if rel == ".":
        return "./"
    return rel + "/"


def pager_links(cert: str, local_path: str, pages: list[tuple[str, str]], titles: dict[str, str]) -> tuple[str, str]:
    order = [p for p, _ in pages]
    i = order.index(local_path)
    prev = order[i - 1] if i else None
    nxt = order[i + 1] if i < len(order) - 1 else None

    def label(path: str) -> str:
        t = titles.get(path) or (path.split("/")[-1].replace("-", " ").title() if path else f"{cert.upper()} Exam")
        if len(t) > 42:
            t = path.split("/")[-1].replace("-", " ").title() if path else f"{cert.upper()} Exam"
        return htmlmod.escape(t)

    if prev is None:
        left = f'<a href="{page_href(local_path, "")}">← {cert.upper()} Exam</a>' if local_path else f'<a href="../">← Kubestronaut</a>'
    else:
        left = f'<a href="{page_href(local_path, prev)}">Previous · {label(prev)}</a>'

    if nxt is None:
        right = f'<a href="../">Kubestronaut →</a>'
    else:
        right = f'<a href="{page_href(local_path, nxt)}">Next · {label(nxt)}</a>'
    return left, right


def wrap(
    cert: str,
    local_path: str,
    title: str,
    crumb: str,
    body: str,
    active_slug: str,
    pager_l: str = "",
    pager_r: str = "",
) -> str:
    home = home_prefix(local_path)
    depth = len(local_path.split("/")) if local_path else 0
    css = f"{home}css/docs.css"
    js = f"{home}js/docs.js"
    fav = f"{home}favicon.svg"
    docs_root = cert_prefix(local_path)
    cert_name = cert.upper()
    tabs = [("cka", "CKA"), ("ckad", "CKAD"), ("cks", "CKS")]
    tab_html = "".join(
        f'<a href="{sibling_cert_href(local_path, cid)}" class="{"active" if cid == cert else ""}">{label}</a>'
        for cid, label in tabs
    )
    roadmap_href = sibling_cert_href(local_path, "..").rstrip("/") + "/" if depth else "../"
    # sibling_cert_href(..., "..") from cka/ -> ../ which is kubestronaut/
    roadmap_href = "../" * (depth + 1) if cert else "../"
    body = f'<div id="top"></div>\n{body}'
    return f"""<!DOCTYPE html>
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
    <a class="docs-brand" href="{home}">i'm<span>.hieu</span></a>
    <nav class="docs-series">
      <a href="{home}blog/web-security/">DevSecOps</a>
      <a class="active" href="{roadmap_href}">Kubestronaut</a>
      <a href="{home}blog/english/">English</a>
    </nav>
    <nav class="docs-cert-tabs">{tab_html}</nav>
    <span class="docs-topbar-spacer"></span>
    <a class="docs-top-link" href="{home}#blogs">blogs</a>
  </header>
  <div class="docs-shell">
    <aside class="docs-sidebar" id="docsSidebar" data-nav="kubestronaut" data-cert="{cert}" data-docs-root="{docs_root}" data-active="{active_slug}">
      <div class="docs-nav-label">{cert_name}</div>
      <ul class="docs-nav" id="docsNav"></ul>
    </aside>
    <article class="docs-main">
      <div class="docs-breadcrumb">
        <a href="{home}">Home</a>
        <span>›</span>
        <a href="{home}#blogs">Blogs</a>
        <span>›</span>
        <a href="{roadmap_href}">Kubestronaut</a>
        <span>›</span>
        <a href="{cert_prefix(local_path)}">{cert_name}</a>
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
"""


def source_url(cert: str, src: str) -> str:
    if src.startswith("category/"):
        from urllib.parse import quote
        cat = src.split("/", 1)[1]
        return f"{ASSET}/en/category/{quote(cat, safe='')}"
    if src == "exam":
        return f"{ASSET}/en/kubernetes/{cert}"
    return f"{ASSET}/en/kubernetes/{cert}/{src}"


def slug_from_path(local_path: str) -> str:
    return local_path.replace("/", "-") if local_path else "exam"


def download_cert(cert: str, pages: list[tuple[str, str]]) -> None:
    cache = Path(f"/tmp/{cert}-src")
    cache.mkdir(parents=True, exist_ok=True)
    meta = []
    for local_path, src in pages:
        url = source_url(cert, src)
        try:
            html = fetch(url)
        except HTTPError as e:
            print("FAIL", cert, local_path, url, e.code)
            continue
        body = extract_body(html)
        body = strip_tail(body)
        if not body.strip():
            print("EMPTY", cert, local_path, url)
            continue
        if src.startswith("category/") and "<h1" not in body:
            title = "CKA: Solved Questions" if cert == "cka" else crumb_from_src(src)
            body = f"<h1>{title}</h1>\n{body}"
        title_m = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
        title = re.sub(r"<[^>]+>", "", title_m.group(1)).strip() if title_m else local_path or "Exam"
        slug = slug_from_path(local_path)
        fname = f"{slug}.html" if local_path else "exam.html"
        (cache / fname).write_text(body, encoding="utf-8")
        meta.append({"local_path": local_path, "slug": slug, "title": title, "url": url, "chars": len(body)})
        print(f"{cert:4} {local_path or 'exam':45} {len(body):7} {title[:55]}")
        time.sleep(0.1)
    (cache / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")


def crumb_from_src(src: str) -> str:
    return src.split("/")[-1].replace("-", " ").title()


def build_cert(cert: str, pages: list[tuple[str, str]]) -> None:
    cache = Path(f"/tmp/{cert}-src")
    meta = {m["local_path"]: m for m in json.loads((cache / "meta.json").read_text())}
    titles = {lp: meta[lp]["title"] for lp in meta}
    dst_root = ROOT / cert
    for local_path, src in pages:
        if local_path not in meta:
            continue
        slug = slug_from_path(local_path)
        fname = f"{slug}.html" if local_path else "exam.html"
        raw = (cache / fname).read_text(encoding="utf-8")
        body = strip_tail(clean(raw, cert, local_path))
        title = meta[local_path]["title"]
        crumb = title if len(title) < 48 else (local_path.split("/")[-1] if local_path else "Exam")
        active_slug = local_path or "exam"
        pager_l, pager_r = pager_links(cert, local_path, pages, titles)
        page = wrap(cert, local_path, title, crumb, body, active_slug, pager_l, pager_r)
        out = dst_root / local_path if local_path else dst_root
        out.mkdir(parents=True, exist_ok=True)
        (out / "index.html").write_text(page, encoding="utf-8")
        print("wrote", cert, local_path or "exam", len(page))


def write_hub() -> None:
    page = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Kubestronaut Roadmap — Hieu Nguyen</title>
  <meta name="description" content="Kubestronaut path: KCNA → CKA → CKAD → KCSA → CKS study notes.">
  <link rel="icon" href="../../favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../../css/docs.css">
</head>
<body class="docs">
  <div class="cursor" id="cursor"></div>
  <div class="cursor-ring" id="cursorRing"></div>
  <canvas id="matrix-canvas"></canvas>
  <div class="grid-bg"></div>
  <header class="docs-topbar">
    <button class="docs-menu-btn" id="docsMenuBtn" type="button">menu</button>
    <a class="docs-brand" href="../../">i'm<span>.hieu</span></a>
    <nav class="docs-series">
      <a href="../web-security/">DevSecOps</a>
      <a class="active" href="./">Kubestronaut</a>
      <a href="../english/">English</a>
    </nav>
    <span class="docs-topbar-spacer"></span>
    <a class="docs-top-link" href="../../#blogs">blogs</a>
  </header>
  <div class="docs-shell-hub">
    <article class="docs-main">
      <div class="docs-breadcrumb">
        <a href="../../">Home</a>
        <span>›</span>
        <a href="../../#blogs">Blogs</a>
        <span>›</span>
        <span>Kubestronaut</span>
      </div>
      <h1>Kubestronaut Roadmap</h1>
      <p class="lede">KCNA → CKA → CKAD → KCSA → CKS — the certification path, in order.</p>
      <div class="docs-meta">
        <span><strong>Track:</strong> 5 certs</span>
        <span><strong>Ready:</strong> CKA · CKAD · CKS</span>
        <span><strong>Soon:</strong> KCNA · KCSA</span>
      </div>

      <div class="cert-roadmap">
        <div class="cert-step cert-step--right">
          <div class="cert-step__milestone" data-short="1">Step 1</div>
          <div class="cert-step__card is-soon" aria-disabled="true">
            <img class="cert-step__logo" src="../../badges/cncf/kcna.svg" alt="Official KCNA logo" width="104" height="104">
            <div class="cert-step__body">
              <span class="cert-step__badge">Associate · Coming soon</span>
              <h2>KCNA</h2>
              <p>Kubernetes and Cloud Native Associate — foundations of containers, orchestration, and cloud-native concepts.</p>
              <div class="cert-step__meta"><span>Notes not published yet</span></div>
              <span class="cert-step__cta">Placeholder — add later</span>
            </div>
          </div>
        </div>

        <div class="cert-step cert-step--left">
          <div class="cert-step__milestone" data-short="2">Step 2</div>
          <a class="cert-step__card" href="cka/">
            <img class="cert-step__logo" src="../../badges/cncf/cka.svg" alt="Official CKA logo" width="104" height="104">
            <div class="cert-step__body">
              <span class="cert-step__badge">Administrator</span>
              <h2>CKA</h2>
              <p>Certified Kubernetes Administrator — cluster ops, troubleshooting, storage, networking, kubeadm.</p>
              <div class="cert-step__meta"><span>Curriculum live</span></div>
              <span class="cert-step__cta">Open CKA notes →</span>
            </div>
          </a>
        </div>

        <div class="cert-step cert-step--right">
          <div class="cert-step__milestone" data-short="3">Step 3</div>
          <a class="cert-step__card" href="ckad/">
            <img class="cert-step__logo" src="../../badges/cncf/ckad.svg" alt="Official CKAD logo" width="104" height="104">
            <div class="cert-step__body">
              <span class="cert-step__badge">Application Developer</span>
              <h2>CKAD</h2>
              <p>Certified Kubernetes Application Developer — workloads, config, observability, volumes, Helm.</p>
              <div class="cert-step__meta"><span>Curriculum live</span></div>
              <span class="cert-step__cta">Open CKAD notes →</span>
            </div>
          </a>
        </div>

        <div class="cert-step cert-step--left">
          <div class="cert-step__milestone" data-short="4">Step 4</div>
          <div class="cert-step__card is-soon" aria-disabled="true">
            <img class="cert-step__logo" src="../../badges/cncf/kcsa.svg" alt="Official KCSA logo" width="104" height="104">
            <div class="cert-step__body">
              <span class="cert-step__badge">Security Associate · Coming soon</span>
              <h2>KCSA</h2>
              <p>Kubernetes and Cloud Native Security Associate — security fundamentals before the specialist track.</p>
              <div class="cert-step__meta"><span>Notes not published yet</span></div>
              <span class="cert-step__cta">Placeholder — add later</span>
            </div>
          </div>
        </div>

        <div class="cert-step cert-step--right">
          <div class="cert-step__milestone" data-short="5">Step 5</div>
          <a class="cert-step__card" href="cks/">
            <img class="cert-step__logo" src="../../badges/cncf/cks.svg" alt="Official CKS logo" width="104" height="104">
            <div class="cert-step__body">
              <span class="cert-step__badge">Security Specialist</span>
              <h2>CKS</h2>
              <p>Certified Kubernetes Security Specialist — hardening, supply chain, runtime security, audit.</p>
              <div class="cert-step__meta"><span>Curriculum live</span></div>
              <span class="cert-step__cta">Open CKS notes →</span>
            </div>
          </a>
        </div>
      </div>
    </article>
  </div>
  <script src="../../js/docs.js"></script>
</body>
</html>
"""
    ROOT.mkdir(parents=True, exist_ok=True)
    (ROOT / "index.html").write_text(page, encoding="utf-8")


if __name__ == "__main__":
    import sys
    if "--build-only" not in sys.argv:
        download_cert("cka", CKA_PAGES)
        download_cert("ckad", CKAD_PAGES)
    build_cert("cka", CKA_PAGES)
    build_cert("ckad", CKAD_PAGES)
    write_hub()
