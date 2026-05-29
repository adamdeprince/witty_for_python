#include "common.hpp"

#include <nanobind/stl/map.h>
#include <nanobind/stl/optional.h>

#include <Wt/Http/Request.h>
#include <Wt/Http/Response.h>
#include <Wt/WFileResource.h>
#include <Wt/WLink.h>
#include <Wt/WMemoryResource.h>
#include <Wt/WResource.h>
#include <Wt/WStreamResource.h>

#include <memory>
#include <ostream>
#include <sstream>
#include <string>
#include <vector>

namespace witty_for_python {

namespace {

// Concrete WResource that delegates to a Python callable. We chose a
// callback-style binding over a trampoline+subclass for the same reason
// most Python libraries reach for `server.add(callback)` instead of
// `class MyHandler(Handler): def handle(self, ...)`: callbacks are
// easier to write (no class boilerplate), easier to compose (closures
// capture state directly, multiple endpoints = multiple functions),
// and easier to test (call the function directly).
//
// Wt invokes `handleRequest` from a worker thread without holding the
// GIL; we acquire it before calling the Python callable and pass
// request + response as non-owning references (they live on Wt's
// stack and are invalid after the call returns).
class CallbackResource : public Wt::WResource {
public:
    explicit CallbackResource(nb::callable cb) : cb_(std::move(cb)) {
        // suggestFileName / disposition / etc. stay at WResource
        // defaults; users can mutate them through the inherited
        // WResource surface if they need to.
    }

    ~CallbackResource() override {
        // Required by every WResource subclass to flush in-flight
        // continuations before destruction.
        beingDeleted();
    }

    void handleRequest(const Wt::Http::Request& request,
                       Wt::Http::Response& response) override {
        nb::gil_scoped_acquire gil;
        try {
            cb_(nb::cast(request,  nb::rv_policy::reference),
                nb::cast(response, nb::rv_policy::reference));
        } catch (const nb::python_error& e) {
            // Don't let a Python exception unwind through Wt's C++
            // worker — surface it to Python via the unraisable hook
            // and let Wt return whatever it had already written.
            PyErr_SetString(e.type().ptr(), e.what());
            PyErr_WriteUnraisable(cb_.ptr());
        }
    }

private:
    nb::callable cb_;
};

}  // namespace

void register_resource(nb::module_& m) {
    // ---- ContentDisposition enum ----

    nb::enum_<Wt::ContentDisposition>(m, "ContentDisposition")
        .value("None_", Wt::ContentDisposition::None)
        .value("Attachment", Wt::ContentDisposition::Attachment)
        .value("Inline", Wt::ContentDisposition::Inline);

    // Wt nests Request / Response / Message / Client / Method under a
    // single `Wt::Http::` namespace. Mirror that as `witty_for_python.Http`
    // — same pattern as `wt.Json` and `wt.chart`. Names inside the
    // submodule match Wt 1:1, so Wt's C++ docs apply directly. This
    // submodule is created here (in register_resource) because the
    // server-side Request/Response are bound first; the client-side
    // Message/Client are added inside the same submodule by
    // register_http_client later.
    nb::module_ http = m.def_submodule("Http",
        "Wt::Http — HTTP types shared by WResource handlers (Request, "
        "Response) and the outbound client (Message, Client, Method, "
        "Header).");

    // ---- Wt::Http::Request: read-only view of an HTTP request ----
    //
    // Lifetime: valid only for the duration of WResource.handle_request.
    // The wrapper points at a stack-local C++ Request on the Wt worker
    // thread; do not store it past the call.

    nb::class_<Wt::Http::Request>(http, "Request")
        .def_prop_ro("method", &Wt::Http::Request::method,
                     "HTTP method as a string ('GET', 'POST', 'PUT', ...).")
        .def_prop_ro("path", &Wt::Http::Request::path,
                     "The deploy path at which this request was received.")
        .def_prop_ro("path_info", &Wt::Http::Request::pathInfo,
                     "Additional path info beyond the deploy path.")
        .def_prop_ro("query_string", &Wt::Http::Request::queryString)
        .def_prop_ro("url_scheme", &Wt::Http::Request::urlScheme)
        .def_prop_ro("content_type", &Wt::Http::Request::contentType)
        .def_prop_ro("content_length", &Wt::Http::Request::contentLength)
        .def_prop_ro("user_agent", &Wt::Http::Request::userAgent)
        .def_prop_ro("client_address", &Wt::Http::Request::clientAddress)
        .def_prop_ro("host_name", &Wt::Http::Request::hostName)
        .def_prop_ro("server_name", &Wt::Http::Request::serverName)
        .def_prop_ro("server_port", &Wt::Http::Request::serverPort)
        .def("get_parameter",
             [](const Wt::Http::Request& r, const std::string& name)
                 -> std::optional<std::string> {
                 const std::string* v = r.getParameter(name);
                 if (!v) return std::nullopt;
                 return *v;
             },
             "name"_a,
             "First value for query/POST parameter `name`, or None.")
        .def("get_parameter_values",
             [](const Wt::Http::Request& r, const std::string& name) {
                 return r.getParameterValues(name);
             },
             "name"_a,
             "All values for a parameter (e.g. `?n=a&n=b` → ['a','b']).")
        .def_prop_ro("parameters",
             [](const Wt::Http::Request& r) {
                 return r.getParameterMap();
             },
             "All query/POST parameters as a dict[str, list[str]].")
        .def("header_value", &Wt::Http::Request::headerValue,
             "field"_a,
             "Header value (empty string if absent).")
        .def("cookie_value",
             [](const Wt::Http::Request& r, const std::string& name)
                 -> std::optional<std::string> {
                 const std::string* v = r.getCookieValue(name);
                 if (!v) return std::nullopt;
                 return *v;
             },
             "name"_a,
             "Cookie value, or None if absent.")
        .def_prop_ro("cookies",
             [](const Wt::Http::Request& r) { return r.cookies(); },
             "All cookies as a dict[str, str].")
        .def("body",
             [](const Wt::Http::Request& r) -> nb::bytes {
                 std::istream& in = r.in();
                 std::ostringstream oss;
                 oss << in.rdbuf();
                 std::string s = oss.str();
                 return nb::bytes(s.data(), s.size());
             },
             "Read the entire request body as `bytes`. For "
             "application/x-www-form-urlencoded or multipart/form-data Wt "
             "has already consumed the stream and exposes the values via "
             "`get_parameter` instead.");

    // ---- Wt::Http::Response: write-only response handle ----
    //
    // Headers must be set BEFORE the first write() / set_mime_type;
    // after that point Wt commits headers to the wire and addHeader
    // becomes a no-op.

    nb::class_<Wt::Http::Response>(http, "Response")
        .def("set_status", &Wt::Http::Response::setStatus, "status"_a,
             "Set the HTTP status code (default 200).")
        .def("set_content_length",
             [](Wt::Http::Response& r, std::uint64_t n) {
                 r.setContentLength(n);
             },
             "length"_a)
        .def("set_mime_type", &Wt::Http::Response::setMimeType,
             "mime_type"_a,
             "Set the Content-Type. After this (or any write) headers "
             "are committed.")
        .def("add_header", &Wt::Http::Response::addHeader,
             "name"_a, "value"_a)
        .def("insert_header", &Wt::Http::Response::insertHeader,
             "name"_a, "value"_a,
             "Set an HTTP header, replacing any earlier value with the "
             "same name.")
        .def("write",
             [](Wt::Http::Response& r, nb::bytes data) {
                 r.out().write(
                     reinterpret_cast<const char*>(data.c_str()),
                     static_cast<std::streamsize>(data.size()));
             },
             "data"_a,
             "Write `bytes` to the response body.")
        .def("write",
             [](Wt::Http::Response& r, const std::string& data) {
                 r.out().write(data.data(),
                               static_cast<std::streamsize>(data.size()));
             },
             "data"_a,
             "Write a `str` (UTF-8) to the response body.");

    // ---- WResource (abstract base) ----
    //
    // Concrete subclasses below: WMemoryResource and WFileResource ship
    // their own handle_request. For a dynamic endpoint, use
    // `wt.CallbackResource(callable)` (or wt.callback_resource) below —
    // simpler and more Pythonic than subclassing.

    nb::class_<Wt::WResource, Wt::WObject>(m, "WResource")
        .def("suggest_file_name",
             [](Wt::WResource& r, const Wt::WString& name) {
                 r.suggestFileName(name);
             },
             "name"_a,
             "Set the suggested filename the browser uses when saving the "
             "resource (e.g. 'export.csv').")
        .def("set_disposition_type", &Wt::WResource::setDispositionType,
             "disposition"_a)
        .def("set_changed", &Wt::WResource::setChanged,
             "Invalidate any browser-side cache of this resource so the "
             "next fetch sees the latest data. Call after set_data() etc.")
        .def_prop_rw("internal_path",
            [](const Wt::WResource& r) { return r.internalPath(); },
            [](Wt::WResource& r, const std::string& p) { r.setInternalPath(p); })
        .def("set_invalid_after_changed", &Wt::WResource::setInvalidAfterChanged,
             "enabled"_a)
        .def("set_takes_update_lock", &Wt::WResource::setTakesUpdateLock,
             "enabled"_a,
             "When true, handle_request() acquires the session update lock "
             "before serving — required if your subclass touches widget "
             "state. Default is false (lock-free serving, faster).")
        .def("generate_url", &Wt::WResource::generateUrl,
             "Return a URL at which this resource can be fetched.");

    // ---- WStreamResource (intermediate) ----
    //
    // Bound as a base for WFileResource. Not directly constructed from
    // Python — its purpose is to be subclassed in C++ to feed bytes from
    // a std::istream. Users wanting streaming should hand a path to
    // WFileResource (file-on-disk) or use WMemoryResource (already-in-RAM).

    nb::class_<Wt::WStreamResource, Wt::WResource>(m, "WStreamResource")
        .def_prop_rw("mime_type",
            [](const Wt::WStreamResource& r) { return r.mimeType(); },
            [](Wt::WStreamResource& r, const std::string& m) { r.setMimeType(m); })
        .def("set_buffer_size", &Wt::WStreamResource::setBufferSize,
             "size"_a);

    // ---- WMemoryResource: serve in-memory bytes ----
    //
    // The data is set via Python `bytes`. To update what gets served:
    //
    //     r.data = new_bytes
    //     r.set_changed()           # invalidate cached version
    //
    // Construction takes a MIME type and optional initial bytes.

    nb::class_<Wt::WMemoryResource, Wt::WResource>(m, "WMemoryResource")
        .def(heap_init<Wt::WMemoryResource>())
        .def(heap_init<Wt::WMemoryResource, const std::string&>(), "mime_type"_a)
        .def(nb::new_(
                [](const std::string& mime, nb::bytes data) {
                    const auto* p = reinterpret_cast<const unsigned char*>(
                        data.c_str());
                    return std::make_unique<Wt::WMemoryResource>(
                        mime,
                        std::vector<unsigned char>(p, p + data.size()));
                }),
             "mime_type"_a, "data"_a)
        .def_prop_rw("data",
            // Getter — return a Python `bytes` snapshot of the stored data.
            [](const Wt::WMemoryResource& r) {
                const auto& v = r.data();
                return nb::bytes(reinterpret_cast<const char*>(v.data()), v.size());
            },
            // Setter — accept Python `bytes`; set_changed() is the user's
            // call to invalidate the cached version.
            [](Wt::WMemoryResource& r, nb::bytes data) {
                const auto* p = reinterpret_cast<const unsigned char*>(data.c_str());
                r.setData(std::vector<unsigned char>(p, p + data.size()));
            })
        .def_prop_rw("mime_type",
            [](const Wt::WMemoryResource& r) { return r.mimeType(); },
            [](Wt::WMemoryResource& r, const std::string& m) { r.setMimeType(m); });

    // ---- WFileResource: serve a file from disk ----

    nb::class_<Wt::WFileResource, Wt::WStreamResource>(m, "WFileResource")
        .def(heap_init<Wt::WFileResource>())
        .def(heap_init<Wt::WFileResource, const std::string&>(), "file_name"_a)
        .def(heap_init<Wt::WFileResource, const std::string&, const std::string&>(),
             "mime_type"_a, "file_name"_a)
        .def_prop_rw("file_name",
            [](const Wt::WFileResource& r) { return r.fileName(); },
            [](Wt::WFileResource& r, const std::string& f) { r.setFileName(f); });

    // ---- WLink (single binding) ----
    //
    // Lives here (not in bind_widgets.cpp) because it needs WResource bound
    // before its `shared_ptr<WResource>` implicit constructor can be
    // registered. Both implicit constructors mean any endpoint that takes a
    // WLink (WAnchor, WImage, the `link` setters) transparently accepts
    //   - a `str` (becomes a URL link), or
    //   - a `WResource` (becomes a resource link).

    nb::class_<Wt::WLink>(m, "WLink")
        .def(nb::init<>())
        .def(nb::init_implicit<const std::string&>(), "url"_a)
        .def(nb::init_implicit<std::shared_ptr<Wt::WResource>>(),
             "resource"_a)
        .def_prop_rw("url",
            [](const Wt::WLink& l) { return l.url(); },
            [](Wt::WLink& l, const std::string& u) { l.setUrl(u); });

    // ---- CallbackResource: dynamic HTTP endpoint backed by a callable ----
    //
    //     def handle(req: wt.HttpRequest, resp: wt.HttpResponse) -> None:
    //         resp.set_mime_type("application/json")
    //         resp.write(b'{"ok": true}')
    //
    //     server.add_resource(wt.CallbackResource(handle), "/api/whatever")
    //
    // The callable runs on a Wt worker thread; the binding acquires the
    // GIL before invoking it. Request / Response wrappers are valid only
    // for the duration of the call. Captured state in the callable
    // (closures, dataclass attributes, anything) survives across
    // invocations — the CallbackResource itself holds a strong ref.

    nb::class_<CallbackResource, Wt::WResource>(m, "CallbackResource")
        .def(nb::new_([](nb::callable cb) {
                 return std::make_shared<CallbackResource>(std::move(cb));
             }),
             "callback"_a,
             "Mount a Python callable as an HTTP endpoint. The callable "
             "is invoked as `callback(request, response)` on every "
             "request, with the GIL held. Exceptions are routed through "
             "`PyErr_WriteUnraisable` rather than crashing Wt's worker.");
}

}  // namespace witty_for_python
