"""Optional UI smoke test. Requires host playwright and its Chromium browser."""
from pathlib import Path
import base64
import json
import time
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]
credentials = (root / '.build/demo-login.txt').read_text().splitlines()
password = next(line.split(': ', 1)[1] for line in credentials if line.startswith('Password:'))
folder = root / 'evidence/screenshots'
folder.mkdir(parents=True, exist_ok=True)
with sync_playwright() as playwright:
    browser = playwright.chromium.launch()
    page = browser.new_page(viewport={'width': 1440, 'height': 1000})
    page.goto('http://localhost:5000/auth/login', wait_until='networkidle')
    page.screenshot(path=str(folder / '01-login.png'), full_page=True)
    page.locator('#username').fill('audit')
    page.locator('#password').fill(password)
    page.locator('#remember_me').check()
    page.locator('#submit').click()
    page.wait_for_url('http://localhost:5000/index')
    assert page.locator('#post').is_visible(), 'Authenticated post form must be visible'
    content = 'Verified local security lab: authentication, posting and PostgreSQL persistence.'
    page.locator('#post').fill(content)
    page.locator('#submit').click()
    page.wait_for_load_state('networkidle')
    assert page.get_by_text(content, exact=False).count() > 0
    page.screenshot(path=str(folder / '02-authenticated-post.png'), full_page=True)
    page.goto('http://localhost:5000/explore', wait_until='networkidle')
    assert page.get_by_text(content, exact=False).count() > 0
    page.screenshot(path=str(folder / '03-explore.png'), full_page=True)
    cookies = page.context.cookies()
    assert all(c['secure'] and c['httpOnly'] and c['sameSite'] == 'Lax'
               for c in cookies if c['name'] in ('session', 'remember_token'))
    auth = base64.b64encode(('audit:' + password).encode()).decode()
    issued = page.request.post('http://localhost:5000/api/tokens',
                               headers={'Authorization': 'Basic ' + auth})
    assert issued.status == 200
    bearer = issued.json()['token']
    assert page.request.get('http://localhost:5000/api/users',
        headers={'Authorization': 'Bearer ' + bearer}).status == 200
    assert page.request.get('http://localhost:5000/api/users').status == 401
    # A second context with no cookies must be redirected to login.
    other = browser.new_context()
    unauthenticated = other.new_page()
    unauthenticated.goto('http://localhost:5000/index', wait_until='networkidle')
    assert '/auth/login' in unauthenticated.url
    (root / 'evidence/app/browser_smoke.txt').write_text(
        'Chromium browser smoke test: PASS\n'
        'Login with real CSRF form: PASS\nRemember cookie and session flags: PASS\n'
        'Authenticated create post: PASS\nExplore reads persisted post: PASS\n'
        'Bearer-authenticated API user list: PASS\nAPI user list without token returns 401: PASS\n'
        'Unauthenticated index redirects to login: PASS\n'
        'Credentials/cookie values withheld. Screenshots contain disposable lab data only.\n', encoding='utf-8')
    browser.close()
print('Browser UI smoke test passed; three screenshots saved.')
