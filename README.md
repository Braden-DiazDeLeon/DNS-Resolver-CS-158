# DNS-Resolver-CS-158

Each part lives in its own self-contained folder with the code it needs and its
own test cases, so it can be run independently.

## part1/ — Recursive Resolver

Files:
 - `part_1.py` — build DNS queries
 - `part_2.py` — parse DNS responses, `lookup_domain` helpers
 - `part_3.py` — recursive `resolve`
 - `phase_1_testcases.py` — test cases

Run:
```
cd part1
python phase_1_testcases.py
```

Testcases:
 - Correctness, compared with IP addresses obtained from google
 - Decision-making when given multiple choices
 - Subdomain
 - Non-existent domain

## part2/ — Caching Resolver

Files:
 - `part_1.py`, `part_2.py`, `part_3.py` — resolver code from part 1
 - `phase_2.py` — resolver with a TTL-aware cache
 - `phase_2_testcases.py` — test cases

Run:
```
cd part2
python phase_2_testcases.py
```

Testcases:
 - The cache being used, for both domains and subqueries
 - Time to live being handled correctly

## part3/ — CNAME chasing and loop detection, compression loop detection

Files:
 - `part_1.py`, `part_2.py`, `part_3.py` — resolver code from part 1.
   - Two small additions to `part_3.py` `TYPE_CNAME` decoding in `parse_record`\
   and a `get_cname` helper method. 
   - Small adjustments to `part_2.py` that implement a counter-based loop
   detection.  
 - `phase_3.py` — resolver with CNAME chasing and loop detection built
   on top of the phase 2 caching which caches CNAME now
 - `phase_3_testcases.py` — test cases

Run:
```
cd part3
python3 phase_3_testcases.py
```

### The gap

#### CNAME
The resolver (`part_3.resolve`) only extracts `A` records
(`get_answer` matches `TYPE_A`) and never looks at `CNAME` records. When it asks
a server for `A example.com` and the name is an alias the server answers with a `CNAME.`
The baseline then finds no `A` answer and either says `something went wrong` 
like `en.wikipedia.org` or loops forever like `www.reddit.com`.

#### Compression
The domain name decoder (`part_2.decode_name`) was unable to handle
compressed names if there was a loop, e.g. a compressed pointer points to
itself creating an infinite loop. This vulnerability can be easily abused 
by malicious users to create a Denial of Service (DoS) attack by infinitely
stalling the resolver in the decoding loop.

### RFC basis

#### CNAME
 - **RFC 1035 §3.3.1 (CNAME RDATA format)** — CNAME rdata is a single
   `<domain-name>`, so it may use message compression and must be decoded with
   pointer support. Fixed in `parse_record` (`elif type_ == TYPE_CNAME: data = decode_name(reader)`).
 - **RFC 1034 §4.3.2, step 3a (name-server algorithm)** — when the node has a
   `CNAME` and `QTYPE` is not `CNAME`, the query is restarted at the canonical
   name. Our resolver does the client-side equivalent: on a `CNAME` answer with
   no matching `A`, it restarts resolution from the root at the canonical name.
 - **RFC 1034 §3.6.2 (aliases)** — "CNAME chains should be followed and CNAME
   loops signalled as an error." We follow chains and detect loops by tracking the set of names already visited in
   the current chain we raise an error instead of looping.
 - **RFC 2181 §10.1 (CNAME and other data)** — an alias has exactly one `CNAME`
   and no other ordinary data at that name; this is why a `CNAME`-only answer is
   valid and must be chased rather than treated as an error.

#### Compression
 - **RFC 9267** — In RFC 1035, infinite loop detection is not explicitly
 stated as a mandatory implemention when handling compression pointers,
 it should still be implemented to prevent attacks such as DoS attacks.
 - **RFC 1035 §2.3.4 (Size limits), §4.1.4 (Message compression)** — 
 There is a limit to the amount of octets for a domain name, 255 octets.
 Since Compression pointers are declared by two octets, with the two most
 first bits as ones. Therefore, the max amount of compression pointers
 should not exceed 255/2 or 128 octets rounded up. By using this number
 as the upper bound, this ensure that all messages that adhere to the 
 standards mentioned are read correctly, while those which violate RFC
 1035 or are malicious are discarded correctly.

### What breaks in the real world without it

#### CNAME
A huge amount of real hostnames are aliases CDNs like Fastly, Akamai,
Cloudflare, load balancers, GitHub Pages, and platform-managed domains all put
a `CNAME` at the name. Without CNAME chasing the resolver doesnt return
addresses for these names so connection is impossible and it can hang instead of failing

#### Compression
Having no loop detection for decoding means that our resolver is vulnerable to
DoS attacks, making it unreliable and easily broken when used in the real world.

### How it was tested

#### CNAME
`phase_3_testcases.py` follows the same structure as `phase_2_testcases.py`
(a `test_domains` loop, `Test i:` prints, a `correct` counter, and an
`X/Y Tests Passed.` summary) and verifies each address against
`dig +short <domain> A`. 

The first part of the test file checks CNAME chasing by comparing the baseline part_3.
resolve implementation with the extended phase_3.resolve implementation and with dig.
For `www.nytimes.com` the baseline resolver fails with `something went wrong.`  
The phase 3 resolver  follows a three hop CNAME chain and returns the IP that matches
dig. For `en.wikipedia.org` the baseline also fails but the phase 3 resolver 
follows a CNAME chain and returns the correct IP. For `www.reddit.com` the baseline
hangs because it falls into an infinite loop while the phase 3 resolver follows the
CNAME correctly and gives a matching IP. For docs.github.com the baseline already
returns an IP because the CNAME and A record are bundled in the response but the 
phase 3 resolver still handles the result correctly and matches dig.

The baseline resolver is bounded by an alarm so that the www.reddit.com hang can be 
shown without causing the entire testcases to hang. 

The second part tests caching by reusing the phase 2 caching test. Test 0 populates the
cache with the CNAME hop and the final A record. The cache stores `en.wikipedia.org 5` 
which points to dyna.wikimedia.org and to 198.35.26.224. Test 1 is  from the cache
printing Found CNAME followed by Found Record. Test 2 then gets rid if 
stale entries by printing Expired Record for both the final A record and the CNAME 
record before getting them from the network.

#### Compression
Compression loop detection is tested in the last part of `phase_3_testcases.py`.
There are two tests: a single hop loop, and a double hop loop, both test directly
call on the `part_2.decode_name`. Both tests are effectively the same situation,
with one test just having a tighter loop.