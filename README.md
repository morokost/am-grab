# 🍎 applemusic-dl

**applemusic-dl** — это библиотека Python и CLI-утилита для загрузки музыки из **Apple Music** с полным набором метаданных, обложками Ultra-HD и мульти-источниками поиска.

По умолчанию работает на **чистом Python без внешних зависимостей (Zero FFmpeg)**, сохраняя оригинальный нативный поток Apple/AAC в формате `.m4a`.

---

## ✨ Возможности

- 🚀 **Zero-Dependency (без FFmpeg по умолчанию)**:
  - Прямое скачивание оригинального AAC-потока в нативный контейнер **`.m4a`** (официальный формат Apple Music и iTunes).
  - Никакой потери качества от двойного пережатия (AAC → MP3).
  - Скачивание за **3–4 секунды** без нагрузки на процессор.
  - Работает «из коробки» на любой ОС, в Docker, на серверах и в облаке (PythonAnywhere, Heroku, VPS) без установки системных пакетов.
- 🎵 **Скачивание отдельных треков и целых альбомов**:
  - Поддерживает ссылки на песни (`/song/...`), треки внутри альбомов (`?i=...`) и целые альбомы (`/album/...`).
  - При скачивании альбома треки автоматически нумеруются по порядку.
- 📡 **Мульти-источники поиска (Multi-Provider Architecture)**:
  - 🎹 **YouTube Music** (`ytmusic`): **основной приоритет** — поиск официальных студийных релизов (Topic-каналы) без диалогов, заставок и шумов из клипов.
  - 📺 **YouTube** (`youtube`): глобальный каталог видеоклипов и фанатских загрузок.
  - ☁️ **SoundCloud** (`soundcloud`): идеальный источник для инди-музыки, ремиксов, EDM и треков, недоступных на YouTube из-за геоблокировок.
  - 🔌 **Кастомные провайдеры**: лёгкое подключение собственных источников (VK, Яндекс Музыка, локальный медиасервер).
- 🧠 **Умная система скоринга (Scoring Engine)**:
  - Ранжирует кандидатов по точности хронометража (до 1–2 секунд).
  - Штрафует и отсекает `live`, `cover`, `slowed`, `remix`, если в оригинальном треке их нет.
- 🖼️ **Обложки Ultra-HD**:
  - Автоматическая замена разрешения на 1400×1400 px и внедрение в тег обложки.
- 🏷️ **Полный набор тегов (iTunes Atoms & ID3v2.4)**:
  - В `.m4a`: нативные атомы Apple (`©nam`, `©ART`, `©alb`, `trkn`, `disk`, `©day`, `©gen`, `covr`). 100% совместимость с iOS, macOS, Windows Media Player, Android, Telegram.
  - В `.mp3`: теги ID3v2.4 (`TIT2`, `TPE1`, `TALB`, `TRCK`, `TPOS`, `TDRC`, `TCON`, `APIC`).
- 🌍 **Поддержка регионов**:
  - Автоматическое определение страны каталога (RU, US, KZ, GB, DE и др.) и разворачивание мобильных коротких ссылок `apple.co`.
- 🎛️ **Опциональный MP3-режим**:
  - Если вам строго необходим `.mp3`, библиотека умеет конвертировать через FFmpeg (с автодетектом путей WinGet / Chocolatey / Scoop), а при его отсутствии безопасно сохранит файл в `.m4a` без ошибок.

---

## 🚀 Установка

```bash
git clone https://github.com/example/applemusic-dl.git
cd applemusic-dl
pip install -e .
```

> **Примечание:** Для работы по умолчанию (в нативном формате `.m4a`) **FFmpeg устанавливать НЕ нужно**.
> Он требуется только в случае, если вы явно укажете принудительную конвертацию в `.mp3` (`-f mp3`).

---

## 💻 Использование через CLI (`apple-dl`)

После установки в системе доступна команда `apple-dl`:

```bash
# 1. Скачать трек в оригинальном качестве без FFmpeg (.m4a)
apple-dl "https://music.apple.com/us/album/blinding-lights/1499378108?i=1499378607"

# 2. Скачать целый альбом в папку Music с раскладкой "Исполнитель / Альбом / 01 - Название.m4a"
apple-dl -o ./Music --organize "https://music.apple.com/us/album/after-hours/1499378108"

# 3. Принудительно конвертировать в MP3 320 kbps (если установлен FFmpeg)
apple-dl -f mp3 -q 320 "https://music.apple.com/us/album/blinding-lights/1499378108?i=1499378607"

# 4. Настроить источники поиска (например, искать сначала в YouTube Music, затем в SoundCloud)
apple-dl -p ytmusic,soundcloud "https://music.apple.com/us/album/after-hours/1499378108"

# 5. Только посмотреть метаданные и треклист без скачивания
apple-dl --info-only "https://music.apple.com/us/album/after-hours/1499378108"
```

### Параметры командной строки:
| Флаг | Описание | По умолчанию |
|---|---|---|
| `url` | Ссылка на трек или альбом Apple Music | *(обязательный)* |
| `-f`, `--format` | Аудиоформат: `m4a` (нативный без FFmpeg) или `mp3` | `m4a` |
| `-o`, `--output-dir` | Папка для сохранения музыки | `./downloads` |
| `-p`, `--providers` | Список источников через запятую (`ytmusic`, `youtube`, `soundcloud`) | `ytmusic,youtube,soundcloud` |
| `-q`, `--quality` | Битрейт при конвертации в MP3 (`128`, `192`, `256`, `320`) | `320` |
| `--organize` | Создавать дерево папок `Исполнитель / Альбом / 01 - Трек.<ext>` | `False` |
| `--overwrite` | Перезаписывать уже существующие файлы | `False` |
| `--info-only` | Показать метаданные и список треков без загрузки | `False` |
| `--tolerance` | Допустимое расхождение длительности между Apple Music и аудио (сек) | `8` |

---

## 🐍 Использование в Python

### 1. Простое скачивание трека (без FFmpeg)
```python
from applemusic_dl import AppleMusicDownloader

# По умолчанию preferred_codec="m4a" — без внешних зависимостей
downloader = AppleMusicDownloader(output_dir="./music")

result = downloader.download("https://music.apple.com/us/album/blinding-lights/1499378108?i=1499378607")
if result.success:
    print(f"✅ Трек сохранён: {result.file_path}")
    print(f"🎵 {result.track.artist} — {result.track.title} ({result.track.duration_sec} сек)")
```

### 2. Скачивание целого альбома с отслеживанием прогресса
```python
from applemusic_dl import AppleMusicDownloader

downloader = AppleMusicDownloader(
    output_dir="./albums",
    organize_by_album=True,  # Создаст папки: Артист / Альбом / 01 - Трек.m4a
)

def on_start(track, idx, total):
    print(f"[{idx}/{total}] ⬇️ Скачиваем: {track.title}...")

def on_done(res, idx, total):
    if res.success:
        print(f"[{idx}/{total}] ✅ Готово: {res.file_path}")
    else:
        print(f"[{idx}/{total}] ❌ Ошибка: {res.error}")

results = downloader.download_album(
    "https://music.apple.com/us/album/after-hours/1499378108",
    on_track_start=on_start,
    on_track_complete=on_done,
)
```

### 3. Только получение метаданных и треклиста
```python
from applemusic_dl import AppleMusicClient

client = AppleMusicClient()

# Информация о треке
track = client.get_track_metadata("https://music.apple.com/us/album/blinding-lights/1499378108?i=1499378607")
print(f"Трек: {track.artist} - {track.title}, Обложка: {track.artwork_url}")

# Информация об альбоме и треклист
album = client.get_album_metadata("https://music.apple.com/us/album/after-hours/1499378108")
print(f"Альбом: {album.title}, треков: {len(album.tracks)}")
for t in album.tracks:
    print(f" {t.track_number:02d}. {t.title}")
```

### 4. Подключение собственного источника поиска
```python
from applemusic_dl import AppleMusicDownloader, BaseAudioProvider, AudioCandidate

class CustomStorageProvider(BaseAudioProvider):
    name = "custom"
    display_name = "My Private Storage"

    def search(self, meta, limit=5):
        # Ваша логика поиска (VK, Яндекс, личный сервер, локальный диск)
        return [
            AudioCandidate(
                provider_name=self.name,
                url="https://my-storage.example.com/audio/song.m4a",
                title=meta.title,
                duration=meta.duration_sec,
            )
        ]

downloader = AppleMusicDownloader(providers=["custom", "ytmusic"])
downloader.searcher.registry.register(CustomStorageProvider)
```

---

## 🌐 Пример веб-сервера на Flask

Пример готового легковесного веб-интерфейса находится в [examples/web_server.py](file:///d:/gfdgf/examples/web_server.py) или [test.py](file:///d:/gfdgf/test.py):

```python
import os, tempfile
from flask import Flask, request, send_file, render_template_string, after_this_request
from applemusic_dl import AppleMusicDownloader, AppleMusicError

app = Flask(__name__)
downloader = AppleMusicDownloader(output_dir=os.path.join(tempfile.gettempdir(), "apple_web"))

@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url", "").strip()
    try:
        res = downloader.download_track(url)
        if not res.success:
            return f"Ошибка: {res.error}", 400

        @after_this_request
        def cleanup(response):
            if res.file_path and os.path.exists(res.file_path):
                os.remove(res.file_path)
            return response

        return send_file(
            res.file_path,
            as_attachment=True,
            download_name=os.path.basename(res.file_path)
        )
    except AppleMusicError as e:
        return f"Ошибка: {str(e)}", 400

if __name__ == "__main__":
    app.run(debug=True, port=5000)
```

---

## 📁 Структура проекта

```text
applemusic-dl/
├── applemusic_dl/
│   ├── __init__.py          # Публичный интерфейс пакета
│   ├── models.py            # Датаклассы TrackMetadata, AlbumMetadata, DownloadResult
│   ├── apple.py             # Парсинг ссылок (apple.co, страны) + iTunes Lookup API
│   ├── searcher.py          # Поиск по провайдерам и скачивание аудио (M4A/MP3)
│   ├── tagger.py            # Внедрение тегов: iTunes MP4 Atoms (M4A) и ID3v2.4 (MP3)
│   ├── downloader.py        # Главный класс-оркестратор AppleMusicDownloader
│   ├── exceptions.py        # Иерархия типизированных исключений
│   ├── cli.py               # Консольный интерфейс apple-dl
│   └── providers/           # Модульные источники поиска
│       ├── base.py          # Базовый класс BaseAudioProvider и скоринг кандидатов
│       ├── youtube_music.py # Провайдер YouTube Music (Topic студийные релизы)
│       ├── youtube.py       # Провайдер стандартного YouTube
│       ├── soundcloud.py    # Провайдер SoundCloud
│       └── registry.py      # Диспетчер провайдеров и скоринга
├── examples/
│   ├── basic_download.py    # Пример скачивания одного трека
│   ├── download_album.py    # Пример загрузки альбома с прогрессом
│   └── web_server.py        # Пример веб-сервера на Flask
├── tests/
│   ├── test_apple.py        # Unit-тесты парсера и iTunes API
│   └── test_providers.py    # Unit-тесты провайдеров и скоринга
├── pyproject.toml           # Стандарт сборки пакета (PEP 517/518)
├── requirements.txt         # Зависимости
├── .gitignore
└── README.md                # Полная документация проекта
```

---

## 📄 Лицензия
MIT License.
