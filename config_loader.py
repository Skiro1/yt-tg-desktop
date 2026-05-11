from settings_manager import get_api_credentials


def get_config():
    """Возвращает конфигурацию API для Telegram из настроек."""
    creds = get_api_credentials()
    
    api_id = creds.get('api_id')
    api_hash = creds.get('api_hash')
    
    if not api_id or not api_hash:
        raise ValueError(
            "API_ID и API_HASH не настроены. "
            "Откройте Настройки и введите свои данные с my.telegram.org"
        )
    
    return {
        'api_id': int(api_id),
        'api_hash': api_hash,
    }
