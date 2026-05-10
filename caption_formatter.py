import re


def clean_tag_underscores(tag: str) -> str:
    """
    Очищает тег от лишних подчеркиваний:
    1. Удаляет все '_' в начале и конце.
    2. Заменяет двойные и более '_' на одно '_'.
    """
    if not tag:
        return tag

    # Сохраняем # если он есть в начале
    has_hash = tag.startswith('#')
    working_tag = tag[1:] if has_hash else tag

    # 1. Удаляем '_' в начале и конце
    working_tag = working_tag.strip('_')

    # 2. Заменяем кратные '_' на одно '_'
    working_tag = re.sub(r'_{2,}', '_', working_tag)

    return f"#{working_tag}" if has_hash else working_tag


def create_hashtag(channel_name):
    """Создает хештег из имени канала/загрузчика."""
    if channel_name is None:
        return "#Unknown_Uploader"

    invalid_chars = ['#', '@', '!', '$', '%', '^', '&', '*', '(', ')', '-', '=', '+', '{', '}', ';', ':', '"', ',', '.',
                     '<', '>', '/', '?', '\\', '|', '[', ']']
    cleaned_name = channel_name.replace(' ', '_')
    for char in invalid_chars:
        cleaned_name = cleaned_name.replace(char, '')

    # Применяем фильтрацию подчеркиваний
    cleaned_name = clean_tag_underscores(cleaned_name)

    # Если clean_tag_underscores вернул с #, убираем его, так как в конце добавим сами
    if cleaned_name.startswith('#'):
        cleaned_name = cleaned_name[1:]

    return f"#{cleaned_name}"


def format_caption_with_description(title: str, uploader: str, url: str, description: str) -> str:
    """Формирует caption с описанием (как в боте)."""
    hashtag = create_hashtag(uploader)
    if description:
        description = description[:850]
    else:
        description = ""

    if not description:
        # Если описание пустое, используем формат без описания
        return format_caption_without_description(title, uploader, url)

    caption = (
        f"<b>{title}</b> — <b>{uploader}</b> [<b><a href='{url}'>ORIGINAL</a></b>]\n\n"
        f"<blockquote expandable><i>'{description}...'</i></blockquote>\n"
        f"<b>{hashtag}</b> <b>ㅤ</b>\n\n"
        f"<b><a href='https://t.me/RCGDTUBE'>РКГДTUBE</a></b>"
    )
    return caption


def format_caption_without_description(title: str, uploader: str, url: str) -> str:
    """Формирует caption без описания (как в боте)."""
    hashtag = create_hashtag(uploader)

    caption = (
        f"<b>{title}</b> — <b>{uploader}</b> [<b><a href='{url}'><b>ORIGINAL</b></a></b>]\n\n"
        f"<b>{hashtag}</b> <b>ㅤ</b>\n\n"
        f"<b><a href='https://t.me/RCGDTUBE'>РКГДTUBE</a></b>"
    )
    return caption


def add_tag_to_caption(caption: str, tag: str) -> str:
    """
    Добавляет тег в caption перед символом ㅤ.
    Логика из update_caption_with_formatting бота.
    """
    tag_text = f"#{tag} "

    if "ㅤ" in caption:
        parts = caption.rsplit("ㅤ", 1)
        updated_caption = f"{parts[0].strip()}<br>{tag_text}<br>ㅤ{parts[-1].strip()}"
    else:
        updated_caption = f"{caption}<br>{tag_text}<br>ㅤ"

    return updated_caption


def remove_all_tags(caption: str) -> str:
    """Удаляет все теги (#gp, #deco и т.д.), оставляя базовый caption."""
    # Удаляем все теги между частями caption
    # Простой способ: убираем все <br>#... <br> перед ㅤ
    import re
    # Убираем теги формата <br>#tag <br>ㅤ
    caption = re.sub(r'<br>#[^<]+<br>ㅤ', ' <b>ㅤ</b>', caption)
    # Убираем возможные оставшиеся пустые строки
    caption = re.sub(r'\n{3,}', '\n\n', caption)
    return caption
