#!/usr/bin/env python3
"""Generate Web Security chapter HTML (Part II–VIII + appendix). Run from repo root or this folder."""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "public" / "blog" / "web-security"

NAV = [
    ("01-gioi-thieu", "01. Giới thiệu"),
    ("02-http", "02. HTTP"),
    ("03-burp", "03. Burp"),
    ("04", "04. Authentication"),
    ("05", "05. Session"),
    ("06", "06. Access Control"),
    ("07", "07. OAuth"),
    ("08", "08. JWT"),
    ("09", "09. CORS"),
    ("10", "10. CSRF"),
    ("11", "11. XSS"),
    ("12", "12. SQLi"),
    ("13", "13. NoSQLi"),
    ("14", "14. Command Injection"),
    ("15", "15. SSRF"),
    ("16", "16. XXE"),
    ("17", "17. File Upload"),
    ("18", "18. Path Traversal"),
    ("19", "19. Open Redirect"),
    ("20", "20. Race Condition"),
    ("21", "21. Business Logic"),
    ("22", "22. Clickjacking"),
    ("23", "23. Cache Poisoning"),
    ("24", "24. Request Smuggling"),
    ("25", "25. SSTI"),
    ("26", "26. Deserialization"),
    ("27", "27. GraphQL"),
    ("28", "28. API Security"),
    ("29", "29. Kubernetes"),
    ("30", "30. CI/CD"),
    ("31", "31. Secrets"),
    ("32", "32. Cloud"),
    ("33", "33. Logging"),
    ("34", "34. Incident Response"),
    ("35", "35. Checklist"),
    ("appendix", "Appendix"),
]


def h2(i, t):
    return f'<h2 id="{i}">{t}</h2>\n'


def h3(i, t):
    return f'<h3 id="{i}">{t}</h3>\n'


def p(*xs):
    return "".join(f"<p>{x}</p>\n" for x in xs)


def ul(xs):
    return "<ul>\n" + "".join(f"        <li>{x}</li>\n" for x in xs) + "      </ul>\n"


def ol(xs):
    return "<ol>\n" + "".join(f"        <li>{x}</li>\n" for x in xs) + "      </ol>\n"


def bq(x):
    return f"<blockquote>{x}</blockquote>\n"


def pre(x):
    return f"<pre><code>{x}</code></pre>\n"


def toc_from(body: str) -> str:
    items = []
    for m in re.finditer(r'<h([23]) id="([^"]+)">(.*?)</h\1>', body):
        depth, hid, title = m.group(1), m.group(2), m.group(3)
        cls = ' class="depth-3"' if depth == "3" else ""
        items.append(f'        <a{cls} href="#{hid}">{title}</a>')
    return "\n".join(items)


def wrap(cid, crumb, title, lede, part, desc, body, tags):
    ids = [x[0] for x in NAV]
    i = ids.index(cid)
    prev_id, prev_l = (NAV[i - 1] if i else None)
    next_id, next_l = (NAV[i + 1] if i < len(NAV) - 1 else (None, None))
    prev = f'<a href="../{prev_id}/">Previous · {prev_l}</a>' if prev_id else '<a href="../">Previous · Overview</a>'
    nxt = f'<a href="../{next_id}/">Next · {next_l}</a>' if next_id else '<a href="../">Overview</a>'
    tags_html = "\n".join(f'        <span class="docs-tag">{t}</span>' for t in tags)
    return f'''<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — Hieu Nguyen</title>
  <meta name="description" content="{desc}">
  <link rel="icon" href="../../../favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../../../css/docs.css">
</head>
<body class="docs">
  <div class="cursor" id="cursor"></div>
  <div class="cursor-ring" id="cursorRing"></div>
  <canvas id="matrix-canvas"></canvas>
  <div class="grid-bg"></div>
  <header class="docs-topbar">
    <button class="docs-menu-btn" id="docsMenuBtn" type="button">menu</button>
    <a class="docs-brand" href="../../../">i'm<span>.hiu</span></a>
    <nav class="docs-series">
      <a class="active" href="../">Web Security</a>
      <a href="../../cks-exam/">CKS exam</a>
    </nav>
    <span class="docs-topbar-spacer"></span>
    <a class="docs-top-link" href="../../../#blogs">blogs</a>
  </header>
  <div class="docs-shell">
    <aside class="docs-sidebar" id="docsSidebar" data-docs-root="../" data-active="{cid}">
      <div class="docs-nav-label">Web Security</div>
      <ul class="docs-nav" id="docsNav"></ul>
    </aside>
    <article class="docs-main">
      <div class="docs-breadcrumb">
        <a href="../../../">Home</a>
        <span>›</span>
        <a href="../../../#blogs">Blogs</a>
        <span>›</span>
        <a href="../">Overview</a>
        <span>›</span>
        <span>{crumb}</span>
      </div>
      <h1>{title}</h1>
      <p class="lede">{lede}</p>
      <div class="docs-meta">
        <span><strong>Tác giả:</strong> Hieu Nguyen (Ryan)</span>
        <span><strong>Phần:</strong> {part}</span>
        <span><strong>Cập nhật:</strong> Aug 2026</span>
      </div>
      {body}
      <div class="docs-tags">
{tags_html}
      </div>
      <div class="docs-pager">
        {prev}
        {nxt}
      </div>
    </article>
    <aside class="docs-toc">
      <div class="docs-toc-title">On this page</div>
      <nav>
{toc_from(body)}
      </nav>
    </aside>
  </div>
  <script src="../../../js/docs.js"></script>
</body>
</html>
'''


def quiz(*qs):
    return h2("on-tap", "Câu hỏi ôn tập") + ol(qs)


def tom(*xs):
    return h2("tom-tat", "Tóm tắt") + ul(xs)


CHAPTERS: list[tuple] = []


def add(**kw):
    CHAPTERS.append(kw)


# --- Part II ---
add(
    id="04", crumb="04. Authentication", title="Chương 4: Authentication",
    lede="Login sai không phải “user ngu”. Đó là control bạn chưa siết.",
    part="II — Auth", desc="Authentication cho DevOps: enumeration, MFA, reset password, lockout, và log.",
    tags=["auth", "mfa", "owasp"],
    body=h2("khai-niem", "Khái niệm")
    + p("Authentication trả lời <strong>bạn là ai</strong>. Authorization trả lời <strong>bạn được làm gì</strong>. Nhầm hai thứ này thì 401/403, MFA, và RBAC đều đặt sai chỗ.")
    + h2("hoat-dong", "Cách hoạt động")
    + p("User gửi chứng cứ (password, OTP, WebAuthn, federated token) → server kiểm tra → phát session hoặc JWT. Mọi bước sau login đều giả định bước này đúng.")
    + h2("lo-hong", "Các lớp lỗ hổng thường gặp")
    + h3("enum", "Username / email enumeration")
    + p("Message khác nhau (“user không tồn tại” vs “sai mật khẩu”), thời gian response khác nhau, hoặc reset-password tiết lộ account. Attacker chỉ cần danh sách email đã leak.")
    + h3("brute", "Đoán mật khẩu và lockout giả")
    + p("Không rate-limit, lockout chỉ theo username (đổi IP/username là né), CAPTCHA chỉ trên UI không trên API. Password spray: một mật khẩu yếu trên nhiều tài khoản — log trông “thưa” hơn brute một user.")
    + h3("mfa", "MFA làm cho có")
    + p("OTP gửi cùng response login, MFA cookie không bind device, backup code không rotate, “remember this device” sống hàng năm. Bypass thường ở <em>nhánh phụ</em> (reset, OAuth, API cũ) chứ không phải form login chính.")
    + h3("reset", "Password reset")
    + p("Token ngắn, một lần, hết hạn; Host header không được dùng để ghép link (Chương 2). Token trong URL thì access log giữ secret.")
    + h3("remember", "Remember me")
    + p("Selector + verifier hashed phía server; đừng để token login thuần trong cookie dài hạn.")
    + h2("phat-hien", "Cách phát hiện")
    + ul(["So response login fail: status, length, thời gian.", "API /login và /forgot-password có cùng policy rate-limit không.", "Audit: MFA bắt buộc nhóm admin chưa."])
    + h2("phong", "Phòng chống")
    + ul(["Thông báo lỗi login chung.", "Rate-limit + backoff theo IP và account; alert spray.", "MFA phishing-resistant (WebAuthn) cho privileged.", "Reset: token random, TTL ngắn, invalidate session cũ.", "Password: check denylist / leak, không tự roll hash yếu."])
    + h2("devops", "Góc nhìn DevOps")
    + p("IdP (Keycloak, Cognito, Entra) tập trung policy. WAF rate-limit là lớp phụ. Secret SMTP/SMS cho OTP nằm Vault, không env Pod. Log auth event (success/fail/MFA/reset) đủ field nhưng không log password.")
    + tom("Auth ≠ authz.", "Enumeration và reset là lỗ hay hơn “bẻ hash”.", "MFA phải phủ mọi nhánh login.", "DevOps: IdP, rate-limit, log, secret kênh OTP.")
    + quiz("Vì sao message login khác nhau thành lỗ?", "Lockout theo username thất bại thế nào trước password spray?", "Reset password lấy Host từ request thì rủi ro gì?", "Remember-me cookie nên chứa gì, không chứa gì?", "API login có CAPTCHA UI nhưng không có throttle — hệ quả?")
)

add(
    id="05", crumb="05. Session", title="Chương 5: Session Management",
    lede="Session là chìa sau khi đã chứng minh danh tính. Làm mất chìa thì MFA cũng vô nghĩa.",
    part="II — Auth", desc="Session token, fixation, timeout, cookie flags, JWT vs server session.",
    tags=["session", "cookies", "jwt"],
    body=h2("khai-niem", "Khái niệm")
    + p("Sau login, server nhớ bạn bằng <strong>session token</strong> (cookie hoặc header). Token phải khó đoán, gắn user, và chết đúng lúc.")
    + h2("token", "Yêu cầu bảo mật cho token")
    + ul(["Entropy đủ (CSPRNG), không phải user-id encode.", "Rotate lúc login (chống session fixation).", "Invalidate lúc logout, đổi password, MFA xong.", "Không nhét trong URL / Referer / log."])
    + h2("tan-cong", "Lớp sự cố thường gặp")
    + h3("hijack", "Session hijacking")
    + p("Token lộ: XSS đọc cookie thiếu HttpOnly, HTTP không Secure, log access, XSS stored. Phòng: flag cookie + CSP + HTTPS.")
    + h3("fix", "Session fixation")
    + p("Attacker gài token trước login; nếu app không đổi token khi authenticate thì phiên đó thành của victim. Fix: luôn phát token mới sau login.")
    + h3("weak", "Token yếu")
    + p("Tăng dần, timestamp, MD5(email). Scanner và log là đủ để nhận ra — không cần “bẻ”.")
    + h2("cookie", "Cookie attributes")
    + p("HttpOnly, Secure, SameSite, Domain/Path hẹp, Max-Age hợp lý — xem Chương 2. Session cookie Domain=<code>.company.com</code> quá rộng thì mọi subdomain chia phiên.")
    + h2("timeout", "Timeout")
    + ul(["Idle timeout: không hoạt động thì chết.", "Absolute timeout: dù đang dùng cũng phải re-auth (admin).", "Logout server-side: xóa store, không chỉ xóa cookie client."])
    + h2("jwt-vs", "JWT vs session server-side")
    + p("Session store (Redis) revoke được ngay. JWT stateless khó revoke trừ denylist/short TTL. Hybrid: access ngắn + refresh rotate.")
    + h2("phat-hien", "Cách phát hiện")
    + ul(["Set-Cookie lúc login có đủ flag không.", "Login có Set-Cookie mới hay giữ cookie cũ.", "Logout còn dùng lại token được không (lab của bạn)."])
    + h2("devops", "Góc nhìn DevOps")
    + p("Sticky session vs Redis shared. TLS terminate ở Ingress thì cookie Secure vẫn set được nếu app tin <code>X-Forwarded-Proto</code> từ proxy tin cậy. Session store không public Service.")
    + tom("Rotate session khi login.", "Revoke lúc logout/đổi mật khẩu.", "Cookie flags là lớp rẻ.", "JWT ngắn hạn hoặc có cửa revoke.")
    + quiz("Fixation khác hijacking chỗ nào?", "Vì sao Domain cookie quá rộng nguy hiểm?", "Idle vs absolute timeout?", "Khi nào Redis session hơn JWT thuần?", "Logout chỉ xóa cookie client thì còn gì?")
)

add(
    id="06", crumb="06. Access Control", title="Chương 6: Access Control",
    lede="OWASP A01: user làm việc không thuộc quyền. DevOps hay mở nhầm admin Service.",
    part="II — Auth", desc="IDOR, vertical/horizontal privilege, deny-by-default, RBAC.",
    tags=["access-control", "idor", "rbac"],
    body=h2("khai-niem", "Khái niệm")
    + p("Mỗi request phải hỏi: principal này có được object/action này không — <em>trên server</em>, không phải ẩn nút trên UI.")
    + h2("phan-loai", "Phân loại")
    + ul(["<strong>Vertical:</strong> user → admin function.", "<strong>Horizontal:</strong> user A xem object của B (IDOR).", "<strong>Context:</strong> đúng role nhưng sai trạng thái (sửa đơn đã thanh toán)."])
    + h2("idor", "IDOR")
    + p("Object ID do client chọn (<code>/invoices/318</code>) mà server không kiểm tra sở hữu. UUID không phải control — chỉ làm enumeration chậm hơn. Mass assignment / filter trên query cũng cùng lớp.")
    + h2("vertical", "Leo quyền dọc")
    + p("Admin path không authz, parameter <code>role=admin</code> tin từ client, method override (<code>X-HTTP-Method-Override</code>) đi nhánh khác policy. Ingress mở <code>/admin</code> ra internet là misconfig vận hành.")
    + h2("phat-hien", "Cách phát hiện")
    + ul(["Hai tài khoản lab: gọi object của nhau.", "Bỏ cookie admin, gọi lại path admin.", "Kiểm tra Service/Ingress không expose dashboard."])
    + h2("phong", "Phòng chống")
    + ol(["Deny by default.", "Authz trung tâm (policy library), không copy if role rải controller.", "RBAC/ABAC server-side; ID nội bộ, không tin ID client nếu có thể.", "Test tự động: user A không đọc resource B."])
    + h2("devops", "Góc nhìn DevOps")
    + p("NetworkPolicy không thay authz app. Nhưng không expose admin UI; IP allowlist / VPN / mesh mTLS cho service nội bộ. Audit log: ai đọc object nào.")
    + tom("UI ẩn không phải authz.", "IDOR = thiếu check sở hữu.", "Deny by default.", "Đừng public admin Ingress.")
    + quiz("Horizontal khác vertical?", "UUID hết IDOR không?", "Vì sao tin role trên JSON body sai?", "Test tối thiểu cho IDOR trong CI?", "NetworkPolicy đủ thay access control app?")
)

add(
    id="07", crumb="07. OAuth", title="Chương 7: OAuth 2.0",
    lede="OAuth ủy quyền — không phải “login Google là xong bảo mật”.",
    part="II — Auth", desc="OAuth flows, state, redirect_uri, PKCE, token leak.",
    tags=["oauth", "oidc", "pkce"],
    body=h2("khai-niem", "Khái niệm")
    + p("OAuth 2.0: resource owner cho client truy cập resource server với <strong>scope</strong> giới hạn. OpenID Connect thêm identity. DevOps hay đứng ở IdP, redirect URI, và secret client.")
    + h2("flows", "Flows")
    + ul(["<strong>Authorization code</strong> (+ PKCE): mặc định cho web và SPA/mobile.", "<strong>Implicit</strong>: token trên fragment — deprecated, đừng bật.", "<strong>Client credentials</strong>: service-to-service, không user."])
    + h2("lo-hong", "Lỗ thường gặp")
    + ul(["Thiếu <code>state</code> (CSRF trên consent).", "<code>redirect_uri</code> khớp tiền tố lỏng → token/code về host lạ.", "Token trên query → Referer/log.", "Không kiểm tra <code>aud</code>/<code>iss</code>/expiry.", "Scope rộng hơn user đồng ý.", "Liên kết account theo email chưa verify."])
    + h2("phong", "Phòng chống")
    + ul(["Redirect URI allowlist exact match.", "PKCE bắt buộc public client.", "state/nonce ngẫu nhiên, one-time.", "Secret client chỉ trên backend; SPA dùng public + PKCE.", "Map IdP user theo subject ổn định, không chỉ email."])
    + h2("devops", "Góc nhìn DevOps")
    + p("Cấu hình IdP (Keycloak/Entra/Cognito) là production config: đừng wildcard redirect. Secret client trong Vault. Callback URL chỉ HTTPS. Log token exchange lỗi, không log code/token.")
    + tom("Code flow + PKCE.", "redirect_uri chặt.", "state chống CSRF consent.", "Đừng implicit.")
    + quiz("state làm gì?", "Vì sao prefix match redirect_uri nguy hiểm?", "PKCE giải quyết vấn đề gì của public client?", "Token trên query lộ đường nào?", "Liên kết account theo email chưa verify rủi ro gì?")
)

add(
    id="08", crumb="08. JWT", title="Chương 8: JWT",
    lede="JWT tiện vì stateless. Tiện đó cũng là chỗ revoke và thuật toán bị làm ẩu.",
    part="II — Auth", desc="JWT structure, alg pinning, secret, TTL, gateway validation.",
    tags=["jwt", "oidc", "tokens"],
    body=h2("khai-niem", "Khái niệm")
    + p("JWT: header.payload.signature (Base64URL). Payload đọc được — không mã hóa. Chữ ký mới là control.")
    + h2("cau-truc", "Cấu trúc")
    + p("Header: alg, typ, kid. Payload: sub, exp, iss, aud, role… Signature: HMAC hoặc RSA/ECDSA. Decode trên lab để đọc claim; đổi claim mà không ký lại thì gateway phải reject.")
    + h2("lo-hong", "Lớp bug thư viện / config")
    + ul(["Tin <code>alg</code> từ token (none / nhầm RS↔HS).", "Secret HMAC yếu hoặc default.", "Nhận JWK/jku/kid từ attacker (SSRF + key confuse).", "TTL dài, không <code>exp</code>, không check <code>aud</code>."])
    + bq("Phòng: pin algorithm trên server, lấy key từ JWKS nội bộ allowlist, không từ header token.")
    + h2("phong", "Phòng chống")
    + ul(["Verify chữ ký với key cố định / JWKS tin cậy.", "TTL ngắn; refresh rotate.", "Không nhét PII/secret vào payload.", "Denylist <code>jti</code> khi logout nếu cần cắt ngay."])
    + h2("devops", "Góc nhìn DevOps")
    + p("API gateway (Kong, Istio JWT, Cloud Armor) verify iss/aud/exp. JWKS cache + rotation. Log <code>sub</code> không log raw token.")
    + tom("Payload không bí mật.", "Pin alg + key.", "exp/aud/iss bắt buộc.", "Gateway verify một nơi.")
    + quiz("JWT khác session cookie chỗ revoke?", "Vì sao không tin alg trên token?", "kid nguy hiểm khi nào?", "Claim nào gateway nên bắt?", "Access token sống 24h thì trade-off gì?")
)

# --- Part III ---
add(
    id="09", crumb="09. CORS", title="Chương 9: CORS",
    lede="CORS không phải firewall. Nó là ngoại lệ có kiểm soát của Same-Origin Policy.",
    part="III — Client-side", desc="SOP, CORS misconfig, ACAO, credentials, Ingress.",
    tags=["cors", "sop", "headers"],
    body=h2("khai-niem", "Khái niệm")
    + p("<strong>Same-Origin Policy</strong>: origin = scheme + host + port. JS origin A không đọc response origin B trừ khi B gửi CORS header cho phép.")
    + h2("misconfig", "Misconfiguration")
    + ul(["Phản chiếu mọi <code>Origin</code> kèm <code>Access-Control-Allow-Credentials: true</code>.", "Whitelist regex sai (<code>evilcompany.com</code> khớp <code>company.com</code>).", "Cho <code>null</code> origin (sandbox iframe).", "Wildcard <code>*</code> với credential — browser từ chối; đừng “sửa” bằng reflect origin."])
    + h2("phong", "Phòng chống")
    + ul(["Allowlist origin chính xác.", "API cookie: SameSite + CORS chặt, hoặc tốt hơn: bearer token không dựa cookie cross-origin.", "Preflight: method/header tối thiểu."])
    + h2("devops", "Góc nhìn DevOps")
    + p("Header CORS ở Ingress hay app — một nguồn. Đừng <code>add_header ACAO $http_origin</code> vô điều kiện. Review Helm values <code>cors.origin: '*'</code>.")
    + tom("SOP mặc định chặn đọc cross-origin.", "Reflect Origin + credential = hỏng.", "Allowlist exact.", "Ingress đừng copy Origin mù.")
    + quiz("Origin gồm gì?", "Vì sao * + credentials không “mở cho tiện”?", "null origin đến từ đâu?", "Preflight OPTIONS lộ gì?", "CORS có chặn request server-side (curl) không?")
)

add(
    id="10", crumb="10. CSRF", title="Chương 10: CSRF",
    lede="Trình duyệt tự gửi cookie. Site khác có thể “ký tên bạn” nếu bạn không có token chống giả.",
    part="III — Client-side", desc="CSRF điều kiện, SameSite, synchronizer token, API headers.",
    tags=["csrf", "samesite", "cookies"],
    body=h2("khai-niem", "Khái niệm")
    + p("CSRF: user đã login, cookie session tự đi theo request do trang khác khởi tạo. Server thấy phiên hợp lệ, thực hiện hành động user không cố ý.")
    + h2("dieu-kien", "Điều kiện")
    + ul(["Hành động quan trọng dựa cookie (không thêm secret request).", "Không token/SameSite đủ chặt.", "User đang có phiên."])
    + p("GET có side effect (unsubscribe, transfer) đặc biệt dễ. JSON thuần từ form cross-site khó hơn — đừng coi là đủ.")
    + h2("phong", "Phòng chống")
    + ol(["Synchronizer CSRF token (per-session hoặc per-form), kiểm tra server.", "SameSite=Lax tối thiểu; Strict cho cookie nhạy.", "API: custom header (framework set) + SameSite; không tin Origin/Referer một mình.", "Re-auth cho hành động tiền / đổi email."])
    + h2("devops", "Góc nhìn DevOps")
    + p("Cookie session thiếu SameSite trên Ingress. WAF rule CSRF không thay token app. Tách site thao tác (app) và site marketing origin.")
    + tom("Cookie tự gửi là gốc CSRF.", "Token + SameSite.", "Không side effect trên GET.", "Hành động nhạy cần re-auth.")
    + quiz("CSRF khác XSS chỗ nào?", "SameSite=Lax còn khe nào?", "Vì sao GET transfer nguy hiểm?", "Custom header giúp API thế nào?", "Logout CSRF có đáng lo?")
)

add(
    id="11", crumb="11. XSS", title="Chương 11: XSS",
    lede="Browser tin HTML/JS bạn nhét vào trang. Output encoding và CSP là hai lớp phải có.",
    part="III — Client-side", desc="Reflected, stored, DOM XSS; encoding; CSP; HttpOnly.",
    tags=["xss", "csp", "owasp"],
    body=h2("khai-niem", "Khái niệm")
    + p("XSS: dữ liệu không tin được chạy như script trong phiên user. Hậu quả: đọc DOM, hành động với cookie không HttpOnly, deface — không cần “payload showcase” để hiểu risk.")
    + h2("loai", "Ba loại")
    + ul(["<strong>Reflected:</strong> input về ngay response.", "<strong>Stored:</strong> lưu DB/comment rồi mọi victim mở.", "<strong>DOM-based:</strong> JS client lấy location/hash nhét innerHTML."])
    + h2("phong", "Phòng chống")
    + ol(["Output encoding đúng context (HTML, attr, JS, URL).", "Tránh <code>innerHTML</code> / <code>eval</code> với dữ liệu user.", "CSP: default-src 'self'; không unsafe-inline nếu được nonce/hash.", "Cookie session HttpOnly.", "Framework auto-escape (React default) — vẫn cẩn <code>dangerouslySetInnerHTML</code>."])
    + h2("phat-hien", "Cách phát hiện")
    + p("Lab PortSwigger / pipeline DAST. Code review sink HTML. CSP report-uri trên staging.")
    + h2("devops", "Góc nhìn DevOps")
    + p("CSP header tại Ingress. Không serve user-upload với <code>text/html</code> trên origin app. WAF XSS signature là lớp phụ, dễ bypass — không phải control chính.")
    + tom("Encode output.", "CSP siết script.", "HttpOnly session.", "Stored XSS rộng hơn reflected.")
    + quiz("Stored khác reflected?", "DOM XSS nằm tầng nào?", "CSP unsafe-inline làm yếu gì?", "HttpOnly chặn XSS đọc cookie chứ không chặn gì?", "Upload HTML trên cùng origin rủi ro gì?")
)

add(
    id="22", crumb="22. Clickjacking", title="Chương 22: Clickjacking",
    lede="User nghĩ đang bấm trang bạn. Thực ra bấm nút trong iframe trong suốt.",
    part="III — Client-side", desc="Clickjacking, X-Frame-Options, CSP frame-ancestors.",
    tags=["clickjacking", "csp", "iframe"],
    body=h2("khai-niem", "Khái niệm")
    + p("Trang độc hại nhúng app trong iframe, overlay UI. Cú click “trúng” Transfer / Grant permission.")
    + h2("phong", "Phòng chống")
    + ul(["<code>Content-Security-Policy: frame-ancestors 'none'</code> (hoặc self).", "<code>X-Frame-Options: DENY</code> / SAMEORIGIN cho client cũ.", "Không dựa JS frame-busting làm control chính."])
    + h2("devops", "Góc nhìn DevOps")
    + p("Header tại Ingress cho mọi response HTML. App cần nhúng (widget) thì allowlist ancestor, không mở hết.")
    + tom("Cấm embed mặc định.", "frame-ancestors hơn XFO.", "Ngoại lệ widget phải hẹp.")
    + quiz("Clickjacking cần XSS không?", "frame-ancestors khác XFO?", "Widget chat nên allow ancestor thế nào?", "Header này đặt ở CDN có đủ?", "UI confirm có thay clickjacking defense không?")
)

# --- Part IV ---
add(
    id="12", crumb="12. SQLi", title="Chương 12: SQL Injection",
    lede="String SQL cộng với input user. Database làm đúng những gì bạn vô tình viết.",
    part="IV — Injection", desc="SQLi khái niệm, parameterized queries, least privilege, WAF phụ.",
    tags=["sqli", "injection", "owasp"],
    body=h2("khai-niem", "Khái niệm")
    + p("SQL injection: input trở thành câu lệnh. Lớp: error-based, UNION, boolean/time blind, second-order (lưu rồi query sau). Chi tiết kỹ thuật khai thác để học trên lab được phép (PortSwigger), không đem ra hệ thống thật.")
    + h2("phong", "Phòng chống")
    + ol(["Parameterized queries / bind variables — control chính.", "ORM đúng cách (không raw concat).", "DB user least privilege: app không cần FILE / DBA.", "Input allowlist khi dynamic identifier (ORDER BY cột) — không nhét raw vào identifier.", "WAF: lớp phụ."])
    + h2("phat-hien", "Cách phát hiện")
    + p("SAST, code review concat SQL, error DB lộ trên staging, DAST trên lab. Production: không hiện SQL error cho client.")
    + h2("devops", "Góc nhìn DevOps")
    + p("Secret DB không admin. NetworkPolicy: chỉ app subnet tới 5432. Log slow query, không log full bound params nếu có PII. Image không ship CLI dump lung tung.")
    + tom("Bind parameters.", "Ít quyền DB.", "Ẩn lỗi SQL.", "WAF không thay code.")
    + quiz("Vì sao escape tay kém prepared statement?", "Second-order là gì?", "App role DB nên thiếu quyền nào?", "ORM vẫn SQLi khi nào?", "Hiện stack SQL trên 500 page hại gì?")
)

add(
    id="13", crumb="13. NoSQLi", title="Chương 13: NoSQL Injection",
    lede="Mongo/Redis không phải “hết injection”. Operator và JSON type mới là cửa.",
    part="IV — Injection", desc="NoSQL operator injection, type validation, disable $where.",
    tags=["nosql", "mongodb", "injection"],
    body=h2("khai-niem", "Khái niệm")
    + p("NoSQL nhận object/operator chứ không chỉ string. Nếu parser HTTP nhét JSON operator vào query login, điều kiện trở thành luôn đúng hoặc chạy JS (<code>$where</code>).")
    + h2("phong", "Phòng chống")
    + ul(["Validate type: password phải string, không object.", "Không nhét raw JSON user vào filter.", "Tắt JS server-side trên Mongo nếu không cần.", "Redis: không COMPOSITE lệnh từ user; dùng API an toàn."])
    + h2("devops", "Góc nhìn DevOps")
    + p("Mongo bind nội bộ, auth + TLS. Không expose 27017. Backup không public bucket.")
    + tom("Type check input.", "Không tin operator từ client.", "Tắt feature nguy hiểm.", "DB không public.")
    + quiz("Operator injection khác SQLi string chỗ nào?", "$where rủi ro gì?", "Vì sao Content-Type JSON vs form đổi payload?", "Redis injection thường đi với anti-pattern nào?", "NetworkPolicy giúp gì?")
)

add(
    id="14", crumb="14. Command Injection", title="Chương 14: Command Injection",
    lede="App gọi shell với string có user input. OS làm phần còn lại.",
    part="IV — Injection", desc="OS command injection, subprocess list, no shell, least privilege.",
    tags=["command-injection", "rce", "devops"],
    body=h2("khai-niem", "Khái niệm")
    + p("Command injection khi ghép lệnh OS từ input (ping host, convert file). Metacharacter shell biến một tham số thành nhiều lệnh. Không cần liệt kê payload để biết: đừng gọi shell.")
    + h2("phong", "Phòng chống")
    + ol(["Đừng gọi OS — dùng library.", "Bắt buộc: exec mảng argument, <code>shell=False</code>.", "Allowlist giá trị (enum), không blacklist ký tự.", "Process / container non-root, không mount docker.sock."])
    + h2("devops", "Góc nhìn DevOps")
    + p("Pod: drop ALL caps, readOnlyRootFilesystem, không privileged. Seccomp. Egress DNS/HTTP siết — giảm impact nếu code còn gọi nhầm.")
    + tom("Không shell=True.", "Allowlist.", "Least privilege container.", "Không docker.sock trong app Pod.")
    + quiz("shell=True khác list args?", "Blacklist khoảng trắng đủ không?", "Capability nào nên drop?", "Vì sao ping-from-form là mùi?", "Egress policy giảm gì sau khi bị inject?")
)

add(
    id="16", crumb="16. XXE", title="Chương 16: XXE",
    lede="Parser XML mặc định hay tải entity ngoài. Đó là SSRF/file read núp sau SOAP/upload.",
    part="IV — Injection", desc="XML External Entity, disable DTD, Content-Type confusion.",
    tags=["xxe", "xml", "ssrf"],
    body=h2("khai-niem", "Khái niệm")
    + p("XXE: XML khai entity trỏ file local hoặc URL. Parser resolve → đọc file hoặc gọi nội bộ (SSRF). Hay gặp SOAP, Office XML, SAML, upload “document”.")
    + h2("phong", "Phòng chống")
    + ul(["Tắt DTD / external entity trên parser.", "Không parse XML nếu API nhận JSON.", "Limit size; không follow HTTP entity.", "Content-Type: đừng parse XML khi client gửi nhầm."])
    + h2("devops", "Góc nhìn DevOps")
    + p("WAF có rule XXE — phụ. Image libxml phiên bản còn hỗ trợ. NetworkPolicy chặn Pod app gọi metadata/IMDS.")
    + tom("Disable external entity.", "Prefer JSON.", "Giới hạn parser.", "Egress siết.")
    + quiz("XXE dẫn tới class lỗ nào khác?", "SAML/SOAP vì sao hay dính?", "Tắt DTD ở đâu?", "Upload docx liên quan gì?", "Parser default-safe hay default-mở?")
)

add(
    id="25", crumb="25. SSTI", title="Chương 25: SSTI",
    lede="Template engine render string user. Đôi khi string đó là code.",
    part="IV — Injection", desc="Server-side template injection, sandbox, không render user template.",
    tags=["ssti", "templates"],
    body=h2("khai-niem", "Khái niệm")
    + p("SSTI khi Jinja/Freemarker/Twig… compile input user như template. Hậu quả từ XSS tới RCE tùy engine — học chi tiết trên lab, vá bằng không render input như template.")
    + h2("phong", "Phòng chống")
    + ul(["Template cố định trong repo; user data chỉ biến đã escape.", "Không <code>from_string(user)</code>.", "Sandbox engine nếu bắt buộc (vẫn coi là yếu).", "Tách privilege process render."])
    + h2("devops", "Góc nhìn DevOps")
    + p("Review PR có render template từ CMS. WAF không đủ. Container render không mount secret rộng.")
    + tom("User input ≠ template source.", "Escape context.", "Sandbox không phải viên đạn bạc.")
    + quiz("SSTI khác XSS chỗ nào?", "from_string nguy hiểm vì sao?", "Email template user-edit rủi ro gì?", "Phát hiện SSTI trên lab khác production scan?", "Quyền Pod render nên thế nào?")
)

# --- Part V ---
add(
    id="15", crumb="15. SSRF", title="Chương 15: SSRF",
    lede="Server đi fetch URL hộ user. Cloud metadata và Kubernetes API ở ngay góc mạng đó.",
    part="V — Server-side", desc="SSRF, IMDS, allowlist, egress, metadata hop limit.",
    tags=["ssrf", "imds", "owasp"],
    body=h2("khai-niem", "Khái niệm")
    + p("SSRF: app mở kết nối tới URL attacker chỉ định (webhook, preview, import). Mục tiêu: localhost, RFC1918, IMDS <code>169.254.169.254</code>, kube API.")
    + h2("phong", "Phòng chống")
    + ul(["Allowlist scheme + host; DNS rebinding: resolve rồi khóa IP, cấm redirect lệch.", "Không tin URL user cho file://.", "IMDS v2 / hop-limit; NetworkPolicy deny metadata.", "Webhook: IP allowlist customer, không server-side fetch tùy ý."])
    + h2("devops", "Góc nhìn DevOps")
    + p("Đây là chương DevOps. Egress mặc định deny. ServiceAccount token không automount. Split webhook worker ra network riêng.")
    + tom("Allowlist URL.", "Chặn IMDS.", "Egress deny.", "Không automount SA.")
    + quiz("IMDS liên quan SSRF thế nào?", "DNS rebinding phá allowlist host ra sao?", "Hop-limit IMDS giúp gì?", "Webhook nên validate gì?", "Kube API từ Pod app: control nào?")
)

add(
    id="17", crumb="17. File Upload", title="Chương 17: File Upload",
    lede="Upload không phải “lưu file”. Đó là parser, thumbnail, và chỗ execute nếu nhầm path.",
    part="V — Server-side", desc="Upload: type, size, storage, không execute, virus scan.",
    tags=["upload", "content-type"],
    body=h2("khai-niem", "Khái niệm")
    + p("Rủi ro: extension kép, MIME do client, file polyglot, path traversal tên file, store trên origin executable (PHP trong webroot), XXE/image magick.")
    + h2("phong", "Phòng chống")
    + ul(["Allowlist MIME + magic bytes server-side.", "Tên file random; không dùng tên user làm path.", "Store object storage, không webroot.", "Serve với Content-Disposition attachment + nosniff.", "Giới hạn size; quét malware trên async worker.", "Resize ảnh bằng lib an toàn, patch ImageMagick."])
    + h2("devops", "Góc nhìn DevOps")
    + p("Bucket private + signed URL. CDN không execute. Pod upload không quyền write trừ volume dedicated.")
    + tom("Đừng tin extension client.", "Object storage.", "Không execute upload.", "Signed URL.")
    + quiz("Content-Type từ browser đủ không?", "Vì sao cấm lưu dưới /static user?", "Polyglot là gì?", "nosniff giúp gì?", "Lambda/worker scan virus đặt đâu?")
)

add(
    id="18", crumb="18. Path Traversal", title="Chương 18: Path Traversal",
    lede="Ghép path từ user rồi đọc file. Dấu chấm chấm vẫn là bug 30 năm.",
    part="V — Server-side", desc="Path traversal, canonicalize, chroot, object key.",
    tags=["path-traversal", "lfi"],
    body=h2("khai-niem", "Khái niệm")
    + p("Input <code>../</code> hoặc encoding đi ra ngoài thư mục cho phép. Ảnh hưởng read file config, key, hoặc ghi đè.")
    + h2("phong", "Phòng chống")
    + ul(["Không ghép path user; dùng ID → object key map.", "Canonicalize rồi kiểm tra prefix nằm trong root.", "OS allowlist filename charset.", "Least privilege FS; không chạy root."])
    + h2("devops", "Góc nhìn DevOps")
    + p("readOnlyRootFilesystem; volume chỉ data dir. Secret không mount vào chỗ app “download template”.")
    + tom("Map ID → file.", "Canonical path check.", "FS hẹp.", "Không tin encoding một lần.")
    + quiz("Canonicalize giải quyết gì?", "URL encoding traversal né filter thế nào (ý tưởng)?", "Object storage key user-controlled rủi ro?", "readOnlyRootFS đủ không?", "Log path đã resolve để làm gì?")
)

add(
    id="19", crumb="19. Open Redirect", title="Chương 19: Open Redirect",
    lede="redirect=https://… nghe hiền. Phishing và token trên URL thì không.",
    part="V — Server-side", desc="Open redirect, allowlist, OAuth redirect.",
    tags=["open-redirect", "oauth"],
    body=h2("khai-niem", "Khái niệm")
    + p("Param redirect đưa user sang host attacker. Dùng trong phishing và đôi khi chuỗi OAuth/token.")
    + h2("phong", "Phòng chống")
    + ul(["Allowlist path nội bộ (relative) hoặc host cố định.", "Cấm scheme lạ (javascript:, //evil).", "OAuth: exact redirect_uri."])
    + h2("devops", "Góc nhìn DevOps")
    + p("WAF rule mở; control chính là code/IdP config. Không log full URL có token.")
    + tom("Allowlist đích.", "Relative path an toàn hơn URL đầy đủ.", "OAuth URI chặt.")
    + quiz("Open redirect thành phishing thế nào?", "//host khác https://host chỗ nào?", "Vì sao next=/dashboard ổn hơn next=https://…?", "Liên quan OAuth?", "Header Location có cần allowlist?")
)

add(
    id="20", crumb="20. Race Condition", title="Chương 20: Race Condition",
    lede="Hai request cùng lúc. Số dư, coupon, unique constraint — ai commit trước.",
    part="V — Server-side", desc="TOCTOU, idempotency, locking, unique constraints.",
    tags=["race", "idempotency"],
    body=h2("khai-niem", "Khái niệm")
    + p("Time-of-check vs time-of-use: kiểm tra còn 1 coupon rồi hai request đều redeem. Cần atomicity trên DB, không “if” trên app đơn luồng.")
    + h2("phong", "Phòng chống")
    + ul(["Transaction + constraint unique.", "Idempotency-Key trên API thanh toán.", "Lock pessimistic/optimistic version.", "Hàng đợi một consumer cho nghiệp vụ tiền."])
    + h2("devops", "Góc nhìn DevOps")
    + p("N replica không tạo race — DB mới là chỗ arbitrate. Rate-limit không thay unique constraint. Test load lab trên endpoint tiền.")
    + tom("Atomic DB.", "Idempotency key.", "Đừng tin check-then-act.", "Scale-out làm race dễ lộ hơn.")
    + quiz("TOCTOU nghĩa là gì?", "Unique constraint cứu coupon thế nào?", "Idempotency-Key dùng khi nào?", "Vì sao 1 replica app vẫn race?", "Queue giúp gì?")
)

add(
    id="21", crumb="21. Business Logic", title="Chương 21: Business Logic",
    lede="Mọi scanner xanh. Workflow vẫn sai: giá âm, bước nhảy, hoàn tiền kép.",
    part="V — Server-side", desc="Business logic flaws, workflow, negative tests.",
    tags=["business-logic", "abuse"],
    body=h2("khai-niem", "Khái niệm")
    + p("Lỗ logic: đúng auth nhưng sai luật nghiệp vụ — đổi giá client-side, skip bước verify, voucher stack. Không có CVE chung; cần threat model.")
    + h2("phong", "Phòng chống")
    + ul(["Giá / role / hạn mức chỉ tin server.", "State machine đơn hàng: transition hợp lệ.", "Giới hạn abuse (số lần trial).", "Test negative: bước 3 không gọi khi chưa bước 2."])
    + h2("devops", "Góc nhìn DevOps")
    + p("Feature flag không thay validation. Log business event (refund, role change). Rate-limit API tiền.")
    + tom("Server là nguồn sự thật.", "State machine.", "Test abuse.", "Log nghiệp vụ.")
    + quiz("Vì sao DAST bỏ sót logic?", "Giá trên JSON client sai chỗ nào?", "Voucher stacking là lớp gì?", "Event refund nên log field nào?", "Rate-limit khác authz?")
)

add(
    id="26", crumb="26. Deserialization", title="Chương 26: Insecure Deserialization",
    lede="Unpickle / Java gadget / PHP unserialize từ dữ liệu user. Object thành code path.",
    part="V — Server-side", desc="Insecure deserialization, avoid native pickle, signed tokens.",
    tags=["deserialization", "rce"],
    body=h2("khai-niem", "Khái niệm")
    + p("Deserialize dữ liệu không tin được có thể gọi constructor/magic và gadget chain. Cookie PHP serialized, Java session, Python pickle, YAML load — cùng lớp.")
    + h2("phong", "Phòng chống")
    + ul(["JSON schema, không pickle/unserialize user.", "Nếu bắt buộc: chữ ký + allowlist class.", "Thư viện YAML safe load.", "Tách network service deserialize."])
    + h2("devops", "Góc nhìn DevOps")
    + p("Redis/session không nhận blob lạ từ client. Dependency gadget: SCA. Runtime: non-root.")
    + tom("Đừng deserialize input thô.", "JSON + schema.", "SCA gadget.", "Ký blob nếu bắt buộc.")
    + quiz("Pickle khác JSON chỗ nào?", "Cookie serialized PHP rủi ro?", "safe_load YAML?", "Gadget chain nghĩa là gì (ý tưởng)?", "Session store tin client blob khi nào sai?")
)

# --- Part VI ---
add(
    id="23", crumb="23. Cache Poisoning", title="Chương 23: Web Cache Poisoning",
    lede="Cache nhớ response theo key sai. Một header độc hại thành trang của mọi user.",
    part="VI — Infra", desc="Web cache poisoning, cache key, unkeyed headers, CDN.",
    tags=["cache", "cdn", "http"],
    body=h2("khai-niem", "Khái niệm")
    + p("CDN/Varnish key thường Host + path. Header/query không nằm trong key nhưng làm đổi body → poison. Unkeyed header (X-Forwarded-Host, malformed Accept) hay gặp.")
    + h2("phong", "Phòng chống")
    + ul(["Cache key gồm mọi input ảnh hưởng response.", "Không tin Host/XFH chưa allowlist (Chương 2).", "Tách cache cookie-personalized vs static.", "Normalize URL; không cache response lỗi lạ."])
    + h2("devops", "Góc nhìn DevOps")
    + p("Cloudflare/Fastly cache rules là production. Review “cache everything”. Purge khi incident. Vary header đúng.")
    + tom("Key = mọi input ảnh hưởng body.", "Allowlist Host.", "Đừng cache HTML cá nhân hóa như static.", "Purge playbook.")
    + quiz("Unkeyed header là gì?", "X-Forwarded-Host liên quan poison?", "Vary dùng để làm gì?", "Cache everything trên HTML login?", "Poison khác XSS stored chỗ nào?")
)

add(
    id="24", crumb="24. Request Smuggling", title="Chương 24: HTTP Request Smuggling",
    lede="Front-end và back-end bất đồng CL vs TE. Request của bạn dính request người sau.",
    part="VI — Infra", desc="HTTP request smuggling, Content-Length vs Transfer-Encoding, HTTP/2.",
    tags=["smuggling", "http", "proxy"],
    body=h2("khai-niem", "Khái niệm")
    + p("Smuggling khi proxy và origin parse ranh giới request khác nhau (Content-Length vs Transfer-Encoding, HTTP/2 downgrade). Hậu quả: cache poison, bypass WAF, bắt request khác. Khai thác cụ thể chỉ trên lab được phép.")
    + h2("phong", "Phòng chống")
    + ul(["Cùng HTTP version end-to-end khi được (h2c cẩn thận).", "Tắt TE trên hop không cần; normalize request ở một chỗ.", "Cập nhật Nginx/Envoy/Ingress — bug parser là CVE.", "WAF và origin cùng cách đếm body."])
    + h2("devops", "Góc nhìn DevOps")
    + p("Đây là lỗ hạ tầng. Patch Ingress. Không mix custom proxy tự viết. HTTP/2 chỉ terminate một lớp rồi h2 hoặc h1 thống nhất phía sau.")
    + tom("Một parser chuẩn.", "Patch proxy.", "Đừng tự ghép CL+TE.", "Lab, không production probing mù.")
    + quiz("CL vs TE bất đồng gây gì?", "Vì sao HTTP/2 downgrade liên quan?", "Ai chịu patch?", "WAF bypass ý tưởng (không PoC)?", "Normalize request nghĩa là gì?")
)

# --- Part VII ---
add(
    id="27", crumb="27. GraphQL", title="Chương 27: GraphQL Security",
    lede="Một endpoint, nhiều field. Introspection, IDOR, và query sâu là DoS miễn phí.",
    part="VII — API", desc="GraphQL introspection, depth limit, IDOR resolvers, batching.",
    tags=["graphql", "api"],
    body=h2("khai-niem", "Khái niệm")
    + p("GraphQL: client chọn shape dữ liệu. Authz phải nằm từng resolver, không chỉ “đã login”.")
    + h2("rui-ro", "Rủi ro")
    + ul(["Introspection production → lộ schema.", "IDOR: query node(id) thiếu check.", "Batching / alias phá rate-limit.", "Query sâu / circular → CPU DoS."])
    + h2("phong", "Phòng chống")
    + ul(["Tắt introspection prod; persist queries nếu được.", "Authz per field.", "Depth/complexity limit; timeout.", "Rate-limit theo cost không theo request count."])
    + h2("devops", "Góc nhìn DevOps")
    + p("Timeout Envoy. Không cache GraphQL POST mù. Schema file không public bucket.")
    + tom("Resolver authz.", "Limit depth/cost.", "Tắt introspection prod.", "Rate-limit theo cost.")
    + quiz("Introspection hại gì?", "IDOR GraphQL khác REST?", "Vì sao rate-limit theo request fail?", "Persisted query giúp gì?", "Timeout đặt ở đâu?")
)

add(
    id="28", crumb="28. API Security", title="Chương 28: API Security",
    lede="OWASP API Top 10: object authz, mass assignment, rate-limit, version already-dead.",
    part="VII — API", desc="BOLA, mass assignment, API rate limit, versioning, gateway.",
    tags=["api", "bola", "owasp"],
    body=h2("khai-niem", "Khái niệm")
    + p("API không HTML — CSRF cookie khác, BOLA (IDOR) là số 1. Auth: token, mTLS service-to-service.")
    + h2("bola", "BOLA / object authz")
    + p("Giống Chương 6: mọi GET/PATCH theo id phải check sở hữu.")
    + h2("mass", "Mass assignment")
    + p("Bind JSON thẳng vào model: client gửi <code>role</code>/<code>balance</code>. Allowlist field.")
    + h2("rate", "Rate limiting")
    + p("Theo user + IP + cost. 429 + backoff. Trên gateway và app.")
    + h2("version", "Versioning")
    + p("v1 không vá vẫn live. Sunset header; tắt path cũ trên Ingress.")
    + h2("devops", "Góc nhìn DevOps")
    + p("API gateway: JWT, quota, schema validation. OpenAPI làm contract test. Không public swagger prod nếu không cần.")
    + tom("Object-level authz.", "Allowlist field.", "Quota.", "Tắt API già.")
    + quiz("BOLA là gì?", "Mass assignment ví dụ field?", "429 nên kèm gì?", "Swagger public rủi ro?", "mTLS dùng khi nào?")
)

# --- Part VIII ---
add(
    id="29", crumb="29. Kubernetes", title="Chương 29: Kubernetes Security liên quan web",
    lede="Ingress, SA token, secret env, NetworkPolicy — web bug đội cánh cluster.",
    part="VIII — DevOps", desc="Ingress, SSRF to kube API, PSS, NetworkPolicy, image, secrets.",
    tags=["kubernetes", "ingress", "pss"],
    body=h2("khai-niem", "Khái niệm")
    + p("Web app trên K8s thừa attack surface: API server, etcd, IMDS, sidecar. Control cluster là hàng rào khi app lỗi.")
    + h2("ingress", "Ingress")
    + ul(["TLS, security headers (Chương 2).", "Không expose dashboard / admin.", "snippet annotation cẩn thận (inject config)."])
    + h2("ssrf-k8s", "SSRF tới Kubernetes API")
    + p("Pod có SA token mặc định + SSRF = gọi API. Tắt automount; RBAC hẹp; egress deny API.")
    + h2("secrets-k8s", "Secrets")
    + p("Không env nếu có thể (còn dump /proc). Volume file + KMS encryption etcd. Không secret trong image/Helm default.")
    + h2("pss", "Pod Security")
    + p("restricted PSS: non-root, drop caps, no priv-esc, seccomp. Policy namespace.")
    + h2("np", "NetworkPolicy")
    + p("Default deny ingress/egress; allow DNS + DB + IdP.")
    + h2("image", "Image")
    + p("Digest pin, scan CI, distroless, không latest.")
    + tom("Không automount SA.", "PSS restricted.", "NP default deny.", "Secret không plaintext Git.")
    + quiz("Automount SA + SSRF?", "PSS restricted cấm gì?", "Env secret lộ đường nào?", "Ingress snippet rủi ro?", "Pin digest khác tag?")
)

add(
    id="30", crumb="30. CI/CD", title="Chương 30: CI/CD Security",
    lede="Pipeline là production. Ai push YAML là ai ship code lên cluster.",
    part="VIII — DevOps", desc="Pipeline injection, dependency confusion, secrets CI, SAST DAST SCA.",
    tags=["cicd", "supply-chain"],
    body=h2("khai-niem", "Khái niệm")
    + p("CI/CD đọc PR, secret cloud, deploy. Lỗ pipeline = lỗ prod.")
    + h2("rui-ro", "Rủi ro")
    + ul(["Script inj từ tên nhánh / PR untrusted (script injection).", "Dependency confusion: package nội bộ bị cướp tên public.", "Secret trong log / variable unmasked.", "Supply chain: action/tag GitHub không pin hash.", "Self-hosted runner không isolate."])
    + h2("scan", "SAST / DAST / SCA")
    + p("SCA sớm (Trivy/Snyk). SAST PR. DAST staging. Fail build mức critical có SLA.")
    + h2("phong", "Phòng chống")
    + ul(["Least privilege OIDC to cloud, không long-lived key.", "Pin actions SHA.", "Tách privileged pipeline.", "Signed artifact + admission verify."])
    + tom("Pin dependencies/actions.", "OIDC ngắn hạn.", "Không secret log.", "Gate scan.")
    + quiz("Dependency confusion?", "Vì sao pin SHA action?", "OIDC hơn static key?", "DAST chạy đâu?", "PR từ fork chạy privileged job sai chỗ nào?")
)

add(
    id="31", crumb="31. Secrets", title="Chương 31: Secrets Management",
    lede="Secret trong Git là incident đã xảy ra, chưa bị khai thác thôi.",
    part="VIII — DevOps", desc="Secret scan, Vault, cloud managers, External Secrets, rotation.",
    tags=["secrets", "vault", "eso"],
    body=h2("khai-niem", "Khái niệm")
    + p("Secret: key, token, cert, mật khẩu. Vòng đời: tạo, phân phối, rotate, revoke, audit.")
    + h2("scan", "Scanning")
    + p("gitleaks/trufflehog trên pre-commit + CI + lịch sử. Rotate ngay khi lộ.")
    + h2("tools", "Công cụ")
    + ul(["Vault / cloud secret manager: dynamic DB creds.", "External Secrets Operator: sync vào K8s Secret đã mã hóa rest.", "Sealed Secrets: chỉ nếu hiểu model giải mã."])
    + h2("bp", "Best practices")
    + ul(["Không env trên frontend.", "Rotate + dual-run.", "Audit who read.", "Tách secret per env."])
    + tom("Scan Git.", "Central manager.", "Rotate.", "Audit access.")
    + quiz("Phát hiện secret Git lúc nào là trễ?", "Dynamic secret hơn static?", "ESO giải quyết gì?", "K8s Secret etcd plaintext khi nào?", "Frontend env NEXT_PUBLIC_ chứa gì thì sai?")
)

add(
    id="32", crumb="32. Cloud", title="Chương 32: Cloud Security liên quan web",
    lede="IMDS, IAM *, bucket public — web app chỉ là client của cloud API.",
    part="VIII — DevOps", desc="IMDS, IAM, S3/GCS exposure, WAF, metadata.",
    tags=["cloud", "iam", "imds"],
    body=h2("imds", "IMDS và credential")
    + p("SSRF + IMDS = key node. Bật IMDSv2, hop limit, deny metadata từ Pod.")
    + h2("iam", "IAM")
    + p("Không * trên prod role. IRSA/Workload Identity thay key file. Boundary + deny IAM create.")
    + h2("bucket", "Object storage")
    + p("Block public ACL; policy; encryption; access log. Static site bucket ≠ backup bucket.")
    + h2("check", "Checklist nhanh")
    + ul(["WAF + TLS + Shield/Armor tùy cloud.", "SG/NACL: DB không 0.0.0.0/0.", "CloudTrail/Activity log bật.", "Secret manager, không plaintext VM."])
    + tom("IMDSv2.", "Least privilege IAM.", "Bucket không public mặc định.", "Audit cloud API.")
    + quiz("IMDSv2 khác v1?", "IRSA tránh được gì?", "Public list bucket hại gì?", "CloudTrail dùng IR?", "WAF thay IAM?")
)

add(
    id="33", crumb="33. Logging", title="Chương 33: Logging và Detection",
    lede="A09: không log thì không incident — chỉ có tin đồn.",
    part="VIII — DevOps", desc="What to log, what not, SIEM, detection rules.",
    tags=["logging", "detection", "siem"],
    body=h2("what", "What to log")
    + ul(["Authn: success/fail/MFA/reset, id, IP, UA.", "Authz deny (403) với object id.", "Admin / money actions.", "4xx/5xx spike, WAF block.", "K8s audit: secret get, rbac bind."])
    + h2("not", "Không log")
    + p("Password, cookie, Authorization, card, token query. Mask. Retention và mã hóa at rest.")
    + h2("detect", "Detection")
    + ul(["Spray: fail login nhiều user một IP.", "IDOR: 403/200 xen kẽ cùng user khác id.", "SSRF: app gọi 169.254.", "Privilege: RoleBinding cluster-admin."])
    + h2("stack", "Stack")
    + p("OTLP/Loki/ELK + alert. Pipeline parse JSON structured. Time sync NTP.")
    + tom("Structured log.", "Không secret.", "Alert abuse.", "K8s audit song song app.")
    + quiz("Field auth nên có?", "Vì sao không log Authorization?", "Spray vs brute một user?", "Audit Secret get?", "Retention vs forensic?")
)

add(
    id="34", crumb="34. Incident Response", title="Chương 34: Incident Response cơ bản",
    lede="Runbook trước 3 giờ sáng. Không improvisation trên prod đang chảy máu.",
    part="VIII — DevOps", desc="IR lifecycle, contain, forensics nhẹ, comms, post-mortem.",
    tags=["ir", "incident"],
    body=h2("lifecycle", "Lifecycle")
    + p("Prepare → Detect → Contain → Eradicate → Recover → Lessons. Prepare là exercise + quyền break-glass.")
    + h2("detect", "Detection")
    + p("Alert Chương 33. On-call biết dashboard. Severity: data leak / RCE / deface khác SLA.")
    + h2("contain", "Containment")
    + ul(["Cắt Ingress / scale 0 / NP deny.", "Rotate secret + session invalidate.", "Isolate namespace.", "Không xóa log/pod trước khi snapshot."])
    + h2("forensics", "Forensics tối thiểu")
    + p("Timeline log, kubectl describe/events, image digest đang chạy, audit API. Snapshot volume nếu cần. Chuỗi custody nội bộ.")
    + h2("comms", "Communication")
    + p("Kênh riêng, pháp chế nếu PII. Không tweet root cause sớm. Status page sự thật.")
    + h2("pm", "Post-mortem")
    + p("Blameless: timeline, gap control, ticket vá, game-day.")
    + tom("Prepare.", "Contain trước forensics đầy đủ.", "Rotate.", "Học ra ticket.")
    + quiz("Contain khác eradicate?", "Vì sao không xóa Pod ngay?", "Break-glass account?", "Ai nói với khách?", "Metric thành công IR?")
)

add(
    id="35", crumb="35. Checklist", title="Chương 35: Checklist bảo mật cho DevOps",
    lede="Một trang trước mỗi deploy. Không thay threat model, nhưng bắt được 80% sơ suất.",
    part="VIII — DevOps", desc="Checklist deploy, K8s, CI/CD, monitoring.",
    tags=["checklist", "devops"],
    body=h2("deploy", "Deploy / app")
    + ul(["TLS + HSTS + headers Chương 2.", "Cookie flags.", "Không secret Git.", "Authz server-side; không admin public.", "Rate-limit login/API tiền.", "CORS allowlist.", "DB bind param + role hẹp."])
    + h2("k8s", "Container / K8s")
    + ul(["PSS restricted.", "NP default deny.", "SA không automount.", "Image digest + scan.", "Resource limit.", "readOnlyRootFS khi được.", "Secret KMS."])
    + h2("cicd", "CI/CD")
    + ul(["SCA/SAST gate.", "Pin actions.", "OIDC cloud.", "Signed artifact.", "Không secret log.", "DAST staging."])
    + h2("mon", "Monitoring")
    + ul(["Auth + 403 + WAF log.", "Alert spray / 500 / egress lạ.", "Backup restore đã test.", "On-call runbook IR."])
    + tom("Headers + TLS.", "PSS + NP.", "Scan gate.", "Log/alert/IR.")
    + quiz("Mục nào DevOps “sở hữu” nếu app team trễ authz?", "Digest vs latest?", "Checklist thay pentest?", "Mục nào liên A05/A09?", "Ai sign-off checklist?")
)

add(
    id="appendix", crumb="Appendix", title="Phụ lục: Lộ trình 30 ngày",
    lede="Một tháng để đọc series và làm lab được phép — không phải trở thành pentester.",
    part="Appendix", desc="Lộ trình 30 ngày Web Security cho DevOps: lab PortSwigger, không test hệ thống ngoài scope.",
    tags=["roadmap", "learning"],
    body=h2("tong-quan", "Tổng quan")
    + p("Mỗi ngày: đọc chương + lab PortSwigger/Juice Shop local. Không test prod người khác.")
    + h2("w1", "Tuần 1 — Nền tảng")
    + ul(["Ngày 1: lab DVWA/Juice Shop local, Burp CA.", "Ngày 2–3: HTTP + Burp History/Repeater.", "Ngày 4–5: Authentication.", "Ngày 6–7: Session + Access Control."])
    + h2("w2", "Tuần 2 — Injection & XSS")
    + ul(["8–9: SQLi lab Academy.", "10: NoSQL + command injection khái niệm + lab.", "11–12: XSS + CSP trên app bạn.", "13–14: SSRF/XXE — chú IMDS trên cloud lab của bạn."])
    + h2("w3", "Tuần 3 — Protocol & client")
    + ul(["15–16: OAuth/JWT config IdP.", "17–18: CORS/CSRF trên SPA.", "19–20: Upload + path.", "21: Race + logic — test tiền trên staging."])
    + h2("w4", "Tuần 4 — Infra & DevOps")
    + ul(["22–23: Clickjacking, cache, smuggling (đọc + patch Ingress).", "24–25: SSTI/deserialize — review code.", "26–27: GraphQL/API gateway.", "28–29: K8s/CI/secrets/cloud checklist.", "30: IR tabletop + ghi gap."])
    + h2("res", "Tài nguyên")
    + ul(["PortSwigger Academy, OWASP WSTG, k8s.io security.", "Trivy, gitleaks, kube-score, Falco.", "CKS notes nếu bạn thi CNCF."])
    + bq("Mindset: vá control, không sưu tầm payload. Tracking: checklist Chương 35.")
    + tom("Lab hợp pháp.", "Đọc + làm.", "Tuần 4 mang vào cluster thật của bạn.", "Gap → ticket.")
    + quiz("Vì sao tuần 1 trước injection?", "Lab SSRF trên cloud công ty khi nào được?", "Ngày 30 nên ra artifact gì?", "Academy thay production scan?", "Làm song song CKS thế nào?")
)


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    for ch in CHAPTERS:
        html = wrap(ch["id"], ch["crumb"], ch["title"], ch["lede"], ch["part"], ch["desc"], ch["body"], ch["tags"])
        d = ROOT / ch["id"]
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(html, encoding="utf-8")
        print("wrote", ch["id"])
    print("total", len(CHAPTERS))


if __name__ == "__main__":
    main()
