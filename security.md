# Secure by Design

Load whenever code crosses a trust boundary — HTTP handlers, database layers, file I/O, deserialisation, auth, or anything touching user-supplied data.

Security is not a feature bolted on at the end. It's a property of how the code is structured. Treat every input as hostile until proven otherwise, and every output as potentially observable.

---

## The trust boundary mindset

Any data crossing into your process from outside — HTTP request, file upload, database read, message queue, environment variable — is untrusted. Validate it at the boundary. Once validated and typed, the interior of your system can trust it.

---

## Concrete rules

### Input validation
- Allowlist, not blocklist. Define what's valid; reject everything else.
- Validate type, range, length, format. "It's a string" is not validation.
- Validate at the boundary, once, then pass typed, trusted values inward.

### Injection prevention
- SQL: parameterised queries only. Never string-concatenate user input into SQL.
- Shell: prefer APIs over shelling out. If you must, use argument arrays (`subprocess.run([...], shell=False)`), never `shell=True` with user input.
- Templates: use auto-escaping template engines. Never `innerHTML` user-provided content.
- Deserialisation: never deserialise untrusted data with formats that can execute code (pickle, Java serialisation, YAML without safe-load).

### Authentication & Authorisation
- Distinguish the two. Authentication answers "who are you?". Authorisation answers "what are you allowed to do?". Both are required at every protected boundary.
- Check authorisation on every request, not just at the login screen. Assume session hijacking is possible.
- Deny by default. If the rule engine doesn't explicitly grant access, access is denied.

### Secrets
- Never commit secrets to version control — not even in `.env.example`, not even "just for testing".
- Read from environment variables, secret managers (AWS Secrets Manager, HashiCorp Vault, etc.), or a dedicated config loader.
- Secrets never go in logs. Never. If you log a request, redact the auth header, password fields, tokens, session IDs, and PII.
- Errors involving secrets must not echo the secret in the error message.

### Cryptography
- Don't invent your own. Use the standard library / well-maintained libraries.
- Use `bcrypt`, `argon2`, or `scrypt` for passwords. Never `md5` or `sha1` or plain `sha256` for passwords.
- Use a CSPRNG (`secrets` in Python, `crypto/rand` in Go) for tokens, not the regular PRNG.
- TLS everywhere in transit. No exceptions in production paths.

### Safe defaults
- Deny by default, allow by exception.
- Fail closed (security decisions that error out should deny access, not grant it).
- New features ship with the most restrictive permissions; loosen only when required.

### Output hygiene
- HTML: escape on output, not on input.
- JSON: don't concatenate strings; use the serialiser.
- Logs: structured, redacted, with the level right (don't `INFO`-log user credentials even accidentally).
- Error messages to users are generic. Error messages to logs are detailed and correlated.

### Dependencies
- Pin versions. Audit the supply chain. Prefer the standard library where reasonable.
- Run a dependency audit (`npm audit`, `pip-audit`, `govulncheck`) as part of CI.
- Distrust transitive dependencies. A small, focused dependency tree is a security property.

### Resource limits
- Every external call has a timeout. Defaults are usually too long or absent.
- Every loop processing external data has a bound.
- Every file upload has a maximum size, enforced before reading the whole thing into memory.

---

## Security review questions (before declaring done)

- What happens if this input is 10MB? 10GB?
- What happens if this field contains `' OR 1=1 --`? `<script>alert(1)</script>`? `../../../../etc/passwd`? `${jndi:ldap://...}`?
- What happens if this external API never responds?
- What does this log contain? Would I be comfortable if it leaked?
- Who's allowed to call this endpoint? How is that enforced?
- If this fails halfway, does the system end up in a safe state?
