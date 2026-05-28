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


from . import Json as Json, chart as chart


class Coordinates:
    def __init__(self, x: int, y: int) -> None: ...

    @property
    def x(self) -> int: ...

    @x.setter
    def x(self, arg: int, /) -> None: ...

    @property
    def y(self) -> int: ...

    @y.setter
    def y(self, arg: int, /) -> None: ...

    def __repr__(self) -> str: ...

class MouseButton(enum.IntEnum):
    Left = 1

    Middle = 2

    Right = 4

class KeyboardModifier(enum.IntEnum):
    Shift = 1

    Control = 2

    Alt = 4

    Meta = 8

class Key(enum.IntEnum):
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
    @property
    def button(self) -> MouseButton: ...

    @property
    def modifiers(self) -> int: ...

    @property
    def document(self) -> Coordinates: ...

    @property
    def window(self) -> Coordinates: ...

    @property
    def screen(self) -> Coordinates: ...

    @property
    def widget(self) -> Coordinates: ...

    @property
    def wheel_delta(self) -> int: ...

class WKeyEvent:
    @property
    def key(self) -> Key: ...

    @property
    def char_code(self) -> int: ...

    @property
    def modifiers(self) -> int: ...

class Connection:
    def disconnect(self) -> None: ...

    def is_connected(self) -> bool: ...

class Signal:
    def __init__(self) -> None: ...

    def connect(self, callable: Callable) -> Connection: ...

    def emit(self) -> None: ...

    def disconnect_all_slots(self) -> None: ...

class IntSignal:
    def __init__(self) -> None: ...

    def connect(self, callable: Callable) -> Connection: ...

    def emit(self, arg: int, /) -> None: ...

    def disconnect_all_slots(self) -> None: ...

class BoolSignal:
    def __init__(self) -> None: ...

    def connect(self, callable: Callable) -> Connection: ...

    def emit(self, arg: bool, /) -> None: ...

    def disconnect_all_slots(self) -> None: ...

class DoubleSignal:
    def __init__(self) -> None: ...

    def connect(self, callable: Callable) -> Connection: ...

    def emit(self, arg: float, /) -> None: ...

    def disconnect_all_slots(self) -> None: ...

class StringSignal:
    def __init__(self) -> None: ...

    def connect(self, callable: Callable) -> Connection: ...

    def emit(self, arg: str, /) -> None: ...

    def disconnect_all_slots(self) -> None: ...

class EventSignal:
    def connect(self, callable: Callable) -> Connection: ...

    def disconnect_all_slots(self) -> None: ...

class MouseEventSignal:
    def connect(self, callable: Callable) -> Connection: ...

    def disconnect_all_slots(self) -> None: ...

class KeyEventSignal:
    def connect(self, callable: Callable) -> Connection: ...

    def disconnect_all_slots(self) -> None: ...

class JIntSignal:
    def connect(self, callable: Callable) -> Connection: ...

    def disconnect_all_slots(self) -> None: ...

class JInt64Signal:
    def connect(self, callable: Callable) -> Connection: ...

    def disconnect_all_slots(self) -> None: ...

class Uint64PairSignal:
    def connect(self, callable: Callable) -> Connection: ...

    def disconnect_all_slots(self) -> None: ...

class WEnvironment:
    @property
    def user_agent(self) -> str: ...

    @property
    def host_name(self) -> str: ...

    @property
    def url_scheme(self) -> str: ...

    @property
    def internal_path(self) -> str: ...

    @property
    def supports_cookies(self) -> bool: ...

    @property
    def server_signature(self) -> str: ...

class WObject:
    def bind_safe(self, function: Callable[[], None]) -> Callable[[], None]:
        """
        Wrap `function` to no-op if this WObject is destroyed before it's invoked. Use for cross-thread callbacks to WServer.post() that reference widget state.
        """

class WWidget(WObject):
    def set_width(self, arg: float, /) -> None: ...

    def set_height(self, arg: float, /) -> None: ...

    @property
    def hidden(self) -> bool: ...

    @hidden.setter
    def hidden(self, arg: bool, /) -> None: ...

    def animate_show(self, animation: WAnimation) -> None:
        """
        Show the widget with a transition. Pass a `WAnimation` describing the slide/fade/timing.
        """

    def animate_hide(self, animation: WAnimation) -> None:
        """Hide with a transition. Inverse of animate_show."""

    @property
    def style_class(self) -> str: ...

    @style_class.setter
    def style_class(self, arg: str, /) -> None: ...

    def add_style_class(self, arg: str, /) -> None: ...

    def remove_style_class(self, arg: str, /) -> None: ...

    @property
    def id(self) -> str: ...

    @id.setter
    def id(self, arg: str, /) -> None: ...

    @property
    def tool_tip(self) -> str: ...

    @tool_tip.setter
    def tool_tip(self, arg: str, /) -> None: ...

class WInteractWidget(WWidget):
    @property
    def clicked(self) -> MouseEventSignal: ...

    @property
    def double_clicked(self) -> MouseEventSignal: ...

    @property
    def mouse_over(self) -> MouseEventSignal: ...

    @property
    def mouse_out(self) -> MouseEventSignal: ...

    @property
    def key_pressed(self) -> KeyEventSignal: ...

    @property
    def key_went_down(self) -> KeyEventSignal: ...

    @property
    def enter_pressed(self) -> EventSignal: ...

class ValidationState(enum.Enum):
    Invalid = 0

    InvalidEmpty = 1

    Valid = 2

class ValidationResult:
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, state: ValidationState) -> None: ...

    @overload
    def __init__(self, state: ValidationState, message: str) -> None: ...

    @property
    def state(self) -> ValidationState: ...

    @property
    def message(self) -> str: ...

    def __repr__(self) -> str: ...

class ValidationResultSignal:
    def connect(self, callable: Callable) -> Connection: ...

    def disconnect_all_slots(self) -> None: ...

class WValidator:
    @property
    def mandatory(self) -> bool: ...

    @mandatory.setter
    def mandatory(self, arg: bool, /) -> None: ...

    @property
    def invalid_blank_text(self) -> str: ...

    @invalid_blank_text.setter
    def invalid_blank_text(self, arg: str, /) -> None: ...

    def validate(self, input: str) -> ValidationResult: ...

class WIntValidator(WValidator):
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, minimum: int, maximum: int) -> None: ...

    @property
    def bottom(self) -> int: ...

    @bottom.setter
    def bottom(self, arg: int, /) -> None: ...

    @property
    def top(self) -> int: ...

    @top.setter
    def top(self, arg: int, /) -> None: ...

    def set_range(self, bottom: int, top: int) -> None: ...

    @property
    def invalid_not_a_number_text(self) -> str: ...

    @invalid_not_a_number_text.setter
    def invalid_not_a_number_text(self, arg: str, /) -> None: ...

    @property
    def invalid_too_small_text(self) -> str: ...

    @invalid_too_small_text.setter
    def invalid_too_small_text(self, arg: str, /) -> None: ...

    @property
    def invalid_too_large_text(self) -> str: ...

    @invalid_too_large_text.setter
    def invalid_too_large_text(self, arg: str, /) -> None: ...

    @property
    def ignore_trailing_spaces(self) -> bool: ...

    @ignore_trailing_spaces.setter
    def ignore_trailing_spaces(self, arg: bool, /) -> None: ...

class WDoubleValidator(WValidator):
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, minimum: float, maximum: float) -> None: ...

    @property
    def bottom(self) -> float: ...

    @bottom.setter
    def bottom(self, arg: float, /) -> None: ...

    @property
    def top(self) -> float: ...

    @top.setter
    def top(self, arg: float, /) -> None: ...

    def set_range(self, bottom: float, top: float) -> None: ...

    @property
    def invalid_not_a_number_text(self) -> str: ...

    @invalid_not_a_number_text.setter
    def invalid_not_a_number_text(self, arg: str, /) -> None: ...

    @property
    def invalid_too_small_text(self) -> str: ...

    @invalid_too_small_text.setter
    def invalid_too_small_text(self, arg: str, /) -> None: ...

    @property
    def invalid_too_large_text(self) -> str: ...

    @invalid_too_large_text.setter
    def invalid_too_large_text(self, arg: str, /) -> None: ...

class WLengthValidator(WValidator):
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, minimum_length: int, maximum_length: int) -> None: ...

    @property
    def minimum_length(self) -> int: ...

    @minimum_length.setter
    def minimum_length(self, arg: int, /) -> None: ...

    @property
    def maximum_length(self) -> int: ...

    @maximum_length.setter
    def maximum_length(self, arg: int, /) -> None: ...

    @property
    def invalid_too_short_text(self) -> str: ...

    @invalid_too_short_text.setter
    def invalid_too_short_text(self, arg: str, /) -> None: ...

    @property
    def invalid_too_long_text(self) -> str: ...

    @invalid_too_long_text.setter
    def invalid_too_long_text(self, arg: str, /) -> None: ...

class WRegExpValidator(WValidator):
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, pattern: str) -> None: ...

    @property
    def pattern(self) -> str: ...

    @pattern.setter
    def pattern(self, arg: str, /) -> None: ...

    @property
    def invalid_no_match_text(self) -> str: ...

    @invalid_no_match_text.setter
    def invalid_no_match_text(self, arg: str, /) -> None: ...

class WEmailValidator(WValidator):
    def __init__(self) -> None: ...

    @property
    def multiple(self) -> bool: ...

    @multiple.setter
    def multiple(self, arg: bool, /) -> None: ...

    @property
    def pattern(self) -> str: ...

    @pattern.setter
    def pattern(self, arg: str, /) -> None: ...

    @property
    def invalid_not_an_email_address_text(self) -> str: ...

    @invalid_not_an_email_address_text.setter
    def invalid_not_an_email_address_text(self, arg: str, /) -> None: ...

class WStackedValidator(WValidator):
    def __init__(self) -> None: ...

    def add_validator(self, validator: WValidator) -> None: ...

    def insert_validator(self, index: int, validator: WValidator) -> None: ...

    def remove_validator(self, validator: WValidator) -> None: ...

    @property
    def size(self) -> int: ...

    def clear(self) -> None: ...

class WFormWidget(WInteractWidget):
    @property
    def enabled(self) -> bool: ...

    @enabled.setter
    def enabled(self, arg: bool, /) -> None: ...

    def set_focus(self) -> None: ...

    @property
    def changed(self) -> EventSignal: ...

    def set_validator(self, validator: WValidator) -> None: ...

    @property
    def validator(self) -> WValidator: ...

    @property
    def validated(self) -> ValidationResultSignal: ...

class WApplication(WObject):
    def __init__(self, environment: WEnvironment) -> None: ...

    @property
    def root(self) -> WContainerWidget: ...

    @property
    def environment(self) -> WEnvironment: ...

    @property
    def title(self) -> str: ...

    @title.setter
    def title(self, arg: str, /) -> None: ...

    def set_internal_path(self, path: str, emit_change: bool = False) -> None: ...

    @property
    def internal_path(self) -> str: ...

    @property
    def session_id(self) -> str: ...

    def redirect(self, arg: str, /) -> None: ...

    def quit(self) -> None: ...

    def trigger_update(self) -> None:
        """
        Force a server-initiated update push to the connected client. Combine with WServer.post() for cross-thread updates.
        """

    @staticmethod
    def instance() -> WApplication: ...

    @property
    def theme(self) -> WTheme: ...

    @theme.setter
    def theme(self, arg: WTheme, /) -> None: ...

class UpdateLock:
    def __init__(self, application: WApplication) -> None:
        """
        Acquire the application's update lock. Use bool(lock) to check success — it may fail if the application is being torn down.
        """

    def __bool__(self) -> bool: ...

class ContentDisposition(enum.Enum):
    Attachment = 1

    Inline = 2

class WResource(WObject):
    def suggest_file_name(self, name: str) -> None:
        """
        Set the suggested filename the browser uses when saving the resource (e.g. 'export.csv').
        """

    def set_disposition_type(self, disposition: ContentDisposition) -> None: ...

    def set_changed(self) -> None:
        """
        Invalidate any browser-side cache of this resource so the next fetch sees the latest data. Call after set_data() etc.
        """

    @property
    def internal_path(self) -> str: ...

    @internal_path.setter
    def internal_path(self, arg: str, /) -> None: ...

    def set_invalid_after_changed(self, enabled: bool) -> None: ...

    def set_takes_update_lock(self, enabled: bool) -> None:
        """
        When true, handle_request() acquires the session update lock before serving — required if your subclass touches widget state. Default is false (lock-free serving, faster).
        """

    def generate_url(self) -> str:
        """Return a URL at which this resource can be fetched."""

class WStreamResource(WResource):
    @property
    def mime_type(self) -> str: ...

    @mime_type.setter
    def mime_type(self, arg: str, /) -> None: ...

    def set_buffer_size(self, size: int) -> None: ...

class WMemoryResource(WResource):
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, mime_type: str) -> None: ...

    @overload
    def __init__(self, mime_type: str, data: bytes) -> None: ...

    @property
    def data(self) -> bytes: ...

    @data.setter
    def data(self, arg: bytes, /) -> None: ...

    @property
    def mime_type(self) -> str: ...

    @mime_type.setter
    def mime_type(self, arg: str, /) -> None: ...

class WFileResource(WStreamResource):
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, file_name: str) -> None: ...

    @overload
    def __init__(self, mime_type: str, file_name: str) -> None: ...

    @property
    def file_name(self) -> str: ...

    @file_name.setter
    def file_name(self, arg: str, /) -> None: ...

class WLink:
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, url: str) -> None: ...

    @overload
    def __init__(self, resource: WResource) -> None: ...

    @property
    def url(self) -> str: ...

    @url.setter
    def url(self, arg: str, /) -> None: ...

class WContainerWidget(WInteractWidget):
    def __init__(self) -> None: ...

    @overload
    def add_widget(self, text: str) -> WText: ...

    @overload
    def add_widget(self, widget: _T_Widget) -> _T_Widget: ...

    @overload
    def add_widgets(self, texts: Sequence[str]) -> list[WText]: ...

    @overload
    def add_widgets(self, widgets: list[_T_Widget]) -> list[_T_Widget]: ...

    def clear(self) -> None: ...

    @property
    def count(self) -> int: ...

    def widget(self, index: int) -> WWidget: ...

    def remove_widget(self, widget: WWidget) -> WWidget: ...

    def set_layout(self, layout: WLayout) -> None: ...

class WText(WInteractWidget):
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, text: str) -> None: ...

    @property
    def text(self) -> str: ...

    @text.setter
    def text(self, arg: str, /) -> None: ...

class WPushButton(WFormWidget):
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, text: str) -> None: ...

    @property
    def text(self) -> str: ...

    @text.setter
    def text(self, arg: str, /) -> None: ...

    @property
    def link(self) -> WLink: ...

    @link.setter
    def link(self, arg: WLink, /) -> None: ...

class WLineEdit(WFormWidget):
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, text: str) -> None: ...

    @property
    def text(self) -> str: ...

    @text.setter
    def text(self, arg: str, /) -> None: ...

    @property
    def placeholder(self) -> str: ...

    @placeholder.setter
    def placeholder(self, arg: str, /) -> None: ...

    @property
    def max_length(self) -> int: ...

    @max_length.setter
    def max_length(self, arg: int, /) -> None: ...

    @property
    def text_input(self) -> EventSignal: ...

class WCheckBox(WFormWidget):
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, text: str) -> None: ...

    @property
    def checked(self) -> bool: ...

    @checked.setter
    def checked(self, arg: bool, /) -> None: ...

    @property
    def on_check(self) -> EventSignal: ...

    @property
    def on_uncheck(self) -> EventSignal: ...

class WAnchor(WContainerWidget):
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, link: WLink) -> None: ...

    @overload
    def __init__(self, link: WLink, text: str) -> None: ...

    @property
    def link(self) -> WLink: ...

    @link.setter
    def link(self, arg: WLink, /) -> None: ...

class WImage(WInteractWidget):
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, link: WLink) -> None: ...

    @overload
    def __init__(self, link: WLink, alt_text: str) -> None: ...

    @property
    def image_link(self) -> WLink: ...

    @image_link.setter
    def image_link(self, arg: WLink, /) -> None: ...

    @property
    def alt_text(self) -> str: ...

    @alt_text.setter
    def alt_text(self, arg: str, /) -> None: ...

class Orientation(enum.IntEnum):
    Horizontal = 1

    Vertical = 2

class SelectionMode(enum.Enum):
    Single = 1

    Extended = 3

class WLabel(WInteractWidget):
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, text: str) -> None: ...

    @property
    def text(self) -> str: ...

    @text.setter
    def text(self, arg: str, /) -> None: ...

    def set_buddy(self, buddy: WFormWidget) -> None: ...

    @property
    def word_wrap(self) -> bool: ...

    @word_wrap.setter
    def word_wrap(self, arg: bool, /) -> None: ...

    def set_image(self, image: WImage) -> None: ...

class WBreak(WWidget):
    def __init__(self) -> None: ...

class WTextArea(WFormWidget):
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, text: str) -> None: ...

    @property
    def text(self) -> str: ...

    @text.setter
    def text(self, arg: str, /) -> None: ...

    @property
    def rows(self) -> int: ...

    @rows.setter
    def rows(self, arg: int, /) -> None: ...

    @property
    def columns(self) -> int: ...

    @columns.setter
    def columns(self, arg: int, /) -> None: ...

    @property
    def placeholder(self) -> str: ...

    @placeholder.setter
    def placeholder(self, arg: str, /) -> None: ...

    @property
    def selection_start(self) -> int: ...

    @property
    def has_selected_text(self) -> bool: ...

    @property
    def cursor_position(self) -> int: ...

class WSpinBox(WLineEdit):
    def __init__(self) -> None: ...

    @property
    def value(self) -> int: ...

    @value.setter
    def value(self, arg: int, /) -> None: ...

    @property
    def minimum(self) -> int: ...

    @minimum.setter
    def minimum(self, arg: int, /) -> None: ...

    @property
    def maximum(self) -> int: ...

    @maximum.setter
    def maximum(self, arg: int, /) -> None: ...

    @property
    def single_step(self) -> int: ...

    @single_step.setter
    def single_step(self, arg: int, /) -> None: ...

    def set_range(self, minimum: int, maximum: int) -> None: ...

    @property
    def wrap_around(self) -> bool: ...

    @wrap_around.setter
    def wrap_around(self, arg: bool, /) -> None: ...

    @property
    def value_changed(self) -> IntSignal: ...

class WDoubleSpinBox(WLineEdit):
    def __init__(self) -> None: ...

    @property
    def value(self) -> float: ...

    @value.setter
    def value(self, arg: float, /) -> None: ...

    @property
    def minimum(self) -> float: ...

    @minimum.setter
    def minimum(self, arg: float, /) -> None: ...

    @property
    def maximum(self) -> float: ...

    @maximum.setter
    def maximum(self, arg: float, /) -> None: ...

    @property
    def single_step(self) -> float: ...

    @single_step.setter
    def single_step(self, arg: float, /) -> None: ...

    @property
    def decimals(self) -> int: ...

    @decimals.setter
    def decimals(self, arg: int, /) -> None: ...

    def set_range(self, minimum: float, maximum: float) -> None: ...

    @property
    def value_changed(self) -> DoubleSignal: ...

class WSlider(WFormWidget):
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, orientation: Orientation) -> None: ...

    @property
    def value(self) -> int: ...

    @value.setter
    def value(self, arg: int, /) -> None: ...

    @property
    def minimum(self) -> int: ...

    @minimum.setter
    def minimum(self, arg: int, /) -> None: ...

    @property
    def maximum(self) -> int: ...

    @maximum.setter
    def maximum(self, arg: int, /) -> None: ...

    @property
    def step(self) -> int: ...

    @step.setter
    def step(self, arg: int, /) -> None: ...

    @property
    def tick_interval(self) -> int: ...

    @tick_interval.setter
    def tick_interval(self, arg: int, /) -> None: ...

    def set_range(self, minimum: int, maximum: int) -> None: ...

    def set_orientation(self, orientation: Orientation) -> None: ...

    @property
    def value_changed(self) -> IntSignal: ...

class WComboBox(WFormWidget):
    def __init__(self) -> None: ...

    def add_item(self, text: str) -> None: ...

    def add_items(self, items: Sequence[str]) -> None: ...

    def insert_item(self, index: int, text: str) -> None: ...

    def remove_item(self, index: int) -> None: ...

    @property
    def count(self) -> int: ...

    def item_text(self, index: int) -> str: ...

    def set_item_text(self, index: int, text: str) -> None: ...

    @property
    def current_index(self) -> int: ...

    @current_index.setter
    def current_index(self, arg: int, /) -> None: ...

    def clear(self) -> None: ...

    @property
    def activated(self) -> IntSignal: ...

    @property
    def string_activated(self) -> StringSignal: ...

class WSelectionBox(WComboBox):
    def __init__(self) -> None: ...

    @property
    def vertical_size(self) -> int: ...

    @vertical_size.setter
    def vertical_size(self, arg: int, /) -> None: ...

    def set_selection_mode(self, mode: SelectionMode) -> None: ...

    def set_selected_indexes(self, selection: "std::set<int, std::less<int>, std::allocator<int> >") -> None: ...

    def clear_selection(self) -> None: ...

class WRadioButton(WFormWidget):
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, text: str) -> None: ...

    @property
    def checked(self) -> bool: ...

    @checked.setter
    def checked(self, arg: bool, /) -> None: ...

    @property
    def on_check(self) -> EventSignal: ...

    @property
    def on_uncheck(self) -> EventSignal: ...

class WButtonGroup(WObject):
    def __init__(self) -> None: ...

    def add_button(self, button: WRadioButton, id: int = -1) -> None: ...

    def remove_button(self, button: WRadioButton) -> None: ...

    @property
    def count(self) -> int: ...

    @property
    def checked_id(self) -> int: ...

    @property
    def selected_button_index(self) -> int: ...

    @selected_button_index.setter
    def selected_button_index(self, arg: int, /) -> None: ...

class WProgressBar(WInteractWidget):
    def __init__(self) -> None: ...

    @property
    def value(self) -> float: ...

    @value.setter
    def value(self, arg: float, /) -> None: ...

    @property
    def minimum(self) -> float: ...

    @minimum.setter
    def minimum(self, arg: float, /) -> None: ...

    @property
    def maximum(self) -> float: ...

    @maximum.setter
    def maximum(self, arg: float, /) -> None: ...

    def set_range(self, minimum: float, maximum: float) -> None: ...

    def set_format(self, format: str) -> None: ...

    @property
    def value_changed(self) -> DoubleSignal: ...

class DateSignal:
    def __init__(self) -> None: ...

    def connect(self, callable: Callable) -> Connection: ...

    def emit(self, arg: datetime.date | None, /) -> None: ...

    def disconnect_all_slots(self) -> None: ...

class WDateEdit(WLineEdit):
    def __init__(self) -> None: ...

    @property
    def date(self) -> datetime.date | None: ...

    @date.setter
    def date(self, arg: datetime.date | None, /) -> None: ...

    @property
    def bottom(self) -> datetime.date | None: ...

    @bottom.setter
    def bottom(self, arg: datetime.date | None, /) -> None: ...

    @property
    def top(self) -> datetime.date | None: ...

    @top.setter
    def top(self, arg: datetime.date | None, /) -> None: ...

    def set_format(self, format: str) -> None: ...

    def format(self) -> str: ...

class WTimeEdit(WLineEdit):
    def __init__(self) -> None: ...

    @property
    def time(self) -> datetime.time | None: ...

    @time.setter
    def time(self, arg: datetime.time | None, /) -> None: ...

    @property
    def bottom(self) -> datetime.time | None: ...

    @bottom.setter
    def bottom(self, arg: datetime.time | None, /) -> None: ...

    @property
    def top(self) -> datetime.time | None: ...

    @top.setter
    def top(self, arg: datetime.time | None, /) -> None: ...

    def set_format(self, format: str) -> None: ...

class WCalendar(WWidget):
    def __init__(self) -> None: ...

    def select(self, date: datetime.date | None) -> None: ...

    def set_selection_mode(self, mode: SelectionMode) -> None: ...

    def browse_to_previous_month(self) -> None: ...

    def browse_to_next_month(self) -> None: ...

    def browse_to_previous_year(self) -> None: ...

    def browse_to_next_year(self) -> None: ...

    @property
    def current_month(self) -> int: ...

    @property
    def current_year(self) -> int: ...

    @property
    def bottom(self) -> datetime.date | None: ...

    @bottom.setter
    def bottom(self, arg: datetime.date | None, /) -> None: ...

    @property
    def top(self) -> datetime.date | None: ...

    @top.setter
    def top(self, arg: datetime.date | None, /) -> None: ...

    @property
    def selection_changed(self) -> Signal: ...

    @property
    def activated(self) -> DateSignal: ...

    @property
    def clicked(self) -> DateSignal: ...

class WDateValidator(WValidator):
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, bottom: datetime.date | None, top: datetime.date | None) -> None: ...

    @overload
    def __init__(self, format: str) -> None: ...

    @property
    def bottom(self) -> datetime.date | None: ...

    @bottom.setter
    def bottom(self, arg: datetime.date | None, /) -> None: ...

    @property
    def top(self) -> datetime.date | None: ...

    @top.setter
    def top(self, arg: datetime.date | None, /) -> None: ...

    def set_format(self, format: str) -> None: ...

    def format(self) -> str: ...

class WTimeValidator(WRegExpValidator):
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, format: str) -> None: ...

    @overload
    def __init__(self, format: str, bottom: datetime.time | None, top: datetime.time | None) -> None: ...

    @property
    def bottom(self) -> datetime.time | None: ...

    @bottom.setter
    def bottom(self, arg: datetime.time | None, /) -> None: ...

    @property
    def top(self) -> datetime.time | None: ...

    @top.setter
    def top(self, arg: datetime.time | None, /) -> None: ...

    def set_format(self, format: str) -> None: ...

    def format(self) -> str: ...

class TextFormat(enum.Enum):
    XHTML = 0

    UnsafeXHTML = 1

    Plain = 2

class TemplateWidgetIdMode(enum.Enum):
    SetObjectName = 1

    SetId = 2

class WTemplate(WInteractWidget):
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, text: str) -> None: ...

    @property
    def template_text(self) -> str: ...

    @template_text.setter
    def template_text(self, arg: str, /) -> None: ...

    def set_template_text(self, text: str, format: TextFormat = TextFormat.XHTML) -> None: ...

    def bind_widget(self, var_name: str, widget: _T_Widget) -> _T_Widget: ...

    def bind_string(self, var_name: str, value: str, format: TextFormat = TextFormat.XHTML) -> None: ...

    def bind_int(self, var_name: str, value: int) -> None: ...

    def bind_empty(self, var_name: str) -> None: ...

    def resolve_widget(self, var_name: str) -> WWidget: ...

    @property
    def widget_id_mode(self) -> TemplateWidgetIdMode: ...

    @widget_id_mode.setter
    def widget_id_mode(self, arg: TemplateWidgetIdMode, /) -> None: ...

    def clear(self) -> None: ...

    def refresh(self) -> None: ...

    def set_condition(self, name: str, value: bool) -> None: ...

    def condition_value(self, name: str) -> bool: ...

class DialogCode(enum.Enum):
    Rejected = 0

    Accepted = 1

class StandardButton(enum.IntEnum):
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
    def connect(self, callable: Callable) -> Connection: ...

    def disconnect_all_slots(self) -> None: ...

class StandardButtonSignal:
    def connect(self, callable: Callable) -> Connection: ...

    def disconnect_all_slots(self) -> None: ...

class WStackedWidget(WContainerWidget):
    def __init__(self) -> None: ...

    @property
    def current_index(self) -> int: ...

    @current_index.setter
    def current_index(self, arg: int, /) -> None: ...

    def set_current_widget(self, widget: WWidget) -> None: ...

class WMenuItem(WContainerWidget):
    @overload
    def __init__(self, label: str) -> None: ...

    @overload
    def __init__(self, label: str, contents: WWidget) -> None: ...

    @property
    def text(self) -> str: ...

    @text.setter
    def text(self, arg: str, /) -> None: ...

    def set_link(self, link: WLink) -> None: ...

    @property
    def checkable(self) -> bool: ...

    @checkable.setter
    def checkable(self, arg: bool, /) -> None: ...

    @property
    def checked(self) -> bool: ...

    @checked.setter
    def checked(self, arg: bool, /) -> None: ...

    def select(self) -> None: ...

    def set_selectable(self, selectable: bool) -> None: ...

    def set_closeable(self, closeable: bool) -> None: ...

class MenuItemSignal:
    def connect(self, callable: Callable) -> Connection: ...

    def disconnect_all_slots(self) -> None: ...

class WMenu(WWidget):
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, contents_stack: WStackedWidget) -> None: ...

    @overload
    def add_item(self, label: str) -> WMenuItem: ...

    @overload
    def add_item(self, item: _T_MenuItem) -> _T_MenuItem: ...

    @overload
    def add_items(self, items: list[_T_MenuItem]) -> list[_T_MenuItem]: ...

    @overload
    def add_items(self, labels: Sequence[str]) -> None: ...

    def select(self, index: int) -> None: ...

    def current_item(self) -> WMenuItem: ...

    @property
    def item_selected(self) -> MenuItemSignal: ...

class WTabWidget(WWidget):
    def __init__(self) -> None: ...

    def add_tab(self, child: object, label: str) -> WMenuItem: ...

    @property
    def count(self) -> int: ...

    def index_of(self, widget: WWidget) -> int: ...

    @property
    def current_index(self) -> int: ...

    @current_index.setter
    def current_index(self, arg: int, /) -> None: ...

    def set_tab_enabled(self, index: int, enable: bool) -> None: ...

    def set_tab_hidden(self, index: int, hidden: bool) -> None: ...

    def set_tab_closeable(self, index: int, closeable: bool) -> None: ...

    def set_tab_text(self, index: int, label: str) -> None: ...

    def tab_text(self, index: int) -> str: ...

    @property
    def current_changed(self) -> IntSignal: ...

class WPanel(WWidget):
    def __init__(self) -> None: ...

    @property
    def title(self) -> str: ...

    @title.setter
    def title(self, arg: str, /) -> None: ...

    def set_title_bar(self, enable: bool) -> None: ...

    @property
    def title_bar(self) -> bool: ...

    @property
    def collapsible(self) -> bool: ...

    @collapsible.setter
    def collapsible(self, arg: bool, /) -> None: ...

    @property
    def collapsed(self) -> bool: ...

    @collapsed.setter
    def collapsed(self, arg: bool, /) -> None: ...

    def collapse(self) -> None: ...

    def expand(self) -> None: ...

    def set_central_widget(self, widget: WWidget) -> None: ...

class WGroupBox(WContainerWidget):
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, title: str) -> None: ...

    @property
    def title(self) -> str: ...

    @title.setter
    def title(self, arg: str, /) -> None: ...

class WDialog(WWidget):
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, window_title: str) -> None: ...

    @property
    def window_title(self) -> str: ...

    @window_title.setter
    def window_title(self, arg: str, /) -> None: ...

    @property
    def modal(self) -> bool: ...

    @modal.setter
    def modal(self, arg: bool, /) -> None: ...

    @property
    def closable(self) -> bool: ...

    @closable.setter
    def closable(self, arg: bool, /) -> None: ...

    def set_resizable(self, resizable: bool) -> None: ...

    def show(self) -> None: ...

    def accept(self) -> None: ...

    def reject(self) -> None: ...

    def done(self, result: DialogCode) -> None: ...

    def reject_when_escape_pressed(self, enable: bool = True) -> None: ...

    @property
    def contents(self) -> WContainerWidget: ...

    @property
    def title_bar_widget(self) -> WContainerWidget: ...

    @property
    def footer(self) -> WContainerWidget: ...

    @property
    def result(self) -> DialogCode: ...

    @property
    def finished(self) -> DialogCodeSignal: ...

class WMessageBox(WDialog):
    def __init__(self) -> None: ...

    @property
    def text(self) -> str: ...

    @text.setter
    def text(self, arg: str, /) -> None: ...

    def set_standard_buttons(self, buttons: int) -> None: ...

    @property
    def button_result(self) -> StandardButton: ...

    @property
    def button_clicked(self) -> StandardButtonSignal: ...

class WTableCell(WContainerWidget):
    @property
    def row(self) -> int: ...

    @property
    def column(self) -> int: ...

    @property
    def row_span(self) -> int: ...

    @row_span.setter
    def row_span(self, arg: int, /) -> None: ...

    @property
    def column_span(self) -> int: ...

    @column_span.setter
    def column_span(self, arg: int, /) -> None: ...

class WTableRow:
    @property
    def row_num(self) -> int: ...

    def element_at(self, column: int) -> WTableCell: ...

class WTableColumn:
    @property
    def column_num(self) -> int: ...

class WTable(WInteractWidget):
    def __init__(self) -> None: ...

    def element_at(self, row: int, column: int) -> WTableCell: ...

    @property
    def row_count(self) -> int: ...

    @property
    def column_count(self) -> int: ...

    def clear(self) -> None: ...

    def remove_row(self, row: int) -> WTableRow: ...

    def remove_column(self, column: int) -> WTableColumn: ...

    def insert_row(self, row: int) -> WTableRow: ...

    def insert_column(self, column: int) -> WTableColumn: ...

class WLayout:
    pass

class LayoutDirection(enum.Enum):
    LeftToRight = 0

    RightToLeft = 1

    TopToBottom = 2

    BottomToTop = 3

class WBoxLayout(WLayout):
    def __init__(self, direction: LayoutDirection) -> None: ...

    def add_widget(self, widget: _T_Widget, stretch: int = 0) -> _T_Widget: ...

    def add_widgets(self, widgets: list[_T_Widget]) -> list[_T_Widget]: ...

    def add_stretch(self, stretch: int = 1) -> None: ...

    def add_spacing(self, size_px: float) -> None: ...

class WHBoxLayout(WBoxLayout):
    def __init__(self) -> None: ...

class WVBoxLayout(WBoxLayout):
    def __init__(self) -> None: ...

class WGridLayout(WLayout):
    def __init__(self) -> None: ...

    def add_widget(self, widget: _T_Widget, row: int, column: int, row_span: int = 1, column_span: int = 1) -> _T_Widget: ...

    def set_row_stretch(self, row: int, stretch: int) -> None: ...

    def set_column_stretch(self, column: int, stretch: int) -> None: ...

    @property
    def row_count(self) -> int: ...

    @property
    def column_count(self) -> int: ...

class EntryPointType(enum.Enum):
    Application = 0

    WidgetSet = 1

    StaticResource = 2

class WServer:
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, application_path: str) -> None: ...

    def set_server_configuration(self, argv: Sequence[str], wt_config: str = '') -> None: ...

    def add_entry_point(self, type: EntryPointType, factory: object, path: str = '/', favicon: str = '') -> None: ...

    def start(self) -> bool: ...

    def stop(self) -> None: ...

    def run(self) -> None: ...

    def is_running(self) -> bool: ...

    @staticmethod
    def wait_for_shutdown() -> int: ...

    def post(self, session_id: str, function: Callable[[], None], fallback: Callable[[], None] | None = None) -> None:
        """
        Schedule `function` to run within the session's event loop. Thread-safe. If the session is gone, `fallback` is called (if given). Returns immediately.
        """

    def post_all(self, function: Callable[[], None]) -> None:
        """
        Schedule `function` to run within every currently-active session. Thread-safe.
        """

class WTheme(WObject):
    def name(self) -> str:
        """Theme identifier — e.g. 'polished', 'bootstrap5'."""

    def resources_url(self) -> str:
        """URL prefix where the theme's CSS / asset files are served from."""

class WCssTheme(WTheme):
    def __init__(self, name: str) -> None:
        """
        Construct a plain-CSS theme — pass 'default' or 'polished' to use Wt's built-in styles, or any name that matches a CSS file you serve at <resources>/themes/<name>/wt.css.
        """

class WBootstrap5Theme(WTheme):
    def __init__(self) -> None:
        """
        Construct a Bootstrap 5 theme. Attach it to an application with `app.theme = wt.WBootstrap5Theme()`.
        """

class WBootstrap2Theme(WTheme):
    def __init__(self) -> None:
        """
        Bootstrap 2 theme. Useful for older apps; new code should prefer WBootstrap5Theme.
        """

class WBootstrap3Theme(WTheme):
    def __init__(self) -> None:
        """
        Bootstrap 3 theme. Useful for apps tracking the Bootstrap-3 ecosystem; new code should prefer WBootstrap5Theme.
        """

class WTimer(WObject):
    def __init__(self) -> None: ...

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
    def __init__(self) -> None: ...

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
    def __init__(self, role: int) -> None: ...

    @property
    def value(self) -> int: ...

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
    def __init__(self) -> None: ...

    @property
    def row(self) -> int: ...

    @property
    def column(self) -> int: ...

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
    def connect(self, callable: Callable) -> Connection: ...

    def disconnect_all_slots(self) -> None: ...

class WAbstractItemModel(WObject):
    def row_count(self, parent: WModelIndex = ...) -> int:
        """
        Number of rows under `parent` (top-level when parent is the default invalid index).
        """

    def column_count(self, parent: WModelIndex = ...) -> int: ...

    def has_children(self, index: WModelIndex) -> bool: ...

    def index(self, row: int, column: int, parent: WModelIndex = ...) -> WModelIndex: ...

    def parent_of(self, index: WModelIndex) -> WModelIndex: ...

    def display_data(self, index: WModelIndex) -> object: ...

    def set_header_data(self, section: int, value: object) -> bool:
        """
        Set a header label. Accepts str/int/float/bool — anything else is stringified via Python repr.
        """

class WAbstractListModel(WAbstractItemModel):
    pass

class WStringListModel(WAbstractListModel):
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, strings: Sequence[str]) -> None: ...

    def set_string_list(self, strings: Sequence[str]) -> None: ...

    def add_string(self, string: str) -> None: ...

    @property
    def string_list(self) -> list[str]: ...

class WStandardItem:
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, text: str) -> None: ...

    @property
    def text(self) -> str: ...

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
    def style_class(self) -> str: ...

    @style_class.setter
    def style_class(self, arg: str, /) -> None: ...

    @property
    def tool_tip(self) -> str: ...

    @tool_tip.setter
    def tool_tip(self, arg: str, /) -> None: ...

    def set_link(self, link: WLink) -> None: ...

    @property
    def checkable(self) -> bool: ...

    @checkable.setter
    def checkable(self, arg: bool, /) -> None: ...

    @property
    def checked(self) -> bool: ...

    @checked.setter
    def checked(self, arg: bool, /) -> None: ...

    @property
    def tristate(self) -> bool: ...

    @tristate.setter
    def tristate(self, arg: bool, /) -> None: ...

    @property
    def editable(self) -> bool: ...

    @editable.setter
    def editable(self, arg: bool, /) -> None: ...

    @property
    def has_children(self) -> bool: ...

    @property
    def row_count(self) -> int: ...

    @property
    def column_count(self) -> int: ...

    def set_row_count(self, rows: int) -> None: ...

    def set_column_count(self, columns: int) -> None: ...

    def append_row(self, items: list[WStandardItem]) -> None:
        """
        Append a single child row. Each item's Python wrapper stays usable after the call (re-armed as a non-owning alias).
        """

    def append_column(self, items: list[WStandardItem]) -> None: ...

    def insert_rows(self, row: int, count: int) -> None: ...

    def insert_columns(self, column: int, count: int) -> None: ...

    def child(self, row: int, column: int = 0) -> WStandardItem:
        """The child item at (row, column) — None if absent."""

    def parent(self) -> WStandardItem:
        """Parent item — None for items in invisibleRootItem()."""

class WStandardItemModel(WAbstractItemModel):
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, rows: int, columns: int) -> None: ...

    def clear(self) -> None:
        """Drop every item; rowCount and columnCount go to 0."""

    @property
    def invisible_root_item(self) -> WStandardItem:
        """
        The internal root item. Manipulate it directly for advanced tree construction; for flat tables prefer model.append_row.
        """

    def index_from_item(self, item: WStandardItem) -> WModelIndex: ...

    def item_from_index(self, index: WModelIndex) -> WStandardItem: ...

    def item(self, row: int, column: int = 0) -> WStandardItem:
        """Top-level item at (row, column)."""

    def set_item(self, row: int, column: int, item: WStandardItem) -> None:
        """
        Place an item at (row, column). Transfers ownership; the Python wrapper is re-armed as a non-owning alias.
        """

    def append_row(self, items: list[WStandardItem]) -> None: ...

    def append_column(self, items: list[WStandardItem]) -> None: ...

class SelectionBehavior(enum.Enum):
    SelectItems = 0

    SelectRows = 1

class SortOrder(enum.Enum):
    Ascending = 0

    Descending = 1

class ScrollHint(enum.Enum):
    EnsureVisible = 0

    PositionAtTop = 1

    PositionAtBottom = 2

    PositionAtCenter = 3

    PositionAtLeft = 4

    PositionAtRight = 5

    NoScroll = 6

class WAbstractItemView(WWidget):
    @property
    def model(self) -> WAbstractItemModel: ...

    @model.setter
    def model(self, arg: WAbstractItemModel, /) -> None: ...

    def set_root_index(self, root_index: WModelIndex) -> None: ...

    @property
    def root_index(self) -> WModelIndex: ...

    def clear_selection(self) -> None: ...

    def is_selected(self, index: WModelIndex) -> bool: ...

    def sort_by_column(self, column: int, order: SortOrder) -> None: ...

    @property
    def clicked(self) -> ModelIndexMouseSignal: ...

    @property
    def double_clicked(self) -> ModelIndexMouseSignal: ...

    @property
    def selection_changed(self) -> Signal: ...

    def set_column_width(self, column: int, width: WLength) -> None: ...

    @property
    def sorting_enabled(self) -> bool: ...

    @sorting_enabled.setter
    def sorting_enabled(self, arg: bool, /) -> None: ...

    @property
    def column_resize_enabled(self) -> bool: ...

    @column_resize_enabled.setter
    def column_resize_enabled(self, arg: bool, /) -> None: ...

    @property
    def selection_behavior(self) -> SelectionBehavior: ...

    @selection_behavior.setter
    def selection_behavior(self, arg: SelectionBehavior, /) -> None: ...

    @property
    def selection_mode(self) -> SelectionMode: ...

    @selection_mode.setter
    def selection_mode(self, arg: SelectionMode, /) -> None: ...

class WTableView(WAbstractItemView):
    def __init__(self) -> None: ...

    def scroll_to(self, index: WModelIndex, hint: ScrollHint = ScrollHint.EnsureVisible) -> None: ...

class WTreeView(WAbstractItemView):
    def __init__(self) -> None: ...

    def set_expanded(self, index: WModelIndex, expanded: bool) -> None: ...

    def is_expanded(self, index: WModelIndex) -> bool: ...

    def expand(self, index: WModelIndex) -> None: ...

    def collapse(self, index: WModelIndex) -> None: ...

    def collapse_all(self) -> None: ...

    def expand_to_depth(self, depth: int) -> None: ...

    @property
    def root_is_decorated(self) -> bool: ...

    @root_is_decorated.setter
    def root_is_decorated(self, arg: bool, /) -> None: ...

class WAbstractProxyModel(WAbstractItemModel):
    @property
    def source_model(self) -> WAbstractItemModel:
        """
        The wrapped model. Setting it disconnects from the previous source and rewires the proxy.
        """

    @source_model.setter
    def source_model(self, arg: WAbstractItemModel, /) -> None: ...

    def map_from_source(self, source_index: WModelIndex) -> WModelIndex:
        """
        Translate a source-model index to the proxy's coordinate system (sorted/filtered/etc. position).
        """

    def map_to_source(self, proxy_index: WModelIndex) -> WModelIndex:
        """
        Translate a proxy index back to the source model. Required when handing a clicked index back to source-specific logic.
        """

class WIdentityProxyModel(WAbstractProxyModel):
    def __init__(self) -> None: ...

class WReadOnlyProxyModel(WAbstractProxyModel):
    def __init__(self) -> None: ...

class WSortFilterProxyModel(WAbstractProxyModel):
    def __init__(self) -> None: ...

    @property
    def filter_key_column(self) -> int:
        """
        Column index in the source model whose values are matched against the filter regex. Default 0.
        """

    @filter_key_column.setter
    def filter_key_column(self, arg: int, /) -> None: ...

    def set_filter_regexp(self, pattern: str) -> None:
        """
        Set the regex pattern applied to the filter column. Empty string disables filtering. Wt uses std::regex_match (FULL-STRING match, not substring search), ECMAScript flavour — to search for a substring, wrap with wildcards: `.*foo.*`. Re-runs the filter immediately when `dynamic_sort_filter` is True; otherwise call `invalidate()` afterward.
        """

    @property
    def filter_role(self) -> ItemDataRole:
        """
        Data role read from the filter column before matching against the regex. Default Display.
        """

    @filter_role.setter
    def filter_role(self, arg: ItemDataRole, /) -> None: ...

    @property
    def sort_role(self) -> ItemDataRole:
        """Data role read when comparing rows during sort. Default Display."""

    @sort_role.setter
    def sort_role(self, arg: ItemDataRole, /) -> None: ...

    @property
    def sort_column(self) -> int:
        """Current sort column, or -1 when sort() has not been called."""

    @property
    def sort_order(self) -> SortOrder: ...

    @property
    def dynamic_sort_filter(self) -> bool:
        """
        When True, the proxy re-runs filter + sort whenever the source model changes. False (default) requires an explicit invalidate() call after modifications.
        """

    @dynamic_sort_filter.setter
    def dynamic_sort_filter(self, arg: bool, /) -> None: ...

    def invalidate(self) -> None:
        """
        Force a re-evaluation of filter + sort against the current source data. Needed after source mutations when dynamic_sort_filter is False.
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
    @overload
    def __init__(self) -> None:
        """Default-construct as 'auto' (no explicit length)."""

    @overload
    def __init__(self, value: float, unit: LengthUnit = LengthUnit.Pixel) -> None: ...

    @overload
    def __init__(self, css_text: str) -> None:
        """Parse a CSS length string — e.g. 'auto', '50%', '12px', '1em'."""

    @property
    def is_auto(self) -> bool: ...

    @property
    def value(self) -> float: ...

    @property
    def unit(self) -> LengthUnit: ...

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
    def timing_function(self) -> TimingFunction: ...

    @timing_function.setter
    def timing_function(self, arg: TimingFunction, /) -> None: ...

    @property
    def empty(self) -> bool:
        """True for the default (no-effect) animation."""

class Touch:
    def document(self) -> Coordinates:
        """Touch position relative to the document, as Coordinates."""

    def window(self) -> Coordinates:
        """Touch position relative to the visible window."""

    def screen(self) -> Coordinates:
        """Touch position relative to the physical screen."""

    def widget(self) -> Coordinates:
        """Touch position relative to the target widget."""

class WTouchEvent:
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
    @property
    def scale(self) -> float: ...

    @property
    def rotation(self) -> float: ...

class WScrollEvent:
    @property
    def scroll_x(self) -> int: ...

    @property
    def scroll_y(self) -> int: ...

    @property
    def viewport_width(self) -> int: ...

    @property
    def viewport_height(self) -> int: ...

class DropEventOriginalEventType(enum.Enum):
    Mouse = 0

    Touch = 1

class WDropEvent:
    @property
    def source(self) -> WObject:
        """
        The WObject that was the drag source. Don't outlive the slot call — the pointer's lifetime is the source widget's.
        """

    @property
    def mime_type(self) -> str: ...

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
    def connect(self, callable: Callable) -> Connection: ...

    def disconnect_all_slots(self) -> None: ...

class WIcon(WInteractWidget):
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, name: str) -> None:
        """Construct with a Font Awesome icon name (e.g. 'play', 'gear')."""

    @property
    def name(self) -> str: ...

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
    URI = 0

    IconName = 1

class WIconPair(WWidget):
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

    def show_icon2(self) -> None: ...

    def set_icon1_type(self, type: IconType) -> None: ...

    def set_icon2_type(self, type: IconType) -> None: ...

    def set_icons_type(self, type: IconType) -> None:
        """Shortcut for setting both icons to the same IconType."""

    @property
    def icon1_clicked(self) -> MouseEventSignal:
        """MouseEventSignal — clicks while icon1 is visible."""

    @property
    def icon2_clicked(self) -> MouseEventSignal: ...

class WPopupWidget(WWidget):
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
    def set_message(self, text: str) -> None:
        """Replace the loading message shown to the user."""

class WDefaultLoadingIndicator(WLoadingIndicator):
    def __init__(self) -> None:
        """Wt's plain-text loading indicator: a small fixed-position text label."""

class WOverlayLoadingIndicator(WLoadingIndicator):
    def __init__(self) -> None:
        """
        A more visible loading indicator — dims the page contents with a translucent overlay during requests.
        """

class NotificationPermission(enum.Enum):
    Default = 0

    Granted = 1

    Denied = 2

class WNotification(WObject):
    def __init__(self, title: str = '', body: str = '') -> None: ...

    def set_title(self, title: str) -> None: ...

    def set_body(self, body: str) -> None: ...

    def set_icon(self, icon_link: WLink) -> None: ...

    def set_badge(self, badge_link: WLink) -> None: ...

    @property
    def silent(self) -> bool: ...

    @silent.setter
    def silent(self, arg: bool, /) -> None: ...

    @property
    def require_interaction(self) -> bool: ...

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
    def closed(self) -> JSignal0: ...

    @property
    def shown(self) -> JSignal0: ...

    @property
    def error(self) -> JSignal0:
        """
        JSignal0 — fires when the OS rejects the show request (e.g. permission denied at run time).
        """

class LayoutPosition(enum.Enum):
    North = 0

    East = 1

    South = 2

    West = 3

    Center = 4

class WBorderLayout(WLayout):
    def __init__(self) -> None: ...

    def add_widget(self, widget: _T_Widget, position: LayoutPosition) -> _T_Widget: ...

class WFitLayout(WLayout):
    def __init__(self) -> None: ...

    def add_widget(self, widget: _T_Widget) -> _T_Widget:
        """
        Set the single fitted child. Replacing it requires calling the inherited removeWidget on the previous one first.
        """

class JDoubleSignal:
    def connect(self, callable: Callable) -> Connection: ...

    def disconnect_all_slots(self) -> None: ...

class PlayerOption(enum.IntEnum):
    Autoplay = 1

    Loop = 2

    Controls = 4

class MediaPreloadMode(enum.Enum):
    Auto = 1

    Metadata = 2

class WAbstractMedia(WInteractWidget):
    def add_source(self, source: WLink, mime_type: str = '', media: str = '') -> None:
        """
        Add a source URL (via WLink). `mime_type` is the content-type hint the browser uses to pick a source; `media` is a CSS media query (e.g. 'screen and (min-width: 600px)').
        """

    def clear_sources(self) -> None: ...

    def set_alternative_content(self, widget: WWidget) -> None:
        """
        Widget shown to users whose browser can't play any of the configured sources. Ownership transfers; the wrapper is re-armed as a non-owning alias.
        """

    def set_options(self, options: int) -> None:
        """Bitwise-OR of PlayerOption values (Autoplay | Loop | Controls)."""

    def set_preload_mode(self, mode: MediaPreloadMode) -> None: ...

    def play(self) -> None:
        """Start playback. No-op if already playing."""

    def pause(self) -> None: ...

    @property
    def playing(self) -> bool:
        """True iff the media element is currently playing."""

    @property
    def playback_started(self) -> EventSignal:
        """EventSignal[] — fires when playback begins."""

    @property
    def playback_paused(self) -> EventSignal: ...

    @property
    def ended(self) -> EventSignal: ...

    @property
    def time_updated(self) -> EventSignal:
        """
        EventSignal[] — fires periodically (~4×/sec by browser convention) during playback.
        """

    @property
    def volume_changed(self) -> EventSignal: ...

class WAudio(WAbstractMedia):
    def __init__(self) -> None: ...

class WVideo(WAbstractMedia):
    def __init__(self) -> None: ...

    def set_poster(self, url: str) -> None:
        """
        URL of a thumbnail shown before playback starts (HTML `poster` attribute).
        """

class MediaEncoding(enum.Enum):
    PosterImage = 0

    MP3 = 1

    M4A = 2

    OGA = 3

    WAV = 4

    WEBMA = 5

    FLA = 6

    M4V = 7

    OGV = 8

    WEBMV = 9

    FLV = 10

class MediaType(enum.Enum):
    Audio = 0

    Video = 1

class MediaPlayerButtonId(enum.Enum):
    VideoPlay = 0

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
    Time = 0

    Volume = 1

class MediaPlayerTextId(enum.Enum):
    CurrentTime = 0

    Duration = 1

    Title = 2

class WMediaPlayer(WWidget):
    def __init__(self, media_type: MediaType) -> None:
        """Construct an audio or video player."""

    def add_source(self, encoding: MediaEncoding, link: WLink) -> None:
        """
        Register a source URL for a given encoding. Add the same content under multiple encodings for cross-browser support.
        """

    def get_source(self, encoding: MediaEncoding) -> WLink: ...

    def clear_sources(self) -> None: ...

    def set_title(self, title: str) -> None: ...

    def set_video_size(self, width: int, height: int) -> None: ...

    @property
    def video_width(self) -> int: ...

    @property
    def video_height(self) -> int: ...

    def play(self) -> None: ...

    def pause(self) -> None: ...

    def stop(self) -> None: ...

    def seek(self, time: float) -> None:
        """Jump to `time` seconds into the media."""

    def set_playback_rate(self, rate: float) -> None:
        """1.0 = normal; 2.0 = 2× speed; 0.5 = half-speed."""

    def set_volume(self, volume: float) -> None:
        """0.0 (silent) to 1.0 (max)."""

    def mute(self, mute: bool) -> None: ...

    def set_button(self, id: MediaPlayerButtonId, button: WInteractWidget) -> None:
        """
        Override the widget used for a control. The button is associated (not owned); place it in the page yourself.
        """

    def set_progress_bar(self, id: MediaPlayerProgressBarId, progress_bar: WProgressBar) -> None: ...

    def set_text(self, id: MediaPlayerTextId, text: WText) -> None: ...

    @property
    def playback_started(self) -> JSignal0:
        """JSignal0 — fires when playback starts."""

    @property
    def playback_paused(self) -> JSignal0: ...

    @property
    def ended(self) -> JSignal0: ...

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
    def __init__(self) -> None: ...

    def add_source(self, encoding: MediaEncoding, link: WLink) -> None: ...

    def get_source(self, encoding: MediaEncoding) -> WLink: ...

    @property
    def loops(self) -> int:
        """Number of times to repeat the clip. 0 = infinite."""

    @loops.setter
    def loops(self, arg: int, /) -> None: ...

    def play(self) -> None: ...

    def stop(self) -> None: ...

class WPointF:
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, x: float, y: float) -> None: ...

    @property
    def x(self) -> float: ...

    @x.setter
    def x(self, arg: float, /) -> None: ...

    @property
    def y(self) -> float: ...

    @y.setter
    def y(self, arg: float, /) -> None: ...

    def __repr__(self) -> str: ...

class WRectF:
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, x: float, y: float, width: float, height: float) -> None: ...

    @property
    def x(self) -> float: ...

    @x.setter
    def x(self, arg: float, /) -> None: ...

    @property
    def y(self) -> float: ...

    @y.setter
    def y(self, arg: float, /) -> None: ...

    @property
    def width(self) -> float: ...

    @width.setter
    def width(self, arg: float, /) -> None: ...

    @property
    def height(self) -> float: ...

    @height.setter
    def height(self, arg: float, /) -> None: ...

    @property
    def is_null(self) -> bool: ...

    @property
    def is_empty(self) -> bool: ...

    @property
    def left(self) -> float: ...

    @property
    def top(self) -> float: ...

    def __repr__(self) -> str: ...

class WLineF:
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, x1: float, y1: float, x2: float, y2: float) -> None: ...

    @property
    def x1(self) -> float: ...

    @property
    def y1(self) -> float: ...

    @property
    def x2(self) -> float: ...

    @property
    def y2(self) -> float: ...

    @property
    def p1(self) -> WPointF: ...

    @property
    def p2(self) -> WPointF: ...

class WTransform:
    def __init__(self) -> None:
        """Identity transform."""

    @property
    def is_identity(self) -> bool: ...

    @property
    def m11(self) -> float: ...

    @property
    def m12(self) -> float: ...

    @property
    def m21(self) -> float: ...

    @property
    def m22(self) -> float: ...

    @property
    def dx(self) -> float: ...

    @property
    def dy(self) -> float: ...

    def reset(self) -> None:
        """Restore the identity transform."""

    @property
    def determinant(self) -> float: ...

    def adjoint(self) -> WTransform: ...

    def map_point(self, x: float, y: float) -> tuple:
        """Apply the transform to (x, y) and return (tx, ty)."""

class FontFamily(enum.Enum):
    Default = 0

    Serif = 1

    SansSerif = 2

    Cursive = 3

    Fantasy = 4

    Monospace = 5

class FontStyle(enum.Enum):
    NormalStyle = 0

    Italic = 1

    Oblique = 2

class FontVariant(enum.Enum):
    Normal = 0

    SmallCaps = 1

class FontWeight(enum.Enum):
    Normal = 0

    Bold = 1

    Bolder = 2

    Lighter = 3

    Value = 4

class FontSize(enum.Enum):
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
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, family: FontFamily) -> None: ...

    def set_family(self, family: FontFamily, specific_families: str = '') -> None:
        """
        Generic family + optional comma-separated specific font names (e.g. setFamily(Monospace, "'Courier New'")).
        """

    def set_style(self, style: FontStyle) -> None: ...

    def set_variant(self, variant: FontVariant) -> None: ...

    def set_weight(self, weight: FontWeight, value: int = 400) -> None:
        """
        When weight=Value, the second argument is the CSS numeric weight (100, 200, …, 900).
        """

    def set_size(self, size: WLength) -> None:
        """
        Size as a WLength — accepts a number (treated as pixels), a WLength('1.2em'), or a parsed CSS string.
        """

    def size_length(self, medium_size: float = 16.0) -> WLength: ...

class GradientStyle(enum.Enum):
    Linear = 0

    Radial = 1

class WGradient:
    def __init__(self) -> None: ...

    @property
    def style(self) -> GradientStyle: ...

    @property
    def is_empty(self) -> bool: ...

    def set_linear_gradient(self, x0: float, y0: float, x1: float, y1: float) -> None:
        """Configure a linear gradient from (x0,y0) to (x1,y1)."""

    def set_radial_gradient(self, cx: float, cy: float, r: float, fx: float, fy: float) -> None:
        """
        Configure a radial gradient: bounding circle centred at (cx,cy) with radius r, focal point at (fx,fy).
        """

    def add_color_stop(self, position: float, color: WColor) -> None:
        """Add a color stop at `position` (0.0 = start, 1.0 = end)."""

    def clear_color_stops(self) -> None: ...

class WShadow:
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, dx: float, dy: float, color: WColor, blur: float) -> None: ...

    def set_offsets(self, dx: float, dy: float) -> None: ...

    def set_color(self, color: WColor) -> None: ...

    def set_blur(self, blur: float) -> None: ...

    @property
    def offset_x(self) -> float: ...

    @property
    def offset_y(self) -> float: ...

    @property
    def color(self) -> WColor: ...

    @property
    def blur(self) -> float: ...

    @property
    def none(self) -> bool:
        """True for the default (no-shadow) value."""

class BorderStyle(enum.Enum):
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
    Thin = 0

    Medium = 1

    Thick = 2

    Explicit = 3

class WBorder:
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, style: BorderStyle, width: BorderWidth, color: WColor) -> None: ...

    @overload
    def __init__(self, style: BorderStyle, width: WLength, color: WColor) -> None:
        """
        Explicit-width variant — `width` is a WLength rather than the Thin/Medium/Thick preset.
        """

    def set_style(self, style: BorderStyle) -> None: ...

    def set_color(self, color: WColor) -> None: ...

    @property
    def style(self) -> BorderStyle: ...

    @property
    def color(self) -> WColor: ...

    @property
    def explicit_width(self) -> WLength: ...

class PenStyle(enum.Enum):
    NoPen = 0

    SolidLine = 1

    DashLine = 2

    DotLine = 3

    DashDotLine = 4

    DashDotDotLine = 5

class PenCapStyle(enum.Enum):
    FlatCap = 0

    SquareCap = 1

    RoundCap = 2

class PenJoinStyle(enum.Enum):
    MiterJoin = 0

    BevelJoin = 1

    RoundJoin = 2

class WPen:
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, style: PenStyle) -> None: ...

    @overload
    def __init__(self, color: WColor) -> None: ...

    def set_style(self, style: PenStyle) -> None: ...

    def set_cap_style(self, style: PenCapStyle) -> None: ...

    def set_join_style(self, style: PenJoinStyle) -> None: ...

    def set_width(self, width: WLength) -> None: ...

    def set_color(self, color: WColor) -> None: ...

    def set_gradient(self, gradient: WGradient) -> None:
        """Use a gradient for the stroke instead of a solid color."""

    @property
    def color(self) -> WColor: ...

    @property
    def style(self) -> PenStyle: ...

    @property
    def cap_style(self) -> PenCapStyle: ...

    @property
    def join_style(self) -> PenJoinStyle: ...

    @property
    def width(self) -> WLength: ...

class BrushStyle(enum.Enum):
    NoBrush = 0

    SolidPattern = 1

    Gradient = 2

class WBrush:
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, style: BrushStyle) -> None: ...

    @overload
    def __init__(self, color: WColor) -> None: ...

    @overload
    def __init__(self, gradient: WGradient) -> None:
        """Construct a gradient-filled brush. style is set to Gradient."""

    def set_style(self, style: BrushStyle) -> None: ...

    def set_color(self, color: WColor) -> None: ...

    def set_gradient(self, gradient: WGradient) -> None:
        """Use a gradient for the fill. Sets style to Gradient."""

    @property
    def color(self) -> WColor: ...

    @property
    def style(self) -> BrushStyle: ...

class WPainterPath:
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, start: WPointF) -> None:
        """Begin the path at the given start point."""

    @property
    def is_empty(self) -> bool: ...

    @property
    def current_position(self) -> WPointF: ...

    def close_sub_path(self) -> None:
        """Close the current sub-path with a line back to its start."""

    def move_to(self, x: float, y: float) -> None: ...

    def line_to(self, x: float, y: float) -> None: ...

    def cubic_to(self, c1x: float, c1y: float, c2x: float, c2y: float, end_x: float, end_y: float) -> None:
        """
        Cubic Bézier from current position to (end_x, end_y) via control points (c1x, c1y) and (c2x, c2y).
        """

    def arc_to(self, cx: float, cy: float, radius: float, start_angle: float, sweep_length: float) -> None:
        """
        Arc of `radius` centred at (cx, cy); angles in degrees, 0° = 3 o'clock, sweeping counter-clockwise.
        """

    def add_rect(self, x: float, y: float, width: float, height: float) -> None: ...

    def add_ellipse(self, x: float, y: float, width: float, height: float) -> None: ...

class PainterImage:
    @overload
    def __init__(self, url: str, width: int, height: int) -> None:
        """Reference an external image at `url` with explicit pixel dimensions."""

    @overload
    def __init__(self, url: str, file: str) -> None:
        """
        Reference an image whose pixel dimensions Wt should read from local file `file` (the URL is what the browser uses; the file is where Wt looks for size metadata).
        """

    @property
    def uri(self) -> str: ...

    @property
    def width(self) -> int: ...

    @property
    def height(self) -> int: ...

class WPainter:
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

    def restore(self) -> None: ...

    def set_pen(self, pen: WPen) -> None: ...

    def set_brush(self, brush: WBrush) -> None: ...

    def set_font(self, font: WFont) -> None: ...

    def set_shadow(self, shadow: WShadow) -> None:
        """
        Apply a drop-shadow effect to subsequent draw operations. Pass `wt.WShadow()` to clear.
        """

    @property
    def pen(self) -> WPen: ...

    @property
    def brush(self) -> WBrush: ...

    def set_world_transform(self, transform: WTransform, combine: bool = False) -> None: ...

    def translate(self, dx: float, dy: float) -> None: ...

    def rotate(self, angle: float) -> None:
        """
        Rotate by `angle` degrees about the origin of the local coordinate system.
        """

    def scale(self, sx: float, sy: float) -> None: ...

    def set_clipping(self, enabled: bool) -> None: ...

    def set_clip_path(self, path: WPainterPath) -> None: ...

    def draw_line(self, x1: float, y1: float, x2: float, y2: float) -> None: ...

    def draw_rect(self, x: float, y: float, width: float, height: float) -> None: ...

    def draw_ellipse(self, x: float, y: float, width: float, height: float) -> None:
        """Ellipse inscribed in the given bounding rect."""

    def draw_arc(self, x: float, y: float, width: float, height: float, start_angle: int, span_angle: int) -> None:
        """
        Arc inscribed in the bounding rect, swept from start to start+span (in 1/16-degree units, Wt convention).
        """

    def draw_pie(self, x: float, y: float, width: float, height: float, start_angle: int, span_angle: int) -> None: ...

    def draw_chord(self, x: float, y: float, width: float, height: float, start_angle: int, span_angle: int) -> None: ...

    def draw_point(self, x: float, y: float) -> None: ...

    def draw_path(self, path: WPainterPath) -> None: ...

    def draw_lines(self, lines: Sequence[WLineF]) -> None: ...

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
    def is_active(self) -> bool: ...

    Image: TypeAlias = PainterImage

class WPaintedWidget(WInteractWidget):
    @overload
    def __init__(self) -> None: ...

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
    def preferred_method(self) -> RenderMethod: ...

    def add_area(self, area: _T_Area) -> _T_Area:
        """
        Attach an image-map area (WRectArea / WCircleArea / WPolygonArea) that becomes a clickable region on top of the painted output.
        """

    def insert_area(self, index: int, area: _T_Area) -> _T_Area: ...

class RenderMethod(enum.Enum):
    InlineSvgVml = 0

    HtmlCanvas = 1

    PngImage = 2

class WAbstractArea(WObject):
    def set_link(self, link: WLink) -> None: ...

    def set_alternate_text(self, text: str) -> None: ...

    def set_tool_tip(self, text: str) -> None: ...

    def set_style_class(self, style_class: str) -> None: ...

    @property
    def hole(self) -> bool:
        """
        When True, this area is treated as a hole (transparent to clicks) cut out of the surrounding map.
        """

    @hole.setter
    def hole(self, arg: bool, /) -> None: ...

    @property
    def transformable(self) -> bool: ...

    @transformable.setter
    def transformable(self, arg: bool, /) -> None: ...

class WCircleArea(WAbstractArea):
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, x: int, y: int, radius: int) -> None: ...

    def set_center(self, x: int, y: int) -> None: ...

    @property
    def center_x(self) -> int: ...

    @property
    def center_y(self) -> int: ...

    @property
    def radius(self) -> int: ...

    @radius.setter
    def radius(self, arg: int, /) -> None: ...

class WRectArea(WAbstractArea):
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, x: int, y: int, width: int, height: int) -> None: ...

    @overload
    def __init__(self, rect: WRectF) -> None: ...

class WPolygonArea(WAbstractArea):
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, points: Sequence[WPointF]) -> None: ...

    def add_point(self, x: float, y: float) -> None: ...

    def set_points(self, points: Sequence[WPointF]) -> None: ...

class PaintDeviceFeatureFlag(enum.IntEnum):
    HasFontMetrics = 2

    CanWordWrap = 1

class WPaintDevice:
    @property
    def width(self) -> WLength: ...

    @property
    def height(self) -> WLength: ...

class WVectorImage(WPaintDevice):
    pass

class WSvgImage(WResource):
    def __init__(self, width: WLength, height: WLength) -> None:
        """
        Create an SVG paint surface of the given size. Construct a WPainter against it, paint, then mount the WSvgImage on a URL — clients fetch the SVG text.
        """

class WCanvasPaintDevice(WPaintDevice):
    def __init__(self, width: WLength, height: WLength) -> None: ...

class WMeasurePaintDevice(WPaintDevice):
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
    def __init__(self, width: WLength, height: WLength) -> None:
        """
        Create a PDF paint surface with the given page dimensions (typically in WLength.Point units — A4 portrait is roughly 595×842 pt).
        """

    def add_font_collection(self, directory: str, recursive: bool = True) -> None:
        """
        Search `directory` for TrueType / Type1 fonts and make them available to drawText. Pair with WFont.set_family(..., specific='Some Font') to reference one. Without registered fonts the PDF uses libharu's built-in 14 base fonts only.
        """

class ErrorCorrectionLevel(enum.Enum):
    Low = 0

    Medium = 1

    Quartile = 2

    High = 3

class WQrCode(WInteractWidget):
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, message: str, square_size: float) -> None: ...

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
    def square_size(self) -> float: ...

    @square_size.setter
    def square_size(self, arg: float, /) -> None: ...

    def set_error_correction_level(self, ecl: ErrorCorrectionLevel) -> None: ...

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

    def update(self) -> None: ...

class GoogleMapsVersion(enum.Enum):
    v3 = 0

class MapTypeControl(enum.Enum):
    Default = 1

    Menu = 2

    Hierarchical = 3

    HorizontalBar = 4

class GoogleMapCoordinate:
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, latitude: float, longitude: float) -> None: ...

    @property
    def latitude(self) -> float: ...

    @latitude.setter
    def latitude(self, arg: float, /) -> None: ...

    @property
    def longitude(self) -> float: ...

    @longitude.setter
    def longitude(self, arg: float, /) -> None: ...

    def distance_to(self, other: GoogleMapCoordinate) -> float:
        """
        Great-circle distance to `other` in kilometres (despite Wt's docs naming metres).
        """

    def __repr__(self) -> str: ...

class WGoogleMap(WWidget):
    def __init__(self, version: GoogleMapsVersion) -> None: ...

    @overload
    def set_center(self, center: GoogleMapCoordinate) -> None: ...

    @overload
    def set_center(self, center: GoogleMapCoordinate, zoom: int) -> None:
        """Pan to `center` and set the zoom level in one call."""

    def pan_to(self, center: GoogleMapCoordinate) -> None: ...

    def set_zoom(self, level: int) -> None: ...

    def zoom_in(self) -> None: ...

    def zoom_out(self) -> None: ...

    def save_position(self) -> None:
        """
        Remember the current centre + zoom. Restore with return_to_saved_position.
        """

    def return_to_saved_position(self) -> None: ...

    def add_marker(self, position: GoogleMapCoordinate) -> None: ...

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
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, latitude: float, longitude: float) -> None: ...

    @property
    def latitude(self) -> float: ...

    @latitude.setter
    def latitude(self, arg: float, /) -> None: ...

    @property
    def longitude(self) -> float: ...

    @longitude.setter
    def longitude(self, arg: float, /) -> None: ...

    def __repr__(self) -> str: ...

class WLeafletMapAbstractMapItem(WObject):
    def move(self, pos: LeafletMapCoordinate) -> None:
        """
        Move the item to a new coordinate. Triggers a re-render if the item is already attached to a map.
        """

    @property
    def position(self) -> LeafletMapCoordinate: ...

    @property
    def clicked(self) -> Signal:
        """
        Signal[] — user clicked the item. For overlay items (Popup, Tooltip), `interactive` must be set in options.
        """

    @property
    def double_clicked(self) -> Signal: ...

    @property
    def mouse_went_down(self) -> Signal: ...

    @property
    def mouse_went_up(self) -> Signal: ...

    @property
    def mouse_went_over(self) -> Signal: ...

    @property
    def mouse_went_out(self) -> Signal: ...

class WLeafletMapAbstractOverlayItem(WLeafletMapAbstractMapItem):
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

    def open(self) -> None: ...

    def close(self) -> None: ...

    def toggle(self) -> None: ...

    @property
    def is_open(self) -> bool: ...

    @property
    def opened_signal(self) -> Signal: ...

    @property
    def closed_signal(self) -> Signal: ...

class WLeafletMapPopup(WLeafletMapAbstractOverlayItem):
    @overload
    def __init__(self, pos: LeafletMapCoordinate) -> None: ...

    @overload
    def __init__(self, content: str) -> None:
        """Shortcut: popup whose content is a WText wrapping the given string."""

    @overload
    def __init__(self, pos: LeafletMapCoordinate, content: str) -> None: ...

    @overload
    def __init__(self, pos: LeafletMapCoordinate, content: WWidget) -> None:
        """
        Popup at `pos` with a widget content. Ownership of `content` transfers.
        """

class WLeafletMapTooltip(WLeafletMapAbstractOverlayItem):
    @overload
    def __init__(self, pos: LeafletMapCoordinate) -> None: ...

    @overload
    def __init__(self, content: str) -> None: ...

    @overload
    def __init__(self, pos: LeafletMapCoordinate, content: str) -> None: ...

    @overload
    def __init__(self, pos: LeafletMapCoordinate, content: WWidget) -> None: ...

class WLeafletMapMarker(WLeafletMapAbstractMapItem):
    def add_popup(self, popup: _T_Popup) -> _T_Popup:
        """
        Attach a popup that opens when the marker is clicked. Replaces any previously-added popup on this marker.
        """

    def remove_popup(self) -> None: ...

    @property
    def popup(self) -> WLeafletMapPopup:
        """Current popup, or None if none is attached."""

    def add_tooltip(self, tooltip: _T_Tooltip) -> _T_Tooltip:
        """
        Attach a tooltip that appears on hover. Replaces any previously-added tooltip.
        """

    def remove_tooltip(self) -> None: ...

    @property
    def tooltip(self) -> WLeafletMapTooltip: ...

class WLeafletMapLeafletMarker(WLeafletMapMarker):
    def __init__(self, pos: LeafletMapCoordinate) -> None:
        """Construct the standard Leaflet pin marker."""

    def set_options(self, options: Json.Object) -> None:
        """
        Leaflet marker options (icon, draggable, riseOnHover, …). See https://leafletjs.com/reference.html#marker.
        """

class WLeafletMapWidgetMarker(WLeafletMapMarker):
    def __init__(self, pos: LeafletMapCoordinate, widget: WWidget) -> None:
        """
        Place an arbitrary Wt widget at `pos` on the map. Ownership of the widget transfers.
        """

    @property
    def widget(self) -> WWidget: ...

    def set_anchor_point(self, x: float, y: float) -> None:
        """
        Anchor (the 'tip' of the marker relative to its top-left corner) in pixels. Negative x = horizontal center; negative y = vertical center. Default is centred both ways.
        """

class WLeafletMap(WWidget):
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, options: Json.Object) -> None:
        """
        Construct with Leaflet map options (e.g. centre, zoom). Pass a Json.Object (or use the default ctor + set_options).
        """

    def set_options(self, options: Json.Object) -> None: ...

    def add_tile_layer(self, url_template: str, options: Json.Object) -> None:
        """
        Add a tile source. `url_template` is a Leaflet URL template with {z}/{x}/{y} placeholders (e.g. 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'). `options` is a Json.Object holding Leaflet tile-layer options (maxZoom, attribution, subdomains, …).
        """

    def pan_to(self, center: LeafletMapCoordinate) -> None: ...

    @property
    def zoom_level(self) -> int: ...

    @zoom_level.setter
    def zoom_level(self, arg: int, /) -> None: ...

    @property
    def position(self) -> LeafletMapCoordinate: ...

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

    def add_tooltip(self, tooltip: _T_Tooltip) -> _T_Tooltip: ...

    Coordinate: TypeAlias = LeafletMapCoordinate

    AbstractMapItem: TypeAlias = WLeafletMapAbstractMapItem

    AbstractOverlayItem: TypeAlias = WLeafletMapAbstractOverlayItem

    Popup: TypeAlias = WLeafletMapPopup

    Tooltip: TypeAlias = WLeafletMapTooltip

    Marker: TypeAlias = WLeafletMapMarker

    LeafletMarker: TypeAlias = WLeafletMapLeafletMarker

    WidgetMarker: TypeAlias = WLeafletMapWidgetMarker

class WColor:
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, red: int, green: int, blue: int, alpha: int = 255) -> None: ...

    @overload
    def __init__(self, name: str) -> None: ...

    @property
    def red(self) -> int: ...

    @property
    def green(self) -> int: ...

    @property
    def blue(self) -> int: ...

    @property
    def alpha(self) -> int: ...

    @property
    def is_default(self) -> bool:
        """True for the default-constructed color (transparent/inherited)."""

    def set_rgb(self, red: int, green: int, blue: int, alpha: int = 255) -> None: ...

    def set_name(self, name: str) -> None: ...

class WPasswordEdit(WLineEdit):
    def __init__(self) -> None: ...

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
    @overload
    def __init__(self, text: str) -> None: ...

    @overload
    def __init__(self, with_buttons: bool, text: str) -> None:
        """
        When `with_buttons` is False, the edit auto-saves on blur and no save/cancel buttons are shown.
        """

    @property
    def text(self) -> str: ...

    @text.setter
    def text(self, arg: str, /) -> None: ...

    @property
    def placeholder_text(self) -> str: ...

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
    Editing = 1

    DropDownIcon = 2

class Options:
    def __init__(self) -> None: ...

    @property
    def highlight_begin_tag(self) -> str: ...

    @highlight_begin_tag.setter
    def highlight_begin_tag(self, arg: str, /) -> None: ...

    @property
    def highlight_end_tag(self) -> str: ...

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
    def whitespace(self) -> str: ...

    @whitespace.setter
    def whitespace(self, arg: str, /) -> None: ...

    @property
    def word_separators(self) -> str: ...

    @word_separators.setter
    def word_separators(self, arg: str, /) -> None: ...

    @property
    def append_replaced_text(self) -> str: ...

    @append_replaced_text.setter
    def append_replaced_text(self, arg: str, /) -> None: ...

    @property
    def word_start_regexp(self) -> str: ...

    @word_start_regexp.setter
    def word_start_regexp(self, arg: str, /) -> None: ...

class IntFormWidgetSignal:
    def connect(self, callable: Callable) -> Connection: ...

    def disconnect_all_slots(self) -> None: ...

class WSuggestionPopup(WWidget):
    def __init__(self, options: Options) -> None:
        """Construct with an Options config — see WSuggestionPopup.Options."""

    def for_edit(self, edit: WFormWidget, triggers: int = 1) -> None:
        """
        Attach this popup to a form widget. The popup will offer completions while the user edits the field. Pass triggers as a bitwise OR of PopupTrigger values.
        """

    def remove_edit(self, edit: WFormWidget) -> None: ...

    def show_at(self, edit: WFormWidget) -> None: ...

    def clear_suggestions(self) -> None: ...

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

    def set_auto_select_enabled(self, enabled: bool) -> None: ...

    @property
    def activated(self) -> IntFormWidgetSignal:
        """
        IntFormWidgetSignal — fires when the user picks a suggestion. Slot receives (row_index, edit_widget); edit_widget is whichever WFormWidget the popup was for_edit'd against.
        """

    def set_model(self, model: WAbstractItemModel) -> None: ...

    @property
    def model(self) -> WAbstractItemModel: ...

    class Options:
        def __init__(self) -> None: ...

        @property
        def highlight_begin_tag(self) -> str: ...

        @highlight_begin_tag.setter
        def highlight_begin_tag(self, arg: str, /) -> None: ...

        @property
        def highlight_end_tag(self) -> str: ...

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
        def whitespace(self) -> str: ...

        @whitespace.setter
        def whitespace(self, arg: str, /) -> None: ...

        @property
        def word_separators(self) -> str: ...

        @word_separators.setter
        def word_separators(self, arg: str, /) -> None: ...

        @property
        def append_replaced_text(self) -> str: ...

        @append_replaced_text.setter
        def append_replaced_text(self, arg: str, /) -> None: ...

        @property
        def word_start_regexp(self) -> str: ...

        @word_start_regexp.setter
        def word_start_regexp(self, arg: str, /) -> None: ...

class WColorPicker(WFormWidget):
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, color: WColor) -> None: ...

    @property
    def color(self) -> WColor: ...

    @color.setter
    def color(self, arg: WColor, /) -> None: ...

    @property
    def color_input(self) -> EventSignal:
        """
        EventSignal[] — fires continuously while the user drags through the color picker. Use the inherited `changed` signal for commit-only notifications.
        """

class WTextEdit(WTextArea):
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, text: str) -> None: ...

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
    FileSelection = 1

    DirectorySelection = 2

class WFileDropWidgetFile(WObject):
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
    def connect(self, callable: Callable) -> Connection: ...

    def disconnect_all_slots(self) -> None: ...

class FileListSignal:
    def connect(self, callable: Callable) -> Connection: ...

    def disconnect_all_slots(self) -> None: ...

class FileSizeSignal:
    def connect(self, callable: Callable) -> Connection: ...

    def disconnect_all_slots(self) -> None: ...

class WFileDropWidget(WContainerWidget):
    def __init__(self) -> None: ...

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

    def set_accept_drops(self, enable: bool) -> None: ...

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
    def on_click_file_picker(self) -> FilePickerType: ...

    def open_file_picker(self) -> None:
        """
        Programmatically open the file picker as if the user clicked. Useful when wiring the widget to an external button.
        """

    def open_directory_picker(self) -> None: ...

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
    Left = 1

    Right = 2

    Center = 4

    Justify = 8

    Baseline = 16

    Top = 128

    Middle = 512

    Bottom = 1024

class WPoint:
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, x: int, y: int) -> None: ...

    @property
    def x(self) -> int: ...

    @x.setter
    def x(self, arg: int, /) -> None: ...

    @property
    def y(self) -> int: ...

    @y.setter
    def y(self, arg: int, /) -> None: ...

    def __repr__(self) -> str: ...

class WPopupMenu(WMenu):
    def __init__(self) -> None: ...

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
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, text: str) -> None: ...

    @property
    def use_default_style(self) -> bool:
        """
        When True (default), Wt applies its theme's badge CSS class. Disable to style purely via your own classes/CSS.
        """

    @use_default_style.setter
    def use_default_style(self, arg: bool, /) -> None: ...

class WToolBar(WWidget):
    def __init__(self) -> None: ...

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

    def add_button(self, button: _T_Button, alignment: AlignmentFlag = AlignmentFlag.Left) -> _T_Button: ...

    def add_widget(self, widget: _T_Widget, alignment: AlignmentFlag = AlignmentFlag.Left) -> _T_Widget: ...

    def add_separator(self) -> None:
        """Add a visual divider between groups of items."""

class WSplitButton(WWidget):
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, label: str) -> None: ...

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
    def __init__(self) -> None: ...

    def set_title(self, title: str, link: WLink = ...) -> None:
        """
        Set the brand/title shown at the left of the nav bar. Optionally wraps it in a link.
        """

    def set_responsive(self, responsive: bool) -> None:
        """
        When True, collapses the contents into a hamburger menu on narrow viewports (Bootstrap responsive behaviour). Wt has no getter for this — the flag is write-only on the C++ side.
        """

    def add_menu(self, menu: _T_Menu, alignment: AlignmentFlag = AlignmentFlag.Left) -> _T_Menu: ...

    def add_form_field(self, widget: _T_Widget, alignment: AlignmentFlag = AlignmentFlag.Left) -> _T_Widget:
        """
        Embed a form field (e.g. a small WLineEdit for a search bar). Distinct from the standalone add_search variant only in styling.
        """

    def add_search(self, field: _T_LineEdit, alignment: AlignmentFlag = AlignmentFlag.Left) -> _T_LineEdit: ...

    def add_widget(self, widget: _T_Widget, alignment: AlignmentFlag = AlignmentFlag.Left) -> _T_Widget: ...
