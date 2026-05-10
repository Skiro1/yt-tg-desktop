import json
import os


SETTINGS_FILE = "settings.json"


def load_settings():
    """Загружает настройки из JSON файла."""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_settings(settings):
    """Сохраняет настройки в JSON файл."""
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
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
