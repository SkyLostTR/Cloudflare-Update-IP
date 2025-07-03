<p align="center" dir="auto">
   <a href="https://github.com/SkyLostTR/Cloudflare-Update-IP/graphs/contributors">
     <img alt="GitHub Contributors" src="https://img.shields.io/github/contributors/SkyLostTR/Cloudflare-Update-IP" style="max-width: 100%;">
   </a>
   <a href="https://github.com/SkyLostTR/Cloudflare-Update-IP/issues">
     <img alt="Issues" src="https://img.shields.io/github/issues/SkyLostTR/Cloudflare-Update-IP?color=0088ff" style="max-width: 100%;">
   </a>
   <a href="https://github.com/SkyLostTR/Cloudflare-Update-IP/pulls">
     <img alt="GitHub pull requests" src="https://img.shields.io/github/issues-pr/SkyLostTR/Cloudflare-Update-IP?color=0088ff" style="max-width: 100%;">
   </a>
   <a href="https://github.com/SkyLostTR/Cloudflare-Update-IP/stargazers">
     <img alt="GitHub stars" src="https://img.shields.io/github/stars/SkyLostTR/Cloudflare-Update-IP?color=yellow" style="max-width: 100%;">
   </a>
   <a href="https://github.com/SkyLostTR/Cloudflare-Update-IP/network/members">
     <img alt="GitHub forks" src="https://img.shields.io/github/forks/SkyLostTR/Cloudflare-Update-IP?color=orange" style="max-width: 100%;">
   </a>
   <a href="https://github.com/SkyLostTR/Cloudflare-Update-IP/blob/main/LICENSE">
     <img alt="License" src="https://img.shields.io/github/license/SkyLostTR/Cloudflare-Update-IP?color=blue" style="max-width: 100%;">
   </a>
  <a href="https://pypi.org/project/requests/">
    <img alt="Python Version" src="https://img.shields.io/badge/python-3.7%2B-blue.svg" style="max-width: 100%;">
  </a>
  <a href="https://nodejs.org/">
    <img alt="Node Version" src="https://img.shields.io/badge/node-14%2B-green.svg" style="max-width: 100%;">
  </a>
  <a href="https://github.com/SkyLostTR/Cloudflare-Update-IP/actions/workflows/npm-test.yml">
    <img alt="Node.js Tests" src="https://github.com/SkyLostTR/Cloudflare-Update-IP/actions/workflows/npm-test.yml/badge.svg" style="max-width: 100%;">
  </a>
</p>
<!-- Support Buttons -->
<p align="center">
  <a href="https://coff.ee/keeftraum">
    <img src="https://img.shields.io/badge/Buy&nbsp;Me&nbsp;a&nbsp;Coffee-FFDD00?style=for-the-badge&logo=buymeacoffee&logoColor=black" alt="Buy Me a Coffee">
  </a>
  &nbsp;
  <a href="https://github.com/sponsors/SkyLostTR">
    <img src="https://img.shields.io/badge/GitHub&nbsp;Sponsor-ff69b4?style=for-the-badge&logo=github&logoColor=white" alt="GitHub Sponsor">
  </a>
</p>

# Cloudflare Update IP

Easily update all Cloudflare DNS records (A, AAAA, CNAME, TXT, SRV, MX, NS, PTR, CAA, CERT, DNSKEY, DS, LOC, NAPTR, SMIMEA, SSHFP, SVCB, TLSA, URI, and more) to a new IP address using a simple script. Ideal for server migrations, dynamic IP environments, or bulk DNS changes.

The tool can also be installed globally from npm as [`@keeftraum/cloudflare-update-ip`](https://www.npmjs.com/package/@keeftraum/cloudflare-update-ip).

---

## 🚀 Features

- **Bulk Update:** Updates all supported DNS record types across all zones or a single zone.
- **Flexible Matching:** Replaces any occurrence of the old IP in record content with the new IP (not just A records).
- **.env Configuration:** Simple environment variable setup for credentials and options.
- **Dry Run & Debug:** Preview changes and get detailed logs before applying updates.
- **Backup & Restore:** Easily backup and restore DNS records for safety.
- **Colorful Output:** Clear, color-coded console output for easy tracking.
- **HTML Report:** Use `--html-report report.html` to generate a visual summary of all changes.
- **Windows Friendly:** Built for Windows, but works cross-platform with Python.
- **Self-Update Check:** Automatically checks GitHub for a newer version and
  offers to update before running.
- **Interactive Prompts:** Missing environment variables are asked for at runtime.
- **NPM CLI:** Install globally with `npm i -g @keeftraum/cloudflare-update-ip` and run the tool using `cloudflare-update-ip`.

---

## 📦 Requirements

- Python 3.7+
- `requests`, `python-dotenv`, `colorama`, `pyfiglet` (install via `pip install -r requirements.txt`)
- Cloudflare API token with DNS edit permissions
- (Optional) Node.js 14+ for using the npm-based CLI

---

## ⚡ Quick Start

1. **Clone the repository:**
   ```sh
   git clone https://github.com/SkyLostTR/Cloudflare-Update-IP.git
   cd Cloudflare-Update-IP
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Configure your environment:**
   ```sh
   cp .env.example .env   # use `copy` on Windows
   ```
   Edit `.env` and set:
   - `CLOUDFLARE_API_TOKEN` – your Cloudflare API token
   - `NEW_IP` – the new IP address to assign
   - `OLD_IP` – (optional) the current IP address to search/replace
   - `TARGET_DOMAIN` – (optional) domain to update (default: all zones)
   - `DRY_RUN` – (optional) set to `1` to preview changes
   - `DEBUG` – (optional) set to `1` for verbose logging
   - `CENSOR` – (optional) set to `0` to disable censoring of log output
4. **Run the script:**
   ```sh
   python CloudflareUpdate.py --html-report report.html
   ```
   The script will check GitHub for updates before executing.
   Run `python CloudflareUpdate.py -h` to see all available options and
   environment variables.
   
   Backup / Restore:
   ```sh
   python CloudflareUpdate.py --backup
   python CloudflareUpdate.py --restore
   ```

### Use via npm

Alternatively, install the CLI globally from npm and run it anywhere:

```sh
npm install -g @keeftraum/cloudflare-update-ip
cloudflare-update-ip --html-report report.html
```

The npm package runs a postinstall script that installs the required Python
dependencies using `pip`, so make sure Python is available on your system.

---

## 🛠️ Usage

- By default, every supported DNS record (A, AAAA, CNAME, TXT, SRV, MX, NS, PTR, CAA, CERT, DNSKEY, DS, LOC, NAPTR, SMIMEA, SSHFP, SVCB, TLSA, URI, etc.) in all zones will be updated if their content matches the old IP.
- Set `TARGET_DOMAIN` in `.env` to limit updates to a single zone.
- Use `DRY_RUN=1` to preview changes without applying them.
- Use `DEBUG=1` for detailed logs in `debug_output.txt`.
- Use `--html-report report.html` to generate a visual report of all record changes.
- Use `CENSOR=0` to display uncensored environment values in output.
- If installed via npm, run the tool with `cloudflare-update-ip` instead of the Python file.
- Always keep your `.env` file private. **Never commit it to version control.**

## ✅ Tests

Run the automated checks with:

```sh
npm test
```

This compiles the Python script and verifies the Node CLI wrapper.

---

## 📚 Documentation

- **GitHub Wiki:** Full documentation and usage guides are available at: [https://github.com/SkyLostTR/Cloudflare-Update-IP/wiki](https://github.com/SkyLostTR/Cloudflare-Update-IP/wiki)

---

## 🙏 Credits

Created and maintained by [@SkyLostTR](https://github.com/SkyLostTR) ([@Keeftraum](https://github.com/Keeftraum))
ASCII banner generated with [pyfiglet](https://pypi.org/project/pyfiglet/)

---

## 🪪 License

Released under the MIT License. See [LICENSE](LICENSE).

---

## ⚠️ Disclaimer

This project is provided as-is, without any warranty or guarantee of fitness for a particular purpose. Use at your own risk. The author (@SkyLostTR) is not responsible for any data loss, misconfiguration, downtime, or other issues that may arise from using this script. Always backup your DNS records before making bulk changes and review all changes in dry-run mode before applying them.

---

