"""Check tracked submission files for generated credentials and obvious secret formats."""
from pathlib import Path
import json
import re
import subprocess

root = Path(__file__).resolve().parents[1]
secret_values = []
for path in [root / '.env', root / '.build/clean-checkout/.env',
             root / '.build/demo-login.txt', root / '.build/clean-checkout/.build/demo-login.txt']:
    if path.exists():
        for line in path.read_text(encoding='utf-8').splitlines():
            if '=' in line and not line.startswith('URL:'):
                secret_values.append(line.split('=', 1)[1].encode())
            elif line.startswith('Password: '):
                secret_values.append(line.split(': ', 1)[1].encode())
files = subprocess.check_output(['git', 'ls-files', '-z'], cwd=root).decode().split('\0')
issues = []
for name in filter(None, files):
    data = (root / name).read_bytes()
    if any(value and value in data for value in secret_values):
        issues.append(name + ': generated local credential')
    if re.search(rb'(?:gh[pousr]_[A-Za-z0-9]{25,}|AKIA[0-9A-Z]{16}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)', data):
        issues.append(name + ': credential format')
    if name == '.env' or name.startswith('.build/'):
        issues.append(name + ': private runtime file is tracked')
assert not issues, '\n'.join(issues)
# Tool transcripts intentionally preserve column padding and blank lines.
subprocess.run(['git', 'diff', '--check', 'HEAD', '--', '.', ':(exclude)evidence/**'], cwd=root, check=True)
subprocess.run(['git', 'apply', '--reverse', '--check', 'fixes/security-hardening.diff'], cwd=root, check=True)
summary = {'result': 'PASS', 'tracked_files_checked': len(list(filter(None, files))),
           'generated_local_credentials_found': 0,
           'obvious_private_key_or_access_token_formats_found': 0,
           'application_patch_reverse_check': 'PASS',
           'limitations': 'Focused format/known-value check, not an exhaustive secret scanner.'}
(root / 'evidence/submission_checks.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
print('Submission checks passed:', summary['tracked_files_checked'], 'tracked files')
