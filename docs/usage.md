# Usage

This page describes the command-line options and environment variables that
control the behaviour of `CloudflareUpdate.py`.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `CLOUDFLARE_API_TOKEN` | **Required.** API token with DNS edit permissions. |
| `NEW_IP` | **Required.** IP address to apply to all `A` records. |
| `TARGET_DOMAIN` | Optional. If set, only update this domain's zone. |
| `DRY_RUN` | Optional. Set to `1` to preview changes without applying them. |
| `DEBUG` | Optional. Set to `1` for verbose debug output. |

## Dry Run Mode

When `DRY_RUN` is enabled, the script prints out the actions it *would* take
without sending any updates to the Cloudflare API. This is useful for verifying
that your configuration is correct.

## Debug Logging

With `DEBUG` enabled, additional details about API calls and record processing
are written to `debug_output.txt`. Review this file if something does not work as
expected.

## Example

```bash
DRY_RUN=1 DEBUG=1 python CloudflareUpdate.py
```

This command performs a dry run with debug output so you can inspect all steps.
