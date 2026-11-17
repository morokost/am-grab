"""
Консольный интерфейс apple-dl.
Разработчик: @morokost
Дата: 2026-11-17
"""

import argparse
import sys

from .downloader import AppleMusicDownloader
from .exceptions import AppleMusicError
from .models import DownloadResult, TrackMetadata


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="apple-dl",
        description="Загрузчик треков и альбомов из Apple Music.",
    )
    parser.add_argument("url", help="Ссылка на трек или альбом Apple Music")
    parser.add_argument(
        "-o", "--output-dir",
        default="./downloads",
        metavar="DIR",
        help="Папка для сохранения (по умолчанию: ./downloads)",
    )
    parser.add_argument(
        "-f", "--format",
        default="m4a",
        choices=["m4a", "mp3"],
        help="Формат: m4a (без FFmpeg) или mp3 (по умолчанию: m4a)",
    )
    parser.add_argument(
        "-p", "--providers",
        default="ytmusic,youtube,soundcloud",
        metavar="LIST",
        help="Источники поиска через запятую (по умолчанию: ytmusic,youtube,soundcloud)",
    )
    parser.add_argument(
        "-q", "--quality",
        default="320",
        choices=["128", "192", "256", "320"],
        help="Битрейт MP3 в kbps (по умолчанию: 320)",
    )
    parser.add_argument(
        "--organize",
        action="store_true",
        help="Создавать дерево: Исполнитель / Альбом / Номер - Название",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Перезаписывать существующие файлы",
    )
    parser.add_argument(
        "--info-only",
        action="store_true",
        help="Показать метаданные без скачивания",
    )
    parser.add_argument(
        "--tolerance",
        type=int,
        default=8,
        metavar="SEC",
        help="Допустимое расхождение длительности в секундах (по умолчанию: 8)",
    )
    return parser


def _print_info(downloader: AppleMusicDownloader, url: str, res_type: str) -> None:
    if res_type == "album":
        album = downloader.get_album_info(url)
        print(f"📀  {album.artist} — {album.title}")
        print(f"    Жанр: {album.genre or '—'} | Треков: {album.track_count}")
        print(f"    Релиз: {album.release_date[:10] if album.release_date else '—'}")
        print("\nТреклист:")
        for t in album.tracks:
            m, s = divmod(int(t.duration_sec), 60)
            print(f"  {t.track_number or '?':>2}. {t.title}  ({m}:{s:02d})")
    else:
        t = downloader.get_track_info(url)
        m, s = divmod(int(t.duration_sec), 60)
        print(f"🎵  {t.artist} — {t.title}")
        print(f"    Альбом: {t.album}")
        print(f"    Длительность: {m}:{s:02d}")
        print(f"    Жанр: {t.genre or '—'}")
        if t.artwork_url:
            print(f"    Обложка: {t.artwork_url}")


def main() -> None:
    args = _build_parser().parse_args()
    providers = [p.strip() for p in args.providers.split(",") if p.strip()]

    downloader = AppleMusicDownloader(
        output_dir=args.output_dir,
        providers=providers,
        preferred_codec=args.format,
        preferred_quality=args.quality,
        organize_by_album=args.organize,
        tolerance_sec=args.tolerance,
        overwrite=args.overwrite,
    )

    try:
        res_type, _, _ = downloader.apple_client.parse_url(args.url)

        if args.info_only:
            _print_info(downloader, args.url, res_type)
            return

        print("🔍  Получение метаданных из Apple Music…")

        if res_type == "album":
            album = downloader.get_album_info(args.url)
            print(f"📀  {album.artist} — {album.title}  ({len(album.tracks)} треков)")
            print(f"📡  Источники: {', '.join(providers)} | Формат: {args.format.upper()}")

            def on_start(track: TrackMetadata, idx: int, total: int) -> None:
                print(f"\n[{idx}/{total}] ⬇  {track.artist} — {track.title}")

            def on_done(res: DownloadResult, idx: int, total: int) -> None:
                if res.success:
                    print(f"[{idx}/{total}] ✅  {res.file_path}")
                else:
                    print(f"[{idx}/{total}] ❌  {res.error}")

            results = downloader.download_album(args.url, on_track_start=on_start, on_track_complete=on_done)
            ok = sum(1 for r in results if r.success)
            print(f"\n🎉  Альбом завершён: {ok}/{len(results)} треков.")

        else:
            track = downloader.get_track_info(args.url)
            print(f"🎵  {track.artist} — {track.title}")
            print(f"📡  Источники: {', '.join(providers)} | Формат: {args.format.upper()}")
            print("⬇   Загрузка и тегирование…")
            res = downloader.download_track(args.url)
            if res.success:
                print(f"✅  Сохранено: {res.file_path}")
            else:
                print(f"❌  Ошибка: {res.error}", file=sys.stderr)
                sys.exit(1)

    except AppleMusicError as exc:
        print(f"❌  {exc}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠   Прервано пользователем.")
        sys.exit(130)


if __name__ == "__main__":
    main()
