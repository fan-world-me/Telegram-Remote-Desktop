# Telegram Remote Desktop

Control your Windows PC remotely via Telegram bot.

## Features

- 📸 **Screenshot** — take and receive a screenshot instantly
- 🔒 **Lock / Screen status** — lock the screen or check if it's locked
- 💤 **Sleep** — put the PC to sleep
- 💻 **Sysinfo** — CPU, RAM, disk, network, battery, uptime
- 📋 **Clipboard** — read clipboard contents
- ⚙️ **Processes** — list running processes, kill by name or PID
- 📁 **File manager** — full file management from Telegram
- 💻 **Shell** — run arbitrary commands on the machine

## File Manager Commands

| Command | Description |
|---|---|
| `dir [path]` | List files in directory |
| `dir -a [path]` | List all files including hidden |
| `cd <path>` | Change directory |
| `pwd` | Print current directory |
| `mkdir <path>` | Create directory (recursive) |
| `touch <file>` | Create empty file |
| `rm <path>` | Remove file |
| `rm -r <path>` | Remove directory recursively |
| `mv <src> <dst>` | Move or rename |
| `cp <src> <dst>` | Copy file or directory |
| `rename <old> <new>` | Rename in current directory |
| `find [dir] <pattern>` | Search files by glob pattern |
| `stat <path>` | File/directory info |
| `download <path>` | Send file to Telegram chat |
| Upload a file | Send any file to bot — saves to current dir |

## System Commands

| Command | Description |
|---|---|
| `cmd <command>` | Run shell command |
| `ps` | List processes |
| `kill <name\|pid>` | Terminate process |
| `url <link>` | Open URL in browser |
| `lock` | Lock screen |
| `sleep` | Sleep PC |
| `screenshot` | Take screenshot |
| `sysinfo` | System info |
| `clip` | Clipboard contents |

## Setup

### 1. Create a Telegram bot

1. Open [@BotFather](https://t.me/BotFather) in Telegram
2. Send `/newbot` and follow the steps
3. Copy the bot token

### 2. Get your user ID

Open [@userinfobot](https://t.me/userinfobot) — it will show your numeric user ID.

### 3. Configure auth.json

Create `auth.json` in the project root:

```json
{
    "TOKEN": "your-bot-token-here",
    "CHAT_ID": 123456789
}
```

### 4. Set your user ID

Open `telegram-remote-desktop.py` and update:

```python
ALLOWED_USER_ID = 123456789  # your Telegram user ID
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Run

```bash
python telegram-remote-desktop.py
```

### 7. Build EXE (Windows)

```bash
pyinstaller telegram-remote-desktop.spec --clean
```

The executable will be in `dist/telegram-remote-desktop.exe`.

## Security

- Only the user with the configured `ALLOWED_USER_ID` can control the bot
- `auth.json` is excluded from git — never commit it
- The bot responds with "Nothing to see here" to unauthorized users

## Requirements

- Windows 10/11
- Python 3.9+
- Packages: see `requirements.txt`
