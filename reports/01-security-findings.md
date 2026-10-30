# Application security findings

Scope: Microblog at `a975ef64864354867c88e0ed3a17ba7d17dca752`, cloned from
https://github.com/miguelgrinberg/microblog. Test only the isolated local instance.
No public service testing. Severity is qualitative and depends on deployment.

## A-1 — Authentication attempts are not throttled (Medium)

Root cause: `app/api/tokens.py` places Basic authentication on POST `/api/tokens`
without a rate limit. Web login and reset routes similarly have no throttling.
An attacker can perform repeated online guesses; this proof establishes absence
of throttling over the observed burst, not that an unknown password was cracked.

Reproduce: `python scripts/verify.py app`. The runner creates a disposable account,
proves valid authentication first, sends 20 wrong passwords from one peer, then
tries the real password. Baseline returns twenty 401s and then 200. Fixed returns
nine 401s and eleven 429s after the first successful request consumes one slot;
the final correct attempt is also 429. See `evidence/app/a1_baseline.txt` and
`a1_fixed.txt`. Tokens and credentials are intentionally omitted.

Fix: initialize Flask-Limiter and decorate **outside** `login_required`, ensuring
failed authentication is counted too. Token issuance and web login POSTs have
10/minute per-peer limits; reset POST routes have 5/minute. GET login remains
accessible. Do not trust arbitrary `X-Forwarded-For`; the regression test varies
this header and confirms it cannot bypass the local peer bucket.

Tests: `test_token_throttling_and_no_forwarded_ip_bypass` and parametrized web
POST tests in `test_security.py`. A separate peer still authenticates. Upstream
model tests establish that unrelated core behavior remains intact.

Remaining limitations: in-memory limits are a lab mitigation with one worker,
reset on restart, and can be bypassed by distributed peers. Per-peer limits may
affect users sharing NAT. For production use shared persistent storage, account
and peer policies, MFA, logging and carefully configured trusted proxies. This
change does not claim complete protection from credential stuffing.

## A-2 — Public fallback signing key enables forged reset tokens (High)

Root cause: `config.py` silently uses a known source-code string if the environment
key is absent/empty. `User.verify_reset_password_token` trusts HS256 JWTs signed
with that key. Under that configuration, knowledge of a user ID permits generation
of an accepted password-reset token, with potential account takeover.

Reproduce: the same runner starts baseline **without a supplied key**, signs a
short-lived reset JWT for the disposable audit user using the public fallback,
and invokes the real `User.verify_reset_password_token` in the running app.
The forged token resolves to the audit account before hardening and is rejected
afterward; a genuine reset token still succeeds. No other user's data is accessed
and the proof does not actually change a password. See `evidence/app/a2_baseline.txt`
and `a2_fixed.txt`. This is conditional on default-key deployment, not a claim
that all installations are exploitable.

Fix: read the key from environment only. Production app creation rejects absent,
short and known-default keys before extension initialization; importing modules
does not throw. Test/debug mode generates a fresh ephemeral key where needed.
`scripts/setup.py` generates a private random 64-character key. Length checks
cannot establish entropy; use the provided generator or a secret manager.

Related defense in depth: set session and remember cookies to Secure, HttpOnly,
SameSite=Lax. Baseline had HttpOnly already; Secure and SameSite were missing.
Cookie flags do not repair a known signing key or provide HTTPS themselves.
Use TLS on real deployments; localhost browser behavior is a demo convenience.

Tests cover refused production starts, ephemeral test keys, rejected forgery,
valid genuine reset tokens, and flags on **both** session and remember cookies
after a successful login. Evidence includes actual cookie attributes with values
redacted, plus `evidence/app/fail_closed.txt` for a fresh container without a key.

Operational follow-up: replace any previously exposed signing key, invalidate old
sessions/reset tokens and assess access logs. A randomly generated key persists
in ignored `.env` for this lab; use managed secret injection in production.

## Scope decisions

Open registration is an intended feature and was not reported as a vulnerability.
SQLAlchemy ORM use alone neither proves nor disproves injection safety; no SQL
injection claim was established. Old dependency pins remain a review item; no
scanner output is being presented as a verified exploit. Optional upstream
services and production TLS/proxy deployment are outside the exercised scope.
