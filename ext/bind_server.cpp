#include "common.hpp"

#include <Wt/WApplication.h>
#include <Wt/WEnvironment.h>
#include <Wt/WResource.h>
#include <Wt/WServer.h>

#include <functional>
#include <memory>
#include <string>
#include <vector>

namespace witty_for_python {

void register_server(nb::module_& m) {
    nb::enum_<Wt::EntryPointType>(m, "EntryPointType",
        "Selects the deployment mode for an entry point added via\n"
        "`WServer.add_entry_point`. `Application` is the standard mode —\n"
        "Wt owns the page and renders into it. `WidgetSet` embeds Wt\n"
        "widgets into an existing host page that Wt does not own.\n"
        "`StaticResource` serves a single resource (file/blob) without\n"
        "spinning up a session.")
        .value("Application", Wt::EntryPointType::Application)
        .value("WidgetSet", Wt::EntryPointType::WidgetSet)
        .value("StaticResource", Wt::EntryPointType::StaticResource);

    nb::class_<Wt::WServer>(m, "WServer",
        "Process-wide HTTP server hosting one or more Wt entry points.\n"
        "Construct one, configure it via `set_server_configuration` (which\n"
        "parses options out of argv — docroot, listen address, port, …),\n"
        "register entry points with `add_entry_point`, then call `run` to\n"
        "enter the event loop.\n"
        "\n"
        "    def create_app(env):\n"
        "        app = wt.WApplication(env)\n"
        "        app.root.add_widget(wt.WText('Hello.'))\n"
        "        return app\n"
        "\n"
        "    server = wt.WServer()\n"
        "    server.set_server_configuration(sys.argv)\n"
        "    server.add_entry_point(wt.EntryPointType.Application, create_app)\n"
        "    server.run()\n"
        "\n"
        "`post(session_id, fn)` and `post_all(fn)` are the recommended\n"
        "way to push work from a background thread into a Wt session's\n"
        "event loop — Wt acquires the session's update lock around `fn`,\n"
        "so widget mutations inside it are safe. Combine with\n"
        "`WObject.bind_safe` to make the callback no-op if its target\n"
        "widget has been destroyed in the meantime.")
        .def(nb::init<>(),
             "Construct a server with no configuration. Call\n"
             "`set_server_configuration` and `add_entry_point` before\n"
             "`run`.")
        .def(nb::init<const std::string&>(), "application_path"_a,
             "Construct a server tagged with `application_path` — used by\n"
             "Wt's logging to identify which app this server hosts.")
        // argv typically comes from sys.argv. Wt parses options (docroot,
        // http-address, http-port, …) at this point; the argv buffers do not
        // need to outlive the call.
        .def("set_server_configuration",
             [](Wt::WServer& self, std::vector<std::string> argv,
                const std::string& wt_config) {
                 std::vector<char*> c_argv;
                 c_argv.reserve(argv.size());
                 for (auto& s : argv) c_argv.push_back(s.data());
                 self.setServerConfiguration(
                     static_cast<int>(c_argv.size()),
                     c_argv.data(),
                     wt_config);
             },
             "argv"_a, "wt_config"_a = std::string(),
             "Parse Wt's standard command-line options out of `argv` (the\n"
             "same flags `wthttpd` accepts: --docroot, --http-address,\n"
             "--http-port, etc.). Pass `sys.argv` directly. `wt_config`\n"
             "optionally points at a wt_config.xml; empty for defaults.")
        // factory is a Python callable taking WEnvironment and returning a
        // WApplication. We can't use std::function<unique_ptr<WApplication>(
        // const WEnvironment&)> because nanobind's std::function caster
        // converts the env via `infer_policy` for lvalue references, which
        // resolves to `rv_policy::copy` — and WEnvironment is non-copyable.
        // Bind the Python callable directly and do the conversions ourselves
        // so we can pin the env to `rv_policy::reference`.
        .def("add_entry_point",
             [](Wt::WServer& self,
                Wt::EntryPointType type,
                nb::object factory,
                const std::string& path,
                const std::string& favicon) {
                 auto wrapped = [factory_obj = std::move(factory)](
                     const Wt::WEnvironment& env)
                     -> std::unique_ptr<Wt::WApplication> {
                     nb::gil_scoped_acquire gil;
                     nb::object env_py = nb::cast(env, nb::rv_policy::reference);
                     nb::object result = factory_obj(env_py);
                     // Take the unique_ptr (this relinquishes the Python
                     // wrapper into state_relinquished), then re-arm
                     // the wrapper as a non-owning alias. Without the
                     // re-arm, any later access to the original `app`
                     // reference — e.g. a closure inside create_app
                     // calling `app.trigger_update()` from a WTimer
                     // slot — would raise on the wrapper's relinquished
                     // state. Same pattern as add_widget / add_marker
                     // (see docs/binding_design.md §4.2).
                     auto ptr = nb::cast<std::unique_ptr<Wt::WApplication>>(
                         result);
                     nb::inst_set_state(result, /*ready*/ true,
                                        /*destruct*/ false);
                     return ptr;
                 };
                 self.addEntryPoint(type, std::move(wrapped), path, favicon);
             },
             "type"_a, "factory"_a,
             "path"_a = std::string("/"),
             "favicon"_a = std::string(),
             "Register a Python callable as the entry point at `path`.\n"
             "Each new browser session triggers `factory(env)` on a Wt\n"
             "worker thread; return the per-session WApplication.\n"
             "`favicon` optionally overrides the default /favicon.ico.\n"
             "\n"
             "    def create_app(env):\n"
             "        app = wt.WApplication(env)\n"
             "        app.root.add_widget(wt.WText('Hello.'))\n"
             "        return app\n"
             "    server.add_entry_point(wt.EntryPointType.Application,\n"
             "                           create_app)")
        // Mount a WResource at a URL path. The resource serves the same
        // bytes to every client; it has no session state. Useful for
        // small HTTP endpoints alongside the widget UI (a `curl`able
        // JSON state-dump, a generated PDF, etc.). nanobind's
        // shared_ptr from_python wraps the Python wrapper so the
        // resource lives as long as the server keeps it.
        .def("add_resource",
             [](Wt::WServer& self,
                std::shared_ptr<Wt::WResource> resource,
                const std::string& path) {
                 self.addResource(resource, path);
             },
             "resource"_a, "path"_a,
             "Mount `resource` at the given URL path on this server. "
             "The path is process-wide (independent of any session). "
             "Returns nothing; clients fetch via "
             "`http://<server>/<path>`.")
        .def("start", &Wt::WServer::start,
             "Start listening without blocking. Returns immediately —\n"
             "use `wait_for_shutdown` or your own signal loop afterwards.\n"
             "For the simple case, prefer `run` which does both.")
        .def("stop", &Wt::WServer::stop,
             "Stop accepting new connections and tear down existing\n"
             "sessions cleanly. Counterpart to `start`.")
        // run() blocks on the Wt event loop. Release the GIL so the Python
        // factory callbacks (invoked on Wt worker threads) can re-acquire it.
        .def("run", [](Wt::WServer& self) {
            nb::gil_scoped_release release;
            return self.run();
        },
            "Start the server and block until shutdown is requested.\n"
            "Releases the GIL while inside the event loop so Python\n"
            "factory callbacks fired on Wt worker threads can re-acquire\n"
            "it. Returns the exit code (0 on clean shutdown).")
        .def("is_running", &Wt::WServer::isRunning,
             "True iff the server is currently accepting requests.")
        .def_static("wait_for_shutdown", []() {
            nb::gil_scoped_release release;
            return Wt::WServer::waitForShutdown();
        },
            "Block the calling thread until a shutdown signal arrives\n"
            "(SIGINT / SIGTERM). Pair with `start` for non-blocking\n"
            "startup, or use `run` to combine both in one call.")
        // post() and post_all() let other threads schedule work into a Wt
        // session's event loop. Wt acquires the session's update lock before
        // invoking `function`, so widget mutations inside it are safe. The
        // std::function caster wraps the Python callable so the GIL is taken
        // when Wt fires it on its worker thread.
        .def("post",
             [](Wt::WServer& self,
                const std::string& session_id,
                std::function<void()> function,
                std::function<void()> fallback) {
                 self.post(session_id, function, fallback);
             },
             "session_id"_a, "function"_a,
             "fallback"_a = std::function<void()>(),
             "Schedule `function` to run inside the given session's event\n"
             "loop, with the session's update lock held — making widget\n"
             "mutations safe. This is the recommended cross-thread path\n"
             "for pushing updates from a background worker.\n"
             "\n"
             "    def refresh():\n"
             "        label.text = compute()\n"
             "        app.trigger_update()\n"
             "    server.post(session_id, label.bind_safe(refresh))\n"
             "\n"
             "Wrap the callback with `WObject.bind_safe` so it no-ops if\n"
             "the target widget has been destroyed before the post fires.\n"
             "If the session is gone entirely, `fallback` is called (if\n"
             "given). Returns immediately; thread-safe.")
        .def("post_all",
             [](Wt::WServer& self, std::function<void()> function) {
                 self.postAll(function);
             },
             "function"_a,
             "Schedule `function` to run inside every currently-active\n"
             "session, each with its own update lock held. Thread-safe.\n"
             "Useful for broadcast-style updates (e.g. 'system going down\n"
             "in 5 minutes').");
}

}  // namespace witty_for_python
