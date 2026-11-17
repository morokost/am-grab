"""
Модели данных треков и альбомов.
Разработчик: @morokost
Дата: 2026-11-17
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TrackMetadata:
    id: str
    title: str
    artist: str
    album: str
    duration_sec: float
    artwork_url: Optional[str] = None
    track_number: Optional[int] = None
    track_count: Optional[int] = None
    disc_number: Optional[int] = 1
    release_date: Optional[str] = None
    genre: Optional[str] = None
    country: Optional[str] = None
    url: Optional[str] = None

    @property
    def safe_filename(self) -> str:
        name = f"{self.artist} - {self.title}"
        for ch in r'<>:"/\|?*':
            name = name.replace(ch, "_")
        return name.strip()


@dataclass
class AlbumMetadata:
    id: str
    title: str
    artist: str
    track_count: int
    release_date: Optional[str] = None
    genre: Optional[str] = None
    artwork_url: Optional[str] = None
    country: Optional[str] = None
    url: Optional[str] = None
    tracks: List[TrackMetadata] = field(default_factory=list)


@dataclass
class DownloadResult:
    track: TrackMetadata
    file_path: Optional[str] = None
    success: bool = True
    error: Optional[str] = None
