# YT to TG Desktop

Desktop application for downloading YouTube videos and sending them directly to Telegram Saved Messages with formatted captions.

**Languages:** [English](README.md) | [Русский](README-RU.md)

---

## Features

- **YouTube Video Download** — Download videos up to 1080p (H264/MP4)
- **Auto Caption Generation** — Two formats: with description or without
- **Tag System** — Single tag selection: `#gp`, `#deco`, `#gp_deco`, `#preview`
- **Telegram Integration** — Send to Saved Messages with full metadata (duration, resolution, thumbnail)
- **Cookies Support** — Optional YouTube cookies for age-restricted content
- **Deno Runtime** — Enhanced YouTube signature solving via Deno JS runtime
- **Auto Cleanup** — Local files deleted after successful send

---

## Requirements

- Windows 10/11
- Python 3.10+ (for running from source)
- Telegram API credentials ([my.telegram.org](https://my.telegram.org))

---

## Installation

### Option 1: Download Pre-built Executable

1. Download `YT_TG_Desktop.zip` from [Releases](../../releases)
2. Extract to any folder
3. Run `YT_TG_Desktop.exe`

### Option 2: Run from Source

```bash
# Clone repository
git clone https://github.com/Skiro1/yt-tg-desktop.git
cd yt-tg-desktop

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt

# Run
python main.py
```

---

## First Time Setup

### 1. Telegram API Credentials

1. Go to [my.telegram.org](https://my.telegram.org)
2. Log in with your phone number
3. Go to **API Development Tools**
4. Create a new application
5. Copy **api_id** and **api_hash**

### 2. Configure Application

1. Open the app
2. Click **File → Settings**
3. Enter your **API ID** and **API HASH**
4. (Optional) Select **cookies.txt** for YouTube
5. Click **Save**

### 3. Connect to Telegram

1. Click **Connect** button
2. In the console window, enter your phone number
3. Enter the confirmation code from Telegram
4. Done! Status changes to **[ONLINE] Connected**

---

## Usage

1. **Paste YouTube URL** into the URL field
2. Click **Get Info** — app fetches video metadata
3. **Select Caption Format**:
   - `With description` — includes expandable description block
   - `Without description` — title + channel + hashtag only
4. **Select Tag** (optional) — check one tag checkbox
5. **Edit Caption** if needed in the text area
6. Click **Download** — wait for progress bar
7. Click **Send to Telegram** — video appears in Saved Messages

---

## YouTube Cookies (Optional)

For downloading age-restricted or region-locked videos:

1. Install browser extension **"Get cookies.txt"**
2. Go to [youtube.com](https://youtube.com) and log in
3. Click extension → **Export** → save as `cookies.txt`
4. In app: **File → Settings → Browse...** → select `cookies.txt`

---

## Project Structure

```
yt-tg-desktop/
├── main.py                 # PyQt6 GUI application
├── telegram_client.py      # Pyrogram user client wrapper
├── youtube_downloader.py   # yt-dlp download logic
├── caption_formatter.py    # Caption generation from bot logic
├── settings_manager.py     # JSON settings storage
├── settings_dialog.py      # Settings UI dialog
├── deno_runtime.py         # Deno JS runtime detection
├── config_loader.py        # Configuration loader
├── requirements.txt        # Python dependencies
├── start.bat              # Launch script (source)
└── build.bat              # Build script for .exe
```

---

## Building from Source

```bash
# Install pyinstaller
pip install pyinstaller

# Build executable
build.bat
```

Output: `dist\YT_TG_Desktop\YT_TG_Desktop.exe`

---

## Dependencies

| Package | Purpose |
|---------|---------|
| PyQt6 | Desktop GUI |
| pyrogram | Telegram user client |
| yt-dlp | YouTube video downloading |
| Pillow | Thumbnail processing |
| aiohttp | Async HTTP requests |
| tgcrypto | Fast Telegram encryption |

---

## Technical Details

### Caption Format

Captions follow the same format as RKGDTUBE bot:

```html
<b>{title}</b> — <b>{uploader}</b> [<b><a href='{url}'>ORIGINAL</a></b>]

<blockquote expandable><i>'{description}...'</i></blockquote>
<b>#{hashtag}</b> <b>ㅤ</b>

<b><a href='https://t.me/RCGDTUBE'>РКГДTUBE</a></b>
```

### Video Download Settings

- **Format**: `bestvideo[height<=1080]+bestaudio/best[height<=1080]/best`
- **Codec**: H264 (preferred)
- **Container**: MP4
- **Max Size**: 1.95 GB
- **Thumbnail**: 320x320 JPEG

### Security

- API credentials stored locally in `settings.json`
- Telegram session stored in `yt_tg_session.session`
- No data sent to third-party servers

---

## License

MIT License

---

## Author

**Skiro1** — [GitHub](https://github.com/Skiro1)
