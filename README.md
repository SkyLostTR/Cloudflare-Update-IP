# Cloudflare Update IP
Documentation for this project is available in the [docs](docs/) directory.

This repository contains a Windows batch script that updates every `A` record in your Cloudflare account to a new IP address. It is useful when migrating servers or working with dynamic addresses.

## Features

- Updates all DNS `A` records across all zones
- Simple `.env` based configuration
- Colorful output via PowerShell
- Built for Windows environments

## Requirements

- Windows with PowerShell available
- A Cloudflare API token or global API key

## Setup

1. **Clone the repository**
   ```sh
   git clone https://github.com/SkyLostTR/Cloudflare-Update-IP.git
   cd Cloudflare-Update-IP
   ```
2. **Create your configuration**
   ```sh
   copy .env.example .env
   ```
   Edit `.env` and provide:
   - `CLOUDFLARE_AUTH_EMAIL` – your Cloudflare email
   - `CLOUDFLARE_AUTH_KEY` – your API key or token
   - `NEW_IP` – the IP address that should be assigned
   - `OLD_IP` – (optional) the IP address currently in use
3. **Run the script**
   ```sh
   CloudflareUpdate.bat
   ```

## Notes

- Every `A` record in all zones will be updated. Adjust the script if you need more control.
- Keep your `.env` file private. Never commit it to version control.
- The script makes requests to the [Cloudflare API](https://api.cloudflare.com/).

## License

Released under the MIT License. See [LICENSE](LICENSE).

