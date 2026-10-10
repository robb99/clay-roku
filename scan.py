#!/usr/bin/env python3
"""
Roku device scanner - Find Roku devices on your network
"""

import sys
import requests
import concurrent.futures

def check_roku(ip: str, port: int = 8060) -> tuple:
    """Check if a host is a Roku device"""
    try:
        r = requests.get(f'http://{ip}:{port}/query/device-info', timeout=1)
        if r.status_code == 200:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(r.text)
            name = root.findtext('friendly-device-name', 'Unknown')
            model = root.findtext('model-name', 'Unknown')
            return (ip, name, model)
    except:
        pass
    return None


def scan(subnet: str = '192.168.1', start: int = 1, end: int = 254, workers: int = 50):
    """Scan subnet for Roku devices"""
    print(f"Scanning {subnet}.{start}-{end} for Roku devices...")
    
    ips = [f"{subnet}.{i}" for i in range(start, end + 1)]
    found = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        results = executor.map(check_roku, ips)
        for result in results:
            if result:
                found.append(result)
                print(f"  Found: {result[0]} - {result[1]} ({result[2]})")
    
    return found


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Scan network for Roku devices')
    parser.add_argument('--subnet', default='192.168.1', help='Subnet (e.g., 192.168.1)')
    parser.add_argument('--start', type=int, default=1, help='Start IP last octet')
    parser.add_argument('--end', type=int, default=254, help='End IP last octet')
    parser.add_argument('--workers', type=int, default=50, help='Concurrent workers')
    
    args = parser.parse_args()
    
    found = scan(args.subnet, args.start, args.end, args.workers)
    
    if not found:
        print("No Roku devices found. Check your network settings.")
    else:
        print(f"\nFound {len(found)} Roku device(s)")
