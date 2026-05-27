"""Media widget suite: WAbstractMedia, WAudio, WVideo, WMediaPlayer,
WSound + the new JDoubleSignal type.

All five widgets (yes, even WSound — its constructor calls
``WApplication::instance()->getSoundManager()``) need an active session;
the gallery boot test exercises real construction inside a live server.
Here we verify the binding surface and the standalone-instantiable enums.
"""

from __future__ import annotations

import pytest
import witty_for_python as wt


# ---- JDoubleSignal --------------------------------------------------------

def test_jdouble_signal_exposed() -> None:
    assert isinstance(wt.JDoubleSignal, type)
    assert hasattr(wt.JDoubleSignal, "connect")
    assert hasattr(wt.JDoubleSignal, "disconnect_all_slots")


# ---- Inheritance ----------------------------------------------------------

@pytest.mark.parametrize("cls,base", [
    (wt.WAbstractMedia, wt.WInteractWidget),
    (wt.WAudio,         wt.WAbstractMedia),
    (wt.WVideo,         wt.WAbstractMedia),
    (wt.WMediaPlayer,   wt.WWidget),
    (wt.WSound,         wt.WObject),
])
def test_media_class_inheritance(cls: type, base: type) -> None:
    assert issubclass(cls, base)


# ---- Method surface (no construction — needs session) --------------------

@pytest.mark.parametrize("cls,attr", [
    (wt.WAbstractMedia, "add_source"),
    (wt.WAbstractMedia, "clear_sources"),
    (wt.WAbstractMedia, "set_alternative_content"),
    (wt.WAbstractMedia, "set_options"),
    (wt.WAbstractMedia, "set_preload_mode"),
    (wt.WAbstractMedia, "play"),
    (wt.WAbstractMedia, "pause"),
    (wt.WAbstractMedia, "playing"),
    (wt.WAbstractMedia, "playback_started"),
    (wt.WAbstractMedia, "playback_paused"),
    (wt.WAbstractMedia, "ended"),
    (wt.WAbstractMedia, "time_updated"),
    (wt.WAbstractMedia, "volume_changed"),
    (wt.WVideo,         "set_poster"),
    (wt.WMediaPlayer,   "add_source"),
    (wt.WMediaPlayer,   "set_title"),
    (wt.WMediaPlayer,   "set_video_size"),
    (wt.WMediaPlayer,   "play"),
    (wt.WMediaPlayer,   "pause"),
    (wt.WMediaPlayer,   "stop"),
    (wt.WMediaPlayer,   "seek"),
    (wt.WMediaPlayer,   "set_playback_rate"),
    (wt.WMediaPlayer,   "set_volume"),
    (wt.WMediaPlayer,   "mute"),
    (wt.WMediaPlayer,   "set_button"),
    (wt.WMediaPlayer,   "set_progress_bar"),
    (wt.WMediaPlayer,   "set_text"),
    (wt.WMediaPlayer,   "playback_started"),
    (wt.WMediaPlayer,   "time_updated"),
    (wt.WMediaPlayer,   "volume_changed"),
    (wt.WSound,         "add_source"),
    (wt.WSound,         "loops"),
    (wt.WSound,         "play"),
    (wt.WSound,         "stop"),
])
def test_media_attribute_present(cls: type, attr: str) -> None:
    assert hasattr(cls, attr), f"{cls.__name__} missing: {attr}"


# ---- Enum members --------------------------------------------------------

def test_player_option_members() -> None:
    """PlayerOption is bound is_arithmetic so callers OR bits to combine."""
    combined = int(wt.PlayerOption.Autoplay) | int(wt.PlayerOption.Loop)
    assert combined == int(wt.PlayerOption.Autoplay) + int(wt.PlayerOption.Loop)


def test_media_preload_mode_members() -> None:
    assert wt.MediaPreloadMode.None_ != wt.MediaPreloadMode.Auto


def test_media_type_members() -> None:
    assert wt.MediaType.Audio != wt.MediaType.Video


@pytest.mark.parametrize("name", [
    "MP3", "M4A", "OGA", "WAV", "WEBMA", "FLA",
    "M4V", "OGV", "WEBMV", "FLV", "PosterImage",
])
def test_media_encoding_has_format(name: str) -> None:
    assert hasattr(wt.MediaEncoding, name)


@pytest.mark.parametrize("name", [
    "VideoPlay", "Play", "Pause", "Stop", "VolumeMute",
    "VolumeUnmute", "VolumeMax", "FullScreen", "RestoreScreen",
    "RepeatOn", "RepeatOff",
])
def test_media_player_button_id_members(name: str) -> None:
    assert hasattr(wt.MediaPlayerButtonId, name)


def test_media_player_progress_bar_id_members() -> None:
    assert wt.MediaPlayerProgressBarId.Time != wt.MediaPlayerProgressBarId.Volume


def test_media_player_text_id_members() -> None:
    for name in ("CurrentTime", "Duration", "Title"):
        assert hasattr(wt.MediaPlayerTextId, name)
