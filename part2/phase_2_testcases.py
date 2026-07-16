import phase_2, part_2, time

print("\nPhase 2 Testcases\n\n---------\n")
test_domains = ["example.com", "example.com", "example.com"]
#test 0: tests caching records
#test 1: tests checking and using cached records
#test 2: tests removing expired caches
correct = 0
for i in range(len(test_domains)):
    print(f"Test {i}:")
    try:
        fetched_ip = phase_2.resolve(test_domains[i], phase_2.TYPE_A)
        if fetched_ip:
            google_ips = part_2.lookup_domain_all_ips(test_domains[i])
            print(f"Fetched IP: {fetched_ip}\nGoogle IP's: {google_ips}")
            if fetched_ip in google_ips:
                print("Correct IP!\n")
                correct+=1
            else: 
                print("Incorrect IP.\n")
        print(phase_2.expiry_heap)
        print(phase_2.cached_records)
        if i == 1: phase_2.expiry_heap[0] = (1, 'example.com', 1)
        print()
    except:
        print("Failed!\nSomething Went Wrong.\n")
print(f"Phase 2 Tests Complete!\n{correct}/{len(test_domains)} Tests Passed.\n")