# Usage

Running the batch file performs the following steps:

1. Reads configuration from `.env`.
2. Retrieves a list of zones from the Cloudflare API.
3. Iterates over each `A` record and updates its content to `NEW_IP`.

Execute the script from a command prompt:

```sh
CloudflareUpdate.bat
```

You will see progress messages similar to:

```
Found zone ID: <zone>
Updating record <record_id> in zone <zone> to IP <NEW_IP>...
[SUCCESS] Updated record <record_id>
```

Failures are highlighted in red. After completion, the script prints a summary.
