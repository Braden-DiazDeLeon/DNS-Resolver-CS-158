import part_3, heapq, time
TYPE_A = part_3.TYPE_A
TYPE_CNAME = part_3.TYPE_CNAME
expiry_heap = []
heapq.heapify(expiry_heap)
cached_records = {
}

def get_ttl(packet, record_type):
    for x in packet.answers:
        if x.type_ == record_type:
            return x.ttl

def resolve(domain_name, record_type):
    nameserver = '198.41.0.4'
    seen = set()
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
        elif record_type != TYPE_CNAME and (domain_name,TYPE_CNAME) in cached_records:
            cname = cached_records[(domain_name,TYPE_CNAME)]
            print(f"Found CNAME: {domain_name} -> {cname}\n")
            if domain_name in seen:
                raise Exception(f'CNAME loop detected: {domain_name} already visited in this chain')
            seen.add(domain_name)
            domain_name = cname
            nameserver = '198.41.0.4'
        else:
            print(f'Cache Miss.\nQuerying {nameserver} for {domain_name}')
            response = part_3.send_query(nameserver, domain_name, record_type)
            if record_type == TYPE_CNAME and (cname := part_3.get_cname(response)):
                cached_records[(domain_name,record_type)] = cname
                heapq.heappush(expiry_heap, (get_ttl(response, TYPE_CNAME) + time.time(), domain_name, record_type))
                return cname
            elif (ip := part_3.get_answer(response)):
                cached_records[(domain_name,record_type)] = ip
                heapq.heappush(expiry_heap, (get_ttl(response, record_type) + time.time(), domain_name, record_type))
                return ip
            elif (cname := part_3.get_cname(response)):
                if domain_name in seen:
                    raise Exception(f'CNAME loop detected: {domain_name} already visited in this chain')
                seen.add(domain_name)
                cached_records[(domain_name,TYPE_CNAME)] = cname
                heapq.heappush(expiry_heap, (get_ttl(response, TYPE_CNAME) + time.time(), domain_name, TYPE_CNAME))
                print(f'CNAME: {domain_name} -> {cname} (restarting query at canonical name)\n')
                domain_name = cname
                nameserver = '198.41.0.4'
            elif (nsIP := part_3.get_nameserver_ip(response)):
                nameserver = nsIP
            elif (ns_domain := part_3.get_nameserver(response)):
                nameserver = resolve(ns_domain, part_3.TYPE_A)
            else:
                raise Exception('something went wrong')
