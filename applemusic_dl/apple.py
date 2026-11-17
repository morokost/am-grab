"""
Клиент iTunes Lookup API для Apple Music.
Разработчик: @morokost
Дата: 2026-11-17
"""

import re
from typing import List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

import requests

from .exceptions import AlbumNotFoundError, InvalidURLError, TrackNotFoundError
from .models import AlbumMetadata, TrackMetadata

_ARTWORK_LOW = "100x100bb"
_ARTWORK_HIGH = "1400x1400bb"
_ITUNES_API = "https://itunes.apple.com/lookup"
_DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)


def _hires(url: str) -> str:
    return url.replace(_ARTWORK_LOW, _ARTWORK_HIGH) if url else url


class AppleMusicClient:
    def __init__(
        self,
        timeout: int = 10,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.timeout = timeout
        self.session = session or requests.Session()
        self.session.headers.update({"User-Agent": _DEFAULT_UA})

    def resolve_url(self, url: str) -> str:
        url = url.strip()
        if "apple.co" in url:
            try:
                resp = self.session.head(url, allow_redirects=True, timeout=self.timeout)
                return resp.url
            except Exception:
                pass
        return url

    def parse_url(self, url: str) -> Tuple[str, Optional[str], Optional[str]]:
        resolved = self.resolve_url(url)
        parsed = urlparse(resolved)
        query = parse_qs(parsed.query)

        segments = [s for s in parsed.path.split("/") if s]
        country = segments[0] if segments and len(segments[0]) == 2 else None

        if "i" in query and query["i"]:
            return "track", query["i"][0], country

        if "/song/" in parsed.path:
            m = re.search(r"/(\d+)(?:\?|$)", parsed.path)
            if m:
                return "track", m.group(1), country

        if "/album/" in parsed.path:
            m = re.search(r"/(\d+)(?:\?|$)", parsed.path)
            if m:
                return "album", m.group(1), country

        m = re.search(r"/(\d+)(?:\?|$)", parsed.path)
        if m:
            return "track", m.group(1), country

        raise InvalidURLError(f"Не удалось распознать ссылку: '{url}'")

    def _itunes_lookup(
        self,
        entity_id: str,
        country: Optional[str] = None,
        entity: Optional[str] = None,
    ) -> List[dict]:
        def _params(c: Optional[str]) -> dict:
            p: dict = {"id": entity_id}
            if c:
                p["country"] = c
            if entity:
                p["entity"] = entity
            return p

        for params in [_params(country), _params(None)]:
            if params == _params(None) and country is None:
                break
            try:
                resp = self.session.get(_ITUNES_API, params=params, timeout=self.timeout)
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("resultCount", 0) > 0:
                        return data.get("results", [])
            except Exception:
                continue

        try:
            resp = self.session.get(_ITUNES_API, params=_params(None), timeout=self.timeout)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("results", [])
        except Exception:
            pass

        return []

    def get_track_metadata(self, track_id_or_url: str) -> TrackMetadata:
        if track_id_or_url.startswith("http"):
            _, track_id, country = self.parse_url(track_id_or_url)
            original_url: Optional[str] = track_id_or_url
        else:
            track_id = track_id_or_url
            country = None
            original_url = None

        results = self._itunes_lookup(track_id, country=country)
        if not results:
            raise TrackNotFoundError(f"Трек '{track_id}' не найден в Apple Music.")

        item = results[0]
        if item.get("wrapperType") == "collection":
            raise InvalidURLError("Указана ссылка на целый альбом. Используйте get_album_metadata().")

        artwork = _hires(item.get("artworkUrl100", ""))

        return TrackMetadata(
            id=str(item.get("trackId", track_id)),
            title=item.get("trackName", "Unknown Title"),
            artist=item.get("artistName", "Unknown Artist"),
            album=item.get("collectionName", "Unknown Album"),
            duration_sec=float(item.get("trackTimeMillis", 0)) / 1000.0,
            artwork_url=artwork or None,
            track_number=item.get("trackNumber"),
            track_count=item.get("trackCount"),
            disc_number=item.get("discNumber", 1),
            release_date=item.get("releaseDate"),
            genre=item.get("primaryGenreName"),
            country=country,
            url=original_url,
        )

    def get_album_metadata(self, album_id_or_url: str) -> AlbumMetadata:
        if album_id_or_url.startswith("http"):
            _, album_id, country = self.parse_url(album_id_or_url)
            original_url: Optional[str] = album_id_or_url
        else:
            album_id = album_id_or_url
            country = None
            original_url = None

        results = self._itunes_lookup(album_id, country=country, entity="song")
        if not results:
            raise AlbumNotFoundError(f"Альбом '{album_id}' не найден в Apple Music.")

        album_info = results[0]
        artwork = _hires(album_info.get("artworkUrl100", ""))

        tracks: List[TrackMetadata] = []
        for item in results[1:]:
            if item.get("wrapperType") != "track":
                continue
            item_art = _hires(item.get("artworkUrl100", artwork))
            tracks.append(
                TrackMetadata(
                    id=str(item.get("trackId")),
                    title=item.get("trackName", "Unknown Title"),
                    artist=item.get("artistName", album_info.get("artistName", "Unknown Artist")),
                    album=item.get("collectionName", album_info.get("collectionName", "Unknown Album")),
                    duration_sec=float(item.get("trackTimeMillis", 0)) / 1000.0,
                    artwork_url=item_art or None,
                    track_number=item.get("trackNumber"),
                    track_count=item.get("trackCount", album_info.get("trackCount")),
                    disc_number=item.get("discNumber", 1),
                    release_date=item.get("releaseDate", album_info.get("releaseDate")),
                    genre=item.get("primaryGenreName", album_info.get("primaryGenreName")),
                    country=country,
                    url=item.get("trackViewUrl"),
                )
            )

        return AlbumMetadata(
            id=str(album_info.get("collectionId", album_id)),
            title=album_info.get("collectionName", "Unknown Album"),
            artist=album_info.get("artistName", "Unknown Artist"),
            track_count=album_info.get("trackCount", len(tracks)),
            release_date=album_info.get("releaseDate"),
            genre=album_info.get("primaryGenreName"),
            artwork_url=artwork or None,
            country=country,
            url=original_url,
            tracks=tracks,
        )
