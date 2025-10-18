@echo off
REM SSH Key Setup Script for HAOS
REM This script will generate SSH key and prepare it for HAOS

echo ========================================
echo SSH Key Authentication Setup
echo ========================================
echo.

REM Check if SSH key already exists
if exist "%USERPROFILE%\.ssh\id_ed25519.pub" (
    echo [OK] SSH key already exists
    echo Key location: %USERPROFILE%\.ssh\id_ed25519
    echo.
    goto :show_key
)

echo [Step 1/3] Generating new SSH key...
echo.
echo Creating ED25519 key (recommended for HAOS)...
echo Press Enter 3 times when prompted (use default location and no passphrase)
echo.
pause

REM Generate SSH key
ssh-keygen -t ed25519 -C "haos-automation" -f "%USERPROFILE%\.ssh\id_ed25519" -N ""

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to generate SSH key
    echo.
    goto :end
)

echo.
echo [OK] SSH key generated successfully!
echo.

:show_key
echo ========================================
echo [Step 2/3] Your SSH Public Key
echo ========================================
echo.
echo Copy the ENTIRE line below (including 'ssh-ed25519' and everything after):
echo.
echo ----------------------------------------
type "%USERPROFILE%\.ssh\id_ed25519.pub"
echo.
echo ----------------------------------------
echo.

REM Also save to clipboard if possible
where clip >nul 2>&1
if %errorlevel% equ 0 (
    type "%USERPROFILE%\.ssh\id_ed25519.pub" | clip
    echo [OK] Public key copied to clipboard!
    echo.
)

echo ========================================
echo [Step 3/3] Add Key to Home Assistant
echo ========================================
echo.
echo Instructions:
echo 1. Open Home Assistant: http://192.168.31.66:8123
echo 2. Go to: Settings - Add-ons - Advanced SSH ^& Web Terminal
echo 3. Click on "Configuration" tab
echo 4. Find the "authorized_keys" section
echo 5. Click in the text area and paste your key
echo.
echo It should look like this:
echo   authorized_keys:
echo     - "ssh-ed25519 AAAA... haos-automation"
echo.
echo 6. Click Save
echo 7. Go to "Info" tab and click Restart
echo 8. Wait 30 seconds
echo.
echo ========================================
echo Testing Connection
echo ========================================
echo.
echo After you've added the key and restarted the add-on,
echo press any key to test the connection...
pause >nul

echo.
echo Testing SSH connection without password...
ssh -o MACs=hmac-sha2-256-etm@openssh.com -o StrictHostKeyChecking=no hassio@192.168.31.66 "echo 'SSH Key Authentication: SUCCESS'"

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo SUCCESS! SSH Key Authentication Working!
    echo ========================================
    echo.
    echo You can now use deploy.bat without entering password!
    echo.
) else (
    echo.
    echo ========================================
    echo Connection still requires password
    echo ========================================
    echo.
    echo Please check:
    echo 1. Did you paste the ENTIRE public key?
    echo 2. Did you click Save in the SSH add-on?
    echo 3. Did you restart the SSH add-on?
    echo 4. Did you wait 30+ seconds after restart?
    echo.
    echo If issues persist, you can still use deploy.bat with password.
    echo.
)

:end
echo.
echo Press any key to exit...
pause >nul
