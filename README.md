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

## part3/

To be implemented.
