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

    nb::class_<Wt::JSignal<double>>(m, "JDoubleSignal")
        .def("connect",
            [](Wt::JSignal<double>& s, nb::callable cb) {
                return py_connect<Wt::JSignal<double>, double>(s, std::move(cb));
            }, "callable"_a)
        .def("disconnect_all_slots",
            [](Wt::JSignal<double>& s) {
                connection_registry_disconnect_all(&s);
            });

    // ---- Enums (WAbstractMedia) ----

    nb::enum_<Wt::PlayerOption>(m, "PlayerOption", nb::is_arithmetic())
        .value("Autoplay", Wt::PlayerOption::Autoplay)
        .value("Loop",     Wt::PlayerOption::Loop)
        .value("Controls", Wt::PlayerOption::Controls);

    nb::enum_<Wt::MediaPreloadMode>(m, "MediaPreloadMode")
        .value("None_",    Wt::MediaPreloadMode::None)
        .value("Auto",     Wt::MediaPreloadMode::Auto)
        .value("Metadata", Wt::MediaPreloadMode::Metadata);

    // ---- WAbstractMedia (abstract base for WAudio / WVideo) ----
    //
    // Wraps an HTML5 <audio> / <video> element. Accepts multiple sources
    // (the browser picks the first format it can play). The five EventSignals
    // are bound as `..._signal` accessors so they don't clash with the
    // play()/pause()/playing keyword-ish names.

    nb::class_<Wt::WAbstractMedia, Wt::WInteractWidget>(m, "WAbstractMedia")
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
        .def("clear_sources", &Wt::WAbstractMedia::clearSources)
        .def("set_alternative_content",
            [](Wt::WAbstractMedia& self,
               std::unique_ptr<Wt::WWidget> alt) {
                self.setAlternativeContent(std::move(alt));
            },
            "widget"_a,
            "Widget shown to users whose browser can't play any of the "
            "configured sources. Ownership transfers; the wrapper becomes "
            "non-owning.")
        .def("set_options",
            [](Wt::WAbstractMedia& self, int options) {
                self.setOptions(Wt::WFlags<Wt::PlayerOption>(
                    static_cast<Wt::PlayerOption>(options)));
            },
            "options"_a,
            "Bitwise-OR of PlayerOption values (Autoplay | Loop | Controls).")
        .def("set_preload_mode", &Wt::WAbstractMedia::setPreloadMode,
             "mode"_a)
        .def("play", &Wt::WAbstractMedia::play,
             "Start playback. No-op if already playing.")
        .def("pause", &Wt::WAbstractMedia::pause)
        .def_prop_ro("playing", &Wt::WAbstractMedia::playing,
             "True iff the media element is currently playing.")
        .def_prop_ro("playback_started",
                     &Wt::WAbstractMedia::playbackStarted,
                     nb::rv_policy::reference_internal,
                     "EventSignal[] — fires when playback begins.")
        .def_prop_ro("playback_paused",
                     &Wt::WAbstractMedia::playbackPaused,
                     nb::rv_policy::reference_internal)
        .def_prop_ro("ended",
                     &Wt::WAbstractMedia::ended,
                     nb::rv_policy::reference_internal)
        .def_prop_ro("time_updated",
                     &Wt::WAbstractMedia::timeUpdated,
                     nb::rv_policy::reference_internal,
                     "EventSignal[] — fires periodically (~4×/sec by "
                     "browser convention) during playback.")
        .def_prop_ro("volume_changed",
                     &Wt::WAbstractMedia::volumeChanged,
                     nb::rv_policy::reference_internal);

    // ---- WAudio ----

    nb::class_<Wt::WAudio, Wt::WAbstractMedia>(m, "WAudio")
        .def(nb::init<>());

    // ---- WVideo ----

    nb::class_<Wt::WVideo, Wt::WAbstractMedia>(m, "WVideo")
        .def(nb::init<>())
        .def("set_poster", &Wt::WVideo::setPoster, "url"_a,
             "URL of a thumbnail shown before playback starts (HTML "
             "`poster` attribute).");

    // ---- WMediaPlayer (full-featured player with skinned controls) ----
    //
    // Different from WAudio/WVideo: provides Wt-rendered playback
    // controls instead of relying on the browser's defaults. Uses
    // jPlayer under the hood for cross-browser support.

    nb::enum_<Wt::MediaEncoding>(m, "MediaEncoding")
        .value("PosterImage", Wt::MediaEncoding::PosterImage)
        .value("MP3",   Wt::MediaEncoding::MP3)
        .value("M4A",   Wt::MediaEncoding::M4A)
        .value("OGA",   Wt::MediaEncoding::OGA)
        .value("WAV",   Wt::MediaEncoding::WAV)
        .value("WEBMA", Wt::MediaEncoding::WEBMA)
        .value("FLA",   Wt::MediaEncoding::FLA)
        .value("M4V",   Wt::MediaEncoding::M4V)
        .value("OGV",   Wt::MediaEncoding::OGV)
        .value("WEBMV", Wt::MediaEncoding::WEBMV)
        .value("FLV",   Wt::MediaEncoding::FLV);

    nb::enum_<Wt::MediaType>(m, "MediaType")
        .value("Audio", Wt::MediaType::Audio)
        .value("Video", Wt::MediaType::Video);

    nb::enum_<Wt::MediaPlayerButtonId>(m, "MediaPlayerButtonId")
        .value("VideoPlay",     Wt::MediaPlayerButtonId::VideoPlay)
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

    nb::enum_<Wt::MediaPlayerProgressBarId>(m, "MediaPlayerProgressBarId")
        .value("Time",   Wt::MediaPlayerProgressBarId::Time)
        .value("Volume", Wt::MediaPlayerProgressBarId::Volume);

    nb::enum_<Wt::MediaPlayerTextId>(m, "MediaPlayerTextId")
        .value("CurrentTime", Wt::MediaPlayerTextId::CurrentTime)
        .value("Duration",    Wt::MediaPlayerTextId::Duration)
        .value("Title",       Wt::MediaPlayerTextId::Title);

    // WMediaPlayer extends WCompositeWidget — bind as WWidget per project
    // convention.
    nb::class_<Wt::WMediaPlayer, Wt::WWidget>(m, "WMediaPlayer")
        .def(nb::init<Wt::MediaType>(), "media_type"_a,
             "Construct an audio or video player.")
        .def("add_source", &Wt::WMediaPlayer::addSource,
             "encoding"_a, "link"_a,
             "Register a source URL for a given encoding. Add the same "
             "content under multiple encodings for cross-browser support.")
        .def("get_source", &Wt::WMediaPlayer::getSource, "encoding"_a)
        .def("clear_sources", &Wt::WMediaPlayer::clearSources)
        .def("set_title", &Wt::WMediaPlayer::setTitle, "title"_a)
        .def("set_video_size", &Wt::WMediaPlayer::setVideoSize,
             "width"_a, "height"_a)
        .def_prop_ro("video_width", &Wt::WMediaPlayer::videoWidth)
        .def_prop_ro("video_height", &Wt::WMediaPlayer::videoHeight)
        .def("play", &Wt::WMediaPlayer::play)
        .def("pause", &Wt::WMediaPlayer::pause)
        .def("stop", &Wt::WMediaPlayer::stop)
        .def("seek", &Wt::WMediaPlayer::seek, "time"_a,
             "Jump to `time` seconds into the media.")
        .def("set_playback_rate", &Wt::WMediaPlayer::setPlaybackRate,
             "rate"_a, "1.0 = normal; 2.0 = 2× speed; 0.5 = half-speed.")
        .def("set_volume", &Wt::WMediaPlayer::setVolume, "volume"_a,
             "0.0 (silent) to 1.0 (max).")
        .def("mute", &Wt::WMediaPlayer::mute, "mute"_a)
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
            "id"_a, "progress_bar"_a)
        .def("set_text",
            [](Wt::WMediaPlayer& self, Wt::MediaPlayerTextId id,
               Wt::WText* text) {
                self.setText(id, text);
            },
            "id"_a, "text"_a)
        .def_prop_ro("playback_started",
                     &Wt::WMediaPlayer::playbackStarted,
                     nb::rv_policy::reference_internal,
                     "JSignal0 — fires when playback starts.")
        .def_prop_ro("playback_paused",
                     &Wt::WMediaPlayer::playbackPaused,
                     nb::rv_policy::reference_internal)
        .def_prop_ro("ended",
                     &Wt::WMediaPlayer::ended,
                     nb::rv_policy::reference_internal)
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

    // ---- WSound: simple sound-effect player ----
    //
    // Inherits WObject (not a widget). Pre-load short audio clips for
    // sound effects, alarms, notifications. For long-form playback use
    // WAudio or WMediaPlayer.

    nb::class_<Wt::WSound, Wt::WObject>(m, "WSound")
        .def(nb::init<>())
        .def("add_source", &Wt::WSound::addSource,
             "encoding"_a, "link"_a)
        .def("get_source", &Wt::WSound::getSource, "encoding"_a)
        .def_prop_rw("loops",
            &Wt::WSound::loops,
            &Wt::WSound::setLoops,
            "Number of times to repeat the clip. 0 = infinite.")
        .def("play", &Wt::WSound::play)
        .def("stop", &Wt::WSound::stop);
}

}  // namespace witty_for_python
