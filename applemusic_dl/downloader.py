"""
Основной класс загрузчика Apple Music.
Разработчик: @morokost
Дата: 2026-11-17
"""

import os
from typing import Callable, List, Optional, Union

from .apple import AppleMusicClient
from .models import AlbumMetadata, DownloadResult, TrackMetadata
from .searcher import AudioSearcher
from .tagger import MetadataTagger

_FS_FORBIDDEN = r'<>:"/\|?*'


def _sanitize(text: str) -> str:
    for ch in _FS_FORBIDDEN:
        text = text.replace(ch, "_")
    return text.strip()


class AppleMusicDownloader:
    def __init__(
        self,
        output_dir: str = "./downloads",
        providers: Optional[List[str]] = None,
        preferred_codec: str = "m4a",
        preferred_quality: str = "320",
        organize_by_album: bool = False,
        tolerance_sec: int = 8,
        overwrite: bool = False,
        fallback_to_m4a: bool = True,
        ffmpeg_location: Optional[str] = None,
        apple_client: Optional[AppleMusicClient] = None,
    ) -> None:
        self.output_dir = os.path.abspath(output_dir)
        self.organize_by_album = organize_by_album
        self.overwrite = overwrite

        self.apple_client = apple_client or AppleMusicClient()
        self.searcher = AudioSearcher(
            providers=providers,
            tolerance_sec=tolerance_sec,
            preferred_codec=preferred_codec,
            preferred_quality=preferred_quality,
            ffmpeg_location=ffmpeg_location,
            fallback_to_m4a=fallback_to_m4a,
        )
        self.tagger = MetadataTagger()

    def _target_dir(self, meta: TrackMetadata, base: Optional[str] = None) -> str:
        root = os.path.abspath(base) if base else self.output_dir
        if self.organize_by_album:
            root = os.path.join(root, _sanitize(meta.artist), _sanitize(meta.album))
        os.makedirs(root, exist_ok=True)
        return root

    def _file_basename(self, meta: TrackMetadata) -> str:
        if self.organize_by_album and meta.track_number:
            return _sanitize(f"{meta.track_number:02d} - {meta.title}")
        return _sanitize(f"{meta.artist} - {meta.title}")

    def get_track_info(self, url_or_id: str) -> TrackMetadata:
        return self.apple_client.get_track_metadata(url_or_id)

    def get_album_info(self, url_or_id: str) -> AlbumMetadata:
        return self.apple_client.get_album_metadata(url_or_id)

    def download_track(
        self,
        url_or_id: str,
        output_dir: Optional[str] = None,
    ) -> DownloadResult:
        return self._process(self.get_track_info(url_or_id), output_dir)

    def _process(self, meta: TrackMetadata, output_dir: Optional[str] = None) -> DownloadResult:
        target_dir = self._target_dir(meta, base=output_dir)
        base = os.path.join(target_dir, self._file_basename(meta))

        for ext in (".m4a", ".mp3", f".{self.searcher.preferred_codec}"):
            if os.path.exists(base + ext) and not self.overwrite:
                return DownloadResult(track=meta, file_path=base + ext, success=True)

        try:
            candidate = self.searcher.search_best_match(meta)
            file_path = self.searcher.download_audio(candidate.url, base)
            self.tagger.tag_file(file_path, meta)
            return DownloadResult(track=meta, file_path=file_path, success=True)
        except Exception as exc:
            return DownloadResult(track=meta, success=False, error=str(exc))

    def download_album(
        self,
        url_or_id: str,
        output_dir: Optional[str] = None,
        on_track_start: Optional[Callable[[TrackMetadata, int, int], None]] = None,
        on_track_complete: Optional[Callable[[DownloadResult, int, int], None]] = None,
    ) -> List[DownloadResult]:
        album = self.get_album_info(url_or_id)
        total = len(album.tracks)
        results: List[DownloadResult] = []

        for idx, track in enumerate(album.tracks, start=1):
            if on_track_start:
                on_track_start(track, idx, total)
            result = self._process(track, output_dir)
            results.append(result)
            if on_track_complete:
                on_track_complete(result, idx, total)

        return results

    def download(
        self,
        url: str,
        output_dir: Optional[str] = None,
        on_track_start: Optional[Callable[[TrackMetadata, int, int], None]] = None,
        on_track_complete: Optional[Callable[[DownloadResult, int, int], None]] = None,
    ) -> Union[DownloadResult, List[DownloadResult]]:
        res_type, _, _ = self.apple_client.parse_url(url)
        if res_type == "album":
            return self.download_album(url, output_dir, on_track_start, on_track_complete)
        return self.download_track(url, output_dir)
