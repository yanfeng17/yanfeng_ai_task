@echo off
REM Debug version of tar deployment

echo ========================================
echo Yanfeng AI Task - Deploy via TAR (Debug)
echo ========================================
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

echo [OK] Archive created
echo File size:
dir yanfeng_ai_task.tar.gz | findstr "yanfeng"
echo.

echo Step 3: Uploading via SSH pipe...
echo Password: passwd
echo.

type yanfeng_ai_task.tar.gz | ssh %SSH_OPTS% %TARGET% "cat > /tmp/yanfeng_ai_task.tar.gz"
if %errorlevel% neq 0 (
    echo [ERROR] Upload failed
    del yanfeng_ai_task.tar.gz
    pause
    exit /b 1
)
echo [OK] Upload complete
echo.

echo Step 4: Checking uploaded file...
echo Password: passwd
echo.

ssh %SSH_OPTS% %TARGET% "ls -lh /tmp/yanfeng_ai_task.tar.gz"
if %errorlevel% neq 0 (
    echo [ERROR] Uploaded file not found
    del yanfeng_ai_task.tar.gz
    pause
    exit /b 1
)
echo [OK] File exists on remote
echo.

echo Step 5: Testing tar command on remote...
echo Password: passwd
echo.

ssh %SSH_OPTS% %TARGET% "which tar"
echo.

echo Step 6: Deleting old folder...
echo Password: passwd
echo.

ssh %SSH_OPTS% %TARGET% "rm -rf /config/custom_components/yanfeng_ai_task"
echo [OK] Old folder deleted (if existed)
echo.

echo Step 7: Extracting archive (verbose)...
echo Password: passwd
echo.
echo Running: cd /config/custom_components && tar -xzvf /tmp/yanfeng_ai_task.tar.gz
echo.

ssh %SSH_OPTS% %TARGET% "cd /config/custom_components && tar -xzvf /tmp/yanfeng_ai_task.tar.gz"
set EXTRACT_ERROR=%errorlevel%

echo.
echo Extraction exit code: %EXTRACT_ERROR%
echo.

if %EXTRACT_ERROR% neq 0 (
    echo [ERROR] Extraction failed with code: %EXTRACT_ERROR%
    echo.
    echo Trying to get error details...
    echo Password: passwd
    echo.
    ssh %SSH_OPTS% %TARGET% "cd /config/custom_components && tar -xzvf /tmp/yanfeng_ai_task.tar.gz 2>&1"
    echo.
    del yanfeng_ai_task.tar.gz
    pause
    exit /b 1
)

echo [OK] Extraction successful
echo.

echo Step 8: Verifying extracted files...
echo Password: passwd
echo.

ssh %SSH_OPTS% %TARGET% "ls -la /config/custom_components/yanfeng_ai_task | head -n 10"
echo.

echo Step 9: Cleanup...
echo Password: passwd
echo.

ssh %SSH_OPTS% %TARGET% "rm /tmp/yanfeng_ai_task.tar.gz"
del yanfeng_ai_task.tar.gz
echo [OK] Cleanup complete
echo.

echo Step 10: Restarting Home Assistant...
echo Password: passwd
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
echo Press any key to exit...
pause >nul
