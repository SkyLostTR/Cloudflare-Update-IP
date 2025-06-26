# Frequently Asked Questions

## How is this different from a dynamic DNS client?

Traditional dynamic DNS clients update a single record when your IP changes.
This script updates **all** `A` records in your Cloudflare account, which is
handy during migrations or bulk updates.

## Can I limit updates to specific records?

Yes. Set `TARGET_DOMAIN` to restrict updates to that domain. You can further
modify the script to add filters if needed.

## Does the script support IPv6 records?

Currently it only manages `A` records. Pull requests are welcome for `AAAA`
record support.

## My API token doesn't work. What permissions are required?

Ensure the token has `Zone:Read` and `DNS:Edit` permissions for the zones you
intend to update.
