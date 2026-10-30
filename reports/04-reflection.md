# Technical reflection and candidate review

This is an assistant-generated engineering reflection on work executed in this
session. It is not a statement of the candidate's personal experience or prior
knowledge. Before submission, the candidate should re-run the demonstrations and
replace or supplement this section with their own observations.

## What required care

Maintaining a true vulnerable baseline matters: building both tags from whichever
branch happens to be checked out would invalidate the comparison. The build script
instead exports a preserved Git tag to a temporary context. A normal clone includes
the vendored target, its attribution and both source states.

The effective signing key is more significant than a string in source. The proof
uses the app's actual verifier and a real disposable user; the fixed app rejects
the forged token and still accepts legitimate tokens. The secret check belongs in
the factory so imports and test configuration remain usable.

Network silence is ambiguous. A directly connected unauthorized node, an authorized
control, packet capture and firewall counters together establish more than an
isolated timeout. The dual-homed app is not a router; explicit terminology avoids
claiming that IP forwarding was demonstrated when it was not.

An existing host service occupied PostgreSQL's usual port. Moving only the lab's
temporary published port to 15432 preserved the internal service and avoided
interfering with unrelated software. This is a real setup observation, distinct
from the deliberately introduced DB exposure used for the assessment.

## Lessons reflected in the implementation

Evidence should come from assertions against running software and be redacted at
capture time. Cookie flags are useful but cannot compensate for a public signing
key. A rate limit can protect one peer bucket while still having distributed and
restart limitations. Static source allowlists are useful in a controlled container
lab but should not be described as strong workload identity.

## What to investigate next

Move rate-limit storage to shared Redis with failure handling and account-aware
policies; add real TLS termination; rotate and manage signing keys outside files;
review and update the old upstream dependency set; examine authorization and API
token lifetime more deeply; add maintained CI supply-chain checks. A separate
router/VM lab could demonstrate actual routed forwarding and traceroute without
conflating application-layer mediation with a network router.

## Candidate rehearsal

Personally run the full verifier, inspect one raw transcript and decode the pcap.
Explain what an HTTP 401, HTTP 429, TCP SYN/ACK, UDP timeout and INPUT DROP counter
each establish. Locate the corresponding fix, modify one allowed source in a lab
copy, predict the effect and verify it. State clearly which work was AI-assisted
and which observations you personally reproduced.
