#include "common.hpp"

#include <Wt/WApplication.h>
#include <Wt/WEnvironment.h>
#include <Wt/WServer.h>

#include <functional>
#include <memory>
#include <string>
#include <vector>

namespace witty_for_python {

void register_server(nb::module_& m) {
    nb::enum_<Wt::EntryPointType>(m, "EntryPointType")
        .value("Application", Wt::EntryPointType::Application)
        .value("WidgetSet", Wt::EntryPointType::WidgetSet)
        .value("StaticResource", Wt::EntryPointType::StaticResource);

    nb::class_<Wt::WServer>(m, "WServer")
        .def(nb::init<>())
        .def(nb::init<const std::string&>(), "application_path"_a)
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
             "argv"_a, "wt_config"_a = std::string())
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
                     return nb::cast<std::unique_ptr<Wt::WApplication>>(
                         std::move(result));
                 };
                 self.addEntryPoint(type, std::move(wrapped), path, favicon);
             },
             "type"_a, "factory"_a,
             "path"_a = std::string("/"),
             "favicon"_a = std::string())
        .def("start", &Wt::WServer::start)
        .def("stop", &Wt::WServer::stop)
        // run() blocks on the Wt event loop. Release the GIL so the Python
        // factory callbacks (invoked on Wt worker threads) can re-acquire it.
        .def("run", [](Wt::WServer& self) {
            nb::gil_scoped_release release;
            return self.run();
        })
        .def("is_running", &Wt::WServer::isRunning)
        .def_static("wait_for_shutdown", []() {
            nb::gil_scoped_release release;
            return Wt::WServer::waitForShutdown();
        })
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
             "Schedule `function` to run within the session's event loop. "
             "Thread-safe. If the session is gone, `fallback` is called "
             "(if given). Returns immediately.")
        .def("post_all",
             [](Wt::WServer& self, std::function<void()> function) {
                 self.postAll(function);
             },
             "function"_a,
             "Schedule `function` to run within every currently-active "
             "session. Thread-safe.");
}

}  // namespace witty_for_python
