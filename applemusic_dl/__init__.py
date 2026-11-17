"""
applemusic-dl
Разработчик: @morokost
Дата: 2026-11-17
Лицензия: MIT
"""

import os

for _extra_path in [
    os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Links"),
    r"C:\ProgramData\chocolatey\bin",
    os.path.expandvars(r"%USERPROFILE%\scoop\shims"),
]:
    if os.path.exists(_extra_path) and _extra_path not in os.environ.get("PATH", ""):
        os.environ["PATH"] = _extra_path + os.pathsep + os.environ.get("PATH", "")

from .models import TrackMetadata, AlbumMetadata, DownloadResult
from .apple import AppleMusicClient
from .downloader import AppleMusicDownloader
from .providers import (
    BaseAudioProvider,
    AudioCandidate,
    YouTubeMusicProvider,
    YouTubeProvider,
    SoundCloudProvider,
    ProviderRegistry,
)
from .exceptions import (
    AppleMusicError,
    InvalidURLError,
    TrackNotFoundError,
    AlbumNotFoundError,
    AudioMatchNotFoundError,
    FFmpegNotFoundError,
    DownloadFailedError,
)

__version__ = "0.2.0"
__author__ = "@morokost"

__all__ = [
    "AppleMusicDownloader",
    "AppleMusicClient",
    "TrackMetadata",
    "AlbumMetadata",
    "DownloadResult",
    "BaseAudioProvider",
    "AudioCandidate",
    "YouTubeMusicProvider",
    "YouTubeProvider",
    "SoundCloudProvider",
    "ProviderRegistry",
    "AppleMusicError",
    "InvalidURLError",
    "TrackNotFoundError",
    "AlbumNotFoundError",
    "AudioMatchNotFoundError",
    "FFmpegNotFoundError",
    "DownloadFailedError",
]
