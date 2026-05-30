#include "common.hpp"
#include "signal_helpers.hpp"

#include <Wt/WObject.h>
#include <Wt/WWidget.h>
#include <Wt/WInteractWidget.h>
#include <Wt/WFormWidget.h>
#include <Wt/WValidator.h>     // for WFormWidget::setValidator / validator / validated
#include <Wt/WApplication.h>
#include <Wt/WEnvironment.h>
#include <Wt/WContainerWidget.h>
#include <Wt/WLength.h>
#include <Wt/WAnimation.h>     // for WWidget animate_show / animate_hide
#include <Wt/WTheme.h>         // for WApplication.theme property

namespace witty_for_python {

void register_application(nb::module_& m) {
    nb::class_<Wt::WEnvironment>(m, "WEnvironment")
        .def_prop_ro("user_agent", &Wt::WEnvironment::userAgent)
        .def_prop_ro("host_name", &Wt::WEnvironment::hostName)
        .def_prop_ro("url_scheme", &Wt::WEnvironment::urlScheme)
        .def_prop_ro("internal_path", &Wt::WEnvironment::internalPath)
        .def_prop_ro("supports_cookies", &Wt::WEnvironment::supportsCookies)
        .def_prop_ro("server_signature", &Wt::WEnvironment::serverSignature);

    nb::class_<Wt::WObject>(m, "WObject")
        // bind_safe(fn) returns a callable wrapping `fn` that no-ops if this
        // WObject has been destroyed by the time it's invoked. The canonical
        // use is making a cross-thread callback survive its target widget
        // dying out from under it — typically when passed to WServer.post():
        //
        //     safe_update = label.bind_safe(lambda: label.text = "...")
        //     server.post(session_id, safe_update)
        //
        // If `label` is gone when post() fires, safe_update is a no-op.
        // Inherited from Wt::Core::observable; every widget has it.
        .def("bind_safe",
            [](const Wt::WObject& self, std::function<void()> fn)
                -> std::function<void()> {
                return self.bindSafe(fn);
            },
            nb::arg("function"),
            "Wrap `function` to no-op if this WObject is destroyed before "
            "it's invoked. Use for cross-thread callbacks to WServer.post() "
            "that reference widget state.");

    nb::class_<Wt::WWidget, Wt::WObject>(m, "WWidget")
        .def("set_width", [](Wt::WWidget& w, double px) { w.setWidth(Wt::WLength(px)); })
        .def("set_height", [](Wt::WWidget& w, double px) { w.setHeight(Wt::WLength(px)); })
        .def_prop_rw("hidden",
            [](const Wt::WWidget& w) { return w.isHidden(); },
            [](Wt::WWidget& w, bool h) { w.setHidden(h); })
        .def("animate_show", &Wt::WWidget::animateShow, "animation"_a,
             "Show the widget with a transition. Pass a `WAnimation` "
             "describing the slide/fade/timing.")
        .def("animate_hide", &Wt::WWidget::animateHide, "animation"_a,
             "Hide with a transition. Inverse of animate_show.")
        .def_prop_rw("style_class",
            [](const Wt::WWidget& w) { return w.styleClass(); },
            [](Wt::WWidget& w, const Wt::WString& s) { w.setStyleClass(s); })
        .def("add_style_class",
            [](Wt::WWidget& w, const Wt::WString& s) { w.addStyleClass(s); })
        .def("remove_style_class",
            [](Wt::WWidget& w, const Wt::WString& s) { w.removeStyleClass(s); })
        .def_prop_rw("id",
            [](const Wt::WWidget& w) { return w.id(); },
            [](Wt::WWidget& w, const std::string& id) { w.setId(id); })
        .def_prop_rw("tool_tip",
            [](const Wt::WWidget& w) { return w.toolTip(); },
            [](Wt::WWidget& w, const Wt::WString& s) { w.setToolTip(s); });

    nb::class_<Wt::WInteractWidget, Wt::WWidget>(m, "WInteractWidget")
        .def_prop_ro("clicked", &Wt::WInteractWidget::clicked,
                     nb::rv_policy::reference_internal)
        .def_prop_ro("double_clicked", &Wt::WInteractWidget::doubleClicked,
                     nb::rv_policy::reference_internal)
        .def_prop_ro("mouse_over", &Wt::WInteractWidget::mouseWentOver,
                     nb::rv_policy::reference_internal)
        .def_prop_ro("mouse_out", &Wt::WInteractWidget::mouseWentOut,
                     nb::rv_policy::reference_internal)
        .def_prop_ro("key_pressed", &Wt::WInteractWidget::keyPressed,
                     nb::rv_policy::reference_internal)
        .def_prop_ro("key_went_down", &Wt::WInteractWidget::keyWentDown,
                     nb::rv_policy::reference_internal)
        .def_prop_ro("enter_pressed", &Wt::WInteractWidget::enterPressed,
                     nb::rv_policy::reference_internal);

    // WFormWidget binds methods that take/return validator types (`set_validator`,
    // `validator`, `validated`), so the validator family needs to be registered
    // first. Slot it in here rather than from module.cpp so the order is
    // visible at the consuming site.
    register_validators(m);

    nb::class_<Wt::WFormWidget, Wt::WInteractWidget>(m, "WFormWidget")
        .def_prop_rw("enabled",
            [](const Wt::WFormWidget& w) { return w.isEnabled(); },
            [](Wt::WFormWidget& w, bool e) { w.setEnabled(e); })
        .def("set_focus", nb::overload_cast<>(&Wt::WFormWidget::setFocus))
        .def_prop_ro("changed", &Wt::WFormWidget::changed,
                     nb::rv_policy::reference_internal)
        // Validation wiring — types registered above by register_validators(m).
        .def("set_validator", &Wt::WFormWidget::setValidator, "validator"_a)
        .def_prop_ro("validator", &Wt::WFormWidget::validator)
        .def_prop_ro("validated", &Wt::WFormWidget::validated,
                     nb::rv_policy::reference_internal);

    nb::class_<Wt::WApplication, Wt::WObject>(m, "WApplication")
        .def(heap_init<Wt::WApplication, const Wt::WEnvironment&>(), "environment"_a)
        .def_prop_ro("root", &Wt::WApplication::root,
                     nb::rv_policy::reference_internal)
        .def_prop_ro("environment", &Wt::WApplication::environment,
                     nb::rv_policy::reference_internal)
        .def_prop_rw("title",
            [](const Wt::WApplication& a) { return a.title(); },
            [](Wt::WApplication& a, const Wt::WString& t) { a.setTitle(t); })
        .def("set_internal_path", &Wt::WApplication::setInternalPath,
             "path"_a, "emit_change"_a = false)
        .def_prop_ro("internal_path", &Wt::WApplication::internalPath)
        // `internal_path_changed` is a Wt::Signal<std::string>, not the
        // Signal<WString> we expose as `StringSignal`. Rather than bind
        // a second similarly-named Signal class, route connect through
        // the existing py_connect machinery via this thin shim — same
        // pattern as HttpClient.on_body_data_received.
        .def("on_internal_path_changed",
             [](Wt::WApplication& self, nb::callable cb) {
                 return py_connect<Wt::Signal<std::string>, std::string>(
                     self.internalPathChanged(), std::move(cb));
             },
             "callback"_a,
             "Connect `callback(path: str)` to fire when the URL "
             "fragment changes (browser back/forward, set_internal_path "
             "with emit_change=True). Returns a Connection.")
        .def_prop_ro("session_id", &Wt::WApplication::sessionId)
        .def("redirect",
            [](Wt::WApplication& a, const std::string& url) { a.redirect(url); })
        .def("quit", nb::overload_cast<>(&Wt::WApplication::quit))
        .def("trigger_update", &Wt::WApplication::triggerUpdate,
             "Force a server-initiated update push to the connected client. "
             "Combine with WServer.post() for cross-thread updates.")
        .def("require",
             [](Wt::WApplication& self, const std::string& url,
                const std::string& symbol) {
                 return self.require(url, symbol);
             },
             "url"_a, "symbol"_a = std::string(),
             "Load an external JavaScript library before the page is "
             "rendered. Subsequent do_javascript() calls are deferred "
             "until the library has loaded. If `symbol` is given, Wt "
             "checks for its existence to avoid loading the library "
             "twice. Returns True if the library was scheduled to "
             "load, False if `symbol` was already defined.")
        .def("do_javascript",
             [](Wt::WApplication& self, const std::string& js,
                bool after_loaded) {
                 self.doJavaScript(js, after_loaded);
             },
             "javascript"_a, "after_loaded"_a = true,
             "Send arbitrary JS to the client. If `after_loaded` is "
             "True (default) the JS runs after all require()'d "
             "libraries have loaded; False makes it run inline before "
             "the DOM finishes.")
        .def("enable_updates",
             [](Wt::WApplication& self, bool enabled) {
                 self.enableUpdates(enabled);
             },
             "enabled"_a = true,
             "Allow server-initiated updates: changes made to widgets "
             "from a worker thread (WTimer, WServer.post) are pushed "
             "to the connected client. Without this, server-side "
             "widget mutations only reach the browser on the next "
             "client-initiated round-trip.")
        .def("use_style_sheet",
             [](Wt::WApplication& self, const Wt::WLink& link,
                const std::string& media) {
                 self.useStyleSheet(link, media);
             },
             "link"_a, "media"_a = std::string("all"),
             "Add an external stylesheet. `link` is a WLink (URL string or "
             "a WResource handle, e.g. one mounted via WServer.add_resource). "
             "`media` is the CSS media query (default 'all'). The link tag "
             "is added to the page's <head>.")
        .def("defer_rendering", &Wt::WApplication::deferRendering,
             "Suspend rendering of the current event response until "
             "resume_rendering() is called. Use this when an async "
             "operation (HttpClient request, WServer.post background "
             "work) must complete before the page can be delivered.")
        .def("resume_rendering", &Wt::WApplication::resumeRendering,
             "Resume rendering after a previous defer_rendering(). Call "
             "this from the callback that signals 'we are ready'.")
        .def_static("instance", &Wt::WApplication::instance,
                    nb::rv_policy::reference)
        // The theme is owned via shared_ptr — nanobind keeps the Python
        // WTheme wrapper alive while the application holds a reference.
        .def_prop_rw("theme",
            [](const Wt::WApplication& a) { return a.theme(); },
            [](Wt::WApplication& a, const std::shared_ptr<Wt::WTheme>& t) {
                a.setTheme(t);
            });

    // Cross-thread: hold this lock for exclusive access to an app from a
    // thread other than its session's worker thread. RAII — release happens
    // when the Python wrapper is GC'd. Use `witty_for_python.update_lock(app)` for the
    // Pythonic context-manager form. WServer.post() is the recommended path
    // for most cross-thread work; UpdateLock is the lower-level escape hatch.
    nb::class_<Wt::WApplication::UpdateLock>(m, "UpdateLock")
        .def(nb::init<Wt::WApplication*>(), "application"_a,
             "Acquire the application's update lock. Use bool(lock) to "
             "check success — it may fail if the application is being torn "
             "down.")
        .def("__bool__", [](const Wt::WApplication::UpdateLock& self) {
            return static_cast<bool>(self);
        });
}

}  // namespace witty_for_python
