# Getting Started

Clone the repository and copy the example environment file:

```sh
git clone https://github.com/SkyLostTR/Cloudflare-Update-IP.git
cd Cloudflare-Update-IP
copy .env.example .env
```

Edit `.env` with your Cloudflare credentials and desired IP addresses. Set `CLOUDFLARE_AUTH_EMAIL` and `CLOUDFLARE_AUTH_KEY` to a token with permission to edit DNS.

After saving the file, run the batch script:

```sh
CloudflareUpdate.bat
```

Each DNS record will be updated to use the value of `NEW_IP`. Use the `OLD_IP` variable if you only want to update records that currently have a specific address.
