# Tools and AI disclosure

Codex (OpenAI coding assistant) read the assignment and supplied architecture,
reviewed the pinned source, wrote the lab configuration, fixes, tests, evidence
runner and reports, and executed the verification. The candidate must review,
understand and personally re-run this work before representing it as their own
understood assessment. No claim is made that the candidate already did so.

Tools used: Git and GitHub CLI; Docker Desktop / WSL2 / Compose; Python 3.11;
PyMuPDF to read the supplied PDFs; pytest; Flask-Limiter; nmap; iproute2 / ss;
iptables; netcat; tcpdump; PostgreSQL / SQLAlchemy; Playwright browser automation;
ReportLab for the printable report. Runtime tools execute inside local containers.

Verification performed by the assistant is recorded under `evidence/`: live HTTP
attempts, controlled JWT forgery checked by the app's real verifier, upstream and
security tests, host and rogue connection attempts, required app DB queries,
firewall counters, packet inspection and tests after recreation. Screenshots are
separate UI evidence. Secrets are replaced with `[REDACTED]` or never emitted.

Suggestions from the architecture that were changed or rejected:

- Do not claim that a dual-homed application is a router, or that only one node is
  dual-homed: the admin node is too. IP forwarding is explicitly disabled.
- Do not assert that a router failed on this machine; no such diagnosis was made.
- Do not describe a default route as 'no route at all'. Record actual route tables
  and distinguish lack of direct subnet attachment from filtering.
- Do not publish the vulnerable database on all host interfaces; use loopback only.
- Do not include a plaintext throwaway database password in evidence: the assignment
  excludes credentials, so even lab passwords are random and ignored.
- Do not rely on scanner labels or a UDP `nc` exit status: assert responses, inspect
  traffic, and use counters for the directly connected rogue source.
- Use one repository with a baseline tag instead of a nested `.git` directory; a
  clean normal clone must include the target code and reproduce both builds.
- Keep the reflection honest about assistant execution and candidate review.

Primary references consulted:

- Microblog source: https://github.com/miguelgrinberg/microblog/tree/a975ef64864354867c88e0ed3a17ba7d17dca752
- Flask-Limiter initialization, decorators and storage limitations:
  https://flask-limiter.readthedocs.io/en/stable/
- Docker Compose networking, service names and published/container ports:
  https://docs.docker.com/compose/how-tos/networking/

The two supplied PDFs are requirements/design inputs, not evidence that a finding
exists. Findings are established by source review and executable local proofs.
