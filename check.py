import sys
import os

# Test 1: compile all
import py_compile
for f in ['main.py', 'caption_formatter.py', 'telegram_client.py', 'youtube_downloader.py', 'settings_manager.py', 'settings_dialog.py', 'config_loader.py', 'deno_runtime.py']:
    py_compile.compile(f, doraise=True)
print('COMPILE OK')

# Test 2: import main
from main import MainWindow
print('IMPORT OK')

# Test 3: caption escaping
from caption_formatter import format_caption_with_description
c = format_caption_with_description('A < B & C', 'U < X', 'https://x.test/?a=1&b=2', 'desc <tag> & text')
assert '&lt;' in c, 'HTML not escaped in caption'
print('CAPTION OK')

# Test 4: download path
from youtube_downloader import get_download_path
p = get_download_path('test')
assert os.path.isabs(p), 'Download path not absolute'
print('DL PATH', p)

# Test 5: runtime path
from settings_manager import get_runtime_path
rp = get_runtime_path('settings.json')
assert os.path.isabs(rp), 'Runtime path not absolute'
print('RUNTIME PATH', rp)

# Test 6: session path
from telegram_client import TelegramClient
c = TelegramClient(1, 'x')
assert os.path.isabs(c.session_name), 'Session path not absolute'
print('SESSION PATH', c.session_name)

print('ALL CHECKS PASSED')
