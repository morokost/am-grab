"""
Реестр и выбор лучшего аудио-кандидата среди провайдеров.
Разработчик: @morokost
Дата: 2026-11-17
"""

from typing import Dict, List, Optional, Type

from ..exceptions import AudioMatchNotFoundError
from ..models import TrackMetadata
from .base import AudioCandidate, BaseAudioProvider
from .soundcloud import SoundCloudProvider
from .youtube import YouTubeProvider
from .youtube_music import YouTubeMusicProvider

_FAST_MATCH_THRESHOLD = 80.0

_BUILTIN: Dict[str, Type[BaseAudioProvider]] = {
    "ytmusic": YouTubeMusicProvider,
    "youtube": YouTubeProvider,
    "soundcloud": SoundCloudProvider,
}


class ProviderRegistry:
    def __init__(self, active_provider_names: Optional[List[str]] = None) -> None:
        self._providers: Dict[str, Type[BaseAudioProvider]] = dict(_BUILTIN)
        self.active_names: List[str] = active_provider_names or list(_BUILTIN)

    def register(self, provider_cls: Type[BaseAudioProvider]) -> None:
        self._providers[provider_cls.name] = provider_cls

    def get_active_providers(self) -> List[BaseAudioProvider]:
        return [
            self._providers[name.strip().lower()]()
            for name in self.active_names
            if name.strip().lower() in self._providers
        ]

    def find_best_candidate(
        self,
        meta: TrackMetadata,
        tolerance_sec: int = 8,
        search_limit: int = 5,
    ) -> AudioCandidate:
        providers = self.get_active_providers()
        if not providers:
            raise AudioMatchNotFoundError("Не указаны активные провайдеры.")

        all_candidates: List[AudioCandidate] = []

        for provider in providers:
            try:
                candidates = provider.search(meta, limit=search_limit)
            except Exception:
                continue

            for cand in candidates:
                score = cand.compute_score(meta, tolerance_sec=tolerance_sec)
                all_candidates.append(cand)
                if score >= _FAST_MATCH_THRESHOLD:
                    return cand

        if not all_candidates:
            names = ", ".join(p.name for p in providers)
            raise AudioMatchNotFoundError(
                f"Аудио не найдено ({names}) для '{meta.artist} – {meta.title}'."
            )

        return max(all_candidates, key=lambda c: c.score)
