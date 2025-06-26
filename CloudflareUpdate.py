import os
import sys
import requests
from dotenv import load_dotenv
from typing import Optional

# Color output for Windows
try:
    from colorama import init, Fore, Style
    init()
    GREEN = Fore.GREEN
    RED = Fore.RED
    RESET = Style.RESET_ALL
except ImportError:
    GREEN = RED = RESET = ''

load_dotenv()

DEBUG = os.getenv('DEBUG', '0').lower() in ('1', 'true')

def debug(msg: str):
    if DEBUG:
        with open('debug_output.txt', 'a', encoding='utf-8') as f:
            f.write(msg + '\n')

def get_env(var: str, required: bool = True) -> Optional[str]:
    val = os.getenv(var)
    if required and not val:
        print(f"Missing required environment variable: {var}")
        sys.exit(1)
    return val

CLOUDFLARE_API_TOKEN = get_env('CLOUDFLARE_API_TOKEN')
NEW_IP = get_env('NEW_IP')
TARGET_DOMAIN = os.getenv('TARGET_DOMAIN')
DRY_RUN = os.getenv('DRY_RUN', '0').lower() in ('1', 'true')

HEADERS = {
    'Authorization': f'Bearer {CLOUDFLARE_API_TOKEN}',
    'Content-Type': 'application/json',
}

def log_info(msg: str):
    print(f"{GREEN}ℹ️  {msg}{RESET}")

def log_success(msg: str):
    print(f"{GREEN}✅ {msg}{RESET}")

def log_error(msg: str):
    print(f"{RED}❌ {msg}{RESET}")

def log_dryrun(msg: str):
    print(f"{GREEN}🟡 [DRY RUN] {msg}{RESET}")

print("\n" + "="*50)
print(f"🚀 Starting Cloudflare DNS update script for {TARGET_DOMAIN or 'all zones'}!")
print("="*50 + "\n")

def get_zones():
    url = 'https://api.cloudflare.com/client/v4/zones/?per_page=500'
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    zones = resp.json()['result']
    if TARGET_DOMAIN:
        zones = [z for z in zones if z['name'] == TARGET_DOMAIN]
    return zones

def get_a_records(zone_id):
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?per_page=500&type=A'
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()['result']

def update_record(zone_id, record, new_ip):
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record["id"]}'
    data = {
        'type': 'A',
        'name': record['name'],
        'content': new_ip,
        'ttl': 3600,
        'proxied': record.get('proxied', False)
    }
    resp = requests.put(url, headers=HEADERS, json=data)
    return resp.ok, resp.text

def main():
    zones = get_zones()
    total = 0
    updated = 0
    skipped = 0
    for zone in zones:
        zone_id = zone['id']
        if DEBUG:
            debug(f"Found zone ID: {zone_id}")
        try:
            records = get_a_records(zone_id)
        except Exception as e:
            log_error(f"Failed to fetch records for zone {zone_id}: {e}")
            if DEBUG:
                debug(f"[ERROR] Failed to fetch records for zone {zone_id}: {e}")
            continue
        for rec in records:
            total += 1
            if DEBUG:
                debug(f"Raw record: id={rec['id']} name={rec['name']} content={rec['content']}")
            if not all([rec.get('id'), rec.get('name'), rec.get('content')]):
                skipped += 1
                log_info(f"[SKIP] Empty field in record {rec}")
                if DEBUG:
                    debug(f"[DEBUG] Skipped: Empty field in record {rec}")
                continue
            print(f"{'-'*40}\n🌐 Domain: {rec['name']}\n🆔 Record ID: {rec['id']}\n📦 Zone ID: {zone_id}\n➡️  Current IP: {rec['content']}\n➡️  New IP: {NEW_IP}")
            if DEBUG:
                debug(f"Updating record {rec['id']} ({rec['name']}) in zone {zone_id} to IP {NEW_IP}...")
            if DRY_RUN:
                log_dryrun(f"Would update record {rec['id']} ({rec['name']}) in zone {zone_id}: current IP={rec['content']}, new IP={NEW_IP}")
                if DEBUG:
                    debug(f"[DRY RUN] Would update record {rec['id']} ({rec['name']}) in zone {zone_id}: current IP={rec['content']}, new IP={NEW_IP}")
            else:
                ok, resp = update_record(zone_id, rec, NEW_IP)
                if ok:
                    updated += 1
                    log_success(f"Updated record {rec['id']} ({rec['name']})")
                    if DEBUG:
                        debug(f"[SUCCESS] Updated record {rec['id']}")
                else:
                    log_error(f"Failed to update record {rec['id']} ({rec['name']})")
                    if DEBUG:
                        debug(f"[ERROR] Failed to update record {rec['id']}: {resp}")
    print("\n" + "="*50)
    print(f"🎉 DNS update script completed.\nTotal records: {total} | Updated: {updated} | Skipped: {skipped}")
    print("="*50)
    input("\nPress Enter to exit...")

if __name__ == '__main__':
    main()
