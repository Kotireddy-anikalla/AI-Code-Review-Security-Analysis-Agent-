# Secure Coding Guidelines, OWASP Top 10 & Anti-Patterns

This document serves as the knowledge base for the RAG-powered Conversational Assistant. It combines the **OWASP Top 10 (2021)** vulnerability categories with **detailed secure coding practices** across the full software lifecycle, plus common code smells and anti-patterns flagged by the Code Analysis Agent.

---

## Part A — OWASP Top 10 (2021)

### A01: Broken Access Control
Occurs when restrictions on what authenticated users are allowed to do are not properly enforced, letting attackers act outside their intended permissions.
- **Common issues**: Insecure Direct Object References (IDOR), missing function-level access checks, privilege escalation via parameter tampering, CORS misconfiguration allowing unauthorized origins, forced browsing to authenticated pages as an unauthenticated user.
- **Mitigation**:
  - Enforce access control checks server-side on every request; never rely on client-side or hidden-field checks alone.
  - Deny by default; explicitly grant access rather than explicitly denying it.
  - Use centralized access-control logic instead of scattering checks across the codebase.
  - Log access-control failures and alert on repeated failures.
  - Rate-limit API and controller access to reduce automated attack impact.

### A02: Cryptographic Failures
Failures related to cryptography that often lead to exposure of sensitive data such as credentials, health records, or financial information.
- **Common issues**: Transmitting data in clear text (HTTP, SMTP, FTP), using outdated or weak algorithms (MD5, SHA1, DES), hardcoded or reused encryption keys, missing encryption for sensitive data at rest.
- **Mitigation**:
  - Classify data processed by the application and identify what is sensitive.
  - Encrypt sensitive data at rest and in transit using strong, up-to-date algorithms (AES-256, TLS 1.2+).
  - Use proper key management — never hardcode keys or secrets in source code.
  - Disable caching for responses containing sensitive data.

### A03: Injection
Occurs when untrusted data is sent to an interpreter as part of a command or query, tricking it into executing unintended commands.
- **Common issues**: SQL Injection, NoSQL Injection, OS Command Injection, LDAP Injection, Cross-Site Scripting (XSS).
- **Mitigation**:
  - Use parameterized queries, prepared statements, or ORM query builders instead of string concatenation.
  - Validate and sanitize all untrusted input against an allow-list.
  - Context-encode output before rendering in HTML, JavaScript, CSS, or URL contexts.
  - Avoid invoking OS shell commands with unsanitized input; use safe APIs instead.

### A04: Insecure Design
Represents flaws in design and architecture that cannot be fixed by implementation alone — the system was never designed with security requirements in mind.
- **Common issues**: Missing threat modeling, absence of rate limiting on sensitive operations, business logic flaws (e.g., unlimited password reset attempts), lack of segregation between trust zones.
- **Mitigation**:
  - Apply threat modeling during design for critical authentication, access control, and business logic flows.
  - Use secure design patterns and reference architectures.
  - Limit resource consumption per user/session/request to prevent abuse.

### A05: Security Misconfiguration
Occurs when security settings are left at insecure defaults, are incompletely configured, or expose unnecessary information.
- **Common issues**: Default credentials left unchanged, verbose error messages leaking stack traces, unnecessary features/ports/services enabled, missing security headers.
- **Mitigation**:
  - Harden all environments (dev, staging, prod) with a repeatable, automated configuration process.
  - Remove or disable unused features, frameworks, and sample applications.
  - Return generic error messages to users while logging detailed errors server-side.
  - Apply security headers (CSP, X-Content-Type-Options, X-Frame-Options, Strict-Transport-Security).

### A06: Vulnerable and Outdated Components
Occurs when libraries, frameworks, or other software modules with known vulnerabilities are used without tracking their versions or patch status.
- **Mitigation**:
  - Maintain an inventory of all components and their versions (SBOM).
  - Continuously monitor dependencies for known CVEs and patch promptly.
  - Remove unused dependencies and features.
  - Obtain components only from official, trusted sources over secure channels.

### A07: Identification and Authentication Failures
Weaknesses in confirming a user's identity, authentication, or session management.
- **Common issues**: Weak or default passwords permitted, missing multi-factor authentication, session IDs exposed in URLs, session fixation, unlimited login attempts (no lockout/throttling).
- **Mitigation**:
  - Enforce strong password policies and support multi-factor authentication.
  - Rotate session identifiers after login and invalidate them on logout/timeout.
  - Implement account lockout or exponential backoff after repeated failed login attempts.
  - Never expose session tokens in URLs; use secure, HttpOnly, SameSite cookies.

### A08: Software and Data Integrity Failures
Occurs when code or infrastructure does not verify the integrity of software updates, critical data, or CI/CD pipelines.
- **Common issues**: Unsigned or unverified auto-updates, insecure deserialization of untrusted data, CI/CD pipelines without integrity checks.
- **Mitigation**:
  - Use digital signatures to verify software and updates come from a trusted source.
  - Avoid deserializing data from untrusted sources without strict type constraints and validation.
  - Ensure CI/CD pipelines have proper access controls, segregation, and integrity verification.

### A09: Security Logging and Monitoring Failures
Insufficient logging, detection, and monitoring allows attackers to persist in a system undetected.
- **Common issues**: Login/access-control failures not logged, logs stored only locally and lost on compromise, no alerting on suspicious activity.
- **Mitigation**:
  - Log all authentication, access-control, and input-validation failures with sufficient context (avoid logging sensitive data itself).
  - Ensure logs are generated in a format consumable by centralized log management and are tamper-resistant.
  - Establish effective monitoring and alerting so suspicious activity is detected and responded to quickly.

### A10: Server-Side Request Forgery (SSRF)
Occurs when a web application fetches a remote resource without validating the user-supplied URL, allowing an attacker to coerce the server into making unintended requests.
- **Mitigation**:
  - Validate and sanitize all client-supplied URLs/hosts against an allow-list.
  - Disable unused URL schemas and HTTP redirections.
  - Segment remote resource-fetching functionality onto isolated networks with restricted egress.

---

## Part B — Detailed Secure Coding Practices

### 1. Input Validation
- Validate all input (form fields, headers, cookies, query strings, API payloads) on the server side, regardless of client-side validation.
- Prefer allow-list validation (accept known-good patterns) over deny-list validation (block known-bad patterns).
- Validate data type, length, format, and range before use.
- Reject input that fails validation rather than attempting to "fix" or sanitize it silently.

### 2. Output Encoding
- Encode output based on the context it will be rendered in (HTML body, HTML attribute, JavaScript, CSS, URL).
- Use well-tested encoding libraries rather than writing custom encoders.
- Apply encoding as close to the output sink as possible.

### 3. Authentication & Password Management
- Store passwords using a strong, salted, adaptive hashing algorithm (bcrypt, scrypt, or Argon2) — never plain text or fast general-purpose hashes like MD5/SHA1.
- Enforce minimum password complexity and length; encourage passphrases over complex short passwords.
- Support and encourage multi-factor authentication for sensitive accounts.
- Never hardcode credentials, API keys, or tokens in source code; load them from environment variables or a secrets manager.

### 4. Session Management
- Generate session identifiers using a cryptographically secure random number generator.
- Set session cookies with `HttpOnly`, `Secure`, and `SameSite` attributes.
- Invalidate sessions on logout and after a reasonable period of inactivity.
- Regenerate session IDs after privilege changes (e.g., login, password change).

### 5. Access Control
- Apply the principle of least privilege to every user, process, and service account.
- Enforce authorization checks on every request at the server, not just at the UI layer.
- Avoid exposing internal object references (database IDs, file paths) directly; use indirect references or verify ownership server-side.

### 6. Cryptographic Practices
- Use vetted, standard cryptographic libraries; never implement custom cryptographic algorithms.
- Use strong, current algorithms and key lengths (AES-256, RSA-2048+, SHA-256+).
- Store and rotate encryption keys using a dedicated key-management system, separate from application code and data.
- Use secure random number generators for tokens, nonces, and keys — never predictable sources like `Math.random()`.

### 7. Error Handling & Logging
- Fail securely: on error, deny access and don't leak internal state.
- Never expose stack traces, SQL errors, or internal file paths to end users.
- Log security-relevant events (auth failures, access-control violations, input-validation failures) with enough context to investigate, but never log sensitive data (passwords, tokens, full credit card numbers) in plain text.
- Centralize and protect logs from tampering or unauthorized access.

### 8. Data Protection
- Classify data by sensitivity and apply protection controls proportional to that sensitivity.
- Encrypt sensitive data at rest and in transit.
- Apply data minimization — collect and retain only what is necessary.
- Implement secure deletion/retention policies for data no longer needed.

### 9. Communication Security
- Enforce TLS for all network communication carrying sensitive data; disable legacy/insecure protocol versions (SSLv3, TLS 1.0/1.1).
- Validate TLS certificates properly; never disable certificate validation in production code.
- Avoid mixed content (serving some resources over HTTP on an HTTPS page).

### 10. System & Configuration Management
- Use separate configurations and credentials for development, staging, and production environments.
- Keep frameworks, libraries, and runtime environments patched and up to date.
- Disable directory listing, verbose error pages, and debug endpoints in production.
- Apply the principle of least functionality — disable unused services, ports, and features.

### 11. Database Security
- Use parameterized queries or ORM-provided query builders exclusively; never build SQL via string concatenation.
- Apply least-privilege database accounts — application accounts should not have schema-modification rights unless required.
- Avoid returning raw database error messages to clients.

### 12. File Management
- Validate file type, size, and content (not just the extension) before accepting uploads.
- Store uploaded files outside the web root, or serve them through a handler that enforces access control.
- Generate randomized filenames server-side to avoid path traversal or overwrite attacks.
- Scan uploaded files for malicious content where feasible.

### 13. Memory & Resource Management
- Validate buffer sizes and array bounds before use (particularly relevant in native/unmanaged code paths).
- Release resources (file handles, connections, memory) deterministically; avoid leaks under error paths.
- Apply timeouts and resource limits to prevent denial-of-service via resource exhaustion.

### 14. General Secure Coding Practices
- Follow the principle of least privilege throughout the codebase, from database accounts to OS-level process permissions.
- Keep security-relevant logic centralized and reusable rather than duplicated across modules.
- Perform security code reviews and static/dynamic analysis as part of the development workflow, not as an afterthought.
- Maintain a secure software development lifecycle (SDLC) with security gates at design, implementation, and deployment stages.

---

## Part C — Code Smells & Design Anti-Patterns

- **High Cyclomatic Complexity**: Functions with excessive nested loops, conditionals, or branching logic, making the code hard to test and reason about.
  - *Mitigation*: Extract smaller, single-purpose functions; reduce nesting via early returns/guard clauses.
- **God Object / Long Methods**: Functions or classes performing too many responsibilities, violating the Single Responsibility Principle (SRP).
  - *Mitigation*: Decompose responsibilities into cohesive, smaller classes/functions.
- **Bare/Broad Exceptions**: Catching general exceptions (e.g., `except Exception:` or `catch (Exception e)`) without specific handling hides dangerous runtime errors.
  - *Mitigation*: Catch the narrowest exception type possible and handle or log it meaningfully.
- **Duplicated Code**: Repeated logic across multiple locations increases the risk of inconsistent fixes and bugs.
  - *Mitigation*: Extract shared logic into reusable functions or modules.
- **Magic Numbers/Strings**: Unexplained literal values embedded directly in logic reduce readability and maintainability.
  - *Mitigation*: Replace with named constants or configuration values.
- **Tight Coupling**: Modules that depend heavily on each other's internal implementation details are difficult to change or test independently.
  - *Mitigation*: Depend on interfaces/abstractions rather than concrete implementations where practical.
- **Dead Code**: Unused variables, functions, or unreachable branches clutter the codebase and can hide latent bugs.
  - *Mitigation*: Remove unused code; rely on version control history rather than commented-out code.
