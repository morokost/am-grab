"""
Провайдер SoundCloud.
Разработчик: @morokost
Дата: 2026-11-17
"""

from typing import List

import yt_dlp

from ..models import TrackMetadata
from .base import AudioCandidate, BaseAudioProvider


class SoundCloudProvider(BaseAudioProvider):
    name = "soundcloud"
    display_name = "SoundCloud"

    def search(self, meta: TrackMetadata, limit: int = 5) -> List[AudioCandidate]:
        queries = [
            f"scsearch{limit}:{meta.artist} {meta.title}",
            f"scsearch{limit}:{meta.title}",
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
                    entries = [e for e in res.get("entries", []) if e and e.get("url")]
                    if entries:
                        return [
                            AudioCandidate(
                                provider_name=self.name,
                                url=e["url"],
                                title=e.get("title") or "",
                                duration=float(e["duration"]) if e.get("duration") else None,
                                uploader=e.get("uploader"),
                            )
                            for e in entries
                        ]
                except Exception:
                    continue

        return []
