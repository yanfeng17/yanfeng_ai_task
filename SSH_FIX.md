# SSH MAC Error Fix

## Problem
When connecting to Home Assistant OS, you may encounter:
```
Unable to negotiate with 192.168.31.66 port 22: no matching MAC found.
Their offer: umac-128-etm@openssh.com,hmac-sha2-256-etm@openssh.com,hmac-sha2-512-etm@openssh.com
```

## Root Cause
HAOS uses **ETM (Encrypt-then-MAC)** algorithms, which require the `-etm@openssh.com` suffix.

## Solution
The scripts have been updated to use the correct MAC algorithms:
1. Primary: `hmac-sha2-256-etm@openssh.com` (most common)
2. Fallback: `umac-128-etm@openssh.com` (if primary fails)
3. Also available: `hmac-sha2-512-etm@openssh.com`

## Manual SSH Commands

If you need to run SSH commands manually, use:

```cmd
REM Primary method (recommended)
ssh -o MACs=hmac-sha2-256-etm@openssh.com -o StrictHostKeyChecking=no root@192.168.31.66

REM Alternative (if primary fails)
ssh -o MACs=umac-128-etm@openssh.com -o StrictHostKeyChecking=no root@192.168.31.66

REM With verbose output for debugging
ssh -v -o MACs=hmac-sha2-256-etm@openssh.com root@192.168.31.66
```

## For SCP file transfers

```cmd
scp -o MACs=hmac-sha2-256-etm@openssh.com -o StrictHostKeyChecking=no -r local_folder root@192.168.31.66:/remote/path/
```

## Permanent Fix (Recommended)

Create/edit `~/.ssh/config` (usually `C:\Users\YourName\.ssh\config`):

```
Host 192.168.31.66
    MACs hmac-sha2-256-etm@openssh.com,umac-128-etm@openssh.com,hmac-sha2-512-etm@openssh.com
    StrictHostKeyChecking no
    User root
```

Then you can simply use:
```cmd
ssh 192.168.31.66
```

## Alternative: Restart HAOS SSH Service

If the error persists:
1. Open Home Assistant Web UI
2. Go to Settings → Add-ons
3. Find "Terminal & SSH" or "Advanced SSH & Web Terminal"
4. Click "Restart"
5. Wait 30 seconds
6. Try again

## Common Causes

- **Windows OpenSSH** vs **HAOS Dropbear SSH** compatibility
- Network packet corruption (WiFi interference)
- MTU size mismatches
- SSH server configuration differences

## Current Status

Both scripts now handle this automatically - you shouldn't need to worry about it!
