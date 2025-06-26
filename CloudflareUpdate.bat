@echo off
setlocal EnableDelayedExpansion

rem Ensure PowerShell is available
where powershell >nul 2>&1
if errorlevel 1 (
    echo PowerShell is required but was not found in PATH.
    exit /b 1
)

rem Verify configuration file exists
if not exist ".env" (
    echo Missing .env file. Copy .env.example to .env and configure your credentials.
    exit /b 1
)

rem Load variables from .env
for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
    set "%%A=%%B"
)

set "green=powershell -Command \"Write-Host -ForegroundColor Green\""
set "red=powershell -Command \"Write-Host -ForegroundColor Red\""

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

if "%TARGET_DOMAIN%"=="" (
    set "DOMAIN_MSG=all zones"
) else (
    set "DOMAIN_MSG=%TARGET_DOMAIN%"
)

echo Starting Cloudflare DNS update script for %DOMAIN_MSG%...
echo =======================================

rem Fetch zone IDs (filtered by TARGET_DOMAIN if set)
for /f "delims=" %%a in ('powershell -Command "Invoke-RestMethod -Uri https://api.cloudflare.com/client/v4/zones/?per_page=500 -Method GET -Headers @{\"X-Auth-Email\"=\"%CLOUDFLARE_AUTH_EMAIL%\";\"X-Auth-Key\"=\"%CLOUDFLARE_AUTH_KEY%\";\"Content-Type\"=\"application/json\"} | ForEach-Object { $_.result } | Where-Object { \"%TARGET_DOMAIN%\" -eq \"\" -or $_.name -eq \"%TARGET_DOMAIN%\" } | Select-Object -ExpandProperty id"') do (
    set zone_id=%%a
    echo Found zone ID: %%a

    rem Fetch DNS record IDs for the zone
    for /f "delims=" %%b in ('powershell -Command "Invoke-RestMethod -Uri https://api.cloudflare.com/client/v4/zones/%%a/dns_records?per_page=500 -Method GET -Headers @{\"X-Auth-Email\"=\"%CLOUDFLARE_AUTH_EMAIL%\";\"X-Auth-Key\"=\"%CLOUDFLARE_AUTH_KEY%\";\"Content-Type\"=\"application/json\"} | ForEach-Object { $_.result } | Where-Object { $_.type -eq 'A' } | Select-Object -ExpandProperty id"') do (
        set record_id=%%b
        echo Updating record %%b in zone %%a to IP %NEW_IP%...
        powershell -Command "Invoke-RestMethod -Uri 'https://api.cloudflare.com/client/v4/zones/%%a/dns_records/%%b' -Method PUT -Headers @{\"X-Auth-Email\"=\"%CLOUDFLARE_AUTH_EMAIL%\";\"X-Auth-Key\"=\"%CLOUDFLARE_AUTH_KEY%\";\"Content-Type\"=\"application/json\"} -Body (@{type='A'; content='%NEW_IP%'; ttl=3600; proxied=$false} | ConvertTo-Json)" >nul 2>&1
        if !errorlevel! equ 0 (
            !green! "[SUCCESS] Updated record %%b"
        ) else (
            !red! "[ERROR] Failed to update record %%b"
        )
    )
)

echo =======================================
echo DNS update script completed.
pause

