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

    nb::enum_<Wt::ContentDisposition>(m, "ContentDisposition",
        "Controls the `Content-Disposition` header on resource responses\n"
        "— whether the browser displays the bytes inline, prompts the\n"
        "user to save them, or leaves the header off. Pair with\n"
        "`WResource.suggest_file_name` for the save filename.")
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

    nb::class_<Wt::Http::Request>(http, "Request",
        "Read-only view of an incoming HTTP request, passed to your\n"
        "`WResource.handle_request` callback. Exposes the parsed URL\n"
        "path, query/form parameters, headers, cookies, and the raw body\n"
        "stream.\n"
        "\n"
        "Only valid for the duration of the callback that received it —\n"
        "the underlying C++ object lives on a worker-thread stack and\n"
        "vanishes when handle_request returns. Don't stash references.")
        .def_prop_ro("method", &Wt::Http::Request::method,
                     "HTTP method as a string ('GET', 'POST', 'PUT', ...).")
        .def_prop_ro("path", &Wt::Http::Request::path,
                     "The deploy path at which this request was received.")
        .def_prop_ro("path_info", &Wt::Http::Request::pathInfo,
                     "Additional path info beyond the deploy path.")
        .def_prop_ro("query_string", &Wt::Http::Request::queryString,
                     "Raw query string portion of the URL (after '?'),\n"
                     "without the leading '?'.")
        .def_prop_ro("url_scheme", &Wt::Http::Request::urlScheme,
                     "'http' or 'https' depending on how the client\n"
                     "connected.")
        .def_prop_ro("content_type", &Wt::Http::Request::contentType,
                     "Value of the request's Content-Type header, or\n"
                     "empty if not set.")
        .def_prop_ro("content_length", &Wt::Http::Request::contentLength,
                     "Declared body length in bytes (from the\n"
                     "Content-Length header).")
        .def_prop_ro("user_agent", &Wt::Http::Request::userAgent,
                     "Value of the request's User-Agent header.")
        .def_prop_ro("client_address", &Wt::Http::Request::clientAddress,
                     "Client IP address (or the X-Forwarded-For value if\n"
                     "Wt is configured to trust the proxy).")
        .def_prop_ro("host_name", &Wt::Http::Request::hostName,
                     "Host header value from the request.")
        .def_prop_ro("server_name", &Wt::Http::Request::serverName,
                     "Configured server name.")
        .def_prop_ro("server_port", &Wt::Http::Request::serverPort,
                     "Server port the request arrived on.")
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

    nb::class_<Wt::Http::Response>(http, "Response",
        "Write-only handle for building the response from a WResource\n"
        "callback. Set the status, MIME type, and any headers BEFORE\n"
        "calling `write` — once the first byte of body goes out, headers\n"
        "are flushed to the wire and any subsequent `add_header` becomes\n"
        "a no-op.\n"
        "\n"
        "    def handle(req, resp):\n"
        "        resp.set_mime_type('application/json')\n"
        "        resp.write(b'{\"ok\": true}')")
        .def("set_status", &Wt::Http::Response::setStatus, "status"_a,
             "Set the HTTP status code (default 200).")
        .def("set_content_length",
             [](Wt::Http::Response& r, std::uint64_t n) {
                 r.setContentLength(n);
             },
             "length"_a,
             "Set the Content-Length header. Optional — Wt computes one\n"
             "from the body bytes you write if you skip it.")
        .def("set_mime_type", &Wt::Http::Response::setMimeType,
             "mime_type"_a,
             "Set the Content-Type. After this (or any write) headers "
             "are committed.")
        .def("add_header", &Wt::Http::Response::addHeader,
             "name"_a, "value"_a,
             "Append a header — allows duplicates (e.g. Set-Cookie). For\n"
             "replace-on-conflict semantics use `insert_header`.")
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

    nb::class_<Wt::WResource, Wt::WObject>(m, "WResource",
        "Abstract base for anything Wt serves over HTTP that isn't the\n"
        "widget tree itself — file downloads, generated PDFs, JSON APIs,\n"
        "image data, etc. Mount via `WServer.add_resource(resource,\n"
        "path)` for server-wide endpoints, or hand to a `WLink` for\n"
        "session-scoped use (e.g. an inline image).\n"
        "\n"
        "Two concrete subclasses ship in this binding — WMemoryResource\n"
        "(in-RAM bytes) and WFileResource (file on disk). For dynamic\n"
        "endpoints, use `CallbackResource(callable)` which delegates\n"
        "handle_request to a Python function instead of requiring a\n"
        "subclass.")
        .def("suggest_file_name",
             [](Wt::WResource& r, const Wt::WString& name) {
                 r.suggestFileName(name);
             },
             "name"_a,
             "Set the suggested filename the browser uses when saving the "
             "resource (e.g. 'export.csv').")
        .def("set_disposition_type", &Wt::WResource::setDispositionType,
             "disposition"_a,
             "Choose ContentDisposition.Attachment to force a 'Save As'\n"
             "prompt, .Inline to display in-page when the MIME type\n"
             "supports it, or .None_ to omit the header.")
        .def("set_changed", &Wt::WResource::setChanged,
             "Invalidate any browser-side cache of this resource so the "
             "next fetch sees the latest data. Call after set_data() etc.")
        .def_prop_rw("internal_path",
            [](const Wt::WResource& r) { return r.internalPath(); },
            [](Wt::WResource& r, const std::string& p) { r.setInternalPath(p); },
            "Stable internal-path component of the resource's URL.\n"
            "Setting one lets you mount the resource at a known route\n"
            "rather than a generated hash.")
        .def("set_invalid_after_changed", &Wt::WResource::setInvalidAfterChanged,
             "enabled"_a,
             "When True, every `set_changed` invalidates any URL\n"
             "previously handed out — clients with the old URL will get\n"
             "404 and must re-fetch the URL. Default False (URL stays\n"
             "stable across content updates).")
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

    nb::class_<Wt::WStreamResource, Wt::WResource>(m, "WStreamResource",
        "Intermediate base for resources that stream their bytes from a\n"
        "C++ `std::istream`. Bound here only so WFileResource can inherit\n"
        "MIME-type and buffer-size knobs — for Python use, reach for\n"
        "WFileResource (file on disk), WMemoryResource (bytes in RAM),\n"
        "or CallbackResource (write whatever you want directly to the\n"
        "Response).")
        .def_prop_rw("mime_type",
            [](const Wt::WStreamResource& r) { return r.mimeType(); },
            [](Wt::WStreamResource& r, const std::string& m) { r.setMimeType(m); },
            "Content-Type sent with each response.")
        .def("set_buffer_size", &Wt::WStreamResource::setBufferSize,
             "size"_a,
             "Size in bytes of the chunk used to copy from the underlying\n"
             "stream to the HTTP response. Larger reduces syscall\n"
             "overhead; smaller improves first-byte latency.");

    // ---- WMemoryResource: serve in-memory bytes ----
    //
    // The data is set via Python `bytes`. To update what gets served:
    //
    //     r.data = new_bytes
    //     r.set_changed()           # invalidate cached version
    //
    // Construction takes a MIME type and optional initial bytes.

    nb::class_<Wt::WMemoryResource, Wt::WResource>(m, "WMemoryResource",
        "WResource backed by an in-memory `bytes` blob. Useful for small\n"
        "generated payloads (a CSV, a thumbnail) that shouldn't touch the\n"
        "filesystem.\n"
        "\n"
        "    payload = wt.WMemoryResource('text/csv', b'name,age\\nAlice,30\\n')\n"
        "    server.add_resource(payload, '/export.csv')\n"
        "    # later: rebuild and notify clients\n"
        "    payload.data = render_csv(rows)\n"
        "    payload.set_changed()")
        .def(heap_init<Wt::WMemoryResource>(),
             "Construct an empty memory resource with no MIME type or\n"
             "data set — assign both before serving.")
        .def(heap_init<Wt::WMemoryResource, const std::string&>(), "mime_type"_a,
             "Construct a memory resource declaring `mime_type` with no\n"
             "data set yet. Assign `data` before mounting.")
        .def(nb::new_(
                [](const std::string& mime, nb::bytes data) {
                    const auto* p = reinterpret_cast<const unsigned char*>(
                        data.c_str());
                    return std::make_unique<Wt::WMemoryResource>(
                        mime,
                        std::vector<unsigned char>(p, p + data.size()));
                }),
             "mime_type"_a, "data"_a,
             "Construct a memory resource ready to serve `data` as\n"
             "`mime_type`.")
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
            },
            "The bytes served. Reading returns a copy as `bytes`;\n"
            "assigning replaces the served payload. Call `set_changed`\n"
            "afterwards to invalidate any browser cache.")
        .def_prop_rw("mime_type",
            [](const Wt::WMemoryResource& r) { return r.mimeType(); },
            [](Wt::WMemoryResource& r, const std::string& m) { r.setMimeType(m); },
            "Content-Type returned with the bytes.");

    // ---- WFileResource: serve a file from disk ----

    nb::class_<Wt::WFileResource, Wt::WStreamResource>(m, "WFileResource",
        "WResource that streams a file on disk. Wt opens the file per\n"
        "request and copies bytes through to the HTTP response, so the\n"
        "file can change between fetches without restarting the server.\n"
        "\n"
        "    server.add_resource(\n"
        "        wt.WFileResource('application/pdf', '/var/data/report.pdf'),\n"
        "        '/report.pdf')")
        .def(heap_init<Wt::WFileResource>(),
             "Construct an empty file resource with no file or MIME type\n"
             "set. Assign both before serving.")
        .def(heap_init<Wt::WFileResource, const std::string&>(), "file_name"_a,
             "Construct a file resource pointing at `file_name`. The\n"
             "MIME type is left at the inherited default — set\n"
             "`mime_type` afterwards.")
        .def(heap_init<Wt::WFileResource, const std::string&, const std::string&>(),
             "mime_type"_a, "file_name"_a,
             "Construct a file resource that serves `file_name` with\n"
             "`mime_type` as its Content-Type.")
        .def_prop_rw("file_name",
            [](const Wt::WFileResource& r) { return r.fileName(); },
            [](Wt::WFileResource& r, const std::string& f) { r.setFileName(f); },
            "Filesystem path of the file to serve. Assigning swaps the\n"
            "source — call `set_changed` afterwards to invalidate caches.");

    // ---- WLink (single binding) ----
    //
    // Lives here (not in bind_widgets.cpp) because it needs WResource bound
    // before its `shared_ptr<WResource>` implicit constructor can be
    // registered. Both implicit constructors mean any endpoint that takes a
    // WLink (WAnchor, WImage, the `link` setters) transparently accepts
    //   - a `str` (becomes a URL link), or
    //   - a `WResource` (becomes a resource link).

    nb::class_<Wt::WLink>(m, "WLink",
        "Polymorphic link target — wraps a URL string OR a server-side\n"
        "WResource. Used by WAnchor, WImage, WPushButton.link, etc.;\n"
        "Python's implicit conversion lets you pass a bare str or a\n"
        "WResource and get the corresponding WLink automatically.\n"
        "\n"
        "    container.add_widget(wt.WAnchor(wt.WLink('https://example.com'), 'Visit'))\n"
        "\n"
        "    chart = wt.WMemoryResource('image/png', render_png())\n"
        "    container.add_widget(wt.WImage(wt.WLink(chart), 'Chart'))\n"
        "\n"
        "For URL fragments that should drive WApplication.internal_path\n"
        "navigation rather than a full page load, set `internal_path` on\n"
        "the link or use the `wt.internal_path('/route')` factory.")
        .def(nb::init<>(),
             "Construct an empty link with no target.")
        .def(nb::init_implicit<const std::string&>(), "url"_a,
             "Construct a link to an external URL or any same-origin path.\n"
             "Plain `str` arguments to widgets that take a WLink hit this\n"
             "constructor automatically.")
        .def(nb::init_implicit<std::shared_ptr<Wt::WResource>>(),
             "resource"_a,
             "Construct a link to a WResource. The resource's URL is\n"
             "computed by Wt; clients fetch the dynamic content when the\n"
             "link is followed. A `WResource` arg to widgets that take a\n"
             "WLink hits this constructor automatically.")
        .def_prop_rw("url",
            [](const Wt::WLink& l) { return l.url(); },
            [](Wt::WLink& l, const std::string& u) { l.setUrl(u); },
            "The link target as a URL string.")
        // Mark the link as an internal-path link instead of a regular
        // URL. WAnchor with an internal-path WLink does AJAX-style
        // navigation (updates the URL fragment, fires
        // WApplication.internal_path_changed) — clicking does NOT
        // reload the page. Without this, WLink('/1') is treated as an
        // external URL and the browser navigates away from the session.
        .def_prop_rw("internal_path",
            [](const Wt::WLink& l) { return l.internalPath(); },
            [](Wt::WLink& l, const Wt::WString& path) {
                l.setInternalPath(path);
            },
            "Treat the link as an internal-path navigation rather than an\n"
            "external URL. Setting this makes a click update the URL\n"
            "fragment and fire `WApplication.on_internal_path_changed`\n"
            "instead of reloading the page.");

    // Module-level factory: a one-liner for building an internal-path
    // WLink without the two-step `WLink(); link.internal_path = ...`
    // dance. `wt.internal_path('/2')` is the natural way to wire
    // WAnchor / WImage / WPushButton to slide-style URL-fragment
    // navigation.
    m.def("internal_path",
          [](const Wt::WString& path) {
              Wt::WLink link;
              link.setInternalPath(path);
              return link;
          },
          "path"_a,
          "Construct a WLink that points to the given internal path "
          "(e.g. '/slide/3'). Clicking a WAnchor backed by this link "
          "fires WApplication.internal_path_changed instead of "
          "navigating away.");

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

    nb::class_<CallbackResource, Wt::WResource>(m, "CallbackResource",
        "WResource whose `handle_request` delegates to a Python callable.\n"
        "The Pythonic way to expose a dynamic HTTP endpoint without\n"
        "subclassing — the equivalent of a Flask/Django view function in\n"
        "the Wt world.\n"
        "\n"
        "    def api(req, resp):\n"
        "        resp.set_mime_type('application/json')\n"
        "        resp.write(b'{\"ok\": true}')\n"
        "    server.add_resource(wt.CallbackResource(api), '/api/ping')\n"
        "\n"
        "Wt invokes the callable on a worker thread with `(request,\n"
        "response)`; the binding takes the GIL around the call. The\n"
        "request/response wrappers are valid only for the duration of\n"
        "the invocation — don't stash them. Captured state in the\n"
        "callable (closures, class attrs) persists across requests; the\n"
        "CallbackResource holds a strong reference to the callable.")
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
