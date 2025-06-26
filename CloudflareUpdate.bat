@echo off
setlocal enabledelayedexpansion

REM Load variables from .env file
for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
    set "%%A=%%B"
)

:: Set variables for ANSI escape codes for color
set "green=powershell Write-Host -NoNewline '[32m'"
set "red=powershell Write-Host -NoNewline '[31m'"
set "reset=powershell Write-Host -NoNewline '[0m'"

if "%CLOUDFLARE_AUTH_EMAIL%"=="" (
    echo Please set CLOUDFLARE_AUTH_EMAIL in .env file.
    exit /b 1
)
if "%CLOUDFLARE_AUTH_KEY%"=="" (
    echo Please set CLOUDFLARE_AUTH_KEY in .env file.
    exit /b 1
)
if "%NEW_IP%"=="" (
    echo Please set NEW_IP in .env file.
    exit /b 1
)

echo Starting Cloudflare DNS update script...
echo =======================================
echo.

REM Fetch all zone (domain) IDs
for /f "delims=" %%a in ('powershell -Command "Invoke-RestMethod -Uri https://api.cloudflare.com/client/v4/zones/?per_page=500 -Method GET -Headers @{\"X-Auth-Email\"=\"%CLOUDFLARE_AUTH_EMAIL%\";\"X-Auth-Key\"=\"%CLOUDFLARE_AUTH_KEY%\";\"Content-Type\"=\"application/json\"} | ForEach-Object { $_.result } | Select-Object -ExpandProperty id"') do (
    set zone_id=%%a
    echo Found zone ID: %%a
    echo.

    REM Fetch all DNS records for each zone (domain)
    echo Fetching DNS records for zone %%a...
    echo.
    for /f "delims=" %%b in ('powershell -Command "Invoke-RestMethod -Uri https://api.cloudflare.com/client/v4/zones/%%a/dns_records?per_page=500 -Method GET -Headers @{\"X-Auth-Email\"=\"%CLOUDFLARE_AUTH_EMAIL%\";\"X-Auth-Key\"=\"%CLOUDFLARE_AUTH_KEY%\";\"Content-Type\"=\"application/json\"} | ForEach-Object { $_.result } | Where-Object { $_.type -eq 'A' } | Select-Object -ExpandProperty id"') do (
        set record_id=%%b
        echo Found DNS record ID: %%b for zone %%a
        echo.

        REM Update each DNS record to the new IP address
        echo Updating DNS record %%b in zone %%a to new IP %NEW_IP%...
        echo.
        powershell -Command "Invoke-RestMethod -Uri 'https://api.cloudflare.com/client/v4/zones/%%a/dns_records/%%b' -Method PUT -Headers @{\"X-Auth-Email\"=\"%CLOUDFLARE_AUTH_EMAIL%\";\"X-Auth-Key\"=\"%CLOUDFLARE_AUTH_KEY%\";\"Content-Type\"=\"application/json\"} -Body (@{type='A'; content='%NEW_IP%'; ttl=3600; proxied=$false} | ConvertTo-Json)"

        if !errorlevel! equ 0 (
            !green! [SUCCESS] Successfully updated DNS record %%b to IP %NEW_IP%
            echo.
            echo.
            echo =============== NEXT ========================
        ) else (
            !red! [ERROR] Failed to update DNS record %%b in zone %%a.
            echo.
            echo.
            echo =============== NEXT ========================
        )
        echo.
        !reset!
    )
)

echo =======================================
echo DNS update script completed.
pause