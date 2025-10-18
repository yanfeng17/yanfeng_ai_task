@echo off
REM Fix SSH Host Key Changed Error

echo ========================================
echo SSH Host Key Fix Tool
echo ========================================
echo.

echo The SSH server's host key has changed.
echo This is normal after restarting or reconfiguring SSH add-on.
echo.
echo This script will remove the old key from known_hosts file.
echo.

set KNOWN_HOSTS=%USERPROFILE%\.ssh\known_hosts

if not exist "%KNOWN_HOSTS%" (
    echo [OK] known_hosts file does not exist, nothing to fix
    goto :test
)

echo Backing up current known_hosts...
copy "%KNOWN_HOSTS%" "%KNOWN_HOSTS%.backup" >nul
echo [OK] Backup created: %KNOWN_HOSTS%.backup
echo.

echo Removing old key for 192.168.31.66...
findstr /V "192.168.31.66" "%KNOWN_HOSTS%" > "%KNOWN_HOSTS%.tmp"
move /Y "%KNOWN_HOSTS%.tmp" "%KNOWN_HOSTS%" >nul
echo [OK] Old key removed
echo.

:test
echo Testing SSH connection...
echo You will be prompted for password: passwd
echo.

ssh -o MACs=hmac-sha2-256-etm@openssh.com -o StrictHostKeyChecking=accept-new hassio@192.168.31.66 "echo 'SSH Connection Test: OK'"

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo SUCCESS! SSH is working now!
    echo ========================================
    echo.
    echo You can now run deploy_tar.bat
) else (
    echo.
    echo ========================================
    echo Connection still failed
    echo ========================================
    echo.
    echo Please check:
    echo 1. SSH add-on is running
    echo 2. Password is correct: passwd
    echo 3. Network connection: ping 192.168.31.66
)

echo.
echo Press any key to exit...
pause >nul
