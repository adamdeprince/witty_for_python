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
    nb::class_<Wt::WEnvironment>(m, "WEnvironment",
        "Per-session snapshot of the browser environment Wt captured at\n"
        "WApplication construction time. Read inside your entry-point\n"
        "factory to branch on browser type, initial URL, etc.\n"
        "\n"
        "    def make_app(env):\n"
        "        app = wt.WApplication(env)\n"
        "        if not env.supports_cookies:\n"
        "            app.root.add_widget(wt.WText('Cookies required.'))\n"
        "            return app\n"
        "        ...\n"
        "        return app\n"
        "\n"
        "Read-only after construction. Server-driven changes (the user\n"
        "navigating internally) come through `WApplication.on_internal_\n"
        "path_changed`, not via this object.")
        .def_prop_ro("user_agent", &Wt::WEnvironment::userAgent,
            "Raw `User-Agent` header from the initial request.")
        .def_prop_ro("host_name", &Wt::WEnvironment::hostName,
            "`Host` header from the initial request (no scheme, no port).")
        .def_prop_ro("url_scheme", &Wt::WEnvironment::urlScheme,
            "`'http'` or `'https'`, based on the initial request.")
        .def_prop_ro("internal_path", &Wt::WEnvironment::internalPath,
            "URL fragment / internal path the user arrived at — e.g.\n"
            "`/dashboard/42` for a deep-link. Use this to restore state\n"
            "on first paint; subsequent fragment changes arrive via\n"
            "`WApplication.on_internal_path_changed`.")
        .def_prop_ro("supports_cookies", &Wt::WEnvironment::supportsCookies,
            "True if the browser accepted Wt's probe cookie. False means\n"
            "session state can only survive in the URL — plan accordingly.")
        .def_prop_ro("server_signature", &Wt::WEnvironment::serverSignature,
            "The server name as reported in the Server response header.\n"
            "Cosmetic — only useful for diagnostic banners.");

    nb::class_<Wt::WObject>(m, "WObject",
        "Root of the Wt object hierarchy. Every widget, validator,\n"
        "layout, and resource inherits from this. The Python-facing\n"
        "surface is small — its main purpose is to provide `bind_safe`\n"
        "for safely posting cross-thread callbacks that reference an\n"
        "object that may be destroyed before the callback fires.")
        .def("bind_safe",
            [](const Wt::WObject& self, std::function<void()> fn)
                -> std::function<void()> {
                return self.bindSafe(fn);
            },
            nb::arg("function"),
            "Wrap `function` so it no-ops if this WObject has been\n"
            "destroyed by the time it runs. Canonical use is bridging a\n"
            "background-thread callback back into the UI session via\n"
            "`WServer.post`:\n"
            "\n"
            "    def refresh():\n"
            "        label.text = compute()\n"
            "    server.post(session_id, label.bind_safe(refresh))\n"
            "\n"
            "If `label` is gone (e.g. the user navigated away and the\n"
            "session was cleaned up) by the time post fires, the wrapped\n"
            "call is a no-op instead of a use-after-free.");

    nb::class_<Wt::WWidget, Wt::WObject>(m, "WWidget",
        "Base class for everything that renders into the DOM. Defines\n"
        "the universal widget surface: sizing, visibility, CSS-class\n"
        "manipulation, tooltips, and animated show/hide. Concrete\n"
        "widgets (WText, WPushButton, …) inherit from this via\n"
        "WInteractWidget / WFormWidget / WContainerWidget.")
        .def("set_width", [](Wt::WWidget& w, double px) { w.setWidth(Wt::WLength(px)); },
             "px"_a,
             "Set the widget's CSS width in pixels. Pass a float; Wt\n"
             "converts to a WLength internally. For non-px units, use\n"
             "the WLength constructor directly.")
        .def("set_height", [](Wt::WWidget& w, double px) { w.setHeight(Wt::WLength(px)); },
             "px"_a,
             "Set the widget's CSS height in pixels (companion to\n"
             "`set_width`).")
        .def_prop_rw("hidden",
            [](const Wt::WWidget& w) { return w.isHidden(); },
            [](Wt::WWidget& w, bool h) { w.setHidden(h); },
            "Whether the widget is hidden via CSS `display: none`.\n"
            "Hidden widgets still exist in the DOM and keep their state.\n"
            "For animated transitions use `animate_show` / `animate_hide`.")
        .def("animate_show", &Wt::WWidget::animateShow, "animation"_a,
             "Show the widget with a transition. Pass a WAnimation\n"
             "describing the effect:\n"
             "\n"
             "    panel.animate_show(wt.WAnimation(\n"
             "        wt.AnimationEffect.SlideInFromBottom, 300))")
        .def("animate_hide", &Wt::WWidget::animateHide, "animation"_a,
             "Hide with a transition. Inverse of animate_show; pass the\n"
             "same WAnimation form.")
        .def_prop_rw("style_class",
            [](const Wt::WWidget& w) { return w.styleClass(); },
            [](Wt::WWidget& w, const Wt::WString& s) { w.setStyleClass(s); },
            "The widget's full `class` attribute as a single string.\n"
            "Assigning REPLACES every class — use `add_style_class` /\n"
            "`remove_style_class` to mutate one at a time.")
        .def("add_style_class",
            [](Wt::WWidget& w, const Wt::WString& s) { w.addStyleClass(s); },
            "class_name"_a,
            "Append `class_name` to the widget's `class` attribute if\n"
            "not already present.\n"
            "\n"
            "    container.add_widget(wt.WText('Alert!')).add_style_class('warning')")
        .def("remove_style_class",
            [](Wt::WWidget& w, const Wt::WString& s) { w.removeStyleClass(s); },
            "class_name"_a,
            "Remove `class_name` from the widget's `class` attribute.\n"
            "No-op if it isn't there.")
        .def_prop_rw("id",
            [](const Wt::WWidget& w) { return w.id(); },
            [](Wt::WWidget& w, const std::string& id) { w.setId(id); },
            "The DOM `id` attribute. Wt assigns auto-generated ids by\n"
            "default; setting one is useful for CSS / external JS that\n"
            "needs to target the element by name. Keep ids globally\n"
            "unique in the page.")
        .def_prop_rw("tool_tip",
            [](const Wt::WWidget& w) { return w.toolTip(); },
            [](Wt::WWidget& w, const Wt::WString& s) { w.setToolTip(s); },
            "Hover-tooltip text (sets the DOM `title` attribute).");

    nb::class_<Wt::WInteractWidget, Wt::WWidget>(m, "WInteractWidget",
        "Widget surface for things the user can interact with via mouse\n"
        "or keyboard. Adds the standard input signals to WWidget — every\n"
        "concrete widget that isn't purely decorative inherits from this.\n"
        "\n"
        "    container.add_widget(wt.WText('Click me')).clicked.connect(handler)")
        .def_prop_ro("clicked", &Wt::WInteractWidget::clicked,
                     nb::rv_policy::reference_internal,
                     "Fires on left-button click. Signal payload is a\n"
                     "WMouseEvent (button info, coordinates, modifiers).")
        .def_prop_ro("double_clicked", &Wt::WInteractWidget::doubleClicked,
                     nb::rv_policy::reference_internal,
                     "Fires on left-button double-click (in addition to\n"
                     "two `clicked` events). WMouseEvent payload.")
        .def_prop_ro("mouse_over", &Wt::WInteractWidget::mouseWentOver,
                     nb::rv_policy::reference_internal,
                     "Fires when the cursor enters the widget's bounds.")
        .def_prop_ro("mouse_out", &Wt::WInteractWidget::mouseWentOut,
                     nb::rv_policy::reference_internal,
                     "Fires when the cursor leaves the widget's bounds.")
        .def_prop_ro("key_pressed", &Wt::WInteractWidget::keyPressed,
                     nb::rv_policy::reference_internal,
                     "Fires on each printable-key press while the widget\n"
                     "has focus. WKeyEvent payload. Use `key_went_down`\n"
                     "instead to catch non-printable keys (arrows, F-keys).")
        .def_prop_ro("key_went_down", &Wt::WInteractWidget::keyWentDown,
                     nb::rv_policy::reference_internal,
                     "Fires on every key press (printable AND control).\n"
                     "WKeyEvent payload — check `.key` for the symbolic\n"
                     "name when handling non-printables.")
        .def_prop_ro("enter_pressed", &Wt::WInteractWidget::enterPressed,
                     nb::rv_policy::reference_internal,
                     "Convenience signal that fires when the user presses\n"
                     "Enter while the widget has focus. Typical use is\n"
                     "submit-on-enter on a form input.");

    // WFormWidget binds methods that take/return validator types (`set_validator`,
    // `validator`, `validated`), so the validator family needs to be registered
    // first. Slot it in here rather than from module.cpp so the order is
    // visible at the consuming site.
    register_validators(m);

    nb::class_<Wt::WFormWidget, Wt::WInteractWidget>(m, "WFormWidget",
        "Common surface for HTML form inputs — text fields, checkboxes,\n"
        "selects, etc. Adds the `enabled` flag, focus control, the\n"
        "`changed` signal, and validator wiring on top of WInteractWidget.\n"
        "\n"
        "    edit = container.add_widget(wt.WLineEdit())\n"
        "    edit.set_validator(wt.WRegExpValidator(r'\\d+'))\n"
        "    edit.enabled = False    # render disabled\n"
        "    edit.changed.connect(lambda: log(edit.text))")
        .def_prop_rw("enabled",
            [](const Wt::WFormWidget& w) { return w.isEnabled(); },
            [](Wt::WFormWidget& w, bool e) { w.setEnabled(e); },
            "Whether the input accepts user interaction. Disabled inputs\n"
            "render greyed out and don't fire `changed`.")
        .def("set_focus", nb::overload_cast<>(&Wt::WFormWidget::setFocus),
            "Move keyboard focus to this widget. Effect happens on the\n"
            "next client round-trip.")
        .def_prop_ro("changed", &Wt::WFormWidget::changed,
                     nb::rv_policy::reference_internal,
                     "Fires when the user commits a change (blur for text\n"
                     "fields, toggle for checkboxes, Enter for selects).\n"
                     "Compare with WLineEdit's `text_input` which fires\n"
                     "on every keystroke.")
        .def("set_validator", &Wt::WFormWidget::setValidator, "validator"_a,
            "Attach a validator (WIntValidator, WRegExpValidator, …)\n"
            "that decides whether the current input is acceptable. The\n"
            "validator's verdict surfaces via `validated`.")
        .def_prop_ro("validator", &Wt::WFormWidget::validator,
            "The currently-attached validator (shared_ptr), or None.")
        .def_prop_ro("validated", &Wt::WFormWidget::validated,
                     nb::rv_policy::reference_internal,
                     "Fires after the validator has run, with a WValidator\n"
                     ".Result payload — inspect `.state` for Valid /\n"
                     "InvalidEmpty / Invalid.");

    nb::class_<Wt::WApplication, Wt::WObject>(m, "WApplication",
        "The per-session Wt application instance. One WApplication is\n"
        "constructed per browser session by the factory you pass to\n"
        "WServer.add_entry_point, and lives until that session ends.\n"
        "It owns the page's root container, the URL state, and the\n"
        "server→client update channel.\n"
        "\n"
        "    def create_app(env):\n"
        "        app = wt.WApplication(env)\n"
        "        app.title = 'Hello'\n"
        "        app.root.add_widget(wt.WText('Welcome.'))\n"
        "        app.root.add_widget(wt.WPushButton('Quit')).clicked.connect(app.quit)\n"
        "        return app\n"
        "\n"
        "    server = wt.WServer()\n"
        "    server.set_server_configuration(sys.argv)\n"
        "    server.add_entry_point(wt.EntryPointType.Application, create_app)\n"
        "    server.run()\n"
        "\n"
        "Inside a session, `WApplication.instance()` returns the current\n"
        "WApplication on any Wt-managed thread — useful for code that\n"
        "doesn't have a direct reference to it.")
        .def(heap_init<Wt::WApplication, const Wt::WEnvironment&>(), "environment"_a,
            "Construct the per-session application from the WEnvironment\n"
            "passed into your factory. The first thing your entry-point\n"
            "factory typically does.")
        .def_prop_ro("root", &Wt::WApplication::root,
                     nb::rv_policy::reference_internal,
                     "The top-level WContainerWidget — start `add_widget`-\n"
                     "ing UI here. Owned by the application; lives as long\n"
                     "as the session does.")
        .def_prop_ro("environment", &Wt::WApplication::environment,
                     nb::rv_policy::reference_internal,
                     "The captured WEnvironment from construction time.\n"
                     "Use for read-only browser/session info.")
        .def_prop_rw("title",
            [](const Wt::WApplication& a) { return a.title(); },
            [](Wt::WApplication& a, const Wt::WString& t) { a.setTitle(t); },
            "The page's `<title>` text. Assigning updates the browser\n"
            "tab on the next round-trip.")
        .def("set_internal_path", &Wt::WApplication::setInternalPath,
             "path"_a, "emit_change"_a = false,
             "Change the URL fragment (the part after `#`) without\n"
             "a full page reload. Pass `emit_change=True` to also fire\n"
             "`on_internal_path_changed` — useful when you want both\n"
             "the URL update AND the route handler to run.")
        .def_prop_ro("internal_path", &Wt::WApplication::internalPath,
            "The current URL fragment / internal path. Mirrors what's\n"
            "shown after the `#` in the browser address bar.")
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
             "Subscribe to URL-fragment changes — browser back/forward,\n"
             "or `set_internal_path(..., emit_change=True)`.\n"
             "\n"
             "    def route(path):\n"
             "        if path == '/about': show_about()\n"
             "        elif path.startswith('/user/'): show_user(path)\n"
             "    app.on_internal_path_changed(route)\n"
             "\n"
             "Returns a Connection — call `.disconnect()` on it to stop\n"
             "receiving.")
        .def_prop_ro("session_id", &Wt::WApplication::sessionId,
            "Opaque per-session string. Pass to `WServer.post` to\n"
            "schedule cross-thread work back into this session.")
        .def("redirect",
            [](Wt::WApplication& a, const std::string& url) { a.redirect(url); },
            "url"_a,
            "Tell the browser to navigate to `url`. Effective on the\n"
            "next round-trip; the current session terminates if `url`\n"
            "leaves the application.")
        .def("quit", nb::overload_cast<>(&Wt::WApplication::quit),
            "End the session cleanly. The page stays loaded but stops\n"
            "talking to the server; the application instance is\n"
            "destroyed shortly after.")
        .def("trigger_update", &Wt::WApplication::triggerUpdate,
             "Force a server-initiated update push to the connected\n"
             "client. Combine with `WServer.post` for cross-thread\n"
             "updates — only effective after `enable_updates(True)`.")
        .def("require",
             [](Wt::WApplication& self, const std::string& url,
                const std::string& symbol) {
                 return self.require(url, symbol);
             },
             "url"_a, "symbol"_a = std::string(),
             "Load an external JavaScript library before the page is\n"
             "rendered. Subsequent `do_javascript` calls are deferred\n"
             "until the library has loaded. Pass `symbol` (e.g. 'jQuery')\n"
             "to skip the load if it's already defined on `window`.\n"
             "Returns True if the library was scheduled to load, False\n"
             "if `symbol` was already present.")
        .def("do_javascript",
             [](Wt::WApplication& self, const std::string& js,
                bool after_loaded) {
                 self.doJavaScript(js, after_loaded);
             },
             "javascript"_a, "after_loaded"_a = true,
             "Send arbitrary JS to the client. With `after_loaded=True`\n"
             "(default), the JS runs after all `require`'d libraries\n"
             "have loaded; with `False`, inline before the DOM finishes.")
        .def("enable_updates",
             [](Wt::WApplication& self, bool enabled) {
                 self.enableUpdates(enabled);
             },
             "enabled"_a = true,
             "Allow server-initiated updates. Without this, mutations\n"
             "from background threads (WTimer, WServer.post) only reach\n"
             "the browser on the next client-initiated round-trip; with\n"
             "it, `trigger_update` pushes them immediately. Enable once\n"
             "during entry-point setup if you do any background work.")
        .def("use_style_sheet",
             [](Wt::WApplication& self, const Wt::WLink& link,
                const std::string& media) {
                 self.useStyleSheet(link, media);
             },
             "link"_a, "media"_a = std::string("all"),
             "Add an external stylesheet. `link` is a WLink (URL string\n"
             "or a WResource); `media` is the CSS media query (default\n"
             "'all'). The `<link>` tag is appended to `<head>`.")
        .def("defer_rendering", &Wt::WApplication::deferRendering,
             "Suspend rendering of the current event response until\n"
             "`resume_rendering` is called. Use when an async operation\n"
             "(HttpClient request, WServer.post background work) must\n"
             "complete before the page can be delivered.")
        .def("resume_rendering", &Wt::WApplication::resumeRendering,
             "Resume rendering after a prior `defer_rendering`. Call\n"
             "from the callback that signals 'we're ready'.")
        .def_static("instance", &Wt::WApplication::instance,
                    nb::rv_policy::reference,
                    "Return the WApplication for the current Wt-managed\n"
                    "thread, or None if not inside a session. Useful for\n"
                    "code that doesn't carry an explicit `app` reference.")
        // The theme is owned via shared_ptr — nanobind keeps the Python
        // WTheme wrapper alive while the application holds a reference.
        .def_prop_rw("theme",
            [](const Wt::WApplication& a) { return a.theme(); },
            [](Wt::WApplication& a, const std::shared_ptr<Wt::WTheme>& t) {
                a.setTheme(t);
            },
            "The active theme (shared_ptr<WTheme>). Set during entry-\n"
            "point setup to change the default look-and-feel:\n"
            "\n"
            "    app.theme = wt.WBootstrap5Theme()");

    nb::class_<Wt::WApplication::UpdateLock>(m, "UpdateLock",
        "RAII lock for cross-thread access to a WApplication. Acquire\n"
        "to mutate widgets from a non-Wt thread without going through\n"
        "WServer.post; release happens automatically when the wrapper\n"
        "is GC'd.\n"
        "\n"
        "    with wt.update_lock(app):\n"
        "        label.text = computed_value\n"
        "        app.trigger_update()\n"
        "\n"
        "`WServer.post` is the recommended path for most cross-thread\n"
        "work — UpdateLock is the lower-level escape hatch. The\n"
        "Pythonic context-manager wrapper is `witty_for_python.update_lock(app)`.")
        .def(nb::init<Wt::WApplication*>(), "application"_a,
             "Acquire the application's update lock. Check `bool(lock)`\n"
             "to confirm — acquisition can fail if the application is\n"
             "being torn down.")
        .def("__bool__", [](const Wt::WApplication::UpdateLock& self) {
            return static_cast<bool>(self);
        },
        "True if the lock was successfully acquired, False if the\n"
        "application is being torn down.");
}

}  // namespace witty_for_python
