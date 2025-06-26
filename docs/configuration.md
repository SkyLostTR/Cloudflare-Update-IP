# Configuration

The script reads settings from a `.env` file in the project root. The following variables are supported:

- `CLOUDFLARE_AUTH_EMAIL` – your Cloudflare account email
- `CLOUDFLARE_AUTH_KEY` – your API key or API token with permission to edit DNS records
- `NEW_IP` – the IP address that should be assigned to each record
- `OLD_IP` – (optional) the current IP address to replace

Credentials stored in `.env` are read by the batch script at runtime. Never commit this file to version control.

Create your `.env` file based on `.env.example` and update the values accordingly.
