import urllib.request
import ipaddress
import json
import re
from datetime import datetime

DATE = datetime.now().strftime("%Y%m%d")
IP_PATTERN = re.compile(r'^[\d\.:a-fA-F/]+$')

def is_valid_ip(value):
    s = value.strip()
    if not IP_PATTERN.match(s) or len(s) > 43:
        return None
    try:
        net = ipaddress.ip_network(s, strict=False)
        return 'v4' if net.version == 4 else 'v6'
    except ValueError:
        return None

def extract_ips(data):
    v4, v6 = set(), set()
    stack = [data]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            stack.extend(node.values())
        elif isinstance(node, list):
            stack.extend(node)
        elif isinstance(node, str):
            ver = is_valid_ip(node)
            if ver == 'v4':
                v4.add(node.strip())
            elif ver == 'v6':
                v6.add(node.strip())
    return v4, v6

req = urllib.request.Request(
    "https://api.github.com/meta",
    headers={"User-Agent": "Mozilla/5.0"}
)
with urllib.request.urlopen(req) as r:
    meta = json.loads(r.read())

ipv4, ipv6 = extract_ips(meta)

v4_file = f"GitHub_IP4_{DATE}.txt"
v6_file = f"GitHub_IP6_{DATE}.txt"

with open(v4_file, "w") as f:
    f.write("\n".join(sorted(ipv4)))

with open(v6_file, "w") as f:
    f.write("\n".join(sorted(ipv6)))

print(f"Written {len(ipv4)} IPv4 to {v4_file}")
print(f"Written {len(ipv6)} IPv6 to {v6_file}")