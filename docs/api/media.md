# Media

> HTML5 audio and video, the skinned WMediaPlayer, and the play-once WSound.

**Classes in this section:**

- [`PlayerOption`](#PlayerOption)
- [`MediaPreloadMode`](#MediaPreloadMode)
- [`MediaEncoding`](#MediaEncoding)
- [`MediaType`](#MediaType)
- [`MediaPlayerButtonId`](#MediaPlayerButtonId)
- [`MediaPlayerProgressBarId`](#MediaPlayerProgressBarId)
- [`MediaPlayerTextId`](#MediaPlayerTextId)
- [`WAbstractMedia`](#WAbstractMedia)
- [`WAudio`](#WAudio)
- [`WVideo`](#WVideo)
- [`WMediaPlayer`](#WMediaPlayer)
- [`WSound`](#WSound)

---

### PlayerOption {#PlayerOption}

*Inherits:* `enum.IntEnum`

Bitfield of HTML5 media element flags. OR values together when
passing to WAbstractMedia.set_options.

### MediaPreloadMode {#MediaPreloadMode}

*Inherits:* `enum.Enum`

How aggressively the browser preloads media before playback —
maps to the HTML5 `preload` attribute.

### MediaEncoding {#MediaEncoding}

*Inherits:* `enum.Enum`

Encoding label for WMediaPlayer.add_source. Add the same logical
content under several encodings so the player can pick one the
current browser supports.

### MediaType {#MediaType}

*Inherits:* `enum.Enum`

Which kind of player to construct.

### MediaPlayerButtonId {#MediaPlayerButtonId}

*Inherits:* `enum.Enum`

Identifier for one of the player's built-in control buttons —
passed to WMediaPlayer.set_button to substitute a custom widget.

### MediaPlayerProgressBarId {#MediaPlayerProgressBarId}

*Inherits:* `enum.Enum`

Identifier for one of the player's progress bars — passed to
WMediaPlayer.set_progress_bar to substitute a custom WProgressBar.

### MediaPlayerTextId {#MediaPlayerTextId}

*Inherits:* `enum.Enum`

Identifier for one of the player's text fields — passed to
WMediaPlayer.set_text to substitute a custom WText.

### WAbstractMedia {#WAbstractMedia}

*Inherits:* `WInteractWidget`

Abstract base for WAudio and WVideo — wraps an HTML5 `<audio>`
or `<video>` element and exposes the standard playback API
(play / pause / volume / preload) along with the matching
EventSignals.

    video = container.add_widget(wt.WVideo())
    video.add_source(wt.WLink('/clip.webm'), 'video/webm')
    video.set_options(int(wt.PlayerOption.Controls)
                      | int(wt.PlayerOption.Loop))
    video.ended.connect(reset_panel)

Add several sources for cross-browser support; the browser will
use the first one it knows how to decode based on the optional
MIME-type hint.

**Properties**

- `playing: bool` *(read-only)*
  True iff the media element is currently playing.

- `playback_started: EventSignal` *(read-only)*
  EventSignal[] — fires when playback begins.

- `playback_paused: EventSignal` *(read-only)*
  EventSignal[] — fires when playback is paused.

- `ended: EventSignal` *(read-only)*
  EventSignal[] — fires when the media reaches the end
  (does not fire on Loop=True).

- `time_updated: EventSignal` *(read-only)*
  EventSignal[] — fires periodically (~4×/sec by browser convention) during playback.

- `volume_changed: EventSignal` *(read-only)*
  EventSignal[] — fires when the user changes the
  volume via the browser controls.

**Methods**

- `add_source(self, source: WLink, mime_type: str = '', media: str = '') -> None`
  Add a source URL (via WLink). `mime_type` is the content-type hint the browser uses to pick a source; `media` is a CSS media query (e.g. 'screen and (min-width: 600px)').

- `clear_sources(self) -> None`
  Remove every source previously added.

- `set_alternative_content(self, widget: WWidget) -> None`
  Widget shown to users whose browser can't play any of the configured sources. Ownership transfers; the wrapper is re-armed as a non-owning alias.

- `set_options(self, options: int) -> None`
  Bitwise-OR of PlayerOption values (Autoplay | Loop | Controls).

- `set_preload_mode(self, mode: MediaPreloadMode) -> None`
  Set the browser's preload behavior (None_ / Metadata / Auto).

- `play(self) -> None`
  Start playback. No-op if already playing.

- `pause(self) -> None`
  Pause playback. No-op if already paused.

### WAudio {#WAudio}

*Inherits:* `WAbstractMedia`

HTML5 `<audio>` element. Wraps the browser's built-in audio
playback — set sources via the inherited add_source, then either
show the browser controls (PlayerOption.Controls) or drive play()
/ pause() from Python.

    audio = container.add_widget(wt.WAudio())
    audio.add_source(wt.WLink('/clip.mp3'), 'audio/mpeg')
    audio.set_options(int(wt.PlayerOption.Controls))

**Constructors**

- `__init__(self) -> None`
  Construct an empty audio element. Add sources before adding
  to a container.

### WVideo {#WVideo}

*Inherits:* `WAbstractMedia`

HTML5 `<video>` element. Same API as WAudio but renders a video
viewport — combine with `set_poster` for a still-image preview
shown before playback begins.

    video = container.add_widget(wt.WVideo())
    video.add_source(wt.WLink('/clip.webm'), 'video/webm')
    video.add_source(wt.WLink('/clip.mp4'), 'video/mp4')
    video.set_poster('/thumb.jpg')
    video.set_options(int(wt.PlayerOption.Controls))

**Constructors**

- `__init__(self) -> None`
  Construct an empty video element. Add sources before adding
  to a container.

**Methods**

- `set_poster(self, url: str) -> None`
  URL of a thumbnail shown before playback starts (HTML `poster` attribute).

### WMediaPlayer {#WMediaPlayer}

*Inherits:* `WWidget`

Skinned audio/video player. Unlike WAudio / WVideo (which expose
the browser-native controls), WMediaPlayer renders its own
control surface via jPlayer — useful when you want a consistent
look across browsers, or need to substitute custom buttons/
progress bars.

    player = container.add_widget(wt.WMediaPlayer(wt.MediaType.Video))
    player.add_source(wt.MediaEncoding.WEBMV, wt.WLink('/clip.webm'))
    player.add_source(wt.MediaEncoding.M4V,   wt.WLink('/clip.mp4'))
    player.set_title('Demo')
    player.set_video_size(640, 360)
    player.ended.connect(reset_panel)

**Constructors**

- `__init__(self, media_type: MediaType) -> None`
  Construct an audio or video player.

**Properties**

- `video_width: int` *(read-only)*
  Width of the video viewport in pixels.

- `video_height: int` *(read-only)*
  Height of the video viewport in pixels.

- `playback_started: JSignal0` *(read-only)*
  JSignal0 — fires when playback starts.

- `playback_paused: JSignal0` *(read-only)*
  JSignal0 — fires when playback pauses.

- `ended: JSignal0` *(read-only)*
  JSignal0 — fires when the media reaches its end.

- `time_updated: JDoubleSignal` *(read-only)*
  JDoubleSignal — fires periodically with the current playback time in seconds.

- `volume_changed: JDoubleSignal` *(read-only)*
  JDoubleSignal — fires when volume changes; payload is the new volume (0.0–1.0).

**Methods**

- `add_source(self, encoding: MediaEncoding, link: WLink) -> None`
  Register a source URL for a given encoding. Add the same content under multiple encodings for cross-browser support.

- `get_source(self, encoding: MediaEncoding) -> WLink`
  Return the WLink registered for `encoding`, or an empty
  WLink if none was added.

- `clear_sources(self) -> None`
  Remove every source previously added.

- `set_title(self, title: str) -> None`
  Set the title shown in the player's Title text field (when
  configured to show one).

- `set_video_size(self, width: int, height: int) -> None`
  Set the video viewport dimensions in pixels.

- `play(self) -> None`
  Start playback.

- `pause(self) -> None`
  Pause playback.

- `stop(self) -> None`
  Stop playback and return to the start.

- `seek(self, time: float) -> None`
  Jump to `time` seconds into the media.

- `set_playback_rate(self, rate: float) -> None`
  1.0 = normal; 2.0 = 2× speed; 0.5 = half-speed.

- `set_volume(self, volume: float) -> None`
  0.0 (silent) to 1.0 (max).

- `mute(self, mute: bool) -> None`
  Mute (True) or unmute (False) the audio output without
  changing the configured volume.

- `set_button(self, id: MediaPlayerButtonId, button: WInteractWidget) -> None`
  Override the widget used for a control. The button is associated (not owned); place it in the page yourself.

- `set_progress_bar(self, id: MediaPlayerProgressBarId, progress_bar: WProgressBar) -> None`
  Override the WProgressBar used for the Time or Volume bar.
  The bar is associated (not owned); place it in the page yourself.

- `set_text(self, id: MediaPlayerTextId, text: WText) -> None`
  Override the WText used for one of the player's text displays
  (CurrentTime, Duration, Title). The widget is associated, not
  owned.

### WSound {#WSound}

*Inherits:* `WObject`

A simple sound-effect player — short, fire-and-forget audio
playback with no visible UI. Inherits WObject (not a widget),
so it's not added to a container; just construct, configure
sources, and call `play`.

    chime = wt.WSound()
    chime.add_source(wt.MediaEncoding.MP3, wt.WLink('/ding.mp3'))
    chime.loops = 1
    container.add_widget(wt.WPushButton('Ding')).clicked.connect(chime.play)

For long-form streaming, user-driven playback controls, or video
use WAudio / WVideo / WMediaPlayer instead.

**Constructors**

- `__init__(self) -> None`
  Construct an empty sound. Add sources before calling play.

**Properties**

- `loops: int` *(read/write)*
  Number of times to repeat the clip. 0 = infinite.

**Methods**

- `add_source(self, encoding: MediaEncoding, link: WLink) -> None`
  Register a source URL for a given encoding. Add the same
  clip in multiple encodings for cross-browser support.

- `get_source(self, encoding: MediaEncoding) -> WLink`
  Return the WLink registered for `encoding`, or an empty
  WLink if none was added.

- `play(self) -> None`
  Play the sound. Starts from the beginning each time.

- `stop(self) -> None`
  Stop any currently-playing playback.
