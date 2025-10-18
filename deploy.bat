@echo off
REM Yanfeng AI Task - Auto Deploy Script with SSH compatibility fixes
REM This script will delete old files, upload new files, and restart Home Assistant

echo ========================================
echo Yanfeng AI Task - Auto Deploy
echo ========================================
echo.
echo Target server: hassio@192.168.31.66
echo Script location: %~dp0
echo Note: Using SSH compatibility options for HAOS
echo.

REM Check SSH command
where ssh >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] SSH command not found!
    echo.
    echo Please install:
    echo - Git for Windows (includes SSH): https://git-scm.com/download/win
    echo - Or enable OpenSSH Client in Windows Optional Features
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)
echo [OK] SSH command check passed
echo.

REM Set SSH options for compatibility with HAOS
REM HAOS uses ETM (Encrypt-then-MAC) algorithms
set SSH_OPTS=-o MACs=hmac-sha2-256-etm@openssh.com -o StrictHostKeyChecking=no
set SCP_OPTS=-o MACs=hmac-sha2-256-etm@openssh.com -o StrictHostKeyChecking=no

echo ========================================
echo [1/4] Deleting old remote folder...
echo ========================================
echo Command: ssh %SSH_OPTS% hassio@192.168.31.66 "rm -rf /config/custom_components/yanfeng_ai_task"
ssh %SSH_OPTS% hassio@192.168.31.66 "rm -rf /config/custom_components/yanfeng_ai_task"
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Delete failed! Error code: %errorlevel%
    echo.
    echo Possible causes:
    echo 1. SSH connection failed
    echo 2. Password required
    echo 3. Network issue
    echo.
    echo Trying alternative MAC algorithm (umac-128-etm)...
    ssh -o MACs=umac-128-etm@openssh.com -o StrictHostKeyChecking=no hassio@192.168.31.66 "rm -rf /config/custom_components/yanfeng_ai_task"
    if %errorlevel% neq 0 (
        echo [ERROR] All attempts failed
        echo Press any key to exit...
        pause >nul
        exit /b 1
    )
    set SSH_OPTS=-o MACs=umac-128-etm@openssh.com -o StrictHostKeyChecking=no
    set SCP_OPTS=-o MACs=umac-128-etm@openssh.com -o StrictHostKeyChecking=no
    echo [OK] Connected with alternative algorithm
)
echo [OK] Old folder deleted
echo.

echo ========================================
echo [2/4] Uploading new files...
echo ========================================
echo Source: %~dp0custom_components\yanfeng_ai_task
echo Target: hassio@192.168.31.66:/config/custom_components/
echo.
scp %SCP_OPTS% -r "%~dp0custom_components\yanfeng_ai_task" hassio@192.168.31.66:/config/custom_components/
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Upload failed! Error code: %errorlevel%
    echo.
    echo Possible causes:
    echo 1. Source folder not found
    echo 2. SSH connection interrupted
    echo 3. Disk space full
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)
echo [OK] Files uploaded successfully
echo.

echo ========================================
echo [3/4] Restarting Home Assistant...
echo ========================================
echo Command: ssh %SSH_OPTS% hassio@192.168.31.66 "ha core restart"
ssh %SSH_OPTS% hassio@192.168.31.66 "ha core restart"
if %errorlevel% neq 0 (
    echo.
    echo [WARN] Restart command returned error code: %errorlevel%
    echo This may be normal - HA is restarting...
)
echo [OK] Restart command sent
echo.

echo ========================================
echo [4/4] Waiting for Home Assistant...
echo ========================================
echo Waiting 30 seconds for HA to restart...
timeout /t 30 /nobreak >nul
echo.

echo ========================================
echo Checking logs (filtered for 'yanfeng')
echo ========================================
ssh %SSH_OPTS% hassio@192.168.31.66 "tail -n 100 /config/home-assistant.log 2>/dev/null | grep -i yanfeng"
if %errorlevel% neq 0 (
    echo [WARN] No logs found or grep failed
    echo.
    echo To view full logs manually:
    echo   ssh %SSH_OPTS% hassio@192.168.31.66 "tail -f /config/home-assistant.log"
)

echo.
echo ========================================
echo Deployment Complete!
echo ========================================
echo.
echo Next steps:
echo - View logs: ssh %SSH_OPTS% hassio@192.168.31.66 "tail -f /config/home-assistant.log"
echo - Check integration: http://192.168.31.66:8123/config/integrations
echo - Test intent: "Turn on bedroom AC" or "Set AC to 26 degrees"
echo.
echo Press any key to exit...
pause >nul

