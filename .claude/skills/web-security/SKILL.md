---
name: web-security
description: Use me for web application security reviews covering XSS prevention, CSRF protection, clickjacking prevention, content security policy (CSP), security headers, cookie security, and OWASP Top 10 web vulnerabilities. I return ASVS-mapped findings with rule IDs and secure code examples.
version: 1.0.0
domains:
  - xss-prevention
  - csrf-protection
  - clickjacking
  - content-security-policy
allowed-tools: Read, Grep, Bash
---

# Web Security Skill

**I provide web application security guidance following ASVS, OWASP Top 10, and CWE standards.**

**Complete Security Rules**: [rules.json](./rules.json) | 9 ASVS-aligned web security rules with detection patterns

## Activation Triggers

**I respond to these queries and tasks**:
- Cross-Site Scripting (XSS) prevention and detection
- Cross-Site Request Forgery (CSRF) protection
- Clickjacking prevention (X-Frame-Options, CSP frame-ancestors)
- Content Security Policy (CSP) implementation
- Security headers configuration (HSTS, X-Content-Type-Options)
- Cookie security (HttpOnly, Secure, SameSite)
- Open redirect vulnerability prevention
- Server-Side Request Forgery (SSRF) prevention
- Subdomain takeover risks

**Manual activation**: Use `/web-security` or mention "web security review"

**Agent variant**: For parallel analysis with other security checks, use the `web-security-specialist` agent via the Task tool

## Security Knowledge Base

### XSS Prevention (3 rules)
- Output encoding context-aware (HTML, JavaScript, URL, CSS)
- Content Security Policy (CSP) with nonce/hash for inline scripts
- Input validation and sanitization
- Use template engines with auto-escaping
- Validate and sanitize all user input
- Never use innerHTML with untrusted data

### CSRF Protection (2 rules)
- Use CSRF tokens for state-changing requests
- Validate Origin/Referer headers
- Use SameSite cookie attribute
- Require re-authentication for sensitive operations
- Never use GET for state-changing operations

### Clickjacking Prevention (1 rule)
- Set X-Frame-Options: DENY or SAMEORIGIN
- Use CSP frame-ancestors directive
- Implement frame-busting code as defense-in-depth
- Consider UI redress attack vectors

### Security Headers (3 rules)
- Implement HSTS with includeSubDomains and preload
- Set X-Content-Type-Options: nosniff
- Configure X-XSS-Protection (legacy browsers)
- Set Referrer-Policy
- Use Permissions-Policy to restrict features

## Common Vulnerabilities

| Vulnerability | Severity | CWE | OWASP Top 10 |
|--------------|----------|-----|--------------|
| Reflected XSS | **HIGH** | CWE-79 | A03:2021 Injection |
| Stored XSS | **CRITICAL** | CWE-79 | A03:2021 Injection |
| DOM-based XSS | **HIGH** | CWE-79 | A03:2021 Injection |
| Missing CSRF protection | **HIGH** | CWE-352 | A01:2021 Broken Access Control |
| Clickjacking (no X-Frame-Options) | **MEDIUM** | CWE-1021 | A04:2021 Insecure Design |
| Missing CSP | **MEDIUM** | CWE-1021 | A05:2021 Security Misconfiguration |
| Open redirect | **MEDIUM** | CWE-601 | A01:2021 Broken Access Control |
| SSRF | **HIGH** | CWE-918 | A10:2021 SSRF |

## Detection Patterns

**I scan for these security issues**:

### XSS Prevention
```javascript
// ❌ VULNERABLE: Direct HTML injection
app.get('/search', (req, res) => {
  const query = req.query.q;
  res.send(`<h1>Results for: ${query}</h1>`);  // XSS!
});

// ❌ VULNERABLE: innerHTML with user data
document.getElementById('result').innerHTML = userInput;  // XSS!

// ❌ VULNERABLE: eval() or Function() with user input
eval(userCode);  // Code injection!

// ✅ SECURE: Context-aware output encoding
const escapeHtml = (unsafe) => {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
};

app.get('/search', (req, res) => {
  const query = escapeHtml(req.query.q);
  res.send(`<h1>Results for: ${query}</h1>`);
});

// ✅ SECURE: Use textContent (not innerHTML)
document.getElementById('result').textContent = userInput;  // Safe!

// ✅ SECURE: Template engine with auto-escaping (React, Vue, Angular)
function SearchResults({ query }) {
  return <h1>Results for: {query}</h1>;  // Auto-escaped
}

// ✅ SECURE: CSP with nonce for inline scripts
const cspNonce = crypto.randomBytes(16).toString('base64');
res.setHeader(
  'Content-Security-Policy',
  `default-src 'self'; script-src 'self' 'nonce-${cspNonce}'; object-src 'none';`
);
res.send(`
  <script nonce="${cspNonce}">
    // Inline script allowed with nonce
  </script>
`);
```

### CSRF Protection
```python
# ❌ VULNERABLE: No CSRF protection
@app.route('/transfer', methods=['POST'])
def transfer():
    amount = request.form['amount']
    recipient = request.form['recipient']
    perform_transfer(current_user, recipient, amount)  # CSRF vulnerable!
    return "Transfer complete"

# ❌ VULNERABLE: Using GET for state changes
@app.route('/delete/<int:item_id>')  # GET method - CSRF risk!
def delete_item(item_id):
    Item.query.filter_by(id=item_id).delete()
    return "Deleted"

# ✅ SECURE: CSRF token validation
from flask_wtf.csrf import CSRFProtect, generate_csrf

csrf = CSRFProtect(app)

@app.route('/transfer', methods=['POST'])
@csrf_protect  # Validates CSRF token
def transfer():
    amount = request.form['amount']
    recipient = request.form['recipient']

    # Double-check: validate Origin header
    origin = request.headers.get('Origin')
    if origin and origin not in ALLOWED_ORIGINS:
        abort(403, "Invalid origin")

    perform_transfer(current_user, recipient, amount)
    return "Transfer complete"

# Template: Include CSRF token
'''
<form method="POST" action="/transfer">
  <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
  <input type="text" name="amount"/>
  <input type="text" name="recipient"/>
  <button type="submit">Transfer</button>
</form>
'''

# ✅ SECURE: SameSite cookie for defense-in-depth
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Strict',  # Prevents CSRF via cookies
    WTF_CSRF_SSL_STRICT=True
)

# ✅ SECURE: Custom header validation (for APIs)
@app.route('/api/transfer', methods=['POST'])
def api_transfer():
    # Require custom header (can't be set by forms)
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        abort(403, "Missing X-Requested-With header")

    # Validate Origin/Referer
    origin = request.headers.get('Origin')
    if not origin or origin not in ALLOWED_ORIGINS:
        abort(403, "Invalid origin")

    # Process request
    data = request.get_json()
    perform_transfer(current_user, data['recipient'], data['amount'])
    return jsonify({"status": "success"})
```

### Clickjacking Prevention
```java
// ❌ VULNERABLE: No clickjacking protection
@Configuration
public class SecurityConfig {
    // Missing X-Frame-Options!
}

// ✅ SECURE: X-Frame-Options and CSP
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .headers(headers -> headers
                // Prevent clickjacking
                .frameOptions(frame -> frame.deny())  // X-Frame-Options: DENY

                // CSP with frame-ancestors (more flexible than X-Frame-Options)
                .contentSecurityPolicy(csp -> csp
                    .policyDirectives("default-src 'self'; " +
                        "frame-ancestors 'none';")  // No framing allowed
                )
            );

        return http.build();
    }
}

// ✅ SECURE: Allow framing from specific domains
http.headers().contentSecurityPolicy(
    "default-src 'self'; frame-ancestors 'self' https://trusted-site.com;"
);
```

### Content Security Policy (CSP)
```javascript
// ❌ VULNERABLE: No CSP or permissive CSP
// No CSP header at all!

// ❌ VULNERABLE: Overly permissive CSP
res.setHeader('Content-Security-Policy', "default-src *");  // Allows everything!

// ❌ VULNERABLE: 'unsafe-inline' and 'unsafe-eval'
res.setHeader(
  'Content-Security-Policy',
  "script-src 'self' 'unsafe-inline' 'unsafe-eval'"  // Defeats XSS protection!
);

// ✅ SECURE: Strict CSP with nonce
const crypto = require('crypto');

app.use((req, res, next) => {
  // Generate nonce for this request
  const nonce = crypto.randomBytes(16).toString('base64');
  res.locals.cspNonce = nonce;

  // Set strict CSP
  res.setHeader(
    'Content-Security-Policy',
    [
      `default-src 'self'`,
      `script-src 'self' 'nonce-${nonce}'`,  // Only allow scripts with nonce
      `style-src 'self' 'nonce-${nonce}'`,
      `img-src 'self' data: https:`,
      `font-src 'self'`,
      `connect-src 'self'`,
      `frame-ancestors 'none'`,  // Clickjacking protection
      `base-uri 'self'`,  // Prevent base tag injection
      `form-action 'self'`,  // Restrict form submissions
      `upgrade-insecure-requests`  // Upgrade HTTP to HTTPS
    ].join('; ')
  );

  next();
});

// Template usage with nonce
app.get('/', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
      <script nonce="${res.locals.cspNonce}">
        // Inline script allowed with nonce
        console.log('Protected by CSP');
      </script>
    </head>
    <body>
      <h1>CSP Protected Page</h1>
    </body>
    </html>
  `);
});

// ✅ SECURE: CSP with hash (for static inline scripts)
const scriptHash = 'sha256-abc123...';  // Hash of script content
res.setHeader(
  'Content-Security-Policy',
  `script-src 'self' '${scriptHash}'`
);

// ✅ SECURE: Report-Only mode for testing
res.setHeader(
  'Content-Security-Policy-Report-Only',
  `default-src 'self'; report-uri /csp-report`
);

app.post('/csp-report', express.json({ type: 'application/csp-report' }), (req, res) => {
  console.log('CSP Violation:', req.body);
  res.status(204).end();
});
```

### Open Redirect Prevention
```python
# ❌ VULNERABLE: Unvalidated redirect
@app.route('/redirect')
def redirect_user():
    url = request.args.get('url')
    return redirect(url)  # Open redirect!
    # Attacker: /redirect?url=https://evil.com/phishing

# ❌ VULNERABLE: Weak validation
@app.route('/redirect')
def redirect_user():
    url = request.args.get('url')
    if url.startswith('http'):  # Still vulnerable!
        return redirect(url)

# ✅ SECURE: Whitelist-based validation
ALLOWED_REDIRECT_DOMAINS = [
    'example.com',
    'www.example.com',
    'app.example.com'
]

@app.route('/redirect')
def redirect_user():
    url = request.args.get('url')

    # Parse URL
    try:
        parsed = urlparse(url)
    except Exception:
        abort(400, "Invalid URL")

    # Validate scheme
    if parsed.scheme not in ['http', 'https']:
        abort(400, "Invalid URL scheme")

    # Validate domain against whitelist
    if parsed.netloc not in ALLOWED_REDIRECT_DOMAINS:
        abort(400, "Redirect to external domain not allowed")

    return redirect(url)

# ✅ SECURE: Relative URL only (safest)
@app.route('/redirect')
def redirect_user():
    path = request.args.get('path', '/')

    # Only allow relative paths (no domain)
    if path.startswith('/') and not path.startswith('//'):
        return redirect(path)
    else:
        abort(400, "Only relative redirects allowed")
```

### SSRF Prevention
```java
// ❌ VULNERABLE: User-controlled URL in HTTP request
@PostMapping("/fetch")
public String fetchUrl(@RequestParam String url) throws IOException {
    URL targetUrl = new URL(url);  // SSRF vulnerability!
    URLConnection conn = targetUrl.openConnection();
    return IOUtils.toString(conn.getInputStream());
    // Attacker: url=http://169.254.169.254/latest/meta-data/
}

// ✅ SECURE: URL validation and allowlist
import java.net.*;
import java.util.Set;

@PostMapping("/fetch")
public String fetchUrl(@RequestParam String url) throws IOException {
    // Parse and validate URL
    URL targetUrl;
    try {
        targetUrl = new URL(url);
    } catch (MalformedURLException e) {
        throw new BadRequestException("Invalid URL");
    }

    // Validate scheme (only HTTP/HTTPS)
    String scheme = targetUrl.getProtocol();
    if (!scheme.equals("http") && !scheme.equals("https")) {
        throw new BadRequestException("Invalid URL scheme");
    }

    // Validate against allowlist
    Set<String> allowedHosts = Set.of(
        "api.example.com",
        "cdn.example.com"
    );

    if (!allowedHosts.contains(targetUrl.getHost())) {
        throw new BadRequestException("Host not allowed");
    }

    // Block private IP ranges
    InetAddress addr = InetAddress.getByName(targetUrl.getHost());
    if (isPrivateOrLocalAddress(addr)) {
        throw new BadRequestException("Private IP addresses not allowed");
    }

    // Make request with timeout
    URLConnection conn = targetUrl.openConnection();
    conn.setConnectTimeout(5000);
    conn.setReadTimeout(5000);

    return IOUtils.toString(conn.getInputStream());
}

private boolean isPrivateOrLocalAddress(InetAddress addr) {
    // Block RFC1918 private networks, loopback, link-local
    return addr.isSiteLocalAddress() ||
           addr.isLoopbackAddress() ||
           addr.isLinkLocalAddress() ||
           addr.isMulticastAddress();
}
```

## Integration with Agents

**For comprehensive security analysis, use parallel agents**:

```javascript
// Example: Review web application security
use the .claude/agents/web-security-specialist.md agent to validate XSS/CSRF protection
use the .claude/agents/input-validation-specialist.md agent to check injection prevention
use the .claude/agents/configuration-specialist.md agent to verify security headers
```

## Progressive Disclosure

**This overview provides the essentials. For deeper analysis, I can provide**:
- Framework-specific security configurations (React, Angular, Vue, Django, Rails)
- CSP report analysis and policy refinement
- XSS filter bypass techniques and detection
- CORS security configuration
- Subdomain takeover prevention
- WebSocket security
- GraphQL security considerations
- Single Page Application (SPA) security

**Security Rules**: See [rules.json](./rules.json) for complete ASVS-aligned rule specifications

---

**Related Skills**: [input-validation](../input-validation/SKILL.md), [secure-configuration](../secure-configuration/SKILL.md), [session-management](../session-management/SKILL.md)

**Standards Compliance**: ASVS V13.1-V13.4 | OWASP Top 10 2021: A03, A05 | CWE-79, CWE-352, CWE-601, CWE-918, CWE-1021
