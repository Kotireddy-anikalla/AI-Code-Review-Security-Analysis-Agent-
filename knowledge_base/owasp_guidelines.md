
# OWASP Secure Coding Guidelines & Anti-Patterns

## 1. Injection Vulnerabilities (OWASP A03:2021)
- **SQL Injection**: Occurs when untrusted data is concatenated directly into SQL queries without parameterization.
  - *Mitigation*: Always use parameterized queries or PreparedStatements.
- **Cross-Site Scripting (XSS)**: Occurs when unvalidated user inputs are rendered directly in web outputs.
  - *Mitigation*: Sanitize and Context-encode all user-supplied data before output rendering.

## 2. Broken Authentication & Secrets (OWASP A07:2021)
- **Hardcoded Secrets**: Never store credentials, API keys, private keys, or passwords inside source code files.
  - *Mitigation*: Fetch secrets from environment variables or dedicated secret stores (e.g., HashiCorp Vault, AWS Secrets Manager).

## 3. Broken Access Control (OWASP A01:2021)
- Direct object references without authorization checks allow attackers to access or modify resources belonging to other users.
  - *Mitigation*: Enforce strict server-side authorization checks on every request.

## 4. Code Smells & Design Anti-Patterns
- **High Cyclomatic Complexity**: Functions with excessive nested loops, conditionals, or branching logic.
- **God Object / Long Methods**: Functions or classes performing too many responsibilities violate the Single Responsibility Principle (SRP).
- **Bare Exceptions**: Catching general exceptions without specific logging or handling hides dangerous runtime errors.
