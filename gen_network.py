#!/usr/bin/env python3
"""
Script to generate a network and endpoints for RPE-021. This script generates the
"final" JSON, manual work is required to achieve more realistic "incremental discovery"
and such.
"""

import argparse
import datetime
import ipaddress
import json
import random


def generateInterface(endpoint_id, ip):
    macAddr = '00:0%01x:%02x:%02x:%02x:%02x' % (random.randint(0, 15), random.randint(0, 255),
        random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    return { 'label': 'eth0', 'interface_id': endpoint_id + '_eth0', 'ipv4': ip, 'mac': macAddr }


def generateNetwork(args):
    """Generate a network with a specified number of different, random endpoints."""
    name = args.network
    genTime = datetime.datetime.now()
    timestamp = genTime.strftime("%Y-%m-%dT%H:%M:%S")

    # Generate the network element
    network = { 'id': name, 'label': name, 'timestamp': timestamp, 'color': 'red', 'elem_type': 'network',
        'data': '', 'cidr_block': args.cidr_block }
    
    allElements = [ network ]

    # Create all possible IPs to draw from
    allIps = [str(ip) for ip in ipaddress.IPv4Network(args.cidr_block)]
    allIps.pop(0) # throw away .0

    # Use a map of IPs to endpoints so they can be sorted in the array
    endpoints = {}

    # Routers
    for i in range(args.routers):
        # Select IP addresses from the start of the CIDR block
        ip = allIps.pop(0)

        # Generate the endpoint
        endpoint = { 'id': ip, 'label': ip, 'timestamp': timestamp, 'color': 'gray', 'data': "",
            'elem_type': 'endpoint', 'endpoint_type': 'router', 'os_type': 'linux',
            'network': name, 'interfaces': [ generateInterface(ip, ip) ] }
        endpoints[ip] = endpoint

    # Switches
    switch_os = ["linux", "unknown"]
    for i in range(args.switches):
        # Select IP addresses from the end of the CIDR block
        ip = allIps.pop(-1)

        # Generate the endpoint
        endpoint = { 'id': ip, 'label': ip, 'timestamp': timestamp, 'color': 'gray', 'data': "",
            'elem_type': 'endpoint', 'endpoint_type': 'switch', 'os_type': random.choice(switch_os),
            'network': name, 'interfaces': [ generateInterface(ip, ip) ] }
        endpoints[ip] = endpoint

    # Firewalls
    fw_os = ["linux", "unknown"]
    for i in range(args.firewalls):
        # Select IP addresses from the start of the CIDR block
        ip = allIps.pop(0)

        # Generate the endpoint
        endpoint = { 'id': ip, 'label': ip, 'timestamp': timestamp, 'color': 'gray', 'data': "",
            'elem_type': 'endpoint', 'endpoint_type': 'firewall', 'os_type': random.choice(fw_os),
            'network': name, 'interfaces': [ generateInterface(ip, ip) ] }
        endpoints[ip] = endpoint

    # Wireless access points
    wap_os = ["linux", "android", "unknown"]
    for i in range(args.waps):
        # Select IP addresses from the start of the CIDR block
        ip = allIps.pop(0)

        # Generate the endpoint
        endpoint = { 'id': ip, 'label': ip, 'timestamp': timestamp, 'color': 'gray', 'data': "",
            'elem_type': 'endpoint', 'endpoint_type': 'wap', 'os_type': random.choice(wap_os),
            'network': name, 'interfaces': [ generateInterface(ip, ip) ] }
        endpoints[ip] = endpoint

    # Linux workstations
    for i in range(args.wslinux):
        # Select a random IP address
        ip = random.choice(allIps)
        allIps.remove(ip)

        if random.randint(0, 99) < 25:
            os_type = 'macosx'
        else:
            os_type = 'linux'

        # Generate the endpoint
        endpoint = { 'id': ip, 'label': ip, 'timestamp': timestamp, 'color': 'gray', 'data': "",
            'elem_type': 'endpoint', 'endpoint_type': 'workstation', 'os_type': os_type,
            'network': name, 'interfaces': [ generateInterface(ip, ip) ] }
        endpoints[ip] = endpoint

    # Windows workstations
    for i in range(args.wswin):
        # Select a random IP address
        ip = random.choice(allIps)
        allIps.remove(ip)

        # Generate the endpoint
        endpoint = { 'id': ip, 'label': ip, 'timestamp': timestamp, 'color': 'gray', 'data': "",
            'elem_type': 'endpoint', 'endpoint_type': 'workstation', 'os_type': 'windows',
            'network': name, 'interfaces': [ generateInterface(ip, ip) ] }
        endpoints[ip] = endpoint

    # Linux servers
    for i in range(args.svrlinux):
        # Select a random IP address
        ip = random.choice(allIps)
        allIps.remove(ip)

        # Generate the endpoint
        endpoint = { 'id': ip, 'label': ip, 'timestamp': timestamp, 'color': 'gray', 'data': "",
            'elem_type': 'endpoint', 'endpoint_type': 'server', 'os_type': 'linux',
            'network': name, 'interfaces': [ generateInterface(ip, ip) ] }
        endpoints[ip] = endpoint

    # Windows servers
    for i in range(args.svrwin):
        # Select a random IP address
        ip = random.choice(allIps)
        allIps.remove(ip)

        # Generate the endpoint
        endpoint = { 'id': ip, 'label': ip, 'timestamp': timestamp, 'color': 'gray', 'data': "",
            'elem_type': 'endpoint', 'endpoint_type': 'server', 'os_type': 'windows',
            'network': name, 'interfaces': [ generateInterface(ip, ip) ] }
        endpoints[ip] = endpoint
    
    # ICS
    ics_os = [ "unknown", "linux" ]
    for i in range(args.ics):
        # Select a random IP address
        ip = random.choice(allIps)
        allIps.remove(ip)

        # Generate the endpoint
        endpoint = { 'id': ip, 'label': ip, 'timestamp': timestamp, 'color': 'gray', 'data': "",
            'elem_type': 'endpoint', 'endpoint_type': "ics_device", 'os_type': random.choice(ics_os),
            'network': name, 'interfaces': [ generateInterface(ip, ip) ] }
        endpoints[ip] = endpoint
    
    # IoT
    iot_os = [ "unknown", "linux", "android" ]
    for i in range(args.iot):
        # Select a random IP address
        ip = random.choice(allIps)
        allIps.remove(ip)

        # Generate the endpoint
        endpoint = { 'id': ip, 'label': ip, 'timestamp': timestamp, 'color': 'gray', 'data': "",
            'elem_type': 'endpoint', 'endpoint_type': "iot_device", 'os_type': random.choice(iot_os),
            'network': name, 'interfaces': [ generateInterface(ip, ip) ] }
        endpoints[ip] = endpoint
    
    # Phones
    phone_os = [ "android", "ios" ]
    for i in range(args.phones):
        # Select a random IP address
        ip = random.choice(allIps)
        allIps.remove(ip)

        # Generate the endpoint (too bad there is no 'phone' endpoint_type)
        endpoint = { 'id': ip, 'label': ip, 'timestamp': timestamp, 'color': 'gray', 'data': "",
            'elem_type': 'endpoint', 'endpoint_type': "workstation", 'os_type': random.choice(phone_os),
            'network': name, 'interfaces': [ generateInterface(ip, ip) ] }
        endpoints[ip] = endpoint
    
    # Add endpoints to allElements sorted by IP address
    epIPs = list(endpoints.keys())
    epIPs.sort()
    for ip in epIPs:
        allElements.append(endpoints[ip])
    
    # If there are at least two endpoints, create some example connections
    epList = allElements[1:] # copy the list so we don't try to connect to a connection!
    if args.example_connections and len(endpoints) >= 2:
        lineTypes = ["solid", "dashed"]
        for i in range(2):
            from_ep = random.choice(epList)
            to_ep = random.choice(epList)
            conn = { 'id': 'connection%d' % (i,), 'label': 'ExConn%d' % (i,), 'timestamp': timestamp,
                'color': 'orange', 'line_type': lineTypes[i % 2], 'data': '', 'elem_type': 'connection',
                'interface_from': from_ep['interfaces'][0]['interface_id'],
                'interface_to': to_ep['interfaces'][0]['interface_id'] }
            allElements.append(conn)
    
    # Print all elements as an array (can then send via `curl` or rpe021_client.py)
    print(json.dumps(allElements, indent=4))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--network', required=True, help="network name")
    parser.add_argument('-c', '--cidr_block', required=True, help="CIDR block, e.g., '192.168.0.0/24'")
    parser.add_argument('--routers', type=int, default=0, help="number of routers")
    parser.add_argument('--switches', type=int, default=0, help="number of switches")
    parser.add_argument('--firewalls', type=int, default=0, help="number of firewalls")
    parser.add_argument('--waps', type=int, default=0, help="number of wireless access points")
    parser.add_argument('--wslinux', type=int, default=0, help="number of Linux workstations")
    parser.add_argument('--wswin', type=int, default=0, help="number of Windows workstations")
    parser.add_argument('--svrlinux', type=int, default=0, help="number of Linux servers")
    parser.add_argument('--svrwin', type=int, default=0, help="number of Windows servers")
    parser.add_argument('--ics', type=int, default=0, help="number of ICS devices")
    parser.add_argument('--iot', type=int, default=0, help="number of IoT devices")
    parser.add_argument('--phones', type=int, default=0, help="number of phones")
    parser.add_argument('--example_connections', action='store_true', help="create example connections")
    args = parser.parse_args()

    generateNetwork(args)
