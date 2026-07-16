import part_3, part_2

print("\nPhase 1 Testcases\n\n---------\n")
test_domains = ["example.com", "www.example.com", "google.com", "twitter.com", "yahoo.com", "reddit.com", "www.lasminassunnyvale.com", "target.com", "lolesports.net", "incorrectTest", "incorrectTest.two"]
#somtimes twitter works, sometimes it doesnt because google is not grabbing a whole list of the possible IPs
correct = 0
for i in range(len(test_domains)):
    print(f"Test {i}:")
    try:
        fetched_ip = part_3.resolve(test_domains[i], part_3.TYPE_A)
        if fetched_ip:
            google_ip = part_2.lookup_domain(test_domains[i])
            print(f"Fetched IP: {fetched_ip}\nGoogle IP: {google_ip}")
            if fetched_ip == google_ip:
                print("Correct IP!\n")
                correct+=1
            else: 
                print("Incorrect IP.\n")
    except:
        print("Failed!\nSomething Went Wrong.\n")
print(f"Phase 1 Tests Complete!\n{correct}/{len(test_domains)} Tests Passed.\n")