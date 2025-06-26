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
CENSOR = os.getenv('CENSOR', '1').lower() in ('1', 'true', 'yes')

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

def censor_value(val, kind=None):
    if not CENSOR or not val:
        return val
    if kind == 'id':
        return val[:4] + '...' + val[-4:] if len(val) > 8 else '****'
    if kind == 'name':
        # Censor each label in the domain, keep TLD
        if '.' in val:
            parts = val.split('.')
            tld = parts[-1]
            censored_labels = []
            for i, label in enumerate(parts[:-1]):
                if len(label) <= 2:
                    censored_labels.append('*' * len(label))
                else:
                    censored_labels.append(label[:2] + '***')
            return '.'.join(censored_labels + [tld])
        return val[:2] + '***' + val[-2:] if len(val) > 4 else '***'
    return '***'

def censor_env(env_dict):
    CENSOR_KEYS = [
        'CLOUDFLARE_API_TOKEN', 'CLOUDFLARE_AUTH_KEY', 'CLOUDFLARE_AUTH_EMAIL',
        'NEW_IP', 'OLD_IP', 'TARGET_DOMAIN'
    ]
    censored = {}
    for k, v in env_dict.items():
        if k in CENSOR_KEYS and v:
            if 'TOKEN' in k or 'KEY' in k:
                censored[k] = v[:4] + '...' + v[-4:] if len(v) > 8 else '****'
            elif 'EMAIL' in k:
                censored[k] = v[0] + '***@***' + v.split('@')[-1][-3:] if '@' in v else '***'
            elif 'IP' in k:
                censored[k] = v[:3] + '.*.*.' + v.split('.')[-1] if '.' in v else '***'
            elif 'DOMAIN' in k:
                censored[k] = v[:2] + '***' + v[-2:] if len(v) > 4 else '***'
            else:
                censored[k] = '***'
        else:
            censored[k] = v
    return censored

def print_censored_env():
    if not CENSOR:
        print("\nENVIRONMENT (uncensored):")
        env_vars = [
            'CLOUDFLARE_API_TOKEN', 'CLOUDFLARE_AUTH_KEY', 'CLOUDFLARE_AUTH_EMAIL',
            'NEW_IP', 'OLD_IP', 'TARGET_DOMAIN', 'DRY_RUN', 'DEBUG'
        ]
        for k in env_vars:
            print(f"  {k} = {os.getenv(k)}")
        return
    env_vars = [
        'CLOUDFLARE_API_TOKEN', 'CLOUDFLARE_AUTH_KEY', 'CLOUDFLARE_AUTH_EMAIL',
        'NEW_IP', 'OLD_IP', 'TARGET_DOMAIN', 'DRY_RUN', 'DEBUG'
    ]
    env_dict = {k: os.getenv(k) for k in env_vars}
    censored = censor_env(env_dict)
    print("\nCENSORED ENVIRONMENT (safe for screenshot):")
    for k, v in censored.items():
        print(f"  {k} = {v}")

print("\n" + "="*50)
print(f"🚀 Starting Cloudflare DNS update script for {TARGET_DOMAIN or 'all zones'}!")
print("="*50 + "\n")
print_censored_env()

def get_zones():
    url = 'https://api.cloudflare.com/client/v4/zones/?per_page=500'
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    zones = resp.json()['result']
    if TARGET_DOMAIN:
        zones = [z for z in zones if z['name'] == TARGET_DOMAIN]
    return zones

def get_records(zone_id, record_type=None):
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?per_page=500'
    if record_type:
        url += f'&type={record_type}'
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()['result']

def update_generic_record(zone_id, record, new_content):
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record["id"]}'
    data = {
        'type': record['type'],
        'name': record['name'],
        'content': new_content,
        'ttl': record.get('ttl', 3600),
        'proxied': record.get('proxied', False) if record['type'] in ['A', 'AAAA', 'CNAME'] else None
    }
    # Remove proxied if not supported
    if data['proxied'] is None:
        data.pop('proxied')
    resp = requests.put(url, headers=HEADERS, json=data)
    return resp.ok, resp.text

def backup_records(zones, backup_file='cf_backup.json'):
    import json
    backup_data = {}
    for zone in zones:
        zone_id = zone['id']
        zone_name = zone['name']
        backup_data[zone_name] = []
        for rtype in ['A', 'TXT', 'SRV', 'MX']:
            try:
                recs = get_records(zone_id, rtype)
                backup_data[zone_name].extend(recs)
            except Exception as e:
                log_error(f"Failed to fetch {rtype} records for backup in zone {zone_id}: {e}")
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, indent=2)
    log_success(f"Backup completed: {backup_file}")


def restore_records(backup_file='cf_backup.json'):
    import json
    if not os.path.exists(backup_file):
        log_error(f"Backup file not found: {backup_file}")
        return
    with open(backup_file, 'r', encoding='utf-8') as f:
        backup_data = json.load(f)
    for zone_name, records in backup_data.items():
        log_info(f"Restoring records for zone: {zone_name}")
        # Find zone_id by name
        zones = get_zones()
        zone = next((z for z in zones if z['name'] == zone_name), None)
        if not zone:
            log_error(f"Zone not found: {zone_name}")
            continue
        zone_id = zone['id']
        for rec in records:
            # Only restore supported types
            if rec['type'] not in ['A', 'TXT', 'SRV', 'MX']:
                continue
            ok, resp = update_generic_record(zone_id, rec, rec['content'])
            if ok:
                log_success(f"Restored record {rec['id']} ({rec['name']}) [{rec['type']}]")
            else:
                log_error(f"Failed to restore record {rec['id']} ({rec['name']}) [{rec['type']}]")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Cloudflare DNS update script with backup/restore')
    parser.add_argument('--backup', action='store_true', help='Backup all DNS records to cf_backup.json')
    parser.add_argument('--restore', action='store_true', help='Restore DNS records from cf_backup.json')
    args = parser.parse_args()

    zones = get_zones()
    if args.backup:
        backup_records(zones)
        return
    if args.restore:
        restore_records()
        return
    total = 0
    updated = 0
    skipped = 0
    # Support more DNS record types
    record_types = [
        'A', 'AAAA', 'CNAME', 'TXT', 'SRV', 'MX', 'NS', 'PTR', 'CAA', 'CERT', 'DNSKEY', 'DS', 'LOC', 'NAPTR', 'SMIMEA', 'SSHFP', 'SVCB', 'TLSA', 'URI'
    ]
    OLD_IP = os.getenv('OLD_IP')
    for zone in zones:
        zone_id = zone['id']
        if DEBUG:
            debug(f"Found zone ID: {zone_id}")
        all_records = []
        for rtype in record_types:
            try:
                recs = get_records(zone_id, rtype)
                all_records.extend(recs)
            except Exception as e:
                log_error(f"Failed to fetch {rtype} records for zone {zone_id}: {e}")
                if DEBUG:
                    debug(f"[ERROR] Failed to fetch {rtype} records for zone {zone_id}: {e}")
        for rec in all_records:
            total += 1
            if DEBUG:
                debug(f"Raw record: id={rec['id']} type={rec['type']} name={rec['name']} content={rec['content']}")
            if not all([rec.get('id'), rec.get('name'), rec.get('content')]):
                skipped += 1
                log_info(f"[SKIP] Empty field in record {rec}")
                if DEBUG:
                    debug(f"[DEBUG] Skipped: Empty field in record {rec}")
                continue
            should_update = False
            new_content = rec['content']
            if rec['type'] == 'A':
                if rec['content'] != NEW_IP:
                    should_update = True
                    new_content = NEW_IP
            elif OLD_IP and OLD_IP in str(rec['content']):
                should_update = True
                new_content = str(rec['content']).replace(OLD_IP, NEW_IP)
            if not should_update:
                skipped += 1
                censored_id = censor_value(rec['id'], 'id')
                censored_name = censor_value(rec['name'], 'name')
                print(f"⏭️  Skipped record {censored_id} ({censored_name}) [{rec['type']}] (no match or unchanged)")
                if DEBUG:
                    debug(f"[SKIP] Record {censored_id} ({censored_name}) [{rec['type']}] not matching OLD_IP or already updated")
                continue
            censored_id = censor_value(rec['id'], 'id')
            censored_name = censor_value(rec['name'], 'name')
            print(f"{'-'*40}\n🌐 Domain: {censored_name}\n🆔 Record ID: {censored_id}\n📦 Zone ID: {zone_id}\n📄 Type: {rec['type']}\n➡️  Current: {rec['content']}\n➡️  New: {new_content}")
            if DRY_RUN:
                log_dryrun(f"Would update record {rec['id']} ({rec['name']}) [{rec['type']}] in zone {zone_id}: current={rec['content']}, new={new_content}")
                if DEBUG:
                    debug(f"[DRY RUN] Would update record {rec['id']} ({rec['name']}) [{rec['type']}] in zone {zone_id}: current={rec['content']}, new={new_content}")
            else:
                ok, resp = update_generic_record(zone_id, rec, new_content)
                if ok:
                    updated += 1
                    log_success(f"Updated record {rec['id']} ({rec['name']}) [{rec['type']}]" )
                    if DEBUG:
                        debug(f"[SUCCESS] Updated record {rec['id']} [{rec['type']}]" )
                else:
                    log_error(f"Failed to update record {rec['id']} ({rec['name']}) [{rec['type']}]" )
                    if DEBUG:
                        debug(f"[ERROR] Failed to update record {rec['id']} [{rec['type']}]: {resp}")
    print("\n" + "="*50)
    print(f"🎉 DNS update script completed.\nTotal records: {total} | Updated: {updated} | Skipped: {skipped}")
    print("="*50)
    input("\nPress Enter to exit...")

if __name__ == '__main__':
    main()
