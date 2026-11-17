"""
Провайдер YouTube Music.
Разработчик: @morokost
Дата: 2026-11-17
"""

from typing import List

import yt_dlp

from ..models import TrackMetadata
from .base import AudioCandidate, BaseAudioProvider


class YouTubeMusicProvider(BaseAudioProvider):
    name = "ytmusic"
    display_name = "YouTube Music"

    def search(self, meta: TrackMetadata, limit: int = 5) -> List[AudioCandidate]:
        queries = [
            f"ytsearch{limit}:{meta.artist} {meta.title} topic",
            f"ytsearch{limit}:{meta.artist} - {meta.title} official audio",
        ]

        opts = {
            "quiet": True,
            "extract_flat": True,
            "skip_download": True,
            "nocheckcertificate": True,
        }

        with yt_dlp.YoutubeDL(opts) as ydl:
            for query in queries:
                try:
                    res = ydl.extract_info(query, download=False)
                    entries = [e for e in res.get("entries", []) if e]
                    if entries:
                        return [
                            AudioCandidate(
                                provider_name=self.name,
                                url=e.get("url") or f"https://www.youtube.com/watch?v={e.get('id')}",
                                title=e.get("title") or "",
                                duration=float(e["duration"]) if e.get("duration") else None,
                                channel=e.get("channel") or e.get("uploader"),
                            )
                            for e in entries
                        ]
                except Exception:
                    continue

        return []
