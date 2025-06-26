# Getting Started

This page guides you through the initial setup of **Cloudflare Update IP**.

## 1. Clone the repository

```bash
git clone https://github.com/SkyLostTR/Cloudflare-Update-IP.git
cd Cloudflare-Update-IP
```

## 2. Install dependencies

The script only requires `requests` and `python-dotenv` which are listed in
[`requirements.txt`](../requirements.txt). Install them using pip:

```bash
pip install -r requirements.txt
```

## 3. Configure environment variables

Create a copy of the example environment file and edit it:

```bash
cp .env.example .env
```

Open `.env` in your favourite editor and set the following variables:

- `CLOUDFLARE_API_TOKEN` – your Cloudflare API token with DNS edit permissions.
- `NEW_IP` – the new IP address that all `A` records should point to.
- `TARGET_DOMAIN` (optional) – update only this domain.
- `DRY_RUN` (optional) – set to `1` to simulate updates without applying them.
- `DEBUG` (optional) – set to `1` to enable debug logging.

## 4. Run the script

After configuring the environment, simply execute:

```bash
python CloudflareUpdate.py
```

The script will display each record it intends to update and provide a summary
at the end.
