# Cloudflare Update IP

Easily update all Cloudflare DNS `A` records to a new IP address using a cross-platform **Python** script. Ideal for server migrations or dynamic IP environments.

## Documentation

- **GitBook-style site:** Full documentation is available in the [docs/](docs/) directory and can be published as a GitBook-style site using HonKit and GitHub Pages (see below).
- **GitHub Wiki:** You can also use the GitHub Wiki for documentation (see instructions below).

## Features

- Updates all DNS `A` records across all zones or a single zone
- Simple `.env`-based configuration
- Colored output via [colorama](https://pypi.org/project/colorama/)
- Runs on any OS with Python 3

## Requirements

- Python 3
- Cloudflare API token with DNS edit permissions

## Quick Start

1. **Clone the repository:**
   ```sh
   git clone https://github.com/SkyLostTR/Cloudflare-Update-IP.git
   cd Cloudflare-Update-IP
   ```
2. **Configure your environment:**
   ```sh
   cp .env.example .env  # use `copy` on Windows
   ```
   Edit `.env` and set:
   - `CLOUDFLARE_API_TOKEN` – your Cloudflare API token
   - `NEW_IP` – the new IP address to assign
   - `OLD_IP` – (optional) the current IP address
   - `TARGET_DOMAIN` – (optional) domain to update (default: all zones)
   - Set `DRY_RUN` to `true` to preview changes
3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
4. **Run the script:**
   ```sh
   python CloudflareUpdate.py
   ```

## Usage

- By default, every `A` record in all zones will be updated. Set `TARGET_DOMAIN` in `.env` to limit updates to a single zone.
- Keep your `.env` file private. **Never commit it to version control.**
- The script uses the [Cloudflare API](https://api.cloudflare.com/).

---

## GitBook-style Documentation (GitHub Pages)

This project supports a GitBook-style documentation site using [HonKit](https://github.com/honkit/honkit), a modern fork of GitBook.

### How to Build and Preview Locally

1. Install Node.js (if not already installed): https://nodejs.org/
2. Install HonKit globally:
   ```powershell
   npm install -g honkit
   ```
3. Install project dependencies:
   ```powershell
   npm install
   ```
4. Build the documentation:
   ```powershell
   npm run docs:build
   ```
   The static site will be generated in `docs/_book`.
5. Preview locally:
   ```powershell
   npm run docs:serve
   ```
   Then open http://localhost:4000 in your browser.

### Publish to GitHub Pages

1. Commit and push your changes to GitHub.
2. In your repository, go to **Settings > Pages**.
3. Set the source to `main` branch and `/docs/_book` folder.
4. Save. Your documentation will be live at `https://<username>.github.io/<repo>/`.

---

## GitHub Wiki

To use the GitHub Wiki for your documentation:

1. Go to your repository on GitHub.
2. Click the **Wiki** tab.
3. Create new pages and copy content from the markdown files in `docs/` (e.g., `getting-started.md`, `usage.md`, etc.).
4. The Wiki is managed separately from your main repo and can be edited directly on GitHub or cloned via git.

---

## License

Released under the MIT License. See [LICENSE](LICENSE).

