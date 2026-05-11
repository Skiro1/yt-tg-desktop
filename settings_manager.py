import json
import os
import sys


def get_app_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def get_runtime_path(filename):
    return os.path.join(get_app_dir(), filename)


def get_settings_path():
    return get_runtime_path("settings.json")


def get_downloads_dir():
    path = get_runtime_path("downloads")
    os.makedirs(path, exist_ok=True)
    return path


SETTINGS_FILE = get_settings_path()


def load_settings():
    """Загружает настройки из JSON файла."""
    settings_file = get_settings_path()
    if os.path.exists(settings_file):
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_settings(settings):
    """Сохраняет настройки в JSON файл."""
    with open(get_settings_path(), 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)


def get_api_credentials():
    """Возвращает API_ID и API_HASH из настроек."""
    settings = load_settings()
    return {
        'api_id': settings.get('api_id', ''),
        'api_hash': settings.get('api_hash', ''),
    }


def set_api_credentials(api_id, api_hash):
    """Сохраняет API_ID и API_HASH в настройки."""
    settings = load_settings()
    settings['api_id'] = api_id
    settings['api_hash'] = api_hash
    save_settings(settings)


def get_cookies_path():
    """Возвращает путь к cookies.txt из настроек."""
    settings = load_settings()
    return settings.get('cookies_path', '')


def set_cookies_path(path):
    """Сохраняет путь к cookies.txt в настройки."""
    settings = load_settings()
    if path and os.path.exists(path):
        settings['cookies_path'] = path
    else:
        settings.pop('cookies_path', None)
    save_settings(settings)
