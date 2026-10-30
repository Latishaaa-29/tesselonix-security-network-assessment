# Network assessment

See [network-diagram.svg](network-diagram.svg). The runtime inventory and route
tables are in `evidence/network/addressing_routes.txt` and `port_inventory.txt`.

| Node | Edge 172.28.10.0/24 | Internal 172.28.20.0/24 | Role |
|---|---|---|---|
| Docker gateway | .1 | .1 (configured bridge) | Bridge boundaries |
| app | .10 | .11 | HTTP/API and DB client |
| db | — | .10 | PostgreSQL / UDP echo / host firewall |
| netops | .60 | .60 | Authorized administration/tests |
| client | .50 | — | Untrusted edge peer |
| rogue | — | .99 | Unlisted directly connected peer |

Both subnets are /24. The internal bridge has `internal: true`, so it does not
offer ordinary external forwarding. Default routes and gateway behavior are
platform-generated; consult the captured `ip route` and app `/proc/net/route`
rather than assuming each node uses both configured gateways.

App and netops are dual-homed but **not routers**; `ip_forward=0` is explicit.
The app mediates HTTP-to-database operations in userspace. Docker bridges isolate
the segments. The edge client has a default route but no directly connected
internal route; inter-network filtering prevents access. We demonstrate two
subnets and their boundary, not successful IP routing through a router container.
The assignment's router preference is 'where feasible'; this limitation is disclosed.

## Inventory and policy

| Service | Listener | Protocol | Required access |
|---|---|---|---|
| Gunicorn/Flask | app 0.0.0.0:5000 | TCP / HTTP | Client, local browser |
| PostgreSQL | db 0.0.0.0:5432 and IPv6 listener | TCP | App and authorized admin |
| Synthetic UDP echo | db 0.0.0.0:5353 | UDP | Authorized admin demonstration only |
| Docker embedded DNS | Container-local resolver | TCP/UDP 53 | Container name resolution |

IPv6 application-network addressing is not enabled. The host publishes only
`127.0.0.1:5000`; no DB or UDP mapping in secure mode. A bind address inside a
container is not the host's publication address. UDP port 5353 is a synthetic
unicast echo service here, **not an implementation of mDNS**.

The port-only nmap scan labels TCP 5000 `upnp` using its port-name database;
that is not a service fingerprint. The configured Gunicorn listener and real HTTP
responses establish that this lab's service is Flask HTTP, not UPnP.

| Source → destination | app TCP 5000 | db TCP 5432 | db UDP 5353 |
|---|---|---|---|
| client edge | Allow | Deny | Deny |
| app internal | — | Allow | Deny |
| netops internal | Allow | Allow | Allow |
| rogue internal | No requirement | Deny | Deny |
| host loopback | Allow | Deny | Deny |

The network test automates client/app/admin/rogue and host checks. The DB default
DROP policy also denies app UDP by configuration; that specific matrix cell is
not separately probed. No claim that every port on every node was exhaustively
scanned. Netops is a trusted dual-homed administration node, not an untrusted peer.

Firewall: allow loopback and established/related replies; allow TCP 5432 from
`.11` and `.60`; allow UDP 5353 only from `.60`; default-drop INPUT. Docker may
install resolver-related rules in the namespace as well. Capture effective rules
with `iptables -S INPUT`, not only the script. No host firewall is modified.

## N-1 — Unnecessary database access (Medium, controlled misconfiguration)

This weakness is **deliberately introduced in a separate local lab configuration**,
not attributed to the upstream Microblog repository. The insecure override
publishes DB TCP 5432 to host loopback port 15432 and makes the DB firewall permissive.
It also disables `internal: true` in the controlled before-state so Docker permits
host publication. Secure mode restores internal isolation as well as the firewall.
The host can connect and the rogue peer reaches the service. An existing host
service already listens on 5432, so 15432 avoids interfering with it. This grants an
unnecessary attack surface even though PostgreSQL authentication still applies.
No unauthorized database read is claimed. The loopback restriction limits risk
while preserving the unwanted-host-access demonstration.

Reproduce and fix: `python scripts/verify.py network` applies the override, tests
access, tears it down without deleting volumes, then uses the secure file alone.
It removes publication and reinstates source allowlists. Host connections fail,
rogue TCP times out, UDP has no reply, while the app runs a real `SELECT 1` and
the edge client gets HTTP 200. See `n1_before.txt`, `n1_host_after.txt`,
`access_tests.txt` and `firewall_counters.txt`.

Rules reapply in the DB entrypoint on each creation. The runner force-recreates
the stack and verifies host/rogue denial and successful API authentication again:
`redeploy_verified.txt`. This proves persistence of declarative configuration,
not merely a one-off command left in a container namespace.

## TCP/UDP diagnosis and interpretation

The pcap and decoded transcript show TCP SYN, SYN/ACK and ACK on authorized
traffic, plus attempted SYN retransmissions with no success for the rogue source.
A real app SQL query separately establishes usable database communication;
TCP reachability alone does not prove database credentials or a successful query.

UDP has no handshake. Netops sends a synthetic datagram and receives the echo;
client/rogue probes receive no echo. A timeout alone cannot distinguish packet
loss, filtering, wrong route or an unavailable service. The authorized control,
directly connected rogue source, captured requests and increasing default-drop
counters jointly support the firewall conclusion. `nc -u` success exit alone is
not evidence of a delivered datagram.

`traffic.pcap` retains zero-payload TCP segments and synthetic UDP only, using a
BPF length filter. It intentionally excludes TCP auth/query payloads. Capture at
the DB sees incoming packets before INPUT dropping, so seeing a rogue packet in
the trace does not mean it was delivered to PostgreSQL. Edge packets may be
blocked before reaching the DB capture; absence alone does not locate the drop.

Limitations: static source IPs are not identities against a privileged Docker
administrator; Docker/host compromise is outside this lab. Internal DB traffic
is not a claim of encrypted production transport. A production design needs
TLS, stronger identity controls, managed secrets and maintained dependencies.
