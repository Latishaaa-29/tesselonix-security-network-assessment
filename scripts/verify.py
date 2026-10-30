"""Execute lab proofs; save actual redacted output and fail on unexpected results.

Run from anywhere with Python 3.11+, Docker Desktop running and images built.
Never probes anything other than localhost and the dedicated Compose lab.
"""
import base64
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import secrets
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
PREFIX = os.environ.get('TX_PROJECT_PREFIX', 'tx')
APP = ['docker', 'compose', '-p', PREFIX + '-app', '--env-file', '.env', '-f', 'lab/docker-compose.yml']
NET = ['docker', 'compose', '-p', PREFIX + '-net', '--env-file', '.env', '-f', 'lab/docker-compose.net.yml']
INSECURE = NET + ['-f', 'lab/docker-compose.net.insecure.yml']
SENSITIVE = [line.split('=', 1)[1] for line in (ROOT / '.env').read_text().splitlines() if '=' in line]
PASSWORD = secrets.token_hex(20)
SENSITIVE.append(PASSWORD)


def redact(text):
    for value in SENSITIVE:
        if value:
            text = text.replace(value, '[REDACTED]')
    return text


def save(name, text):
    target = ROOT / 'evidence' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('Captured UTC: ' + datetime.now(timezone.utc).isoformat() + '\n' +
                      redact(text) + '\n', encoding='utf-8')
    print('Saved', name, flush=True)


def run(command, *, code=None, env=None, check=True):
    result = subprocess.run(command, input=code, text=True, encoding='utf-8',
        errors='replace', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
    if check and result.returncode:
        raise RuntimeError(redact(result.stdout))
    return result


def execute(compose, service, code):
    return run(compose + ['exec', '-T', service, 'python', '-'], code=code).stdout


def request(path, auth=None):
    headers = {}
    if auth:
        headers['Authorization'] = 'Basic ' + base64.b64encode(('audit:' + auth).encode()).decode()
    req = urllib.request.Request('http://localhost:5000' + path, data=b'' if auth else None, headers=headers)
    try:
        response = urllib.request.urlopen(req, timeout=8)
    except urllib.error.HTTPError as exc:
        return exc.code
    with response:
        return response.status


def wait_http():
    for _ in range(60):
        try:
            if request('/auth/login') == 200:
                return
        except (OSError, urllib.error.URLError):
            pass
        time.sleep(1)
    raise RuntimeError('Application did not become ready')


def seed(compose):
    execute(compose, 'app', """from microblog import app
from app import db
from app.models import User
import sqlalchemy as sa
with app.app_context():
    u = db.session.scalar(sa.select(User).where(User.username == 'audit'))
    if u is None:
        u = User(username='audit', email='audit@example.invalid')
        db.session.add(u)
    u.set_password(%r)
    db.session.commit()
    print('Seeded local audit account; credentials withheld')
""" % PASSWORD)


def app_proof(tag):
    env = dict(os.environ, TX_TAG=tag)
    if tag == 'baseline':
        env['SECRET_KEY'] = ''
    run(APP + ['up', '-d', '--wait'], env=env)
    wait_http()
    seed(APP)
    # A valid request first proves this is an existing account and functional endpoint.
    valid_first = request('/api/tokens', PASSWORD)
    codes = [request('/api/tokens', 'wrong-local-password') for _ in range(20)]
    valid_last = request('/api/tokens', PASSWORD)
    assert valid_first == 200
    if tag == 'baseline':
        assert codes == [401] * 20 and valid_last == 200
    else:
        assert codes[:9] == [401] * 9 and codes[9:] == [429] * 11 and valid_last == 429
    save(f'app/a1_{tag}.txt', 'POST /api/tokens using HTTP Basic; same peer, sequential requests\n'
         f'Valid credential first: {valid_first}\nWrong passwords: {codes}\n'
         f'Valid credential after burst: {valid_last}\nCredentials and bearer tokens withheld.')
    proof = execute(APP, 'app', """from microblog import app
from app.models import User
from app import db
import jwt, time
with app.app_context():
    u = db.session.scalar(db.select(User).where(User.username == 'audit'))
    forged = jwt.encode({'reset_password': u.id, 'exp': time.time()+600}, 'you-will-never-guess', algorithm='HS256')
    accepted = User.verify_reset_password_token(forged)
    print('Effective key equals public upstream default:', app.secret_key == 'you-will-never-guess')
    print('Forged reset JWT resolves to audit account:', accepted is not None and accepted.id == u.id)
    print('Genuine reset JWT accepted:', User.verify_reset_password_token(u.get_reset_password_token()).id == u.id)
    print('Session cookie policy:', {k: app.config[k] for k in ['SESSION_COOKIE_SECURE','SESSION_COOKIE_HTTPONLY','SESSION_COOKIE_SAMESITE']})
    response = app.test_client().get('/auth/login', base_url='https://localhost')
    for value in response.headers.getlist('Set-Cookie'):
        print('Set-Cookie:', value.split('=',1)[0] + '=[REDACTED];' + value.split(';',1)[1])
""")
    assert ('Forged reset JWT resolves to audit account: ' + str(tag == 'baseline')) in proof
    save(f'app/a2_{tag}.txt', proof)
    tests = ['tests.py'] if tag == 'baseline' else ['tests.py', 'test_security.py']
    result = run(['docker', 'run', '--rm', 'tx-microblog:' + tag, 'pytest', '-q'] + tests)
    save(f'app/tests_{tag}.txt', 'Command: docker run --rm tx-microblog:' + tag + ' pytest -q ' + ' '.join(tests) + '\n' + result.stdout)
    if tag == 'fixed':
        result = run(['docker', 'run', '--rm', 'tx-microblog:fixed', 'python', '-c',
                      'from app import create_app; create_app()'], check=False)
        assert result.returncode != 0 and 'SECRET_KEY must' in result.stdout
        save('app/fail_closed.txt', 'Fresh container without SECRET_KEY; expected nonzero exit\n' + result.stdout)
    run(APP + ['down'])


def probe_host():
    try:
        with socket.create_connection(('127.0.0.1', 15432), timeout=3):
            return True, 'Host 127.0.0.1:15432 TCP connected'
    except OSError as exc:
        return False, f'Host 127.0.0.1:15432 blocked: {type(exc).__name__}: {exc}'


def command_evidence(compose, service, command, check=True):
    result = run(compose + ['exec', '-T', service, 'sh', '-c', command], check=check)
    return '$ ' + service + ': ' + command + '\n' + result.stdout + f'Exit: {result.returncode}\n', result


def network_proof():
    run(NET + ['down'])
    run(INSECURE + ['up', '-d', '--wait'])
    wait_http()
    allowed, output = probe_host()
    assert allowed
    text, result = command_evidence(INSECURE, 'rogue', 'nc -zv -w 3 172.28.20.10 5432')
    save('network/n1_before.txt', 'Controlled, deliberately introduced local DB exposure\n' + output + '\n' + text)
    # Recreate DB in secure mode and remove its port mapping.
    run(INSECURE + ['down'])
    run(NET + ['up', '-d', '--wait'])
    wait_http()
    seed(NET)
    allowed, output = probe_host()
    assert not allowed
    save('network/n1_host_after.txt', output)
    addresses = ''
    for node in ['app', 'db', 'netops', 'client', 'rogue']:
        if node == 'app':
            addresses += execute(NET, node, "import socket; print('app hostname IPs:', socket.gethostbyname_ex(socket.gethostname()))\nprint(open('/proc/net/route').read())\nprint('ip_forward:', open('/proc/sys/net/ipv4/ip_forward').read())")
        else:
            text, _ = command_evidence(NET, node, 'ip -br address; ip route')
            addresses += text + '\n'
    save('network/addressing_routes.txt', addresses)
    text, _ = command_evidence(NET, 'db', 'ss -lntup; iptables -S INPUT')
    for node in ['app', 'db', 'netops']:
        cid = run(NET + ['ps', '-q', node]).stdout.strip()
        result = run(['docker', 'inspect', '--format', '{{json .NetworkSettings.Ports}}', cid])
        text += node + ' published ports: ' + result.stdout
    save('network/port_inventory.txt', text)
    # Keep only zero-payload TCP segments plus synthetic UDP probes. No auth/SQL payload is captured.
    capture_filter = '(tcp port 5432 and (ip[2:2] - ((ip[0] & 15) << 2) - ((tcp[12] & 240) >> 2) = 0)) or udp port 5353'
    start = 'echo $$ > /tmp/capture.pid; exec tcpdump -i any -U -s 128 -w /tmp/traffic.pcap "' + capture_filter + '"'
    run(NET + ['exec', '-T', '-d', 'db', 'sh', '-c', start])
    time.sleep(1)
    transcript = ''
    text, _ = command_evidence(NET, 'netops', 'nc -zv -w 3 172.28.20.10 5432')
    transcript += text
    # Read the DB secret inside the app process; neither command nor output contains it.
    transcript += execute(NET, 'app', "from microblog import app\nfrom app import db\nfrom sqlalchemy import text\nwith app.app_context():\n    print('App database query:', db.session.execute(text('SELECT 1')).scalar())")
    text, _ = command_evidence(NET, 'netops', "printf 'tx-udp-probe' | nc -u -w 2 172.28.20.10 5353")
    assert 'tx-udp-probe' in text
    transcript += text
    for node in ['client', 'rogue']:
        text, result = command_evidence(NET, node, 'nc -zv -w 3 172.28.20.10 5432', check=False)
        assert result.returncode != 0
        transcript += text
        text, _ = command_evidence(NET, node, "printf 'denied-udp-probe' | nc -u -w 2 172.28.20.10 5353", check=False)
        assert 'denied-udp-probe' not in text.split('\n', 1)[1]
        transcript += text + 'No UDP reply; nc exit alone does not establish delivery.\n'
    text, _ = command_evidence(NET, 'client', 'curl -s -o /dev/null -w "HTTP %{http_code}\\n" http://172.28.10.10:5000/auth/login')
    assert 'HTTP 200' in text
    transcript += text
    text, _ = command_evidence(NET, 'netops', 'nmap -n -Pn -sT -p 5000 172.28.10.10; nmap -n -Pn -sT -p 5432 172.28.20.10')
    transcript += text
    save('network/access_tests.txt', transcript)
    text, _ = command_evidence(NET, 'db', 'iptables -nvL INPUT; kill -INT $(cat /tmp/capture.pid)')
    save('network/firewall_counters.txt', text)
    time.sleep(1)
    cid = run(NET + ['ps', '-q', 'db']).stdout.strip()
    run(['docker', 'cp', cid + ':/tmp/traffic.pcap', 'evidence/network/traffic.pcap'])
    text, _ = command_evidence(NET, 'db', 'tcpdump -nn -tttt -r /tmp/traffic.pcap')
    assert 'Flags [S]' in text and 'Flags [S.]' in text and 'Flags [.]' in text
    save('network/traffic_decoded.txt', text)
    # Declarative policy survives recreation; volumes are preserved.
    run(NET + ['up', '-d', '--force-recreate', '--wait'])
    wait_http()
    text, result = command_evidence(NET, 'rogue', 'nc -zv -w 3 172.28.20.10 5432', check=False)
    assert result.returncode != 0
    allowed, output = probe_host()
    assert not allowed
    valid = request('/api/tokens', PASSWORD)
    assert valid == 200
    save('network/redeploy_verified.txt', text + output + f'\nValid API authentication after recreation: {valid}')
    (ROOT / '.build').mkdir(exist_ok=True)
    (ROOT / '.build/demo-login.txt').write_text('URL: http://localhost:5000\nUsername: audit\nPassword: ' + PASSWORD + '\n', encoding='utf-8')


if __name__ == '__main__':
    phase = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if phase in ('all', 'app'):
        run(NET + ['down'])
        app_proof('baseline')
        app_proof('fixed')
    if phase in ('all', 'network'):
        run(APP + ['down'])
        network_proof()
    save('verification_summary.json', json.dumps({'phase': phase, 'result': 'PASS',
        'application_left_running': phase in ('all', 'network')}, indent=2))
    print('All requested proofs passed.', flush=True)
