# Scheduling Automatic Updates

You can run the script on a schedule using **Task Scheduler** on Windows. This is useful if your IP address changes frequently.

1. Open Task Scheduler and create a new task.
2. Choose a trigger such as "Daily" or "At startup".
3. Set the action to run `CloudflareUpdate.bat` from the repository directory.
4. Ensure the task runs with sufficient privileges and that the `.env` file is accessible.

Scheduled tasks will execute without user interaction, so keep API tokens secure and consider restricting their permissions to DNS editing only.
