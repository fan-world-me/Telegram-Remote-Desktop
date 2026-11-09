<div align="center">

[![Telegram](https://img.shields.io/badge/Telegram-@fan__world__me-2CA5E0?style=flat-square&logo=telegram)](https://t.me/fan_world_me)&nbsp;&nbsp;
[![Discord](https://img.shields.io/badge/Discord-fan__world__me-5865F2?style=flat-square&logo=discord)](https://discord.com/users/1040301536036786248)&nbsp;&nbsp;
[![GitHub](https://img.shields.io/badge/GitHub-fan--world--me-181717?style=flat-square&logo=github)](https://github.com/fan-world-me)&nbsp;&nbsp;
[![Portfolio](https://img.shields.io/badge/Portfolio-fan--world--me.github.io-00e5ff?style=flat-square&logo=githubpages&logoColor=white)](https://fan-world-me.github.io/)

</div>

<br/>

<div align="center">

```
██████╗ ███████╗███╗   ███╗ ██████╗ ████████╗███████╗
██╔══██╗██╔════╝████╗ ████║██╔═══██╗╚══██╔══╝██╔════╝
██████╔╝█████╗  ██╔████╔██║██║   ██║   ██║   █████╗
██╔══██╗██╔══╝  ██║╚██╔╝██║██║   ██║   ██║   ██╔══╝
██║  ██║███████╗██║ ╚═╝ ██║╚██████╔╝   ██║   ███████╗
╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝ ╚═════╝    ╚═╝   ╚══════╝
  Telegram Remote Desktop — control your Windows PC from anywhere
```

</div>

<div align="center">

<img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/python--telegram--bot-20.x-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white"/>
<img src="https://img.shields.io/badge/Windows-10%2F11-0078D4?style=for-the-badge&logo=windows&logoColor=white"/>
<img src="https://img.shields.io/badge/license-GPL--3.0-blueviolet?style=for-the-badge"/>

</div>

<br/>

Telegram bot that gives you full remote control over your Windows PC — file manager, shell, screenshot, process manager, system info, and more. Runs as a silent background process or standalone `.exe`.

### 💭 More about this bot

- 📁 **File manager** — browse, create, move, copy, delete files and folders via chat
- 💻 **Shell** — run any Windows command and get output back in Telegram
- 📸 **Screenshot** — take and receive a screenshot of your desktop instantly
- ⚙️ **Process manager** — list all running processes, kill by name or PID
- 💻 **Sysinfo** — CPU, RAM, disk, network, battery level, uptime
- 📋 **Clipboard** — read clipboard contents remotely
- 🔒 **Lock / Sleep** — lock screen or put PC to sleep from your phone
- ⬇️ **Download files** — send any file from your PC directly to Telegram chat
- ⬆️ **Upload files** — send a file to the bot and it saves to the current directory
- 🔐 **User ID auth** — only your Telegram account can control the bot

---

### 📁 File Manager Commands

| Command | Description |
|---|---|
| `dir [path]` | List files in directory |
| `dir -a [path]` | List all files including hidden |
| `cd <path>` | Change directory (persists between commands) |
| `pwd` | Print current directory |
| `mkdir <path>` | Create directory (recursive) |
| `touch <file>` | Create empty file |
| `rm <path>` | Remove file |
| `rm -r <path>` | Remove directory recursively |
| `mv <src> <dst>` | Move or rename |
| `cp <src> <dst>` | Copy file or directory |
| `rename <old> <new>` | Rename in current directory |
| `find [dir] <pattern>` | Search files by glob pattern |
| `stat <path>` | Detailed file / directory info |
| `download <path>` | Send file to Telegram chat |
| Upload a file | Send any file to the bot — saves to current dir |

### ⚙️ System Commands

| Command | Description |
|---|---|
| `cmd <command>` | Run shell command, get output |
| `ps` | List running processes |
| `kill <name\|pid>` | Terminate process by name or PID |
| `url <link>` | Open URL in browser on the PC |
| `lock` | Lock screen |
| `sleep` | Put PC to sleep |
| `screenshot` | Take and receive screenshot |
| `sysinfo` | CPU / RAM / disk / battery / uptime |
| `clip` | Read clipboard contents |

---

### 🧰 Tech Stack

**Runtime & Framework**

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)
![python-telegram-bot](https://img.shields.io/badge/python--telegram--bot-20.7-2CA5E0?style=flat-square&logo=telegram&logoColor=white)
![asyncio](https://img.shields.io/badge/asyncio-native-00e5ff?style=flat-square)

**System**

![psutil](https://img.shields.io/badge/psutil-processes%20%26%20sysinfo-00b4d8?style=flat-square)
![mss](https://img.shields.io/badge/mss-screenshot-00b4d8?style=flat-square)
![pyperclip](https://img.shields.io/badge/pyperclip-clipboard-00b4d8?style=flat-square)
![ctypes](https://img.shields.io/badge/ctypes-lock%20screen-00b4d8?style=flat-square)

**Build**

![PyInstaller](https://img.shields.io/badge/PyInstaller-exe-F55036?style=flat-square)

---

### 🗂️ Project Structure

```
Telegram-Remote-Desktop/
├── telegram-remote-desktop.py   — main bot: handlers, file manager, system commands
├── telegram-remote-desktop.spec — PyInstaller build spec
├── auth.json                    — TOKEN + CHAT_ID (gitignored, create manually)
├── requirements.txt             — pinned dependencies
└── dist/
    └── telegram-remote-desktop.exe  — standalone executable (built via spec)
```

---

### 🚀 How it works

```
[Incoming message]
        │
        ├── user_id != ALLOWED_USER_ID? ──► "Nothing to see here."
        │
        ▼
[_strip_emoji: normalize button labels → command]
        │
        ├── dir / cd / pwd / mkdir / touch
        ├── rm / mv / cp / rename / find / stat
        ├── download ──────────────────────────► send file to chat
        ├── upload (document received) ────────► save to cwd
        ├── cmd ───────────────────────────────► subprocess → stdout/stderr
        ├── ps / kill ─────────────────────────► psutil
        ├── screenshot ────────────────────────► mss → send photo
        ├── sysinfo ───────────────────────────► psutil metrics
        ├── lock / sleep ──────────────────────► ctypes / rundll32
        └── url ───────────────────────────────► webbrowser.open()
```

---

### 🔧 Setup

**1. Create a bot**

Open [@BotFather](https://t.me/BotFather), send `/newbot`, copy the token.

**2. Get your user ID**

Open [@userinfobot](https://t.me/userinfobot) — it shows your numeric ID.

**3. Create `auth.json`**

```json
{
    "TOKEN": "your-bot-token-here",
    "CHAT_ID": 123456789
}
```

**4. Set your user ID in the script**

```python
ALLOWED_USER_ID = 123456789
```

**5. Install dependencies**

```bash
pip install -r requirements.txt
```

**6. Run**

```bash
python telegram-remote-desktop.py
```

---

### 📦 Build EXE

```bash
pyinstaller telegram-remote-desktop.spec --clean
```

Output: `dist/telegram-remote-desktop.exe` — single file, no console window, `auth.json` bundled inside.

---

### 🔒 Security

> Only the Telegram account with the configured `ALLOWED_USER_ID` can control the bot.
> `auth.json` is gitignored — never commit it.
> The bot replies "Nothing to see here." to any unauthorized user.

---

### 📄 License

[GPL-3.0](LICENSE) © [fan-world-me](https://github.com/fan-world-me)

---

<div align="center">

Made with 🩵 in Ukraine 🇺🇦

[![Telegram](https://img.shields.io/badge/Telegram-@fan__world__me-2CA5E0?style=flat-square&logo=telegram)](https://t.me/fan_world_me)&nbsp;&nbsp;
[![Discord](https://img.shields.io/badge/Discord-fan__world__me-5865F2?style=flat-square&logo=discord)](https://discord.com/users/1040301536036786248)&nbsp;&nbsp;
[![Portfolio](https://img.shields.io/badge/Portfolio-fan--world--me.github.io-00e5ff?style=flat-square&logo=githubpages&logoColor=white)](https://fan-world-me.github.io/)

</div>
