# Configuration

The script reads settings from a `.env` file in the project root. Key variables include:

- `CLOUDFLARE_API_TOKEN` – API token with DNS edit permissions (required)
- `NEW_IP` – the IP address that should be assigned to each record
- `OLD_IP` – (optional) only update records currently pointing to this IP
- `TARGET_DOMAIN` – (optional) limit updates to a single zone
- `DRY_RUN` – set to `true` to preview changes without sending updates
- `DEBUG` – set to `true` for verbose logging

Credentials stored in `.env` are read at runtime. **Never commit this file to version control.**
