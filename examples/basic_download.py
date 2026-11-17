"""
Пример базового использования applemusic_dl: скачивание одного трека в M4A.

Разработчик : @morokost
Дата        : 2026-11-17
"""
from applemusic_dl import AppleMusicDownloader

def main():
    downloader = AppleMusicDownloader(
        output_dir="./my_music",
        preferred_codec="m4a",
        organize_by_album=True,
    )

    track_url = "https://music.apple.com/us/album/blinding-lights/1499378108?i=1499378607"

    print("1. Получение информации о треке...")
    info = downloader.get_track_info(track_url)
    print(f"🎵 Трек: {info.artist} — {info.title}")
    print(f"📀 Альбом: {info.album}")
    print(f"⏱️ Длительность: {info.duration_sec} сек")
    print(f"🖼️ Обложка: {info.artwork_url}")

    print("\n2. Скачивание и тегирование...")
    result = downloader.download(track_url)

    if result.success:
        print(f"✅ Файл сохранён: {result.file_path}")
    else:
        print(f"❌ Ошибка: {result.error}")

if __name__ == "__main__":
    main()
