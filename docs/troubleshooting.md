# Troubleshooting

If the script exits immediately or reports errors, check the following:

- Ensure Python 3 and `requests` library are installed.
- Confirm that `.env` exists and all variables are populated.
- Verify that your API token has permission to edit DNS records.
- Look at `OLD_IP` – if set, only records matching this IP will be changed.

Enable `DEBUG=true` for more verbose output written to `debug_output.txt`.
