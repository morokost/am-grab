"""
Базовые типы провайдеров аудио.
Разработчик: @morokost
Дата: 2026-11-17
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from ..models import TrackMetadata

_PENALTY_WORDS = ("live", "cover", "remix", "instrumental", "acoustic", "slowed", "reverb")


@dataclass
class AudioCandidate:
    provider_name: str
    url: str
    title: str
    duration: Optional[float] = None
    channel: Optional[str] = None
    uploader: Optional[str] = None
    score: float = 0.0

    def compute_score(self, meta: TrackMetadata, tolerance_sec: int = 8) -> float:
        score = 50.0

        if self.duration and meta.duration_sec:
            diff = abs(self.duration - meta.duration_sec)
            if diff <= 2.0:
                score += 35.0
            elif diff <= tolerance_sec:
                score += max(0.0, 30.0 - diff * 2.5)
            else:
                score -= min(40.0, diff * 2.0)

        title_lower = (self.title or "").lower()
        channel_lower = (self.channel or self.uploader or "").lower()
        track_title_lower = meta.title.lower()
        artist_lower = meta.artist.lower()

        if track_title_lower in title_lower:
            score += 15.0
        if artist_lower in title_lower or artist_lower in channel_lower:
            score += 15.0

        if "topic" in channel_lower:
            score += 15.0
        if "official audio" in title_lower:
            score += 10.0

        for word in _PENALTY_WORDS:
            if word in title_lower and word not in track_title_lower:
                score -= 25.0

        self.score = max(0.0, score)
        return self.score


class BaseAudioProvider(ABC):
    name: str = "base"
    display_name: str = "Base Provider"

    @abstractmethod
    def search(self, meta: TrackMetadata, limit: int = 5) -> List[AudioCandidate]:
        pass
