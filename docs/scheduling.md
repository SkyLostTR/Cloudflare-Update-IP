# Scheduling Automatic Updates

You can run the script on a schedule using **cron** on Linux/macOS or **Task Scheduler** on Windows.

Example cron job to run every day at midnight:

```
0 0 * * * /usr/bin/python3 /path/to/CloudflareUpdate.py >/dev/null 2>&1
```

On Windows, create a task that runs `python CloudflareUpdate.py` at your desired interval.
