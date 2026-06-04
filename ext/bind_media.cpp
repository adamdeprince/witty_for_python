#include "common.hpp"
#include "signal_helpers.hpp"

#include <Wt/WAbstractMedia.h>
#include <Wt/WAudio.h>
#include <Wt/WJavaScript.h>           // JSignal<double>
#include <Wt/WLink.h>
#include <Wt/WMediaPlayer.h>
#include <Wt/WProgressBar.h>          // WMediaPlayer.setProgressBar
#include <Wt/WSound.h>
#include <Wt/WText.h>                 // WMediaPlayer.setText
#include <Wt/WVideo.h>

#include <memory>
#include <string>

namespace witty_for_python {

void register_media(nb::module_& m) {
    // ---- JSignal<double> ----
    //
    // Bound here because WMediaPlayer.timeUpdated / volumeChanged are
    // JSignal<double> (the current playback time / volume from the
    // client). Same shape as the existing JInt64Signal binding.

    nb::class_<Wt::JSignal<double>>(m, "JDoubleSignal",
        "JavaScript signal carrying a single double payload. Used by\n"
        "WMediaPlayer.time_updated (current playback time in seconds) and\n"
        "WMediaPlayer.volume_changed (volume in 0.0-1.0).")
        .def("connect",
            [](Wt::JSignal<double>& s, nb::callable cb) {
                return py_connect<Wt::JSignal<double>, double>(s, std::move(cb));
            }, "callable"_a,
            "Subscribe a callable taking a float. Returns a Connection —\n"
            "call `.disconnect()` to stop receiving.")
        .def("disconnect_all_slots",
            [](Wt::JSignal<double>& s) {
                connection_registry_disconnect_all(&s);
            },
            "Drop every Python subscriber attached via `connect`.");

    // ---- Enums (WAbstractMedia) ----

    nb::enum_<Wt::PlayerOption>(m, "PlayerOption", nb::is_arithmetic(),
        "Bitfield of HTML5 media element flags. OR values together when\n"
        "passing to WAbstractMedia.set_options.")
        .value("Autoplay", Wt::PlayerOption::Autoplay,
               "Begin playback as soon as the media loads (browsers often\n"
               "block this unless the audio is muted).")
        .value("Loop",     Wt::PlayerOption::Loop,
               "Restart from the beginning when playback ends.")
        .value("Controls", Wt::PlayerOption::Controls,
               "Show the browser-default playback controls.");

    nb::enum_<Wt::MediaPreloadMode>(m, "MediaPreloadMode",
        "How aggressively the browser preloads media before playback —\n"
        "maps to the HTML5 `preload` attribute.")
        .value("None_",    Wt::MediaPreloadMode::None,
               "Don't preload anything until play() is called.")
        .value("Auto",     Wt::MediaPreloadMode::Auto,
               "Preload as much as the browser sees fit.")
        .value("Metadata", Wt::MediaPreloadMode::Metadata,
               "Fetch metadata (duration, dimensions) but not the media\n"
               "body itself.");

    // Multiple sources can be added; the browser picks the first format
    // it can play. The five EventSignals are bound as the property names
    // they wear in C++; the play/pause methods are bound directly.

    nb::class_<Wt::WAbstractMedia, Wt::WInteractWidget>(m, "WAbstractMedia",
        "Abstract base for WAudio and WVideo — wraps an HTML5 `<audio>`\n"
        "or `<video>` element and exposes the standard playback API\n"
        "(play / pause / volume / preload) along with the matching\n"
        "EventSignals.\n"
        "\n"
        "    video = container.add_widget(wt.WVideo())\n"
        "    video.add_source(wt.WLink('/clip.webm'), 'video/webm')\n"
        "    video.set_options(int(wt.PlayerOption.Controls)\n"
        "                      | int(wt.PlayerOption.Loop))\n"
        "    video.ended.connect(reset_panel)\n"
        "\n"
        "Add several sources for cross-browser support; the browser will\n"
        "use the first one it knows how to decode based on the optional\n"
        "MIME-type hint.")
        .def("add_source",
            [](Wt::WAbstractMedia& self, const Wt::WLink& source,
               const std::string& mime_type, const std::string& media) {
                self.addSource(source, mime_type, media);
            },
            "source"_a,
            "mime_type"_a = std::string(),
            "media"_a = std::string(),
            "Add a source URL (via WLink). `mime_type` is the content-type "
            "hint the browser uses to pick a source; `media` is a CSS media "
            "query (e.g. 'screen and (min-width: 600px)').")
        .def("clear_sources", &Wt::WAbstractMedia::clearSources,
             "Remove every source previously added.")
        .def("set_alternative_content",
            [](Wt::WAbstractMedia& self, nb::object py_alt) {
                auto alt = nb::cast<std::unique_ptr<Wt::WWidget>>(py_alt);
                self.setAlternativeContent(std::move(alt));
                nb::inst_set_state(py_alt, /*ready*/ true,
                                   /*destruct*/ false);
            },
            "widget"_a,
            "Widget shown to users whose browser can't play any of the "
            "configured sources. Ownership transfers; the wrapper is "
            "re-armed as a non-owning alias.")
        .def("set_options",
            [](Wt::WAbstractMedia& self, int options) {
                self.setOptions(Wt::WFlags<Wt::PlayerOption>(
                    static_cast<Wt::PlayerOption>(options)));
            },
            "options"_a,
            "Bitwise-OR of PlayerOption values (Autoplay | Loop | Controls).")
        .def("set_preload_mode", &Wt::WAbstractMedia::setPreloadMode,
             "mode"_a,
             "Set the browser's preload behavior (None_ / Metadata / Auto).")
        .def("play", &Wt::WAbstractMedia::play,
             "Start playback. No-op if already playing.")
        .def("pause", &Wt::WAbstractMedia::pause,
             "Pause playback. No-op if already paused.")
        .def_prop_ro("playing", &Wt::WAbstractMedia::playing,
             "True iff the media element is currently playing.")
        .def_prop_ro("playback_started",
                     &Wt::WAbstractMedia::playbackStarted,
                     nb::rv_policy::reference_internal,
                     "EventSignal[] — fires when playback begins.")
        .def_prop_ro("playback_paused",
                     &Wt::WAbstractMedia::playbackPaused,
                     nb::rv_policy::reference_internal,
                     "EventSignal[] — fires when playback is paused.")
        .def_prop_ro("ended",
                     &Wt::WAbstractMedia::ended,
                     nb::rv_policy::reference_internal,
                     "EventSignal[] — fires when the media reaches the end\n"
                     "(does not fire on Loop=True).")
        .def_prop_ro("time_updated",
                     &Wt::WAbstractMedia::timeUpdated,
                     nb::rv_policy::reference_internal,
                     "EventSignal[] — fires periodically (~4×/sec by "
                     "browser convention) during playback.")
        .def_prop_ro("volume_changed",
                     &Wt::WAbstractMedia::volumeChanged,
                     nb::rv_policy::reference_internal,
                     "EventSignal[] — fires when the user changes the\n"
                     "volume via the browser controls.");

    nb::class_<Wt::WAudio, Wt::WAbstractMedia>(m, "WAudio",
        "HTML5 `<audio>` element. Wraps the browser's built-in audio\n"
        "playback — set sources via the inherited add_source, then either\n"
        "show the browser controls (PlayerOption.Controls) or drive play()\n"
        "/ pause() from Python.\n"
        "\n"
        "    audio = container.add_widget(wt.WAudio())\n"
        "    audio.add_source(wt.WLink('/clip.mp3'), 'audio/mpeg')\n"
        "    audio.set_options(int(wt.PlayerOption.Controls))")
        .def(heap_init<Wt::WAudio>(),
             "Construct an empty audio element. Add sources before adding\n"
             "to a container.");

    nb::class_<Wt::WVideo, Wt::WAbstractMedia>(m, "WVideo",
        "HTML5 `<video>` element. Same API as WAudio but renders a video\n"
        "viewport — combine with `set_poster` for a still-image preview\n"
        "shown before playback begins.\n"
        "\n"
        "    video = container.add_widget(wt.WVideo())\n"
        "    video.add_source(wt.WLink('/clip.webm'), 'video/webm')\n"
        "    video.add_source(wt.WLink('/clip.mp4'), 'video/mp4')\n"
        "    video.set_poster('/thumb.jpg')\n"
        "    video.set_options(int(wt.PlayerOption.Controls))")
        .def(heap_init<Wt::WVideo>(),
             "Construct an empty video element. Add sources before adding\n"
             "to a container.")
        .def("set_poster", &Wt::WVideo::setPoster, "url"_a,
             "URL of a thumbnail shown before playback starts (HTML "
             "`poster` attribute).");

    // Different from WAudio/WVideo: provides Wt-rendered playback
    // controls instead of relying on the browser's defaults. Uses
    // jPlayer under the hood for cross-browser support.

    nb::enum_<Wt::MediaEncoding>(m, "MediaEncoding",
        "Encoding label for WMediaPlayer.add_source. Add the same logical\n"
        "content under several encodings so the player can pick one the\n"
        "current browser supports.")
        .value("PosterImage", Wt::MediaEncoding::PosterImage,
               "Not a media source — a still image shown before playback.")
        .value("MP3",   Wt::MediaEncoding::MP3,
               "MPEG-1 Audio Layer 3.")
        .value("M4A",   Wt::MediaEncoding::M4A,
               "MPEG-4 Audio (AAC in MP4 container).")
        .value("OGA",   Wt::MediaEncoding::OGA,
               "Ogg Vorbis / Opus audio.")
        .value("WAV",   Wt::MediaEncoding::WAV,
               "Waveform audio.")
        .value("WEBMA", Wt::MediaEncoding::WEBMA,
               "WebM audio.")
        .value("FLA",   Wt::MediaEncoding::FLA,
               "Flash audio (legacy fallback).")
        .value("M4V",   Wt::MediaEncoding::M4V,
               "MPEG-4 Video.")
        .value("OGV",   Wt::MediaEncoding::OGV,
               "Ogg Theora video.")
        .value("WEBMV", Wt::MediaEncoding::WEBMV,
               "WebM video.")
        .value("FLV",   Wt::MediaEncoding::FLV,
               "Flash video (legacy fallback).");

    nb::enum_<Wt::MediaType>(m, "MediaType",
        "Which kind of player to construct.")
        .value("Audio", Wt::MediaType::Audio,
               "Audio-only player; renders a horizontal control strip.")
        .value("Video", Wt::MediaType::Video,
               "Video player; renders a video viewport with controls below.");

    nb::enum_<Wt::MediaPlayerButtonId>(m, "MediaPlayerButtonId",
        "Identifier for one of the player's built-in control buttons —\n"
        "passed to WMediaPlayer.set_button to substitute a custom widget.")
        .value("VideoPlay",     Wt::MediaPlayerButtonId::VideoPlay,
               "Large central play-overlay button for video.")
        .value("Play",          Wt::MediaPlayerButtonId::Play)
        .value("Pause",         Wt::MediaPlayerButtonId::Pause)
        .value("Stop",          Wt::MediaPlayerButtonId::Stop)
        .value("VolumeMute",    Wt::MediaPlayerButtonId::VolumeMute)
        .value("VolumeUnmute",  Wt::MediaPlayerButtonId::VolumeUnmute)
        .value("VolumeMax",     Wt::MediaPlayerButtonId::VolumeMax)
        .value("FullScreen",    Wt::MediaPlayerButtonId::FullScreen)
        .value("RestoreScreen", Wt::MediaPlayerButtonId::RestoreScreen)
        .value("RepeatOn",      Wt::MediaPlayerButtonId::RepeatOn)
        .value("RepeatOff",     Wt::MediaPlayerButtonId::RepeatOff);

    nb::enum_<Wt::MediaPlayerProgressBarId>(m, "MediaPlayerProgressBarId",
        "Identifier for one of the player's progress bars — passed to\n"
        "WMediaPlayer.set_progress_bar to substitute a custom WProgressBar.")
        .value("Time",   Wt::MediaPlayerProgressBarId::Time,
               "The seek/playback-position bar.")
        .value("Volume", Wt::MediaPlayerProgressBarId::Volume,
               "The volume-level bar.");

    nb::enum_<Wt::MediaPlayerTextId>(m, "MediaPlayerTextId",
        "Identifier for one of the player's text fields — passed to\n"
        "WMediaPlayer.set_text to substitute a custom WText.")
        .value("CurrentTime", Wt::MediaPlayerTextId::CurrentTime,
               "Display of the current playback position.")
        .value("Duration",    Wt::MediaPlayerTextId::Duration,
               "Display of the media's total duration.")
        .value("Title",       Wt::MediaPlayerTextId::Title,
               "Display of the title set via set_title.");

    // WMediaPlayer extends WCompositeWidget — bind as WWidget per project
    // convention.
    nb::class_<Wt::WMediaPlayer, Wt::WWidget>(m, "WMediaPlayer",
        "Skinned audio/video player. Unlike WAudio / WVideo (which expose\n"
        "the browser-native controls), WMediaPlayer renders its own\n"
        "control surface via jPlayer — useful when you want a consistent\n"
        "look across browsers, or need to substitute custom buttons/\n"
        "progress bars.\n"
        "\n"
        "    player = container.add_widget(wt.WMediaPlayer(wt.MediaType.Video))\n"
        "    player.add_source(wt.MediaEncoding.WEBMV, wt.WLink('/clip.webm'))\n"
        "    player.add_source(wt.MediaEncoding.M4V,   wt.WLink('/clip.mp4'))\n"
        "    player.set_title('Demo')\n"
        "    player.set_video_size(640, 360)\n"
        "    player.ended.connect(reset_panel)")
        .def(heap_init<Wt::WMediaPlayer, Wt::MediaType>(), "media_type"_a,
             "Construct an audio or video player.")
        .def("add_source", &Wt::WMediaPlayer::addSource,
             "encoding"_a, "link"_a,
             "Register a source URL for a given encoding. Add the same "
             "content under multiple encodings for cross-browser support.")
        .def("get_source", &Wt::WMediaPlayer::getSource, "encoding"_a,
             "Return the WLink registered for `encoding`, or an empty\n"
             "WLink if none was added.")
        .def("clear_sources", &Wt::WMediaPlayer::clearSources,
             "Remove every source previously added.")
        .def("set_title", &Wt::WMediaPlayer::setTitle, "title"_a,
             "Set the title shown in the player's Title text field (when\n"
             "configured to show one).")
        .def("set_video_size", &Wt::WMediaPlayer::setVideoSize,
             "width"_a, "height"_a,
             "Set the video viewport dimensions in pixels.")
        .def_prop_ro("video_width", &Wt::WMediaPlayer::videoWidth,
             "Width of the video viewport in pixels.")
        .def_prop_ro("video_height", &Wt::WMediaPlayer::videoHeight,
             "Height of the video viewport in pixels.")
        .def("play", &Wt::WMediaPlayer::play,
             "Start playback.")
        .def("pause", &Wt::WMediaPlayer::pause,
             "Pause playback.")
        .def("stop", &Wt::WMediaPlayer::stop,
             "Stop playback and return to the start.")
        .def("seek", &Wt::WMediaPlayer::seek, "time"_a,
             "Jump to `time` seconds into the media.")
        .def("set_playback_rate", &Wt::WMediaPlayer::setPlaybackRate,
             "rate"_a, "1.0 = normal; 2.0 = 2× speed; 0.5 = half-speed.")
        .def("set_volume", &Wt::WMediaPlayer::setVolume, "volume"_a,
             "0.0 (silent) to 1.0 (max).")
        .def("mute", &Wt::WMediaPlayer::mute, "mute"_a,
             "Mute (True) or unmute (False) the audio output without\n"
             "changing the configured volume.")
        .def("set_button",
            [](Wt::WMediaPlayer& self, Wt::MediaPlayerButtonId id,
               Wt::WInteractWidget* btn) {
                self.setButton(id, btn);
            },
            "id"_a, "button"_a,
            "Override the widget used for a control. The button is "
            "associated (not owned); place it in the page yourself.")
        .def("set_progress_bar",
            [](Wt::WMediaPlayer& self, Wt::MediaPlayerProgressBarId id,
               Wt::WProgressBar* bar) {
                self.setProgressBar(id, bar);
            },
            "id"_a, "progress_bar"_a,
            "Override the WProgressBar used for the Time or Volume bar.\n"
            "The bar is associated (not owned); place it in the page yourself.")
        .def("set_text",
            [](Wt::WMediaPlayer& self, Wt::MediaPlayerTextId id,
               Wt::WText* text) {
                self.setText(id, text);
            },
            "id"_a, "text"_a,
            "Override the WText used for one of the player's text displays\n"
            "(CurrentTime, Duration, Title). The widget is associated, not\n"
            "owned.")
        .def_prop_ro("playback_started",
                     &Wt::WMediaPlayer::playbackStarted,
                     nb::rv_policy::reference_internal,
                     "JSignal0 — fires when playback starts.")
        .def_prop_ro("playback_paused",
                     &Wt::WMediaPlayer::playbackPaused,
                     nb::rv_policy::reference_internal,
                     "JSignal0 — fires when playback pauses.")
        .def_prop_ro("ended",
                     &Wt::WMediaPlayer::ended,
                     nb::rv_policy::reference_internal,
                     "JSignal0 — fires when the media reaches its end.")
        .def_prop_ro("time_updated",
                     &Wt::WMediaPlayer::timeUpdated,
                     nb::rv_policy::reference_internal,
                     "JDoubleSignal — fires periodically with the current "
                     "playback time in seconds.")
        .def_prop_ro("volume_changed",
                     &Wt::WMediaPlayer::volumeChanged,
                     nb::rv_policy::reference_internal,
                     "JDoubleSignal — fires when volume changes; payload "
                     "is the new volume (0.0–1.0).");

    // Inherits WObject (not a widget). Pre-load short audio clips for
    // sound effects, alarms, notifications. For long-form playback use
    // WAudio or WMediaPlayer.

    nb::class_<Wt::WSound, Wt::WObject>(m, "WSound",
        "A simple sound-effect player — short, fire-and-forget audio\n"
        "playback with no visible UI. Inherits WObject (not a widget),\n"
        "so it's not added to a container; just construct, configure\n"
        "sources, and call `play`.\n"
        "\n"
        "    chime = wt.WSound()\n"
        "    chime.add_source(wt.MediaEncoding.MP3, wt.WLink('/ding.mp3'))\n"
        "    chime.loops = 1\n"
        "    container.add_widget(wt.WPushButton('Ding')).clicked.connect(chime.play)\n"
        "\n"
        "For long-form streaming, user-driven playback controls, or video\n"
        "use WAudio / WVideo / WMediaPlayer instead.")
        .def(heap_init<Wt::WSound>(),
             "Construct an empty sound. Add sources before calling play.")
        .def("add_source", &Wt::WSound::addSource,
             "encoding"_a, "link"_a,
             "Register a source URL for a given encoding. Add the same\n"
             "clip in multiple encodings for cross-browser support.")
        .def("get_source", &Wt::WSound::getSource, "encoding"_a,
             "Return the WLink registered for `encoding`, or an empty\n"
             "WLink if none was added.")
        .def_prop_rw("loops",
            &Wt::WSound::loops,
            &Wt::WSound::setLoops,
            "Number of times to repeat the clip. 0 = infinite.")
        .def("play", &Wt::WSound::play,
             "Play the sound. Starts from the beginning each time.")
        .def("stop", &Wt::WSound::stop,
             "Stop any currently-playing playback.");
}

}  // namespace witty_for_python
