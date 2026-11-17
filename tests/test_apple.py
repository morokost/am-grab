"""
Тесты для модуля applemusic_dl.apple.

Разработчик : @morokost
Дата        : 2026-11-17
"""

import unittest
from applemusic_dl.apple import AppleMusicClient
from applemusic_dl.models import TrackMetadata, AlbumMetadata
from applemusic_dl.exceptions import InvalidURLError


class TestAppleMusicClient(unittest.TestCase):
    def setUp(self):
        self.client = AppleMusicClient()

    def test_parse_track_album_url(self):
        url = "https://music.apple.com/ru/album/song-name/1234567890?i=9876543210"
        res_type, entity_id, country = self.client.parse_url(url)
        self.assertEqual(res_type, "track")
        self.assertEqual(entity_id, "9876543210")
        self.assertEqual(country, "ru")

    def test_parse_album_url(self):
        url = "https://music.apple.com/us/album/after-hours/1499378108"
        res_type, entity_id, country = self.client.parse_url(url)
        self.assertEqual(res_type, "album")
        self.assertEqual(entity_id, "1499378108")
        self.assertEqual(country, "us")

    def test_parse_song_url(self):
        url = "https://music.apple.com/kz/song/some-song/1122334455"
        res_type, entity_id, country = self.client.parse_url(url)
        self.assertEqual(res_type, "track")
        self.assertEqual(entity_id, "1122334455")
        self.assertEqual(country, "kz")

    def test_invalid_url(self):
        with self.assertRaises(InvalidURLError):
            self.client.parse_url("https://google.com/test")

    def test_get_track_metadata(self):
        url = "https://music.apple.com/us/album/blinding-lights/1499378108?i=1499378607"
        meta = self.client.get_track_metadata(url)
        self.assertIsInstance(meta, TrackMetadata)
        self.assertEqual(meta.artist, "The Weeknd")
        self.assertEqual(meta.title, "Blinding Lights")
        self.assertGreater(meta.duration_sec, 100)
        self.assertTrue(meta.artwork_url.startswith("https://"))


if __name__ == "__main__":
    unittest.main()
