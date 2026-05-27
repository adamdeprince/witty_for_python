#include "common.hpp"
#include "signal_helpers.hpp"

#include <Wt/WLink.h>

NB_MODULE(_witty_for_python, m) {
    m.doc() = "Python bindings for the Wt (Web Toolkit) C++ library.";

    // Order matters: base classes (WObject -> WWidget -> WInteractWidget ->
    // WFormWidget / WContainerWidget) must be registered before their
    // derived classes are referenced.
    witty_for_python::register_signals(m);
    // register_application invokes register_validators internally between
    // WInteractWidget and WFormWidget (which needs the validator types).
    witty_for_python::register_application(m);
    // register_resource binds WLink (which depends only on WObject, and
    // wants WResource present so its `shared_ptr<WResource>` implicit
    // constructor can be registered). Everything that uses WLink as a
    // parameter (WAnchor, WImage, …) must come *after* this call.
    witty_for_python::register_resource(m);
    witty_for_python::register_container(m);
    witty_for_python::register_widgets(m);
    witty_for_python::register_form(m);
    // Date/time widgets (WDateEdit, WTimeEdit) extend WLineEdit, so they
    // need bind_widgets registered first.
    witty_for_python::register_datetime(m);
    witty_for_python::register_template(m);
    witty_for_python::register_navigation(m);
    witty_for_python::register_table(m);
    witty_for_python::register_layout(m);
    witty_for_python::register_server(m);
    // Theme classes (WCssTheme, WBootstrap5Theme) — depend only on WObject.
    witty_for_python::register_themes(m);
    // WTimer — depends on WObject + the MouseEventSignal binding from
    // register_signals (timeout returns EventSignal<WMouseEvent>).
    witty_for_python::register_timer(m);
    // WFileUpload — depends on WWidget (so register_application).
    witty_for_python::register_upload(m);
    // Model/view subsystem. Runs BEFORE register_extra_form because
    // WSuggestionPopup.set_model takes a shared_ptr<WAbstractItemModel>,
    // and that base class is bound here.
    witty_for_python::register_modelview(m);
    // Proxy models (sort/filter, identity, read-only) sit on top of the
    // model/view base classes registered above.
    witty_for_python::register_modelview_proxy(m);
    // Value types (WLength, WAnimation) — referenced as parameters by
    // many other bindings, but as value types they only need to be
    // registered before code that *uses* them as parameter casters at
    // call time. Placing them here keeps the file organisation tidy.
    witty_for_python::register_value_types(m);
    // Event payloads (WDropEvent, WTouchEvent, WGestureEvent,
    // WScrollEvent + Touch). Standalone value-type bindings — needed
    // when a future binding routes these as signal payloads.
    witty_for_python::register_event_payloads(m);
    // Misc UI widgets (WIcon, WIconPair, WPopupWidget, WNotification,
    // WLoadingIndicator family). WIcon extends WInteractWidget; others
    // are WCompositeWidget descendants bound as WWidget.
    witty_for_python::register_misc_ui(m);
    // Layouts we missed in the first pass (WBorderLayout, WFitLayout).
    witty_for_python::register_layouts_extra(m);
    // Extra form widgets — most extend WLineEdit / WTextArea /
    // WFormWidget, so they need register_form already run.
    witty_for_python::register_extra_form(m);
    // WFileDropWidget + the File* signal types — depends on
    // WContainerWidget (register_container) and on UploadedFile being
    // bound (register_upload, since the File class returns it).
    witty_for_python::register_filedrop(m);
    // Navigation chrome (WPopupMenu, WNavigationBar, WToolBar, WBadge,
    // WSplitButton) — depends on WMenu, WTemplate, WText, WPushButton,
    // which are all registered above.
    witty_for_python::register_chrome(m);

    // Module-level helpers used by the Python atexit handler in
    // witty_for_python/__init__.py to drop every Python-callable connection before
    // nanobind's shutdown-time leak detector runs.
    m.def("_cleanup_all_connections",
          &witty_for_python::connection_registry_disconnect_all_signals,
          "Disconnect every Python-callable slot opened through witty_for_python. "
          "Idempotent. Called automatically at interpreter exit.");
    m.def("_live_connection_count",
          &witty_for_python::connection_registry_size,
          "Count of Python-callable connections currently held by witty_for_python.");

    // Round-trip helper for tests. Takes anything that converts to WLink and
    // returns the URL string. Used to verify str→WLink implicit conversion
    // without needing a WApplication context.
    m.def("_link_url",
          [](const Wt::WLink& l) { return l.url(); },
          nb::arg("link"),
          "Return the URL of a WLink (str auto-converts via nb::init_implicit).");

    // datetime caster round-trip helpers — also used by tests to verify the
    // WDate / WTime / WDateTime casters without setting up a WApplication.
    m.def("_round_trip_date",
          [](const Wt::WDate& d) { return d; }, nb::arg("date"));
    m.def("_round_trip_time",
          [](const Wt::WTime& t) { return t; }, nb::arg("time"));
    m.def("_round_trip_datetime",
          [](const Wt::WDateTime& dt) { return dt; }, nb::arg("dt"));
}
