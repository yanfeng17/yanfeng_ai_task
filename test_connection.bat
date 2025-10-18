@echo off
REM SSH Connection Test Script with MAC algorithm fix

echo ========================================
echo SSH Connection Test (with compatibility fixes)
echo ========================================
echo.

echo [1/4] Checking SSH command...
where ssh >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] SSH command not found!
    echo.
    echo Solutions:
    echo - Install Git for Windows: https://git-scm.com/download/win
    echo - Or enable OpenSSH Client in Windows Optional Features
    echo.
    goto :end
)
echo [OK] SSH command found
echo.

echo [2/4] Testing SSH connection with compatibility options...
echo Command: ssh -o MACs=hmac-sha2-256-etm@openssh.com hassio@192.168.31.66 "echo Test OK"
echo.
ssh -o MACs=hmac-sha2-256-etm@openssh.com -o StrictHostKeyChecking=no hassio@192.168.31.66 "echo 'SSH Connection Test: OK'"
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Connection failed with hmac-sha2-256-etm, trying umac-128-etm...
    echo.
    ssh -o MACs=umac-128-etm@openssh.com -o StrictHostKeyChecking=no hassio@192.168.31.66 "echo 'SSH Connection Test: OK'"
    if %errorlevel% neq 0 (
        echo.
        echo [ERROR] All SSH connection attempts failed!
        echo.
        echo Possible solutions:
        echo 1. Restart SSH service on HAOS (Settings - Add-ons - Terminal SSH - Restart)
        echo 2. Check network: ping 192.168.31.66
        echo 3. Set password in SSH add-on configuration
        echo.
        goto :end
    )
)
echo.
echo [OK] SSH connection successful!
echo.

echo [3/4] Checking remote path...
ssh -o MACs=hmac-sha2-256-etm@openssh.com -o StrictHostKeyChecking=no hassio@192.168.31.66 "ls -la /config/custom_components/ | head -n 5"
if %errorlevel% neq 0 (
    echo [ERROR] Cannot access remote path
    goto :end
)
echo [OK] Remote path accessible
echo.

echo [4/4] Checking local folder...
echo Script location: %~dp0
if exist "%~dp0custom_components\yanfeng_ai_task" (
    echo [OK] Local folder exists
    echo Path: %~dp0custom_components\yanfeng_ai_task
    echo.
    dir "%~dp0custom_components\yanfeng_ai_task" | findstr /C:"File(s)"
) else (
    echo [ERROR] Local folder not found!
    echo Expected: %~dp0custom_components\yanfeng_ai_task
    echo.
    goto :end
)
echo.

echo ========================================
echo All tests passed! You can run deploy.bat
echo ========================================
echo.
echo Note: SSH is using MAC algorithm compatibility mode
echo This is normal for some HAOS configurations

:end
echo.
echo Press any key to exit...
pause >nul
