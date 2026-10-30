"""Regression tests for the two verified upstream findings."""
import base64
import time
import jwt
import pytest
from app import create_app, db
from app.models import User
from config import Config


class SecurityConfig(Config):
    TESTING = True
    SECRET_KEY = 'test-only-key-' * 5
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    WTF_CSRF_ENABLED = False
    ELASTICSEARCH_URL = None


@pytest.fixture
def app():
    instance = create_app(SecurityConfig)
    with instance.app_context():
        db.create_all()
        user = User(username='audit', email='audit@example.invalid')
        user.set_password('test-only-password')
        db.session.add(user)
        db.session.commit()
        yield instance
        db.session.remove()
        db.drop_all()


def test_token_throttling_and_no_forwarded_ip_bypass(app):
    client = app.test_client()
    good = base64.b64encode(b'audit:test-only-password').decode()
    assert client.post('/api/tokens', headers={'Authorization': 'Basic ' + good}).status_code == 200
    codes = [client.post('/api/tokens', headers={
        'Authorization': 'Basic ' + base64.b64encode(b'audit:wrong').decode(),
        'X-Forwarded-For': f'192.0.2.{i}'
    }).status_code for i in range(12)]
    assert codes[:9] == [401] * 9
    assert codes[9:] == [429] * 3
    # A separate peer can still authenticate; an exhausted peer is throttled.
    assert client.post('/api/tokens', headers={'Authorization': 'Basic ' + good},
                       environ_overrides={'REMOTE_ADDR': '192.0.2.100'}).status_code == 200


@pytest.mark.parametrize('path,limit', [('/auth/login', 10),
    ('/auth/reset_password_request', 5), ('/auth/reset_password/invalid', 5)])
def test_web_auth_post_limits(app, path, limit):
    client = app.test_client()
    for _ in range(limit):
        assert client.post(path).status_code != 429
    assert client.post(path).status_code == 429
    assert client.get('/auth/login').status_code == 200


@pytest.mark.parametrize('key', [None, '', 'you-will-never-guess', 'short'])
def test_production_refuses_missing_or_weak_key(key):
    class Missing(SecurityConfig):
        TESTING = False
        SECRET_KEY = key
    with pytest.raises(RuntimeError, match='SECRET_KEY'):
        create_app(Missing)


def test_test_keys_are_ephemeral():
    class Missing(SecurityConfig):
        SECRET_KEY = None
    assert create_app(Missing).secret_key != create_app(Missing).secret_key


def test_public_key_forgery_rejected_and_real_reset_valid(app):
    forged = jwt.encode({'reset_password': 1, 'exp': time.time() + 600},
                        'you-will-never-guess', algorithm='HS256')
    assert User.verify_reset_password_token(forged) is None
    assert User.verify_reset_password_token(db.session.get(User, 1).get_reset_password_token()).id == 1


def test_login_and_remember_cookie_flags(app):
    response = app.test_client().post('/auth/login', base_url='https://localhost',
        data={'username': 'audit', 'password': 'test-only-password', 'remember_me': 'y'})
    assert response.status_code == 302
    cookies = response.headers.getlist('Set-Cookie')
    for name in ('session=', 'remember_token='):
        cookie = next(value for value in cookies if value.startswith(name))
        assert all(flag in cookie for flag in ('Secure', 'HttpOnly', 'SameSite=Lax'))
