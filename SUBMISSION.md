# Submission package

Repository: https://github.com/Latishaaa-29/tesselonix-security-network-assessment

Candidate: **Latisha Saxena**  
Enrollment number: **02617711623**  
Role: **Cybersecurity and Computer Networking**

Ready-to-review deliverables:

- `README.md`: setup, run commands and architecture.
- `reports/01-security-findings.md`: two verified pre-existing app findings.
- `reports/02-network-assessment.md`: addressing, service inventory, policy and controlled exposure.
- `reports/03-verification.md`: reproduction and before/after mapping.
- `reports/04-reflection.md`: engineering reflection and required candidate review.
- `reports/05-walkthrough.md`: explanation and live-demo rehearsal.
- `reports/06-requirements-check.md`: mapping to the assignment and submission email.
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

Submit by **Reply All to the original assignment email thread**, retaining the
placement office and all original recipients. Keep the existing email subject.
The deadline is within **3 calendar days of receiving that email**; check its
actual received date rather than calculating from the date of this report.

Include the repository link and attach the PDF report and complete ZIP. The
repository is private, so the ZIP provides the full source and evidence without
requiring GitHub access; invite the evaluator if repository browsing is required.
Review the AI disclosure and personally run and understand the walkthrough.
The package is prepared for submission; no email has been sent by the assistant.
