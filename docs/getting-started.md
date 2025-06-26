# Getting Started

Clone the repository and copy the example environment file:

```sh
git clone https://github.com/SkyLostTR/Cloudflare-Update-IP.git
cd Cloudflare-Update-IP
cp .env.example .env
```

Edit `.env` with your Cloudflare token and desired IP addresses. The required variable is `CLOUDFLARE_API_TOKEN` with permission to edit DNS.

Run the script using Python:

```sh
python CloudflareUpdate.py
```

Each DNS record will be updated to use the value of `NEW_IP`. Set `TARGET_DOMAIN` if you only want to update records in a specific zone.
