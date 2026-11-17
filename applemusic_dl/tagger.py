"""
Тегирование файлов M4A и MP3 метаданными и обложками.
Разработчик: @morokost
Дата: 2026-11-17
"""

import os
from typing import Optional

import requests
from mutagen.id3 import APIC, ID3, TALB, TCON, TDRC, TIT2, TPOS, TPE1, TRCK
from mutagen.id3 import error as ID3Error
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4, MP4Cover

from .models import TrackMetadata


class MetadataTagger:
    def __init__(self, session: Optional[requests.Session] = None) -> None:
        self.session = session or requests.Session()

    def tag_file(self, file_path: str, meta: TrackMetadata) -> None:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл не найден: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()

        if ext in (".m4a", ".mp4", ".aac"):
            self._tag_m4a(file_path, meta)
        elif ext == ".mp3":
            self._tag_mp3(file_path, meta)
        else:
            try:
                self._tag_m4a(file_path, meta)
            except Exception:
                self._tag_mp3(file_path, meta)

    def _tag_m4a(self, file_path: str, meta: TrackMetadata) -> None:
        audio = MP4(file_path)

        if meta.title:
            audio["\xa9nam"] = [meta.title]
        if meta.artist:
            audio["\xa9ART"] = [meta.artist]
        if meta.album:
            audio["\xa9alb"] = [meta.album]
        if meta.track_number:
            audio["trkn"] = [(meta.track_number, meta.track_count or 0)]
        if meta.disc_number:
            audio["disk"] = [(meta.disc_number, 1)]
        if meta.genre:
            audio["\xa9gen"] = [meta.genre]
        if meta.release_date:
            audio["\xa9day"] = [meta.release_date[:4]]

        if meta.artwork_url:
            cover = self._fetch_artwork(meta.artwork_url)
            if cover:
                audio["covr"] = [MP4Cover(cover, imageformat=MP4Cover.FORMAT_JPEG)]

        audio.save()

    def _tag_mp3(self, file_path: str, meta: TrackMetadata) -> None:
        try:
            audio = MP3(file_path, ID3=ID3)
        except Exception as exc:
            raise ValueError(f"Не удалось открыть MP3: {exc}") from exc

        try:
            audio.add_tags()
        except ID3Error:
            pass

        tags = audio.tags
        if meta.title:
            tags.add(TIT2(encoding=3, text=meta.title))
        if meta.artist:
            tags.add(TPE1(encoding=3, text=meta.artist))
        if meta.album:
            tags.add(TALB(encoding=3, text=meta.album))
        if meta.track_number:
            trck = f"{meta.track_number}/{meta.track_count}" if meta.track_count else str(meta.track_number)
            tags.add(TRCK(encoding=3, text=trck))
        if meta.disc_number:
            tags.add(TPOS(encoding=3, text=str(meta.disc_number)))
        if meta.genre:
            tags.add(TCON(encoding=3, text=meta.genre))
        if meta.release_date:
            tags.add(TDRC(encoding=3, text=meta.release_date[:4]))
        if meta.artwork_url:
            cover = self._fetch_artwork(meta.artwork_url)
            if cover:
                tags.add(APIC(encoding=3, mime="image/jpeg", type=3, desc="Cover", data=cover))

        audio.save()

    def _fetch_artwork(self, url: str) -> Optional[bytes]:
        try:
            resp = self.session.get(url, timeout=10)
            if resp.status_code == 200:
                return resp.content
        except Exception:
            pass
        return None
