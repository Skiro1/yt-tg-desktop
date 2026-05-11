# YT to TG Desktop

Десктопное приложение для скачивания видео с YouTube и отправки их прямо в Избранное (Saved Messages) Telegram с отформатированными подписями (caption).

**Языки:** [English](README.md) | [Русский](README-RU.md)

---

## Возможности

- **Скачивание с YouTube** — Видео до 1080p (H264/MP4)
- **Авто-генерация Caption** — Два формата: с описанием и без
- **Система тегов** — Только один тег за раз: `#gp`, `#deco`, `#gp_deco`, `#preview`
- **Интеграция с Telegram** — Отправка в Избранное с полными метаданными (длительность, разрешение, превью)
- **Поддержка Cookies** — Опциональные YouTube-cookies для обхода возрастных ограничений
- **Deno Runtime** — Улучшенное решение подписей YouTube через Deno JS runtime
- **Автоочистка** — Локальные файлы удаляются после успешной отправки

---

## Требования

- Windows 10/11
- Python 3.10+ (для запуска из исходников)
- Telegram API credentials ([my.telegram.org](https://my.telegram.org))

---

## Установка

### Вариант 1: Скачать готовый .exe

1. Скачать `YT_TG_Desktop.zip` из [Releases](../../releases)
2. Распаковать в любую папку
3. Запустить `YT_TG_Desktop.exe`

### Вариант 2: Запуск из исходников

```bash
# Клонировать репозиторий
git clone https://github.com/Skiro1/yt-tg-desktop.git
cd yt-tg-desktop

# Создать виртуальное окружение
python -m venv .venv
.venv\Scripts\activate.bat

# Установить зависимости
pip install -r requirements.txt

# Запустить
python main.py
```

---

## Первоначальная настройка

### 1. Telegram API Credentials

1. Перейти на [my.telegram.org](https://my.telegram.org)
2. Войти по номеру телефона
3. Перейти в **API Development Tools**
4. Создать новое приложение
5. Скопировать **api_id** и **api_hash**

### 2. Настройка приложения

1. Открыть приложение
2. Нажать **Файл → Настройки**
3. Ввести **API ID** и **API HASH**
4. (Опционально) Выбрать **cookies.txt** для YouTube
5. Нажать **Сохранить**

### 3. Подключение к Telegram

1. Нажать кнопку **Connect**
2. В консольном окне ввести номер телефона
3. Ввести код подтверждения из Telegram
4. Готово! Статус изменится на **[ONLINE] Connected**

---

## Использование

1. **Вставить ссылку YouTube** в поле URL
2. Нажать **Get Info** — приложение получит метаданные видео
3. **Выбрать формат Caption**:
   - `With description` — с раскрываемым блоком описания
   - `Without description` — только название, канал, хештег
4. **Выбрать тег** (опционально) — отметить один чекбокс
5. **Отредактировать Caption** при необходимости в текстовом поле
6. Нажать **Download** — дождаться заполнения прогресс-бара
7. Нажать **Send to Telegram** — видео появится в Избранном

---

## YouTube Cookies (Опционально)

Для скачивания видео с возрастными ограничениями или региональной блокировкой:

1. Установить расширение браузера **"Get cookies.txt"**
2. Зайти на [youtube.com](https://youtube.com) и авторизоваться
3. Нажать на расширение → **Export** → сохранить как `cookies.txt`
4. В приложении: **Файл → Настройки → Browse...** → выбрать `cookies.txt`

---

## Структура проекта

```
yt-tg-desktop/
├── main.py                 # PyQt6 GUI приложение
├── telegram_client.py      # Pyrogram user client
├── youtube_downloader.py   # Логика скачивания через yt-dlp
├── caption_formatter.py    # Генерация caption (как в боте)
├── settings_manager.py     # Хранение настроек в JSON
├── settings_dialog.py      # Окно настроек
├── deno_runtime.py         # Поиск Deno JS runtime
├── config_loader.py        # Загрузчик конфигурации
├── requirements.txt        # Python зависимости
├── start.bat              # Скрипт запуска (из исходников)
└── build.bat              # Скрипт сборки .exe
```

---

## Сборка из исходников

```bash
# Установить pyinstaller
pip install pyinstaller

# Собрать .exe
build.bat
```

Результат: `dist\YT_TG_Desktop.exe`

---

## Зависимости

| Пакет | Назначение |
|---------|---------|
| PyQt6 | Desktop GUI |
| pyrogram | Telegram user client |
| yt-dlp | Скачивание с YouTube |
| Pillow | Обработка превью |
| aiohttp | Асинхронные HTTP запросы |
| tgcrypto | Быстрое шифрование Telegram |

---

## Технические детали

### Формат Caption

Caption следует тому же формату, что и бот РКГДTUBE:

```html
<b>{title}</b> — <b>{uploader}</b> [<b><a href='{url}'>ORIGINAL</a></b>]

<blockquote expandable><i>'{description}...'</i></blockquote>
<b>#{hashtag}</b> <b>ㅤ</b>

<b><a href='https://t.me/RCGDTUBE'>РКГДTUBE</a></b>
```

### Настройки скачивания видео

- **Формат**: `best[height<=1080][ext=mp4]/bestvideo[height<=1080]+bestaudio/best[height<=1080]/best`
- **Кодек**: H264 (предпочтительно)
- **Контейнер**: MP4
- **Макс. размер**: 1.95 GB
- **Превью**: 320x320 JPEG

### Безопасность

- API credentials хранятся локально в `settings.json`
- Сессия Telegram хранится в `yt_tg_session.session`
- Данные не отправляются на сторонние серверы

---

## Лицензия

MIT License

---

## Автор

**Skiro1** — [GitHub](https://github.com/Skiro1)
