"""
Тесты для провайдеров аудио: YouTube Music, YouTube, SoundCloud.

Разработчик : @morokost
Дата        : 2026-11-17
"""

import unittest
from applemusic_dl.models import TrackMetadata
from applemusic_dl.providers import (
    ProviderRegistry,
    YouTubeMusicProvider,
    YouTubeProvider,
    SoundCloudProvider,
    AudioCandidate,
)


class TestProviders(unittest.TestCase):
    def setUp(self):
        self.meta = TrackMetadata(
            id="1499378607",
            title="Blinding Lights",
            artist="The Weeknd",
            album="After Hours",
            duration_sec=200.0,
        )

    def test_candidate_scoring(self):
        cand = AudioCandidate(
            provider_name="ytmusic",
            url="https://youtube.com/watch?v=123",
            title="The Weeknd - Blinding Lights (Official Audio)",
            duration=201.0,
            channel="The Weeknd - Topic",
        )
        score = cand.compute_score(self.meta)
        self.assertGreaterEqual(score, 80.0)

    def test_registry_lookup(self):
        registry = ProviderRegistry(active_provider_names=["ytmusic", "youtube", "soundcloud"])
        active = registry.get_active_providers()
        self.assertEqual(len(active), 3)
        self.assertEqual(active[0].name, "ytmusic")
        self.assertEqual(active[1].name, "youtube")
        self.assertEqual(active[2].name, "soundcloud")

    def test_ytmusic_search(self):
        provider = YouTubeMusicProvider()
        candidates = provider.search(self.meta, limit=3)
        self.assertTrue(len(candidates) > 0)
        self.assertIn("The Weeknd", candidates[0].title or candidates[0].channel)

    def test_soundcloud_search(self):
        provider = SoundCloudProvider()
        candidates = provider.search(self.meta, limit=3)
        self.assertTrue(len(candidates) > 0)
        self.assertTrue(candidates[0].url.startswith("https://"))


if __name__ == "__main__":
    unittest.main()
