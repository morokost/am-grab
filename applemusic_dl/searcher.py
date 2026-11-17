"""
Модуль поиска и загрузки аудиопотока через yt-dlp.
Разработчик: @morokost
Дата: 2026-11-17
"""

import glob
import os
import shutil
from typing import List, Optional

import yt_dlp

from .exceptions import DownloadFailedError, FFmpegNotFoundError
from .models import TrackMetadata
from .providers import AudioCandidate, ProviderRegistry

_M4A_FORMAT = "140/bestaudio[ext=m4a]/bestaudio"
_TEMP_EXTS = (".part", ".ytdl")


class AudioSearcher:
    def __init__(
        self,
        providers: Optional[List[str]] = None,
        tolerance_sec: int = 8,
        preferred_codec: str = "m4a",
        preferred_quality: str = "320",
        search_count: int = 5,
        ffmpeg_location: Optional[str] = None,
        fallback_to_m4a: bool = True,
    ) -> None:
        self.tolerance_sec = tolerance_sec
        self.preferred_codec = preferred_codec.lower().strip()
        self.preferred_quality = preferred_quality
        self.search_count = search_count
        self.fallback_to_m4a = fallback_to_m4a
        self.ffmpeg_location = ffmpeg_location or self._detect_ffmpeg()
        self.registry = ProviderRegistry(active_provider_names=providers)

    @staticmethod
    def _detect_ffmpeg() -> Optional[str]:
        found = shutil.which("ffmpeg")
        if found:
            return os.path.dirname(found)
        winget = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Links")
        if os.path.exists(os.path.join(winget, "ffmpeg.exe")):
            return winget
        return None

    def search_best_match(self, meta: TrackMetadata) -> AudioCandidate:
        return self.registry.find_best_candidate(
            meta=meta,
            tolerance_sec=self.tolerance_sec,
            search_limit=self.search_count,
        )

    def download_audio(self, target_url: str, output_path_without_ext: str) -> str:
        is_mp3 = self.preferred_codec in ("mp3", "audio/mp3")
        has_ffmpeg = bool(self.ffmpeg_location or shutil.which("ffmpeg"))
        use_ffmpeg = is_mp3 and has_ffmpeg

        if is_mp3 and not has_ffmpeg and not self.fallback_to_m4a:
            raise FFmpegNotFoundError("FFmpeg не обнаружен. Установите его или используйте m4a.")

        opts: dict = {
            "outtmpl": f"{output_path_without_ext}.%(ext)s",
            "quiet": True,
            "nocheckcertificate": True,
        }

        if use_ffmpeg:
            opts["format"] = "bestaudio/best"
            opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": self.preferred_quality,
            }]
            if self.ffmpeg_location:
                opts["ffmpeg_location"] = self.ffmpeg_location
        else:
            opts["format"] = _M4A_FORMAT

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([target_url])
        except Exception as exc:
            if ("ffmpeg" in str(exc).lower() or "ffprobe" in str(exc).lower()) and use_ffmpeg:
                return self._download_m4a(target_url, output_path_without_ext)
            raise DownloadFailedError(f"Ошибка загрузки: {exc}") from exc

        return self._find_output(output_path_without_ext)

    def _download_m4a(self, url: str, out: str) -> str:
        opts = {
            "format": _M4A_FORMAT,
            "outtmpl": f"{out}.%(ext)s",
            "quiet": True,
            "nocheckcertificate": True,
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
        return self._find_output(out)

    @staticmethod
    def _find_output(base: str) -> str:
        files = [f for f in glob.glob(f"{base}.*") if not f.endswith(_TEMP_EXTS)]
        if not files:
            raise DownloadFailedError(f"Файл не найден: {base}.*")
        return files[0]
