@echo off
REM Create tar.gz for manual upload

echo ========================================
echo Create Deployment Package
echo ========================================
echo.

cd "%~dp0custom_components"
if not exist "yanfeng_ai_task" (
    echo [ERROR] yanfeng_ai_task folder not found
    pause
    exit /b 1
)

echo Creating tar.gz archive...
tar -czf yanfeng_ai_task.tar.gz yanfeng_ai_task
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create archive
    pause
    exit /b 1
)

echo [OK] Archive created successfully!
echo.
echo File location: %CD%\yanfeng_ai_task.tar.gz
echo File size:
dir yanfeng_ai_task.tar.gz | findstr "yanfeng"
echo.

echo ========================================
echo Next Steps
echo ========================================
echo.
echo 1. Open File Browser in your browser:
echo    http://192.168.31.66:8123/7eca76cc_filebrowser-wg
echo.
echo 2. Navigate to /tmp directory
echo.
echo 3. Upload the file:
echo    %CD%\yanfeng_ai_task.tar.gz
echo.
echo 4. Open Web Terminal:
echo    Settings - Add-ons - Advanced SSH ^& Web Terminal - OPEN WEB UI
echo.
echo 5. Run these commands in Web Terminal:
echo.
echo    rm -rf /config/custom_components/yanfeng_ai_task
echo    cd /config/custom_components
echo    tar -xzf /tmp/yanfeng_ai_task.tar.gz
echo    ls -la yanfeng_ai_task/
echo    rm /tmp/yanfeng_ai_task.tar.gz
echo    ha core restart
echo.

echo Opening File Browser in default browser...
start http://192.168.31.66:8123/7eca76cc_filebrowser-wg
timeout /t 2 >nul

echo Opening folder containing tar.gz...
explorer "%CD%"

echo.
echo ========================================
echo Package Ready for Upload!
echo ========================================
echo.
echo Press any key to exit...
pause >nul
