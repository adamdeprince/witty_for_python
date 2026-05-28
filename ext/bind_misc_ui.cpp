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

    nb::class_<Wt::JSignal<>>(m, "JSignal0")
        .def("connect",
            [](Wt::JSignal<>& s, nb::callable cb) {
                return py_connect<Wt::JSignal<>>(s, std::move(cb));
            }, "callable"_a)
        .def("disconnect_all_slots",
            [](Wt::JSignal<>& s) {
                connection_registry_disconnect_all(&s);
            });

    // ---- WIcon: a Font-Awesome-backed icon widget ----
    //
    // Inherits WInteractWidget so `clicked` and friends already work. Pass
    // a name like "play", "envelope" — Wt looks it up in the bundled
    // Font Awesome stylesheet (loaded on first use via `load_icon_font`).

    nb::class_<Wt::WIcon, Wt::WInteractWidget>(m, "WIcon")
        .def(heap_init<Wt::WIcon>())
        .def(heap_init<Wt::WIcon, const std::string&>(), "name"_a,
             "Construct with a Font Awesome icon name (e.g. 'play', 'gear').")
        .def_prop_rw("name",
            [](const Wt::WIcon& self) { return self.name(); },
            [](Wt::WIcon& self, const std::string& n) { self.setName(n); })
        .def_prop_rw("size",
            &Wt::WIcon::size,
            &Wt::WIcon::setSize,
            "Multiplier on the default icon size. 1.0 = unchanged; 2.0 = "
            "doubled.")
        .def_static("load_icon_font", &Wt::WIcon::loadIconFont,
            "Add Font Awesome's CSS stylesheet to the application. Called "
            "automatically the first time a WIcon is constructed; expose "
            "it here for explicit early-load.");

    // ---- WIconPair: a togglable two-icon widget ----

    nb::enum_<Wt::WIconPair::IconType>(m, "IconType")
        .value("URI", Wt::WIconPair::IconType::URI)
        .value("IconName", Wt::WIconPair::IconType::IconName);

    nb::class_<Wt::WIconPair, Wt::WWidget>(m, "WIconPair")
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
        .def("show_icon2", &Wt::WIconPair::showIcon2)
        .def("set_icon1_type", &Wt::WIconPair::setIcon1Type, "type"_a)
        .def("set_icon2_type", &Wt::WIconPair::setIcon2Type, "type"_a)
        .def("set_icons_type", &Wt::WIconPair::setIconsType, "type"_a,
             "Shortcut for setting both icons to the same IconType.")
        .def_prop_ro("icon1_clicked", &Wt::WIconPair::icon1Clicked,
                     nb::rv_policy::reference_internal,
                     "MouseEventSignal — clicks while icon1 is visible.")
        .def_prop_ro("icon2_clicked", &Wt::WIconPair::icon2Clicked,
                     nb::rv_policy::reference_internal);

    // ---- WPopupWidget: generic floating overlay ----
    //
    // Wraps a content widget (passed at construction time, ownership
    // transferred) into a thing that can pop up over the page anchored to
    // another widget. Different from WPopupMenu (which is a menu); use
    // WPopupWidget for arbitrary popup content (tooltips, custom menus,
    // detail panels).
    //
    // Bound as inheriting WWidget per the project convention for
    // WCompositeWidget descendants.

    nb::class_<Wt::WPopupWidget, Wt::WWidget>(m, "WPopupWidget")
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

    // ---- WLoadingIndicator family ----
    //
    // The base is abstract — concrete subclasses (WDefaultLoadingIndicator,
    // WOverlayLoadingIndicator) provide the visible loading UI shown by
    // WApplication during a server round-trip. Plug a custom one in via
    // WApplication.set_loading_indicator (not bound in v1).

    nb::class_<Wt::WLoadingIndicator, Wt::WWidget>(m, "WLoadingIndicator")
        .def("set_message", &Wt::WLoadingIndicator::setMessage, "text"_a,
             "Replace the loading message shown to the user.");

    nb::class_<Wt::WDefaultLoadingIndicator, Wt::WLoadingIndicator>(
        m, "WDefaultLoadingIndicator")
        .def(heap_init<Wt::WDefaultLoadingIndicator>(),
             "Wt's plain-text loading indicator: a small fixed-position "
             "text label.");

    nb::class_<Wt::WOverlayLoadingIndicator, Wt::WLoadingIndicator>(
        m, "WOverlayLoadingIndicator")
        .def(heap_init<Wt::WOverlayLoadingIndicator>(),
             "A more visible loading indicator — dims the page contents "
             "with a translucent overlay during requests.");

    // ---- WNotification: browser-native Notification API wrapper ----
    //
    // Shows OS-level notifications (the same kind that a website asks
    // permission for). Requires user permission via Permission.Grant
    // requested upfront. See WApplication.requestPermission to drive that.

    nb::enum_<Wt::WNotification::Permission>(m, "NotificationPermission")
        .value("Default", Wt::WNotification::Permission::Default)
        .value("Granted", Wt::WNotification::Permission::Granted)
        .value("Denied",  Wt::WNotification::Permission::Denied);

    nb::class_<Wt::WNotification, Wt::WObject>(m, "WNotification")
        .def(heap_init<Wt::WNotification, const Wt::WString&, const Wt::WString&>(),
             "title"_a = Wt::WString(), "body"_a = Wt::WString())
        .def("set_title", &Wt::WNotification::setTitle, "title"_a)
        .def("set_body", &Wt::WNotification::setBody, "body"_a)
        .def("set_icon", &Wt::WNotification::setIcon, "icon_link"_a)
        .def("set_badge", &Wt::WNotification::setBadge, "badge_link"_a)
        .def_prop_rw("silent",
            &Wt::WNotification::silent,
            [](Wt::WNotification& self, bool silent) {
                self.setSilent(silent);
            })
        .def_prop_rw("require_interaction",
            &Wt::WNotification::requireInteraction,
            [](Wt::WNotification& self, bool require) {
                self.setRequireInteraction(require);
            })
        .def("send", &Wt::WNotification::send,
             "Push the notification to the browser. Permission must be "
             "already granted.")
        .def("close", &Wt::WNotification::close,
             "Dismiss the notification programmatically.")
        .def_prop_ro("clicked", &Wt::WNotification::clicked,
                     nb::rv_policy::reference_internal,
                     "JSignal0 — user clicked on the notification body.")
        .def_prop_ro("closed", &Wt::WNotification::closed,
                     nb::rv_policy::reference_internal)
        .def_prop_ro("shown", &Wt::WNotification::shown,
                     nb::rv_policy::reference_internal)
        .def_prop_ro("error", &Wt::WNotification::error,
                     nb::rv_policy::reference_internal,
                     "JSignal0 — fires when the OS rejects the show "
                     "request (e.g. permission denied at run time).");
}

}  // namespace witty_for_python
