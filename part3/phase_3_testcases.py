import phase_3, part_3, heapq, signal, re, subprocess

print("\nPhase 3 Testcases\n\n---------\n")

# Oracle: `dig +short` (recommended by the assignment). dig shares our network
# vantage, so it matches CDN/anycast answers better than a fixed public resolver.
_IPV4 = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")
def dig_ips(domain):
    out = subprocess.run(["dig", "+short", domain, "A"], capture_output=True, text=True, timeout=15).stdout
    return {line for line in out.split() if _IPV4.match(line)}

# The baseline resolver has no CNAME handling and can loop forever on a CNAME
# whose answer also carries NS records (e.g. reddit), so we bound it with a timer.
class BaselineTimeout(Exception): pass
def _timeout(signum, frame): raise BaselineTimeout()
def run_baseline(domain, seconds=8):
    signal.signal(signal.SIGALRM, _timeout)
    signal.alarm(seconds)
    try:
        return part_3.resolve(domain, part_3.TYPE_A)
    finally:
        signal.alarm(0)


print("Part 1: CNAME Chasing\n")
test_domains = ["www.nytimes.com", "en.wikipedia.org", "www.reddit.com", "docs.github.com"]
#test 0: multi-hop CNAME chain (several restarts)
#test 1: single CNAME, baseline raises "something went wrong"
#test 2: CNAME + NS in authority, baseline loops forever
#test 3: CNAME to GitHub Pages
correct = 0
for i in range(len(test_domains)):
    print(f"Test {i}: {test_domains[i]}")
    try:
        try:
            print(f"Baseline part_3.resolve: {run_baseline(test_domains[i])}")
        except BaselineTimeout:
            print("Baseline part_3.resolve: HUNG (infinite referral loop)")
        except:
            print("Baseline part_3.resolve: Failed! Something Went Wrong.")
        fetched_ip = phase_3.resolve(test_domains[i], phase_3.TYPE_A)
        if fetched_ip:
            oracle_ips = dig_ips(test_domains[i])
            print(f"Fetched IP: {fetched_ip}\ndig IP's: {oracle_ips}")
            if fetched_ip in oracle_ips:
                print("Correct IP!\n")
                correct+=1
            else:
                print("Incorrect IP.\n")
    except:
        print("Failed!\nSomething Went Wrong.\n")
print(f"CNAME Chasing Complete!\n{correct}/{len(test_domains)} Tests Passed.\n")


print("Part 2: Caching (with CNAMEs)\n")
phase_3.cached_records.clear()
phase_3.expiry_heap.clear()
test_domains = ["en.wikipedia.org", "en.wikipedia.org", "en.wikipedia.org"]
#test 0: caches records 
#test 1: checks and uses the cached records
#test 2: removes expired caches then refetches
correct = 0
for i in range(len(test_domains)):
    print(f"Test {i}:")
    try:
        fetched_ip = phase_3.resolve(test_domains[i], phase_3.TYPE_A)
        if fetched_ip:
            oracle_ips = dig_ips(test_domains[i])
            print(f"Fetched IP: {fetched_ip}\ndig IP's: {oracle_ips}")
            if fetched_ip in oracle_ips:
                print("Correct IP!\n")
                correct+=1
            else:
                print("Incorrect IP.\n")
        print(phase_3.expiry_heap)
        print(phase_3.cached_records)
        if i == 1:
            phase_3.expiry_heap[:] = [(1, name, type_) for (name, type_) in phase_3.cached_records]
            heapq.heapify(phase_3.expiry_heap)
        print()
    except:
        print("Failed!\nSomething Went Wrong.\n")
print(f"Caching Tests Complete!\n{correct}/{len(test_domains)} Tests Passed.\n")


print("Part 3: CNAME Loop Detection\n")
phase_3.cached_records.clear()
phase_3.expiry_heap.clear()
#test 0: a.example -> b.example -> a.example must be signalled as an error RFC 1034 3.6.2
def make_cname_response(target):
    record = part_3.DNSRecord(name=b"", type_=part_3.TYPE_CNAME, class_=1, ttl=60, data=target.encode("utf-8"))
    header = part_3.DNSHeader(id=0, flags=0, num_questions=1, num_answers=1)
    return part_3.DNSPacket(header, [], [record], [], [])
loop_responses = {"a.example": make_cname_response("b.example"), "b.example": make_cname_response("a.example")}
original_send_query = part_3.send_query
part_3.send_query = lambda nameserver, domain_name, record_type: loop_responses[domain_name]
correct = 0
print("Test 0: a.example <-> b.example (CNAME cycle)")
try:
    phase_3.resolve("a.example", phase_3.TYPE_A)
    print("Loop NOT detected.\nIncorrect.\n")
except Exception as e:
    if "loop" in str(e).lower():
        print(f"Loop detected: {e}\nCorrect!\n")
        correct+=1
    else:
        print("Failed!\nSomething Went Wrong.\n")
finally:
    part_3.send_query = original_send_query
print(f"Loop Detection Complete!\n{correct}/1 Tests Passed.\n")

print("Phase 3 Tests Complete!\n")
