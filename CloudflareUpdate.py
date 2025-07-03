"""Utility script for updating Cloudflare DNS records."""

import os
import sys
import requests
from dotenv import load_dotenv
from typing import Optional
import getpass
from dotenv import find_dotenv
import re
import json

def get_version_from_package_json():
    pkg_path = os.path.join(os.path.dirname(__file__), "package.json")
    try:
        with open(pkg_path, "r", encoding="utf-8") as f:
            pkg = json.load(f)
            return pkg.get("version", "0.0.0")
    except Exception:
        return "0.0.0"

__version__ = get_version_from_package_json()

try:
    from pyfiglet import figlet_format
except ImportError:  # pragma: no cover - optional dependency
    figlet_format = None

# Color output for Windows
try:
    from colorama import init, Fore, Style
    init()
    GREEN = Fore.GREEN
    RED = Fore.RED
    CYAN = Fore.CYAN
    YELLOW = Fore.YELLOW
    RESET = Style.RESET_ALL
except ImportError:
    GREEN = RED = CYAN = YELLOW = RESET = ''

load_dotenv()

DEBUG = os.getenv('DEBUG', '0').lower() in ('1', 'true')
CENSOR = os.getenv('CENSOR', '1').lower() in ('1', 'true', 'yes')

# INTERACTIVE_ENV must be defined before any function uses it
INTERACTIVE_ENV = False

# Global config variables (will be set in init_env)
CLOUDFLARE_API_TOKEN = None
NEW_IP = None
OLD_IP = None
TARGET_DOMAIN = None
DRY_RUN = None
DEBUG = None
CENSOR = None
HEADERS = None
HTML_REPORT = None
CHANGES = []

def log_info(msg: str):
    print(f"{CYAN}ℹ️  {msg}{RESET}")
    """Print an informational message in green."""

def log_success(msg: str):
    """Print a success message."""
    print(f"{GREEN}✅ {msg}{RESET}")

def log_error(msg: str):
    """Print an error message in red."""
    print(f"{RED}❌ {msg}{RESET}")

def log_dryrun(msg: str):
    print(f"{YELLOW}🟡 [DRY RUN] {msg}{RESET}")
    """Print a message when running with --dry-run."""

def check_for_update():
    """Check GitHub for a newer version of this script."""
    url = (
        "https://raw.githubusercontent.com/SkyLostTR/Cloudflare-Update-IP/main/"
        "CloudflareUpdate.py"
    )
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        match = re.search(r"__version__\s*=\s*['\"]([^'\"]+)['\"]", resp.text)
        if match and match.group(1) != __version__:
            remote_version = match.group(1)
            print(
                f"A new version ({remote_version}) is available. "
                f"You have {__version__}."
            )
            choice = input("Update now? (y/N): ").strip().lower()
            if choice in ("y", "yes"):
                try:
                    with open(__file__, "w", encoding="utf-8") as f:
                        f.write(resp.text)
                    print("Updated successfully. Please run the script again.")
                    sys.exit(0)
                except Exception as e:
                    log_error(f"Automatic update failed: {e}")
                    print("Please update manually from GitHub.")
        elif not match:
            log_error("Failed to determine remote version for update check")
    except Exception as e:
        log_error(f"Update check failed: {e}")

def init_env():
    """Load environment variables from .env or ask interactively."""
    global CLOUDFLARE_API_TOKEN, NEW_IP, OLD_IP, TARGET_DOMAIN, DRY_RUN, DEBUG, CENSOR, INTERACTIVE_ENV, HEADERS
    # Try to load .env, if not found or missing required, prompt interactively
    try:
        dotenv_exists = False
        try:
            import importlib
            dotenv_spec = importlib.util.find_spec('dotenv')
            if dotenv_spec is not None:
                dotenv_module = importlib.util.module_from_spec(dotenv_spec)
                dotenv_spec.loader.exec_module(dotenv_module)
                if hasattr(dotenv_module, 'find_dotenv'):
                    dotenv_path = dotenv_module.find_dotenv()
                    dotenv_exists = os.path.exists(dotenv_path) if dotenv_path else False
        except Exception:
            dotenv_exists = False
        if not dotenv_exists:
            for fname in ['.env', '.env.local', '.env.example']:
                if os.path.exists(fname):
                    dotenv_exists = True
                    break
    except Exception:
        dotenv_exists = False

    def get_env(var: str, required: bool = True) -> Optional[str]:
        val = os.getenv(var)
        if required and not val and not INTERACTIVE_ENV:
            print(f"Missing required environment variable: {var}")
            sys.exit(1)
        return val

    if not dotenv_exists or not os.getenv('CLOUDFLARE_API_TOKEN') or not os.getenv('NEW_IP'):
        INTERACTIVE_ENV = True
        env = prompt_for_env()
        CLOUDFLARE_API_TOKEN = env['CLOUDFLARE_API_TOKEN']
        NEW_IP = env['NEW_IP']
        OLD_IP = env['OLD_IP']
        TARGET_DOMAIN = env['TARGET_DOMAIN']
        DRY_RUN = env['DRY_RUN'].lower() in ('1', 'true', 'yes')
        DEBUG = env['DEBUG'].lower() in ('1', 'true', 'yes')
        CENSOR = env['CENSOR'].lower() in ('1', 'true', 'yes')
    else:
        INTERACTIVE_ENV = False
        CLOUDFLARE_API_TOKEN = get_env('CLOUDFLARE_API_TOKEN')
        NEW_IP = get_env('NEW_IP')
        OLD_IP = os.getenv('OLD_IP')
        TARGET_DOMAIN = os.getenv('TARGET_DOMAIN')
        DRY_RUN = os.getenv('DRY_RUN', '0').lower() in ('1', 'true')
        DEBUG = os.getenv('DEBUG', '0').lower() in ('1', 'true')
        CENSOR = os.getenv('CENSOR', '1').lower() in ('1', 'true', 'yes')
    HEADERS = {
        'Authorization': f'Bearer {CLOUDFLARE_API_TOKEN}',
        'Content-Type': 'application/json',
    }

def debug(msg: str):
    """Write debug messages to a file when DEBUG is enabled."""
    if DEBUG:
        with open('debug_output.txt', 'a', encoding='utf-8') as f:
            f.write(msg + '\n')

def print_banner():
    text = "Cloudflare Batch Tool"
    if figlet_format:
        banner = figlet_format(text)
    else:
        banner = text
    print(f"{CYAN}{banner}{RESET}")
    print(f"{YELLOW}(credit: @SkyLostTR/@Keeftraum){RESET}")

def censor_value(val, kind=None):
    """Mask sensitive values before printing."""
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
    """Return a copy of env dict with sensitive fields masked."""
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
    """Display environment variables with optional censoring."""
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

def get_zones():
    """Fetch all accessible zones or filter by TARGET_DOMAIN."""
    url = 'https://api.cloudflare.com/client/v4/zones/?per_page=500'
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    zones = resp.json()['result']
    if TARGET_DOMAIN:
        zones = [z for z in zones if z['name'] == TARGET_DOMAIN]
    return zones

def get_records(zone_id, record_type=None):
    """Return DNS records for the given zone."""
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?per_page=500'
    if record_type:
        url += f'&type={record_type}'
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()['result']

def update_generic_record(zone_id, record, new_content):
    """Update a DNS record with new content."""
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
    """Backup all DNS records for all zones to a JSON file."""
    all_data = {}
    for zone in zones:
        zone_id = zone['id']
        zone_name = zone['name']
        try:
            resp = requests.get(f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records', headers=HEADERS)
            resp.raise_for_status()
            records = resp.json().get('result', [])
            all_data[zone_name] = {
                'zone_id': zone_id,
                'records': records
            }
            log_success(f"Backed up {len(records)} records for zone {zone_name}")
        except Exception as e:
            log_error(f"Failed to backup zone {zone_name}: {e}")
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2)
    log_success(f"Backup complete. Saved to {backup_file}")


def restore_records(backup_file='cf_backup.json'):
    """Restore DNS records from a backup JSON file."""
    if not os.path.exists(backup_file):
        log_error(f"Backup file {backup_file} not found.")
        return
    with open(backup_file, 'r', encoding='utf-8') as f:
        all_data = json.load(f)
    for zone_name, data in all_data.items():
        zone_id = data['zone_id']
        records = data['records']
        for rec in records:
            rec_id = rec.get('id')
            rec_data = {k: v for k, v in rec.items() if k not in ['id', 'zone_id', 'zone_name', 'created_on', 'modified_on']}
            try:
                # Try to update if exists, else create
                if rec_id:
                    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{rec_id}'
                    resp = requests.put(url, headers=HEADERS, json=rec_data)
                else:
                    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records'
                    resp = requests.post(url, headers=HEADERS, json=rec_data)
                resp.raise_for_status()
                log_success(f"Restored record {rec.get('name')} ({rec.get('type')}) in {zone_name}")
            except Exception as e:
                log_error(f"Failed to restore record {rec.get('name')} in {zone_name}: {e}")

def generate_html_report(changes, output_file='report.html'):
    html_header = """<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='utf-8'>
    <title>Cloudflare DNS Update Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin:20px; }
        table { border-collapse: collapse; width:100%; }
        th, td { border:1px solid #ddd; padding:8px; }
        th { background-color:#4CAF50; color:white; }
        tr:nth-child(even) { background-color:#f2f2f2; }
    </style>
</head>
<body>
<h2>Cloudflare DNS Update Report</h2>
<table>
<tr><th>Domain</th><th>Record ID</th><th>Type</th><th>Old Content</th><th>New Content</th><th>Status</th></tr>
"""
    rows = []
    for c in changes:
        rows.append(
            f"<tr><td>{c['domain']}</td><td>{c['record_id']}</td><td>{c['type']}</td><td>{c.get('old','')}</td><td>{c.get('new','')}</td><td>{c['status']}</td></tr>"
        )
    html_footer = """</table>
</body>
</html>"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_header + "\n".join(rows) + html_footer)
    log_success(f"HTML report generated: {output_file}")

def prompt_for_env():
    """Prompt the user for all required environment variables."""
    print("\nNo .env file found or required variables missing. Please enter the required parameters:")
    def ask(prompt, default=None, secret=False):
        if default:
            prompt = f"{prompt} [{default}]: "
        else:
            prompt = f"{prompt}: "
        if secret:
            val = getpass.getpass(prompt)
        else:
            val = input(prompt)
        return val if val else default

    api_token = ask("Cloudflare API Token", secret=True)
    new_ip = ask("New IP address (to set)")
    old_ip = ask("Old IP address (to replace, optional)")
    target_domain = ask("Target domain (leave blank for all zones)")
    dry_run = ask("Dry run? (1/0)", default="1")
    debug = ask("Enable debug? (1/0)", default="0")
    censor = ask("Censor output? (1/0)", default="1")
    return {
        'CLOUDFLARE_API_TOKEN': api_token,
        'NEW_IP': new_ip,
        'OLD_IP': old_ip,
        'TARGET_DOMAIN': target_domain,
        'DRY_RUN': dry_run,
        'DEBUG': debug,
        'CENSOR': censor
    }

def main():
    """Entry point for running the update or backup logic."""
    import argparse
    import json
    check_for_update()
    init_env()
    print_banner()
    print("\n" + "="*50)
    print(f"{GREEN}🚀 Starting Cloudflare DNS update script for {TARGET_DOMAIN or 'all zones'}!{RESET}")
    print("="*50 + "\n")
    print_censored_env()
    help_epilog = """Environment variables:\n"
    help_epilog += "  CLOUDFLARE_API_TOKEN  Cloudflare API token with DNS edit permissions (required)\n"
    help_epilog += "  NEW_IP                New IP address to set for records (required)\n"
    help_epilog += "  OLD_IP                Existing IP address to replace (optional)\n"
    help_epilog += "  TARGET_DOMAIN         Only update this zone (optional, default: all zones)\n"
    help_epilog += "  DRY_RUN               Set to 1 to preview changes without applying\n"
    help_epilog += "  DEBUG                 Set to 1 for verbose logging\n"
    help_epilog += "  CENSOR                Set to 0 to show uncensored environment values\n"""  # noqa: E501

    parser = argparse.ArgumentParser(
        description='Cloudflare DNS update script with backup/restore',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=help_epilog,
    )
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument('--backup', action='store_true', help='Backup all DNS records to cf_backup.json')
    parser.add_argument('--restore', action='store_true', help='Restore DNS records from cf_backup.json')
    parser.add_argument('--html-report', metavar='FILE', help='Write HTML report of changes')
    args = parser.parse_args()
    global HTML_REPORT
    HTML_REPORT = args.html_report

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
    # Cloudflare supports a wide range of DNS record types.
    # This list determines which types we will iterate over when updating.
    record_types = [
        'A', 'AAAA', 'CNAME', 'TXT', 'SRV', 'MX', 'NS', 'PTR', 'CAA', 'CERT', 'DNSKEY', 'DS', 'LOC', 'NAPTR', 'SMIMEA', 'SSHFP', 'SVCB', 'TLSA', 'URI'
    ]
    OLD_IP = os.getenv('OLD_IP')
    # Iterate over every zone returned by the API
    for zone in zones:
        zone_id = zone['id']
        if DEBUG:
            debug(f"Found zone ID: {zone_id}")
        all_records = []
        # Fetch records of each supported type
        for rtype in record_types:
            try:
                recs = get_records(zone_id, rtype)
                all_records.extend(recs)
            except Exception as e:
                log_error(f"Failed to fetch {rtype} records for zone {zone_id}: {e}")
                if DEBUG:
                    debug(f"[ERROR] Failed to fetch {rtype} records for zone {zone_id}: {e}")
        # Now iterate through every retrieved record
        for rec in all_records:
            total += 1
            if DEBUG:
                debug(f"Raw record: id={rec['id']} type={rec['type']} name={rec['name']} content={rec['content']}")
            if not all([rec.get('id'), rec.get('name'), rec.get('content')]):
                skipped += 1
                log_info(f"[SKIP] Empty field in record {rec}")
                if DEBUG:
                    debug(f"[DEBUG] Skipped: Empty field in record {rec}")
                CHANGES.append({
                    'domain': rec.get('name'),
                    'record_id': rec.get('id'),
                    'type': rec.get('type'),
                    'old': rec.get('content'),
                    'new': rec.get('content'),
                    'status': 'skipped'
                })
                continue
            should_update = False
            new_content = rec['content']
            # Determine if this record needs to be changed
            if rec['type'] == 'A':
                # For A records we simply compare with the desired NEW_IP
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
                CHANGES.append({
                    'domain': rec['name'],
                    'record_id': rec['id'],
                    'type': rec['type'],
                    'old': rec['content'],
                    'new': rec['content'],
                    'status': 'skipped'
                })
                continue
            censored_id = censor_value(rec['id'], 'id')
            censored_name = censor_value(rec['name'], 'name')
            print(f"{'-'*40}\n🌐 Domain: {censored_name}\n🆔 Record ID: {censored_id}\n📦 Zone ID: {zone_id}\n📄 Type: {rec['type']}\n➡️  Current: {rec['content']}\n➡️  New: {new_content}")
            # Perform the update unless running in dry-run mode
            if DRY_RUN:
                log_dryrun(f"Would update record {rec['id']} ({rec['name']}) [{rec['type']}] in zone {zone_id}: current={rec['content']}, new={new_content}")
                if DEBUG:
                    debug(f"[DRY RUN] Would update record {rec['id']} ({rec['name']}) [{rec['type']}] in zone {zone_id}: current={rec['content']}, new={new_content}")
                CHANGES.append({
                    'domain': rec['name'],
                    'record_id': rec['id'],
                    'type': rec['type'],
                    'old': rec['content'],
                    'new': new_content,
                    'status': 'dry-run'
                })
            else:
                ok, resp = update_generic_record(zone_id, rec, new_content)
                if ok:
                    updated += 1
                    log_success(f"Updated record {rec['id']} ({rec['name']}) [{rec['type']}]" )
                    if DEBUG:
                        debug(f"[SUCCESS] Updated record {rec['id']} [{rec['type']}]" )
                    CHANGES.append({
                        'domain': rec['name'],
                        'record_id': rec['id'],
                        'type': rec['type'],
                        'old': rec['content'],
                        'new': new_content,
                        'status': 'updated'
                    })
                else:
                    log_error(f"Failed to update record {rec['id']} ({rec['name']}) [{rec['type']}]" )
                    if DEBUG:
                        debug(f"[ERROR] Failed to update record {rec['id']} [{rec['type']}]: {resp}")
                    CHANGES.append({
                        'domain': rec['name'],
                        'record_id': rec['id'],
                        'type': rec['type'],
                        'old': rec['content'],
                        'new': new_content,
                        'status': 'failed'
                    })
    print("\n" + "="*50)
    print(f"{GREEN}🎉 DNS update script completed.{RESET}")
    print(f"{CYAN}Total records: {total} | Updated: {updated} | Skipped: {skipped}{RESET}")
    print("="*50)
    if HTML_REPORT:
        generate_html_report(CHANGES, HTML_REPORT)
    input("\nPress Enter to exit...")

if __name__ == '__main__':
    main()
