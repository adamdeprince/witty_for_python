#include "common.hpp"
#include "signal_helpers.hpp"

#include <Wt/WDefaultLoadingIndicator.h>
#include <Wt/WIcon.h>
#include <Wt/WIconPair.h>
#include <Wt/WJavaScript.h>      // JSignal<>
#include <Wt/WLink.h>
#include <Wt/WLoadingIndicator.h>
#include <Wt/WNotification.h>
#include <Wt/WOverlayLoadingIndicator.h>
#include <Wt/WPopupWidget.h>

#include <memory>
#include <string>

namespace witty_for_python {

void register_misc_ui(nb::module_& m) {
    // ---- JSignal<> (no-payload variant) ----
    //
    // Bound here because the first consumer is WNotification (clicked /
    // closed / shown / error are all parameterless JSignals). Same shape
    // as the existing JInt64Signal binding in bind_signals.cpp.

    nb::class_<Wt::JSignal<>>(m, "JSignal0",
        "Parameterless JavaScript signal — a Wt::JSignal<> bridged for\n"
        "Python. Fires when the corresponding client-side JS event happens\n"
        "(e.g. WNotification's clicked/closed/shown/error).")
        .def("connect",
            [](Wt::JSignal<>& s, nb::callable cb) {
                return py_connect<Wt::JSignal<>>(s, std::move(cb));
            }, "callable"_a,
            "Subscribe a no-arg callable. Returns a Connection — call\n"
            "`.disconnect()` to stop receiving.")
        .def("disconnect_all_slots",
            [](Wt::JSignal<>& s) {
                connection_registry_disconnect_all(&s);
            },
            "Drop every Python subscriber attached via `connect`.");

    nb::class_<Wt::WIcon, Wt::WInteractWidget>(m, "WIcon",
        "A Font Awesome icon rendered inline. Inherits WInteractWidget so\n"
        "`clicked` and the other input signals work without further setup.\n"
        "\n"
        "    container.add_widget(wt.WIcon('envelope')).clicked.connect(open_inbox)\n"
        "\n"
        "The icon name is looked up in the bundled Font Awesome stylesheet,\n"
        "which is added to the page lazily on first WIcon construction (or\n"
        "explicitly via `load_icon_font`).")
        .def(heap_init<Wt::WIcon>(),
             "Construct with no icon — set `name` later.")
        .def(heap_init<Wt::WIcon, const std::string&>(), "name"_a,
             "Construct with a Font Awesome icon name (e.g. 'play', 'gear').")
        .def_prop_rw("name",
            [](const Wt::WIcon& self) { return self.name(); },
            [](Wt::WIcon& self, const std::string& n) { self.setName(n); },
            "The Font Awesome icon name. Assigning swaps the rendered\n"
            "glyph on the next round-trip.")
        .def_prop_rw("size",
            &Wt::WIcon::size,
            &Wt::WIcon::setSize,
            "Multiplier on the default icon size. 1.0 = unchanged; 2.0 = "
            "doubled.")
        .def_static("load_icon_font", &Wt::WIcon::loadIconFont,
            "Add Font Awesome's CSS stylesheet to the application. Called "
            "automatically the first time a WIcon is constructed; expose "
            "it here for explicit early-load.");

    nb::enum_<Wt::WIconPair::IconType>(m, "IconType",
        "Tells WIconPair how to interpret its two icon strings.")
        .value("URI", Wt::WIconPair::IconType::URI,
               "Treat the string as a URL pointing at an image.")
        .value("IconName", Wt::WIconPair::IconType::IconName,
               "Treat the string as a Font Awesome icon name.");

    nb::class_<Wt::WIconPair, Wt::WWidget>(m, "WIconPair",
        "Two icons displayed one at a time, with optional click-to-toggle\n"
        "behavior. Useful for expand/collapse indicators, on/off lamps,\n"
        "anywhere a small bistable visual cue is wanted.\n"
        "\n"
        "    pair = container.add_widget(\n"
        "        wt.WIconPair('plus-square', 'minus-square'))\n"
        "    pair.set_icons_type(wt.IconType.IconName)\n"
        "    pair.icon1_clicked.connect(expand)\n"
        "    pair.icon2_clicked.connect(collapse)")
        .def(heap_init<Wt::WIconPair, const std::string&, const std::string&, bool>(),
             "icon1"_a, "icon2"_a, "click_is_switch"_a = true,
             "Two icon strings (URLs or Font-Awesome names). When "
             "`click_is_switch` is True (default), clicking either icon "
             "toggles the visible state.")
        .def_prop_rw("state",
            &Wt::WIconPair::state,
            &Wt::WIconPair::setState,
            "Active icon: 0 → icon1, 1 → icon2.")
        .def("show_icon1", &Wt::WIconPair::showIcon1,
             "Equivalent to `state = 0`.")
        .def("show_icon2", &Wt::WIconPair::showIcon2,
             "Equivalent to `state = 1`.")
        .def("set_icon1_type", &Wt::WIconPair::setIcon1Type, "type"_a,
             "Set whether icon1's string is a URL or a Font Awesome name.")
        .def("set_icon2_type", &Wt::WIconPair::setIcon2Type, "type"_a,
             "Set whether icon2's string is a URL or a Font Awesome name.")
        .def("set_icons_type", &Wt::WIconPair::setIconsType, "type"_a,
             "Shortcut for setting both icons to the same IconType.")
        .def_prop_ro("icon1_clicked", &Wt::WIconPair::icon1Clicked,
                     nb::rv_policy::reference_internal,
                     "MouseEventSignal — clicks while icon1 is visible.")
        .def_prop_ro("icon2_clicked", &Wt::WIconPair::icon2Clicked,
                     nb::rv_policy::reference_internal,
                     "MouseEventSignal — clicks while icon2 is visible.");

    // Bound as inheriting WWidget per the project convention for
    // WCompositeWidget descendants.

    nb::class_<Wt::WPopupWidget, Wt::WWidget>(m, "WPopupWidget",
        "A floating overlay that wraps an arbitrary widget. Anchors to\n"
        "another widget in the page and pops up over the surrounding\n"
        "content — useful for custom tooltips, detail callouts, or any\n"
        "content panel that should appear next to a trigger.\n"
        "\n"
        "    info = wt.WText('More details here.')\n"
        "    popup = wt.WPopupWidget(info)\n"
        "    popup.set_anchor_widget(trigger)\n"
        "    popup.transient = True\n"
        "\n"
        "Different from WPopupMenu (which is a menu of selectable items).")
        .def(nb::new_(
                [](std::unique_ptr<Wt::WWidget> contents) {
                    return std::make_unique<Wt::WPopupWidget>(
                        std::move(contents));
                }),
            "contents"_a,
            "Construct with the inner widget shown in the popup. Ownership "
            "transfers; the contents widget's Python wrapper becomes non-"
            "owning.")
        .def("set_anchor_widget",
            [](Wt::WPopupWidget& self, Wt::WWidget* anchor) {
                self.setAnchorWidget(anchor);
            },
            "anchor"_a,
            "Position the popup relative to `anchor` whenever it's shown.")
        .def_prop_rw("transient",
            &Wt::WPopupWidget::isTransient,
            [](Wt::WPopupWidget& self, bool transient) {
                self.setTransient(transient);
            },
            "When True, the popup auto-hides on outside click or focus loss.")
        .def("set_transient",
            &Wt::WPopupWidget::setTransient,
            "transient"_a, "auto_hide_delay_ms"_a = 0,
            "Variant of the `transient` setter that also sets the grace "
            "period before auto-hide fires after the mouse leaves.")
        .def_prop_ro("hidden_signal", &Wt::WPopupWidget::hidden,
                     nb::rv_policy::reference_internal,
                     "Signal[] — fires when the popup transitions to hidden "
                     "via a client-side event (not via Python `hidden=True`).")
        .def_prop_ro("shown_signal", &Wt::WPopupWidget::shown,
                     nb::rv_policy::reference_internal,
                     "Signal[] — fires when the popup transitions to shown.");

    // The base is abstract — concrete subclasses (WDefaultLoadingIndicator,
    // WOverlayLoadingIndicator) provide the visible loading UI shown by
    // WApplication during a server round-trip. Plug a custom one in via
    // WApplication.set_loading_indicator (not bound in v1).

    nb::class_<Wt::WLoadingIndicator, Wt::WWidget>(m, "WLoadingIndicator",
        "Abstract base for the spinner / banner shown during a server\n"
        "round-trip. Concrete subclasses (WDefaultLoadingIndicator,\n"
        "WOverlayLoadingIndicator) provide the visible UI; plug one into\n"
        "the application to control the look of the load state.")
        .def("set_message", &Wt::WLoadingIndicator::setMessage, "text"_a,
             "Replace the loading message shown to the user.");

    nb::class_<Wt::WDefaultLoadingIndicator, Wt::WLoadingIndicator>(
        m, "WDefaultLoadingIndicator",
        "The default unobtrusive loading indicator — a small fixed-\n"
        "position text label in the corner of the page.")
        .def(heap_init<Wt::WDefaultLoadingIndicator>(),
             "Construct the default text-label indicator.");

    nb::class_<Wt::WOverlayLoadingIndicator, Wt::WLoadingIndicator>(
        m, "WOverlayLoadingIndicator",
        "A more aggressive loading indicator — dims the entire page with\n"
        "a translucent overlay and a centered banner during requests.\n"
        "Useful when the user shouldn't be interacting with stale content\n"
        "while the server is busy.")
        .def(heap_init<Wt::WOverlayLoadingIndicator>(),
             "Construct the overlay-style indicator.");

    // Shows OS-level notifications (the same kind that a website asks
    // permission for). Requires user permission via Permission.Grant
    // requested upfront. See WApplication.requestPermission to drive that.

    nb::enum_<Wt::WNotification::Permission>(m, "NotificationPermission",
        "User-granted permission state for the browser Notification API.")
        .value("Default", Wt::WNotification::Permission::Default,
               "Permission not yet requested or decided.")
        .value("Granted", Wt::WNotification::Permission::Granted,
               "User allowed notifications — `send` will work.")
        .value("Denied",  Wt::WNotification::Permission::Denied,
               "User denied notifications — `send` will silently fail and\n"
               "`error` will fire.");

    nb::class_<Wt::WNotification, Wt::WObject>(m, "WNotification",
        "Browser Notification API wrapper — produces native OS-level\n"
        "notifications (the toasts the operating system displays outside\n"
        "the page). Inherits WObject, not a widget, so it's not added to\n"
        "a container.\n"
        "\n"
        "    note = wt.WNotification('Build done', 'All tests passed.')\n"
        "    note.set_icon(wt.WLink('/static/check.png'))\n"
        "    note.clicked.connect(focus_app)\n"
        "    note.send()\n"
        "\n"
        "The browser must have granted notification permission first;\n"
        "without it `send` fails silently and `error` fires.")
        .def(heap_init<Wt::WNotification, const Wt::WString&, const Wt::WString&>(),
             "title"_a = Wt::WString(), "body"_a = Wt::WString(),
             "Construct a notification with optional title and body. Both\n"
             "can be set later via set_title / set_body.")
        .def("set_title", &Wt::WNotification::setTitle, "title"_a,
             "Set the notification's heading line.")
        .def("set_body", &Wt::WNotification::setBody, "body"_a,
             "Set the notification's body text.")
        .def("set_icon", &Wt::WNotification::setIcon, "icon_link"_a,
             "Set the small icon shown in the notification (WLink to an\n"
             "image URL or resource).")
        .def("set_badge", &Wt::WNotification::setBadge, "badge_link"_a,
             "Set the badge image — used on some platforms when the full\n"
             "notification can't be shown (e.g. lock screens).")
        .def_prop_rw("silent",
            &Wt::WNotification::silent,
            [](Wt::WNotification& self, bool silent) {
                self.setSilent(silent);
            },
            "When True, the OS suppresses the usual notification sound.")
        .def_prop_rw("require_interaction",
            &Wt::WNotification::requireInteraction,
            [](Wt::WNotification& self, bool require) {
                self.setRequireInteraction(require);
            },
            "When True, the notification stays on screen until the user\n"
            "dismisses it instead of auto-fading.")
        .def("send", &Wt::WNotification::send,
             "Push the notification to the browser. Permission must be "
             "already granted.")
        .def("close", &Wt::WNotification::close,
             "Dismiss the notification programmatically.")
        .def_prop_ro("clicked", &Wt::WNotification::clicked,
                     nb::rv_policy::reference_internal,
                     "JSignal0 — user clicked on the notification body.")
        .def_prop_ro("closed", &Wt::WNotification::closed,
                     nb::rv_policy::reference_internal,
                     "JSignal0 — fires when the notification is dismissed,\n"
                     "either by the user or via `close`.")
        .def_prop_ro("shown", &Wt::WNotification::shown,
                     nb::rv_policy::reference_internal,
                     "JSignal0 — fires once the OS has accepted and\n"
                     "displayed the notification.")
        .def_prop_ro("error", &Wt::WNotification::error,
                     nb::rv_policy::reference_internal,
                     "JSignal0 — fires when the OS rejects the show "
                     "request (e.g. permission denied at run time).");
}

}  // namespace witty_for_python
