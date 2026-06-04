#include "common.hpp"
#include "signal_helpers.hpp"

#include <Wt/WEvent.h>
#include <Wt/WGlobal.h>     // Key, KeyboardModifier, MouseButton
#include <Wt/WJavaScript.h> // JSignal
#include <Wt/WSignal.h>
#include <Wt/WString.h>

#include <memory>
#include <mutex>
#include <string>
#include <string_view>
#include <unordered_map>
#include <vector>

namespace witty_for_python {

namespace {

// Maps signal raw pointer → live connections opened through py_connect.
// Used solely for the atexit cleanup pass; see signal_helpers.hpp.
struct Registry {
    std::mutex mu;
    std::unordered_map<const void*, std::vector<Wt::Signals::connection>> by_signal;
};

Registry& registry() {
    // Function-local static avoids static-init-order issues across TUs.
    static Registry r;
    return r;
}

}  // namespace

void connection_registry_add(const void* signal_ptr,
                             Wt::Signals::connection conn) {
    auto& r = registry();
    std::lock_guard<std::mutex> lk(r.mu);
    r.by_signal[signal_ptr].push_back(std::move(conn));
}

void connection_registry_disconnect_all(const void* signal_ptr) noexcept {
    // Move the vector out under the lock, then disconnect outside it: the
    // connection destructors run user-defined code (slot dtors → shared_ptr
    // dtors → Py_DECREF) and we don't want the registry mutex held during
    // that. Robust against re-entrancy.
    std::vector<Wt::Signals::connection> taken;
    {
        auto& r = registry();
        std::lock_guard<std::mutex> lk(r.mu);
        auto it = r.by_signal.find(signal_ptr);
        if (it == r.by_signal.end()) return;
        taken = std::move(it->second);
        r.by_signal.erase(it);
    }
    for (auto& c : taken) c.disconnect();
}

void connection_registry_disconnect_all_signals() noexcept {
    std::unordered_map<const void*, std::vector<Wt::Signals::connection>> taken;
    {
        auto& r = registry();
        std::lock_guard<std::mutex> lk(r.mu);
        taken = std::move(r.by_signal);
        r.by_signal.clear();
    }
    for (auto& kv : taken) {
        for (auto& c : kv.second) c.disconnect();
    }
}

std::size_t connection_registry_size() noexcept {
    auto& r = registry();
    std::lock_guard<std::mutex> lk(r.mu);
    std::size_t n = 0;
    for (auto& kv : r.by_signal) n += kv.second.size();
    return n;
}

int python_arity(nb::handle callable) noexcept {
    try {
        // nanobind bound methods (e.g. `dialog.show`) report `*args, **kwargs`
        // to inspect.signature, but their underlying C++ binding has fixed
        // arity. Treat them as 0-arg slots so `button.clicked.connect(
        // dialog.show)` does the expected thing — payload is dropped, show()
        // is called with no args. Callers who want a bound method to receive
        // payload should wrap explicitly: `sig.connect(lambda x: obj.f(x))`.
        // We identify the type by `type(cb).__name__` since the limited ABI
        // hides `PyTypeObject::tp_name`.
        nb::handle tp(reinterpret_cast<PyObject*>(Py_TYPE(callable.ptr())));
        std::string type_name = nb::cast<std::string>(tp.attr("__name__"));
        if (type_name == "nb_bound_method") {
            return 0;
        }

        nb::object inspect = nb::module_::import_("inspect");
        nb::object sig = inspect.attr("signature")(callable);
        nb::object params = sig.attr("parameters");
        int positional = 0;
        bool variadic = false;
        for (nb::handle p : params.attr("values")()) {
            // inspect.Parameter.kind: POSITIONAL_ONLY=0, POSITIONAL_OR_KEYWORD=1,
            // VAR_POSITIONAL=2, KEYWORD_ONLY=3, VAR_KEYWORD=4.
            int kind = nb::cast<int>(p.attr("kind"));
            if (kind == 0 || kind == 1) {
                ++positional;
            } else if (kind == 2) {
                variadic = true;
            }
        }
        return variadic ? -1 : positional;
    } catch (...) {
        return -1;
    }
}

void register_signals(nb::module_& m) {
    // ---- Event-related enums & structs ----

    nb::class_<Wt::Coordinates>(m, "Coordinates",
        "An (x, y) pixel pair, used wherever an event reports a position\n"
        "(WMouseEvent.document, .window, .screen, .widget). Plain value\n"
        "type — construct directly if you need to synthesize one.")
        .def(nb::init<int, int>(), "x"_a, "y"_a,
             "Construct a Coordinates with the given pixel offsets.")
        .def_rw("x", &Wt::Coordinates::x, "Horizontal offset in pixels.")
        .def_rw("y", &Wt::Coordinates::y, "Vertical offset in pixels.")
        .def("__repr__", [](const Wt::Coordinates& c) {
            return "Coordinates(x=" + std::to_string(c.x)
                + ", y=" + std::to_string(c.y) + ")";
        });

    nb::enum_<Wt::MouseButton>(m, "MouseButton", nb::is_arithmetic(),
        "Mouse button identifier surfaced on WMouseEvent.button. None_\n"
        "is the no-button case (e.g. a pure move event); the trailing\n"
        "underscore avoids a clash with the Python `None` literal.")
        .value("None_", Wt::MouseButton::None)   // `None` is reserved in Python
        .value("Left", Wt::MouseButton::Left)
        .value("Middle", Wt::MouseButton::Middle)
        .value("Right", Wt::MouseButton::Right);

    nb::enum_<Wt::KeyboardModifier>(m, "KeyboardModifier", nb::is_arithmetic(),
        "Keyboard-modifier bit; combine via bitwise OR to express\n"
        "compound chords. Surfaced as an int bitmask on event payloads\n"
        "(WMouseEvent.modifiers, WKeyEvent.modifiers).")
        .value("None_", Wt::KeyboardModifier::None)
        .value("Shift", Wt::KeyboardModifier::Shift)
        .value("Control", Wt::KeyboardModifier::Control)
        .value("Alt", Wt::KeyboardModifier::Alt)
        .value("Meta", Wt::KeyboardModifier::Meta);

    nb::enum_<Wt::Key>(m, "Key", nb::is_arithmetic(),
        "Symbolic key codes surfaced on WKeyEvent.key. Use these to\n"
        "match non-printable keys (Enter, arrows, F-keys, …); printable\n"
        "characters are easier to handle via `WKeyEvent.char_code`.")
        .value("Unknown", Wt::Key::Unknown)
        .value("Enter", Wt::Key::Enter)
        .value("Tab", Wt::Key::Tab)
        .value("Backspace", Wt::Key::Backspace)
        .value("Shift", Wt::Key::Shift)
        .value("Control", Wt::Key::Control)
        .value("Alt", Wt::Key::Alt)
        .value("Pause", Wt::Key::Pause)
        .value("Escape", Wt::Key::Escape)
        .value("PageUp", Wt::Key::PageUp)
        .value("PageDown", Wt::Key::PageDown)
        .value("End", Wt::Key::End)
        .value("Home", Wt::Key::Home)
        .value("Left", Wt::Key::Left)
        .value("Up", Wt::Key::Up)
        .value("Right", Wt::Key::Right)
        .value("Down", Wt::Key::Down)
        .value("Insert", Wt::Key::Insert)
        .value("Delete", Wt::Key::Delete)
        .value("Meta", Wt::Key::Meta)
        .value("F1", Wt::Key::F1).value("F2", Wt::Key::F2)
        .value("F3", Wt::Key::F3).value("F4", Wt::Key::F4)
        .value("F5", Wt::Key::F5).value("F6", Wt::Key::F6)
        .value("F7", Wt::Key::F7).value("F8", Wt::Key::F8)
        .value("F9", Wt::Key::F9).value("F10", Wt::Key::F10)
        .value("F11", Wt::Key::F11).value("F12", Wt::Key::F12)
        .value("Space", Wt::Key::Space)
        .value("A", Wt::Key::A).value("B", Wt::Key::B).value("C", Wt::Key::C)
        .value("D", Wt::Key::D).value("E", Wt::Key::E).value("F", Wt::Key::F)
        .value("G", Wt::Key::G).value("H", Wt::Key::H).value("I", Wt::Key::I)
        .value("J", Wt::Key::J).value("K", Wt::Key::K).value("L", Wt::Key::L)
        .value("M", Wt::Key::M).value("N", Wt::Key::N).value("O", Wt::Key::O)
        .value("P", Wt::Key::P).value("Q", Wt::Key::Q).value("R", Wt::Key::R)
        .value("S", Wt::Key::S).value("T", Wt::Key::T).value("U", Wt::Key::U)
        .value("V", Wt::Key::V).value("W", Wt::Key::W).value("X", Wt::Key::X)
        .value("Y", Wt::Key::Y).value("Z", Wt::Key::Z);

    nb::class_<Wt::WMouseEvent>(m, "WMouseEvent",
        "Payload delivered to mouse-event handlers (clicked,\n"
        "double_clicked, mouse_over, mouse_out, wheel events).\n"
        "\n"
        "    def on_click(e: wt.WMouseEvent):\n"
        "        if e.button == wt.MouseButton.Right:\n"
        "            show_context_menu(e.widget.x, e.widget.y)\n"
        "    button.clicked.connect(on_click)\n"
        "\n"
        "The four coordinate properties report the cursor's position in\n"
        "different reference frames — use whichever frame your math is in.")
        .def_prop_ro("button", &Wt::WMouseEvent::button,
            "MouseButton that triggered the event (None_ for pure-move).")
        .def_prop_ro("modifiers",
            [](const Wt::WMouseEvent& e) {
                return static_cast<int>(e.modifiers().value());
            },
            "Int bitmask of KeyboardModifier values held during the event.")
        .def_prop_ro("document", &Wt::WMouseEvent::document,
            "Cursor position relative to the document's top-left corner.")
        .def_prop_ro("window", &Wt::WMouseEvent::window,
            "Cursor position relative to the browser window's top-left\n"
            "(equivalent to viewport coordinates).")
        .def_prop_ro("screen", &Wt::WMouseEvent::screen,
            "Cursor position relative to the user's screen.")
        .def_prop_ro("widget", &Wt::WMouseEvent::widget,
            "Cursor position relative to the widget that fired the event\n"
            "— most useful for picking inside the widget's own geometry.")
        .def_prop_ro("wheel_delta", &Wt::WMouseEvent::wheelDelta,
            "Signed wheel ticks for wheel events (positive = up). Zero\n"
            "for non-wheel events.");

    nb::class_<Wt::WKeyEvent>(m, "WKeyEvent",
        "Payload delivered to keyboard-event handlers (key_pressed,\n"
        "key_went_down, enter_pressed).\n"
        "\n"
        "    def on_key(e: wt.WKeyEvent):\n"
        "        if e.key == wt.Key.Escape:\n"
        "            dialog.hide()\n"
        "    dialog.key_went_down.connect(on_key)")
        .def_prop_ro("key", &Wt::WKeyEvent::key,
            "Symbolic Key value — use to match non-printable keys.")
        .def_prop_ro("char_code", &Wt::WKeyEvent::charCode,
            "Unicode code point of the printable character pressed, or 0\n"
            "for non-printable keys. Easier than `key` for typed-text logic.")
        .def_prop_ro("modifiers",
            [](const Wt::WKeyEvent& e) {
                return static_cast<int>(e.modifiers().value());
            },
            "Int bitmask of KeyboardModifier values held during the event.");

    // ---- Connection handle ----

    nb::class_<Wt::Signals::connection>(m, "Connection",
        "Handle to a signal subscription returned by `Signal.connect`.\n"
        "Keep it if you need to disconnect later; otherwise discard.\n"
        "\n"
        "    conn = button.clicked.connect(on_click)\n"
        "    ...\n"
        "    conn.disconnect()                    # stop receiving")
        .def("disconnect", &Wt::Signals::connection::disconnect,
            "Drop the subscription. The connected callback won't be\n"
            "invoked again for new emits. Idempotent.")
        .def("is_connected", &Wt::Signals::connection::isConnected,
            "True until `disconnect` is called or the signal is destroyed.");

    // ---- Signal types ----
    //
    // Each Wt::Signal<...> / Wt::EventSignal<...> instantiation is a separate
    // C++ type and therefore a separate Python class. We bind the common ones.
    // Slots are Python callables; we inspect their arity at connect time and
    // forward the payload only when the callable wants it.

    // Generic Wt::Signal<T> instantiations get a no-arg constructor so they
    // can be created on the Python side for testing or for free-standing
    // signal/slot patterns outside the Wt widget tree.
    // Each binding below exposes `disconnect_all_slots()`. It clears every
    // connection opened through py_connect, releasing the Python-callable
    // holders. The Python-side atexit handler in witty_for_python/__init__.py invokes
    // this on every live Signal/EventSignal instance before nanobind's
    // shutdown-time leak detector runs. See README "Shutdown warnings".

    nb::class_<Wt::Signal<>>(m, "Signal",
        "Zero-payload signal. Construct standalone for ad-hoc pub/sub,\n"
        "or use the no-arg signals already on widgets.\n"
        "\n"
        "    s = wt.Signal()\n"
        "    s.connect(lambda: print('fired'))\n"
        "    s.emit()")
        .def(nb::init<>(),
             "Construct a fresh signal with no subscribers.")
        .def("connect",
            [](Wt::Signal<>& s, nb::callable cb) {
                return py_connect<Wt::Signal<>>(s, std::move(cb));
            }, "callable"_a,
            "Subscribe `callable()` to this signal. Returns a Connection;\n"
            "the callable runs on each `emit`.")
        .def("emit", &Wt::Signal<>::emit,
            "Fire the signal — every connected callable is invoked once,\n"
            "in connection order.")
        .def("disconnect_all_slots",
            [](Wt::Signal<>& s) { connection_registry_disconnect_all(&s); },
            "Drop every connection opened through `connect`. Used by the\n"
            "library's shutdown handler; most code doesn't need it.");

    nb::class_<Wt::Signal<int>>(m, "IntSignal",
        "Signal carrying a single int payload.\n"
        "\n"
        "    s = wt.IntSignal()\n"
        "    s.connect(lambda n: print(f'got {n}'))\n"
        "    s.emit(42)")
        .def(nb::init<>(),
             "Construct a fresh signal with no subscribers.")
        .def("connect",
            [](Wt::Signal<int>& s, nb::callable cb) {
                return py_connect<Wt::Signal<int>, int>(s, std::move(cb));
            }, "callable"_a,
            "Subscribe `callable(int)` to this signal. A zero-arg\n"
            "callable also works — the payload is dropped.")
        .def("emit", &Wt::Signal<int>::emit,
            "Fire the signal with the given int payload.")
        .def("disconnect_all_slots",
            [](Wt::Signal<int>& s) { connection_registry_disconnect_all(&s); },
            "Drop every connection opened through `connect`.");

    nb::class_<Wt::Signal<bool>>(m, "BoolSignal",
        "Signal carrying a single bool payload.")
        .def(nb::init<>(),
             "Construct a fresh signal with no subscribers.")
        .def("connect",
            [](Wt::Signal<bool>& s, nb::callable cb) {
                return py_connect<Wt::Signal<bool>, bool>(s, std::move(cb));
            }, "callable"_a,
            "Subscribe `callable(bool)` to this signal.")
        .def("emit", &Wt::Signal<bool>::emit,
            "Fire the signal with the given bool payload.")
        .def("disconnect_all_slots",
            [](Wt::Signal<bool>& s) { connection_registry_disconnect_all(&s); },
            "Drop every connection opened through `connect`.");

    nb::class_<Wt::Signal<double>>(m, "DoubleSignal",
        "Signal carrying a single float payload.")
        .def(nb::init<>(),
             "Construct a fresh signal with no subscribers.")
        .def("connect",
            [](Wt::Signal<double>& s, nb::callable cb) {
                return py_connect<Wt::Signal<double>, double>(s, std::move(cb));
            }, "callable"_a,
            "Subscribe `callable(float)` to this signal.")
        .def("emit", &Wt::Signal<double>::emit,
            "Fire the signal with the given float payload.")
        .def("disconnect_all_slots",
            [](Wt::Signal<double>& s) { connection_registry_disconnect_all(&s); },
            "Drop every connection opened through `connect`.");

    nb::class_<Wt::Signal<Wt::WString>>(m, "StringSignal",
        "Signal carrying a single string payload.")
        .def(nb::init<>(),
             "Construct a fresh signal with no subscribers.")
        .def("connect",
            [](Wt::Signal<Wt::WString>& s, nb::callable cb) {
                return py_connect<Wt::Signal<Wt::WString>, Wt::WString>(s, std::move(cb));
            }, "callable"_a,
            "Subscribe `callable(str)` to this signal.")
        .def("emit", &Wt::Signal<Wt::WString>::emit,
            "Fire the signal with the given string payload.")
        .def("disconnect_all_slots",
            [](Wt::Signal<Wt::WString>& s) { connection_registry_disconnect_all(&s); },
            "Drop every connection opened through `connect`.");

    // EventSignals — same shape, distinct C++ types for DOM events.
    nb::class_<Wt::EventSignal<>>(m, "EventSignal",
        "Zero-payload signal backing DOM events (e.g. WCheckBox.on_check,\n"
        "WInteractWidget.enter_pressed). Like Signal but with no public\n"
        "constructor — the widget owns the instance and exposes it as a\n"
        "property.\n"
        "\n"
        "    container.add_widget(wt.WCheckBox('OK')).on_check.connect(handler)")
        .def("connect",
            [](Wt::EventSignal<>& s, nb::callable cb) {
                return py_connect<Wt::EventSignal<>>(s, std::move(cb));
            }, "callable"_a,
            "Subscribe `callable()` to this DOM event. Returns a Connection.")
        .def("disconnect_all_slots",
            [](Wt::EventSignal<>& s) { connection_registry_disconnect_all(&s); },
            "Drop every connection opened through `connect`.");

    nb::class_<Wt::EventSignal<Wt::WMouseEvent>>(m, "MouseEventSignal",
        "DOM-event signal carrying a WMouseEvent payload. Backs the\n"
        "`clicked` / `double_clicked` / `mouse_over` / `mouse_out` props\n"
        "on WInteractWidget.\n"
        "\n"
        "    button.clicked.connect(lambda e: print(e.button))")
        .def("connect",
            [](Wt::EventSignal<Wt::WMouseEvent>& s, nb::callable cb) {
                return py_connect<Wt::EventSignal<Wt::WMouseEvent>,
                                  const Wt::WMouseEvent&>(s, std::move(cb));
            }, "callable"_a,
            "Subscribe `callable(WMouseEvent)`. A zero-arg callable also\n"
            "works — the payload is dropped.")
        .def("disconnect_all_slots",
            [](Wt::EventSignal<Wt::WMouseEvent>& s) {
                connection_registry_disconnect_all(&s);
            },
            "Drop every connection opened through `connect`.");

    nb::class_<Wt::EventSignal<Wt::WKeyEvent>>(m, "KeyEventSignal",
        "DOM-event signal carrying a WKeyEvent payload. Backs the\n"
        "`key_pressed` / `key_went_down` props on WInteractWidget.\n"
        "\n"
        "    field.key_went_down.connect(\n"
        "        lambda e: dialog.hide() if e.key == wt.Key.Escape else None)")
        .def("connect",
            [](Wt::EventSignal<Wt::WKeyEvent>& s, nb::callable cb) {
                return py_connect<Wt::EventSignal<Wt::WKeyEvent>,
                                  const Wt::WKeyEvent&>(s, std::move(cb));
            }, "callable"_a,
            "Subscribe `callable(WKeyEvent)`. Zero-arg also works.")
        .def("disconnect_all_slots",
            [](Wt::EventSignal<Wt::WKeyEvent>& s) {
                connection_registry_disconnect_all(&s);
            },
            "Drop every connection opened through `connect`.");

    // ---- 64-bit / pair signals used by WFileUpload + WFileDropWidget ----
    //
    // No constructors are bound: these are always created C++-side as
    // members of widgets. JSignal has no public default ctor anyway
    // (requires a parent WObject + a JS name).

    // JSignal<int> — used by WLeafletMap.zoom_level_changed.
    nb::class_<Wt::JSignal<int>>(m, "JIntSignal",
        "JavaScript-emitted signal carrying an int. Like IntSignal but\n"
        "originates on the browser side and travels back to the server.\n"
        "Used for widgets where the client emits semantic events (e.g.\n"
        "WLeafletMap.zoom_level_changed).")
        .def("connect",
            [](Wt::JSignal<int>& s, nb::callable cb) {
                return py_connect<Wt::JSignal<int>, int>(s, std::move(cb));
            }, "callable"_a,
            "Subscribe `callable(int)` to client-side emits.")
        .def("disconnect_all_slots",
            [](Wt::JSignal<int>& s) {
                connection_registry_disconnect_all(&s);
            },
            "Drop every connection opened through `connect`.");

    // JSignal<long long> — file-too-large carries the rejected upload's
    // size in bytes. Used by WFileUpload.file_too_large.
    nb::class_<Wt::JSignal<long long>>(m, "JInt64Signal",
        "JavaScript-emitted signal carrying a 64-bit int — used where\n"
        "byte sizes don't fit in 32 bits (e.g. WFileUpload.file_too_large\n"
        "reporting the rejected upload's size).")
        .def("connect",
            [](Wt::JSignal<long long>& s, nb::callable cb) {
                return py_connect<Wt::JSignal<long long>, long long>(
                    s, std::move(cb));
            }, "callable"_a,
            "Subscribe `callable(int)` to client-side emits.")
        .def("disconnect_all_slots",
            [](Wt::JSignal<long long>& s) {
                connection_registry_disconnect_all(&s);
            },
            "Drop every connection opened through `connect`.");

    // Signal<unsigned long long, unsigned long long> — upload-progress
    // ticks: (bytes received so far, total bytes). Used by
    // WFileUpload.data_received and WFileDropWidget.File.data_received.
    nb::class_<Wt::Signal<unsigned long long, unsigned long long>>(
        m, "Uint64PairSignal",
        "Signal carrying a (uint64, uint64) pair — typically a\n"
        "progress tick reporting (bytes received, total bytes) on\n"
        "WFileUpload and WFileDropWidget.\n"
        "\n"
        "    upload.data_received.connect(\n"
        "        lambda recv, total: bar.set_value(100 * recv / total))")
        .def("connect",
            [](Wt::Signal<unsigned long long, unsigned long long>& s,
               nb::callable cb) {
                return py_connect<
                    Wt::Signal<unsigned long long, unsigned long long>,
                    unsigned long long, unsigned long long>(s, std::move(cb));
            }, "callable"_a,
            "Subscribe `callable(received, total)`. Either both ints or\n"
            "zero args; intermediate arities are an error.")
        .def("disconnect_all_slots",
            [](Wt::Signal<unsigned long long, unsigned long long>& s) {
                connection_registry_disconnect_all(&s);
            },
            "Drop every connection opened through `connect`.");
}

}  // namespace witty_for_python
