# Live walkthrough and project explanation

Use this as a rehearsal guide after reviewing the implementation. Do not claim
personal verification until you have actually run and understood it.

## 1. What runs where

The browser sends HTTP to host localhost:5000. Docker forwards this to Gunicorn,
which serves the Flask Microblog app. Flask uses SQLAlchemy to query PostgreSQL
over TCP 5432. The host does not need PostgreSQL or Python app packages installed.
Web login uses Flask-Login sessions; API token creation uses HTTP Basic, and other
API requests use a bearer token. Passwords are hashed by upstream code.

`app/microblog/config.py` supplies settings. `app/__init__.py` creates the app and
extensions. `app/auth/routes.py` implements web auth; `app/api/tokens.py` implements
token creation/revocation. `app/models.py` holds users/posts and reset-token logic.
Alembic migrations create the database schema before Gunicorn starts.

## 2. See the working application

```powershell
docker compose --env-file .env -f lab/docker-compose.net.yml ps
Start-Process http://localhost:5000
```

Register your own local user, log in, create a post and visit Explore. If the
verifier ran, its disposable login is in `.build/demo-login.txt`. Keep that file
private; it is deliberately excluded from Git and the submission ZIP.

## 3. Explain the application findings

A-1: Basic authentication checks credentials on every POST. Without a throttle,
the endpoint accepts repeated attempts. The limiter now counts by the actual
remote peer before authentication. A correct password is also blocked after that
peer has exhausted its allowance. This is why a 429 is expected even for a valid
password at the end of the burst. Memory storage is suitable only for this
single-worker demonstration; multiple workers need shared storage.

A-2: a signing key is not a password hash. It lets the server recognize data it
signed. If everyone knows that key, an attacker can sign a reset token too. The
fix refuses unsafe production configuration and generates a private key locally.
The forgery is rejected while a token signed by the app still works. Existing
deployments using the public fallback must rotate their key and invalidate tokens.

Secure tells a browser to restrict cookies to secure transport (with browser
localhost allowances); HttpOnly prevents ordinary JavaScript from reading them;
SameSite=Lax restricts some cross-site cookie sending. None replaces server-side
authorization, CSRF protection or a private signing key.

```powershell
python scripts/verify.py app
docker run --rm tx-microblog:fixed pytest -q tests.py test_security.py
```

The app phase ends by stopping Task A. Start Task B again for the following demo.

## 4. Explain the network and prove the fix

```powershell
python scripts/verify.py network
docker compose --env-file .env -f lab/docker-compose.net.yml exec db iptables -nvL INPUT
docker compose --env-file .env -f lab/docker-compose.net.yml exec client ip route
docker compose --env-file .env -f lab/docker-compose.net.yml exec netops nc -zv -w 3 172.28.20.10 5432
docker compose --env-file .env -f lab/docker-compose.net.yml exec rogue nc -zv -w 3 172.28.20.10 5432
```

The authorized connection succeeds; rogue times out. The verifier separately
queries the DB through the app. PostgreSQL may listen on all container interfaces,
but only allowed network sources can reach it. Removing a Docker host publication
and applying a DB firewall are separate controls. The host test uses 15432 because
an unrelated service already occupies host port 5432.

TCP performs SYN → SYN/ACK → ACK before application data. A handshake proves
transport reachability, not a valid database login. UDP sends datagrams without
a handshake; the admin echo reply establishes a round trip. No reply could mean
several things, so use captures, the authorized control and counters together.
The synthetic UDP 5353 echo is not DNS or mDNS.

```powershell
docker compose --env-file .env -f lab/docker-compose.net.yml cp evidence/network/traffic.pcap db:/tmp/review.pcap
docker compose --env-file .env -f lab/docker-compose.net.yml exec db tcpdump -nn -r /tmp/review.pcap
```

The two Docker bridges are separate subnets. The app and trusted admin attach to
both, but IP forwarding is disabled. They do not act as routers. HTTP and DB
requests are separate application connections; say so if asked about routing.

## 5. Explain evidence and trade-offs

Open the matching file under `evidence/` as you show each claim. Timestamped
transcripts are actual outputs; `traffic.pcap` is machine-readable packet proof;
screenshots show UI operation. The patch shows precisely what changed from the
baseline. The reports explain meaning and limits rather than replacing raw proof.

Useful questions to rehearse: What happens after a worker restart? Why is IP-only
throttling incomplete? Why does a UDP `nc` exit not prove delivery? Why use a rogue
peer on the internal subnet? What does `internal: true` provide? Why can a packet
appear in tcpdump and still be blocked? Which controls survive recreation?
