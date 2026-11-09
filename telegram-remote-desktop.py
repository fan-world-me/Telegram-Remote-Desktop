import asyncio
import json
import os
import shutil
import subprocess
import tempfile
import webbrowser
from pathlib import Path

import psutil
import pyperclip
import ctypes
from mss import mss
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# ─── CONFIG ────────────────────────────────────────────────────────────────────

with open("auth.json") as f:
    auth = json.load(f)

TOKEN = auth["TOKEN"]
CHAT_ID = auth["CHAT_ID"]          # int
ALLOWED_USER_ID = 5128628326       # авторизованный пользователь

# текущая рабочая директория (сохраняется между командами)
cwd = Path.home()

# ─── KEYBOARD ──────────────────────────────────────────────────────────────────

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["📸 Screenshot",  "📋 Clipboard"],
        ["🔒 Lock screen", "⚠️ Screen status"],
        ["💤 Sleep",       "💻 Sysinfo"],
        ["📁 Files",       "⚙️ Processes"],
        ["💡 Help"],
    ],
    resize_keyboard=True,
)

FILES_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["📂 dir",         "📂 dir -a"],
        ["🗂 pwd",         "📁 mkdir"],
        ["📄 touch",       "🗑 rm"],
        ["📦 mv",          "📋 cp"],
        ["🔍 find",        "⬇️ download"],
        ["⬅️ Back"],
    ],
    resize_keyboard=True,
)

# ─── GUARDS ────────────────────────────────────────────────────────────────────

def is_allowed(update: Update) -> bool:
    return update.effective_user.id == ALLOWED_USER_ID

async def deny(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    username = update.effective_user.username or "unknown"
    print(f"[!] Denied access for @{username} (id={uid})")
    await update.message.reply_text("Nothing to see here.")

# ─── SCREENSHOT ────────────────────────────────────────────────────────────────

def take_screenshot() -> str:
    tmp = tempfile.gettempdir()
    with mss() as sct:
        # mon=0 — все мониторы вместе
        path = sct.shot(mon=0, output=os.path.join(tmp, "screenshot.png"))
    return path

# ─── SYSINFO ───────────────────────────────────────────────────────────────────

def get_sysinfo() -> str:
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage(os.path.splitdrive(os.getcwd())[0] + "\\" or "C:\\")
    net = psutil.net_io_counters()

    lines = [
        "💻 *System Info*",
        f"🖥 CPU: `{cpu}%`",
        f"🧠 RAM: `{ram.percent}%` ({_fmt(ram.used)} / {_fmt(ram.total)})",
        f"💾 Disk: `{disk.percent}%` ({_fmt(disk.used)} / {_fmt(disk.total)})",
        f"🌐 Net ↑ {_fmt(net.bytes_sent)}  ↓ {_fmt(net.bytes_recv)}",
    ]

    # батарея (не у всех есть)
    battery = psutil.sensors_battery()
    if battery:
        plug = "🔌" if battery.power_plugged else "🔋"
        lines.append(f"{plug} Battery: `{battery.percent:.0f}%`")

    # uptime
    import datetime
    boot = datetime.datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.datetime.now() - boot
    h, rem = divmod(int(uptime.total_seconds()), 3600)
    m = rem // 60
    lines.append(f"⏱ Uptime: `{h}h {m}m`")

    return "\n".join(lines)

def _fmt(b: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if b < 1024:
            return f"{b:.1f}{unit}"
        b //= 1024
    return f"{b:.1f}PB"

# ─── FILE OPERATIONS ───────────────────────────────────────────────────────────

def resolve(path_str: str) -> Path:
    """Резолвит путь относительно cwd."""
    p = Path(path_str)
    if not p.is_absolute():
        p = cwd / p
    return p.resolve()

def cmd_ls(args: list[str], show_hidden=False) -> str:
    global cwd
    target = resolve(args[0]) if args else cwd
    if not target.exists():
        return f"❌ Path not found: `{target}`"
    if target.is_file():
        return f"📄 {target.name}  ({_fmt(target.stat().st_size)})"

    entries = sorted(target.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
    lines = [f"📂 `{target}`\n"]
    for e in entries:
        if not show_hidden and e.name.startswith("."):
            continue
        if e.is_dir():
            lines.append(f"📁 {e.name}/")
        else:
            try:
                size = _fmt(e.stat().st_size)
            except Exception:
                size = "?"
            lines.append(f"📄 {e.name}  `{size}`")
    if len(lines) == 1:
        lines.append("_(empty)_")
    return "\n".join(lines)

def cmd_pwd() -> str:
    return f"`{cwd}`"

def cmd_cd(args: list[str]) -> str:
    global cwd
    if not args:
        cwd = Path.home()
        return f"➡️ `{cwd}`"
    target = resolve(args[0])
    if not target.exists():
        return f"❌ Directory not found: `{target}`"
    if not target.is_dir():
        return f"❌ Not a directory: `{target}`"
    cwd = target
    return f"➡️ `{cwd}`"

def cmd_mkdir(args: list[str]) -> str:
    if not args:
        return "❌ Usage: `mkdir <path>`"
    target = resolve(args[0])
    try:
        target.mkdir(parents=True, exist_ok=True)
        return f"✅ Created: `{target}`"
    except Exception as e:
        return f"❌ {e}"

def cmd_touch(args: list[str]) -> str:
    if not args:
        return "❌ Usage: `touch <file>`"
    target = resolve(args[0])
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.touch(exist_ok=True)
        return f"✅ Created: `{target}`"
    except Exception as e:
        return f"❌ {e}"

def cmd_rm(args: list[str]) -> str:
    if not args:
        return "❌ Usage: `rm <path>` or `rm -r <path>`"
    recursive = "-r" in args or "-rf" in args
    paths = [a for a in args if not a.startswith("-")]
    if not paths:
        return "❌ No path specified"
    results = []
    for p_str in paths:
        target = resolve(p_str)
        if not target.exists():
            results.append(f"❌ Not found: `{target}`")
            continue
        try:
            if target.is_dir():
                if recursive:
                    shutil.rmtree(target)
                    results.append(f"🗑 Removed dir: `{target}`")
                else:
                    results.append(f"❌ `{target}` is a directory, use `rm -r`")
            else:
                target.unlink()
                results.append(f"🗑 Removed: `{target}`")
        except Exception as e:
            results.append(f"❌ {e}")
    return "\n".join(results)

def cmd_mv(args: list[str]) -> str:
    if len(args) < 2:
        return "❌ Usage: `mv <src> <dst>`"
    src = resolve(args[0])
    dst = resolve(args[1])
    if not src.exists():
        return f"❌ Source not found: `{src}`"
    try:
        # если dst — существующая папка, кладём внутрь
        if dst.is_dir():
            shutil.move(str(src), str(dst / src.name))
        else:
            shutil.move(str(src), str(dst))
        return f"✅ Moved: `{src}` → `{dst}`"
    except Exception as e:
        return f"❌ {e}"

def cmd_cp(args: list[str]) -> str:
    if len(args) < 2:
        return "❌ Usage: `cp <src> <dst>`"
    src = resolve(args[0])
    dst = resolve(args[1])
    if not src.exists():
        return f"❌ Source not found: `{src}`"
    try:
        if src.is_dir():
            shutil.copytree(str(src), str(dst))
        else:
            if dst.is_dir():
                shutil.copy2(str(src), str(dst / src.name))
            else:
                shutil.copy2(str(src), str(dst))
        return f"✅ Copied: `{src}` → `{dst}`"
    except Exception as e:
        return f"❌ {e}"

def cmd_find(args: list[str]) -> str:
    if not args:
        return "❌ Usage: `find <pattern>` or `find <dir> <pattern>`"
    if len(args) == 1:
        search_dir = cwd
        pattern = args[0]
    else:
        search_dir = resolve(args[0])
        pattern = args[1]
    try:
        matches = list(search_dir.rglob(pattern))[:50]
        if not matches:
            return f"🔍 Nothing found for `{pattern}` in `{search_dir}`"
        lines = [f"🔍 Results for `{pattern}`:"]
        for m in matches:
            icon = "📁" if m.is_dir() else "📄"
            lines.append(f"{icon} {m}")
        if len(matches) == 50:
            lines.append("_(showing first 50)_")
        return "\n".join(lines)
    except Exception as e:
        return f"❌ {e}"

def cmd_rename(args: list[str]) -> str:
    if len(args) < 2:
        return "❌ Usage: `rename <old> <new>`"
    src = resolve(args[0])
    if not src.exists():
        return f"❌ Not found: `{src}`"
    dst = src.parent / args[1]
    try:
        src.rename(dst)
        return f"✅ Renamed: `{src.name}` → `{dst.name}`"
    except Exception as e:
        return f"❌ {e}"

def cmd_stat(args: list[str]) -> str:
    if not args:
        return "❌ Usage: `stat <path>`"
    target = resolve(args[0])
    if not target.exists():
        return f"❌ Not found: `{target}`"
    import datetime
    s = target.stat()
    lines = [
        f"📊 *{target.name}*",
        f"Path: `{target}`",
        f"Type: {'Directory' if target.is_dir() else 'File'}",
        f"Size: `{_fmt(s.st_size)}`",
        f"Modified: `{datetime.datetime.fromtimestamp(s.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}`",
        f"Created: `{datetime.datetime.fromtimestamp(s.st_ctime).strftime('%Y-%m-%d %H:%M:%S')}`",
    ]
    return "\n".join(lines)

# ─── SHELL ─────────────────────────────────────────────────────────────────────

def cmd_shell(args: list[str]) -> str:
    if not args:
        return "❌ Usage: `cmd <command>`"
    command = " ".join(args)
    try:
        res = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            cwd=str(cwd),
            timeout=30,
        )
        stdout = res.stdout.decode("utf-8", "ignore").strip()
        stderr = res.stderr.decode("utf-8", "ignore").strip()
        out = stdout or stderr or "(no output)"
        return f"```\n{out}\n```"
    except subprocess.TimeoutExpired:
        return "❌ Command timed out (30s)"
    except Exception as e:
        return f"❌ {e}"

# ─── PROCESSES ─────────────────────────────────────────────────────────────────

def cmd_ps() -> str:
    seen = set()
    lines = ["⚙️ *Running processes:*\n"]
    for proc in sorted(psutil.process_iter(["name", "pid", "cpu_percent", "memory_percent"]),
                       key=lambda p: p.info["name"] or ""):
        name = proc.info["name"] or "?"
        if name in seen:
            continue
        seen.add(name)
        lines.append(f"`{name}`")
    return "\n".join(lines)

def cmd_kill(args: list[str]) -> str:
    if not args:
        return "❌ Usage: `kill <name|pid>`"
    target = args[0]
    killed = []
    errors = []
    for proc in psutil.process_iter(["name", "pid"]):
        try:
            if proc.info["name"] == target or str(proc.info["pid"]) == target:
                proc.terminate()
                killed.append(f"{proc.info['name']} (pid={proc.info['pid']})")
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            errors.append(str(e))
    if killed:
        return "✅ Terminated:\n" + "\n".join(killed)
    if errors:
        return "❌ Errors:\n" + "\n".join(errors)
    return f"❌ Process not found: `{target}`"

# ─── HANDLERS ──────────────────────────────────────────────────────────────────

HELP_TEXT = """
*Available commands:*

*Navigation*
`cd <dir>` — change directory
`pwd` — print working directory
`dir [dir]` — list files
`dir -a [dir]` — list all (hidden too)

*Files*
`touch <file>` — create file
`mkdir <dir>` — create directory (recursive)
`rm <path>` — remove file
`rm -r <path>` — remove directory
`mv <src> <dst>` — move / rename
`cp <src> <dst>` — copy
`rename <old> <new>` — rename in same dir
`find [dir] <pattern>` — search files (glob)
`stat <path>` — file/dir info
`download <path>` — send file to chat
`upload` — reply with upload to save file

*System*
`sysinfo` — CPU / RAM / disk / battery
`ps` — list processes
`kill <name|pid>` — terminate process
`lock` — lock screen
`sleep` — sleep
`url <link>` — open URL
`cmd <command>` — run shell command
`clip` — paste clipboard
`screenshot` — take screenshot
""".strip()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        await deny(update, context)
        return
    await update.message.reply_text(
        "👋 Bot started. Choose a category:", reply_markup=MAIN_KEYBOARD
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        await deny(update, context)
        return

    text = update.message.text.strip()
    # нормализуем: убираем эмодзи-кнопки → команда
    text = _strip_emoji(text)

    parts = text.split()
    cmd = parts[0].lower() if parts else ""
    args = parts[1:]

    response: str | None = None

    # ── меню ───────────────────────────────────────────────────────────────────
    if cmd in ("files", "📁"):
        await update.message.reply_text(
            f"📁 File manager\nCurrent dir: `{cwd}`",
            parse_mode="Markdown",
            reply_markup=FILES_KEYBOARD,
        )
        return

    if cmd in ("processes", "⚙️"):
        response = cmd_ps()

    elif cmd in ("back", "⬅️"):
        await update.message.reply_text("Main menu:", reply_markup=MAIN_KEYBOARD)
        return

    # ── info ───────────────────────────────────────────────────────────────────
    elif cmd in ("screenshot", "📸"):
        path = await asyncio.get_event_loop().run_in_executor(None, take_screenshot)
        await update.message.reply_photo(photo=open(path, "rb"), caption="📸 Screenshot")
        return

    elif cmd in ("sysinfo", "💻"):
        response = get_sysinfo()

    elif cmd in ("clipboard", "clip", "📋"):
        response = pyperclip.paste() or "_(clipboard is empty)_"

    elif cmd in ("screen status", "⚠️", "status"):
        locked = any(p.name() == "LogonUI.exe" for p in psutil.process_iter())
        response = "🔒 Screen is Locked" if locked else "🔓 Screen is Unlocked"

    elif cmd in ("lock screen", "lock", "🔒"):
        try:
            ctypes.windll.user32.LockWorkStation()
            response = "🔒 Screen locked"
        except Exception as e:
            response = f"❌ {e}"

    elif cmd in ("sleep", "💤"):
        try:
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            response = "💤 Going to sleep..."
        except Exception as e:
            response = f"❌ {e}"

    elif cmd == "shutdown":
        response = "⚠️ Shutdown not allowed from bot for safety. Use `cmd shutdown /s /t 0` if you're sure."

    elif cmd == "restart":
        response = "⚠️ Restart not allowed from bot for safety. Use `cmd shutdown /r /t 0` if you're sure."

    elif cmd in ("help", "💡"):
        await update.message.reply_text(HELP_TEXT, parse_mode="Markdown")
        return

    # ── navigation ─────────────────────────────────────────────────────────────
    elif cmd == "cd":
        response = cmd_cd(args)

    elif cmd == "pwd" or cmd == "🗂":
        response = cmd_pwd()

    elif cmd in ("ls", "dir"):
        hidden = "-a" in args
        clean_args = [a for a in args if not a.startswith("-")]
        response = cmd_ls(clean_args, show_hidden=hidden)

    elif cmd in ("ls -a", "dir -a"):  # кнопка
        response = cmd_ls([], show_hidden=True)

    # ── files ──────────────────────────────────────────────────────────────────
    elif cmd == "mkdir" or cmd == "📁 mkdir":
        response = cmd_mkdir(args)

    elif cmd == "touch" or cmd == "📄 touch":
        response = cmd_touch(args)

    elif cmd == "rm" or cmd == "🗑 rm":
        response = cmd_rm(args)

    elif cmd == "mv" or cmd == "📦 mv":
        response = cmd_mv(args)

    elif cmd == "cp" or cmd == "📋 cp":
        response = cmd_cp(args)

    elif cmd == "rename":
        response = cmd_rename(args)

    elif cmd == "find" or cmd == "🔍 find":
        response = cmd_find(args)

    elif cmd == "stat":
        response = cmd_stat(args)

    elif cmd in ("download", "⬇️ download"):
        if not args:
            response = "❌ Usage: `download <path>`"
        else:
            target = resolve(args[0])
            if not target.exists():
                response = f"❌ Not found: `{target}`"
            elif target.is_dir():
                response = f"❌ `{target}` is a directory, zip it first"
            else:
                try:
                    await update.message.reply_document(
                        document=open(target, "rb"),
                        filename=target.name,
                        caption=f"📄 `{target.name}`",
                    )
                    return
                except Exception as e:
                    response = f"❌ {e}"

    # ── system ─────────────────────────────────────────────────────────────────
    elif cmd == "ps" or cmd == "⚙️ processes":
        response = cmd_ps()

    elif cmd == "kill":
        response = cmd_kill(args)

    elif cmd == "url":
        if not args:
            response = "❌ Usage: `url <link>`"
        else:
            try:
                webbrowser.open(args[0])
                response = f"🌐 Opened: {args[0]}"
            except Exception as e:
                response = f"❌ {e}"

    elif cmd == "cmd":
        response = cmd_shell(args)

    else:
        response = f"❓ Unknown command: `{cmd}`\nType `help` for the list of commands."

    if response:
        await _send_long(update, response)


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получаем файл от юзера и сохраняем в cwd."""
    if not is_allowed(update):
        await deny(update, context)
        return
    doc = update.message.document
    file = await context.bot.get_file(doc.file_id)
    dest = cwd / doc.file_name
    await file.download_to_drive(str(dest))
    await update.message.reply_text(f"✅ Saved: `{dest}`", parse_mode="Markdown")


# ─── HELPERS ───────────────────────────────────────────────────────────────────

def _strip_emoji(text: str) -> str:
    """Убирает emoji-префиксы из кнопок меню."""
    replacements = {
        "📸 screenshot": "screenshot",
        "📋 clipboard": "clipboard",
        "🔒 lock screen": "lock",
        "⚠️ screen status": "status",
        "💤 sleep": "sleep",
        "💻 sysinfo": "sysinfo",
        "📁 files": "files",
        "⚙️ processes": "ps",
        "💡 help": "help",
        "📂 dir -a": "dir -a",
        "📂 dir": "dir",
        "🗂 pwd": "pwd",
        "📁 mkdir": "mkdir",
        "📄 touch": "touch",
        "🗑 rm": "rm",
        "📦 mv": "mv",
        "📋 cp": "cp",
        "🔍 find": "find",
        "⬇️ download": "download",
        "⬅️ back": "back",
    }
    lower = text.lower()
    for k, v in replacements.items():
        if lower == k:
            return v
    return text


async def _send_long(update: Update, text: str, parse_mode="Markdown"):
    """Разбивает длинные сообщения на части по 4096 символов."""
    for i in range(0, len(text), 4096):
        chunk = text[i : i + 4096]
        try:
            await update.message.reply_text(chunk, parse_mode=parse_mode)
        except Exception:
            # fallback без разметки если Markdown невалиден
            await update.message.reply_text(chunk)


# ─── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print(f"[+] Bot started | authorized user_id={ALLOWED_USER_ID}")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
