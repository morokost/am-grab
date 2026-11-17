"""
Провайдеры поиска аудио.
Разработчик: @morokost
Дата: 2026-11-17
"""

from .base import AudioCandidate, BaseAudioProvider
from .registry import ProviderRegistry
from .soundcloud import SoundCloudProvider
from .youtube import YouTubeProvider
from .youtube_music import YouTubeMusicProvider

__all__ = [
    "BaseAudioProvider",
    "AudioCandidate",
    "YouTubeMusicProvider",
    "YouTubeProvider",
    "SoundCloudProvider",
    "ProviderRegistry",
]
