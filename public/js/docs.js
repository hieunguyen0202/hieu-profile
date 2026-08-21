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

  if (navEl && sidebar?.dataset.nav === "kubestronaut") {
    const r = root;
    const cert = sidebar.dataset.cert || "cks";
    const certItem = (path, label) => {
      const href = path ? `${r}${path}/` : r;
      const id = path || "exam";
      const cls = id === active ? "active" : "";
      return `<li><a class="${cls}" href="${href}">${label}</a></li>`;
    };
    const open = (paths) => paths.some((p) => p === active || (p === "exam" && active === "exam"));

    const cksNav = () => [
      certItem("", "CKS Exam"),
      group("Introduction", open(["introduction", "study-environment", "review-kubernetes", "review-containers"]), [
        certItem("introduction", "Introduction"),
        certItem("study-environment", "Study Environment"),
        certItem("review-kubernetes", "Review Kubernetes"),
        certItem("review-containers", "Review Containers"),
      ].join("")),
      group("Network", open(["network-security-policies", "ingress", "mtls", "cloud-platform-node-metadata", "control-access-gui-elements"]), [
        certItem("network-security-policies", "Network Policies"),
        certItem("ingress", "Ingress"),
        certItem("mtls", "mTLS"),
        certItem("cloud-platform-node-metadata", "Node metadata"),
        certItem("control-access-gui-elements", "GUI access"),
      ].join("")),
      group("Hardening &amp; Security", open(["cis-benchmark", "attack-surface-reduction", "hash-verification"]), [
        certItem("cis-benchmark", "CIS Benchmark"),
        certItem("attack-surface-reduction", "Attack surface"),
        certItem("hash-verification", "Hash verification"),
      ].join("")),
      group("RBAC", open(["rbac", "rbac-users", "service-accounts"]), [
        certItem("rbac", "RBAC"),
        certItem("rbac-users", "Users"),
        certItem("service-accounts", "Service accounts"),
      ].join("")),
      group("API", open(["restrict-access", "secrets", "update-process"]), [
        certItem("restrict-access", "Restrict API access"),
        certItem("secrets", "Secrets"),
        certItem("update-process", "Update process"),
      ].join("")),
      group("Container Runtime", open(["runtime-classes", "sandboxes", "security-context"]), [
        certItem("runtime-classes", "RuntimeClasses"),
        certItem("sandboxes", "Sandboxes"),
        certItem("security-context", "Security context"),
      ].join("")),
      group("Supply Chain", open(["container-registries", "images-vulnerabilities", "security-images", "static-analysis-conftest", "static-analysis-kubesec", "pod-security-standards", "open-policy-agent"]), [
        certItem("container-registries", "Registries"),
        certItem("images-vulnerabilities", "Image vulnerabilities"),
        certItem("security-images", "Secure images"),
        certItem("static-analysis-conftest", "Conftest"),
        certItem("static-analysis-kubesec", "Kubesec"),
        certItem("pod-security-standards", "Pod Security Standards"),
        certItem("open-policy-agent", "OPA"),
      ].join("")),
      group("Behavioral Analysis", open(["kernel-space-security", "falco-runtime-security", "container-immutability", "kubernetes-auditing"]), [
        certItem("kernel-space-security", "Kernel space security"),
        certItem("falco-runtime-security", "Falco runtime security"),
        certItem("container-immutability", "Container immutability"),
        certItem("kubernetes-auditing", "Kubernetes auditing"),
      ].join("")),
      certItem("solved-questions", "CKS: Solved Questions"),
      certItem("tips", "CKS Tips"),
      certItem("real-world-exam", "CKS Real World exam"),
    ].join("");

    const ckaNav = () => [
      certItem("", "Exam"),
      group("CKA: Conceitos principais", open(["review", "cluster-architecture", "design-cluster", "etcd", "etcd-ha", "kube-api-server", "kube-controller-manager", "kube-scheduler", "kube-proxy", "static-pods", "labels-selectors"]), [
        certItem("review", "Review"),
        certItem("cluster-architecture", "Cluster Architecture"),
        certItem("design-cluster", "Design Cluster"),
        certItem("etcd", "etcd"),
        certItem("etcd-ha", "etcd HA"),
        certItem("kube-api-server", "kube-api-server"),
        certItem("kube-controller-manager", "kube-controller-manager"),
        certItem("kube-scheduler", "kube-scheduler"),
        certItem("kube-proxy", "kube-proxy"),
        certItem("static-pods", "Static Pods"),
        certItem("labels-selectors", "Labels &amp; Selectors"),
      ].join("")),
      group("Scheduling", open(["manual-scheduling", "multiple-schedulers", "node-selector-affinity", "taint-tolerations", "resource-requirements-limits"]), [
        certItem("manual-scheduling", "Manual Scheduling"),
        certItem("multiple-schedulers", "Multiple Schedulers"),
        certItem("node-selector-affinity", "Node Selector &amp; Affinity"),
        certItem("taint-tolerations", "Taints &amp; Tolerations"),
        certItem("resource-requirements-limits", "Resource Requirements"),
      ].join("")),
      group("Logging Monitoring", open(["kubernetes-logs", "monitoring-cluster"]), [
        certItem("kubernetes-logs", "Kubernetes Logs"),
        certItem("monitoring-cluster", "Monitoring Cluster"),
      ].join("")),
      group("Application Lifecycle Management", open(["init-containers-multi-containers", "liveness-readiness-startup-probes", "rolling-updates-rollbacks", "configmap-envs", "secrets", "container-entrypoint-command"]), [
        certItem("init-containers-multi-containers", "Init &amp; Multi Containers"),
        certItem("liveness-readiness-startup-probes", "Probes"),
        certItem("rolling-updates-rollbacks", "Rolling Updates"),
        certItem("configmap-envs", "ConfigMaps"),
        certItem("secrets", "Secrets"),
        certItem("container-entrypoint-command", "Entrypoint &amp; Command"),
      ].join("")),
      group("Cluster Maintenance", open(["cluster-maintenance/backup-restore", "cluster-maintenance/cluster-update-process", "cluster-maintenance/create-cluster-kubeadm", "cluster-maintenance/os-upgrade", "cluster-maintenance/releases"]), [
        certItem("cluster-maintenance/backup-restore", "Backup &amp; Restore"),
        certItem("cluster-maintenance/cluster-update-process", "Cluster Update"),
        certItem("cluster-maintenance/create-cluster-kubeadm", "Create Cluster"),
        certItem("cluster-maintenance/os-upgrade", "OS Upgrade"),
        certItem("cluster-maintenance/releases", "Releases"),
      ].join("")),
      group("CKA: Security", open(["security-primitives", "authentication", "authorization", "api-groups", "api-certificates", "service-accounts", "kubeconfig", "kubectx-kubens", "tls-fundamentals", "kubernetes-tls", "network-policies", "security-context", "image-security"]), [
        certItem("security-primitives", "Security Primitives"),
        certItem("authentication", "Authentication"),
        certItem("authorization", "Authorization"),
        certItem("api-groups", "API Groups"),
        certItem("api-certificates", "API Certificates"),
        certItem("service-accounts", "Service Accounts"),
        certItem("kubeconfig", "kubeconfig"),
        certItem("kubectx-kubens", "kubectx &amp; kubens"),
        certItem("tls-fundamentals", "TLS Fundamentals"),
        certItem("kubernetes-tls", "Kubernetes TLS"),
        certItem("network-policies", "Network Policies"),
        certItem("security-context", "Security Context"),
        certItem("image-security", "Image Security"),
      ].join("")),
      group("Storage", open(["storage/conceitos-armazenamento", "storage/volumes", "storage/persistent-volume", "storage/storage-class", "storage/container-storage-interface"]), [
        certItem("storage/conceitos-armazenamento", "Storage Concepts"),
        certItem("storage/volumes", "Volumes"),
        certItem("storage/persistent-volume", "Persistent Volume"),
        certItem("storage/storage-class", "Storage Class"),
        certItem("storage/container-storage-interface", "CSI"),
      ].join("")),
      group("Networking", open(["networking-pre-requisites", "network-namespaces", "docker-networking", "cluster-network", "pod-network-interface", "container-network-interface", "coredns", "dns-basics", "dns-kubernetes", "service-network", "ingress"]), [
        certItem("networking-pre-requisites", "Prerequisites"),
        certItem("network-namespaces", "Network Namespaces"),
        certItem("docker-networking", "Docker Networking"),
        certItem("cluster-network", "Cluster Network"),
        certItem("pod-network-interface", "Pod Network"),
        certItem("container-network-interface", "CNI"),
        certItem("coredns", "CoreDNS"),
        certItem("dns-basics", "DNS Basics"),
        certItem("dns-kubernetes", "DNS in Kubernetes"),
        certItem("service-network", "Services"),
        certItem("ingress", "Ingress"),
      ].join("")),
      group("Installation Configuration Validation", open(["kubeadm-installation", "download-kubernetes-binaries"]), [
        certItem("kubeadm-installation", "kubeadm Installation"),
        certItem("download-kubernetes-binaries", "Download Binaries"),
      ].join("")),
      group("Troubleshooting", open(["troubleshooting/sequence-check-failure-application", "troubleshooting/sequence-check-failure-control-plane", "troubleshooting/sequence-check-failure-nodes", "troubleshooting/network-troubleshooting", "troubleshooting/kubectl-advanced-commands"]), [
        certItem("troubleshooting/sequence-check-failure-application", "App Failures"),
        certItem("troubleshooting/sequence-check-failure-control-plane", "Control Plane"),
        certItem("troubleshooting/sequence-check-failure-nodes", "Node Failures"),
        certItem("troubleshooting/network-troubleshooting", "Network"),
        certItem("troubleshooting/kubectl-advanced-commands", "kubectl Advanced"),
      ].join("")),
      group("Hardway Installation", open(["hardway-install/proposal", "hardway-install/preparing-required-files", "hardway-install/bootstraps"]), [
        certItem("hardway-install/proposal", "Proposal"),
        certItem("hardway-install/preparing-required-files", "Required Files"),
        certItem("hardway-install/bootstraps", "Bootstraps"),
      ].join("")),
      certItem("tips", "Tips"),
      certItem("cheats", "Cheats"),
      certItem("solved-questions", "CKA: Solved Questions"),
    ].join("");

    const ckadNav = () => [
      certItem("", "CKAD Exam"),
      group("CKAD: Conceitos principais", open(["recap-kubernetes", "configuration-from-cka", "containers-images"]), [
        certItem("recap-kubernetes", "Recap Kubernetes"),
        certItem("configuration-from-cka", "Configuration from CKA"),
        certItem("containers-images", "Containers &amp; Images"),
      ].join("")),
      group("Configuration", open(["deployments", "jobs-cronjobs"]), [
        certItem("deployments", "Deployments"),
        certItem("jobs-cronjobs", "Jobs &amp; CronJobs"),
      ].join("")),
      group("Multi Containers Pods", open(["multi-containers-pods"]), [
        certItem("multi-containers-pods", "Multi Containers Pods"),
      ].join("")),
      group("Observability", open(["readiness-liveness-startup-probes", "logs-and-monitoring"]), [
        certItem("readiness-liveness-startup-probes", "Probes"),
        certItem("logs-and-monitoring", "Logs &amp; Monitoring"),
      ].join("")),
      group("Pod Design", open(["statefulset", "custom-resources"]), [
        certItem("statefulset", "StatefulSet"),
        certItem("custom-resources", "Custom Resources"),
      ].join("")),
      group("Services &amp; Networking", open(["services-networking"]), [
        certItem("services-networking", "Services &amp; Networking"),
      ].join("")),
      group("Volumes", open(["volumes"]), [
        certItem("volumes", "Volumes"),
      ].join("")),
      group("CKAD: Security", open(["api-version", "api-depreciations", "admission-controllers", "security-roadmap"]), [
        certItem("api-version", "API Version"),
        certItem("api-depreciations", "API Depreciations"),
        certItem("admission-controllers", "Admission Controllers"),
        certItem("security-roadmap", "Security Roadmap"),
      ].join("")),
      group("CKAD: Helm", open(["helm-basics"]), [
        certItem("helm-basics", "Helm Basics"),
      ].join("")),
    ].join("");

    const label = cert === "cka" ? "CKA" : cert === "ckad" ? "CKAD" : "CKS";
    sidebar.querySelector(".docs-nav-label").textContent = label;
    navEl.innerHTML = cert === "cka" ? ckaNav() : cert === "ckad" ? ckadNav() : cksNav();
  } else if (navEl && sidebar?.dataset.nav === "english") {
    // Topic sidebar is rendered in HTML by _gen_english_vocab.py
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
