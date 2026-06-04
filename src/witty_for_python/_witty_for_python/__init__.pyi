"""Python bindings for the Wt (Web Toolkit) C++ library."""

from collections.abc import Callable, Sequence
import datetime
import enum
from typing import TypeVar, TypeAlias, overload

_T_Area = TypeVar("_T_Area", bound=WAbstractArea)
_T_Button = TypeVar("_T_Button", bound=WInteractWidget)
_T_LineEdit = TypeVar("_T_LineEdit", bound=WLineEdit)
_T_Marker = TypeVar("_T_Marker", bound=WLeafletMap.Marker)
_T_Menu = TypeVar("_T_Menu", bound=WMenu)
_T_MenuItem = TypeVar("_T_MenuItem", bound=WMenuItem)
_T_Popup = TypeVar("_T_Popup", bound=WLeafletMap.Popup)
_T_Tooltip = TypeVar("_T_Tooltip", bound=WLeafletMap.Tooltip)
_T_Widget = TypeVar("_T_Widget", bound=WWidget)


from . import Http as Http, Json as Json, chart as chart


class Coordinates:
    """
    An (x, y) pixel pair, used wherever an event reports a position
    (WMouseEvent.document, .window, .screen, .widget). Plain value
    type — construct directly if you need to synthesize one.
    """

    def __init__(self, x: int, y: int) -> None:
        """Construct a Coordinates with the given pixel offsets."""

    @property
    def x(self) -> int:
        """Horizontal offset in pixels."""

    @x.setter
    def x(self, arg: int, /) -> None: ...

    @property
    def y(self) -> int:
        """Vertical offset in pixels."""

    @y.setter
    def y(self, arg: int, /) -> None: ...

    def __repr__(self) -> str: ...

class MouseButton(enum.IntEnum):
    """
    Mouse button identifier surfaced on WMouseEvent.button. None_
    is the no-button case (e.g. a pure move event); the trailing
    underscore avoids a clash with the Python `None` literal.
    """

    Left = 1

    Middle = 2

    Right = 4

class KeyboardModifier(enum.IntEnum):
    """
    Keyboard-modifier bit; combine via bitwise OR to express
    compound chords. Surfaced as an int bitmask on event payloads
    (WMouseEvent.modifiers, WKeyEvent.modifiers).
    """

    Shift = 1

    Control = 2

    Alt = 4

    Meta = 8

class Key(enum.IntEnum):
    """
    Symbolic key codes surfaced on WKeyEvent.key. Use these to
    match non-printable keys (Enter, arrows, F-keys, …); printable
    characters are easier to handle via `WKeyEvent.char_code`.
    """

    Unknown = 0

    Enter = 13

    Tab = 9

    Backspace = 8

    Shift = 16

    Control = 17

    Alt = 18

    Pause = 19

    Escape = 27

    PageUp = 33

    PageDown = 34

    End = 35

    Home = 36

    Left = 37

    Up = 38

    Right = 39

    Down = 40

    Insert = 45

    Delete = 46

    Meta = 91

    F1 = 112

    F2 = 113

    F3 = 114

    F4 = 115

    F5 = 116

    F6 = 117

    F7 = 118

    F8 = 119

    F9 = 120

    F10 = 121

    F11 = 122

    F12 = 123

    Space = 32

    A = 65

    B = 66

    C = 67

    D = 68

    E = 69

    F = 70

    G = 71

    H = 72

    I = 73

    J = 74

    K = 75

    L = 76

    M = 77

    N = 78

    O = 79

    P = 80

    Q = 81

    R = 82

    S = 83

    T = 84

    U = 85

    V = 86

    W = 87

    X = 88

    Y = 89

    Z = 90

class WMouseEvent:
    """
    Payload delivered to mouse-event handlers (clicked,
    double_clicked, mouse_over, mouse_out, wheel events).

        def on_click(e: wt.WMouseEvent):
            if e.button == wt.MouseButton.Right:
                show_context_menu(e.widget.x, e.widget.y)
        button.clicked.connect(on_click)

    The four coordinate properties report the cursor's position in
    different reference frames — use whichever frame your math is in.
    """

    @property
    def button(self) -> MouseButton:
        """MouseButton that triggered the event (None_ for pure-move)."""

    @property
    def modifiers(self) -> int:
        """Int bitmask of KeyboardModifier values held during the event."""

    @property
    def document(self) -> Coordinates:
        """Cursor position relative to the document's top-left corner."""

    @property
    def window(self) -> Coordinates:
        """
        Cursor position relative to the browser window's top-left
        (equivalent to viewport coordinates).
        """

    @property
    def screen(self) -> Coordinates:
        """Cursor position relative to the user's screen."""

    @property
    def widget(self) -> Coordinates:
        """
        Cursor position relative to the widget that fired the event
        — most useful for picking inside the widget's own geometry.
        """

    @property
    def wheel_delta(self) -> int:
        """
        Signed wheel ticks for wheel events (positive = up). Zero
        for non-wheel events.
        """

class WKeyEvent:
    """
    Payload delivered to keyboard-event handlers (key_pressed,
    key_went_down, enter_pressed).

        def on_key(e: wt.WKeyEvent):
            if e.key == wt.Key.Escape:
                dialog.hide()
        dialog.key_went_down.connect(on_key)
    """

    @property
    def key(self) -> Key:
        """Symbolic Key value — use to match non-printable keys."""

    @property
    def char_code(self) -> int:
        """
        Unicode code point of the printable character pressed, or 0
        for non-printable keys. Easier than `key` for typed-text logic.
        """

    @property
    def modifiers(self) -> int:
        """Int bitmask of KeyboardModifier values held during the event."""

class Connection:
    """
    Handle to a signal subscription returned by `Signal.connect`.
    Keep it if you need to disconnect later; otherwise discard.

        conn = button.clicked.connect(on_click)
        ...
        conn.disconnect()                    # stop receiving
    """

    def disconnect(self) -> None:
        """
        Drop the subscription. The connected callback won't be
        invoked again for new emits. Idempotent.
        """

    def is_connected(self) -> bool:
        """True until `disconnect` is called or the signal is destroyed."""

class Signal:
    """
    Zero-payload signal. Construct standalone for ad-hoc pub/sub,
    or use the no-arg signals already on widgets.

        s = wt.Signal()
        s.connect(lambda: print('fired'))
        s.emit()
    """

    def __init__(self) -> None:
        """Construct a fresh signal with no subscribers."""

    def connect(self, callable: Callable) -> Connection:
        """
        Subscribe `callable()` to this signal. Returns a Connection;
        the callable runs on each `emit`.
        """

    def emit(self) -> None:
        """
        Fire the signal — every connected callable is invoked once,
        in connection order.
        """

    def disconnect_all_slots(self) -> None:
        """
        Drop every connection opened through `connect`. Used by the
        library's shutdown handler; most code doesn't need it.
        """

class IntSignal:
    """
    Signal carrying a single int payload.

        s = wt.IntSignal()
        s.connect(lambda n: print(f'got {n}'))
        s.emit(42)
    """

    def __init__(self) -> None:
        """Construct a fresh signal with no subscribers."""

    def connect(self, callable: Callable) -> Connection:
        """
        Subscribe `callable(int)` to this signal. A zero-arg
        callable also works — the payload is dropped.
        """

    def emit(self, arg: int, /) -> None:
        """Fire the signal with the given int payload."""

    def disconnect_all_slots(self) -> None:
        """Drop every connection opened through `connect`."""

class BoolSignal:
    """Signal carrying a single bool payload."""

    def __init__(self) -> None:
        """Construct a fresh signal with no subscribers."""

    def connect(self, callable: Callable) -> Connection:
        """Subscribe `callable(bool)` to this signal."""

    def emit(self, arg: bool, /) -> None:
        """Fire the signal with the given bool payload."""

    def disconnect_all_slots(self) -> None:
        """Drop every connection opened through `connect`."""

class DoubleSignal:
    """Signal carrying a single float payload."""

    def __init__(self) -> None:
        """Construct a fresh signal with no subscribers."""

    def connect(self, callable: Callable) -> Connection:
        """Subscribe `callable(float)` to this signal."""

    def emit(self, arg: float, /) -> None:
        """Fire the signal with the given float payload."""

    def disconnect_all_slots(self) -> None:
        """Drop every connection opened through `connect`."""

class StringSignal:
    """Signal carrying a single string payload."""

    def __init__(self) -> None:
        """Construct a fresh signal with no subscribers."""

    def connect(self, callable: Callable) -> Connection:
        """Subscribe `callable(str)` to this signal."""

    def emit(self, arg: str, /) -> None:
        """Fire the signal with the given string payload."""

    def disconnect_all_slots(self) -> None:
        """Drop every connection opened through `connect`."""

class EventSignal:
    """
    Zero-payload signal backing DOM events (e.g. WCheckBox.on_check,
    WInteractWidget.enter_pressed). Like Signal but with no public
    constructor — the widget owns the instance and exposes it as a
    property.

        container.add_widget(wt.WCheckBox('OK')).on_check.connect(handler)
    """

    def connect(self, callable: Callable) -> Connection:
        """Subscribe `callable()` to this DOM event. Returns a Connection."""

    def disconnect_all_slots(self) -> None:
        """Drop every connection opened through `connect`."""

class MouseEventSignal:
    """
    DOM-event signal carrying a WMouseEvent payload. Backs the
    `clicked` / `double_clicked` / `mouse_over` / `mouse_out` props
    on WInteractWidget.

        button.clicked.connect(lambda e: print(e.button))
    """

    def connect(self, callable: Callable) -> Connection:
        """
        Subscribe `callable(WMouseEvent)`. A zero-arg callable also
        works — the payload is dropped.
        """

    def disconnect_all_slots(self) -> None:
        """Drop every connection opened through `connect`."""

class KeyEventSignal:
    """
    DOM-event signal carrying a WKeyEvent payload. Backs the
    `key_pressed` / `key_went_down` props on WInteractWidget.

        field.key_went_down.connect(
            lambda e: dialog.hide() if e.key == wt.Key.Escape else None)
    """

    def connect(self, callable: Callable) -> Connection:
        """Subscribe `callable(WKeyEvent)`. Zero-arg also works."""

    def disconnect_all_slots(self) -> None:
        """Drop every connection opened through `connect`."""

class JIntSignal:
    """
    JavaScript-emitted signal carrying an int. Like IntSignal but
    originates on the browser side and travels back to the server.
    Used for widgets where the client emits semantic events (e.g.
    WLeafletMap.zoom_level_changed).
    """

    def connect(self, callable: Callable) -> Connection:
        """Subscribe `callable(int)` to client-side emits."""

    def disconnect_all_slots(self) -> None:
        """Drop every connection opened through `connect`."""

class JInt64Signal:
    """
    JavaScript-emitted signal carrying a 64-bit int — used where
    byte sizes don't fit in 32 bits (e.g. WFileUpload.file_too_large
    reporting the rejected upload's size).
    """

    def connect(self, callable: Callable) -> Connection:
        """Subscribe `callable(int)` to client-side emits."""

    def disconnect_all_slots(self) -> None:
        """Drop every connection opened through `connect`."""

class Uint64PairSignal:
    """
    Signal carrying a (uint64, uint64) pair — typically a
    progress tick reporting (bytes received, total bytes) on
    WFileUpload and WFileDropWidget.

        upload.data_received.connect(
            lambda recv, total: bar.set_value(100 * recv / total))
    """

    def connect(self, callable: Callable) -> Connection:
        """
        Subscribe `callable(received, total)`. Either both ints or
        zero args; intermediate arities are an error.
        """

    def disconnect_all_slots(self) -> None:
        """Drop every connection opened through `connect`."""

class WEnvironment:
    """
    Per-session snapshot of the browser environment Wt captured at
    WApplication construction time. Read inside your entry-point
    factory to branch on browser type, initial URL, etc.

        def make_app(env):
            app = wt.WApplication(env)
            if not env.supports_cookies:
                app.root.add_widget(wt.WText('Cookies required.'))
                return app
            ...
            return app

    Read-only after construction. Server-driven changes (the user
    navigating internally) come through `WApplication.on_internal_
    path_changed`, not via this object.
    """

    @property
    def user_agent(self) -> str:
        """Raw `User-Agent` header from the initial request."""

    @property
    def host_name(self) -> str:
        """`Host` header from the initial request (no scheme, no port)."""

    @property
    def url_scheme(self) -> str:
        """`'http'` or `'https'`, based on the initial request."""

    @property
    def internal_path(self) -> str:
        """
        URL fragment / internal path the user arrived at — e.g.
        `/dashboard/42` for a deep-link. Use this to restore state
        on first paint; subsequent fragment changes arrive via
        `WApplication.on_internal_path_changed`.
        """

    @property
    def supports_cookies(self) -> bool:
        """
        True if the browser accepted Wt's probe cookie. False means
        session state can only survive in the URL — plan accordingly.
        """

    @property
    def server_signature(self) -> str:
        """
        The server name as reported in the Server response header.
        Cosmetic — only useful for diagnostic banners.
        """

class WObject:
    """
    Root of the Wt object hierarchy. Every widget, validator,
    layout, and resource inherits from this. The Python-facing
    surface is small — its main purpose is to provide `bind_safe`
    for safely posting cross-thread callbacks that reference an
    object that may be destroyed before the callback fires.
    """

    def bind_safe(self, function: Callable[[], None]) -> Callable[[], None]:
        """
        Wrap `function` so it no-ops if this WObject has been
        destroyed by the time it runs. Canonical use is bridging a
        background-thread callback back into the UI session via
        `WServer.post`:

            def refresh():
                label.text = compute()
            server.post(session_id, label.bind_safe(refresh))

        If `label` is gone (e.g. the user navigated away and the
        session was cleaned up) by the time post fires, the wrapped
        call is a no-op instead of a use-after-free.
        """

class WWidget(WObject):
    """
    Base class for everything that renders into the DOM. Defines
    the universal widget surface: sizing, visibility, CSS-class
    manipulation, tooltips, and animated show/hide. Concrete
    widgets (WText, WPushButton, …) inherit from this via
    WInteractWidget / WFormWidget / WContainerWidget.
    """

    def set_width(self, px: float) -> None:
        """
        Set the widget's CSS width in pixels. Pass a float; Wt
        converts to a WLength internally. For non-px units, use
        the WLength constructor directly.
        """

    def set_height(self, px: float) -> None:
        """
        Set the widget's CSS height in pixels (companion to
        `set_width`).
        """

    @property
    def hidden(self) -> bool:
        """
        Whether the widget is hidden via CSS `display: none`.
        Hidden widgets still exist in the DOM and keep their state.
        For animated transitions use `animate_show` / `animate_hide`.
        """

    @hidden.setter
    def hidden(self, arg: bool, /) -> None: ...

    def animate_show(self, animation: WAnimation) -> None:
        """
        Show the widget with a transition. Pass a WAnimation
        describing the effect:

            panel.animate_show(wt.WAnimation(
                wt.AnimationEffect.SlideInFromBottom, 300))
        """

    def animate_hide(self, animation: WAnimation) -> None:
        """
        Hide with a transition. Inverse of animate_show; pass the
        same WAnimation form.
        """

    @property
    def style_class(self) -> str:
        """
        The widget's full `class` attribute as a single string.
        Assigning REPLACES every class — use `add_style_class` /
        `remove_style_class` to mutate one at a time.
        """

    @style_class.setter
    def style_class(self, arg: str, /) -> None: ...

    def add_style_class(self, class_name: str) -> None:
        """
        Append `class_name` to the widget's `class` attribute if
        not already present.

            container.add_widget(wt.WText('Alert!')).add_style_class('warning')
        """

    def remove_style_class(self, class_name: str) -> None:
        """
        Remove `class_name` from the widget's `class` attribute.
        No-op if it isn't there.
        """

    @property
    def id(self) -> str:
        """
        The DOM `id` attribute. Wt assigns auto-generated ids by
        default; setting one is useful for CSS / external JS that
        needs to target the element by name. Keep ids globally
        unique in the page.
        """

    @id.setter
    def id(self, arg: str, /) -> None: ...

    @property
    def tool_tip(self) -> str:
        """Hover-tooltip text (sets the DOM `title` attribute)."""

    @tool_tip.setter
    def tool_tip(self, arg: str, /) -> None: ...

class WInteractWidget(WWidget):
    """
    Widget surface for things the user can interact with via mouse
    or keyboard. Adds the standard input signals to WWidget — every
    concrete widget that isn't purely decorative inherits from this.

        container.add_widget(wt.WText('Click me')).clicked.connect(handler)
    """

    @property
    def clicked(self) -> MouseEventSignal:
        """
        Fires on left-button click. Signal payload is a
        WMouseEvent (button info, coordinates, modifiers).
        """

    @property
    def double_clicked(self) -> MouseEventSignal:
        """
        Fires on left-button double-click (in addition to
        two `clicked` events). WMouseEvent payload.
        """

    @property
    def mouse_over(self) -> MouseEventSignal:
        """Fires when the cursor enters the widget's bounds."""

    @property
    def mouse_out(self) -> MouseEventSignal:
        """Fires when the cursor leaves the widget's bounds."""

    @property
    def key_pressed(self) -> KeyEventSignal:
        """
        Fires on each printable-key press while the widget
        has focus. WKeyEvent payload. Use `key_went_down`
        instead to catch non-printable keys (arrows, F-keys).
        """

    @property
    def key_went_down(self) -> KeyEventSignal:
        """
        Fires on every key press (printable AND control).
        WKeyEvent payload — check `.key` for the symbolic
        name when handling non-printables.
        """

    @property
    def enter_pressed(self) -> EventSignal:
        """
        Convenience signal that fires when the user presses
        Enter while the widget has focus. Typical use is
        submit-on-enter on a form input.
        """

class ValidationState(enum.Enum):
    """
    Outcome of a validator's check on the current input.

        Valid         — input acceptable, OK to submit.
        InvalidEmpty  — input is empty, validator marks it mandatory.
        Invalid       — input present but doesn't satisfy the rule.

    InvalidEmpty is split out from Invalid because the typical UX
    shows a different message for 'required field missing' than for
    'wrong format'.
    """

    Invalid = 0

    InvalidEmpty = 1

    Valid = 2

class ValidationResult:
    """
    Verdict from `WValidator.validate(input)` — a (state, message)
    pair. The message is the localized text shown to the user when
    the input is rejected.

        r = validator.validate('not-an-int')
        if r.state != wt.ValidationState.Valid:
            label.text = r.message
    """

    @overload
    def __init__(self) -> None:
        """Construct a result with state=Valid and no message."""

    @overload
    def __init__(self, state: ValidationState) -> None:
        """Construct a result with the given state and no message."""

    @overload
    def __init__(self, state: ValidationState, message: str) -> None:
        """
        Construct a result with the given state and an explanatory
        message (typically a localized 'too short' / 'invalid'
        string to show next to the input).
        """

    @property
    def state(self) -> ValidationState:
        """The ValidationState verdict."""

    @property
    def message(self) -> str:
        """The localized human-readable message; empty when state is Valid."""

    def __repr__(self) -> str: ...

class ValidationResultSignal:
    """
    Signal carrying a ValidationResult payload. Surfaced via
    `WFormWidget.validated` — fires after the form widget's
    validator has run.

        edit.validated.connect(lambda r: label.text = r.message)
    """

    def connect(self, callable: Callable) -> Connection:
        """
        Subscribe `callable(result)` to validation events. Returns
        a Connection; call its `.disconnect()` to stop receiving.
        """

    def disconnect_all_slots(self) -> None:
        """
        Drop every connection opened through `connect`. Mostly an
        internal shutdown hook — most code doesn't need this.
        """

class WValidator:
    """
    Base class for input validators. Concrete subclasses (WIntValidator,
    WDoubleValidator, WRegExpValidator, …) inherit the `mandatory` flag
    and the empty-input message. Validators are normally attached to a
    WFormWidget via `form_widget.set_validator(v)`; the form widget then
    fires `validated` after each input change.

        edit = container.add_widget(wt.WLineEdit())
        v = wt.WIntValidator(0, 100)
        v.mandatory = True
        edit.set_validator(v)
        edit.validated.connect(lambda r: print(r))
    """

    @property
    def mandatory(self) -> bool:
        """
        Whether empty input counts as Invalid (specifically as
        InvalidEmpty). False (the default) makes empty input Valid.
        """

    @mandatory.setter
    def mandatory(self, arg: bool, /) -> None: ...

    @property
    def invalid_blank_text(self) -> str:
        """
        The message shown when `mandatory` is True and the input
        is empty. Replaces the default 'this field is required'.
        """

    @invalid_blank_text.setter
    def invalid_blank_text(self, arg: str, /) -> None: ...

    def validate(self, input: str) -> ValidationResult:
        """
        Run the validation rule against `input` and return a
        ValidationResult. Pure function — does NOT mutate either
        the validator or the form widget; safe to call from anywhere.
        """

class WIntValidator(WValidator):
    """
    Accepts an integer in an optional [bottom, top] range.

        edit.set_validator(wt.WIntValidator(0, 100))
    """

    @overload
    def __init__(self) -> None:
        """Construct a validator with no range limits."""

    @overload
    def __init__(self, minimum: int, maximum: int) -> None:
        """
        Construct a validator that accepts integers in [minimum,
        maximum] inclusive.
        """

    @property
    def bottom(self) -> int:
        """Lowest accepted value (inclusive)."""

    @bottom.setter
    def bottom(self, arg: int, /) -> None: ...

    @property
    def top(self) -> int:
        """Highest accepted value (inclusive)."""

    @top.setter
    def top(self, arg: int, /) -> None: ...

    def set_range(self, bottom: int, top: int) -> None:
        """Set both bounds atomically."""

    @property
    def invalid_not_a_number_text(self) -> str:
        """Message shown when the input isn't a valid integer at all."""

    @invalid_not_a_number_text.setter
    def invalid_not_a_number_text(self, arg: str, /) -> None: ...

    @property
    def invalid_too_small_text(self) -> str:
        """Message shown when the integer is below `bottom`."""

    @invalid_too_small_text.setter
    def invalid_too_small_text(self, arg: str, /) -> None: ...

    @property
    def invalid_too_large_text(self) -> str:
        """Message shown when the integer exceeds `top`."""

    @invalid_too_large_text.setter
    def invalid_too_large_text(self, arg: str, /) -> None: ...

    @property
    def ignore_trailing_spaces(self) -> bool:
        """
        Whether trailing whitespace in the input is stripped before
        parsing. Useful when users paste numbers with stray spaces.
        """

    @ignore_trailing_spaces.setter
    def ignore_trailing_spaces(self, arg: bool, /) -> None: ...

class WDoubleValidator(WValidator):
    """
    Accepts a floating-point number in an optional [bottom, top] range.

        edit.set_validator(wt.WDoubleValidator(0.0, 1.0))
    """

    @overload
    def __init__(self) -> None:
        """Construct a validator with no range limits."""

    @overload
    def __init__(self, minimum: float, maximum: float) -> None:
        """
        Construct a validator that accepts floats in [minimum,
        maximum] inclusive.
        """

    @property
    def bottom(self) -> float:
        """Lowest accepted value (inclusive)."""

    @bottom.setter
    def bottom(self, arg: float, /) -> None: ...

    @property
    def top(self) -> float:
        """Highest accepted value (inclusive)."""

    @top.setter
    def top(self, arg: float, /) -> None: ...

    def set_range(self, bottom: float, top: float) -> None:
        """Set both bounds atomically."""

    @property
    def invalid_not_a_number_text(self) -> str:
        """Message shown when the input isn't a valid number."""

    @invalid_not_a_number_text.setter
    def invalid_not_a_number_text(self, arg: str, /) -> None: ...

    @property
    def invalid_too_small_text(self) -> str:
        """Message shown when the value is below `bottom`."""

    @invalid_too_small_text.setter
    def invalid_too_small_text(self, arg: str, /) -> None: ...

    @property
    def invalid_too_large_text(self) -> str:
        """Message shown when the value exceeds `top`."""

    @invalid_too_large_text.setter
    def invalid_too_large_text(self, arg: str, /) -> None: ...

class WLengthValidator(WValidator):
    """
    Accepts text whose length (in characters) falls within an
    optional [minimum_length, maximum_length] range. Useful for
    things like 'username 3–20 chars'.

        edit.set_validator(wt.WLengthValidator(3, 20))
    """

    @overload
    def __init__(self) -> None:
        """Construct a validator with no length limits."""

    @overload
    def __init__(self, minimum_length: int, maximum_length: int) -> None:
        """Construct a validator with the given length bounds (inclusive)."""

    @property
    def minimum_length(self) -> int:
        """Shortest accepted length (inclusive)."""

    @minimum_length.setter
    def minimum_length(self, arg: int, /) -> None: ...

    @property
    def maximum_length(self) -> int:
        """Longest accepted length (inclusive)."""

    @maximum_length.setter
    def maximum_length(self, arg: int, /) -> None: ...

    @property
    def invalid_too_short_text(self) -> str:
        """Message shown when the input is shorter than `minimum_length`."""

    @invalid_too_short_text.setter
    def invalid_too_short_text(self, arg: str, /) -> None: ...

    @property
    def invalid_too_long_text(self) -> str:
        """Message shown when the input exceeds `maximum_length`."""

    @invalid_too_long_text.setter
    def invalid_too_long_text(self, arg: str, /) -> None: ...

class WRegExpValidator(WValidator):
    r"""
    Accepts text matching a regular-expression pattern. Useful for
    phone numbers, postal codes, custom formats.

        edit.set_validator(wt.WRegExpValidator(r'\d{5}'))     # US ZIP
    """

    @overload
    def __init__(self) -> None:
        """Construct a validator with no pattern (matches anything)."""

    @overload
    def __init__(self, pattern: str) -> None:
        """
        Construct a validator that requires the input to match
        `pattern` end-to-end.
        """

    @property
    def pattern(self) -> str:
        """
        The regex pattern. Wt uses its own regex syntax (close to
        PCRE); test on the form to confirm matching behavior.
        """

    @pattern.setter
    def pattern(self, arg: str, /) -> None: ...

    @property
    def invalid_no_match_text(self) -> str:
        """Message shown when the input doesn't match `pattern`."""

    @invalid_no_match_text.setter
    def invalid_no_match_text(self, arg: str, /) -> None: ...

class WEmailValidator(WValidator):
    """
    Accepts a syntactically-valid email address (or a comma-separated
    list when `multiple` is True). Doesn't verify the address actually
    exists — that needs an out-of-band confirm step.

        edit.set_validator(wt.WEmailValidator())
    """

    def __init__(self) -> None:
        """
        Construct an email validator with the default RFC-5322-ish
        pattern accepting a single address.
        """

    @property
    def multiple(self) -> bool:
        """Accept a comma-separated list of addresses instead of just one."""

    @multiple.setter
    def multiple(self, arg: bool, /) -> None: ...

    @property
    def pattern(self) -> str:
        """Override the built-in regex with a custom pattern."""

    @pattern.setter
    def pattern(self, arg: str, /) -> None: ...

    @property
    def invalid_not_an_email_address_text(self) -> str:
        """Message shown when the input doesn't look like an email address."""

    @invalid_not_an_email_address_text.setter
    def invalid_not_an_email_address_text(self, arg: str, /) -> None: ...

class WStackedValidator(WValidator):
    """
    Composite validator that runs a sequence of sub-validators in
    order; the first one that rejects wins. Useful for combining
    concerns (length AND pattern, range AND custom rule).

        stacked = wt.WStackedValidator()
        stacked.add_validator(wt.WLengthValidator(8, 64))
        stacked.add_validator(wt.WRegExpValidator(r'.*[A-Z].*'))
        edit.set_validator(stacked)
    """

    def __init__(self) -> None:
        """Construct an empty stacked validator."""

    def add_validator(self, validator: WValidator) -> None:
        """Append `validator` to the end of the chain."""

    def insert_validator(self, index: int, validator: WValidator) -> None:
        """Insert `validator` at `index` so it runs before later ones."""

    def remove_validator(self, validator: WValidator) -> None:
        """Remove `validator` from the chain. No-op if it isn't there."""

    @property
    def size(self) -> int:
        """Number of sub-validators currently in the chain."""

    def clear(self) -> None:
        """Drop every sub-validator."""

class WFormWidget(WInteractWidget):
    r"""
    Common surface for HTML form inputs — text fields, checkboxes,
    selects, etc. Adds the `enabled` flag, focus control, the
    `changed` signal, and validator wiring on top of WInteractWidget.

        edit = container.add_widget(wt.WLineEdit())
        edit.set_validator(wt.WRegExpValidator(r'\d+'))
        edit.enabled = False    # render disabled
        edit.changed.connect(lambda: log(edit.text))
    """

    @property
    def enabled(self) -> bool:
        """
        Whether the input accepts user interaction. Disabled inputs
        render greyed out and don't fire `changed`.
        """

    @enabled.setter
    def enabled(self, arg: bool, /) -> None: ...

    def set_focus(self) -> None:
        """
        Move keyboard focus to this widget. Effect happens on the
        next client round-trip.
        """

    @property
    def changed(self) -> EventSignal:
        """
        Fires when the user commits a change (blur for text
        fields, toggle for checkboxes, Enter for selects).
        Compare with WLineEdit's `text_input` which fires
        on every keystroke.
        """

    def set_validator(self, validator: WValidator) -> None:
        """
        Attach a validator (WIntValidator, WRegExpValidator, …)
        that decides whether the current input is acceptable. The
        validator's verdict surfaces via `validated`.
        """

    @property
    def validator(self) -> WValidator:
        """The currently-attached validator (shared_ptr), or None."""

    @property
    def validated(self) -> ValidationResultSignal:
        """
        Fires after the validator has run, with a WValidator
        .Result payload — inspect `.state` for Valid /
        InvalidEmpty / Invalid.
        """

class WApplication(WObject):
    """
    The per-session Wt application instance. One WApplication is
    constructed per browser session by the factory you pass to
    WServer.add_entry_point, and lives until that session ends.
    It owns the page's root container, the URL state, and the
    server→client update channel.

        def create_app(env):
            app = wt.WApplication(env)
            app.title = 'Hello'
            app.root.add_widget(wt.WText('Welcome.'))
            app.root.add_widget(wt.WPushButton('Quit')).clicked.connect(app.quit)
            return app

        server = wt.WServer()
        server.set_server_configuration(sys.argv)
        server.add_entry_point(wt.EntryPointType.Application, create_app)
        server.run()

    Inside a session, `WApplication.instance()` returns the current
    WApplication on any Wt-managed thread — useful for code that
    doesn't have a direct reference to it.
    """

    def __init__(self, environment: WEnvironment) -> None:
        """
        Construct the per-session application from the WEnvironment
        passed into your factory. The first thing your entry-point
        factory typically does.
        """

    @property
    def root(self) -> WContainerWidget:
        """
        The top-level WContainerWidget — start `add_widget`-
        ing UI here. Owned by the application; lives as long
        as the session does.
        """

    @property
    def environment(self) -> WEnvironment:
        """
        The captured WEnvironment from construction time.
        Use for read-only browser/session info.
        """

    @property
    def title(self) -> str:
        """
        The page's `<title>` text. Assigning updates the browser
        tab on the next round-trip.
        """

    @title.setter
    def title(self, arg: str, /) -> None: ...

    def set_internal_path(self, path: str, emit_change: bool = False) -> None:
        """
        Change the URL fragment (the part after `#`) without
        a full page reload. Pass `emit_change=True` to also fire
        `on_internal_path_changed` — useful when you want both
        the URL update AND the route handler to run.
        """

    @property
    def internal_path(self) -> str:
        """
        The current URL fragment / internal path. Mirrors what's
        shown after the `#` in the browser address bar.
        """

    def on_internal_path_changed(self, callback: Callable) -> Connection:
        """
        Subscribe to URL-fragment changes — browser back/forward,
        or `set_internal_path(..., emit_change=True)`.

            def route(path):
                if path == '/about': show_about()
                elif path.startswith('/user/'): show_user(path)
            app.on_internal_path_changed(route)

        Returns a Connection — call `.disconnect()` on it to stop
        receiving.
        """

    @property
    def session_id(self) -> str:
        """
        Opaque per-session string. Pass to `WServer.post` to
        schedule cross-thread work back into this session.
        """

    def redirect(self, url: str) -> None:
        """
        Tell the browser to navigate to `url`. Effective on the
        next round-trip; the current session terminates if `url`
        leaves the application.
        """

    def quit(self) -> None:
        """
        End the session cleanly. The page stays loaded but stops
        talking to the server; the application instance is
        destroyed shortly after.
        """

    def trigger_update(self) -> None:
        """
        Force a server-initiated update push to the connected
        client. Combine with `WServer.post` for cross-thread
        updates — only effective after `enable_updates(True)`.
        """

    def require(self, url: str, symbol: str = '') -> bool:
        """
        Load an external JavaScript library before the page is
        rendered. Subsequent `do_javascript` calls are deferred
        until the library has loaded. Pass `symbol` (e.g. 'jQuery')
        to skip the load if it's already defined on `window`.
        Returns True if the library was scheduled to load, False
        if `symbol` was already present.
        """

    def do_javascript(self, javascript: str, after_loaded: bool = True) -> None:
        """
        Send arbitrary JS to the client. With `after_loaded=True`
        (default), the JS runs after all `require`'d libraries
        have loaded; with `False`, inline before the DOM finishes.
        """

    def enable_updates(self, enabled: bool = True) -> None:
        """
        Allow server-initiated updates. Without this, mutations
        from background threads (WTimer, WServer.post) only reach
        the browser on the next client-initiated round-trip; with
        it, `trigger_update` pushes them immediately. Enable once
        during entry-point setup if you do any background work.
        """

    def use_style_sheet(self, link: WLink, media: str = 'all') -> None:
        """
        Add an external stylesheet. `link` is a WLink (URL string
        or a WResource); `media` is the CSS media query (default
        'all'). The `<link>` tag is appended to `<head>`.
        """

    def defer_rendering(self) -> None:
        """
        Suspend rendering of the current event response until
        `resume_rendering` is called. Use when an async operation
        (HttpClient request, WServer.post background work) must
        complete before the page can be delivered.
        """

    def resume_rendering(self) -> None:
        """
        Resume rendering after a prior `defer_rendering`. Call
        from the callback that signals 'we're ready'.
        """

    @staticmethod
    def instance() -> WApplication:
        """
        Return the WApplication for the current Wt-managed
        thread, or None if not inside a session. Useful for
        code that doesn't carry an explicit `app` reference.
        """

    @property
    def theme(self) -> WTheme:
        """
        The active theme (shared_ptr<WTheme>). Set during entry-
        point setup to change the default look-and-feel:

            app.theme = wt.WBootstrap5Theme()
        """

    @theme.setter
    def theme(self, arg: WTheme, /) -> None: ...

class UpdateLock:
    """
    RAII lock for cross-thread access to a WApplication. Acquire
    to mutate widgets from a non-Wt thread without going through
    WServer.post; release happens automatically when the wrapper
    is GC'd.

        with wt.update_lock(app):
            label.text = computed_value
            app.trigger_update()

    `WServer.post` is the recommended path for most cross-thread
    work — UpdateLock is the lower-level escape hatch. The
    Pythonic context-manager wrapper is `witty_for_python.update_lock(app)`.
    """

    def __init__(self, application: WApplication) -> None:
        """
        Acquire the application's update lock. Check `bool(lock)`
        to confirm — acquisition can fail if the application is
        being torn down.
        """

    def __bool__(self) -> bool:
        """
        True if the lock was successfully acquired, False if the
        application is being torn down.
        """

class ContentDisposition(enum.Enum):
    """
    Controls the `Content-Disposition` header on resource responses
    — whether the browser displays the bytes inline, prompts the
    user to save them, or leaves the header off. Pair with
    `WResource.suggest_file_name` for the save filename.
    """

    Attachment = 1

    Inline = 2

class WResource(WObject):
    """
    Abstract base for anything Wt serves over HTTP that isn't the
    widget tree itself — file downloads, generated PDFs, JSON APIs,
    image data, etc. Mount via `WServer.add_resource(resource,
    path)` for server-wide endpoints, or hand to a `WLink` for
    session-scoped use (e.g. an inline image).

    Two concrete subclasses ship in this binding — WMemoryResource
    (in-RAM bytes) and WFileResource (file on disk). For dynamic
    endpoints, use `CallbackResource(callable)` which delegates
    handle_request to a Python function instead of requiring a
    subclass.
    """

    def suggest_file_name(self, name: str) -> None:
        """
        Set the suggested filename the browser uses when saving the resource (e.g. 'export.csv').
        """

    def set_disposition_type(self, disposition: ContentDisposition) -> None:
        """
        Choose ContentDisposition.Attachment to force a 'Save As'
        prompt, .Inline to display in-page when the MIME type
        supports it, or .None_ to omit the header.
        """

    def set_changed(self) -> None:
        """
        Invalidate any browser-side cache of this resource so the next fetch sees the latest data. Call after set_data() etc.
        """

    @property
    def internal_path(self) -> str:
        """
        Stable internal-path component of the resource's URL.
        Setting one lets you mount the resource at a known route
        rather than a generated hash.
        """

    @internal_path.setter
    def internal_path(self, arg: str, /) -> None: ...

    def set_invalid_after_changed(self, enabled: bool) -> None:
        """
        When True, every `set_changed` invalidates any URL
        previously handed out — clients with the old URL will get
        404 and must re-fetch the URL. Default False (URL stays
        stable across content updates).
        """

    def set_takes_update_lock(self, enabled: bool) -> None:
        """
        When true, handle_request() acquires the session update lock before serving — required if your subclass touches widget state. Default is false (lock-free serving, faster).
        """

    def generate_url(self) -> str:
        """Return a URL at which this resource can be fetched."""

class WStreamResource(WResource):
    """
    Intermediate base for resources that stream their bytes from a
    C++ `std::istream`. Bound here only so WFileResource can inherit
    MIME-type and buffer-size knobs — for Python use, reach for
    WFileResource (file on disk), WMemoryResource (bytes in RAM),
    or CallbackResource (write whatever you want directly to the
    Response).
    """

    @property
    def mime_type(self) -> str:
        """Content-Type sent with each response."""

    @mime_type.setter
    def mime_type(self, arg: str, /) -> None: ...

    def set_buffer_size(self, size: int) -> None:
        """
        Size in bytes of the chunk used to copy from the underlying
        stream to the HTTP response. Larger reduces syscall
        overhead; smaller improves first-byte latency.
        """

class WMemoryResource(WResource):
    r"""
    WResource backed by an in-memory `bytes` blob. Useful for small
    generated payloads (a CSV, a thumbnail) that shouldn't touch the
    filesystem.

        payload = wt.WMemoryResource('text/csv', b'name,age\nAlice,30\n')
        server.add_resource(payload, '/export.csv')
        # later: rebuild and notify clients
        payload.data = render_csv(rows)
        payload.set_changed()
    """

    @overload
    def __init__(self) -> None:
        """
        Construct an empty memory resource with no MIME type or
        data set — assign both before serving.
        """

    @overload
    def __init__(self, mime_type: str) -> None:
        """
        Construct a memory resource declaring `mime_type` with no
        data set yet. Assign `data` before mounting.
        """

    @overload
    def __init__(self, mime_type: str, data: bytes) -> None:
        """
        Construct a memory resource ready to serve `data` as
        `mime_type`.
        """

    @property
    def data(self) -> bytes:
        """
        The bytes served. Reading returns a copy as `bytes`;
        assigning replaces the served payload. Call `set_changed`
        afterwards to invalidate any browser cache.
        """

    @data.setter
    def data(self, arg: bytes, /) -> None: ...

    @property
    def mime_type(self) -> str:
        """Content-Type returned with the bytes."""

    @mime_type.setter
    def mime_type(self, arg: str, /) -> None: ...

class WFileResource(WStreamResource):
    """
    WResource that streams a file on disk. Wt opens the file per
    request and copies bytes through to the HTTP response, so the
    file can change between fetches without restarting the server.

        server.add_resource(
            wt.WFileResource('application/pdf', '/var/data/report.pdf'),
            '/report.pdf')
    """

    @overload
    def __init__(self) -> None:
        """
        Construct an empty file resource with no file or MIME type
        set. Assign both before serving.
        """

    @overload
    def __init__(self, file_name: str) -> None:
        """
        Construct a file resource pointing at `file_name`. The
        MIME type is left at the inherited default — set
        `mime_type` afterwards.
        """

    @overload
    def __init__(self, mime_type: str, file_name: str) -> None:
        """
        Construct a file resource that serves `file_name` with
        `mime_type` as its Content-Type.
        """

    @property
    def file_name(self) -> str:
        """
        Filesystem path of the file to serve. Assigning swaps the
        source — call `set_changed` afterwards to invalidate caches.
        """

    @file_name.setter
    def file_name(self, arg: str, /) -> None: ...

class WLink:
    """
    Polymorphic link target — wraps a URL string OR a server-side
    WResource. Used by WAnchor, WImage, WPushButton.link, etc.;
    Python's implicit conversion lets you pass a bare str or a
    WResource and get the corresponding WLink automatically.

        container.add_widget(wt.WAnchor(wt.WLink('https://example.com'), 'Visit'))

        chart = wt.WMemoryResource('image/png', render_png())
        container.add_widget(wt.WImage(wt.WLink(chart), 'Chart'))

    For URL fragments that should drive WApplication.internal_path
    navigation rather than a full page load, set `internal_path` on
    the link or use the `wt.internal_path('/route')` factory.
    """

    @overload
    def __init__(self) -> None:
        """Construct an empty link with no target."""

    @overload
    def __init__(self, url: str) -> None:
        """
        Construct a link to an external URL or any same-origin path.
        Plain `str` arguments to widgets that take a WLink hit this
        constructor automatically.
        """

    @overload
    def __init__(self, resource: WResource) -> None:
        """
        Construct a link to a WResource. The resource's URL is
        computed by Wt; clients fetch the dynamic content when the
        link is followed. A `WResource` arg to widgets that take a
        WLink hits this constructor automatically.
        """

    @property
    def url(self) -> str:
        """The link target as a URL string."""

    @url.setter
    def url(self, arg: str, /) -> None: ...

    @property
    def internal_path(self) -> str:
        """
        Treat the link as an internal-path navigation rather than an
        external URL. Setting this makes a click update the URL
        fragment and fire `WApplication.on_internal_path_changed`
        instead of reloading the page.
        """

    @internal_path.setter
    def internal_path(self, arg: str, /) -> None: ...

def internal_path(path: str) -> WLink:
    """
    Construct a WLink that points to the given internal path (e.g. '/slide/3'). Clicking a WAnchor backed by this link fires WApplication.internal_path_changed instead of navigating away.
    """

class CallbackResource(WResource):
    """
    WResource whose `handle_request` delegates to a Python callable.
    The Pythonic way to expose a dynamic HTTP endpoint without
    subclassing — the equivalent of a Flask/Django view function in
    the Wt world.

        def api(req, resp):
            resp.set_mime_type('application/json')
            resp.write(b'{"ok": true}')
        server.add_resource(wt.CallbackResource(api), '/api/ping')

    Wt invokes the callable on a worker thread with `(request,
    response)`; the binding takes the GIL around the call. The
    request/response wrappers are valid only for the duration of
    the invocation — don't stash them. Captured state in the
    callable (closures, class attrs) persists across requests; the
    CallbackResource holds a strong reference to the callable.
    """

    def __init__(self, callback: Callable) -> None:
        """
        Mount a Python callable as an HTTP endpoint. The callable is invoked as `callback(request, response)` on every request, with the GIL held. Exceptions are routed through `PyErr_WriteUnraisable` rather than crashing Wt's worker.
        """

class WContainerWidget(WInteractWidget):
    """
    A `<div>`-style box that holds child widgets in document order.
    The default container for composing UIs — every Wt application
    starts with a root WContainerWidget (`app.root`) and adds
    widgets into it.

        page = app.root
        page.add_widget(wt.WText('Welcome.'))
        page.add_widget(wt.WPushButton('Click me')).clicked.connect(say_hi)

    Children render stacked top-to-bottom unless a `layout` is
    installed via `set_layout` (then the layout class decides). The
    container owns its children: when it's destroyed, every widget
    added to it is destroyed too.
    """

    def __init__(self) -> None:
        """Construct an empty container with no children and no layout."""

    @overload
    def add_widget(self, text: str) -> WText:
        """
        Convenience for `add_widget(WText(text))`. Wraps `text` in
        a freshly-constructed WText and adds it; returns a
        non-owning handle to the WText so you can mutate it later.

            label = container.add_widget('Loading…')
            # later, after data arrives:
            label.text = 'Loaded 42 rows.'

        If you need any setting on the WText other than its text
        (e.g. CSS class, format), build the WText yourself and use
        the widget-taking overload below.
        """

    @overload
    def add_widget(self, widget: _T_Widget) -> _T_Widget:
        """
        Transfer ownership of `widget` to this container and
        return the same Python wrapper (subtype preserved), re-armed
        as a non-owning alias. Chain straight off the return:

            container.add_widget(wt.WPushButton('Save')).clicked.connect(save)

        Or keep the typed handle for later mutation:

            edit = container.add_widget(wt.WLineEdit())
            edit.placeholder = 'Email…'

        From the moment of transfer, the container is responsible
        for destroying the widget — garbage-collecting the Python
        wrapper does NOT delete the C++ object (Wt's widget tree
        does, on container teardown).
        """

    @overload
    def add_widgets(self, texts: Sequence[str]) -> list[WText]:
        """
        Bulk version of `add_widget(str)`. Wraps each string in a
        WText and adds them in order. Returns the list of handles.

            rows = container.add_widgets(['Apples', 'Pears', 'Plums'])
            rows[0].text = 'Granny Smith'           # mutate one
        """

    @overload
    def add_widgets(self, widgets: list[_T_Widget]) -> list[_T_Widget]:
        """
        Bulk version of `add_widget(widget)`. Transfers ownership
        of each widget to this container in order. Returns the
        same Python wrappers, each re-armed as a non-owning alias
        (identity and subtype preserved).

            items = [wt.WPushButton(label) for label in choices]
            container.add_widgets(items)            # one round-trip
            for btn in items:                       # still typed + usable
                btn.clicked.connect(lambda b=btn: pick(b.text))
        """

    def clear(self) -> None:
        """
        Remove and destroy every child widget. After this returns
        the container has no children and `count` is 0; any Python
        wrappers still referencing the removed widgets are now
        dangling — calling methods on them raises.
        """

    @property
    def count(self) -> int:
        """Number of direct child widgets currently in the container."""

    def widget(self, index: int) -> WWidget:
        """
        Return a non-owning handle to the child at position
        `index` (0-based). Useful for inspecting children when
        you didn't keep handles from `add_widget`. The static
        type is WWidget; use `isinstance` to narrow.
        """

    def remove_widget(self, widget: WWidget) -> WWidget:
        """
        Detach `widget` from this container and return ownership
        to Python. The widget is NOT destroyed — it's left dangling
        until either the returned reference is dropped (Python
        destroys it) or it's re-attached to a different container
        via `add_widget`.

            moved = src.remove_widget(some_btn)
            dst.add_widget(moved)                  # re-parented
        """

    def set_layout(self, layout: WLayout) -> None:
        """
        Install `layout` as the container's layout manager. Once
        set, the layout (not the container's add_widget order)
        decides how children are positioned — use the layout's own
        add_widget / add_item methods after this. Same ownership
        transfer as add_widget: the container takes the C++ object,
        the Python wrapper is re-armed as a non-owning alias.

            layout = wt.WVBoxLayout()
            container.set_layout(layout)
            layout.add_widget(wt.WText('top'))
            layout.add_widget(wt.WText('bottom'))
        """

class WText(WInteractWidget):
    """
    Static text content. Renders a span of XHTML in the page; the
    simplest building block for displaying text or inline markup.

        label = container.add_widget(wt.WText('Loading…'))
        label.text = 'Loaded 42 rows.'

    Text is interpreted as XHTML by default — passing untrusted
    user input is XSS-unsafe. Wrap with HTML escaping before
    assigning, or use a future PlainText TextFormat binding.
    """

    @overload
    def __init__(self) -> None:
        """Construct an empty WText with no content. Set `text` later."""

    @overload
    def __init__(self, text: str) -> None:
        """Construct a WText displaying `text` (interpreted as XHTML)."""

    @property
    def text(self) -> str:
        """
        The widget's displayed text (XHTML). Assigning re-renders
        the widget on the next client round-trip; no need to call
        any refresh method.
        """

    @text.setter
    def text(self, arg: str, /) -> None: ...

class WPushButton(WFormWidget):
    """
    A clickable button. Connect to `clicked` for an action button,
    or set `link` for navigation (the button renders as a styled
    anchor).

        container.add_widget(wt.WPushButton('Save')).clicked.connect(save)

        home = container.add_widget(wt.WPushButton('Home'))
        home.link = wt.WLink('/')
    """

    @overload
    def __init__(self) -> None:
        """Construct an empty button with no caption."""

    @overload
    def __init__(self, text: str) -> None:
        """Construct a button captioned `text`."""

    @property
    def text(self) -> str:
        """The button's caption (XHTML)."""

    @text.setter
    def text(self, arg: str, /) -> None: ...

    @property
    def link(self) -> WLink:
        """
        URL the button navigates to when clicked. Setting a link
        makes the button render as an anchor under the hood; if you
        want pure action behavior, leave `link` unset and connect
        to `clicked` instead.
        """

    @link.setter
    def link(self, arg: WLink, /) -> None: ...

class WLineEdit(WFormWidget):
    """
    Single-line text input.

        edit = container.add_widget(wt.WLineEdit())
        edit.placeholder = 'Email…'
        edit.max_length = 64
        container.add_widget(wt.WPushButton('Send')).clicked.connect(
            lambda: send(edit.text))
    """

    @overload
    def __init__(self) -> None:
        """Construct an empty line edit."""

    @overload
    def __init__(self, text: str) -> None:
        """Construct a line edit with initial value `text`."""

    @property
    def text(self) -> str:
        """
        The current input value. Reads what the user has typed;
        assigning replaces the current contents.
        """

    @text.setter
    def text(self, arg: str, /) -> None: ...

    @property
    def placeholder(self) -> str:
        """
        Greyed-out hint shown when the field is empty (the standard
        browser `placeholder` attribute).
        """

    @placeholder.setter
    def placeholder(self, arg: str, /) -> None: ...

    @property
    def max_length(self) -> int:
        """
        Maximum number of characters the browser will accept.
        Negative (the default) means no limit. Enforced client-side
        only — re-validate server-side if it matters.
        """

    @max_length.setter
    def max_length(self, arg: int, /) -> None: ...

    @property
    def text_input(self) -> EventSignal:
        """
        Per-keystroke signal (`EventSignal<>`). Fires as
        the user types, before the change is committed.
        Use `changed` instead for the standard
        blur/Enter-fires-once semantics.
        """

class WCheckBox(WFormWidget):
    """
    Bistable boolean control with an optional caption.

        container.add_widget(wt.WCheckBox('Subscribe')).on_check.connect(subscribe)

        box = container.add_widget(wt.WCheckBox('Remember me'))
        box.checked = True
        box.on_check.connect(lambda: store('remember', True))
        box.on_uncheck.connect(lambda: store('remember', False))

    Inherits all WFormWidget validation/state plumbing — wire to
    `set_validator` if the value participates in a form submit.
    """

    @overload
    def __init__(self) -> None:
        """Construct an unlabelled checkbox in the unchecked state."""

    @overload
    def __init__(self, text: str) -> None:
        """Construct a labelled checkbox; `text` renders next to the box."""

    @property
    def checked(self) -> bool:
        """
        The current boolean state. Assigning programmatically does
        NOT fire `on_check`/`on_uncheck` — those are user-input
        events.
        """

    @checked.setter
    def checked(self, arg: bool, /) -> None: ...

    @property
    def on_check(self) -> EventSignal:
        """
        Fires when the user checks the box. No-arg signal.
        Programmatic `checked = True` does not fire it.
        """

    @property
    def on_uncheck(self) -> EventSignal:
        """Fires when the user unchecks the box. Mirror of `on_check`."""

class WAnchor(WContainerWidget):
    """
    A hyperlink. Inherits WContainerWidget so the visible body can
    be arbitrary widgets, not just text — wrap an image to make a
    clickable banner, etc.

        container.add_widget(wt.WAnchor(wt.WLink('https://example.com'), 'Visit'))

        container.add_widget(wt.WAnchor(wt.WLink('/landing'))).add_widget(
            wt.WImage(wt.WLink('/banner.png'), 'Promo'))
    """

    @overload
    def __init__(self) -> None:
        """Construct an empty anchor with no link or content."""

    @overload
    def __init__(self, link: WLink) -> None:
        """
        Construct an anchor pointing to `link` with no visible text.
        Useful when the body will be set up via `add_widget`.
        """

    @overload
    def __init__(self, link: WLink, text: str) -> None:
        """
        Construct an anchor whose visible body is the plain text
        `text` and which targets `link` on click.
        """

    @property
    def link(self) -> WLink:
        """
        The hyperlink target. A WLink wraps a URL string, an
        internal-path reference, or a server-side WResource.
        """

    @link.setter
    def link(self, arg: WLink, /) -> None: ...

class WImage(WInteractWidget):
    """
    An `<img>` element. The image source can be any WLink — a URL
    string, a static resource path, or a dynamically-served
    WResource (e.g. a WPdfImage or chart rendered to PNG).

        container.add_widget(
            wt.WImage(wt.WLink('/logo.png'), 'Logo')
        ).clicked.connect(zoom_logo)

        server.add_resource(MyChartResource(), '/chart.png')
        container.add_widget(wt.WImage(wt.WLink('/chart.png'), 'Live chart'))
    """

    @overload
    def __init__(self) -> None:
        """Construct an empty image with no source."""

    @overload
    def __init__(self, link: WLink) -> None:
        """
        Construct an image sourced from `link` with no alt text.
        Set `alt_text` afterwards for accessibility.
        """

    @overload
    def __init__(self, link: WLink, alt_text: str) -> None:
        """
        Construct an image sourced from `link` with the given
        alt text (used by screen readers and shown if the image
        fails to load).
        """

    @property
    def image_link(self) -> WLink:
        """
        The image source. Assigning swaps the displayed image on
        the next client round-trip.
        """

    @image_link.setter
    def image_link(self, arg: WLink, /) -> None: ...

    @property
    def alt_text(self) -> str:
        """
        Text shown if the image fails to load and read aloud by
        screen readers. Set it on any image whose meaning matters.
        """

    @alt_text.setter
    def alt_text(self, arg: str, /) -> None: ...

class Orientation(enum.IntEnum):
    """
    Layout axis. `Horizontal` lays things out left-to-right;
    `Vertical` lays things out top-to-bottom. Used by WSlider and
    other widgets that have a natural axis.
    """

    Horizontal = 1

    Vertical = 2

class SelectionMode(enum.Enum):
    """
    Selection policy for list-style widgets. `None_` disables
    selection entirely, `Single` allows one selected row at a time,
    and `Extended` lets the user pick multiple rows with Ctrl/Shift.
    """

    Single = 1

    Extended = 3

class WLabel(WInteractWidget):
    """
    An HTML `<label>` element. Renders short text (or an image) that
    describes a sibling form input; clicking the label transfers
    focus to the buddy.

        edit = container.add_widget(wt.WLineEdit())
        label = container.add_widget(wt.WLabel('Email:'))
        label.set_buddy(edit)
    """

    @overload
    def __init__(self) -> None:
        """Construct an empty label with no text or image."""

    @overload
    def __init__(self, text: str) -> None:
        """Construct a label displaying `text`."""

    @property
    def text(self) -> str:
        """The label's text. Assigning replaces the current content."""

    @text.setter
    def text(self, arg: str, /) -> None: ...

    def set_buddy(self, buddy: WFormWidget) -> None:
        """
        Associate the label with a form widget. Clicking the label
        then forwards focus to `buddy` (the HTML `for` attribute is
        wired to the buddy's id).
        """

    @property
    def word_wrap(self) -> bool:
        """
        Whether long text wraps to multiple lines. When False the
        label is rendered on a single line.
        """

    @word_wrap.setter
    def word_wrap(self, arg: bool, /) -> None: ...

    def set_image(self, image: WImage) -> None:
        """
        Display a WImage in place of (or alongside) the label text.
        Takes ownership of `image`; the Python wrapper is re-armed
        as a non-owning alias.
        """

class WBreak(WWidget):
    """
    A line break — renders as `<br>`. Drop one into a container to
    force the following widget onto a new line.

        container.add_widget(wt.WText('First line'))
        container.add_widget(wt.WBreak())
        container.add_widget(wt.WText('Second line'))
    """

    def __init__(self) -> None:
        """Construct a line break."""

class WTextArea(WFormWidget):
    """
    Multi-line text input — renders as `<textarea>`. Use for longer
    free-form input that wouldn't fit on a single line.

        notes = container.add_widget(wt.WTextArea())
        notes.rows = 8
        notes.columns = 60
        notes.placeholder = 'Add notes…'
    """

    @overload
    def __init__(self) -> None:
        """Construct an empty text area."""

    @overload
    def __init__(self, text: str) -> None:
        """Construct a text area pre-filled with `text`."""

    @property
    def text(self) -> str:
        """
        The current input value. Reads what the user has typed;
        assigning replaces the contents.
        """

    @text.setter
    def text(self, arg: str, /) -> None: ...

    @property
    def rows(self) -> int:
        """Visible row count — the HTML `rows` attribute."""

    @rows.setter
    def rows(self, arg: int, /) -> None: ...

    @property
    def columns(self) -> int:
        """Visible column count — the HTML `cols` attribute."""

    @columns.setter
    def columns(self, arg: int, /) -> None: ...

    @property
    def placeholder(self) -> str:
        """Greyed-out hint shown when the field is empty."""

    @placeholder.setter
    def placeholder(self, arg: str, /) -> None: ...

    @property
    def selection_start(self) -> int:
        """
        Character index where the current text selection begins, or
        -1 if there is no selection.
        """

    @property
    def has_selected_text(self) -> bool:
        """True if the user currently has text selected."""

    @property
    def cursor_position(self) -> int:
        """Character index of the caret, as of the last client update."""

class WSpinBox(WLineEdit):
    """
    Integer-valued numeric input with up/down stepper buttons.

        qty = container.add_widget(wt.WSpinBox())
        qty.set_range(1, 99)
        qty.single_step = 1
        qty.value_changed.connect(lambda v: print('picked', v))
    """

    def __init__(self) -> None:
        """Construct a spin box at value 0."""

    @property
    def value(self) -> int:
        """The current integer value."""

    @value.setter
    def value(self, arg: int, /) -> None: ...

    @property
    def minimum(self) -> int:
        """Lower bound on `value` enforced by the stepper buttons."""

    @minimum.setter
    def minimum(self, arg: int, /) -> None: ...

    @property
    def maximum(self) -> int:
        """Upper bound on `value` enforced by the stepper buttons."""

    @maximum.setter
    def maximum(self, arg: int, /) -> None: ...

    @property
    def single_step(self) -> int:
        """Amount the stepper buttons add or subtract per click."""

    @single_step.setter
    def single_step(self, arg: int, /) -> None: ...

    def set_range(self, minimum: int, maximum: int) -> None:
        """Set `minimum` and `maximum` in a single call."""

    @property
    def wrap_around(self) -> bool:
        """
        Whether stepping past the maximum loops back to the minimum
        (and vice-versa).
        """

    @wrap_around.setter
    def wrap_around(self, arg: bool, /) -> None: ...

    @property
    def value_changed(self) -> IntSignal:
        """
        Fires with the new int value whenever the user
        commits a change.
        """

class WDoubleSpinBox(WLineEdit):
    """
    Floating-point spin box. Same surface as WSpinBox but the value
    is a double and `decimals` controls display precision.

        price = container.add_widget(wt.WDoubleSpinBox())
        price.set_range(0.0, 1000.0)
        price.decimals = 2
        price.single_step = 0.05
    """

    def __init__(self) -> None:
        """Construct a spin box at value 0.0."""

    @property
    def value(self) -> float:
        """The current double value."""

    @value.setter
    def value(self, arg: float, /) -> None: ...

    @property
    def minimum(self) -> float:
        """Lower bound on `value`."""

    @minimum.setter
    def minimum(self, arg: float, /) -> None: ...

    @property
    def maximum(self) -> float:
        """Upper bound on `value`."""

    @maximum.setter
    def maximum(self, arg: float, /) -> None: ...

    @property
    def single_step(self) -> float:
        """Amount the stepper buttons add or subtract per click."""

    @single_step.setter
    def single_step(self, arg: float, /) -> None: ...

    @property
    def decimals(self) -> int:
        """Number of decimal places shown when formatting `value`."""

    @decimals.setter
    def decimals(self, arg: int, /) -> None: ...

    def set_range(self, minimum: float, maximum: float) -> None:
        """Set `minimum` and `maximum` in a single call."""

    @property
    def value_changed(self) -> DoubleSignal:
        """
        Fires with the new double value whenever the user
        commits a change.
        """

class WSlider(WFormWidget):
    """
    Integer slider — a draggable handle along a track. Orientation
    can be horizontal (default) or vertical.

        vol = container.add_widget(wt.WSlider(wt.Orientation.Horizontal))
        vol.set_range(0, 100)
        vol.tick_interval = 10
        vol.value_changed.connect(lambda v: mixer.set_volume(v))
    """

    @overload
    def __init__(self) -> None:
        """Construct a horizontal slider at value 0."""

    @overload
    def __init__(self, orientation: Orientation) -> None:
        """Construct a slider with the given orientation."""

    @property
    def value(self) -> int:
        """The current integer position along the track."""

    @value.setter
    def value(self, arg: int, /) -> None: ...

    @property
    def minimum(self) -> int:
        """Value at the leftmost (or bottom-most) end of the track."""

    @minimum.setter
    def minimum(self, arg: int, /) -> None: ...

    @property
    def maximum(self) -> int:
        """Value at the rightmost (or top-most) end of the track."""

    @maximum.setter
    def maximum(self, arg: int, /) -> None: ...

    @property
    def step(self) -> int:
        """Smallest increment the handle snaps to as the user drags."""

    @step.setter
    def step(self, arg: int, /) -> None: ...

    @property
    def tick_interval(self) -> int:
        """
        Spacing between visible tick marks along the track. Zero
        disables tick rendering.
        """

    @tick_interval.setter
    def tick_interval(self, arg: int, /) -> None: ...

    def set_range(self, minimum: int, maximum: int) -> None:
        """Set `minimum` and `maximum` in a single call."""

    def set_orientation(self, orientation: Orientation) -> None:
        """Switch between Horizontal and Vertical layouts."""

    @property
    def value_changed(self) -> IntSignal:
        """
        Fires with the new int value when the user moves
        the handle.
        """

class WComboBox(WFormWidget):
    """
    Drop-down list — renders as `<select>` with one row visible.
    Populate via `add_item` / `add_items` and observe selection
    changes through `activated` or `string_activated`.

        cb = container.add_widget(wt.WComboBox())
        cb.add_items(['Red', 'Green', 'Blue'])
        cb.string_activated.connect(lambda s: print('picked', s))
    """

    def __init__(self) -> None:
        """Construct an empty combo box."""

    def add_item(self, text: str) -> None:
        """
        Append a new item with the given label to the end of the
        drop-down list.
        """

    def add_items(self, items: Sequence[str]) -> None:
        """Bulk version of `add_item`. Appends each label in order."""

    def insert_item(self, index: int, text: str) -> None:
        """
        Insert a new item at position `index`; existing items at
        and after that position shift down.
        """

    def remove_item(self, index: int) -> None:
        """Remove the item at position `index`."""

    @property
    def count(self) -> int:
        """Number of items currently in the drop-down."""

    def item_text(self, index: int) -> str:
        """Return the label of the item at position `index`."""

    def set_item_text(self, index: int, text: str) -> None:
        """Replace the label of the item at position `index`."""

    @property
    def current_index(self) -> int:
        """
        Index of the selected item, or -1 if none is selected.
        Assigning programmatically does NOT fire `activated`.
        """

    @current_index.setter
    def current_index(self, arg: int, /) -> None: ...

    def clear(self) -> None:
        """Remove every item; the combo box ends up empty."""

    @property
    def activated(self) -> IntSignal:
        """
        Fires with the int index of the newly-selected item
        when the user picks something.
        """

    @property
    def string_activated(self) -> StringSignal:
        """
        Fires with the WString label of the newly-selected
        item. Convenient when you don't need the index.
        """

class WSelectionBox(WComboBox):
    """
    Multi-row list-box — renders as `<select size=N>` showing several
    items at once. Inherits the populate / query surface from
    WComboBox; adds vertical sizing and multi-select.

        sb = container.add_widget(wt.WSelectionBox())
        sb.add_items(['Apples', 'Pears', 'Plums'])
        sb.vertical_size = 6
        sb.set_selection_mode(wt.SelectionMode.Extended)
    """

    def __init__(self) -> None:
        """Construct an empty selection box."""

    @property
    def vertical_size(self) -> int:
        """
        Number of rows visible without scrolling — the HTML `size`
        attribute.
        """

    @vertical_size.setter
    def vertical_size(self, arg: int, /) -> None: ...

    def set_selection_mode(self, mode: SelectionMode) -> None:
        """
        Choose between Single and Extended selection (see
        SelectionMode).
        """

    def set_selected_indexes(self, selection: "std::set<int, std::less<int>, std::allocator<int> >") -> None:
        """
        Replace the current selection with the given set of int
        indices. Only meaningful in Extended mode.
        """

    def clear_selection(self) -> None:
        """Deselect every item."""

class WRadioButton(WFormWidget):
    """
    A single radio button. On its own, a radio acts like a checkbox
    with a different glyph; the mutual-exclusion behavior comes from
    adding several to the same WButtonGroup.

        group = wt.WButtonGroup()
        red = container.add_widget(wt.WRadioButton('Red'))
        grn = container.add_widget(wt.WRadioButton('Green'))
        group.add_button(red)
        group.add_button(grn)
        red.on_check.connect(lambda: print('red'))
    """

    @overload
    def __init__(self) -> None:
        """Construct an unlabelled radio button in the unchecked state."""

    @overload
    def __init__(self, text: str) -> None:
        """Construct a labelled radio; `text` renders next to the dot."""

    @property
    def checked(self) -> bool:
        """
        The current boolean state. Assigning programmatically does
        NOT fire `on_check`/`on_uncheck`.
        """

    @checked.setter
    def checked(self, arg: bool, /) -> None: ...

    @property
    def on_check(self) -> EventSignal:
        """Fires when the user selects this radio."""

    @property
    def on_uncheck(self) -> EventSignal:
        """
        Fires when this radio loses its selected state because a
        sibling in the same group was picked.
        """

class WButtonGroup(WObject):
    """
    Mutual-exclusion group for a set of WRadioButtons. Adding a
    radio to a group makes it part of the same logical choice — at
    most one button in the group can be checked at a time. The
    group itself is not a widget; it's a coordinator.

        group = wt.WButtonGroup()
        for label in ['Free', 'Pro', 'Enterprise']:
            rb = container.add_widget(wt.WRadioButton(label))
            group.add_button(rb)
    """

    def __init__(self) -> None:
        """
        Construct an empty button group. Add WRadioButtons via
        `add_button`.
        """

    def add_button(self, button: WRadioButton, id: int = -1) -> None:
        """
        Enroll `button` in the group. `id` is an optional integer
        tag returned by `checked_id` — pass -1 (the default) to
        auto-assign.
        """

    def remove_button(self, button: WRadioButton) -> None:
        """
        Detach `button` from the group. The button keeps existing
        as an independent radio.
        """

    @property
    def count(self) -> int:
        """Number of buttons currently in the group."""

    @property
    def checked_id(self) -> int:
        """
        The `id` of the currently-selected button (the value passed
        to `add_button`), or -1 if none is selected.
        """

    @property
    def selected_button_index(self) -> int:
        """
        Position in insertion order of the selected button, or -1
        if none is selected. Assigning programmatically toggles the
        corresponding radio's state.
        """

    @selected_button_index.setter
    def selected_button_index(self, arg: int, /) -> None: ...

class WProgressBar(WInteractWidget):
    """
    A horizontal progress indicator. Set `value` between `minimum`
    and `maximum` to render the fill, optionally annotate with a
    format string for the percentage label.

        bar = container.add_widget(wt.WProgressBar())
        bar.set_range(0, 100)
        bar.value = 42
    """

    def __init__(self) -> None:
        """Construct a progress bar with range 0..100 and value 0."""

    @property
    def value(self) -> float:
        """
        The current fill amount. Should sit between `minimum` and
        `maximum`.
        """

    @value.setter
    def value(self, arg: float, /) -> None: ...

    @property
    def minimum(self) -> float:
        """Value corresponding to an empty bar."""

    @minimum.setter
    def minimum(self, arg: float, /) -> None: ...

    @property
    def maximum(self) -> float:
        """Value corresponding to a full bar."""

    @maximum.setter
    def maximum(self, arg: float, /) -> None: ...

    def set_range(self, minimum: float, maximum: float) -> None:
        """Set `minimum` and `maximum` in a single call."""

    def set_format(self, format: str) -> None:
        """
        Format string used to render the percentage label inside
        the bar — e.g. `'%.0f%%'`. Pass an empty WString to hide
        the label.
        """

    @property
    def value_changed(self) -> DoubleSignal:
        """Fires with the new `value` whenever it changes."""

class DateSignal:
    """
    Signal that emits a date payload. Wt::WDate is bridged through
    the datetime caster, so slots receive a Python `datetime.date`
    (or `None` for an invalid date). Same connect/emit shape as the
    other Signal subclasses.
    """

    def __init__(self) -> None:
        """
        Construct a free-standing date signal. Useful for tests or
        ad-hoc signal/slot wiring outside the Wt widget tree.
        """

    def connect(self, callable: Callable) -> Connection:
        """
        Subscribe `callable(date)` to this signal. Returns a
        Connection — call `.disconnect()` on it to unsubscribe.
        """

    def emit(self, arg: datetime.date | None, /) -> None:
        """
        Fire the signal with the given date. Each connected slot
        runs synchronously in turn.
        """

    def disconnect_all_slots(self) -> None:
        """
        Disconnect every slot connected through this binding.
        Releases the Python callable references the connections hold.
        """

class WDateEdit(WLineEdit):
    """
    Line-edit specialised for picking a date. Reads/writes its value
    as a Python `datetime.date` via the `date` property, and shows a
    calendar popup for date selection. Inherits all of WLineEdit's
    text-field plumbing (validators, `changed` signal, etc.).

        picker = container.add_widget(wt.WDateEdit())
        picker.date = date.today()
        picker.bottom = date(2020, 1, 1)
        picker.changed.connect(lambda: log(picker.date))
    """

    def __init__(self) -> None:
        """Construct an empty date edit with no selected date."""

    @property
    def date(self) -> datetime.date | None:
        """
        The selected date as a `datetime.date`, or `None` if the
        field is empty / unparseable.
        """

    @date.setter
    def date(self, arg: datetime.date | None, /) -> None: ...

    @property
    def bottom(self) -> datetime.date | None:
        """
        Earliest accepted date. Dates before this are rejected by
        the built-in validator and the popup grays them out.
        """

    @bottom.setter
    def bottom(self, arg: datetime.date | None, /) -> None: ...

    @property
    def top(self) -> datetime.date | None:
        """Latest accepted date. Companion to `bottom`."""

    @top.setter
    def top(self, arg: datetime.date | None, /) -> None: ...

    def set_format(self, format: str) -> None:
        """
        Set the display / parse format string for the date
        (Wt-style format letters, e.g. 'yyyy-MM-dd').
        """

    def format(self) -> str:
        """The current display / parse format string."""

class WTimeEdit(WLineEdit):
    """
    Line-edit specialised for picking a time of day. Mirror of
    WDateEdit on the time side — reads/writes a Python `datetime.time`
    via the `time` property and inherits the WLineEdit surface.

        picker = container.add_widget(wt.WTimeEdit())
        picker.time = time(9, 30)
        picker.changed.connect(lambda: log(picker.time))
    """

    def __init__(self) -> None:
        """Construct an empty time edit with no selected time."""

    @property
    def time(self) -> datetime.time | None:
        """
        The selected time as a `datetime.time`, or `None` if the
        field is empty / unparseable.
        """

    @time.setter
    def time(self, arg: datetime.time | None, /) -> None: ...

    @property
    def bottom(self) -> datetime.time | None:
        """Earliest accepted time. Values before this fail validation."""

    @bottom.setter
    def bottom(self, arg: datetime.time | None, /) -> None: ...

    @property
    def top(self) -> datetime.time | None:
        """Latest accepted time. Companion to `bottom`."""

    @top.setter
    def top(self, arg: datetime.time | None, /) -> None: ...

    def set_format(self, format: str) -> None:
        """
        Set the display / parse format string for the time
        (e.g. 'HH:mm:ss').
        """

class WCalendar(WWidget):
    """
    Standalone month calendar — a navigable grid that lets the user
    select dates and walk through months/years. Use as a top-level
    calendar widget; for date-picker behaviour embedded in a text
    field, prefer WDateEdit.

        cal = container.add_widget(wt.WCalendar())
        cal.bottom = date(2020, 1, 1)
        cal.activated.connect(lambda d: log('picked', d))

    `selection_changed` fires on any change to the selection set;
    `activated` fires when the user double-clicks (or otherwise
    commits) a single day; `clicked` fires on every single-day click.
    """

    def __init__(self) -> None:
        """Construct an empty calendar showing the current month."""

    def select(self, date: datetime.date | None) -> None:
        """
        Add `date` to the selection. In Single selection mode this
        replaces the previous selection; in Extended mode it adds
        to the set.
        """

    def set_selection_mode(self, mode: SelectionMode) -> None:
        """
        Set the selection model (SelectionMode.Single, .Extended,
        or .None_).
        """

    def browse_to_previous_month(self) -> None:
        """Scroll the visible month back by one."""

    def browse_to_next_month(self) -> None:
        """Scroll the visible month forward by one."""

    def browse_to_previous_year(self) -> None:
        """Scroll the visible year back by one."""

    def browse_to_next_year(self) -> None:
        """Scroll the visible year forward by one."""

    @property
    def current_month(self) -> int:
        """The month (1–12) currently displayed."""

    @property
    def current_year(self) -> int:
        """The year currently displayed."""

    @property
    def bottom(self) -> datetime.date | None:
        """
        Earliest selectable date. Dates before this are rendered
        as un-pickable.
        """

    @bottom.setter
    def bottom(self, arg: datetime.date | None, /) -> None: ...

    @property
    def top(self) -> datetime.date | None:
        """Latest selectable date. Companion to `bottom`."""

    @top.setter
    def top(self, arg: datetime.date | None, /) -> None: ...

    @property
    def selection_changed(self) -> Signal:
        """
        Fires whenever the set of selected dates changes
        (no-arg signal). Read `selection()` for the new state.
        """

    @property
    def activated(self) -> DateSignal:
        """
        DateSignal — fires when the user commits a date
        (typically a double-click). Payload is the activated
        `datetime.date`.
        """

    @property
    def clicked(self) -> DateSignal:
        """
        DateSignal — fires on each single-day click,
        regardless of whether the selection changed.
        """

class WDateValidator(WValidator):
    """
    WValidator that accepts dates within an optional [bottom, top]
    range, parsed against a configurable format string. Attach to a
    WLineEdit (or any WFormWidget) when you want server-side date
    validation independent of WDateEdit.

        v = wt.WDateValidator(date(2020, 1, 1), date(2030, 12, 31))
        edit.set_validator(v)
        edit.validated.connect(lambda r: log(r.state))
    """

    @overload
    def __init__(self) -> None:
        """
        Construct a validator with no range constraints and the
        default date format.
        """

    @overload
    def __init__(self, bottom: datetime.date | None, top: datetime.date | None) -> None:
        """
        Construct a validator that requires the parsed date to lie
        between `bottom` and `top` (inclusive).
        """

    @overload
    def __init__(self, format: str) -> None:
        """
        Construct a validator using `format` as the parse format
        (Wt-style letters, e.g. 'yyyy-MM-dd').
        """

    @property
    def bottom(self) -> datetime.date | None:
        """Earliest accepted date (inclusive)."""

    @bottom.setter
    def bottom(self, arg: datetime.date | None, /) -> None: ...

    @property
    def top(self) -> datetime.date | None:
        """Latest accepted date (inclusive)."""

    @top.setter
    def top(self, arg: datetime.date | None, /) -> None: ...

    def set_format(self, format: str) -> None:
        """Set the format string used to parse / display dates."""

    def format(self) -> str:
        """The current parse format string."""

class WTimeValidator(WRegExpValidator):
    """
    WValidator that accepts time-of-day values within an optional
    [bottom, top] range, parsed against a configurable format string.
    Inherits the regex-validator surface internally but the public
    knobs you usually care about are `format`, `bottom`, and `top`.

        v = wt.WTimeValidator('HH:mm', time(9, 0), time(17, 0))
        edit.set_validator(v)
    """

    @overload
    def __init__(self) -> None:
        """
        Construct a validator with no range constraints and the
        default time format.
        """

    @overload
    def __init__(self, format: str) -> None:
        """
        Construct a validator using `format` as the parse format
        (e.g. 'HH:mm:ss').
        """

    @overload
    def __init__(self, format: str, bottom: datetime.time | None, top: datetime.time | None) -> None:
        """
        Construct a validator using `format` and a [bottom, top]
        time range (both inclusive).
        """

    @property
    def bottom(self) -> datetime.time | None:
        """Earliest accepted time (inclusive)."""

    @bottom.setter
    def bottom(self, arg: datetime.time | None, /) -> None: ...

    @property
    def top(self) -> datetime.time | None:
        """Latest accepted time (inclusive)."""

    @top.setter
    def top(self, arg: datetime.time | None, /) -> None: ...

    def set_format(self, format: str) -> None:
        """Set the format string used to parse / display times."""

    def format(self) -> str:
        """The current parse format string."""

class TextFormat(enum.Enum):
    """
    How a piece of text should be interpreted when rendered.
    `XHTML` is sanitised XHTML — tags allowed but checked for
    common XSS vectors. `UnsafeXHTML` is raw, unfiltered XHTML —
    use only with content you trust completely. `Plain` escapes
    everything so the string appears verbatim in the page.
    """

    XHTML = 0

    UnsafeXHTML = 1

    Plain = 2

class TemplateWidgetIdMode(enum.Enum):
    """
    Policy WTemplate uses when stamping ids on bound widgets.
    `None_` leaves the widget's id alone; `SetObjectName` sets the
    Wt object name to the bind var; `SetId` sets the DOM `id`
    attribute to it.
    """

    SetObjectName = 1

    SetId = 2

class WTemplate(WInteractWidget):
    """
    Renders an XHTML template with `${var}` placeholders that get
    replaced by bound strings, integers, or live child widgets.
    Separates layout (the template text) from behavior (the bound
    widgets and their signal handlers).

        tpl = container.add_widget(wt.WTemplate(
            '<div>${greeting}, ${name}! ${ok-button}</div>'))
        tpl.bind_string('greeting', 'Hello')
        tpl.bind_string('name', user_name)
        tpl.bind_widget('ok-button', wt.WPushButton('OK')
        ).clicked.connect(submit)

    Templates also support conditional blocks: a region wrapped in
    `${<flag>}…${</flag>}` renders only when `set_condition('flag',
    True)` has been called.
    """

    @overload
    def __init__(self) -> None:
        """Construct an empty template. Set `template_text` later."""

    @overload
    def __init__(self, text: str) -> None:
        """Construct a template using `text` as the source markup."""

    @property
    def template_text(self) -> str:
        """
        The template source. Assigning re-renders on the next
        round-trip, preserving any current bindings.
        """

    @template_text.setter
    def template_text(self, arg: str, /) -> None: ...

    def set_template_text(self, text: str, format: TextFormat = TextFormat.XHTML) -> None:
        """
        Replace the template source. `format` controls how `text`
        itself is sanitised (the default XHTML strips XSS-prone
        constructs from the template body).
        """

    def bind_widget(self, var_name: str, widget: _T_Widget) -> _T_Widget:
        """
        Substitute `${var_name}` in the template with a live
        `widget`. Takes ownership and re-arms the Python wrapper
        as a non-owning alias; returns the same wrapper for fluent
        chaining:

            tpl.bind_widget('ok', wt.WPushButton('OK')).clicked.connect(go)
        """

    def bind_string(self, var_name: str, value: str, format: TextFormat = TextFormat.XHTML) -> None:
        """
        Substitute `${var_name}` with `value`, rendered according
        to `format`. Use this for static text content; pick
        `bind_widget` instead when you need a widget to wire
        signals to.
        """

    def bind_int(self, var_name: str, value: int) -> None:
        """
        Substitute `${var_name}` with the decimal rendering of
        `value`.
        """

    def bind_empty(self, var_name: str) -> None:
        """
        Bind `${var_name}` to nothing — useful for clearing a
        placeholder without removing the surrounding template
        markup.
        """

    def resolve_widget(self, var_name: str) -> WWidget:
        """
        Return a non-owning handle to the widget currently bound
        to `var_name`, or None if no widget is bound there.
        """

    @property
    def widget_id_mode(self) -> TemplateWidgetIdMode:
        """
        Controls how bound widgets pick up the bind variable as an
        id. See TemplateWidgetIdMode.
        """

    @widget_id_mode.setter
    def widget_id_mode(self, arg: TemplateWidgetIdMode, /) -> None: ...

    def clear(self) -> None:
        """
        Drop every binding and condition. The template source
        stays as-is.
        """

    def refresh(self) -> None:
        """
        Force a re-render. Normally called automatically after
        bindings change; useful when external state the template
        depends on has shifted.
        """

    def set_condition(self, name: str, value: bool) -> None:
        """
        Set the value of a named condition flag. Regions wrapped
        in `${<name>}…${</name>}` render only while the flag is
        True.
        """

    def condition_value(self, name: str) -> bool:
        """Read the current value of a named condition flag."""

class DialogCode(enum.Enum):
    """
    Outcome of a closed WDialog. `Accepted` if `accept()` was
    called, `Rejected` if `reject()` was called or the dialog was
    dismissed via Escape / close button.
    """

    Rejected = 0

    Accepted = 1

class StandardButton(enum.IntEnum):
    """
    Bit-flag enum identifying the standard buttons a WMessageBox
    can show. Combine with `|` to request several at once:

        box.set_standard_buttons(wt.StandardButton.Ok | wt.StandardButton.Cancel)
    """

    Ok = 1

    Cancel = 2

    Yes = 4

    No = 8

    Abort = 16

    Retry = 32

    Ignore = 64

    YesAll = 128

    NoAll = 256

class DialogCodeSignal:
    """
    Signal payload type for WDialog's `finished` — fires with a
    DialogCode when the dialog closes.
    """

    def connect(self, callable: Callable) -> Connection:
        """
        Subscribe `callable` to the signal. Returns a Connection;
        call `.disconnect()` on it to stop receiving.
        """

    def disconnect_all_slots(self) -> None:
        """
        Disconnect every Python callback currently bound to this
        signal.
        """

class StandardButtonSignal:
    """
    Signal payload type for WMessageBox's `button_clicked` — fires
    with the StandardButton the user picked.
    """

    def connect(self, callable: Callable) -> Connection:
        """
        Subscribe `callable` to the signal. Returns a Connection;
        call `.disconnect()` on it to stop receiving.
        """

    def disconnect_all_slots(self) -> None:
        """
        Disconnect every Python callback currently bound to this
        signal.
        """

class WStackedWidget(WContainerWidget):
    """
    Container that shows exactly one of its children at a time.
    Each child added becomes a `page`; switch via `current_index`
    or `set_current_widget`. Pair with WMenu for wizard-style or
    tabbed navigation that doesn't use WTabWidget's chrome.

        stack = container.add_widget(wt.WStackedWidget())
        stack.add_widget(wt.WText('First page'))
        stack.add_widget(wt.WText('Second page'))
        stack.current_index = 1
    """

    def __init__(self) -> None:
        """Construct an empty stacked widget."""

    @property
    def current_index(self) -> int:
        """
        Index of the visible page (0-based). All other children
        are hidden but kept alive.
        """

    @current_index.setter
    def current_index(self, arg: int, /) -> None: ...

    def set_current_widget(self, widget: WWidget) -> None:
        """
        Show `widget`, which must already be a child of this
        stack.
        """

class WMenuItem(WContainerWidget):
    """
    A single entry in a WMenu. Has a label and optionally a
    `contents` widget that is shown in the menu's associated stack
    when this item is selected. Items can be checkable, closeable,
    or link to an internal/external URL.

        menu.add_item(wt.WMenuItem('Inbox', wt.WText('No messages.')))
    """

    @overload
    def __init__(self, label: str) -> None:
        """
        Construct a menu item with the given label and no contents
        widget. Useful for menus that only fire `item_selected`.
        """

    @overload
    def __init__(self, label: str, contents: WWidget) -> None:
        """
        Construct a menu item with both a label and a contents
        widget. When the menu is paired with a WStackedWidget, the
        contents widget is shown in that stack on selection.
        """

    @property
    def text(self) -> str:
        """The item's label."""

    @text.setter
    def text(self, arg: str, /) -> None: ...

    def set_link(self, link: WLink) -> None:
        """
        Turn the item into a hyperlink — clicking it navigates to
        the given WLink instead of (or in addition to) emitting
        selection.
        """

    @property
    def checkable(self) -> bool:
        """
        Whether the item shows a check mark when selected — turns
        it into a toggleable menu entry.
        """

    @checkable.setter
    def checkable(self, arg: bool, /) -> None: ...

    @property
    def checked(self) -> bool:
        """The checked state, for a checkable item."""

    @checked.setter
    def checked(self, arg: bool, /) -> None: ...

    def select(self) -> None:
        """
        Select this item programmatically, as if the user had
        clicked it. Fires `item_selected` on the parent menu.
        """

    def set_selectable(self, selectable: bool) -> None:
        """
        Whether the item responds to clicks. Disable for section
        headers or dividers.
        """

    def set_closeable(self, closeable: bool) -> None:
        """
        Whether the item shows a close button. The user can then
        remove it from the menu by clicking that button.
        """

class MenuItemSignal:
    """
    Signal payload type for WMenu's `item_selected` — fires with
    the WMenuItem the user picked.
    """

    def connect(self, callable: Callable) -> Connection:
        """
        Subscribe `callable` to the signal. Returns a Connection;
        call `.disconnect()` on it to stop receiving.
        """

    def disconnect_all_slots(self) -> None:
        """
        Disconnect every Python callback currently bound to this
        signal.
        """

class WMenu(WWidget):
    """
    A list of selectable items (sidebar nav, vertical or horizontal
    menu, tab strip…). Pair with a WStackedWidget at construction
    time to have the selected item's `contents` show up in the
    stack automatically.

        stack = container.add_widget(wt.WStackedWidget())
        menu = container.add_widget(wt.WMenu(stack))
        menu.add_item(wt.WMenuItem('Home', wt.WText('Welcome!')))
        menu.add_item(wt.WMenuItem('About', wt.WText('About us.')))
        menu.item_selected.connect(lambda item: print(item.text))
    """

    @overload
    def __init__(self) -> None:
        """Construct a menu without an associated content stack."""

    @overload
    def __init__(self, contents_stack: WStackedWidget) -> None:
        """
        Construct a menu wired to the given WStackedWidget — when
        the user picks an item, the corresponding `contents` widget
        is made the visible page of `contents_stack`.
        """

    @overload
    def add_item(self, label: str) -> WMenuItem:
        """
        Convenience for `add_item(WMenuItem(label))`. Returns a
        non-owning handle to the freshly-constructed item.
        """

    @overload
    def add_item(self, item: _T_MenuItem) -> _T_MenuItem:
        """
        Transfer ownership of `item` to the menu and return the
        same Python wrapper, re-armed as a non-owning alias.
        """

    @overload
    def add_items(self, items: list[_T_MenuItem]) -> list[_T_MenuItem]:
        """
        Bulk version of the widget-taking `add_item`. Returns the
        same wrappers, each re-armed as a non-owning alias.
        """

    @overload
    def add_items(self, labels: Sequence[str]) -> None:
        """
        Bulk version of the string-taking `add_item`. Wraps each
        label in a fresh WMenuItem.
        """

    def select(self, index: int) -> None:
        """
        Programmatically select the item at position `index`.
        Fires `item_selected`.
        """

    def current_item(self) -> WMenuItem:
        """
        Return a non-owning handle to the currently-selected item,
        or None if nothing is selected.
        """

    @property
    def item_selected(self) -> MenuItemSignal:
        """
        Fires with the WMenuItem the user selected (a
        MenuItemSignal).
        """

class WTabWidget(WWidget):
    """
    Tab strip on top of a stacked content area. Each `add_tab`
    registers one tab whose contents are the widget you pass.

        tabs = container.add_widget(wt.WTabWidget())
        tabs.add_tab(wt.WText('General settings.'), 'General')
        tabs.add_tab(wt.WText('Account settings.'), 'Account')
        tabs.current_changed.connect(lambda i: print('on tab', i))
    """

    def __init__(self) -> None:
        """Construct an empty tab widget."""

    def add_tab(self, child: object, label: str) -> WMenuItem:
        """
        Add a new tab whose content is `child` and whose label is
        `label`. Takes ownership of `child` (the Python wrapper is
        re-armed as a non-owning alias). Returns the WMenuItem that
        represents the new tab — useful for further per-tab tweaks.
        """

    @property
    def count(self) -> int:
        """Number of tabs currently in the widget."""

    def index_of(self, widget: WWidget) -> int:
        """
        Return the tab index whose contents are `widget`, or -1
        if `widget` is not a tab's content.
        """

    @property
    def current_index(self) -> int:
        """Index of the visible tab."""

    @current_index.setter
    def current_index(self, arg: int, /) -> None: ...

    def set_tab_enabled(self, index: int, enable: bool) -> None:
        """
        Enable or disable the tab at `index`. Disabled tabs render
        greyed out and can't be selected.
        """

    def set_tab_hidden(self, index: int, hidden: bool) -> None:
        """
        Hide or show the tab at `index`. Hidden tabs keep their
        contents but don't appear in the tab strip.
        """

    def set_tab_closeable(self, index: int, closeable: bool) -> None:
        """Whether the tab at `index` shows a close (×) button."""

    def set_tab_text(self, index: int, label: str) -> None:
        """Set the label shown on the tab at `index`."""

    def tab_text(self, index: int) -> str:
        """Return the current label of the tab at `index`."""

    @property
    def current_changed(self) -> IntSignal:
        """
        Fires with the new int index whenever the active
        tab changes.
        """

class WPanel(WWidget):
    """
    A titled box holding a single central widget. Optionally
    collapsible (the user can fold it down to just the title bar).

        panel = container.add_widget(wt.WPanel())
        panel.title = 'Details'
        panel.collapsible = True
        panel.set_central_widget(wt.WText('More info here.'))
    """

    def __init__(self) -> None:
        """Construct an empty panel."""

    @property
    def title(self) -> str:
        """Text shown in the title bar."""

    @title.setter
    def title(self, arg: str, /) -> None: ...

    def set_title_bar(self, enable: bool) -> None:
        """
        Whether the title bar is rendered. Disabling hides both
        the title and the collapse toggle.
        """

    @property
    def title_bar(self) -> bool:
        """
        Non-owning handle to the title-bar widget — useful for
        adding extra controls (e.g. action buttons) next to the
        title.
        """

    @property
    def collapsible(self) -> bool:
        """
        Whether the panel can be collapsed by the user. Enabling
        adds an expand/collapse toggle to the title bar.
        """

    @collapsible.setter
    def collapsible(self, arg: bool, /) -> None: ...

    @property
    def collapsed(self) -> bool:
        """
        The current collapsed state. Only meaningful when
        `collapsible` is True.
        """

    @collapsed.setter
    def collapsed(self, arg: bool, /) -> None: ...

    def collapse(self) -> None:
        """Fold the panel down to just its title bar."""

    def expand(self) -> None:
        """Restore the panel to its full size."""

    def set_central_widget(self, widget: WWidget) -> None:
        """
        Install `widget` as the panel's single content widget,
        replacing any previous one. The panel takes ownership; the
        Python wrapper is re-armed as a non-owning alias.
        """

class WGroupBox(WContainerWidget):
    """
    A container with a border and a caption — renders as HTML
    `<fieldset>` with a `<legend>`. Use to visually group a few
    related form widgets.

        group = container.add_widget(wt.WGroupBox('Address'))
        group.add_widget(wt.WLineEdit())
        group.add_widget(wt.WLineEdit())
    """

    @overload
    def __init__(self) -> None:
        """Construct an untitled group box."""

    @overload
    def __init__(self, title: str) -> None:
        """Construct a group box captioned `title`."""

    @property
    def title(self) -> str:
        """Caption text — the `<legend>`."""

    @title.setter
    def title(self, arg: str, /) -> None: ...

class WDialog(WWidget):
    """
    A pop-up window with a title bar, content area, and footer.
    Modal by default. Build up the `contents` container, call
    `show()`, and react via the `finished` signal (which fires with
    a DialogCode).

        dlg = wt.WDialog('Confirm')
        dlg.contents.add_widget(wt.WText('Really delete?'))
        ok = dlg.footer.add_widget(wt.WPushButton('OK'))
        cancel = dlg.footer.add_widget(wt.WPushButton('Cancel'))
        ok.clicked.connect(dlg.accept)
        cancel.clicked.connect(dlg.reject)
        dlg.finished.connect(lambda code: print(code))
        dlg.show()
    """

    @overload
    def __init__(self) -> None:
        """Construct a dialog with no title."""

    @overload
    def __init__(self, window_title: str) -> None:
        """Construct a dialog with the given title bar caption."""

    @property
    def window_title(self) -> str:
        """Caption shown in the dialog's title bar."""

    @window_title.setter
    def window_title(self, arg: str, /) -> None: ...

    @property
    def modal(self) -> bool:
        """
        Whether the dialog blocks interaction with the rest of the
        page while it's shown.
        """

    @modal.setter
    def modal(self, arg: bool, /) -> None: ...

    @property
    def closable(self) -> bool:
        """
        Whether the title bar shows a close (×) button that rejects
        the dialog.
        """

    @closable.setter
    def closable(self, arg: bool, /) -> None: ...

    def set_resizable(self, resizable: bool) -> None:
        """Whether the user can drag the dialog's edges to resize it."""

    def show(self) -> None:
        """
        Display the dialog. If modal, blocks page interaction
        until accepted, rejected, or closed.
        """

    def accept(self) -> None:
        """
        Close with `DialogCode.Accepted`. Convenient slot for an
        OK button's `clicked` signal.
        """

    def reject(self) -> None:
        """
        Close with `DialogCode.Rejected`. Convenient slot for a
        Cancel button's `clicked` signal.
        """

    def done(self, result: DialogCode) -> None:
        """Close with an explicit DialogCode."""

    def reject_when_escape_pressed(self, enable: bool = True) -> None:
        """Whether pressing Escape rejects the dialog."""

    @property
    def contents(self) -> WContainerWidget:
        """
        Non-owning handle to the dialog's content container.
        Add the dialog body widgets here.
        """

    @property
    def title_bar_widget(self) -> WContainerWidget:
        """
        Non-owning handle to the title-bar container. Use
        to inject custom controls into the title strip.
        """

    @property
    def footer(self) -> WContainerWidget:
        """
        Non-owning handle to the footer container. Conventional
        place for the OK / Cancel buttons.
        """

    @property
    def result(self) -> DialogCode:
        """Final DialogCode after `accept` / `reject` / `done`."""

    @property
    def finished(self) -> DialogCodeSignal:
        """
        Fires with the DialogCode when the dialog closes
        (a DialogCodeSignal).
        """

class WMessageBox(WDialog):
    """
    Standard alert/confirm dialog — a WDialog preset with a message
    and a row of standard buttons.

        box = wt.WMessageBox()
        box.window_title = 'Confirm'
        box.text = 'Discard unsaved changes?'
        box.set_standard_buttons(wt.StandardButton.Yes | wt.StandardButton.No)
        box.button_clicked.connect(lambda btn: print(btn))
        box.show()
    """

    def __init__(self) -> None:
        """
        Construct an empty message box. Set `text` and `set_standard
        _buttons` before showing.
        """

    @property
    def text(self) -> str:
        """Message body shown in the dialog."""

    @text.setter
    def text(self, arg: str, /) -> None: ...

    def set_standard_buttons(self, buttons: int) -> None:
        """
        Configure which buttons to display. `buttons` is an int
        made by OR-ing StandardButton values together — e.g.
        `StandardButton.Ok | StandardButton.Cancel`.
        """

    @property
    def button_result(self) -> StandardButton:
        """
        The StandardButton the user clicked, available after the
        box has closed.
        """

    @property
    def button_clicked(self) -> StandardButtonSignal:
        """
        Fires with the StandardButton that was clicked (a
        StandardButtonSignal).
        """

class WTableCell(WContainerWidget):
    """
    One cell of a WTable, addressed by (row, column). Inherits
    WContainerWidget — fill it with any widgets you like, the same
    way you'd populate any other container.

        cell = table.element_at(0, 0)
        cell.add_widget(wt.WText('Name'))

    Spans cover adjacent cells: setting `row_span = 2` makes the
    cell occupy two rows starting at this position.
    """

    @property
    def row(self) -> int:
        """0-based row index of this cell within its WTable."""

    @property
    def column(self) -> int:
        """0-based column index of this cell within its WTable."""

    @property
    def row_span(self) -> int:
        """Number of rows the cell occupies (HTML `rowspan`). Default 1."""

    @row_span.setter
    def row_span(self, arg: int, /) -> None: ...

    @property
    def column_span(self) -> int:
        """
        Number of columns the cell occupies (HTML `colspan`).
        Default 1.
        """

    @column_span.setter
    def column_span(self, arg: int, /) -> None: ...

class WTableRow:
    """
    Handle to a row of a WTable. Obtained from `WTable.insert_row`;
    lets you reach the row's cells without going through the parent
    table.
    """

    @property
    def row_num(self) -> int:
        """0-based index of this row within its WTable."""

    def element_at(self, column: int) -> WTableCell:
        """
        Return the WTableCell at `column` in this row. Same cell
        you'd get from `table.element_at(self.row_num, column)`.
        """

class WTableColumn:
    """
    Handle to a column of a WTable. Obtained from
    `WTable.insert_column` — chiefly useful for setting column-wide
    styling or width.
    """

    @property
    def column_num(self) -> int:
        """0-based index of this column within its WTable."""

class WTable(WInteractWidget):
    """
    A plain HTML `<table>` widget. Cells grow on demand: ask for
    `element_at(r, c)` and any missing rows/columns are auto-created.

        table = container.add_widget(wt.WTable())
        table.element_at(0, 0).add_widget(wt.WText('Header'))
        table.element_at(1, 0).add_widget(wt.WText('Row 1'))

    Use a WTableView with a model when the data is dynamic or large
    enough that auto-growing cells would be wasteful. WTable is the
    right pick for hand-laid-out small tables.
    """

    def __init__(self) -> None:
        """Construct an empty 0-by-0 table."""

    def element_at(self, row: int, column: int) -> WTableCell:
        """
        Return the WTableCell at (row, column), creating empty
        rows/columns up to that position if they do not exist yet.
        Then populate it like any other container:

            table.element_at(2, 3).add_widget(wt.WText('cell'))
        """

    @property
    def row_count(self) -> int:
        """Total number of rows currently in the table."""

    @property
    def column_count(self) -> int:
        """Total number of columns currently in the table."""

    def clear(self) -> None:
        """
        Remove every row and column. After this, `row_count` and
        `column_count` are both 0 and previously-returned cell
        references are dangling.
        """

    def remove_row(self, row: int) -> WTableRow:
        """
        Remove the row at the given index. Subsequent rows shift up
        by one; any cached WTableCell pointers for the removed row
        become invalid.
        """

    def remove_column(self, column: int) -> WTableColumn:
        """
        Remove the column at the given index. Subsequent columns
        shift left by one.
        """

    def insert_row(self, row: int) -> WTableRow:
        """
        Insert a fresh empty row at index `row` (existing rows
        shift down). Returns the WTableRow handle for the new row.
        """

    def insert_column(self, column: int) -> WTableColumn:
        """
        Insert a fresh empty column at index `column` (existing
        columns shift right). Returns the WTableColumn handle.
        """

class WLayout:
    """
    Abstract base of every layout manager. A layout is installed
    into a WContainerWidget via `container.set_layout(layout)` and
    from then on decides how the container's children are sized
    and positioned — the container's own `add_widget` order is
    ignored. Use the concrete subclasses (WHBoxLayout, WVBoxLayout,
    WGridLayout, WBorderLayout, WFitLayout) instead of this type.
    """

class LayoutDirection(enum.Enum):
    """
    Direction in which a WBoxLayout places its children — horizontal
    (LeftToRight / RightToLeft) or vertical (TopToBottom /
    BottomToTop).
    """

    LeftToRight = 0

    RightToLeft = 1

    TopToBottom = 2

    BottomToTop = 3

class WBoxLayout(WLayout):
    """
    Linear layout — places children in a single row or column
    depending on its LayoutDirection. The two thin subclasses
    WHBoxLayout and WVBoxLayout are usually more convenient.

    Each child has a `stretch` weight that determines how
    extra space is divided up; stretch 0 means natural size, and
    higher values get a proportionally larger share.
    """

    def __init__(self, direction: LayoutDirection) -> None:
        """Construct a box layout with the given LayoutDirection."""

    def add_widget(self, widget: _T_Widget, stretch: int = 0) -> _T_Widget:
        """
        Append `widget` to the layout with the given stretch
        weight. Takes ownership; the Python wrapper is re-armed as
        a non-owning alias and returned for fluent chaining:

            layout.add_widget(wt.WPushButton('Go')).clicked.connect(go)
        """

    def add_widgets(self, widgets: list[_T_Widget]) -> list[_T_Widget]:
        """
        Bulk version of `add_widget` with stretch=0 for every
        child. Use the single-call form if you need per-widget
        stretch values.
        """

    def add_stretch(self, stretch: int = 1) -> None:
        """
        Insert a flexible spacer with the given stretch weight.
        Useful for pushing the next widget to one end of the row
        or column.
        """

    def add_spacing(self, size_px: float) -> None:
        """Insert a fixed-size gap of `size_px` pixels."""

class WHBoxLayout(WBoxLayout):
    """
    Horizontal box layout — children are arranged left-to-right.
    Equivalent to `WBoxLayout(LayoutDirection.LeftToRight)`.

        row = wt.WHBoxLayout()
        container.set_layout(row)
        row.add_widget(wt.WText('Label:'))
        row.add_widget(wt.WLineEdit(), 1)
    """

    def __init__(self) -> None:
        """Construct an empty horizontal box layout."""

class WVBoxLayout(WBoxLayout):
    """
    Vertical box layout — children are arranged top-to-bottom.
    Equivalent to `WBoxLayout(LayoutDirection.TopToBottom)`.

        col = wt.WVBoxLayout()
        container.set_layout(col)
        col.add_widget(wt.WText('Header'))
        col.add_widget(wt.WText('Body'), 1)
    """

    def __init__(self) -> None:
        """Construct an empty vertical box layout."""

class WGridLayout(WLayout):
    """
    Two-dimensional grid layout — children sit at explicit (row,
    column) coordinates and can span multiple cells. Rows and
    columns auto-size from their contents unless given an explicit
    stretch weight.

        grid = wt.WGridLayout()
        container.set_layout(grid)
        grid.add_widget(wt.WText('Name:'),  0, 0)
        grid.add_widget(wt.WLineEdit(),     0, 1)
        grid.add_widget(wt.WText('Notes:'), 1, 0)
        grid.add_widget(wt.WTextArea(),     1, 1)
        grid.set_column_stretch(1, 1)
    """

    def __init__(self) -> None:
        """Construct an empty grid layout."""

    def add_widget(self, widget: _T_Widget, row: int, column: int, row_span: int = 1, column_span: int = 1) -> _T_Widget:
        """
        Place `widget` at the given grid coordinates, optionally
        spanning several rows or columns. Takes ownership; the
        Python wrapper is re-armed as a non-owning alias and
        returned for fluent chaining.
        """

    def set_row_stretch(self, row: int, stretch: int) -> None:
        """
        Set the stretch weight for `row`. Rows with positive
        stretch absorb extra vertical space proportionally.
        """

    def set_column_stretch(self, column: int, stretch: int) -> None:
        """
        Set the stretch weight for `column`. Columns with positive
        stretch absorb extra horizontal space proportionally.
        """

    @property
    def row_count(self) -> int:
        """Number of rows the grid currently uses."""

    @property
    def column_count(self) -> int:
        """Number of columns the grid currently uses."""

class EntryPointType(enum.Enum):
    """
    Selects the deployment mode for an entry point added via
    `WServer.add_entry_point`. `Application` is the standard mode —
    Wt owns the page and renders into it. `WidgetSet` embeds Wt
    widgets into an existing host page that Wt does not own.
    `StaticResource` serves a single resource (file/blob) without
    spinning up a session.
    """

    Application = 0

    WidgetSet = 1

    StaticResource = 2

class WServer:
    """
    Process-wide HTTP server hosting one or more Wt entry points.
    Construct one, configure it via `set_server_configuration` (which
    parses options out of argv — docroot, listen address, port, …),
    register entry points with `add_entry_point`, then call `run` to
    enter the event loop.

        def create_app(env):
            app = wt.WApplication(env)
            app.root.add_widget(wt.WText('Hello.'))
            return app

        server = wt.WServer()
        server.set_server_configuration(sys.argv)
        server.add_entry_point(wt.EntryPointType.Application, create_app)
        server.run()

    `post(session_id, fn)` and `post_all(fn)` are the recommended
    way to push work from a background thread into a Wt session's
    event loop — Wt acquires the session's update lock around `fn`,
    so widget mutations inside it are safe. Combine with
    `WObject.bind_safe` to make the callback no-op if its target
    widget has been destroyed in the meantime.
    """

    @overload
    def __init__(self) -> None:
        """
        Construct a server with no configuration. Call
        `set_server_configuration` and `add_entry_point` before
        `run`.
        """

    @overload
    def __init__(self, application_path: str) -> None:
        """
        Construct a server tagged with `application_path` — used by
        Wt's logging to identify which app this server hosts.
        """

    def set_server_configuration(self, argv: Sequence[str], wt_config: str = '') -> None:
        """
        Parse Wt's standard command-line options out of `argv` (the
        same flags `wthttpd` accepts: --docroot, --http-address,
        --http-port, etc.). Pass `sys.argv` directly. `wt_config`
        optionally points at a wt_config.xml; empty for defaults.
        """

    def add_entry_point(self, type: EntryPointType, factory: object, path: str = '/', favicon: str = '') -> None:
        """
        Register a Python callable as the entry point at `path`.
        Each new browser session triggers `factory(env)` on a Wt
        worker thread; return the per-session WApplication.
        `favicon` optionally overrides the default /favicon.ico.

            def create_app(env):
                app = wt.WApplication(env)
                app.root.add_widget(wt.WText('Hello.'))
                return app
            server.add_entry_point(wt.EntryPointType.Application,
                                   create_app)
        """

    def add_resource(self, resource: WResource, path: str) -> None:
        """
        Mount `resource` at the given URL path on this server. The path is process-wide (independent of any session). Returns nothing; clients fetch via `http://<server>/<path>`.
        """

    def start(self) -> bool:
        """
        Start listening without blocking. Returns immediately —
        use `wait_for_shutdown` or your own signal loop afterwards.
        For the simple case, prefer `run` which does both.
        """

    def stop(self) -> None:
        """
        Stop accepting new connections and tear down existing
        sessions cleanly. Counterpart to `start`.
        """

    def run(self) -> None:
        """
        Start the server and block until shutdown is requested.
        Releases the GIL while inside the event loop so Python
        factory callbacks fired on Wt worker threads can re-acquire
        it. Returns the exit code (0 on clean shutdown).
        """

    def is_running(self) -> bool:
        """True iff the server is currently accepting requests."""

    @staticmethod
    def wait_for_shutdown() -> int:
        """
        Block the calling thread until a shutdown signal arrives
        (SIGINT / SIGTERM). Pair with `start` for non-blocking
        startup, or use `run` to combine both in one call.
        """

    def post(self, session_id: str, function: Callable[[], None], fallback: Callable[[], None] | None = None) -> None:
        """
        Schedule `function` to run inside the given session's event
        loop, with the session's update lock held — making widget
        mutations safe. This is the recommended cross-thread path
        for pushing updates from a background worker.

            def refresh():
                label.text = compute()
                app.trigger_update()
            server.post(session_id, label.bind_safe(refresh))

        Wrap the callback with `WObject.bind_safe` so it no-ops if
        the target widget has been destroyed before the post fires.
        If the session is gone entirely, `fallback` is called (if
        given). Returns immediately; thread-safe.
        """

    def post_all(self, function: Callable[[], None]) -> None:
        """
        Schedule `function` to run inside every currently-active
        session, each with its own update lock held. Thread-safe.
        Useful for broadcast-style updates (e.g. 'system going down
        in 5 minutes').
        """

class WTheme(WObject):
    """
    Abstract base for everything assignable to `WApplication.theme`.
    A theme decides the CSS classes Wt's widgets receive, what extra
    stylesheets/scripts the application pulls in, and how form-state
    decorations (disabled, focus, validation) render.

    Not directly instantiable from Python — pick one of the bundled
    subclasses (WCssTheme, WBootstrap5Theme, WBootstrap3Theme,
    WBootstrap2Theme) and hand it to the application:

        app.theme = wt.WBootstrap5Theme()
    """

    def name(self) -> str:
        """Theme identifier — e.g. 'polished', 'bootstrap5'."""

    def resources_url(self) -> str:
        """URL prefix where the theme's CSS / asset files are served from."""

class WCssTheme(WTheme):
    """
    A plain-CSS theme keyed by name. The name selects which CSS
    bundle Wt loads from `<resources>/themes/<name>/wt.css`. Two
    names — `'default'` and `'polished'` — refer to the bundled
    stylesheets that ship with Wt.

        app.theme = wt.WCssTheme('polished')

    For richer presets, use one of the Bootstrap themes.
    """

    def __init__(self, name: str) -> None:
        """
        Construct a plain-CSS theme — pass 'default' or 'polished' to use Wt's built-in styles, or any name that matches a CSS file you serve at <resources>/themes/<name>/wt.css.
        """

class WBootstrap5Theme(WTheme):
    """
    Bootstrap 5 visual style. The most current of the bundled themes;
    preferred for new applications. Bootstrap's CSS and JS are served
    automatically from Wt's bundled resources tree — no extra setup.

        app.theme = wt.WBootstrap5Theme()
    """

    def __init__(self) -> None:
        """
        Construct a Bootstrap 5 theme. Attach it to an application with `app.theme = wt.WBootstrap5Theme()`.
        """

class WBootstrap2Theme(WTheme):
    """
    Legacy Bootstrap 2 visual style. Kept around for applications
    that haven't migrated to a newer Bootstrap; pick WBootstrap5Theme
    for new code.
    """

    def __init__(self) -> None:
        """
        Bootstrap 2 theme. Useful for older apps; new code should prefer WBootstrap5Theme.
        """

class WBootstrap3Theme(WTheme):
    """
    Bootstrap 3 visual style. Useful when the surrounding ecosystem
    (plugins, third-party widgets) is still on Bootstrap 3; new code
    should prefer WBootstrap5Theme.
    """

    def __init__(self) -> None:
        """
        Bootstrap 3 theme. Useful for apps tracking the Bootstrap-3 ecosystem; new code should prefer WBootstrap5Theme.
        """

class WTimer(WObject):
    """
    Session-bound timer that fires its `timeout` signal at a fixed
    interval. The signal is delivered on the Wt session thread under
    the application's update lock, so slots can touch widgets directly
    without going through `WServer.post` or an `UpdateLock`.

        from datetime import timedelta
        clock = wt.WTimer()
        clock.interval = timedelta(seconds=1)
        def tick():
            label.text = time.strftime('%H:%M:%S')
        clock.timeout.connect(tick)
        clock.start()

    Set `single_shot = True` before `start()` to fire once and stop;
    otherwise the timer repeats until `stop()` is called. Reads of
    `interval` come back as a `datetime.timedelta`.
    """

    def __init__(self) -> None:
        """
        Construct an inactive timer with a zero interval. Set
        `interval` (and optionally `single_shot`), connect `timeout`,
        then call `start()`.
        """

    @property
    def interval(self) -> datetime.timedelta:
        """
        Time between successive timer firings, as a datetime.timedelta. Re-assigning while the timer is active reschedules it.
        """

    @interval.setter
    def interval(self, arg: datetime.timedelta | float, /) -> None: ...

    @property
    def is_active(self) -> bool:
        """
        True between start() and stop() (or first timeout when single_shot is True).
        """

    @property
    def single_shot(self) -> bool:
        """When True, the timer fires exactly once and then deactivates."""

    @single_shot.setter
    def single_shot(self, arg: bool, /) -> None: ...

    def start(self) -> None:
        """
        Begin firing the timeout signal at every interval. No-op if the timer is already active.
        """

    def stop(self) -> None:
        """Stop a running timer. Safe to call from within a timeout slot."""

    @property
    def timeout(self) -> MouseEventSignal:
        """
        EventSignal[WMouseEvent] — fires every interval. The event payload is an implementation artefact; slots typically ignore it.
        """

class UploadedFile:
    """
    One file's worth of metadata + on-disk path for an upload
    delivered through WFileUpload (or returned by
    WFileDropWidget.File.uploaded_file). The bytes live in a Wt-
    managed temp file at `spool_file_name`; read or move them before
    the request that produced this record is torn down — Wt deletes
    the temp file as part of its cleanup unless
    `WFileUpload.steal_spooled_file` has been called.
    """

    @property
    def spool_file_name(self) -> str:
        """
        Filesystem path to the spooled temp file holding the upload's bytes. Read this before the request handler returns — Wt deletes the file on cleanup unless steal_spooled_file is called.
        """

    @property
    def client_file_name(self) -> str:
        """
        Original filename as reported by the browser. Treat as untrusted user input — do NOT use it as a server-side path unchecked.
        """

    @property
    def content_type(self) -> str:
        """MIME type reported by the browser. Same caveat: untrusted."""

class WFileUpload(WWidget):
    """
    Classic HTML file-input widget — a button + filename label.
    Pick a file, call `upload()` (typically right out of the
    `changed` signal), then read the bytes from `spool_file_name`
    when `uploaded` fires.

        up = container.add_widget(wt.WFileUpload())
        def kick_off():
            up.upload()
        def on_done():
            if not up.empty:
                shutil.copy(up.spool_file_name, '/store/last')
        up.changed.connect(kick_off)
        up.uploaded.connect(on_done)

    Set `multiple = True` and walk `uploaded_files` instead of
    `spool_file_name` for multi-file uploads. The bytes land in a
    temp file Wt cleans up after the request; copy/move them
    elsewhere before that happens. For drag-and-drop or queue-style
    uploads use WFileDropWidget instead.
    """

    def __init__(self) -> None:
        """Construct an empty single-file uploader."""

    @property
    def multiple(self) -> bool:
        """
        When True, the browser allows selecting more than one file. After upload, walk `uploaded_files` instead of `spool_file_name`.
        """

    @multiple.setter
    def multiple(self, arg: bool, /) -> None: ...

    @property
    def file_text_size(self) -> int:
        """Approximate visible width of the file-input control in chars."""

    @file_text_size.setter
    def file_text_size(self, arg: int, /) -> None: ...

    @property
    def empty(self) -> bool:
        """True iff no file has been successfully uploaded."""

    @property
    def can_upload(self) -> bool:
        """
        True iff a subsequent call to upload() will start a new upload request (vs. being a no-op).
        """

    @property
    def spool_file_name(self) -> str:
        """
        Filesystem path to the single-file upload's spool file. For multi-uploads use `uploaded_files`.
        """

    @property
    def uploaded_files(self) -> list[UploadedFile]:
        """List of UploadedFile records — one per file the browser sent."""

    def upload(self) -> None:
        """
        Start the upload. Typically called from a slot connected to `changed` so picking a file triggers the upload immediately.
        """

    def set_filters(self, accept_attributes: str) -> None:
        """
        Comma-separated MIME types or extensions used as the HTML accept= attribute, e.g. 'image/png,image/jpeg' or '.csv,.tsv'. Hint only — the browser may still let users pick other files, so re-check content_type server-side.
        """

    @property
    def changed(self) -> EventSignal:
        """
        EventSignal[] — fires when the user picks a file in the browser. Usual slot calls .upload().
        """

    @property
    def uploaded(self) -> EventSignal:
        """
        EventSignal[] — fires when an upload finishes, successful or not. Check `empty` to distinguish.
        """

    @property
    def file_too_large(self) -> "Wt::JSignal<long>":
        """
        JInt64Signal — fires with the rejected file's size in bytes when the user tried to upload more than the configured max-request-size. The upload itself was discarded server-side.
        """

    @property
    def data_received(self) -> "Wt::Signal<unsigned long, unsigned long>":
        """
        Uint64PairSignal — fires periodically during a long upload with (bytes_received, bytes_total). Wire up before calling upload() and pair with set_progress_bar for a built-in progress UI.
        """

class ItemDataRole:
    """
    Identifies which facet of a cell a view is asking for. Models
    store more than just the displayed text per cell — they can
    also hold edit values, decorations (icons), tooltips, style
    classes, hyperlinks, checkbox state, and so on. Each is a
    different ItemDataRole.

        text = model.display_data(model.index(0, 0))
        role = wt.ItemDataRole(wt.ItemDataRole.Display)

    The standard roles are exposed as plain int class attributes
    (Display, Edit, Decoration, ToolTip, StyleClass, Checked, Link,
    …). Wrap one in ItemDataRole(role) when you need the typed
    value to pass into a Wt API.
    """

    def __init__(self, role: int) -> None:
        """
        Construct a role from its integer value. Use the class
        attribute constants (`ItemDataRole.Display`, etc.) rather
        than raw numbers.
        """

    @property
    def value(self) -> int:
        """The underlying integer role identifier."""

    def __eq__(self, arg: ItemDataRole, /) -> bool: ...

    def __lt__(self, arg: ItemDataRole, /) -> bool: ...

    def __hash__(self) -> int: ...

    def __repr__(self) -> str: ...

    Display: int = 0

    Decoration: int = 1

    Edit: int = 2

    StyleClass: int = 3

    Checked: int = 4

    ToolTip: int = 5

    Link: int = 6

    MimeType: int = 7

    Level: int = 8

    MarkerPenColor: int = 16

    MarkerBrushColor: int = 17

    MarkerScaleFactor: int = 20

    MarkerType: int = 21

    BarPenColor: int = 18

    BarBrushColor: int = 19

    User: int = 32

class WModelIndex:
    """
    Lightweight value handle to a single cell of a model, identified
    by (row, column, parent). Returned by model methods like
    `index(row, col)` and used as input wherever a view or proxy
    needs to refer to a cell.

        idx = model.index(2, 0)
        text = model.display_data(idx)

    The default-constructed (and the one returned by `parent()` on
    a top-level row) is the sentinel 'invalid' index — check
    `is_valid` before using it. Comparable and hashable, so it works
    as a dict key or set member.
    """

    def __init__(self) -> None:
        """
        Construct the invalid sentinel index — the same value used
        to mean 'no parent / top level' wherever a parent index is
        expected.
        """

    @property
    def row(self) -> int:
        """0-based row of the cell this index addresses."""

    @property
    def column(self) -> int:
        """0-based column of the cell this index addresses."""

    @property
    def is_valid(self) -> bool:
        """
        False for the root / sentinel index returned by parent() on a top-level item.
        """

    @property
    def internal_id(self) -> int:
        """
        Model-defined opaque id distinguishing tree nodes that share (row, column). Stable for the lifetime of the model item.
        """

    def parent(self) -> WModelIndex:
        """Index of this cell's parent — invalid for top-level rows."""

    def child(self, row: int, column: int) -> WModelIndex:
        """
        Child cell at (row, column) of this index. For non-tree models, only the top-level index has children.
        """

    def __eq__(self, arg: WModelIndex, /) -> bool: ...

    def __lt__(self, arg: WModelIndex, /) -> bool: ...

    def __hash__(self) -> int: ...

    def __repr__(self) -> str: ...

class ModelIndexMouseSignal:
    """
    Two-argument signal fired by item views on click / double-click,
    carrying the WModelIndex of the affected cell and the underlying
    WMouseEvent (buttons, modifiers, coordinates).

        def on_click(index, event):
            if index.is_valid:
                print('clicked row', index.row)
        table_view.clicked.connect(on_click)
    """

    def connect(self, callable: Callable) -> Connection:
        """
        Subscribe `callable` to the signal. The callback receives
        (WModelIndex, WMouseEvent). Returns a Connection — call
        `.disconnect()` on it to unsubscribe.
        """

    def disconnect_all_slots(self) -> None:
        """Drop every Python subscriber from this signal."""

class WAbstractItemModel(WObject):
    """
    Abstract base for everything an item view can render. Models
    expose data as a tree of cells addressed by (row, column,
    parent); flat tables are the special case where no row has
    children. Views (WTableView, WTreeView, …) attach via
    `view.model = some_model` and pull cells through `display_data`
    and the role-typed accessors.

    Not directly constructible from Python — instantiate a concrete
    subclass (WStandardItemModel, WStringListModel) or wrap one in a
    proxy. Writes typically go through the concrete subclass
    (e.g. WStandardItem mutators); this base only exposes the read
    surface and header mutation.
    """

    def row_count(self, parent: WModelIndex = ...) -> int:
        """
        Number of rows under `parent` (top-level when parent is the default invalid index).
        """

    def column_count(self, parent: WModelIndex = ...) -> int:
        """
        Number of columns under `parent` (top-level when parent is
        the default invalid index). For a flat table this is the
        number of columns of the table itself.
        """

    def has_children(self, index: WModelIndex) -> bool:
        """
        True if `index` has any children — i.e. it expands into a
        subtree. Always False for flat list/table models.
        """

    def index(self, row: int, column: int, parent: WModelIndex = ...) -> WModelIndex:
        """
        Build a WModelIndex addressing the cell at (row, column)
        under `parent` (top-level when parent is the default invalid
        index). Returns an invalid index if the coordinates are out
        of range.
        """

    def parent_of(self, index: WModelIndex) -> WModelIndex:
        """
        Parent index of `index`. Invalid for top-level rows. Same
        value as `index.parent()`; provided as a method on the model
        to mirror the C++ API (renamed `parent_of` to avoid colliding
        with Python's `parent` convention elsewhere).
        """

    def display_data(self, index: WModelIndex) -> object:
        """
        The cell's Display-role data stringified — the text a view
        would render for it. Returns None for empty cells. Avoids
        having to deal with the cpp17::any-typed `data()` accessor
        for the common 'just show me what's in the cell' case.
        """

    def set_header_data(self, section: int, value: object) -> bool:
        """
        Set a header label. Accepts str/int/float/bool — anything else is stringified via Python repr.
        """

class WAbstractListModel(WAbstractItemModel):
    """
    Intermediate base for single-column list-shaped models — flat,
    no children. Mostly bound so WStringListModel can declare it as
    its base; users typically interact with the concrete subclass.
    """

class WStringListModel(WAbstractListModel):
    """
    Single-column model whose cells hold strings. Pair with a
    WTableView or feed it to a combo-box-style widget; the simplest
    way to back a UI list with Python data.

        model = wt.WStringListModel(['apples', 'pears', 'plums'])
        view = container.add_widget(wt.WTableView())
        view.model = model
        model.add_string('quinces')
    """

    @overload
    def __init__(self) -> None:
        """Construct an empty string-list model."""

    @overload
    def __init__(self, strings: Sequence[str]) -> None:
        """
        Construct a model populated with `strings` (one row each,
        in order).
        """

    def set_string_list(self, strings: Sequence[str]) -> None:
        """
        Replace every row with `strings`. Attached views are
        notified and redraw.
        """

    def add_string(self, string: str) -> None:
        """Append a single string as a new row at the end."""

    @property
    def string_list(self) -> list[str]:
        """The current list of strings as a Python list of WString."""

class WStandardItem:
    """
    Mutable cell value used by WStandardItemModel. Each cell of a
    table — or each node of a tree — is one WStandardItem holding
    the display text, optional decoration/styling/tooltip, link,
    checkbox state, and any child rows/columns for tree mode.

        item = wt.WStandardItem('Alice')
        item.tool_tip = 'Project lead'
        model.set_item(0, 0, item)
        # mutate in place — the attached view sees the update:
        item.text = 'Alice (PL)'

    Items own their children: `set_child` / `append_row` /
    `set_item` transfer the Python wrapper into Wt's tree (the
    wrapper is re-armed as a non-owning alias, so the same Python
    object keeps working but won't double-free).
    """

    @overload
    def __init__(self) -> None:
        """Construct an empty item with no text."""

    @overload
    def __init__(self, text: str) -> None:
        """Construct an item displaying `text`."""

    @property
    def text(self) -> str:
        """
        The cell's displayed text (the Display-role value).
        Assigning updates attached views on the next round-trip.
        """

    @text.setter
    def text(self, arg: str, /) -> None: ...

    @property
    def icon(self) -> str:
        """
        URL of a small icon shown beside the text (when the view's delegate honours ItemDataRole.Decoration).
        """

    @icon.setter
    def icon(self, arg: str, /) -> None: ...

    @property
    def style_class(self) -> str:
        """
        CSS class applied to this cell's rendered element. Useful
        for per-row colouring or highlighting.
        """

    @style_class.setter
    def style_class(self, arg: str, /) -> None: ...

    @property
    def tool_tip(self) -> str:
        """Hover-tooltip text for this cell."""

    @tool_tip.setter
    def tool_tip(self, arg: str, /) -> None: ...

    def set_link(self, link: WLink) -> None:
        """
        Attach a WLink to the cell, so the rendered text becomes
        clickable and navigates to the link's URL or internal path.
        """

    @property
    def checkable(self) -> bool:
        """
        Whether the cell renders with a checkbox. Set True to show
        one; `checked` then controls its state.
        """

    @checkable.setter
    def checkable(self, arg: bool, /) -> None: ...

    @property
    def checked(self) -> bool:
        """Checkbox state. Only meaningful when `checkable` is True."""

    @checked.setter
    def checked(self, arg: bool, /) -> None: ...

    @property
    def tristate(self) -> bool:
        """
        Whether the checkbox can hold an indeterminate state in
        addition to checked/unchecked.
        """

    @tristate.setter
    def tristate(self, arg: bool, /) -> None: ...

    @property
    def editable(self) -> bool:
        """
        Whether the user can edit the cell in place via the view's
        edit delegate.
        """

    @editable.setter
    def editable(self, arg: bool, /) -> None: ...

    @property
    def has_children(self) -> bool:
        """
        True if this item has any child rows/columns (i.e. forms a
        subtree).
        """

    @property
    def row_count(self) -> int:
        """Number of child rows under this item."""

    @property
    def column_count(self) -> int:
        """Number of child columns under this item."""

    def set_row_count(self, rows: int) -> None:
        """
        Resize the children to have exactly `rows` rows. New rows
        are filled with empty items; excess rows are dropped.
        """

    def set_column_count(self, columns: int) -> None:
        """
        Resize the children to have exactly `columns` columns. New
        columns are filled with empty items; excess are dropped.
        """

    def append_row(self, items: list[WStandardItem]) -> None:
        """
        Append a single child row. Each item's Python wrapper stays usable after the call (re-armed as a non-owning alias).
        """

    def append_column(self, items: list[WStandardItem]) -> None:
        """
        Append a single child column. Each item's Python wrapper
        stays usable after the call (re-armed as a non-owning alias).
        """

    def insert_rows(self, row: int, count: int) -> None:
        """
        Insert `count` empty rows starting at `row`. Existing rows
        at or after that position shift down.
        """

    def insert_columns(self, column: int, count: int) -> None:
        """
        Insert `count` empty columns starting at `column`. Existing
        columns at or after that position shift right.
        """

    def child(self, row: int, column: int = 0) -> WStandardItem:
        """The child item at (row, column) — None if absent."""

    def parent(self) -> WStandardItem:
        """Parent item — None for items in invisibleRootItem()."""

class WStandardItemModel(WAbstractItemModel):
    """
    General-purpose model backed by a grid (or tree) of
    WStandardItem cells. The standard pick when you want to populate
    a WTableView or WTreeView from Python data without writing your
    own model subclass.

        model = wt.WStandardItemModel(0, 2)
        model.set_header_data(0, 'Name')
        model.set_header_data(1, 'Score')
        model.append_row([wt.WStandardItem('Alice'),
                          wt.WStandardItem('42')])
        view = container.add_widget(wt.WTableView())
        view.model = model

    Mutate cells in place by reaching `model.item(row, col)` and
    assigning to its `text`, `checked`, etc. — attached views see
    the change on the next round-trip.
    """

    @overload
    def __init__(self) -> None:
        """Construct an empty 0-by-0 model."""

    @overload
    def __init__(self, rows: int, columns: int) -> None:
        """
        Construct a model pre-sized to `rows` x `columns`, with
        empty WStandardItem cells in every position.
        """

    def clear(self) -> None:
        """Drop every item; rowCount and columnCount go to 0."""

    @property
    def invisible_root_item(self) -> WStandardItem:
        """
        The internal root item. Manipulate it directly for advanced tree construction; for flat tables prefer model.append_row.
        """

    def index_from_item(self, item: WStandardItem) -> WModelIndex:
        """
        WModelIndex of the cell holding `item`, or an invalid index
        if the item is not part of this model.
        """

    def item_from_index(self, index: WModelIndex) -> WStandardItem:
        """
        WStandardItem at `index` — the inverse of `index_from_item`.
        Returns None for the invalid index or out-of-range positions.
        """

    def item(self, row: int, column: int = 0) -> WStandardItem:
        """Top-level item at (row, column)."""

    def set_item(self, row: int, column: int, item: WStandardItem) -> None:
        """
        Place an item at (row, column). Transfers ownership; the Python wrapper is re-armed as a non-owning alias.
        """

    def append_row(self, items: list[WStandardItem]) -> None:
        """
        Append a row of top-level items. The list length should
        match `column_count`; transfers ownership of each item, the
        Python wrappers stay usable as non-owning aliases.
        """

    def append_column(self, items: list[WStandardItem]) -> None:
        """
        Append a column of top-level items. The list length should
        match `row_count`; same ownership transfer as append_row.
        """

class SelectionBehavior(enum.Enum):
    """
    Whether item-view selection operates on individual cells or
    whole rows.
    """

    SelectItems = 0
    """
    Clicks select individual cells; the selection model holds
    WModelIndex values pointing to specific (row, column)
    pairs.
    """

    SelectRows = 1
    """
    Clicks select the whole row; visually the entire row
    highlights.
    """

class SortOrder(enum.Enum):
    """
    Sort direction for column sorts on item views and sort/filter
    proxy models.
    """

    Ascending = 0
    """Smallest / earliest first."""

    Descending = 1
    """Largest / latest first."""

class ScrollHint(enum.Enum):
    """
    How a view should align a target cell within its viewport when
    asked to scroll to it.
    """

    EnsureVisible = 0
    """
    Scroll only as much as needed to make the target visible;
    no scroll if it already is.
    """

    PositionAtTop = 1
    """Scroll so the target sits at the top of the viewport."""

    PositionAtBottom = 2
    """Scroll so the target sits at the bottom of the viewport."""

    PositionAtCenter = 3
    """
    Scroll so the target sits in the vertical middle of the
    viewport.
    """

    PositionAtLeft = 4
    """Scroll so the target column aligns with the left edge."""

    PositionAtRight = 5
    """Scroll so the target column aligns with the right edge."""

    NoScroll = 6
    """Do not scroll at all."""

class WAbstractItemView(WWidget):
    """
    Base widget for views that render a WAbstractItemModel. WTableView
    and WTreeView both derive from this; the shared surface covers
    model attachment, root-index navigation, selection, sorting, and
    the click signals.

        view = container.add_widget(wt.WTableView())
        view.model = model
        view.sorting_enabled = True
        view.selection_behavior = wt.SelectionBehavior.SelectRows
        view.clicked.connect(lambda idx, ev: handle_click(idx))
    """

    @property
    def model(self) -> WAbstractItemModel:
        """
        The attached model (shared_ptr<WAbstractItemModel>). Assign
        a concrete model — or a proxy wrapping one — to populate the
        view; the view re-renders on changes the model emits.
        """

    @model.setter
    def model(self, arg: WAbstractItemModel, /) -> None: ...

    def set_root_index(self, root_index: WModelIndex) -> None:
        """
        Show the children of `root_index` as the view's top-level
        rows. Useful for drilling into a sub-tree of a tree model;
        pass an invalid WModelIndex to reset to showing everything.
        """

    @property
    def root_index(self) -> WModelIndex:
        """
        Current root WModelIndex — the node whose children the view
        is showing as top-level rows.
        """

    def clear_selection(self) -> None:
        """Drop every selected cell/row."""

    def is_selected(self, index: WModelIndex) -> bool:
        """True if `index` is currently part of the selection."""

    def sort_by_column(self, column: int, order: SortOrder) -> None:
        """
        Sort visible rows by `column` in the given SortOrder. The
        underlying model must support sort() for this to take
        effect — e.g. when fronted by a WSortFilterProxyModel.
        """

    @property
    def clicked(self) -> ModelIndexMouseSignal:
        """
        ModelIndexMouseSignal fired when the user clicks a
        cell. Callbacks receive (WModelIndex, WMouseEvent).
        """

    @property
    def double_clicked(self) -> ModelIndexMouseSignal:
        """
        ModelIndexMouseSignal fired on double-click. Same
        payload as `clicked`.
        """

    @property
    def selection_changed(self) -> Signal:
        """
        No-arg signal fired when the selection changes —
        use to refresh detail panes, enable/disable action
        buttons, etc.
        """

    def set_column_width(self, column: int, width: WLength) -> None:
        """Set the rendered width of `column` to the given WLength."""

    @property
    def sorting_enabled(self) -> bool:
        """
        Whether the column headers act as sort toggles. The model
        (or a wrapping sort/filter proxy) must implement sort() for
        the user clicks to have an effect.
        """

    @sorting_enabled.setter
    def sorting_enabled(self, arg: bool, /) -> None: ...

    @property
    def column_resize_enabled(self) -> bool:
        """Whether the user can drag column dividers to resize columns."""

    @column_resize_enabled.setter
    def column_resize_enabled(self, arg: bool, /) -> None: ...

    @property
    def selection_behavior(self) -> SelectionBehavior:
        """
        Whether selection targets individual cells or whole rows
        (a SelectionBehavior value).
        """

    @selection_behavior.setter
    def selection_behavior(self, arg: SelectionBehavior, /) -> None: ...

    @property
    def selection_mode(self) -> SelectionMode:
        """Single vs. multi-select, etc. (a SelectionMode value)."""

    @selection_mode.setter
    def selection_mode(self, arg: SelectionMode, /) -> None: ...

class WTableView(WAbstractItemView):
    """
    Model-driven flat table view. Renders the rows directly under
    its root index as a scrollable grid, one row of cells per row
    of the model. Use with a WStandardItemModel, a WStringListModel,
    or any custom WAbstractItemModel.

        view = container.add_widget(wt.WTableView())
        view.model = model
        view.sorting_enabled = True
        view.clicked.connect(on_row_click)
    """

    def __init__(self) -> None:
        """
        Construct an empty table view. Assign `model` to populate
        it.
        """

    def scroll_to(self, index: WModelIndex, hint: ScrollHint = ScrollHint.EnsureVisible) -> None:
        """
        Scroll so the cell at `index` is positioned per `hint`.
        The default is to bring it into view if it isn't already.
        """

class WTreeView(WAbstractItemView):
    """
    Model-driven tree view. Renders rows hierarchically with
    expand/collapse toggles for any item whose `has_children` is
    true. Suits hierarchical data: directory trees, org charts,
    category browsers.

        view = container.add_widget(wt.WTreeView())
        view.model = standard_model     # any model whose items have children
        view.expand_to_depth(2)
        view.clicked.connect(on_node_click)
    """

    def __init__(self) -> None:
        """
        Construct an empty tree view. Assign `model` to populate
        it.
        """

    def set_expanded(self, index: WModelIndex, expanded: bool) -> None:
        """Expand or collapse the subtree rooted at `index`."""

    def is_expanded(self, index: WModelIndex) -> bool:
        """True if the subtree at `index` is currently expanded."""

    def expand(self, index: WModelIndex) -> None:
        """
        Expand the subtree at `index`. Equivalent to
        `set_expanded(index, True)`.
        """

    def collapse(self, index: WModelIndex) -> None:
        """
        Collapse the subtree at `index`. Equivalent to
        `set_expanded(index, False)`.
        """

    def collapse_all(self) -> None:
        """
        Collapse every expanded node; only the top-level rows
        remain visible.
        """

    def expand_to_depth(self, depth: int) -> None:
        """
        Expand every node whose distance from the root is less
        than `depth`. Depth 0 means everything stays collapsed;
        depth 1 expands the root's immediate children, and so on.
        """

    @property
    def root_is_decorated(self) -> bool:
        """
        Whether top-level rows show an expand/collapse decoration
        (arrow). Turn off to render top-level rows like a flat list
        with the subtrees hanging off them.
        """

    @root_is_decorated.setter
    def root_is_decorated(self, arg: bool, /) -> None: ...

class WAbstractProxyModel(WAbstractItemModel):
    """
    Base class for models that wrap another model and present a
    transformed view of it. Sort/filter, read-only-isation, identity
    pass-through and similar adapters all derive from this. Set the
    underlying model via `source_model`, then attach a view to the
    PROXY (not the source) so it sees the transformed rows.

        proxy = wt.WSortFilterProxyModel()
        proxy.source_model = base_model
        table_view.model = proxy

    Use `map_from_source` / `map_to_source` to translate WModelIndex
    values between the two coordinate systems.
    """

    @property
    def source_model(self) -> WAbstractItemModel:
        """
        The wrapped model. Setting it disconnects from the previous
        source and rewires the proxy.
        """

    @source_model.setter
    def source_model(self, arg: WAbstractItemModel, /) -> None: ...

    def map_from_source(self, source_index: WModelIndex) -> WModelIndex:
        """
        Translate a source-model index to the proxy's coordinate
        system (sorted/filtered/etc. position). Returns an invalid
        index if the source row is filtered out.
        """

    def map_to_source(self, proxy_index: WModelIndex) -> WModelIndex:
        """
        Translate a proxy index back to the source model. Required
        when handing a clicked index back to source-specific logic.
        """

class WIdentityProxyModel(WAbstractProxyModel):
    """
    Proxy that forwards every call to the source model unchanged.
    Useful as a starting point for a custom subclass that only
    tweaks one or two methods (a data-role rewriter, for instance),
    or as a placeholder when an API requires a proxy but no
    transformation is needed yet.
    """

    def __init__(self) -> None:
        """
        Construct an empty identity proxy; assign `source_model`
        to wire it up.
        """

class WReadOnlyProxyModel(WAbstractProxyModel):
    """
    Proxy that forwards reads to the source but refuses every
    mutation (setData, setHeaderData, insertRows, removeRows, …).
    Cheap way to hand a model to a view that must not be allowed to
    edit it — e.g. a preview pane that shares its underlying data
    with an editable master view.

        readonly = wt.WReadOnlyProxyModel()
        readonly.source_model = shared_model
        preview.model = readonly
    """

    def __init__(self) -> None:
        """
        Construct an empty read-only proxy; assign `source_model`
        to wire it up.
        """

class WSortFilterProxyModel(WAbstractProxyModel):
    """
    Proxy that hides rows whose `filter_key_column` value does not
    match a regex, and optionally re-orders the rows it does keep.
    Operates on the rows directly under whatever root index the
    view is showing.

        proxy = wt.WSortFilterProxyModel()
        proxy.source_model = people_model
        proxy.filter_key_column = 1                 # surname column
        proxy.set_filter_regexp('.*smith.*')
        proxy.dynamic_sort_filter = True
        proxy.sort(0, wt.SortOrder.Ascending)       # by first name
        table_view.model = proxy

    The filter regex is implemented with std::regex (ECMAScript
    flavour) and applied as a full-string match — see
    `set_filter_regexp` for details.
    """

    def __init__(self) -> None:
        """
        Construct an empty proxy. Assign `source_model`, then set
        filter/sort parameters as needed.
        """

    @property
    def filter_key_column(self) -> int:
        """
        Column index in the source model whose values are matched
        against the filter regex. Default 0.
        """

    @filter_key_column.setter
    def filter_key_column(self, arg: int, /) -> None: ...

    def set_filter_regexp(self, pattern: str) -> None:
        """
        Set the regex pattern applied to the filter column. Empty
        string disables filtering. Wt uses std::regex_match (FULL-
        STRING match, not substring search), ECMAScript flavour — to
        search for a substring, wrap with wildcards: `.*foo.*`.
        Re-runs the filter immediately when `dynamic_sort_filter` is
        True; otherwise call `invalidate()` afterward.
        """

    @property
    def filter_role(self) -> ItemDataRole:
        """
        Data role read from the filter column before matching against
        the regex. Default Display.
        """

    @filter_role.setter
    def filter_role(self, arg: ItemDataRole, /) -> None: ...

    @property
    def sort_role(self) -> ItemDataRole:
        """
        Data role read when comparing rows during sort. Default
        Display.
        """

    @sort_role.setter
    def sort_role(self, arg: ItemDataRole, /) -> None: ...

    @property
    def sort_column(self) -> int:
        """Current sort column, or -1 when sort() has not been called."""

    @property
    def sort_order(self) -> SortOrder:
        """Current SortOrder in effect (Ascending or Descending)."""

    @property
    def dynamic_sort_filter(self) -> bool:
        """
        When True, the proxy re-runs filter + sort whenever the
        source model changes. False (default) requires an explicit
        invalidate() call after modifications.
        """

    @dynamic_sort_filter.setter
    def dynamic_sort_filter(self, arg: bool, /) -> None: ...

    def invalidate(self) -> None:
        """
        Force a re-evaluation of filter + sort against the current
        source data. Needed after source mutations when
        dynamic_sort_filter is False.
        """

    def sort(self, column: int, order: SortOrder = SortOrder.Ascending) -> None:
        """Sort by the given column. -1 disables sorting."""

class LengthUnit(enum.Enum):
    FontEm = 0

    FontEx = 1

    Pixel = 2

    Inch = 3

    Centimeter = 4

    Millimeter = 5

    Point = 6

    Pica = 7

    Percentage = 8

    ViewportWidth = 9

    ViewportHeight = 10

    ViewportMin = 11

    ViewportMax = 12

class WLength:
    """
    A CSS length — a numeric value paired with a LengthUnit, or the
    special `'auto'` placeholder. Used everywhere Wt accepts a width,
    height, margin, or column dimension. Most APIs that take a length
    also accept a bare float (interpreted as pixels); reach for
    WLength when you need a non-pixel unit.

        panel.set_width(wt.WLength(50, wt.LengthUnit.Percentage))
        margin = wt.WLength('1.5em')           # parsed CSS
    """

    @overload
    def __init__(self) -> None:
        """Default-construct as 'auto' (no explicit length)."""

    @overload
    def __init__(self, value: float, unit: LengthUnit = LengthUnit.Pixel) -> None:
        """
        Construct from a numeric value and a unit (defaults to
        pixels).
        """

    @overload
    def __init__(self, css_text: str) -> None:
        """Parse a CSS length string — e.g. 'auto', '50%', '12px', '1em'."""

    @property
    def is_auto(self) -> bool:
        """True if this is the `'auto'` (default-constructed) length."""

    @property
    def value(self) -> float:
        """The numeric component — pair with `unit` to interpret."""

    @property
    def unit(self) -> LengthUnit:
        """The LengthUnit that scales `value`."""

    def to_css_text(self) -> str:
        """Render as a CSS string Wt's renderer can use."""

    def to_pixels(self, font_size: float = 16.0) -> float:
        """
        Convert to pixels assuming the given root font size (for em/ex/percentage resolution).
        """

    def __repr__(self) -> str: ...

class AnimationEffect(enum.IntEnum):
    SlideInFromLeft = 1

    SlideInFromRight = 2

    SlideInFromBottom = 3

    SlideInFromTop = 4

    Pop = 5

    Fade = 256

class TimingFunction(enum.Enum):
    Ease = 0

    Linear = 1

    EaseIn = 2

    EaseOut = 3

    EaseInOut = 4

    CubicBezier = 5

class WAnimation:
    """
    Describes a show / hide transition. Pass to WWidget.animate_show
    and animate_hide (or use as the second arg to a setHidden overload
    for animated visibility changes). An empty WAnimation means 'no
    transition'; otherwise pick an AnimationEffect, optionally a
    TimingFunction, and a duration in milliseconds.

        panel.animate_show(wt.WAnimation(
            wt.AnimationEffect.SlideInFromBottom,
            wt.TimingFunction.EaseOut, 300))

    Effects can be OR'd together (`SlideInFromLeft | Fade`) to
    combine motion with a fade.
    """

    @overload
    def __init__(self) -> None:
        """Default — an empty animation (no transition)."""

    @overload
    def __init__(self, effects: int, timing: TimingFunction = TimingFunction.Linear, duration_ms: int = 250) -> None:
        """
        Construct from an effect (or `e1 | e2` to combine a slide with Fade). Timing and duration default to Linear / 250ms.
        """

    @property
    def duration(self) -> int:
        """Length of the animation in milliseconds."""

    @duration.setter
    def duration(self, arg: int, /) -> None: ...

    @property
    def timing_function(self) -> TimingFunction:
        """The TimingFunction (easing curve) the animation uses."""

    @timing_function.setter
    def timing_function(self, arg: TimingFunction, /) -> None: ...

    @property
    def empty(self) -> bool:
        """True for the default (no-effect) animation."""

class Touch:
    """
    A single finger contact on a touch-capable device. Bundled
    inside the `touches` / `target_touches` / `changed_touches`
    lists on a WTouchEvent. Read the four coordinate accessors to
    get the contact position in different reference frames.
    """

    def document(self) -> Coordinates:
        """Touch position relative to the document, as Coordinates."""

    def window(self) -> Coordinates:
        """Touch position relative to the visible window."""

    def screen(self) -> Coordinates:
        """Touch position relative to the physical screen."""

    def widget(self) -> Coordinates:
        """Touch position relative to the target widget."""

class WTouchEvent:
    """
    Payload delivered to touch-related event signals. Splits the
    active touches into three views: every finger on the screen,
    only the fingers whose touch started on the target widget, and
    the subset of fingers that changed state in the event firing.
    """

    @property
    def touches(self) -> list[Touch]:
        """List[Touch] — every finger currently touching the screen."""

    @property
    def target_touches(self) -> list[Touch]:
        """List[Touch] — fingers whose touch started inside this widget."""

    @property
    def changed_touches(self) -> list[Touch]:
        """List[Touch] — fingers whose state changed in this event."""

class WGestureEvent:
    """
    Payload for multi-touch pinch and rotate gestures. `scale`
    compares the current finger spread to the start of the gesture
    (1.0 means unchanged, >1 a pinch-out, <1 a pinch-in); `rotation`
    is the angular delta in degrees.
    """

    @property
    def scale(self) -> float:
        """
        Pinch scale relative to the gesture's start (1.0 = no
        change, >1 zoomed out, <1 zoomed in).
        """

    @property
    def rotation(self) -> float:
        """Rotation in degrees relative to the gesture's start."""

class WScrollEvent:
    """
    Payload for scroll-position changes. Reports the current scroll
    offset of the scrolling element together with the viewport
    dimensions, all in CSS pixels.
    """

    @property
    def scroll_x(self) -> int:
        """Horizontal scroll offset in pixels."""

    @property
    def scroll_y(self) -> int:
        """Vertical scroll offset in pixels."""

    @property
    def viewport_width(self) -> int:
        """Visible viewport width in pixels."""

    @property
    def viewport_height(self) -> int:
        """Visible viewport height in pixels."""

class DropEventOriginalEventType(enum.Enum):
    Mouse = 0

    Touch = 1

class WDropEvent:
    """
    Payload delivered to a target widget when something is dropped
    on it. Carries a reference to the source object, the MIME type
    of the dragged data, and the underlying pointer event — either
    a WMouseEvent or a WTouchEvent depending on the input device.

    Inspect `event_type` first to decide which of `mouse_event` /
    `touch_event` is populated; the other is None.
    """

    @property
    def source(self) -> WObject:
        """
        The WObject that was the drag source. Don't outlive the slot call — the pointer's lifetime is the source widget's.
        """

    @property
    def mime_type(self) -> str:
        """
        MIME type of the dragged data, as published by the drag
        source.
        """

    @property
    def event_type(self) -> DropEventOriginalEventType:
        """
        DropEventOriginalEventType — whether the drop originated from a mouse or a touch event.
        """

    @property
    def mouse_event(self) -> WMouseEvent:
        """The originating WMouseEvent, or None when event_type is Touch."""

    @property
    def touch_event(self) -> WTouchEvent:
        """The originating WTouchEvent, or None when event_type is Mouse."""

class JSignal0:
    """
    Parameterless JavaScript signal — a Wt::JSignal<> bridged for
    Python. Fires when the corresponding client-side JS event happens
    (e.g. WNotification's clicked/closed/shown/error).
    """

    def connect(self, callable: Callable) -> Connection:
        """
        Subscribe a no-arg callable. Returns a Connection — call
        `.disconnect()` to stop receiving.
        """

    def disconnect_all_slots(self) -> None:
        """Drop every Python subscriber attached via `connect`."""

class WIcon(WInteractWidget):
    """
    A Font Awesome icon rendered inline. Inherits WInteractWidget so
    `clicked` and the other input signals work without further setup.

        container.add_widget(wt.WIcon('envelope')).clicked.connect(open_inbox)

    The icon name is looked up in the bundled Font Awesome stylesheet,
    which is added to the page lazily on first WIcon construction (or
    explicitly via `load_icon_font`).
    """

    @overload
    def __init__(self) -> None:
        """Construct with no icon — set `name` later."""

    @overload
    def __init__(self, name: str) -> None:
        """Construct with a Font Awesome icon name (e.g. 'play', 'gear')."""

    @property
    def name(self) -> str:
        """
        The Font Awesome icon name. Assigning swaps the rendered
        glyph on the next round-trip.
        """

    @name.setter
    def name(self, arg: str, /) -> None: ...

    @property
    def size(self) -> float:
        """Multiplier on the default icon size. 1.0 = unchanged; 2.0 = doubled."""

    @size.setter
    def size(self, arg: float, /) -> None: ...

    @staticmethod
    def load_icon_font() -> None:
        """
        Add Font Awesome's CSS stylesheet to the application. Called automatically the first time a WIcon is constructed; expose it here for explicit early-load.
        """

class IconType(enum.Enum):
    """Tells WIconPair how to interpret its two icon strings."""

    URI = 0
    """Treat the string as a URL pointing at an image."""

    IconName = 1
    """Treat the string as a Font Awesome icon name."""

class WIconPair(WWidget):
    """
    Two icons displayed one at a time, with optional click-to-toggle
    behavior. Useful for expand/collapse indicators, on/off lamps,
    anywhere a small bistable visual cue is wanted.

        pair = container.add_widget(
            wt.WIconPair('plus-square', 'minus-square'))
        pair.set_icons_type(wt.IconType.IconName)
        pair.icon1_clicked.connect(expand)
        pair.icon2_clicked.connect(collapse)
    """

    def __init__(self, icon1: str, icon2: str, click_is_switch: bool = True) -> None:
        """
        Two icon strings (URLs or Font-Awesome names). When `click_is_switch` is True (default), clicking either icon toggles the visible state.
        """

    @property
    def state(self) -> int:
        """Active icon: 0 → icon1, 1 → icon2."""

    @state.setter
    def state(self, arg: int, /) -> None: ...

    def show_icon1(self) -> None:
        """Equivalent to `state = 0`."""

    def show_icon2(self) -> None:
        """Equivalent to `state = 1`."""

    def set_icon1_type(self, type: IconType) -> None:
        """Set whether icon1's string is a URL or a Font Awesome name."""

    def set_icon2_type(self, type: IconType) -> None:
        """Set whether icon2's string is a URL or a Font Awesome name."""

    def set_icons_type(self, type: IconType) -> None:
        """Shortcut for setting both icons to the same IconType."""

    @property
    def icon1_clicked(self) -> MouseEventSignal:
        """MouseEventSignal — clicks while icon1 is visible."""

    @property
    def icon2_clicked(self) -> MouseEventSignal:
        """MouseEventSignal — clicks while icon2 is visible."""

class WPopupWidget(WWidget):
    """
    A floating overlay that wraps an arbitrary widget. Anchors to
    another widget in the page and pops up over the surrounding
    content — useful for custom tooltips, detail callouts, or any
    content panel that should appear next to a trigger.

        info = wt.WText('More details here.')
        popup = wt.WPopupWidget(info)
        popup.set_anchor_widget(trigger)
        popup.transient = True

    Different from WPopupMenu (which is a menu of selectable items).
    """

    def __init__(self, contents: WWidget) -> None:
        """
        Construct with the inner widget shown in the popup. Ownership transfers; the contents widget's Python wrapper becomes non-owning.
        """

    def set_anchor_widget(self, anchor: WWidget) -> None:
        """Position the popup relative to `anchor` whenever it's shown."""

    @property
    def transient(self) -> bool:
        """When True, the popup auto-hides on outside click or focus loss."""

    @transient.setter
    def transient(self, arg: bool, /) -> None: ...

    def set_transient(self, transient: bool, auto_hide_delay_ms: int = 0) -> None:
        """
        Variant of the `transient` setter that also sets the grace period before auto-hide fires after the mouse leaves.
        """

    @property
    def hidden_signal(self) -> Signal:
        """
        Signal[] — fires when the popup transitions to hidden via a client-side event (not via Python `hidden=True`).
        """

    @property
    def shown_signal(self) -> Signal:
        """Signal[] — fires when the popup transitions to shown."""

class WLoadingIndicator(WWidget):
    """
    Abstract base for the spinner / banner shown during a server
    round-trip. Concrete subclasses (WDefaultLoadingIndicator,
    WOverlayLoadingIndicator) provide the visible UI; plug one into
    the application to control the look of the load state.
    """

    def set_message(self, text: str) -> None:
        """Replace the loading message shown to the user."""

class WDefaultLoadingIndicator(WLoadingIndicator):
    """
    The default unobtrusive loading indicator — a small fixed-
    position text label in the corner of the page.
    """

    def __init__(self) -> None:
        """Construct the default text-label indicator."""

class WOverlayLoadingIndicator(WLoadingIndicator):
    """
    A more aggressive loading indicator — dims the entire page with
    a translucent overlay and a centered banner during requests.
    Useful when the user shouldn't be interacting with stale content
    while the server is busy.
    """

    def __init__(self) -> None:
        """Construct the overlay-style indicator."""

class NotificationPermission(enum.Enum):
    """User-granted permission state for the browser Notification API."""

    Default = 0
    """Permission not yet requested or decided."""

    Granted = 1
    """User allowed notifications — `send` will work."""

    Denied = 2
    """
    User denied notifications — `send` will silently fail and
    `error` will fire.
    """

class WNotification(WObject):
    """
    Browser Notification API wrapper — produces native OS-level
    notifications (the toasts the operating system displays outside
    the page). Inherits WObject, not a widget, so it's not added to
    a container.

        note = wt.WNotification('Build done', 'All tests passed.')
        note.set_icon(wt.WLink('/static/check.png'))
        note.clicked.connect(focus_app)
        note.send()

    The browser must have granted notification permission first;
    without it `send` fails silently and `error` fires.
    """

    def __init__(self, title: str = '', body: str = '') -> None:
        """
        Construct a notification with optional title and body. Both
        can be set later via set_title / set_body.
        """

    def set_title(self, title: str) -> None:
        """Set the notification's heading line."""

    def set_body(self, body: str) -> None:
        """Set the notification's body text."""

    def set_icon(self, icon_link: WLink) -> None:
        """
        Set the small icon shown in the notification (WLink to an
        image URL or resource).
        """

    def set_badge(self, badge_link: WLink) -> None:
        """
        Set the badge image — used on some platforms when the full
        notification can't be shown (e.g. lock screens).
        """

    @property
    def silent(self) -> bool:
        """When True, the OS suppresses the usual notification sound."""

    @silent.setter
    def silent(self, arg: bool, /) -> None: ...

    @property
    def require_interaction(self) -> bool:
        """
        When True, the notification stays on screen until the user
        dismisses it instead of auto-fading.
        """

    @require_interaction.setter
    def require_interaction(self, arg: bool, /) -> None: ...

    def send(self) -> None:
        """
        Push the notification to the browser. Permission must be already granted.
        """

    def close(self) -> None:
        """Dismiss the notification programmatically."""

    @property
    def clicked(self) -> JSignal0:
        """JSignal0 — user clicked on the notification body."""

    @property
    def closed(self) -> JSignal0:
        """
        JSignal0 — fires when the notification is dismissed,
        either by the user or via `close`.
        """

    @property
    def shown(self) -> JSignal0:
        """
        JSignal0 — fires once the OS has accepted and
        displayed the notification.
        """

    @property
    def error(self) -> JSignal0:
        """
        JSignal0 — fires when the OS rejects the show request (e.g. permission denied at run time).
        """

class LayoutPosition(enum.Enum):
    """
    Slot identifier for WBorderLayout's five regions. North and
    South stretch across the top and bottom; West and East stretch
    down the sides; Center fills whatever is left in the middle.
    """

    North = 0

    East = 1

    South = 2

    West = 3

    Center = 4

class WBorderLayout(WLayout):
    """
    Classic BorderLayout — up to five children, one per region
    (North, South, East, West, Center). North and South stretch
    across the top and bottom; West and East stretch vertically on
    the sides; Center fills the remaining space. Regions left empty
    collapse to zero.

        layout = wt.WBorderLayout()
        container.set_layout(layout)
        layout.add_widget(wt.WText('Header'), wt.LayoutPosition.North)
        layout.add_widget(wt.WText('Body'),   wt.LayoutPosition.Center)
        layout.add_widget(wt.WText('Footer'), wt.LayoutPosition.South)
    """

    def __init__(self) -> None:
        """Construct an empty border layout."""

    def add_widget(self, widget: _T_Widget, position: LayoutPosition) -> _T_Widget:
        """
        Place `widget` into the named region. Takes ownership; the
        Python wrapper is re-armed as a non-owning alias and
        returned for fluent chaining. Only one widget per region —
        calling add_widget with a position that's already taken
        replaces the current occupant.
        """

class WFitLayout(WLayout):
    """
    Single-child layout — the one widget you add expands to fill
    the entire parent container. Equivalent to setting the child's
    CSS to `width: 100%; height: 100%` without writing the CSS.

        fit = wt.WFitLayout()
        container.set_layout(fit)
        fit.add_widget(wt.WTextArea())
    """

    def __init__(self) -> None:
        """Construct an empty fit layout."""

    def add_widget(self, widget: _T_Widget) -> _T_Widget:
        """
        Install `widget` as the single fitted child. Takes
        ownership; the Python wrapper is re-armed as a non-owning
        alias and returned for fluent chaining. Replacing the child
        requires calling the inherited removeWidget on the previous
        one first.
        """

class JDoubleSignal:
    """
    JavaScript signal carrying a single double payload. Used by
    WMediaPlayer.time_updated (current playback time in seconds) and
    WMediaPlayer.volume_changed (volume in 0.0-1.0).
    """

    def connect(self, callable: Callable) -> Connection:
        """
        Subscribe a callable taking a float. Returns a Connection —
        call `.disconnect()` to stop receiving.
        """

    def disconnect_all_slots(self) -> None:
        """Drop every Python subscriber attached via `connect`."""

class PlayerOption(enum.IntEnum):
    """
    Bitfield of HTML5 media element flags. OR values together when
    passing to WAbstractMedia.set_options.
    """

    Autoplay = 1
    """
    Begin playback as soon as the media loads (browsers often
    block this unless the audio is muted).
    """

    Loop = 2
    """Restart from the beginning when playback ends."""

    Controls = 4
    """Show the browser-default playback controls."""

class MediaPreloadMode(enum.Enum):
    """
    How aggressively the browser preloads media before playback —
    maps to the HTML5 `preload` attribute.
    """

    Auto = 1
    """Preload as much as the browser sees fit."""

    Metadata = 2
    """
    Fetch metadata (duration, dimensions) but not the media
    body itself.
    """

class WAbstractMedia(WInteractWidget):
    """
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
    """

    def add_source(self, source: WLink, mime_type: str = '', media: str = '') -> None:
        """
        Add a source URL (via WLink). `mime_type` is the content-type hint the browser uses to pick a source; `media` is a CSS media query (e.g. 'screen and (min-width: 600px)').
        """

    def clear_sources(self) -> None:
        """Remove every source previously added."""

    def set_alternative_content(self, widget: WWidget) -> None:
        """
        Widget shown to users whose browser can't play any of the configured sources. Ownership transfers; the wrapper is re-armed as a non-owning alias.
        """

    def set_options(self, options: int) -> None:
        """Bitwise-OR of PlayerOption values (Autoplay | Loop | Controls)."""

    def set_preload_mode(self, mode: MediaPreloadMode) -> None:
        """Set the browser's preload behavior (None_ / Metadata / Auto)."""

    def play(self) -> None:
        """Start playback. No-op if already playing."""

    def pause(self) -> None:
        """Pause playback. No-op if already paused."""

    @property
    def playing(self) -> bool:
        """True iff the media element is currently playing."""

    @property
    def playback_started(self) -> EventSignal:
        """EventSignal[] — fires when playback begins."""

    @property
    def playback_paused(self) -> EventSignal:
        """EventSignal[] — fires when playback is paused."""

    @property
    def ended(self) -> EventSignal:
        """
        EventSignal[] — fires when the media reaches the end
        (does not fire on Loop=True).
        """

    @property
    def time_updated(self) -> EventSignal:
        """
        EventSignal[] — fires periodically (~4×/sec by browser convention) during playback.
        """

    @property
    def volume_changed(self) -> EventSignal:
        """
        EventSignal[] — fires when the user changes the
        volume via the browser controls.
        """

class WAudio(WAbstractMedia):
    """
    HTML5 `<audio>` element. Wraps the browser's built-in audio
    playback — set sources via the inherited add_source, then either
    show the browser controls (PlayerOption.Controls) or drive play()
    / pause() from Python.

        audio = container.add_widget(wt.WAudio())
        audio.add_source(wt.WLink('/clip.mp3'), 'audio/mpeg')
        audio.set_options(int(wt.PlayerOption.Controls))
    """

    def __init__(self) -> None:
        """
        Construct an empty audio element. Add sources before adding
        to a container.
        """

class WVideo(WAbstractMedia):
    """
    HTML5 `<video>` element. Same API as WAudio but renders a video
    viewport — combine with `set_poster` for a still-image preview
    shown before playback begins.

        video = container.add_widget(wt.WVideo())
        video.add_source(wt.WLink('/clip.webm'), 'video/webm')
        video.add_source(wt.WLink('/clip.mp4'), 'video/mp4')
        video.set_poster('/thumb.jpg')
        video.set_options(int(wt.PlayerOption.Controls))
    """

    def __init__(self) -> None:
        """
        Construct an empty video element. Add sources before adding
        to a container.
        """

    def set_poster(self, url: str) -> None:
        """
        URL of a thumbnail shown before playback starts (HTML `poster` attribute).
        """

class MediaEncoding(enum.Enum):
    """
    Encoding label for WMediaPlayer.add_source. Add the same logical
    content under several encodings so the player can pick one the
    current browser supports.
    """

    PosterImage = 0
    """Not a media source — a still image shown before playback."""

    MP3 = 1
    """MPEG-1 Audio Layer 3."""

    M4A = 2
    """MPEG-4 Audio (AAC in MP4 container)."""

    OGA = 3
    """Ogg Vorbis / Opus audio."""

    WAV = 4
    """Waveform audio."""

    WEBMA = 5
    """WebM audio."""

    FLA = 6
    """Flash audio (legacy fallback)."""

    M4V = 7
    """MPEG-4 Video."""

    OGV = 8
    """Ogg Theora video."""

    WEBMV = 9
    """WebM video."""

    FLV = 10
    """Flash video (legacy fallback)."""

class MediaType(enum.Enum):
    """Which kind of player to construct."""

    Audio = 0
    """Audio-only player; renders a horizontal control strip."""

    Video = 1
    """Video player; renders a video viewport with controls below."""

class MediaPlayerButtonId(enum.Enum):
    """
    Identifier for one of the player's built-in control buttons —
    passed to WMediaPlayer.set_button to substitute a custom widget.
    """

    VideoPlay = 0
    """Large central play-overlay button for video."""

    Play = 1

    Pause = 2

    Stop = 3

    VolumeMute = 4

    VolumeUnmute = 5

    VolumeMax = 6

    FullScreen = 7

    RestoreScreen = 8

    RepeatOn = 9

    RepeatOff = 10

class MediaPlayerProgressBarId(enum.Enum):
    """
    Identifier for one of the player's progress bars — passed to
    WMediaPlayer.set_progress_bar to substitute a custom WProgressBar.
    """

    Time = 0
    """The seek/playback-position bar."""

    Volume = 1
    """The volume-level bar."""

class MediaPlayerTextId(enum.Enum):
    """
    Identifier for one of the player's text fields — passed to
    WMediaPlayer.set_text to substitute a custom WText.
    """

    CurrentTime = 0
    """Display of the current playback position."""

    Duration = 1
    """Display of the media's total duration."""

    Title = 2
    """Display of the title set via set_title."""

class WMediaPlayer(WWidget):
    """
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
    """

    def __init__(self, media_type: MediaType) -> None:
        """Construct an audio or video player."""

    def add_source(self, encoding: MediaEncoding, link: WLink) -> None:
        """
        Register a source URL for a given encoding. Add the same content under multiple encodings for cross-browser support.
        """

    def get_source(self, encoding: MediaEncoding) -> WLink:
        """
        Return the WLink registered for `encoding`, or an empty
        WLink if none was added.
        """

    def clear_sources(self) -> None:
        """Remove every source previously added."""

    def set_title(self, title: str) -> None:
        """
        Set the title shown in the player's Title text field (when
        configured to show one).
        """

    def set_video_size(self, width: int, height: int) -> None:
        """Set the video viewport dimensions in pixels."""

    @property
    def video_width(self) -> int:
        """Width of the video viewport in pixels."""

    @property
    def video_height(self) -> int:
        """Height of the video viewport in pixels."""

    def play(self) -> None:
        """Start playback."""

    def pause(self) -> None:
        """Pause playback."""

    def stop(self) -> None:
        """Stop playback and return to the start."""

    def seek(self, time: float) -> None:
        """Jump to `time` seconds into the media."""

    def set_playback_rate(self, rate: float) -> None:
        """1.0 = normal; 2.0 = 2× speed; 0.5 = half-speed."""

    def set_volume(self, volume: float) -> None:
        """0.0 (silent) to 1.0 (max)."""

    def mute(self, mute: bool) -> None:
        """
        Mute (True) or unmute (False) the audio output without
        changing the configured volume.
        """

    def set_button(self, id: MediaPlayerButtonId, button: WInteractWidget) -> None:
        """
        Override the widget used for a control. The button is associated (not owned); place it in the page yourself.
        """

    def set_progress_bar(self, id: MediaPlayerProgressBarId, progress_bar: WProgressBar) -> None:
        """
        Override the WProgressBar used for the Time or Volume bar.
        The bar is associated (not owned); place it in the page yourself.
        """

    def set_text(self, id: MediaPlayerTextId, text: WText) -> None:
        """
        Override the WText used for one of the player's text displays
        (CurrentTime, Duration, Title). The widget is associated, not
        owned.
        """

    @property
    def playback_started(self) -> JSignal0:
        """JSignal0 — fires when playback starts."""

    @property
    def playback_paused(self) -> JSignal0:
        """JSignal0 — fires when playback pauses."""

    @property
    def ended(self) -> JSignal0:
        """JSignal0 — fires when the media reaches its end."""

    @property
    def time_updated(self) -> JDoubleSignal:
        """
        JDoubleSignal — fires periodically with the current playback time in seconds.
        """

    @property
    def volume_changed(self) -> JDoubleSignal:
        """
        JDoubleSignal — fires when volume changes; payload is the new volume (0.0–1.0).
        """

class WSound(WObject):
    """
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
    """

    def __init__(self) -> None:
        """Construct an empty sound. Add sources before calling play."""

    def add_source(self, encoding: MediaEncoding, link: WLink) -> None:
        """
        Register a source URL for a given encoding. Add the same
        clip in multiple encodings for cross-browser support.
        """

    def get_source(self, encoding: MediaEncoding) -> WLink:
        """
        Return the WLink registered for `encoding`, or an empty
        WLink if none was added.
        """

    @property
    def loops(self) -> int:
        """Number of times to repeat the clip. 0 = infinite."""

    @loops.setter
    def loops(self, arg: int, /) -> None: ...

    def play(self) -> None:
        """Play the sound. Starts from the beginning each time."""

    def stop(self) -> None:
        """Stop any currently-playing playback."""

class WPointF:
    """
    A point in 2-D space with floating-point coordinates. Used by
    WPainter for paths and polygons; mutable so you can mutate x/y
    in place.
    """

    @overload
    def __init__(self) -> None:
        """Construct the origin (0, 0)."""

    @overload
    def __init__(self, x: float, y: float) -> None:
        """Construct the point (x, y)."""

    @property
    def x(self) -> float:
        """Horizontal coordinate."""

    @x.setter
    def x(self, arg: float, /) -> None: ...

    @property
    def y(self) -> float:
        """Vertical coordinate."""

    @y.setter
    def y(self, arg: float, /) -> None: ...

    def __repr__(self) -> str: ...

class WRectF:
    """
    Axis-aligned rectangle with floating-point coordinates. Used as
    a parameter to WPainter draw / clip methods and as the result
    type of bounding-box queries.
    """

    @overload
    def __init__(self) -> None:
        """Construct a degenerate rectangle at the origin with zero size."""

    @overload
    def __init__(self, x: float, y: float, width: float, height: float) -> None:
        """
        Construct a rectangle whose top-left corner is at (x, y) and with the given size.
        """

    @property
    def x(self) -> float:
        """Top-left X coordinate."""

    @x.setter
    def x(self, arg: float, /) -> None: ...

    @property
    def y(self) -> float:
        """Top-left Y coordinate."""

    @y.setter
    def y(self, arg: float, /) -> None: ...

    @property
    def width(self) -> float:
        """Rectangle width."""

    @width.setter
    def width(self, arg: float, /) -> None: ...

    @property
    def height(self) -> float:
        """Rectangle height."""

    @height.setter
    def height(self, arg: float, /) -> None: ...

    @property
    def is_null(self) -> bool:
        """
        True when the rectangle is the default-constructed null value (distinct from a present-but-empty rect).
        """

    @property
    def is_empty(self) -> bool:
        """True when width or height is zero (or negative)."""

    @property
    def left(self) -> float:
        """Left edge (same as `x`)."""

    @property
    def top(self) -> float:
        """Top edge (same as `y`)."""

    def __repr__(self) -> str: ...

class WLineF:
    """
    A line segment between two points. Used in bulk-line draws (`WPainter.draw_lines`).
    """

    @overload
    def __init__(self) -> None:
        """Construct a zero-length line at the origin."""

    @overload
    def __init__(self, x1: float, y1: float, x2: float, y2: float) -> None:
        """Construct a line from (x1, y1) to (x2, y2)."""

    @property
    def x1(self) -> float:
        """X coordinate of the start point."""

    @property
    def y1(self) -> float:
        """Y coordinate of the start point."""

    @property
    def x2(self) -> float:
        """X coordinate of the end point."""

    @property
    def y2(self) -> float:
        """Y coordinate of the end point."""

    @property
    def p1(self) -> WPointF:
        """Start point as a WPointF."""

    @property
    def p2(self) -> WPointF:
        """End point as a WPointF."""

class WTransform:
    """
    Affine 2-D transform as a 2x3 matrix (m11, m12, m21, m22, dx,
    dy). Applied to coordinates by WPainter operations after
    `set_world_transform`. Use `WPainter.translate / rotate / scale`
    for the common cases — construct a WTransform directly only
    when you need a combined or pre-computed matrix.
    """

    def __init__(self) -> None:
        """Identity transform."""

    @property
    def is_identity(self) -> bool:
        """True when this transform leaves coordinates unchanged."""

    @property
    def m11(self) -> float:
        """Row 1, column 1 of the matrix (X scale)."""

    @property
    def m12(self) -> float:
        """Row 1, column 2 of the matrix (Y shear into X)."""

    @property
    def m21(self) -> float:
        """Row 2, column 1 of the matrix (X shear into Y)."""

    @property
    def m22(self) -> float:
        """Row 2, column 2 of the matrix (Y scale)."""

    @property
    def dx(self) -> float:
        """X translation component."""

    @property
    def dy(self) -> float:
        """Y translation component."""

    def reset(self) -> None:
        """Restore the identity transform."""

    @property
    def determinant(self) -> float:
        """Matrix determinant — non-zero iff the transform is invertible."""

    def adjoint(self) -> WTransform:
        """
        Return the adjoint (transposed cofactor) matrix. Useful when computing inverses manually.
        """

    def map_point(self, x: float, y: float) -> tuple:
        """Apply the transform to (x, y) and return (tx, ty)."""

class FontFamily(enum.Enum):
    """
    Generic font-family categories. Maps to the CSS generic family of the same name. Combine with `WFont.set_family`'s specific argument to nominate concrete font names.
    """

    Default = 0

    Serif = 1

    SansSerif = 2

    Cursive = 3

    Fantasy = 4

    Monospace = 5

class FontStyle(enum.Enum):
    """CSS `font-style` value — upright, italic, or oblique."""

    NormalStyle = 0

    Italic = 1

    Oblique = 2

class FontVariant(enum.Enum):
    """
    CSS `font-variant` value. SmallCaps renders lowercase as smaller uppercase glyphs.
    """

    Normal = 0

    SmallCaps = 1

class FontWeight(enum.Enum):
    """
    CSS `font-weight` value. Pick a preset; Value means an explicit numeric weight is supplied to `WFont.set_weight`.
    """

    Normal = 0

    Bold = 1

    Bolder = 2

    Lighter = 3

    Value = 4

class FontSize(enum.Enum):
    """
    CSS `font-size` keyword sizes. Use FixedSize together with `WFont.set_size(WLength)` for an explicit numeric size.
    """

    XXSmall = 0

    XSmall = 1

    Small = 2

    Medium = 3

    Large = 4

    XLarge = 5

    XXLarge = 6

    Smaller = 7

    Larger = 8

    FixedSize = 9

class WFont:
    """
    Font specification used by WPainter.draw_text and by widget decoration APIs. Holds family, style, variant, weight, and size — what CSS would call the `font` shorthand.
    """

    @overload
    def __init__(self) -> None:
        """Construct a default-family font at the browser's default size."""

    @overload
    def __init__(self, family: FontFamily) -> None:
        """Construct with the given generic family."""

    def set_family(self, family: FontFamily, specific_families: str = '') -> None:
        """
        Generic family + optional comma-separated specific font names (e.g. setFamily(Monospace, "'Courier New'")).
        """

    def set_style(self, style: FontStyle) -> None:
        """Set the FontStyle (normal / italic / oblique)."""

    def set_variant(self, variant: FontVariant) -> None:
        """Set the FontVariant (normal or small caps)."""

    def set_weight(self, weight: FontWeight, value: int = 400) -> None:
        """
        When weight=Value, the second argument is the CSS numeric weight (100, 200, …, 900).
        """

    def set_size(self, size: WLength) -> None:
        """
        Size as a WLength — accepts a number (treated as pixels), a WLength('1.2em'), or a parsed CSS string.
        """

    def size_length(self, medium_size: float = 16.0) -> WLength:
        """
        Resolve the current size to a concrete WLength. Keyword sizes (Small, Large, …) are computed relative to `medium_size` pixels.
        """

class GradientStyle(enum.Enum):
    """
    Geometric form of a WGradient — straight axis (Linear) or concentric (Radial).
    """

    Linear = 0

    Radial = 1

class WGradient:
    """
    Multi-stop colour gradient used as a pen stroke or brush fill.
    Configure geometry first (`set_linear_gradient` or
    `set_radial_gradient`), then add colour stops in order from 0.0
    (start) to 1.0 (end).

        g = wt.WGradient()
        g.set_linear_gradient(0, 0, 100, 0)
        g.add_color_stop(0.0, wt.WColor('red'))
        g.add_color_stop(1.0, wt.WColor('yellow'))
        painter.set_brush(wt.WBrush(g))
    """

    def __init__(self) -> None:
        """Construct an empty (no-geometry, no-stops) gradient."""

    @property
    def style(self) -> GradientStyle:
        """Linear or Radial — set by the last set_* call."""

    @property
    def is_empty(self) -> bool:
        """True when no colour stops have been added yet."""

    def set_linear_gradient(self, x0: float, y0: float, x1: float, y1: float) -> None:
        """Configure a linear gradient from (x0,y0) to (x1,y1)."""

    def set_radial_gradient(self, cx: float, cy: float, r: float, fx: float, fy: float) -> None:
        """
        Configure a radial gradient: bounding circle centred at (cx,cy) with radius r, focal point at (fx,fy).
        """

    def add_color_stop(self, position: float, color: WColor) -> None:
        """Add a color stop at `position` (0.0 = start, 1.0 = end)."""

    def clear_color_stops(self) -> None:
        """Remove every previously-added colour stop."""

class WShadow:
    """
    Drop-shadow descriptor — offset, blur radius, and colour. Pass to `WPainter.set_shadow` to apply to subsequent draws; pass the default-constructed WShadow() to clear.
    """

    @overload
    def __init__(self) -> None:
        """Construct the no-shadow value."""

    @overload
    def __init__(self, dx: float, dy: float, color: WColor, blur: float) -> None:
        """
        Construct a shadow offset by (dx, dy) in the painter's current coordinates, tinted `color`, with `blur` blur radius.
        """

    def set_offsets(self, dx: float, dy: float) -> None:
        """Set the shadow's offset."""

    def set_color(self, color: WColor) -> None:
        """Set the shadow's tint colour."""

    def set_blur(self, blur: float) -> None:
        """Set the Gaussian blur radius."""

    @property
    def offset_x(self) -> float:
        """Horizontal shadow offset."""

    @property
    def offset_y(self) -> float:
        """Vertical shadow offset."""

    @property
    def color(self) -> WColor:
        """Shadow tint colour."""

    @property
    def blur(self) -> float:
        """Blur radius."""

    @property
    def none(self) -> bool:
        """True for the default (no-shadow) value."""

class BorderStyle(enum.Enum):
    """
    CSS `border-style` value. Mirrors the standard set of CSS borders — Solid for the common case, Dotted/Dashed for discontinuous strokes, Groove/Ridge/Inset/Outset for 3-D effects.
    """

    Hidden = 1

    Dotted = 2

    Dashed = 3

    Solid = 4

    Double = 5

    Groove = 6

    Ridge = 7

    Inset = 8

    Outset = 9

class BorderWidth(enum.Enum):
    """
    CSS `border-width` keyword. Use Explicit together with the WLength-taking WBorder constructor for a numeric width.
    """

    Thin = 0

    Medium = 1

    Thick = 2

    Explicit = 3

class WBorder:
    """
    Value type describing a CSS border — style, width, and colour. Passed to widget decoration APIs (WCssDecorationStyle etc.).
    """

    @overload
    def __init__(self) -> None:
        """Construct the default (no border) value."""

    @overload
    def __init__(self, style: BorderStyle, width: BorderWidth, color: WColor) -> None:
        """
        Construct from a style, a keyword width (Thin/Medium/Thick), and a colour.
        """

    @overload
    def __init__(self, style: BorderStyle, width: WLength, color: WColor) -> None:
        """
        Explicit-width variant — `width` is a WLength rather than the Thin/Medium/Thick preset.
        """

    def set_style(self, style: BorderStyle) -> None:
        """Change the border style."""

    def set_color(self, color: WColor) -> None:
        """Change the border colour."""

    @property
    def style(self) -> BorderStyle:
        """Current BorderStyle."""

    @property
    def color(self) -> WColor:
        """Current border colour."""

    @property
    def explicit_width(self) -> WLength:
        """
        Explicit width as a WLength (meaningful only when the border was constructed with the WLength-taking ctor).
        """

class PenStyle(enum.Enum):
    """
    Stroke dash pattern. NoPen suppresses the stroke entirely (use for fill-only draws).
    """

    NoPen = 0

    SolidLine = 1

    DashLine = 2

    DotLine = 3

    DashDotLine = 4

    DashDotDotLine = 5

class PenCapStyle(enum.Enum):
    """
    Shape applied at the ends of stroked open paths — flush (FlatCap), squared off past the endpoint (SquareCap), or a semicircle (RoundCap).
    """

    FlatCap = 0

    SquareCap = 1

    RoundCap = 2

class PenJoinStyle(enum.Enum):
    """
    Shape applied where two stroked segments meet — sharp point (MiterJoin), flattened (BevelJoin), or rounded (RoundJoin).
    """

    MiterJoin = 0

    BevelJoin = 1

    RoundJoin = 2

class WPen:
    """
    Stroke specification — colour or gradient, dash style, line cap, join style, and width. Assigned to a WPainter via `set_pen`; affects every subsequent stroke or outline.
    """

    @overload
    def __init__(self) -> None:
        """Construct a default black 1-px solid pen."""

    @overload
    def __init__(self, style: PenStyle) -> None:
        """
        Construct a pen with the given dash style (and default colour and width).
        """

    @overload
    def __init__(self, color: WColor) -> None:
        """Construct a solid pen of the given colour."""

    def set_style(self, style: PenStyle) -> None:
        """Set the dash pattern."""

    def set_cap_style(self, style: PenCapStyle) -> None:
        """Set the line-end cap style."""

    def set_join_style(self, style: PenJoinStyle) -> None:
        """Set the join style for connected segments."""

    def set_width(self, width: WLength) -> None:
        """
        Set stroke width (a WLength — number for pixels, or a WLength with explicit units).
        """

    def set_color(self, color: WColor) -> None:
        """Set the stroke colour."""

    def set_gradient(self, gradient: WGradient) -> None:
        """Use a gradient for the stroke instead of a solid color."""

    @property
    def color(self) -> WColor:
        """Current stroke colour."""

    @property
    def style(self) -> PenStyle:
        """Current dash pattern."""

    @property
    def cap_style(self) -> PenCapStyle:
        """Current line-end cap style."""

    @property
    def join_style(self) -> PenJoinStyle:
        """Current segment join style."""

    @property
    def width(self) -> WLength:
        """Current stroke width as a WLength."""

class BrushStyle(enum.Enum):
    """
    Fill pattern for a WBrush. NoBrush leaves the interior unfilled; SolidPattern fills with a single colour; Gradient uses the brush's attached WGradient.
    """

    NoBrush = 0

    SolidPattern = 1

    Gradient = 2

class WBrush:
    """
    Fill specification — a solid colour or a gradient. Assigned to a WPainter via `set_brush`; affects every subsequent filled shape (rectangle, ellipse, path, etc.).
    """

    @overload
    def __init__(self) -> None:
        """Construct the no-fill (NoBrush) value."""

    @overload
    def __init__(self, style: BrushStyle) -> None:
        """Construct with the given style and default colour."""

    @overload
    def __init__(self, color: WColor) -> None:
        """Construct a solid-colour brush."""

    @overload
    def __init__(self, gradient: WGradient) -> None:
        """Construct a gradient-filled brush. style is set to Gradient."""

    def set_style(self, style: BrushStyle) -> None:
        """Switch fill style."""

    def set_color(self, color: WColor) -> None:
        """Set the solid fill colour (also switches to SolidPattern)."""

    def set_gradient(self, gradient: WGradient) -> None:
        """Use a gradient for the fill. Sets style to Gradient."""

    @property
    def color(self) -> WColor:
        """Current fill colour."""

    @property
    def style(self) -> BrushStyle:
        """Current fill style."""

class WPainterPath:
    """
    A geometric path built from straight lines, Bézier curves, and
    arcs — the parametric input to `WPainter.draw_path` and
    `WPainter.set_clip_path`. Build incrementally: move the pen,
    draw segments, optionally close back to the start.

        path = wt.WPainterPath()
        path.move_to(10, 10)
        path.line_to(50, 10)
        path.cubic_to(80, 10, 80, 80, 50, 80)
        path.close_sub_path()
        painter.draw_path(path)
    """

    @overload
    def __init__(self) -> None:
        """Construct an empty path."""

    @overload
    def __init__(self, start: WPointF) -> None:
        """Begin the path at the given start point."""

    @property
    def is_empty(self) -> bool:
        """True when no segments have been added yet."""

    @property
    def current_position(self) -> WPointF:
        """
        End point of the most recently added segment — the implicit starting point of the next `line_to` / `cubic_to` / `arc_to`.
        """

    def close_sub_path(self) -> None:
        """Close the current sub-path with a line back to its start."""

    def move_to(self, x: float, y: float) -> None:
        """Begin a new sub-path at (x, y) without drawing a connecting segment."""

    def line_to(self, x: float, y: float) -> None:
        """Append a straight line from the current position to (x, y)."""

    def cubic_to(self, c1x: float, c1y: float, c2x: float, c2y: float, end_x: float, end_y: float) -> None:
        """
        Cubic Bézier from current position to (end_x, end_y) via control points (c1x, c1y) and (c2x, c2y).
        """

    def arc_to(self, cx: float, cy: float, radius: float, start_angle: float, sweep_length: float) -> None:
        """
        Arc of `radius` centred at (cx, cy); angles in degrees, 0° = 3 o'clock, sweeping counter-clockwise.
        """

    def add_rect(self, x: float, y: float, width: float, height: float) -> None:
        """Add an axis-aligned rectangle as a closed sub-path."""

    def add_ellipse(self, x: float, y: float, width: float, height: float) -> None:
        """Add an ellipse inscribed in the bounding rect as a closed sub-path."""

class PainterImage:
    """
    Value type describing an image that a WPainter can draw. Holds
    the URL the browser will fetch and the intrinsic pixel size
    needed for layout. Pass an instance to `WPainter.draw_image`;
    also re-exported on the WPainter class as `WPainter.Image` for
    the natural nested-class form.
    """

    @overload
    def __init__(self, url: str, width: int, height: int) -> None:
        """Reference an external image at `url` with explicit pixel dimensions."""

    @overload
    def __init__(self, url: str, file: str) -> None:
        """
        Reference an image whose pixel dimensions Wt should read from local file `file` (the URL is what the browser uses; the file is where Wt looks for size metadata).
        """

    @property
    def uri(self) -> str:
        """The URL the browser will load to render this image."""

    @property
    def width(self) -> int:
        """Intrinsic image width in pixels."""

    @property
    def height(self) -> int:
        """Intrinsic image height in pixels."""

class WPainter:
    """
    2-D drawing context. Receives geometric draw commands and turns
    them into output on a paint device — an HTML canvas, an SVG
    document, a PDF page, etc. Modelled on the same verb surface as
    Cairo or HTML5 Canvas: configure pen / brush / font, then call
    draw_* methods.

        pdf = wt.WPdfImage(wt.WLength(595), wt.WLength(842))
        painter = wt.WPainter(pdf)
        painter.set_pen(wt.WPen(wt.WColor('black')))
        painter.draw_line(0, 0, 100, 100)
        painter.draw_text(10, 10, 200, 30, wt.AlignmentFlag.Left,
                          'Report')
        app.add_resource(pdf, '/report.pdf')

    Inside a WPaintedWidget's paint callback the painter is handed
    to you already bound to the right device — don't construct one.
    The painter does NOT own its device; keep the device alive for
    the painter's lifetime. Drop the painter (or let it go out of
    scope) to flush any pending output to the device.
    """

    @overload
    def __init__(self, device: WPaintDevice) -> None:
        """
        Construct a painter bound to a paint device. The device is not owned; the painter borrows it for its lifetime.
        """

    @overload
    def __init__(self, device: WResource) -> None:
        """
        Construct from a WResource that also implements WPaintDevice (WPdfImage / WSvgImage). Equivalent to passing the WPaintDevice view of the same object.
        """

    def save(self) -> None:
        """
        Push the current state (pen, brush, font, transform, clipping) onto an internal stack. Pair with restore().
        """

    def restore(self) -> None:
        """
        Pop the most recently saved state, undoing any pen / brush / font / transform / clipping changes made since the matching save().
        """

    def set_pen(self, pen: WPen) -> None:
        """Set the stroke style for subsequent line / outline draws."""

    def set_brush(self, brush: WBrush) -> None:
        """Set the fill style for subsequent filled-shape draws."""

    def set_font(self, font: WFont) -> None:
        """Set the font used by draw_text."""

    def set_shadow(self, shadow: WShadow) -> None:
        """
        Apply a drop-shadow effect to subsequent draw operations. Pass `wt.WShadow()` to clear.
        """

    @property
    def pen(self) -> WPen:
        """The current pen — what strokes use."""

    @property
    def brush(self) -> WBrush:
        """The current brush — what fills use."""

    def set_world_transform(self, transform: WTransform, combine: bool = False) -> None:
        """
        Replace the painter's current transform with `transform`. Pass combine=True to multiply onto the existing transform instead of replacing it.
        """

    def translate(self, dx: float, dy: float) -> None:
        """Shift the origin of subsequent draws by (dx, dy)."""

    def rotate(self, angle: float) -> None:
        """
        Rotate by `angle` degrees about the origin of the local coordinate system.
        """

    def scale(self, sx: float, sy: float) -> None:
        """
        Scale subsequent draws by sx in X and sy in Y. Pass sx=sy=-1 to flip about the origin.
        """

    def set_clipping(self, enabled: bool) -> None:
        """
        Enable or disable the active clip path. Use set_clip_path first to define the clip region.
        """

    def set_clip_path(self, path: WPainterPath) -> None:
        """
        Restrict subsequent draws to the area inside `path` (a WPainterPath). Does not enable clipping by itself — call set_clipping(True) too.
        """

    def draw_line(self, x1: float, y1: float, x2: float, y2: float) -> None:
        """
        Stroke a straight line from (x1, y1) to (x2, y2) using the current pen.
        """

    def draw_rect(self, x: float, y: float, width: float, height: float) -> None:
        """
        Stroke and fill an axis-aligned rectangle with the current pen and brush.
        """

    def draw_ellipse(self, x: float, y: float, width: float, height: float) -> None:
        """Ellipse inscribed in the given bounding rect."""

    def draw_arc(self, x: float, y: float, width: float, height: float, start_angle: int, span_angle: int) -> None:
        """
        Arc inscribed in the bounding rect, swept from start to start+span (in 1/16-degree units, Wt convention).
        """

    def draw_pie(self, x: float, y: float, width: float, height: float, start_angle: int, span_angle: int) -> None:
        """
        Pie slice — arc closed back to the centre. Angles in 1/16-degree units like draw_arc.
        """

    def draw_chord(self, x: float, y: float, width: float, height: float, start_angle: int, span_angle: int) -> None:
        """
        Chord — arc closed by a straight line between its endpoints (not the centre). Angles in 1/16-degree units.
        """

    def draw_point(self, x: float, y: float) -> None:
        """Draw a single point at (x, y) with the current pen."""

    def draw_path(self, path: WPainterPath) -> None:
        """Stroke and fill a WPainterPath using the current pen and brush."""

    def draw_lines(self, lines: Sequence[WLineF]) -> None:
        """
        Stroke each WLineF in `lines` with the current pen — one round-trip into the device, cheaper than many draw_line calls.
        """

    def draw_text(self, x: float, y: float, width: float, height: float, alignment: int, text: str) -> None:
        """
        Draw text into the rect. `alignment` is an OR of AlignmentFlag values (e.g. Center | Middle).
        """

    @overload
    def draw_image(self, point: WPointF, image: PainterImage) -> None:
        """Draw the image at its intrinsic size with top-left at point."""

    @overload
    def draw_image(self, point: WPointF, image: PainterImage, source_rect: WRectF) -> None:
        """
        Draw a sub-region of the image at its intrinsic size. source_rect is in the image's pixel coordinates.
        """

    @overload
    def draw_image(self, dest_rect: WRectF, image: PainterImage) -> None:
        """Stretch / shrink the image to fill dest_rect."""

    @overload
    def draw_image(self, dest_rect: WRectF, image: PainterImage, source_rect: WRectF) -> None:
        """Stretch a sub-region of the image into dest_rect."""

    @property
    def is_active(self) -> bool:
        """
        True if the painter is currently bound to a device and can accept draw calls.
        """

    Image: TypeAlias = PainterImage

class WPaintedWidget(WInteractWidget):
    """
    A widget whose contents are produced by Python code running
    against a WPainter. Pass a callable at construction; it will be
    invoked each time the widget needs to repaint, with a freshly-
    bound WPainter as its only argument.

        def paint(p):
            p.set_pen(wt.WPen(wt.WColor('navy')))
            p.draw_line(0, 0, 200, 100)
            p.draw_ellipse(20, 20, 60, 60)
        container.add_widget(wt.WPaintedWidget(paint))

    Call `update()` to request a repaint after model changes. The
    WPainter handed to the callback is a non-owning view of a
    stack-allocated object — don't stash it beyond the callback's
    return. The paint callback may run on a worker thread; the
    binding acquires the GIL before calling into Python.
    """

    @overload
    def __init__(self) -> None:
        """
        Construct an empty painted widget with no paint callback. Set one later via `set_paint_callback` before calling `update()`.
        """

    @overload
    def __init__(self, paint: Callable) -> None:
        """
        Construct with the paint callback. The callable takes a single WPainter argument — use its draw_* methods to render.
        """

    def set_paint_callback(self, paint: Callable) -> None:
        """
        Replace the paint callback. The new callback will be used from the next paintEvent onward; call update() to force a redraw immediately.
        """

    def update(self) -> None:
        """
        Schedule a repaint. Wt batches paint events — the actual paintEvent fires after the current event loop tick.
        """

    def set_preferred_method(self, method: RenderMethod) -> None:
        """
        Render backend: InlineSvgVml, HtmlCanvas, or PngImage. HtmlCanvas is the default on modern browsers.
        """

    @property
    def preferred_method(self) -> RenderMethod:
        """The currently selected render backend (RenderMethod enum)."""

    def add_area(self, area: _T_Area) -> _T_Area:
        """
        Attach an image-map area (WRectArea / WCircleArea / WPolygonArea) that becomes a clickable region on top of the painted output.
        """

    def insert_area(self, index: int, area: _T_Area) -> _T_Area:
        """
        Insert an image-map area at position `index`. Earlier areas in the list receive clicks first when regions overlap.
        """

class RenderMethod(enum.Enum):
    """
    Backend a WPaintedWidget uses to render. HtmlCanvas is the default; InlineSvgVml emits inline SVG (legacy IE: VML); PngImage rasterises server-side and serves a PNG.
    """

    InlineSvgVml = 0

    HtmlCanvas = 1

    PngImage = 2

class WAbstractArea(WObject):
    """
    Base class for clickable regions in an image map. Concrete
    subclasses define the region's shape: WRectArea, WCircleArea,
    WPolygonArea. Attach one to a WPaintedWidget or WImage via
    `add_area` to make part of the rendered output respond to clicks.
    """

    def set_link(self, link: WLink) -> None:
        """
        Navigate to `link` when the area is clicked (WLink — URL, internal path, or WResource).
        """

    def set_alternate_text(self, text: str) -> None:
        """
        Text used by screen readers and shown when the underlying image fails to load.
        """

    def set_tool_tip(self, text: str) -> None:
        """Hover-tooltip text shown while the cursor is over this area."""

    def set_style_class(self, style_class: str) -> None:
        """CSS class for the underlying `<area>` element."""

    @property
    def hole(self) -> bool:
        """
        When True, this area is treated as a hole (transparent to clicks) cut out of the surrounding map.
        """

    @hole.setter
    def hole(self, arg: bool, /) -> None: ...

    @property
    def transformable(self) -> bool:
        """
        When True, the area's coordinates are interpreted in the painter's local coordinate system and follow any transforms applied to the widget. When False, coordinates stay fixed in widget pixels.
        """

    @transformable.setter
    def transformable(self, arg: bool, /) -> None: ...

class WCircleArea(WAbstractArea):
    """
    Circular clickable region for an image map. Coordinates are in the widget's pixel space (or local coordinates if `transformable` is True).
    """

    @overload
    def __init__(self) -> None:
        """Construct an empty circle area — set centre and radius afterwards."""

    @overload
    def __init__(self, x: int, y: int, radius: int) -> None:
        """Construct a circle centred at (x, y) with the given radius."""

    def set_center(self, x: int, y: int) -> None:
        """Move the circle's centre to (x, y)."""

    @property
    def center_x(self) -> int:
        """X coordinate of the circle's centre."""

    @property
    def center_y(self) -> int:
        """Y coordinate of the circle's centre."""

    @property
    def radius(self) -> int:
        """Circle radius in pixels (or local coordinate units)."""

    @radius.setter
    def radius(self, arg: int, /) -> None: ...

class WRectArea(WAbstractArea):
    """Rectangular clickable region for an image map."""

    @overload
    def __init__(self) -> None:
        """
        Construct a degenerate (zero-size) rectangle. Set bounds afterwards by reconstructing.
        """

    @overload
    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        """Construct an axis-aligned rectangle with top-left at (x, y)."""

    @overload
    def __init__(self, rect: WRectF) -> None:
        """Construct from an existing WRectF."""

class WPolygonArea(WAbstractArea):
    """
    Polygon-shaped clickable region. Build by passing a list of vertices, or extend a polygon incrementally via `add_point`.
    """

    @overload
    def __init__(self) -> None:
        """Construct an empty polygon area — add vertices afterwards."""

    @overload
    def __init__(self, points: Sequence[WPointF]) -> None:
        """Construct from a sequence of WPointF vertices."""

    def add_point(self, x: float, y: float) -> None:
        """Append a vertex at (x, y) to the polygon."""

    def set_points(self, points: Sequence[WPointF]) -> None:
        """Replace the polygon's vertices with `points`."""

class PaintDeviceFeatureFlag(enum.IntEnum):
    """
    Capability bits a paint device can advertise. Combined with OR into a bitmask. HasFontMetrics means the device can measure text without rendering it; CanWordWrap means it knows how to break long strings on word boundaries.
    """

    HasFontMetrics = 2

    CanWordWrap = 1

class WPaintDevice:
    """
    Abstract base for everything a WPainter can draw into — an
    HTML canvas, an SVG document, a PDF page, an off-screen
    measurement device. Cannot be constructed directly; pick a
    concrete subclass.

        pdf = wt.WPdfImage(wt.WLength(595), wt.WLength(842))
        painter = wt.WPainter(pdf)
        painter.draw_text(...)
        app.add_resource(pdf, '/page.pdf')

    WResource-based devices (WSvgImage, WPdfImage) are typically
    served to the browser by mounting on a URL; off-screen devices
    (WMeasurePaintDevice, WCanvasPaintDevice) are used for sizing
    or capture.
    """

    @property
    def width(self) -> WLength:
        """Device width as a WLength."""

    @property
    def height(self) -> WLength:
        """Device height as a WLength."""

class WVectorImage(WPaintDevice):
    """
    Base class for vector-graphics paint devices (WSvgImage today; a future VML implementation). Exposes no methods of its own — exists so callers can `isinstance(dev, wt.WVectorImage)` to test for the vector family.
    """

class WSvgImage(WResource):
    """
    SVG paint device backed by a WResource. Paint into it with a
    WPainter, then mount the device on a URL via
    `WApplication.add_resource` to serve the resulting SVG document
    to clients (typically as the source of a WImage or a
    `<link rel=icon>`).

        svg = wt.WSvgImage(wt.WLength(200), wt.WLength(100))
        p = wt.WPainter(svg)
        p.draw_ellipse(20, 20, 60, 60)
        del p  # flush
        app.add_resource(svg, '/badge.svg')
        container.add_widget(wt.WImage(wt.WLink('/badge.svg'), 'badge'))

    Because WSvgImage is a WResource the same instance can be
    served to many clients.
    """

    def __init__(self, width: WLength, height: WLength) -> None:
        """
        Create an SVG paint surface of the given size. Construct a WPainter against it, paint, then mount the WSvgImage on a URL — clients fetch the SVG text.
        """

class WCanvasPaintDevice(WPaintDevice):
    """
    HTML5-canvas paint device. The same backend a WPaintedWidget uses when its render method is HtmlCanvas. Construct one directly only for off-screen / capture scenarios; for normal drawing into the page, use WPaintedWidget.
    """

    def __init__(self, width: WLength, height: WLength) -> None:
        """Create a canvas paint surface of the given size."""

class WMeasurePaintDevice(WPaintDevice):
    """
    Pass-through paint device that records the bounding rect of
    every draw operation without actually rendering. Useful for
    sizing an output canvas before allocating the real device.

        measure = wt.WMeasurePaintDevice(reference_device)
        p = wt.WPainter(measure)
        render(p)               # whatever paint code
        rect = measure.bounding_rect
    """

    def __init__(self, delegate: WPaintDevice) -> None:
        """
        Construct over an underlying device — `delegate` is consulted for font metrics but no rendering reaches it.
        """

    @property
    def bounding_rect(self) -> WRectF:
        """
        Union of every WRectF that's been painted into the measure device so far.
        """

class WPdfImage(WResource):
    """
    PDF paint device backed by a WResource. Paint into it with a
    WPainter, then mount it on a URL so clients can download or
    view the resulting PDF.

        pdf = wt.WPdfImage(wt.WLength(595), wt.WLength(842))  # A4
        p = wt.WPainter(pdf)
        p.draw_text(36, 36, 523, 30, wt.AlignmentFlag.Left, 'Report')
        p.draw_rect(36, 80, 523, 200)
        del p  # flush
        app.add_resource(pdf, '/report.pdf')

    Rendered by libharu. Only the 14 PDF base fonts are available
    by default — call `add_font_collection` first if you need a
    specific TrueType/Type1 font.
    """

    def __init__(self, width: WLength, height: WLength) -> None:
        """
        Create a PDF paint surface with the given page dimensions (typically in WLength.Point units — A4 portrait is roughly 595×842 pt).
        """

    def add_font_collection(self, directory: str, recursive: bool = True) -> None:
        """
        Search `directory` for TrueType / Type1 fonts and make them available to drawText. Pair with WFont.set_family(..., specific='Some Font') to reference one. Without registered fonts the PDF uses libharu's built-in 14 base fonts only.
        """

class ErrorCorrectionLevel(enum.Enum):
    """
    QR-code error-correction strength. Higher levels can survive
    more damage to the printed code but encode less data per pixel.
    """

    Low = 0
    """~7% of codewords can be restored."""

    Medium = 1
    """~15% recoverable."""

    Quartile = 2
    """~25% recoverable."""

    High = 3
    """~30% recoverable."""

class WQrCode(WInteractWidget):
    """
    A painted QR code. Encodes a text message as a 2D barcode and
    renders it as a vector image — scales cleanly to any size.

        qr = container.add_widget(wt.WQrCode('https://example.com', 4))
        qr.brush = wt.WBrush(wt.WColor(0, 64, 128))

    If the message is too long for the configured error-correction
    level, the `error` flag turns True — drop to a lower ECL or
    shorten the input.
    """

    @overload
    def __init__(self) -> None:
        """
        Construct an empty QR code. Set `message` and `square_size`
        before adding to a container.
        """

    @overload
    def __init__(self, message: str, square_size: float) -> None:
        """
        Construct encoding `message`, with each module rendered at
        `square_size` pixels and the default error-correction level.
        """

    @overload
    def __init__(self, message: str, ecl: ErrorCorrectionLevel, square_size: float) -> None:
        """
        Construct with text, error-correction level, and the size in pixels of each QR-code square.
        """

    @property
    def message(self) -> str:
        """The text encoded. Mutating triggers a re-paint."""

    @message.setter
    def message(self, arg: str, /) -> None: ...

    @property
    def square_size(self) -> float:
        """
        Side length in pixels of each QR-code module (the black/white
        squares). Larger values make a bigger, easier-to-scan code.
        """

    @square_size.setter
    def square_size(self, arg: float, /) -> None: ...

    def set_error_correction_level(self, ecl: ErrorCorrectionLevel) -> None:
        """
        Replace the active error-correction level. Triggers a
        re-encode and re-paint.
        """

    @property
    def brush(self) -> WBrush:
        """
        Brush used to paint the QR squares (default black solid). Tint with a colored brush; the background stays transparent.
        """

    @brush.setter
    def brush(self, arg: WBrush, /) -> None: ...

    @property
    def error(self) -> bool:
        """
        True if the encoder couldn't fit the message at the configured ECL — try Low or shorten the message.
        """

    def update(self) -> None:
        """
        Force a re-paint. Normally unnecessary — assignments to
        `message` / `brush` / `square_size` re-paint automatically.
        """

class GoogleMapsVersion(enum.Enum):
    """Google Maps JavaScript API version to load."""

    v3 = 0
    """The current (v3) Maps JS API."""

class MapTypeControl(enum.Enum):
    """
    Style of the map-type selector (roadmap / satellite / hybrid /
    terrain switch) rendered over the Google Map.
    """

    Default = 1
    """Whatever the Maps API uses by default for the device."""

    Menu = 2
    """Dropdown menu form."""

    Hierarchical = 3
    """Nested button/menu form for compact displays."""

    HorizontalBar = 4
    """Horizontal row of pill buttons."""

class GoogleMapCoordinate:
    """
    A latitude/longitude pair, used as positions/centres for
    WGoogleMap operations. Plain value type — copy freely.
    """

    @overload
    def __init__(self) -> None:
        """Construct (0, 0) — the null island."""

    @overload
    def __init__(self, latitude: float, longitude: float) -> None:
        """
        Construct from explicit latitude and longitude in decimal
        degrees (positive N/E, negative S/W).
        """

    @property
    def latitude(self) -> float:
        """Latitude in decimal degrees."""

    @latitude.setter
    def latitude(self, arg: float, /) -> None: ...

    @property
    def longitude(self) -> float:
        """Longitude in decimal degrees."""

    @longitude.setter
    def longitude(self, arg: float, /) -> None: ...

    def distance_to(self, other: GoogleMapCoordinate) -> float:
        """
        Great-circle distance to `other` in kilometres (despite Wt's docs naming metres).
        """

    def __repr__(self) -> str: ...

class WGoogleMap(WWidget):
    """
    Embedded Google Maps widget. Renders an interactive map served
    by the Google Maps JS API and lets server-side Python add markers,
    polylines, circles, and info windows.

        gmap = container.add_widget(wt.WGoogleMap(wt.GoogleMapsVersion.v3))
        gmap.set_center(wt.WGoogleMap.Coordinate(37.7749, -122.4194), 12)
        gmap.add_marker(wt.WGoogleMap.Coordinate(37.7749, -122.4194))

    Requires a Google Maps API key configured server-side via Wt's
    config XML (`google_api_key` property). Without it the widget
    renders an error pane.
    """

    def __init__(self, version: GoogleMapsVersion) -> None:
        """Construct against the given Google Maps API version."""

    @overload
    def set_center(self, center: GoogleMapCoordinate) -> None:
        """
        Pan the map so `center` is at the viewport centre. Keeps
        the current zoom level.
        """

    @overload
    def set_center(self, center: GoogleMapCoordinate, zoom: int) -> None:
        """Pan to `center` and set the zoom level in one call."""

    def pan_to(self, center: GoogleMapCoordinate) -> None:
        """
        Smoothly animate the viewport to `center` (vs. the snap-jump
        of `set_center`).
        """

    def set_zoom(self, level: int) -> None:
        """
        Set the zoom level (integer; ~0 = whole world, ~22 = street
        level depending on the area).
        """

    def zoom_in(self) -> None:
        """Increase the zoom level by one."""

    def zoom_out(self) -> None:
        """Decrease the zoom level by one."""

    def save_position(self) -> None:
        """
        Remember the current centre + zoom. Restore with return_to_saved_position.
        """

    def return_to_saved_position(self) -> None:
        """Pan/zoom back to whatever was last `save_position`'d."""

    def add_marker(self, position: GoogleMapCoordinate) -> None:
        """Drop the default Google-Maps pin at `position`."""

    def add_icon_marker(self, position: GoogleMapCoordinate, icon_url: str) -> None:
        """Marker with a custom icon image at `icon_url`."""

    def add_polyline(self, points: Sequence[GoogleMapCoordinate], color: WColor, width: int, opacity: float) -> None:
        """
        All four arguments mandatory — pass wt.WColor(...) and your line width / opacity explicitly.
        """

    def add_circle(self, center: GoogleMapCoordinate, radius_metres: float, stroke_color: WColor, stroke_width: int, fill_color: WColor) -> None:
        """
        Circle of `radius_metres` (a real distance, not pixels) around `center`.
        """

    def clear_overlays(self) -> None:
        """Remove every marker, polyline, circle, etc. added so far."""

    def open_info_window(self, position: GoogleMapCoordinate, html: str) -> None:
        """Show a Google-Maps info window with HTML content."""

    def zoom_window(self, top_left: GoogleMapCoordinate, bottom_right: GoogleMapCoordinate) -> None:
        """Zoom to fit the bounding box (top_left, bottom_right)."""

    Coordinate: TypeAlias = GoogleMapCoordinate

class LeafletMapCoordinate:
    """
    A latitude/longitude pair used as the position for WLeafletMap
    items. Plain value type — copy freely.
    """

    @overload
    def __init__(self) -> None:
        """Construct (0, 0)."""

    @overload
    def __init__(self, latitude: float, longitude: float) -> None:
        """Construct from explicit decimal-degree latitude and longitude."""

    @property
    def latitude(self) -> float:
        """Latitude in decimal degrees."""

    @latitude.setter
    def latitude(self, arg: float, /) -> None: ...

    @property
    def longitude(self) -> float:
        """Longitude in decimal degrees."""

    @longitude.setter
    def longitude(self, arg: float, /) -> None: ...

    def __repr__(self) -> str: ...

class WLeafletMapAbstractMapItem(WObject):
    """
    Abstract base for anything placed on a WLeafletMap — markers,
    popups, tooltips. Holds a coordinate and the standard set of
    mouse-interaction signals.
    """

    def move(self, pos: LeafletMapCoordinate) -> None:
        """
        Move the item to a new coordinate. Triggers a re-render if the item is already attached to a map.
        """

    @property
    def position(self) -> LeafletMapCoordinate:
        """The item's current coordinate."""

    @property
    def clicked(self) -> Signal:
        """
        Signal[] — user clicked the item. For overlay items (Popup, Tooltip), `interactive` must be set in options.
        """

    @property
    def double_clicked(self) -> Signal:
        """Signal[] — user double-clicked the item."""

    @property
    def mouse_went_down(self) -> Signal:
        """Signal[] — mouse button pressed over the item."""

    @property
    def mouse_went_up(self) -> Signal:
        """Signal[] — mouse button released over the item."""

    @property
    def mouse_went_over(self) -> Signal:
        """Signal[] — cursor entered the item."""

    @property
    def mouse_went_out(self) -> Signal:
        """Signal[] — cursor left the item."""

class WLeafletMapAbstractOverlayItem(WLeafletMapAbstractMapItem):
    """
    Common base for Popup and Tooltip — overlay items that hold a
    content widget and can be opened/closed.
    """

    def set_options(self, options: Json.Object) -> None:
        """
        Leaflet-side options for this overlay (autoClose, closeOnClick, etc.). See https://leafletjs.com/reference.html for the full list.
        """

    def set_content(self, content: WWidget) -> None:
        """
        Replace the overlay's content with a widget. Ownership transfers; the Python wrapper is re-armed as a non-owning alias.
        """

    def set_content_text(self, text: str) -> None:
        """
        Convenience: set content to a WText wrapping the given string. Same effect as set_content(WText(text)).
        """

    def open(self) -> None:
        """Show the overlay programmatically."""

    def close(self) -> None:
        """Hide the overlay programmatically."""

    def toggle(self) -> None:
        """Flip between open and closed."""

    @property
    def is_open(self) -> bool:
        """True if the overlay is currently visible."""

    @property
    def opened_signal(self) -> Signal:
        """Signal[] — fires when the overlay transitions to open."""

    @property
    def closed_signal(self) -> Signal:
        """Signal[] — fires when the overlay transitions to closed."""

class WLeafletMapPopup(WLeafletMapAbstractOverlayItem):
    """
    Floating overlay attached to a coordinate. Typically opens on
    marker click (when added via Marker.add_popup) or programmatically
    via open(). Content is either a WText shortcut or any widget.
    """

    @overload
    def __init__(self, pos: LeafletMapCoordinate) -> None:
        """
        Construct an empty popup anchored at `pos`. Set content
        later via set_content / set_content_text.
        """

    @overload
    def __init__(self, content: str) -> None:
        """Shortcut: popup whose content is a WText wrapping the given string."""

    @overload
    def __init__(self, pos: LeafletMapCoordinate, content: str) -> None:
        """Construct anchored at `pos` with the given text as content."""

    @overload
    def __init__(self, pos: LeafletMapCoordinate, content: WWidget) -> None:
        """
        Popup at `pos` with a widget content. Ownership of `content` transfers.
        """

class WLeafletMapTooltip(WLeafletMapAbstractOverlayItem):
    """
    Floating label attached to a coordinate. Like Popup but
    typically shown on hover instead of click. Same content API
    (string-shortcut or arbitrary widget).
    """

    @overload
    def __init__(self, pos: LeafletMapCoordinate) -> None:
        """Construct an empty tooltip anchored at `pos`."""

    @overload
    def __init__(self, content: str) -> None:
        """
        Shortcut: tooltip whose content is a WText wrapping the
        given string.
        """

    @overload
    def __init__(self, pos: LeafletMapCoordinate, content: str) -> None:
        """Construct anchored at `pos` with the given text as content."""

    @overload
    def __init__(self, pos: LeafletMapCoordinate, content: WWidget) -> None:
        """
        Tooltip at `pos` with a widget content. Ownership of
        `content` transfers.
        """

class WLeafletMapMarker(WLeafletMapAbstractMapItem):
    """
    Abstract base for map markers. Carries an optional Popup and
    Tooltip; concrete subclasses (LeafletMarker, WidgetMarker)
    decide what's actually rendered at the marker's position.
    """

    def add_popup(self, popup: _T_Popup) -> _T_Popup:
        """
        Attach a popup that opens when the marker is clicked. Replaces any previously-added popup on this marker.
        """

    def remove_popup(self) -> None:
        """Detach the currently-attached popup, if any."""

    @property
    def popup(self) -> WLeafletMapPopup:
        """Current popup, or None if none is attached."""

    def add_tooltip(self, tooltip: _T_Tooltip) -> _T_Tooltip:
        """
        Attach a tooltip that appears on hover. Replaces any previously-added tooltip.
        """

    def remove_tooltip(self) -> None:
        """Detach the currently-attached tooltip, if any."""

    @property
    def tooltip(self) -> WLeafletMapTooltip:
        """Current tooltip, or None if none is attached."""

class WLeafletMapLeafletMarker(WLeafletMapMarker):
    """
    Marker rendered as the default Leaflet pin. The standard
    round-headed marker drop you get from leafletjs by default.
    """

    def __init__(self, pos: LeafletMapCoordinate) -> None:
        """Construct the standard Leaflet pin marker."""

    def set_options(self, options: Json.Object) -> None:
        """
        Leaflet marker options (icon, draggable, riseOnHover, …). See https://leafletjs.com/reference.html#marker.
        """

class WLeafletMapWidgetMarker(WLeafletMapMarker):
    """
    Marker rendered as an arbitrary Wt widget — pin yourself a
    WImage, a WText, a WContainerWidget with custom HTML, etc.
    Useful when the default Leaflet pin isn't enough.
    """

    def __init__(self, pos: LeafletMapCoordinate, widget: WWidget) -> None:
        """
        Place an arbitrary Wt widget at `pos` on the map. Ownership of the widget transfers.
        """

    @property
    def widget(self) -> WWidget:
        """The widget rendered at the marker's position."""

    def set_anchor_point(self, x: float, y: float) -> None:
        """
        Anchor (the 'tip' of the marker relative to its top-left corner) in pixels. Negative x = horizontal center; negative y = vertical center. Default is centred both ways.
        """

class WLeafletMap(WWidget):
    """
    Interactive map widget powered by leafletjs. Unlike WGoogleMap,
    no API key is required — the widget renders tiles fetched from
    any compatible tile server (OpenStreetMap, Mapbox, etc.) that
    you configure via `add_tile_layer`.

        leaf = container.add_widget(wt.WLeafletMap())
        leaf.add_tile_layer(
            'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            tile_options)
        leaf.pan_to(wt.WLeafletMap.Coordinate(51.5074, -0.1278))
        leaf.zoom_level = 12
        leaf.add_marker(wt.WLeafletMap.LeafletMarker(
            wt.WLeafletMap.Coordinate(51.5074, -0.1278)))

    Markers, popups, and tooltips are added via add_marker /
    add_popup / add_tooltip. Each transfers ownership; the Python
    wrapper is re-armed as a non-owning alias so chaining works.
    """

    @overload
    def __init__(self) -> None:
        """Construct an empty map with default options."""

    @overload
    def __init__(self, options: Json.Object) -> None:
        """
        Construct with Leaflet map options (e.g. centre, zoom). Pass a Json.Object (or use the default ctor + set_options).
        """

    def set_options(self, options: Json.Object) -> None:
        """
        Replace the Leaflet map options. Effective for subsequent
        re-renders.
        """

    def add_tile_layer(self, url_template: str, options: Json.Object) -> None:
        """
        Add a tile source. `url_template` is a Leaflet URL template with {z}/{x}/{y} placeholders (e.g. 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'). `options` is a Json.Object holding Leaflet tile-layer options (maxZoom, attribution, subdomains, …).
        """

    def pan_to(self, center: LeafletMapCoordinate) -> None:
        """
        Smoothly animate the viewport so `center` is at the middle
        of the visible area.
        """

    @property
    def zoom_level(self) -> int:
        """
        Current zoom level (integer). Assigning sets it; mutating
        client-side via scroll/pinch reports back via
        `zoom_level_changed`.
        """

    @zoom_level.setter
    def zoom_level(self, arg: int, /) -> None: ...

    @property
    def position(self) -> LeafletMapCoordinate:
        """Current map centre coordinate. Use `pan_to` to set."""

    @property
    def zoom_level_changed(self) -> JIntSignal:
        """
        JIntSignal — fires with the new zoom level when the user scrolls or pinches.
        """

    def add_marker(self, marker: _T_Marker) -> _T_Marker:
        """
        Attach a Marker (LeafletMarker or WidgetMarker) to the map. Ownership transfers; the wrapper is re-armed as a non-owning alias, so chains like `m.add_marker(mkr).add_popup(p)` work.
        """

    def add_popup(self, popup: _T_Popup) -> _T_Popup:
        """
        Attach a standalone Popup to the map (separate from any marker). The popup opens at its configured coordinate.
        """

    def add_tooltip(self, tooltip: _T_Tooltip) -> _T_Tooltip:
        """
        Attach a standalone Tooltip to the map (separate from any
        marker). Ownership transfers; the wrapper is re-armed as a
        non-owning alias.
        """

    Coordinate: TypeAlias = LeafletMapCoordinate

    AbstractMapItem: TypeAlias = WLeafletMapAbstractMapItem

    AbstractOverlayItem: TypeAlias = WLeafletMapAbstractOverlayItem

    Popup: TypeAlias = WLeafletMapPopup

    Tooltip: TypeAlias = WLeafletMapTooltip

    Marker: TypeAlias = WLeafletMapMarker

    LeafletMarker: TypeAlias = WLeafletMapLeafletMarker

    WidgetMarker: TypeAlias = WLeafletMapWidgetMarker

class WColor:
    """
    An RGBA color value. Used wherever Wt asks for a color — most
    commonly as the value of WColorPicker.color, but also for brushes,
    pens, and chart palettes.

        sky = wt.WColor(135, 206, 235)
        picker = container.add_widget(wt.WColorPicker(sky))

    Construct from explicit RGB(A) components or from a CSS color
    string ('red', '#a0c0e0', 'rgb(160,192,224)'). Named colors
    round-trip via CSS only; the red/green/blue accessors return
    useful values only for numeric forms.
    """

    @overload
    def __init__(self) -> None:
        """Construct the default (transparent / inherit) color."""

    @overload
    def __init__(self, red: int, green: int, blue: int, alpha: int = 255) -> None:
        """
        Construct from 0-255 RGBA components. Alpha defaults to 255
        (fully opaque).
        """

    @overload
    def __init__(self, name: str) -> None:
        """
        Construct from a CSS color string — a named color ('red'),
        a hex literal ('#a0c0e0'), or an rgb()/rgba() form.
        """

    @property
    def red(self) -> int:
        """
        Red component (0-255). Only meaningful for colors built
        from numeric forms.
        """

    @property
    def green(self) -> int:
        """Green component (0-255)."""

    @property
    def blue(self) -> int:
        """Blue component (0-255)."""

    @property
    def alpha(self) -> int:
        """Alpha component (0-255). 0 = fully transparent."""

    @property
    def is_default(self) -> bool:
        """True for the default-constructed color (transparent/inherited)."""

    def set_rgb(self, red: int, green: int, blue: int, alpha: int = 255) -> None:
        """Replace the color with the given 0-255 RGBA components."""

    def set_name(self, name: str) -> None:
        """
        Replace the color with a CSS string (named color, hex,
        or rgb()/rgba() form).
        """

class WPasswordEdit(WLineEdit):
    """
    A single-line password input — renders as `<input type=password>`
    with the characters masked. Inherits WLineEdit, so the standard
    .text / .placeholder / .max_length all work. The password-specific
    properties (min_length, required, pattern) configure a built-in
    validator with its own error messages.

        pw = container.add_widget(wt.WPasswordEdit())
        pw.placeholder = 'Password'
        pw.min_length = 8
        pw.required = True
        container.add_widget(wt.WPushButton('Sign in')).clicked.connect(
            lambda: sign_in(pw.text))

    Attaching your own validator via set_validator replaces the
    built-in length/pattern checks.
    """

    def __init__(self) -> None:
        """Construct an empty password input with no built-in constraints."""

    @property
    def native_control(self) -> bool:
        """
        Use the browser's native <input type=password> behavior. Disable for full Wt-styled rendering.
        """

    @native_control.setter
    def native_control(self, arg: bool, /) -> None: ...

    @property
    def min_length(self) -> int:
        """Minimum password length. 0 means no minimum."""

    @min_length.setter
    def min_length(self, arg: int, /) -> None: ...

    @property
    def required(self) -> bool:
        """When True, an empty field fails validation."""

    @required.setter
    def required(self, arg: bool, /) -> None: ...

    @property
    def pattern(self) -> str:
        """Regular expression the password must match. Empty disables."""

    @pattern.setter
    def pattern(self, arg: str, /) -> None: ...

    @property
    def invalid_too_long_text(self) -> str:
        """Validation message shown when the entered password exceeds max_length."""

    @invalid_too_long_text.setter
    def invalid_too_long_text(self, arg: str, /) -> None: ...

    @property
    def invalid_too_short_text(self) -> str:
        """Validation message shown when shorter than min_length."""

    @invalid_too_short_text.setter
    def invalid_too_short_text(self, arg: str, /) -> None: ...

    @property
    def invalid_no_match_text(self) -> str:
        """Validation message when the password doesn't match pattern."""

    @invalid_no_match_text.setter
    def invalid_no_match_text(self, arg: str, /) -> None: ...

    @property
    def invalid_blank_text(self) -> str:
        """Validation message when required and left blank."""

    @invalid_blank_text.setter
    def invalid_blank_text(self, arg: str, /) -> None: ...

class WInPlaceEdit(WWidget):
    """
    Text that turns into a line edit when clicked. Useful for tables
    or detail panes where the user toggles between read and edit modes
    without a dedicated form.

        cell = container.add_widget(wt.WInPlaceEdit('Untitled'))
        cell.value_changed.connect(lambda new_text: save(new_text))

    By default a save/cancel pair of buttons is shown alongside the
    active editor; with_buttons=False makes the field auto-save on
    Enter or blur.
    """

    @overload
    def __init__(self, text: str) -> None:
        """Construct displaying `text` initially."""

    @overload
    def __init__(self, with_buttons: bool, text: str) -> None:
        """
        When `with_buttons` is False, the edit auto-saves on blur and no save/cancel buttons are shown.
        """

    @property
    def text(self) -> str:
        """
        The currently displayed text. Reads what was last accepted;
        assigning replaces the value programmatically without firing
        value_changed.
        """

    @text.setter
    def text(self, arg: str, /) -> None: ...

    @property
    def placeholder_text(self) -> str:
        """
        Greyed-out hint shown in the embedded line edit when the
        value is empty.
        """

    @placeholder_text.setter
    def placeholder_text(self, arg: str, /) -> None: ...

    def set_buttons_enabled(self, enabled: bool = True) -> None:
        """
        Show/hide the save/cancel buttons. When hidden, the edit auto-saves on Enter / blur.
        """

    @property
    def line_edit(self) -> WLineEdit:
        """
        The internal WLineEdit, exposed for fine-grained styling (placeholder, max length, validator).
        """

    @property
    def value_changed(self) -> StringSignal:
        """Signal[str] — fires with the new text when the user accepts an edit."""

class PopupTrigger(enum.Flag):
    """
    Bitfield deciding when a WSuggestionPopup opens against its
    attached edit. OR values together when passing to `for_edit`.
    """

    Editing = 1
    """Open while the user types."""

    DropDownIcon = 2
    """
    Render a dropdown-arrow icon next to the field; clicking it
    opens the popup unconditionally.
    """

class Options:
    """
    Behavior knobs for WSuggestionPopup. Default-construct, fill in
    the fields you care about, then pass to the WSuggestionPopup
    constructor.

        opts = wt.WSuggestionPopup.Options()
        opts.highlight_begin_tag = '<b>'
        opts.highlight_end_tag = '</b>'
        opts.word_separators = ' '
        popup = wt.WSuggestionPopup(opts)

    Empty defaults work for many cases but the runtime warns if a
    field it requires is left blank.
    """

    def __init__(self) -> None:
        """Construct with empty/zeroed fields. Assign the ones you need."""

    @property
    def highlight_begin_tag(self) -> str:
        """
        Markup wrapped around the matched portion of each suggestion
        (e.g. '<b>'). Empty disables highlighting.
        """

    @highlight_begin_tag.setter
    def highlight_begin_tag(self, arg: str, /) -> None: ...

    @property
    def highlight_end_tag(self) -> str:
        """Closing tag matching highlight_begin_tag."""

    @highlight_end_tag.setter
    def highlight_end_tag(self, arg: str, /) -> None: ...

    @property
    def list_separator(self) -> str:
        r"""
        Separator char for list-of-values fields. Empty/`'\0'` means the field holds a single value (no list).
        """

    @list_separator.setter
    def list_separator(self, arg: str, /) -> None: ...

    @property
    def whitespace(self) -> str:
        """
        Characters considered whitespace when locating word
        boundaries in the user's input.
        """

    @whitespace.setter
    def whitespace(self, arg: str, /) -> None: ...

    @property
    def word_separators(self) -> str:
        """
        Characters that separate words for the purpose of matching
        the next-typed-word against the suggestion list.
        """

    @word_separators.setter
    def word_separators(self, arg: str, /) -> None: ...

    @property
    def append_replaced_text(self) -> str:
        """Text appended after the chosen suggestion is inserted."""

    @append_replaced_text.setter
    def append_replaced_text(self, arg: str, /) -> None: ...

    @property
    def word_start_regexp(self) -> str:
        """
        Regex that identifies the start of a word in the input
        stream. Used when matching mid-string suggestions.
        """

    @word_start_regexp.setter
    def word_start_regexp(self, arg: str, /) -> None: ...

class IntFormWidgetSignal:
    """
    Signal carrying an int and a WFormWidget pointer. Used by
    WSuggestionPopup.activated — the int is the chosen row index in
    the popup's model and the widget is the edit that was being
    assisted.
    """

    def connect(self, callable: Callable) -> Connection:
        """
        Subscribe a Python callable. Returns a Connection — call
        `.disconnect()` to stop receiving.
        """

    def disconnect_all_slots(self) -> None:
        """Drop every Python subscriber attached via `connect`."""

class WSuggestionPopup(WWidget):
    """
    Autocomplete popup attached to one or more WFormWidgets. Holds a
    list of suggestions (either added directly or fed from a
    WAbstractItemModel) and offers them as the user types into a
    wired-up edit.

        opts = wt.WSuggestionPopup.Options()
        opts.highlight_begin_tag = '<b>'
        opts.highlight_end_tag = '</b>'
        popup = app.root.add_widget(wt.WSuggestionPopup(opts))
        for name in ['Alice', 'Bob', 'Charlie']:
            popup.add_suggestion(name)
        edit = container.add_widget(wt.WLineEdit())
        popup.for_edit(edit)
        popup.activated.connect(lambda row, w: print('picked', row))

    A single popup can serve several edits — `for_edit` adds an edit
    without detaching the previous ones.
    """

    def __init__(self, options: Options) -> None:
        """Construct with an Options config — see WSuggestionPopup.Options."""

    def for_edit(self, edit: WFormWidget, triggers: int = 1) -> None:
        """
        Attach this popup to a form widget. The popup will offer completions while the user edits the field. Pass triggers as a bitwise OR of PopupTrigger values.
        """

    def remove_edit(self, edit: WFormWidget) -> None:
        """Detach the popup from `edit`. Other edits stay wired."""

    def show_at(self, edit: WFormWidget) -> None:
        """
        Open the popup against `edit` programmatically, regardless
        of trigger configuration.
        """

    def clear_suggestions(self) -> None:
        """Empty the suggestion list."""

    def add_suggestion(self, text: str, value: str = '') -> None:
        """
        Add a string to the autocomplete list. If `value` is empty, the displayed `text` is also inserted on selection.
        """

    @property
    def filter_length(self) -> int:
        """Minimum input length before the popup activates."""

    @filter_length.setter
    def filter_length(self, arg: int, /) -> None: ...

    @property
    def default_index(self) -> int:
        """Row index pre-selected when the popup first opens; -1 for none."""

    @default_index.setter
    def default_index(self, arg: int, /) -> None: ...

    @property
    def current_item(self) -> int:
        """Index of the currently-highlighted suggestion; -1 if none."""

    def set_drop_down_icon_unfiltered(self, unfiltered: bool) -> None:
        """
        When True, clicking the drop-down icon shows all suggestions regardless of current input. Pairs with PopupTrigger.DropDownIcon.
        """

    def set_auto_select_enabled(self, enabled: bool) -> None:
        """
        When True, Enter pressed inside the edit accepts the
        currently-highlighted suggestion.
        """

    @property
    def activated(self) -> IntFormWidgetSignal:
        """
        IntFormWidgetSignal — fires when the user picks a suggestion. Slot receives (row_index, edit_widget); edit_widget is whichever WFormWidget the popup was for_edit'd against.
        """

    def set_model(self, model: WAbstractItemModel) -> None:
        """
        Replace the underlying suggestion source with a custom
        WAbstractItemModel. The default model is a WStringListModel
        populated by `add_suggestion`.
        """

    @property
    def model(self) -> WAbstractItemModel:
        """Current backing model (shared_ptr)."""

    class Options:
        """
        Behavior knobs for WSuggestionPopup. Default-construct, fill in
        the fields you care about, then pass to the WSuggestionPopup
        constructor.

            opts = wt.WSuggestionPopup.Options()
            opts.highlight_begin_tag = '<b>'
            opts.highlight_end_tag = '</b>'
            opts.word_separators = ' '
            popup = wt.WSuggestionPopup(opts)

        Empty defaults work for many cases but the runtime warns if a
        field it requires is left blank.
        """

        def __init__(self) -> None:
            """Construct with empty/zeroed fields. Assign the ones you need."""

        @property
        def highlight_begin_tag(self) -> str:
            """
            Markup wrapped around the matched portion of each suggestion
            (e.g. '<b>'). Empty disables highlighting.
            """

        @highlight_begin_tag.setter
        def highlight_begin_tag(self, arg: str, /) -> None: ...

        @property
        def highlight_end_tag(self) -> str:
            """Closing tag matching highlight_begin_tag."""

        @highlight_end_tag.setter
        def highlight_end_tag(self, arg: str, /) -> None: ...

        @property
        def list_separator(self) -> str:
            r"""
            Separator char for list-of-values fields. Empty/`'\0'` means the field holds a single value (no list).
            """

        @list_separator.setter
        def list_separator(self, arg: str, /) -> None: ...

        @property
        def whitespace(self) -> str:
            """
            Characters considered whitespace when locating word
            boundaries in the user's input.
            """

        @whitespace.setter
        def whitespace(self, arg: str, /) -> None: ...

        @property
        def word_separators(self) -> str:
            """
            Characters that separate words for the purpose of matching
            the next-typed-word against the suggestion list.
            """

        @word_separators.setter
        def word_separators(self, arg: str, /) -> None: ...

        @property
        def append_replaced_text(self) -> str:
            """Text appended after the chosen suggestion is inserted."""

        @append_replaced_text.setter
        def append_replaced_text(self, arg: str, /) -> None: ...

        @property
        def word_start_regexp(self) -> str:
            """
            Regex that identifies the start of a word in the input
            stream. Used when matching mid-string suggestions.
            """

        @word_start_regexp.setter
        def word_start_regexp(self, arg: str, /) -> None: ...

class WColorPicker(WFormWidget):
    """
    An `<input type=color>` element — the browser-native color picker.
    Renders as a swatch the user clicks to open the OS / browser color
    dialog.

        picker = container.add_widget(wt.WColorPicker(wt.WColor('#3366cc')))
        picker.changed.connect(lambda: apply_color(picker.color))
    """

    @overload
    def __init__(self) -> None:
        """Construct with the default (black) color."""

    @overload
    def __init__(self, color: WColor) -> None:
        """Construct with `color` as the initial selection."""

    @property
    def color(self) -> WColor:
        """
        The currently selected WColor. Assigning updates the swatch
        on the next round-trip.
        """

    @color.setter
    def color(self, arg: WColor, /) -> None: ...

    @property
    def color_input(self) -> EventSignal:
        """
        EventSignal[] — fires continuously while the user drags through the color picker. Use the inherited `changed` signal for commit-only notifications.
        """

class WTextEdit(WTextArea):
    """
    Rich-text editor backed by TinyMCE — a WYSIWYG widget producing
    HTML. Inherits WTextArea, so `.text` reads/writes the editor
    contents as an HTML string.

        editor = container.add_widget(wt.WTextEdit('<p>Hello</p>'))
        editor.set_extra_plugins('lists,advlist')
        container.add_widget(wt.WPushButton('Save')).clicked.connect(
            lambda: save_html(editor.text))

    TinyMCE itself is NOT bundled with Wt — the application must serve
    a TinyMCE build under /resources/tinymce/ (or wherever Wt is
    configured to look). Without it the widget falls back to a plain
    textarea.
    """

    @overload
    def __init__(self) -> None:
        """Construct an empty rich-text editor."""

    @overload
    def __init__(self, text: str) -> None:
        """Construct with initial HTML `text` in the editor."""

    @property
    def version(self) -> int:
        """
        TinyMCE version currently configured (3 or 4 depending on what Wt was built against and what's on disk).
        """

    @property
    def style_sheet(self) -> str:
        """
        Comma-separated list of stylesheets applied inside the editor iframe — also drives the 'styleselect' button options.
        """

    @style_sheet.setter
    def style_sheet(self, arg: str, /) -> None: ...

    def set_extra_plugins(self, plugins: str) -> None:
        """
        Comma-separated TinyMCE plugin names to load on top of the default 'safari' plugin.
        """

    def set_tool_bar(self, row: int, config: str) -> None:
        """
        Configure a single toolbar row by index (0-based). `config` is a TinyMCE 'theme_advanced_buttons_N' string, e.g. 'bold,italic,|,bullist'.
        """

    def set_configuration_setting(self, name: str, value: "std::any") -> None:
        """
        Forward a setting straight to TinyMCE's init() config. `value` is anything TinyMCE accepts as JSON.
        """

class FilePickerType(enum.Enum):
    """
    Which native browser picker WFileDropWidget opens when the
    user clicks the dropzone — files, folders, or neither.
    """

    FileSelection = 1

    DirectorySelection = 2

class WFileDropWidgetFile(WObject):
    """
    Metadata + per-file signals for one file that has been (or is
    being) uploaded through a WFileDropWidget. Read the browser-
    reported `client_file_name` / `size` / `mime_type` before the
    transfer starts; wait on `uploaded` to get `uploaded_file`, which
    carries the on-disk path of the spooled bytes.

        def on_done(f):
            print(f.client_file_name, '->', f.uploaded_file.spool_file_name)
        drop.uploaded.connect(on_done)

    Owned by the parent WFileDropWidget — pointers handed to signal
    callbacks are valid only as long as the widget keeps the file in
    its `uploads` list. Don't stash them beyond the callback.
    """

    @property
    def client_file_name(self) -> str:
        """
        Original filename reported by the browser. Untrusted — sanitise before use as a server-side path.
        """

    @property
    def path(self) -> str:
        """
        Relative path inside the dropped folder, or empty if a single file was dropped.
        """

    @property
    def directory(self) -> bool:
        """
        True iff this entry represents a directory (only when the browser supports folder uploads and the user dropped one).
        """

    @property
    def mime_type(self) -> str:
        """MIME type reported by the browser. Untrusted."""

    @property
    def size(self) -> int:
        """
        File size in bytes as reported by the browser, before the upload starts.
        """

    @property
    def upload_finished(self) -> bool:
        """True iff the bytes have arrived server-side."""

    @property
    def uploaded_file(self) -> UploadedFile:
        """
        The completed upload, as an UploadedFile (with the spool file path). Raises if called before `upload_finished` is True.
        """

    @property
    def data_received(self) -> "Wt::Signal<unsigned long, unsigned long>":
        """Uint64PairSignal — per-file progress ticks (received, total) in bytes."""

    @property
    def uploaded(self) -> Signal:
        """
        Signal[] — fires when this individual file's upload finishes. WFileDropWidget.uploaded fires too with the File* payload.
        """

    @property
    def filter_enabled(self) -> bool:
        """
        Whether the JS filter (set via WFileDropWidget) processes this file before upload. Defaults to True when a filter is set.
        """

    @filter_enabled.setter
    def filter_enabled(self, arg: bool, /) -> None: ...

    @property
    def is_filtered(self) -> bool:
        """True iff the JS filter already ran on this file's bytes."""

class WFileDropWidgetDirectory(WFileDropWidgetFile):
    """
    A File subclass representing a dropped folder rather than a
    single file. Only produced when the widget has
    `set_accept_directories(True)` and the user drops a folder; check
    `isinstance(f, wt.WFileDropWidget.Directory)` from a drop handler
    to branch on it. `contents` walks the folder's entries (which may
    themselves be Directories for recursive drops).
    """

    @property
    def contents(self) -> list[WFileDropWidgetFile]:
        """
        List[File] — children of this folder. For recursive drops these may themselves include further Directory entries.
        """

    @property
    def directory(self) -> bool:
        """
        Always True for Directory — shadows File.directory() for ergonomic type discrimination.
        """

class FileSignal:
    """
    Signal carrying a single WFileDropWidget.File pointer. Used by
    the widget's `new_upload`, `uploaded`, and `upload_failed`
    signals — connect a `callable(file)` to react.
    """

    def connect(self, callable: Callable) -> Connection:
        """
        Subscribe `callable(file)` to the signal. Returns a
        Connection — call `.disconnect()` to stop receiving.
        """

    def disconnect_all_slots(self) -> None:
        """Drop every callback previously connected through this binding."""

class FileListSignal:
    """
    Signal carrying a list of WFileDropWidget.File pointers. Used by
    the widget's `drop` signal — fires once per drop event with the
    freshly-introduced files.
    """

    def connect(self, callable: Callable) -> Connection:
        """
        Subscribe `callable(files)` to the signal. Returns a
        Connection — call `.disconnect()` to stop receiving.
        """

    def disconnect_all_slots(self) -> None:
        """Drop every callback previously connected through this binding."""

class FileSizeSignal:
    """
    Signal carrying (file, size_bytes). Used by `too_large` when a
    dropped file exceeds the configured maximum request size.
    """

    def connect(self, callable: Callable) -> Connection:
        """
        Subscribe `callable(file, size)` to the signal. Returns a
        Connection — call `.disconnect()` to stop receiving.
        """

    def disconnect_all_slots(self) -> None:
        """Drop every callback previously connected through this binding."""

class WFileDropWidget(WContainerWidget):
    """
    Drag-and-drop upload zone. Drop files (and optionally folders)
    onto the widget, or click it to open the browser's native
    picker. Files queue up and upload sequentially in the background
    so the UI stays responsive; per-file lifecycle signals let you
    render a queue / progress list.

        drop = container.add_widget(wt.WFileDropWidget())
        drop.add_widget(wt.WText('Drop files here'))
        def on_drop(files):
            for f in files:
                print('queued:', f.client_file_name)
        drop.drop.connect(on_drop)
        def on_done(f):
            shutil.move(f.uploaded_file.spool_file_name, '/store/' + f.client_file_name)
        drop.uploaded.connect(on_done)

    Inherits WContainerWidget — child widgets become the visible
    body (instructions, an icon, …). Uploaded bytes land in a temp
    spool file; copy or move them somewhere durable before the file
    is dropped from `uploads`.
    """

    def __init__(self) -> None:
        """
        Construct an empty drop zone that accepts files (not
        folders) and shows the browser's file picker on click.
        """

    @property
    def uploads(self) -> list[WFileDropWidgetFile]:
        """
        List[File] — all files known to the widget, including ones whose upload is queued, in progress, completed, or cancelled. Pointers reference internal widget state.
        """

    @property
    def current_index(self) -> int:
        """
        Index into `uploads` of the file currently being transmitted. Equals len(uploads) when idle.
        """

    def cancel_upload(self, file: WFileDropWidgetFile) -> None:
        """
        Cancel a queued or in-progress upload. The File stays in `uploads` but is marked cancelled.
        """

    def remove(self, file: WFileDropWidgetFile) -> bool:
        """
        Drop a completed file from `uploads` to free its temp file. Only valid for files at indices strictly before current_index.
        """

    def clean_directory_resources(self) -> None:
        """
        Release Directory bookkeeping once you no longer need it. Files themselves remain.
        """

    def set_accept_drops(self, enable: bool) -> None:
        """
        When True (the default), drag-and-drop is active. Set to
        False to limit input to the click-to-pick path.
        """

    def set_filters(self, accept_attributes: str) -> None:
        """
        Hint to the file-picker dialog: a comma-separated list of MIME types or extensions (e.g. 'image/png,.csv'). Doesn't constrain drag-drop — re-check content_type server-side.
        """

    @property
    def drop_indication_enabled(self) -> bool:
        """
        When True, the widget visually highlights itself during hover. When False the host page is responsible for any drop UI.
        """

    @drop_indication_enabled.setter
    def drop_indication_enabled(self, arg: bool, /) -> None: ...

    @property
    def global_drop_enabled(self) -> bool:
        """
        When True, files dropped anywhere on the page route to this widget. Use sparingly — only one widget per app should set this.
        """

    @global_drop_enabled.setter
    def global_drop_enabled(self, arg: bool, /) -> None: ...

    def set_on_click_file_picker(self, type: FilePickerType) -> None:
        """
        Which browser dialog opens when the user clicks the widget: FilePickerType.FileSelection (default), .DirectorySelection, or .None_ to disable.
        """

    @property
    def on_click_file_picker(self) -> FilePickerType:
        """The FilePickerType the widget opens on click."""

    def open_file_picker(self) -> None:
        """
        Programmatically open the file picker as if the user clicked. Useful when wiring the widget to an external button.
        """

    def open_directory_picker(self) -> None:
        """
        Programmatically open the directory picker. Requires that
        `set_accept_directories(True)` has been set.
        """

    def set_accept_directories(self, enable: bool, recursive: bool = False) -> None:
        """
        Allow folder drops. When `recursive` is True, subfolders are also walked. Default is files-only.
        """

    @property
    def drop(self) -> FileListSignal:
        """
        FileListSignal — fires once per drop with the list of newly-introduced File entries (these get appended to `uploads`). The actual byte transfer is sequential and tracked through `new_upload` / `uploaded`.
        """

    @property
    def new_upload(self) -> FileSignal:
        """
        FileSignal — fires immediately before the bytes of the next file in the queue start arriving.
        """

    @property
    def uploaded(self) -> FileSignal:
        """
        FileSignal — fires when a single file's upload completes. The File's `uploaded_file` is now valid.
        """

    @property
    def too_large(self) -> FileSizeSignal:
        """
        FileSizeSignal — fires with (file, size) when one of the dropped files exceeds the configured max-request-size. That file's upload is skipped; the queue carries on with the next.
        """

    @property
    def upload_failed(self) -> FileSignal:
        """
        FileSignal — fires when an upload errors out for reasons other than oversize (e.g. browser disconnect).
        """

    File: TypeAlias = WFileDropWidgetFile

    Directory: TypeAlias = WFileDropWidgetDirectory

class AlignmentFlag(enum.IntEnum):
    """
    Bit flags for positioning items inside containers that support
    left/right justification (WNavigationBar, WToolBar) or horizontal/
    vertical alignment (WBoxLayout, WGridLayout). The arithmetic trait
    lets the values be OR'd together where Wt accepts a combined flag
    set.
    """

    Left = 1

    Right = 2

    Center = 4

    Justify = 8

    Baseline = 16

    Top = 128

    Middle = 512

    Bottom = 1024

class WPoint:
    """
    Integer (x, y) coordinate pair in page-relative pixels.
    Used as the position argument to `WPopupMenu.popup(point)`.

        menu.popup(wt.WPoint(120, 80))
    """

    @overload
    def __init__(self) -> None:
        """Construct a point at the origin (0, 0)."""

    @overload
    def __init__(self, x: int, y: int) -> None:
        """Construct a point at (`x`, `y`)."""

    @property
    def x(self) -> int:
        """Horizontal coordinate in pixels."""

    @x.setter
    def x(self, arg: int, /) -> None: ...

    @property
    def y(self) -> int:
        """Vertical coordinate in pixels."""

    @y.setter
    def y(self, arg: int, /) -> None: ...

    def __repr__(self) -> str: ...

class WPopupMenu(WMenu):
    """
    Floating menu that appears at a screen location on demand.
    Inherits the full WMenu surface (add_item, etc.) so building
    entries works the same; what's added is the ability to summon
    the menu at a point, at a mouse event, or anchored to a widget.

        menu = wt.WPopupMenu()
        menu.add_item('Cut')
        menu.add_item('Copy')
        container.add_widget(wt.WPushButton('Edit')).clicked.connect(
            lambda e: menu.popup(e))
        menu.triggered.connect(lambda item: handle(item.text))

    Pair with `set_button(btn)` for the typical menu-button UX, or
    call `popup(...)` yourself from a slot. With `hide_on_select`
    left at its default of True, `triggered` is the signal you watch
    for to know the user picked something.
    """

    def __init__(self) -> None:
        """
        Construct a standalone popup menu with no items. Use the
        inherited `add_item` to populate it.
        """

    @overload
    def popup(self, point: WPoint) -> None:
        """Show the menu at an absolute screen coordinate (page-relative pixels)."""

    @overload
    def popup(self, event: WMouseEvent) -> None:
        """
        Show the menu at the location of a mouse event — convenient from a clicked-handler slot.
        """

    @overload
    def popup(self, location: WWidget, orientation: Orientation = Orientation.Vertical) -> None:
        """
        Show the menu anchored to a widget; orientation controls drop-direction.
        """

    def set_button(self, button: WInteractWidget) -> None:
        """
        Wire `button.clicked` to popup() so the menu opens when the button is clicked. The button is just associated, not owned.
        """

    @property
    def hide_on_select(self) -> bool:
        """When True (default), picking an item hides the popup."""

    @hide_on_select.setter
    def hide_on_select(self, arg: bool, /) -> None: ...

    def set_auto_hide(self, enabled: bool, auto_hide_delay_ms: int = 0) -> None:
        """
        When True, the popup hides itself after the mouse leaves it; `auto_hide_delay_ms` adds a grace period.
        """

    @property
    def about_to_hide(self) -> Signal:
        """
        Signal[] — fires once when the popup is about to close, regardless of how (selection, click-outside, auto-hide). Use this for cleanup.
        """

    @property
    def triggered(self) -> MenuItemSignal:
        """
        MenuItemSignal — fires when the user picks an item. Unlike WMenu.item_selected, this fires only for interactive selection (programmatic .select() is silent).
        """

class WBadge(WText):
    """
    Small inline label, typically appended to another widget for
    counts or status pills (e.g. '12 unread'). Inherits WText, so
    set the displayed value via the `text` property.

        btn = container.add_widget(wt.WPushButton('Inbox'))
        btn.add_widget(wt.WBadge('12'))
    """

    @overload
    def __init__(self) -> None:
        """Construct an empty badge with no caption."""

    @overload
    def __init__(self, text: str) -> None:
        """Construct a badge displaying `text`."""

    @property
    def use_default_style(self) -> bool:
        """
        When True (default), Wt applies its theme's badge CSS class. Disable to style purely via your own classes/CSS.
        """

    @use_default_style.setter
    def use_default_style(self, arg: bool, /) -> None: ...

class WToolBar(WWidget):
    """
    A row (or column) of buttons with optional separators between
    groups. Add buttons via `add_button`; mix in arbitrary widgets
    with `add_widget` for non-button controls.

        bar = container.add_widget(wt.WToolBar())
        bar.add_button(wt.WPushButton('Save')).clicked.connect(save)
        bar.add_separator()
        bar.add_button(wt.WPushButton('Quit')).clicked.connect(app.quit)
    """

    def __init__(self) -> None:
        """Construct an empty toolbar with horizontal orientation."""

    def set_orientation(self, orientation: Orientation) -> None:
        """
        Horizontal or Vertical layout for the buttons. Write-only on the C++ side; no getter is exposed by Wt.
        """

    @property
    def compact(self) -> bool:
        """When True, buttons are visually grouped (no internal margins)."""

    @compact.setter
    def compact(self, arg: bool, /) -> None: ...

    @property
    def count(self) -> int:
        """Number of items (buttons or widgets) currently in the toolbar."""

    def add_button(self, button: _T_Button, alignment: AlignmentFlag = AlignmentFlag.Left) -> _T_Button:
        """
        Transfer ownership of `button` to the toolbar (a WPushButton
        or WSplitButton) and return the same Python wrapper, re-armed
        as a non-owning alias for chaining. `alignment` controls
        left/right placement when the theme supports it.

            bar.add_button(wt.WPushButton('Help'),
                           wt.AlignmentFlag.Right).clicked.connect(open_help)
        """

    def add_widget(self, widget: _T_Widget, alignment: AlignmentFlag = AlignmentFlag.Left) -> _T_Widget:
        """
        Add an arbitrary widget (not necessarily a button) to the
        toolbar at the given alignment. Same ownership-transfer +
        re-arm pattern as `add_button`.
        """

    def add_separator(self) -> None:
        """Add a visual divider between groups of items."""

class WSplitButton(WWidget):
    """
    A primary action button with a small chevron next to it that
    opens a dropdown menu — the typical 'Save / Save As…' split
    button found in toolbars. Build a WPopupMenu, attach it via
    `set_menu`, then wire `action_button.clicked` for the default
    action.

        sb = bar.add_button(wt.WSplitButton('Save'))
        sb.action_button.clicked.connect(save_default)
        menu = wt.WPopupMenu()
        menu.add_item('Save As…')
        menu.add_item('Save All')
        sb.set_menu(menu)
    """

    @overload
    def __init__(self) -> None:
        """Construct an unlabelled split button with no menu attached."""

    @overload
    def __init__(self, label: str) -> None:
        """
        Construct a split button captioned `label` with no menu
        attached. Use `set_menu` to wire the dropdown.
        """

    @property
    def action_button(self) -> WPushButton:
        """The primary (left) button — connect `clicked` for the default action."""

    @property
    def drop_down_button(self) -> WPushButton:
        """
        The chevron (right) button — clicking it opens the attached WPopupMenu.
        """

    def set_menu(self, menu: WPopupMenu) -> None:
        """
        Attach a WPopupMenu as the dropdown. Ownership transfers to the split button; the Python wrapper becomes a non-owning alias of the menu the split button now holds.
        """

class WNavigationBar(WTemplate):
    """
    A page-top navigation bar in the Bootstrap idiom: brand on the
    left, menus and form fields stacked horizontally, optional
    search box. Collapses into a hamburger menu on narrow viewports
    when `set_responsive(True)` is set.

        nav = app.root.add_widget(wt.WNavigationBar())
        nav.set_title('My App', wt.WLink('/'))
        nav.set_responsive(True)
        menu = wt.WMenu()
        menu.add_item('Home')
        menu.add_item('About')
        nav.add_menu(menu)
    """

    def __init__(self) -> None:
        """
        Construct an empty navigation bar. Use `set_title` /
        `add_menu` / `add_search` to populate it.
        """

    def set_title(self, title: str, link: WLink = ...) -> None:
        """
        Set the brand/title shown at the left of the nav bar. Optionally wraps it in a link.
        """

    def set_responsive(self, responsive: bool) -> None:
        """
        When True, collapses the contents into a hamburger menu on narrow viewports (Bootstrap responsive behaviour). Wt has no getter for this — the flag is write-only on the C++ side.
        """

    def add_menu(self, menu: _T_Menu, alignment: AlignmentFlag = AlignmentFlag.Left) -> _T_Menu:
        """
        Embed a WMenu in the nav bar. Ownership transfers; the
        Python wrapper is re-armed as a non-owning alias of the menu
        the bar now holds.
        """

    def add_form_field(self, widget: _T_Widget, alignment: AlignmentFlag = AlignmentFlag.Left) -> _T_Widget:
        """
        Embed a form field (e.g. a small WLineEdit for a search bar). Distinct from the standalone add_search variant only in styling.
        """

    def add_search(self, field: _T_LineEdit, alignment: AlignmentFlag = AlignmentFlag.Left) -> _T_LineEdit:
        """
        Add a styled search box (a WLineEdit) to the nav bar.
        Functionally similar to `add_form_field` but themed as a
        search input.
        """

    def add_widget(self, widget: _T_Widget, alignment: AlignmentFlag = AlignmentFlag.Left) -> _T_Widget:
        """
        Add an arbitrary widget to the nav bar at the given
        alignment. Same ownership-transfer + re-arm pattern as
        `add_menu`.
        """
