# Usage

Running the Python script performs the following steps:

1. Reads configuration from `.env`.
2. Retrieves a list of zones from the Cloudflare API.
3. Iterates over each `A` record and updates its content to `NEW_IP`.

Execute the script from a terminal:

```sh
python CloudflareUpdate.py
```

You will see progress messages similar to:

```
Found zone ID: <zone>
Updating record <record_id> in zone <zone> to IP <NEW_IP>...
[SUCCESS] Updated record <record_id>
```

Enable `DRY_RUN=true` to simulate changes without modifying DNS records.
