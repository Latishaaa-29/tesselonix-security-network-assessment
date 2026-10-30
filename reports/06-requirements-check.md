# Assignment requirements cross-check

Candidate: Latisha Saxena | Enrollment: 02617711623

Basis: supplied Tesselonix Cybersecurity and Networking Practical Assignment PDF
and the HR submission email provided by the candidate. This checks artifacts and
executed tests, not the candidate's personal understanding or a guaranteed grade.

| Requirement | Implementation and review evidence |
|---|---|
| Open-source target with exact version | Microblog URL and pinned commit in README; byte comparison in evidence/source-provenance.txt |
| Authentication, APIs and database | Flask-Login, Basic/bearer API and PostgreSQL; evidence/app/browser_smoke.txt |
| Two verified application weaknesses | Rate limiting and default signing key; reports/01-security-findings.md and evidence/app/a1_*, a2_* |
| Fix or justified mitigation | Application patch, fail-closed key handling, cookie flags and POST throttling; fixes/security-hardening.diff |
| App regression tests | Upstream and added security tests; evidence/app/tests_baseline.txt and tests_fixed.txt |
| Listening services, protocols and interfaces | reports/02-network-assessment.md; evidence/network/port_inventory.txt |
| TCP and UDP success/failure, traffic inspection | evidence/network/access_tests.txt, traffic.pcap and traffic_decoded.txt |
| Diagram, addressing, gateways and routes | reports/network-diagram.svg; evidence/network/addressing_routes.txt |
| Access policy and enforced restrictions | Network report matrix; DB INPUT allowlists/default DROP; rogue and edge denial tests |
| Reproducible network exposure and fix | Clearly labelled controlled misconfiguration; evidence/network/n1_before.txt and n1_host_after.txt |
| Required communication still works | Real app SELECT 1, client HTTP 200 and API authentication after recreation |
| Before/after application and network proof | reports/03-verification.md; raw app/network evidence |
| Configuration persists after redeployment | Compose and entrypoint; evidence/network/redeploy_verified.txt |
| Setup, fixes, reports, evidence and reflection | README, fixes/, reports/, evidence/ and TOOLS_AND_AI.md |
| Disclosed AI/tool use | TOOLS_AND_AI.md; reflection distinguishes assistant execution from candidate review |
| Isolated testing and redacted secrets | Dedicated Docker lab, loopback-only publication, focused credential scan in evidence/submission_checks.json |
| Reproducibility from a clean clone | evidence/clean_clone.txt and clean_build.txt; ZIP includes repository.bundle |
| Email submission method | Reply All to original thread, preserve placement office recipients; attach PDF and ZIP and include repository URL |

## Qualifications to retain in the submission

- There are two subnets and captured routing information, but no dedicated router
  forwarding demonstration. The dual-homed app/admin have forwarding disabled.
  The assignment makes router use conditional on feasibility; this is a disclosed
  design limitation, not a claim of full routed-network equivalence.
- The network exposure is deliberately introduced in the isolated before-state,
  which the assignment permits. It is not attributed to upstream Microblog.
- In-memory per-peer throttling with one worker is a lab mitigation. Shared
  persistent storage, account-aware controls and MFA remain production work.
- Old upstream dependencies and optional services are outside the two-finding
  remediation scope. The project is not presented as comprehensively secure.
- The repository is private. Attach the complete ZIP so reviewers can inspect
  the source and evidence without waiting for GitHub access.
- Candidate ownership must be demonstrated personally in the live follow-up;
  assistant-run tests do not establish candidate understanding.
- Submit within three calendar days of the actual email receipt. Its received
  timestamp was not provided, so an exact deadline cannot be established here.
