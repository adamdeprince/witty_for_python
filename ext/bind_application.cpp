#include "common.hpp"

#include <Wt/WObject.h>
#include <Wt/WWidget.h>
#include <Wt/WInteractWidget.h>
#include <Wt/WFormWidget.h>
#include <Wt/WApplication.h>
#include <Wt/WEnvironment.h>
#include <Wt/WContainerWidget.h>
#include <Wt/WLength.h>

namespace pywitty {

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

    nb::class_<Wt::WFormWidget, Wt::WInteractWidget>(m, "WFormWidget")
        .def_prop_rw("enabled",
            [](const Wt::WFormWidget& w) { return w.isEnabled(); },
            [](Wt::WFormWidget& w, bool e) { w.setEnabled(e); })
        .def("set_focus", nb::overload_cast<>(&Wt::WFormWidget::setFocus))
        .def_prop_ro("changed", &Wt::WFormWidget::changed,
                     nb::rv_policy::reference_internal);

    nb::class_<Wt::WApplication, Wt::WObject>(m, "WApplication")
        .def(nb::init<const Wt::WEnvironment&>(), "environment"_a)
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
        .def_prop_ro("session_id", &Wt::WApplication::sessionId)
        .def("redirect",
            [](Wt::WApplication& a, const std::string& url) { a.redirect(url); })
        .def("quit", nb::overload_cast<>(&Wt::WApplication::quit))
        .def("trigger_update", &Wt::WApplication::triggerUpdate,
             "Force a server-initiated update push to the connected client. "
             "Combine with WServer.post() for cross-thread updates.")
        .def_static("instance", &Wt::WApplication::instance,
                    nb::rv_policy::reference);

    // Cross-thread: hold this lock for exclusive access to an app from a
    // thread other than its session's worker thread. RAII — release happens
    // when the Python wrapper is GC'd. Use `pywitty.update_lock(app)` for the
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

}  // namespace pywitty
