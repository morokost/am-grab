"""
Пример скачивания целого альбома из Apple Music с отслеживанием прогресса.

Разработчик : @morokost
Дата        : 2026-11-17
"""
from applemusic_dl import AppleMusicDownloader

def main():
    downloader = AppleMusicDownloader(
        output_dir="./my_albums",
        organize_by_album=True,
    )

    album_url = "https://music.apple.com/us/album/after-hours/1499378108"

    album_info = downloader.get_album_info(album_url)
    print(f"📀 Альбом: {album_info.artist} — {album_info.title}")
    print(f"Всего треков: {len(album_info.tracks)}\n")

    def on_start(track, idx, total):
        print(f"[{idx}/{total}] ⬇️ Скачиваем: {track.title}...")

    def on_done(res, idx, total):
        if res.success:
            print(f"[{idx}/{total}] ✅ Сохранено: {res.file_path}")
        else:
            print(f"[{idx}/{total}] ❌ Ошибка: {res.error}")

    results = downloader.download_album(
        album_url,
        on_track_start=on_start,
        on_track_complete=on_done,
    )

    downloaded = sum(1 for r in results if r.success)
    print(f"\n🎉 Завершено! Скачано {downloaded} из {len(results)} треков.")

if __name__ == "__main__":
    main()
