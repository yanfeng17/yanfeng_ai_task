# SSH Key Authentication Setup Guide

## Quick Start

**Double-click**: `setup_ssh_key.bat`

This script will:
1. Generate an SSH key (if you don't have one)
2. Display your public key
3. Copy it to clipboard
4. Guide you through adding it to HAOS
5. Test the connection

## Manual Setup (Alternative)

### Step 1: Generate SSH Key

```cmd
ssh-keygen -t ed25519 -C "haos-automation"
```

- Press Enter to use default location
- Press Enter twice to skip passphrase (or set one if you prefer)

### Step 2: View Your Public Key

```cmd
type %USERPROFILE%\.ssh\id_ed25519.pub
```

Copy the **entire output** (starts with `ssh-ed25519 AAAA...`)

### Step 3: Add Key to Home Assistant

1. Open: http://192.168.31.66:8123
2. Go to: **Settings → Add-ons → Advanced SSH & Web Terminal**
3. Click **Configuration** tab
4. Find `authorized_keys:` section
5. Modify it to look like this:

```yaml
authorized_keys:
  - "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI... haos-automation"
```

**IMPORTANT**:
- Paste the ENTIRE key on one line
- Keep the quotes
- Use two spaces for indentation
- The `-` indicates a list item

6. Click **Save** (top right)
7. Go to **Info** tab
8. Click **Restart**
9. Wait 30-60 seconds

### Step 4: Test Connection

```cmd
ssh -o MACs=hmac-sha2-256-etm@openssh.com hassio@192.168.31.66 "echo Test"
```

Should connect **without asking for password**!

## After Setup

Once SSH key authentication is working:

- ✅ `test_connection.bat` - No password needed
- ✅ `deploy.bat` - Fully automated deployment!
- ✅ Any SSH command - Instant access

## Troubleshooting

### Issue 1: Still Asks for Password

**Check**:
1. Did you paste the **ENTIRE** public key? (starts with `ssh-ed25519`, ends with `haos-automation`)
2. Is the indentation correct? (two spaces before the `-`)
3. Did you save the configuration?
4. Did you restart the SSH add-on?
5. Did you wait 30+ seconds after restart?

**Fix**:
- Re-paste the key carefully
- Check YAML syntax (use 2 spaces, not tabs)
- Restart add-on again

### Issue 2: "Too Many Authentication Failures"

**Fix**:
```cmd
ssh -o IdentitiesOnly=yes -o IdentityFile=%USERPROFILE%\.ssh\id_ed25519 hassio@192.168.31.66
```

### Issue 3: "Permission Denied (publickey)"

**Check**:
- Is the key format correct in HAOS?
- Did the add-on restart successfully?

**Fix**:
- Remove and re-add the key
- Make sure there are no extra spaces or line breaks

## Configuration Example

**Correct format in SSH add-on**:

```yaml
ssh:
  username: hassio
  password: ""
  authorized_keys:
    - "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGq... haos-automation"
  sftp: false
  compatibility_mode: false
  allow_agent_forwarding: false
  allow_remote_port_forwarding: false
  allow_tcp_forwarding: false
```

**Multiple keys**:

```yaml
authorized_keys:
  - "ssh-ed25519 AAAA... key1"
  - "ssh-ed25519 AAAA... key2"
```

## Security Notes

- ✅ ED25519 keys are modern and secure
- ✅ SSH keys are more secure than passwords
- ✅ Keys are only for 192.168.31.66 (local network)
- ⚠️ Keep your private key (`id_ed25519`) safe - never share it!
- ℹ️ Public key (`id_ed25519.pub`) is safe to share

## After Successful Setup

You can optionally:

1. **Remove password** from SSH add-on config (set to `""`)
2. **Create SSH config** for easier access:

   Edit `C:\Users\YourName\.ssh\config`:
   ```
   Host ha
       HostName 192.168.31.66
       User hassio
       MACs hmac-sha2-256-etm@openssh.com
       StrictHostKeyChecking no
   ```

   Then simply use: `ssh ha`

## Benefits

- 🚀 **Faster**: No password typing
- 🔒 **More Secure**: Keys are harder to crack than passwords
- 🤖 **Automation-Friendly**: Scripts run without interaction
- 💻 **Convenient**: One-time setup, permanent benefit
