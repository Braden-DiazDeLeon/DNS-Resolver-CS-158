import part_3, heapq, time, sys

TYPE_A = part_3.TYPE_A
TYPE_CNAME = part_3.TYPE_CNAME

# expiry_time, domain, and type entries so the soonest expiry is always at the root
expiry_heap = []
heapq.heapify(expiry_heap)
cached_records = {}

def get_ttl(packet, record_type):
    for x in packet.answers:
        if x.type_ == record_type:
            return x.ttl

def resolve(domain_name, record_type):
    nameserver = '198.41.0.4'  # a.root-servers.net
    seen = set()  # domains already followed through a CNAME used for loop detection
    while True:
        print("Checking Caches...\n")
        #check caches
        # drain everything that has already expired before trusting a cache hit
        if expiry_heap:
            while len(expiry_heap) > 0 and time.time() >= expiry_heap[0][0]:
                expired_record = heapq.heappop(expiry_heap)
                print(f"Expired Record: {expired_record}\n")
                cached_records.pop((expired_record[1], expired_record[2]))
        else:
            print("No Expired Records")

        if (domain_name, record_type) in cached_records:
            print(f"Found Record: {cached_records[(domain_name, record_type)]}\n")
            return cached_records[(domain_name, record_type)]
        elif record_type != TYPE_CNAME and (domain_name, TYPE_CNAME) in cached_records:
            cname = cached_records[(domain_name, TYPE_CNAME)]
            print(f"Found CNAME: {domain_name} -> {cname}\n")
            if domain_name in seen:
                raise Exception(f'CNAME loop detected: {domain_name} already visited in this chain')
            seen.add(domain_name)
            domain_name = cname
            nameserver = '198.41.0.4'  # cname may live in a different zone so go from root again
        else:
            print(f'Cache Miss.\nQuerying {nameserver} for {domain_name}')
            response = part_3.send_query(nameserver, domain_name, record_type)
            if record_type == TYPE_CNAME and (cname := part_3.get_cname(response)):
                cached_records[(domain_name, record_type)] = cname
                heapq.heappush(expiry_heap, (get_ttl(response, TYPE_CNAME) + time.time(), domain_name, record_type))
                return cname
            elif (ip := part_3.get_answer(response)):
                cached_records[(domain_name, record_type)] = ip
                heapq.heappush(expiry_heap, (get_ttl(response, record_type) + time.time(), domain_name, record_type))
                return ip
            elif (cname := part_3.get_cname(response)):
                if domain_name in seen:
                    raise Exception(f'CNAME loop detected: {domain_name} already visited in this chain')
                seen.add(domain_name)
                cached_records[(domain_name, TYPE_CNAME)] = cname
                heapq.heappush(expiry_heap, (get_ttl(response, TYPE_CNAME) + time.time(), domain_name, TYPE_CNAME))
                print(f'CNAME: {domain_name} -> {cname} (restarting query at canonical name)\n')
                domain_name = cname
                nameserver = '198.41.0.4'
            elif (nsIP := part_3.get_nameserver_ip(response)):
                nameserver = nsIP
            elif (ns_domain := part_3.get_nameserver(response)):
                # no glue record so resolve the nameserver's own name first
                nameserver = resolve(ns_domain, part_3.TYPE_A)
            else:
                raise Exception('something went wrong')


if __name__ == '__main__':
    record_types = {'A': TYPE_A, 'CNAME': TYPE_CNAME}
    if not 2 <= len(sys.argv) <= 3:
        sys.exit(f'usage: python3 {sys.argv[0]} <domain> [A|CNAME]')
    # trailing dot and case are legal in a fully qualified name but our wire encoding wants neither
    domain = sys.argv[1].strip().rstrip('.').lower()
    requested = (sys.argv[2] if len(sys.argv) == 3 else 'A').upper()
    if not domain or requested not in record_types:
        sys.exit(f'usage: python3 {sys.argv[0]} <domain> [A|CNAME]')
    try:
        print(f'\n{domain} {requested} -> {resolve(domain, record_types[requested])}')
    except Exception as e:
        sys.exit(f'\nCould not resolve {domain}: {e}')
