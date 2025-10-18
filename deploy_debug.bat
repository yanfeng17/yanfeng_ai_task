@echo off
REM Yanfeng AI Task - Auto Deploy Script (Debug Version)
REM This version has verbose output and won't close on errors

echo ========================================
echo Yanfeng AI Task - Auto Deploy (Debug)
echo ========================================
echo.
echo Target server: hassio@192.168.31.66
echo Script location: %~dp0
echo Current directory: %CD%
echo.

REM Pause to see initial info
timeout /t 2 >nul

echo Step 1: Checking SSH command...
where ssh >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] SSH command not found!
    echo.
    echo Please install Git for Windows or enable OpenSSH Client
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)
echo [OK] SSH found:
where ssh
echo.

echo Step 2: Setting SSH options...
set SSH_OPTS=-o MACs=hmac-sha2-256-etm@openssh.com -o StrictHostKeyChecking=no
set SCP_OPTS=-o MACs=hmac-sha2-256-etm@openssh.com -o StrictHostKeyChecking=no
echo SSH_OPTS=%SSH_OPTS%
echo SCP_OPTS=%SCP_OPTS%
echo.

timeout /t 2 >nul

echo Step 3: Checking local folder...
echo Looking for: %~dp0custom_components\yanfeng_ai_task
if exist "%~dp0custom_components\yanfeng_ai_task" (
    echo [OK] Local folder found
    dir "%~dp0custom_components\yanfeng_ai_task" | findstr /C:"File(s)"
) else (
    echo [ERROR] Local folder NOT found!
    echo Expected path: %~dp0custom_components\yanfeng_ai_task
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)
echo.

timeout /t 2 >nul

echo ========================================
echo [1/4] Deleting old remote folder...
echo ========================================
echo.
echo Command: ssh %SSH_OPTS% hassio@192.168.31.66 "rm -rf /config/custom_components/yanfeng_ai_task"
echo.
echo NOTE: You will be prompted for password
echo Password: passwd
echo.

ssh %SSH_OPTS% hassio@192.168.31.66 "rm -rf /config/custom_components/yanfeng_ai_task"
set DELETE_ERROR=%errorlevel%

echo.
echo Command exit code: %DELETE_ERROR%

if %DELETE_ERROR% neq 0 (
    echo.
    echo [WARN] Delete command returned error code: %DELETE_ERROR%
    echo This might be OK if folder didn't exist
    echo.
    echo Do you want to continue anyway? (Y/N)
    choice /C YN /M "Continue"
    if errorlevel 2 exit /b 1
)
echo [OK] Delete step completed
echo.

timeout /t 2 >nul

echo ========================================
echo [2/4] Uploading new files...
echo ========================================
echo.
echo Source: %~dp0custom_components\yanfeng_ai_task
echo Target: hassio@192.168.31.66:/config/custom_components/
echo.
echo NOTE: You will be prompted for password again
echo Password: passwd
echo.

scp %SCP_OPTS% -r "%~dp0custom_components\yanfeng_ai_task" hassio@192.168.31.66:/config/custom_components/
set UPLOAD_ERROR=%errorlevel%

echo.
echo Command exit code: %UPLOAD_ERROR%

if %UPLOAD_ERROR% neq 0 (
    echo.
    echo [ERROR] Upload failed! Error code: %UPLOAD_ERROR%
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)
echo [OK] Upload successful
echo.

timeout /t 2 >nul

echo ========================================
echo [3/4] Restarting Home Assistant...
echo ========================================
echo.
echo Command: ssh %SSH_OPTS% hassio@192.168.31.66 "ha core restart"
echo.
echo NOTE: You will be prompted for password
echo Password: passwd
echo.

ssh %SSH_OPTS% hassio@192.168.31.66 "ha core restart"
set RESTART_ERROR=%errorlevel%

echo.
echo Command exit code: %RESTART_ERROR%

if %RESTART_ERROR% neq 0 (
    echo [WARN] Restart returned error: %RESTART_ERROR%
    echo This may be normal - HA is restarting...
)
echo [OK] Restart command sent
echo.

echo ========================================
echo [4/4] Waiting for Home Assistant...
echo ========================================
echo.
echo Waiting 30 seconds for HA to restart...
echo.

timeout /t 30 /nobreak

echo ========================================
echo Checking logs...
echo ========================================
echo.
echo NOTE: You will be prompted for password
echo Password: passwd
echo.

ssh %SSH_OPTS% hassio@192.168.31.66 "tail -n 50 /config/home-assistant.log 2>/dev/null | grep -i yanfeng"
if %errorlevel% neq 0 (
    echo.
    echo [WARN] No yanfeng logs found or grep failed
    echo.
    echo View full logs with:
    echo   ssh %SSH_OPTS% hassio@192.168.31.66 "tail -f /config/home-assistant.log"
)

echo.
echo ========================================
echo Deployment Complete!
echo ========================================
echo.
echo Summary:
echo - Delete: Exit code %DELETE_ERROR%
echo - Upload: Exit code %UPLOAD_ERROR%
echo - Restart: Exit code %RESTART_ERROR%
echo.
echo Next steps:
echo 1. Check integration: http://192.168.31.66:8123/config/integrations
echo 2. View logs: ssh %SSH_OPTS% hassio@192.168.31.66 "tail -f /config/home-assistant.log"
echo.
echo TIP: To avoid entering password multiple times,
echo      run setup_ssh_key.bat to configure SSH key authentication
echo.
echo Press any key to exit...
pause >nul
