# Troubleshooting

If the script exits immediately or reports errors, check the following:

- Ensure PowerShell is available in your `PATH`.
- Confirm that `.env` exists and all variables are populated.
- Verify that your API token has permission to edit DNS records.
- Look at `OLD_IP` – if set, only records matching this IP will be changed.

Enabling `echo on` at the top of `CloudflareUpdate.bat` may help diagnose issues.
