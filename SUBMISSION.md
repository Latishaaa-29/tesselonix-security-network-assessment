# Submission package

Repository: https://github.com/Latishaaa-29/tesselonix-security-network-assessment

Candidate name: fill in the exact name required by the assessment portal.
Do not infer a candidate name from the machine user or GitHub account.

Ready-to-review deliverables:

- `README.md`: setup, run commands and architecture.
- `reports/01-security-findings.md`: two verified pre-existing app findings.
- `reports/02-network-assessment.md`: addressing, service inventory, policy and controlled exposure.
- `reports/03-verification.md`: reproduction and before/after mapping.
- `reports/04-reflection.md`: engineering reflection and required candidate review.
- `reports/05-walkthrough.md`: explanation and live-demo rehearsal.
- `reports/network-diagram.svg`: topology.
- `reports/assessment-report.pdf`: printable combined reports.
- `fixes/security-hardening.diff`: app patch.
- `evidence/`: test output, before/after transcripts, packet capture and screenshots.
- `TOOLS_AND_AI.md`: transparent tool/AI disclosure.

The repository includes tag `upstream-baseline` and branch `security-hardening`.
An accompanying submission ZIP includes the tracked files and `repository.bundle`
with all Git refs, so ZIP recipients can reconstruct the baseline history:

```powershell
git clone repository.bundle tesselonix-assessment
cd tesselonix-assessment
python scripts/setup.py
python scripts/build.py
python scripts/verify.py
```

Before sending to the assessment team, fill in your candidate name in the portal,
review the AI disclosure, personally run and understand the walkthrough, and ensure
the evaluator can access the repository (invite them if it remains private) or
submit the ZIP. A GitHub repository link is not itself an email/portal submission.
No assessor email or portal destination has been supplied, so this package is
prepared for you to submit; nothing has been sent to an assessor.
