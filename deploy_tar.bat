@echo off
REM Alternative deployment using tar over SSH (no SCP/SFTP needed)

echo ========================================
echo Yanfeng AI Task - Deploy via TAR
echo ========================================
echo.
echo This method uses tar+ssh instead of scp
echo Works even if SFTP is disabled
echo.

set SSH_OPTS=-o MACs=hmac-sha2-256-etm@openssh.com -o StrictHostKeyChecking=no
set TARGET=hassio@192.168.31.66

echo Step 1: Checking requirements...
where ssh >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] SSH not found
    pause
    exit /b 1
)

where tar >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] tar not found
    echo Please install Git for Windows which includes tar
    pause
    exit /b 1
)

echo [OK] SSH and tar found
echo.

echo Step 2: Creating archive...
cd "%~dp0custom_components"
if not exist "yanfeng_ai_task" (
    echo [ERROR] yanfeng_ai_task folder not found
    pause
    exit /b 1
)

echo Creating tar archive...
tar -czf yanfeng_ai_task.tar.gz yanfeng_ai_task
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create archive
    pause
    exit /b 1
)
echo [OK] Archive created: yanfeng_ai_task.tar.gz
echo.

echo Step 3: Uploading via SSH...
echo You will be prompted for password: passwd
echo.

REM Upload tar file via SSH pipe
type yanfeng_ai_task.tar.gz | ssh %SSH_OPTS% %TARGET% "cat > /tmp/yanfeng_ai_task.tar.gz"
if %errorlevel% neq 0 (
    echo [ERROR] Upload failed
    del yanfeng_ai_task.tar.gz
    pause
    exit /b 1
)
echo [OK] Upload complete
echo.

echo Step 4: Extracting on remote...
echo You will be prompted for password again
echo.

ssh %SSH_OPTS% %TARGET% "rm -rf /config/custom_components/yanfeng_ai_task && cd /config/custom_components && tar -xzf /tmp/yanfeng_ai_task.tar.gz && rm /tmp/yanfeng_ai_task.tar.gz"
if %errorlevel% neq 0 (
    echo [ERROR] Extraction failed
    del yanfeng_ai_task.tar.gz
    pause
    exit /b 1
)
echo [OK] Extraction complete
echo.

REM Cleanup
del yanfeng_ai_task.tar.gz
echo [OK] Local archive cleaned up
echo.

echo Step 5: Restarting Home Assistant...
echo You will be prompted for password
echo.

ssh %SSH_OPTS% %TARGET% "ha core restart"
echo [OK] Restart command sent
echo.

echo Waiting 30 seconds...
timeout /t 30 /nobreak >nul

echo ========================================
echo Deployment Complete!
echo ========================================
echo.
echo Check: http://192.168.31.66:8123/config/integrations
echo.
echo Press any key to exit...
pause >nul
