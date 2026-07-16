import part_3, heapq, time
TYPE_A = part_3.TYPE_A
expiry_heap = []
heapq.heapify(expiry_heap)
cached_records = {
}

def get_ttl(packet):
    for x in packet.answers:
        if x.type_ == part_3.TYPE_A:
            return x.ttl

def resolve(domain_name, record_type):
    nameserver = '198.41.0.4'
    while True:
        print("Checking Caches...\n")
        #check caches
        if expiry_heap:
            while len(expiry_heap) > 0 and time.time() >= expiry_heap[0][0]:
                expired_record = heapq.heappop(expiry_heap)
                print(f"Expired Record: {expired_record}\n")
                cached_records.pop((expired_record[1],expired_record[2]))
        else: print("No Expired Records")
        if (domain_name,record_type) in cached_records:
            print(f"Found Record: {cached_records[(domain_name,record_type)]}\n")
            return cached_records[(domain_name,record_type)]
        else:
            print(f'Cache Miss.\nQuerying {nameserver} for {domain_name}')
            response = part_3.send_query(nameserver, domain_name, record_type)
            if (ip := part_3.get_answer(response)):
                cached_records[(domain_name,record_type)] = ip
                heapq.heappush(expiry_heap, (get_ttl(response) + time.time(), domain_name, record_type))
                return ip
            elif (nsIP := part_3.get_nameserver_ip(response)):
                nameserver = nsIP
            elif (ns_domain := part_3.get_nameserver(response)):
                nameserver = resolve(ns_domain, part_3.TYPE_A)
            else:
                raise Exception('something went wrong')