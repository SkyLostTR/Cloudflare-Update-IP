# Usage

When executed, `CloudflareUpdate.bat` iterates through all zones in your Cloudflare account and updates every `A` record to use the `NEW_IP` specified in the `.env` file. Progress messages are displayed in color using PowerShell.

Use this tool with caution, as it will modify every `A` record in all zones accessible with your API credentials.
