# Cloudflare-Update-IP

A Windows batch script to update all Cloudflare DNS records (A records) under your account to a new IP address. Useful for dynamic IP environments or when migrating to a new server.

## Features

- Updates all DNS `A` records for all zones (domains) in your Cloudflare account to a new IP.
- Easy configuration via `.env` file.
- Color-coded output for clarity.
- Designed for Windows (uses batch + PowerShell).

## Prerequisites

- Windows OS
- PowerShell installed (default in modern Windows)
- Cloudflare API credentials (API key & email)

## Setup

1. **Clone the repository:**

   ```sh
   git clone https://github.com/SkyLostTR/Cloudflare-Update-IP.git
   cd Cloudflare-Update-IP
   ```

2. **Configure the `.env` file:**

   - Copy `.env.example` to `.env`:

     ```sh
     copy .env.example .env
     ```

   - Edit `.env` and fill in your details:
     - `CLOUDFLARE_AUTH_EMAIL`: Your Cloudflare email
     - `CLOUDFLARE_AUTH_KEY`: Your Cloudflare API key (recommended: use a restricted API token)
     - `OLD_IP`: (Optional) Your current IP
     - `NEW_IP`: The new IP address you want to set

3. **Run the script:**

   ```sh
   CloudflareUpdate.bat
   ```

## Notes

- The script updates all `A` records for all zones. If you want to restrict this, modify the logic as needed.
- Do **not** share your API key or .env file.
- The script is provided as-is. Test in a safe environment first.

## License

See [LICENSE](LICENSE).