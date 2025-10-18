# Quick Start - Deployment Scripts

## Files
- `test_connection.bat` - Test SSH connection and environment
- `deploy.bat` - Auto deploy to Home Assistant

## Usage

### Step 1: Test Connection (First Time)
Double-click: `test_connection.bat`

This will check:
- SSH command availability
- SSH connection to HAOS
- Remote path access
- Local folder existence

### Step 2: Deploy
Double-click: `deploy.bat`

This will:
1. Delete old remote folder
2. Upload new files
3. Restart Home Assistant
4. Show logs

## Troubleshooting

### Issue: Script window closes immediately
**Solution**: Run from command prompt to see errors
```cmd
cd C:\AI Coding\000\yanfeng_ai_task-main
test_connection.bat
```

### Issue: "SSH command not found"
**Solution**: Install Git for Windows
- Download: https://git-scm.com/download/win
- Or enable OpenSSH in Windows Optional Features

### Issue: "Connection failed"
**Solution**: Test SSH manually first
```cmd
ssh root@192.168.31.66
```

## Quick Reference

**View logs manually:**
```cmd
ssh root@192.168.31.66 "tail -f /config/home-assistant.log"
```

**Check integration:**
http://192.168.31.66:8123/config/integrations

**Test intent recognition:**
- Chinese: "打开卧室空调" or "把空调调到26度"
- Should see in logs: "✅ 第一层成功: 意图识别匹配"
