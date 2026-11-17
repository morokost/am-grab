"""
Иерархия исключений библиотеки applemusic-dl.
Разработчик: @morokost
Дата: 2026-11-17
"""


class AppleMusicError(Exception):
    pass


class InvalidURLError(AppleMusicError):
    pass


class TrackNotFoundError(AppleMusicError):
    pass


class AlbumNotFoundError(AppleMusicError):
    pass


class AudioMatchNotFoundError(AppleMusicError):
    pass


class FFmpegNotFoundError(AppleMusicError):
    pass


class DownloadFailedError(AppleMusicError):
    pass
