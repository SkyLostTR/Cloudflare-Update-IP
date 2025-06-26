# Cloudflare Update IP

Welcome to the **Cloudflare Update IP** documentation site. This site is hosted via
[GitHub Pages](https://pages.github.com/) and provides a detailed guide on using
this repository to update your Cloudflare DNS records.

![Banner](assets/banner.png)

## Overview

The `CloudflareUpdate.py` script automates updating all `A` records within one or
more Cloudflare zones. It is useful for migrations or environments where the
server's IP address changes frequently.

Key features:

- Update every `A` record in all zones, or limit updates to a single domain.
- Simple `.env` configuration file.
- Optional **dry-run** mode for testing your setup without applying changes.
- Minimal dependencies and clear console output.

Use the navigation links below to get started.

- [Getting Started](getting-started.md)
- [Usage](usage.md)
- [Frequently Asked Questions](faq.md)
