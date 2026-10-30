# Verification and reproducibility

Run `python scripts/setup.py`, `python scripts/build.py`, then
`python scripts/verify.py` from a clone with the baseline tag. The runner uses
only the local app and its dedicated Docker subnet addresses, with assertions
on expected outcomes. Commands for individual container tests are embedded in
the transcripts; the exact automation is version controlled in `scripts/verify.py`.

## Application before/after

| Check | Baseline | Hardened | Evidence |
|---|---|---|---|
| Valid token authentication first | 200 | 200 | `app/a1_*.txt` |
| Twenty wrong passwords after valid request | 20 × 401 | 9 × 401, 11 × 429 | `app/a1_*.txt` |
| Correct password after burst | 200 | 429 | `app/a1_*.txt` |
| Reset JWT signed with public default | Accepted | Rejected | `app/a2_*.txt` |
| Genuine reset JWT | Accepted | Accepted | `app/a2_*.txt` |
| Session Secure / SameSite | False / None | True / Lax | `app/a2_*.txt` |
| Fresh production startup without key | Insecure fallback | RuntimeError | `app/fail_closed.txt` |
| Tests | Upstream suite passes | Upstream + security suite pass | `app/tests_*.txt` |

The one earlier valid request consumes a slot; this explains why the wrong-password
burst has nine rather than ten pre-limit responses. Limits count all POST attempts,
not only failures. They reject at the limiter before credential verification.

The forgery proof checks the real verifier in the running application process with
its effective configuration and real database user. It does not rely solely on
decoding a self-generated JWT or comparing a config string. Unit tests additionally
exercise legitimate web login and session/remember cookie flags.

## Network before/after

Controlled insecure setup: combine `lab/docker-compose.net.yml` with
`lab/docker-compose.net.insecure.yml`. The latter is **not** an override to leave
enabled: the secure test removes the stack and recreates it with the first file only.

| Check | Insecure local lab | Hardened lab | Evidence |
|---|---|---|---|
| Host → localhost:15432 | TCP connects | Connection blocked | `network/n1_before.txt`, `n1_host_after.txt` |
| Rogue → DB TCP 5432 | Connects | Timeout | `network/n1_before.txt`, `access_tests.txt` |
| Admin → DB TCP 5432 | — | Connects | `network/access_tests.txt` |
| App → DB query | — | SELECT 1 returns 1 | `network/access_tests.txt` |
| Admin → UDP 5353 | — | Echo received | `network/access_tests.txt` |
| Client/rogue → UDP 5353 | — | No reply | `network/access_tests.txt` |
| Edge client → HTTP login | — | HTTP 200 | `network/access_tests.txt` |
| Secure stack force-recreated | — | Host/rogue denied, API works | `network/redeploy_verified.txt` |

`network/traffic.pcap` and `traffic_decoded.txt` capture authorized TCP connection
establishment and synthetic UDP request/reply, plus denied probes where visible at
the DB. `firewall_counters.txt` supplies effective rules and counters. Empty-payload
TCP filtering excludes credentials and SQL data; SYN/SYN-ACK/ACK remain visible.

The host originally had a service already using 5432; the lab therefore uses
host **15432**. It never stops or changes the existing host service. The internal
PostgreSQL service remains on **5432**. Source code and documentation use that
distinction consistently.

## Persistence, rollback and limits

App configuration is in source, dependency pins and image; DB access policy is in
the entrypoint and Compose membership/publication. Recreating containers reasserts
the controls. `.env` is generated once and retained privately, so restarts do not
invalidate sessions by silently changing the key. The in-memory limiter bucket
itself is not persistent and is explicitly a lab limitation.

Rollback for comparison uses the immutable baseline tag/image, or the explicitly
insecure local override. Do not use either for production. `down` removes lab
containers/networks while preserving volumes; `down -v` also erases lab data.

This establishes the tested outcomes on this Docker Desktop environment. It does
not establish comprehensive app security, production TLS, exhaustive firewall
coverage, resistance to a Docker administrator or candidate understanding.
The candidate must rehearse the walkthrough before submission.

Browser verification (`evidence/app/browser_smoke.txt`) additionally exercised a
real CSRF-protected login, remember cookie flags, post creation, persisted-post
display on Explore, and redirecting an unauthenticated session. Three actual
screenshots are under `evidence/screenshots/`.
The browser smoke runner also verifies token issuance, bearer-authenticated API
user listing (200), and rejection of the same API read without a token (401).

Clean-clone reproduction is recorded in `evidence/clean_clone.txt` and the actual
image-build output in `evidence/clean_build.txt`. The full verifier was repeated
from commit `9311b29` with fresh random credentials and separate project volumes;
the final hardened app source is unchanged from that commit. Later changes add
documentation, optional browser/API assertions, evidence serialization and package
checks. `evidence/source-provenance.txt` records the byte-for-byte upstream match.
