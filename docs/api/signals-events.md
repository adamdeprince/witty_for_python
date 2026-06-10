# Signals & Events

> Wt's signal/slot machinery, the Connection handle, and the event payloads carried by DOM-level signals (mouse, key, touch, gesture, scroll, drag/drop).

**Classes in this section:**

- [`Connection`](#Connection)
- [`Signal`](#Signal)
- [`IntSignal`](#IntSignal)
- [`BoolSignal`](#BoolSignal)
- [`DoubleSignal`](#DoubleSignal)
- [`StringSignal`](#StringSignal)
- [`EventSignal`](#EventSignal)
- [`MouseEventSignal`](#MouseEventSignal)
- [`KeyEventSignal`](#KeyEventSignal)
- [`JSignal0`](#JSignal0)
- [`JIntSignal`](#JIntSignal)
- [`JInt64Signal`](#JInt64Signal)
- [`JDoubleSignal`](#JDoubleSignal)
- [`Uint64PairSignal`](#Uint64PairSignal)
- [`Coordinates`](#Coordinates)
- [`MouseButton`](#MouseButton)
- [`KeyboardModifier`](#KeyboardModifier)
- [`Key`](#Key)
- [`WMouseEvent`](#WMouseEvent)
- [`WKeyEvent`](#WKeyEvent)
- [`Touch`](#Touch)
- [`WTouchEvent`](#WTouchEvent)
- [`WGestureEvent`](#WGestureEvent)
- [`WScrollEvent`](#WScrollEvent)
- [`DropEventOriginalEventType`](#DropEventOriginalEventType)
- [`WDropEvent`](#WDropEvent)

<!-- topic 'signals-events' lists unresolved class names: JSignal -->

---

### Connection {#Connection}

Handle to a signal subscription returned by `Signal.connect`.
Keep it if you need to disconnect later; otherwise discard.

    conn = button.clicked.connect(on_click)
    ...
    conn.disconnect()                    # stop receiving

**Methods**

- `disconnect(self) -> None`
  Drop the subscription. The connected callback won't be
  invoked again for new emits. Idempotent.

- `is_connected(self) -> bool`
  True until `disconnect` is called or the signal is destroyed.

### Signal {#Signal}

Zero-payload signal. Construct standalone for ad-hoc pub/sub,
or use the no-arg signals already on widgets.

    s = wt.Signal()
    s.connect(lambda: print('fired'))
    s.emit()

**Constructors**

- `__init__(self) -> None`
  Construct a fresh signal with no subscribers.

**Methods**

- `connect(self, callable: Callable) -> Connection`
  Subscribe `callable()` to this signal. Returns a Connection;
  the callable runs on each `emit`.

- `emit(self) -> None`
  Fire the signal — every connected callable is invoked once,
  in connection order.

- `disconnect_all_slots(self) -> None`
  Drop every connection opened through `connect`. Used by the
  library's shutdown handler; most code doesn't need it.

### IntSignal {#IntSignal}

Signal carrying a single int payload.

    s = wt.IntSignal()
    s.connect(lambda n: print(f'got {n}'))
    s.emit(42)

**Constructors**

- `__init__(self) -> None`
  Construct a fresh signal with no subscribers.

**Methods**

- `connect(self, callable: Callable) -> Connection`
  Subscribe `callable(int)` to this signal. A zero-arg
  callable also works — the payload is dropped.

- `emit(self, arg: int, /) -> None`
  Fire the signal with the given int payload.

- `disconnect_all_slots(self) -> None`
  Drop every connection opened through `connect`.

### BoolSignal {#BoolSignal}

Signal carrying a single bool payload.

**Constructors**

- `__init__(self) -> None`
  Construct a fresh signal with no subscribers.

**Methods**

- `connect(self, callable: Callable) -> Connection`
  Subscribe `callable(bool)` to this signal.

- `emit(self, arg: bool, /) -> None`
  Fire the signal with the given bool payload.

- `disconnect_all_slots(self) -> None`
  Drop every connection opened through `connect`.

### DoubleSignal {#DoubleSignal}

Signal carrying a single float payload.

**Constructors**

- `__init__(self) -> None`
  Construct a fresh signal with no subscribers.

**Methods**

- `connect(self, callable: Callable) -> Connection`
  Subscribe `callable(float)` to this signal.

- `emit(self, arg: float, /) -> None`
  Fire the signal with the given float payload.

- `disconnect_all_slots(self) -> None`
  Drop every connection opened through `connect`.

### StringSignal {#StringSignal}

Signal carrying a single string payload.

**Constructors**

- `__init__(self) -> None`
  Construct a fresh signal with no subscribers.

**Methods**

- `connect(self, callable: Callable) -> Connection`
  Subscribe `callable(str)` to this signal.

- `emit(self, arg: str, /) -> None`
  Fire the signal with the given string payload.

- `disconnect_all_slots(self) -> None`
  Drop every connection opened through `connect`.

### EventSignal {#EventSignal}

Zero-payload signal backing DOM events (e.g. WCheckBox.on_check,
WInteractWidget.enter_pressed). Like Signal but with no public
constructor — the widget owns the instance and exposes it as a
property.

    container.add_widget(wt.WCheckBox('OK')).on_check.connect(handler)

**Methods**

- `connect(self, callable: Callable) -> Connection`
  Subscribe `callable()` to this DOM event. Returns a Connection.

- `disconnect_all_slots(self) -> None`
  Drop every connection opened through `connect`.

### MouseEventSignal {#MouseEventSignal}

DOM-event signal carrying a WMouseEvent payload. Backs the
`clicked` / `double_clicked` / `mouse_over` / `mouse_out` props
on WInteractWidget.

    button.clicked.connect(lambda e: print(e.button))

**Methods**

- `connect(self, callable: Callable) -> Connection`
  Subscribe `callable(WMouseEvent)`. A zero-arg callable also
  works — the payload is dropped.

- `disconnect_all_slots(self) -> None`
  Drop every connection opened through `connect`.

### KeyEventSignal {#KeyEventSignal}

DOM-event signal carrying a WKeyEvent payload. Backs the
`key_pressed` / `key_went_down` props on WInteractWidget.

    field.key_went_down.connect(
        lambda e: dialog.hide() if e.key == wt.Key.Escape else None)

**Methods**

- `connect(self, callable: Callable) -> Connection`
  Subscribe `callable(WKeyEvent)`. Zero-arg also works.

- `disconnect_all_slots(self) -> None`
  Drop every connection opened through `connect`.

### JSignal0 {#JSignal0}

Parameterless JavaScript signal — a Wt::JSignal<> bridged for
Python. Fires when the corresponding client-side JS event happens
(e.g. WNotification's clicked/closed/shown/error).

**Methods**

- `connect(self, callable: Callable) -> Connection`
  Subscribe a no-arg callable. Returns a Connection — call
  `.disconnect()` to stop receiving.

- `disconnect_all_slots(self) -> None`
  Drop every Python subscriber attached via `connect`.

### JIntSignal {#JIntSignal}

JavaScript-emitted signal carrying an int. Like IntSignal but
originates on the browser side and travels back to the server.
Used for widgets where the client emits semantic events (e.g.
WLeafletMap.zoom_level_changed).

**Methods**

- `connect(self, callable: Callable) -> Connection`
  Subscribe `callable(int)` to client-side emits.

- `disconnect_all_slots(self) -> None`
  Drop every connection opened through `connect`.

### JInt64Signal {#JInt64Signal}

JavaScript-emitted signal carrying a 64-bit int — used where
byte sizes don't fit in 32 bits (e.g. WFileUpload.file_too_large
reporting the rejected upload's size).

**Methods**

- `connect(self, callable: Callable) -> Connection`
  Subscribe `callable(int)` to client-side emits.

- `disconnect_all_slots(self) -> None`
  Drop every connection opened through `connect`.

### JDoubleSignal {#JDoubleSignal}

JavaScript signal carrying a single double payload. Used by
WMediaPlayer.time_updated (current playback time in seconds) and
WMediaPlayer.volume_changed (volume in 0.0-1.0).

**Methods**

- `connect(self, callable: Callable) -> Connection`
  Subscribe a callable taking a float. Returns a Connection —
  call `.disconnect()` to stop receiving.

- `disconnect_all_slots(self) -> None`
  Drop every Python subscriber attached via `connect`.

### Uint64PairSignal {#Uint64PairSignal}

Signal carrying a (uint64, uint64) pair — typically a
progress tick reporting (bytes received, total bytes) on
WFileUpload and WFileDropWidget.

    upload.data_received.connect(
        lambda recv, total: bar.set_value(100 * recv / total))

**Methods**

- `connect(self, callable: Callable) -> Connection`
  Subscribe `callable(received, total)`. Either both ints or
  zero args; intermediate arities are an error.

- `disconnect_all_slots(self) -> None`
  Drop every connection opened through `connect`.

### Coordinates {#Coordinates}

An (x, y) pixel pair, used wherever an event reports a position
(WMouseEvent.document, .window, .screen, .widget). Plain value
type — construct directly if you need to synthesize one.

**Constructors**

- `__init__(self, x: int, y: int) -> None`
  Construct a Coordinates with the given pixel offsets.

**Properties**

- `x: int` *(read/write)*
  Horizontal offset in pixels.

- `y: int` *(read/write)*
  Vertical offset in pixels.

**Dunder methods**

- `__repr__(self) -> str`

### MouseButton {#MouseButton}

*Inherits:* `enum.IntEnum`

Mouse button identifier surfaced on WMouseEvent.button. None_
is the no-button case (e.g. a pure move event); the trailing
underscore avoids a clash with the Python `None` literal.

### KeyboardModifier {#KeyboardModifier}

*Inherits:* `enum.IntEnum`

Keyboard-modifier bit; combine via bitwise OR to express
compound chords. Surfaced as an int bitmask on event payloads
(WMouseEvent.modifiers, WKeyEvent.modifiers).

### Key {#Key}

*Inherits:* `enum.IntEnum`

Symbolic key codes surfaced on WKeyEvent.key. Use these to
match non-printable keys (Enter, arrows, F-keys, …); printable
characters are easier to handle via `WKeyEvent.char_code`.

### WMouseEvent {#WMouseEvent}

Payload delivered to mouse-event handlers (clicked,
double_clicked, mouse_over, mouse_out, wheel events).

    def on_click(e: wt.WMouseEvent):
        if e.button == wt.MouseButton.Right:
            show_context_menu(e.widget.x, e.widget.y)
    button.clicked.connect(on_click)

The four coordinate properties report the cursor's position in
different reference frames — use whichever frame your math is in.

**Properties**

- `button: MouseButton` *(read-only)*
  MouseButton that triggered the event (None_ for pure-move).

- `modifiers: int` *(read-only)*
  Int bitmask of KeyboardModifier values held during the event.

- `document: Coordinates` *(read-only)*
  Cursor position relative to the document's top-left corner.

- `window: Coordinates` *(read-only)*
  Cursor position relative to the browser window's top-left
  (equivalent to viewport coordinates).

- `screen: Coordinates` *(read-only)*
  Cursor position relative to the user's screen.

- `widget: Coordinates` *(read-only)*
  Cursor position relative to the widget that fired the event
  — most useful for picking inside the widget's own geometry.

- `wheel_delta: int` *(read-only)*
  Signed wheel ticks for wheel events (positive = up). Zero
  for non-wheel events.

### WKeyEvent {#WKeyEvent}

Payload delivered to keyboard-event handlers (key_pressed,
key_went_down, enter_pressed).

    def on_key(e: wt.WKeyEvent):
        if e.key == wt.Key.Escape:
            dialog.hide()
    dialog.key_went_down.connect(on_key)

**Properties**

- `key: Key` *(read-only)*
  Symbolic Key value — use to match non-printable keys.

- `char_code: int` *(read-only)*
  Unicode code point of the printable character pressed, or 0
  for non-printable keys. Easier than `key` for typed-text logic.

- `modifiers: int` *(read-only)*
  Int bitmask of KeyboardModifier values held during the event.

### Touch {#Touch}

A single finger contact on a touch-capable device. Bundled
inside the `touches` / `target_touches` / `changed_touches`
lists on a WTouchEvent. Read the four coordinate accessors to
get the contact position in different reference frames.

**Methods**

- `document(self) -> Coordinates`
  Touch position relative to the document, as Coordinates.

- `window(self) -> Coordinates`
  Touch position relative to the visible window.

- `screen(self) -> Coordinates`
  Touch position relative to the physical screen.

- `widget(self) -> Coordinates`
  Touch position relative to the target widget.

### WTouchEvent {#WTouchEvent}

Payload delivered to touch-related event signals. Splits the
active touches into three views: every finger on the screen,
only the fingers whose touch started on the target widget, and
the subset of fingers that changed state in the event firing.

**Properties**

- `touches: list[Touch]` *(read-only)*
  List[Touch] — every finger currently touching the screen.

- `target_touches: list[Touch]` *(read-only)*
  List[Touch] — fingers whose touch started inside this widget.

- `changed_touches: list[Touch]` *(read-only)*
  List[Touch] — fingers whose state changed in this event.

### WGestureEvent {#WGestureEvent}

Payload for multi-touch pinch and rotate gestures. `scale`
compares the current finger spread to the start of the gesture
(1.0 means unchanged, >1 a pinch-out, <1 a pinch-in); `rotation`
is the angular delta in degrees.

**Properties**

- `scale: float` *(read-only)*
  Pinch scale relative to the gesture's start (1.0 = no
  change, >1 zoomed out, <1 zoomed in).

- `rotation: float` *(read-only)*
  Rotation in degrees relative to the gesture's start.

### WScrollEvent {#WScrollEvent}

Payload for scroll-position changes. Reports the current scroll
offset of the scrolling element together with the viewport
dimensions, all in CSS pixels.

**Properties**

- `scroll_x: int` *(read-only)*
  Horizontal scroll offset in pixels.

- `scroll_y: int` *(read-only)*
  Vertical scroll offset in pixels.

- `viewport_width: int` *(read-only)*
  Visible viewport width in pixels.

- `viewport_height: int` *(read-only)*
  Visible viewport height in pixels.

### DropEventOriginalEventType {#DropEventOriginalEventType}

*Inherits:* `enum.Enum`

### WDropEvent {#WDropEvent}

Payload delivered to a target widget when something is dropped
on it. Carries a reference to the source object, the MIME type
of the dragged data, and the underlying pointer event — either
a WMouseEvent or a WTouchEvent depending on the input device.

Inspect `event_type` first to decide which of `mouse_event` /
`touch_event` is populated; the other is None.

**Properties**

- `source: WObject` *(read-only)*
  The WObject that was the drag source. Don't outlive the slot call — the pointer's lifetime is the source widget's.

- `mime_type: str` *(read-only)*
  MIME type of the dragged data, as published by the drag
  source.

- `event_type: DropEventOriginalEventType` *(read-only)*
  DropEventOriginalEventType — whether the drop originated from a mouse or a touch event.

- `mouse_event: WMouseEvent` *(read-only)*
  The originating WMouseEvent, or None when event_type is Touch.

- `touch_event: WTouchEvent` *(read-only)*
  The originating WTouchEvent, or None when event_type is Mouse.
