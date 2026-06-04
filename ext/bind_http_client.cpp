// Bindings for Wt::Http::Client — outbound HTTP requests from inside
// a Wt application — and Wt::Http::Message, the type used both as the
// payload of an outbound POST/PUT request and as the response handed
// back when a request completes.
//
// This is the *client* side of the HTTP module. The Wt::Http::Request /
// Wt::Http::Response classes (bound in bind_resource.cpp) are for the
// *server* side: when YOUR Wt app is serving a request to someone else.
// `Http::Message` is for the other direction — when you're the one
// making a request.
//
// Usage pattern:
//
//     client = wt.HttpClient()
//     def on_done(err: str, response: wt.HttpMessage) -> None:
//         if err:
//             log.error("fetch failed: %s", err)
//             return
//         print(response.status, response.body)
//     client.on_done(on_done)
//     client.get("https://example.com/api")
//
// The done callback fires asynchronously when the response arrives;
// `err` is an empty string on success, or the asio error message on
// failure. `response` is the parsed response (status / headers / body).

#include "common.hpp"
#include "signal_helpers.hpp"

#include <nanobind/stl/optional.h>

#include <Wt/Http/Client.h>
#include <Wt/Http/Message.h>
#include <Wt/Http/Method.h>

#include <chrono>
#include <memory>
#include <string>
#include <vector>

namespace witty_for_python {

void register_http_client(nb::module_& m) {
    // The `Http` submodule is created in register_resource (which runs
    // first per module.cpp ordering). We attach client-side names to
    // that same submodule so users see `wt.Http.Client`, `wt.Http.Message`,
    // etc. next to the server-side `wt.Http.Request` / `wt.Http.Response`.
    nb::module_ http = nb::cast<nb::module_>(m.attr("Http"));

    // ---- Http::Method enum ----

    nb::enum_<Wt::Http::Method>(http, "Method",
        "HTTP method selector for the generic `Client.request(method,\n"
        "url, message)` call. The method-specific helpers (`get`, `post`,\n"
        "…) cover the common cases without needing this enum.")
        .value("Get",    Wt::Http::Method::Get)
        .value("Post",   Wt::Http::Method::Post)
        .value("Put",    Wt::Http::Method::Put)
        .value("Delete", Wt::Http::Method::Delete)
        .value("Patch",  Wt::Http::Method::Patch)
        .value("Head",   Wt::Http::Method::Head);

    // ---- Http::Message::Header ----
    //
    // In Wt this is `Wt::Http::Message::Header`. We bind it flat as
    // `wt.Http.Header` rather than nested under Message because that's
    // how nanobind class hierarchies work cleanly (no nested types in
    // a single nb::class_), and re-attach it as `Http.Message.Header`
    // below for documentation symmetry.

    auto header_cls = nb::class_<Wt::Http::Message::Header>(http, "Header",
        "A single HTTP header (name, value) pair. Exposed both flat as\n"
        "`wt.Http.Header` and re-attached as `wt.Http.Message.Header` for\n"
        "the nested form. Used as the list element returned by\n"
        "`Message.headers` and accepted by Client's per-call `headers`\n"
        "parameter.")
        .def(nb::init<>(),
             "Construct an empty header with no name or value.")
        .def(nb::init<const std::string&, const std::string&>(),
             "name"_a, "value"_a,
             "Construct a header from a `name` / `value` pair.")
        .def_prop_rw("name",
            &Wt::Http::Message::Header::name,
            &Wt::Http::Message::Header::setName,
            "The header field name (e.g. 'Content-Type').")
        .def_prop_rw("value",
            &Wt::Http::Message::Header::value,
            &Wt::Http::Message::Header::setValue,
            "The header field value.");

    // ---- Http::Message ----
    //
    // The same type is used for both the request body sent to an HTTP
    // server (POST/PUT/PATCH bodies) and the response received from
    // one. For an outbound request, build it via the constructor +
    // add_body_text() / add_header(). For a response, read it via
    // status, headers, body, and get_header().

    auto message_cls = nb::class_<Wt::Http::Message>(http, "Message",
        "An HTTP message — headers plus body — usable in both directions.\n"
        "For outbound requests (POST/PUT/PATCH), build it via the empty\n"
        "constructor and accumulate headers and body bytes through\n"
        "`add_header` / `add_body_text`. For responses delivered to the\n"
        "`Client.on_done` callback, read `status`, `headers`, and `body`.\n"
        "\n"
        "    body = wt.Http.Message()\n"
        "    body.add_header('Content-Type', 'application/json')\n"
        "    body.add_body_text('{\"hello\": 42}')\n"
        "    client.post('https://api.example.com/x', body)")
        .def(nb::init<>(),
             "Construct an empty message with status=-1 and no headers.")
        .def(nb::init<std::vector<Wt::Http::Message::Header>, int>(),
             "headers"_a, "status"_a = -1,
             "Construct with headers and an optional status code.")
        // ---- response-side reads ----
        .def_prop_ro("status", &Wt::Http::Message::status,
             "HTTP status code on the response side. For a request, the "
             "status field is meaningless (the server sets it).")
        .def_prop_ro("headers",
             [](const Wt::Http::Message& m) { return m.headers(); },
             "All headers as a list[HttpHeader]. Note: header names may "
             "appear more than once; use get_header for the first match.")
        .def("get_header",
             [](const Wt::Http::Message& m, const std::string& name)
                 -> std::optional<std::string> {
                 const std::string* v = m.getHeader(name);
                 if (!v) return std::nullopt;
                 return *v;
             },
             "name"_a,
             "First header value with the given name, or None if absent.")
        .def_prop_ro("body", &Wt::Http::Message::body,
             "Response body as a string. For very large or streaming "
             "responses, see HttpClient.on_body_data_received and "
             "HttpClient.set_maximum_response_size(0).")
        // ---- request-side writes ----
        .def("set_header", &Wt::Http::Message::setHeader,
             "name"_a, "value"_a,
             "Set a header on the outbound request (replaces any prior "
             "value with the same name).")
        .def("add_header", &Wt::Http::Message::addHeader,
             "name"_a, "value"_a,
             "Append a header (HTTP allows duplicates for some headers, "
             "e.g. Set-Cookie).")
        .def("add_body_text", &Wt::Http::Message::addBodyText,
             "text"_a,
             "Append to the outbound request body.")
        .def("set_status", &Wt::Http::Message::setStatus, "status"_a,
             "Override the status code. Only meaningful when constructing\n"
             "a synthetic response — outbound requests get their status\n"
             "from the remote server.");

    // ---- Http::Client::URL ----

    auto url_cls = nb::class_<Wt::Http::Client::URL>(http, "ClientURL",
        "Parsed components of a URL, as produced by `Client.parse_url`.\n"
        "All fields are read-only views of the parse result; build a URL\n"
        "string yourself if you need to mutate it.")
        .def_ro("protocol", &Wt::Http::Client::URL::protocol,
            "Scheme part of the URL (e.g. 'http', 'https').")
        .def_ro("auth", &Wt::Http::Client::URL::auth,
            "Userinfo segment (the 'user:pass' between '://' and '@'),\n"
            "or empty if absent.")
        .def_ro("host", &Wt::Http::Client::URL::host,
            "Hostname or IP address from the URL authority.")
        .def_ro("port", &Wt::Http::Client::URL::port,
            "Port number, or the protocol default if not explicit.")
        .def_ro("path", &Wt::Http::Client::URL::path,
            "Path + query string portion of the URL.");

    // ---- Http::Client ----
    //
    // Async outbound HTTP client. Construction is heap-allocated +
    // shared_ptr-managed because Wt's Client uses an internal io_service
    // that we can't share with nb::init's tail-storage instances cleanly.
    //
    // Connect a callback via on_done(...) BEFORE calling get/post/etc.;
    // the callback fires asynchronously when the response arrives, with
    // (error_message: str, response: HttpMessage). An empty error_message
    // means success — the response is valid. A non-empty error_message
    // (e.g. "Connection refused", "Operation timed out") means the
    // request failed and `response` is meaningless.

    auto client_cls = nb::class_<Wt::Http::Client, Wt::WObject>(http, "Client",
        "Asynchronous outbound HTTP client. Issue a request with `get`,\n"
        "`post`, etc.; the response arrives later on the same I/O service\n"
        "via the `on_done` callback.\n"
        "\n"
        "    client = wt.Http.Client()\n"
        "    def on_done(err, response):\n"
        "        if err:\n"
        "            log.error('fetch failed: %s', err)\n"
        "            return\n"
        "        print(response.status, response.body)\n"
        "    client.on_done(on_done)\n"
        "    client.get('https://example.com/api')\n"
        "\n"
        "Connect callbacks BEFORE calling the request methods — they fire\n"
        "asynchronously and a fast localhost response can arrive before\n"
        "control returns. For streaming responses, set\n"
        "`set_maximum_response_size(0)` and wire `on_body_data_received`\n"
        "to consume bytes incrementally.")
        .def(nb::new_([]() {
                 return std::make_shared<Wt::Http::Client>();
             }),
             "Construct using the current WApplication's I/O service. "
             "Call from within a WApplication context (e.g. inside a "
             "create_app factory or a slot fired by a session).")
        .def("set_timeout_seconds",
             [](Wt::Http::Client& self, double s) {
                 self.setTimeout(std::chrono::duration_cast<
                     std::chrono::steady_clock::duration>(
                     std::chrono::duration<double>(s)));
             },
             "seconds"_a,
             "Per-I/O-operation timeout. Resets on each progress event, "
             "so total request time can exceed this. Default 10 seconds.")
        .def_prop_ro("timeout_seconds",
             [](const Wt::Http::Client& self) {
                 return std::chrono::duration_cast<
                     std::chrono::duration<double>>(self.timeout()).count();
             },
             "Current per-I/O-operation timeout in seconds.")
        .def("set_maximum_response_size",
             &Wt::Http::Client::setMaximumResponseSize, "bytes"_a,
             "Cap on the in-memory response size (DoS guard). Default 64 "
             "KiB. A value of 0 disables the limit AND prevents the body "
             "from being accumulated into the HttpMessage — use "
             "on_body_data_received to process chunks incrementally.")
        .def_prop_ro("maximum_response_size",
             &Wt::Http::Client::maximumResponseSize,
             "Current in-memory response cap in bytes. 0 means unlimited\n"
             "and disables body accumulation — read chunks via\n"
             "`on_body_data_received`.")
        .def("set_ssl_certificate_verification_enabled",
             &Wt::Http::Client::setSslCertificateVerificationEnabled,
             "enabled"_a,
             "Verify the server's TLS certificate (https only). Default "
             "True — only disable for testing against self-signed certs.")
        .def_prop_ro("ssl_certificate_verification_enabled",
             &Wt::Http::Client::isSslCertificateVerificationEnabled,
             "Whether the client is currently verifying TLS certificates.")
        .def("set_ssl_verify_file", &Wt::Http::Client::setSslVerifyFile,
             "path"_a,
             "Use a single PEM-encoded CA bundle file as the trust root\n"
             "for TLS verification. Pairs with\n"
             "`set_ssl_certificate_verification_enabled(True)`.")
        .def("set_ssl_verify_path", &Wt::Http::Client::setSslVerifyPath,
             "path"_a,
             "Use a directory of PEM-encoded CA certificates as the trust\n"
             "root for TLS verification.")
        .def("set_follow_redirect", &Wt::Http::Client::setFollowRedirect,
             "follow"_a,
             "When True, the client transparently follows 3xx responses\n"
             "up to `max_redirects` times. Off by default — the redirect\n"
             "response is delivered to `on_done` as-is.")
        .def_prop_ro("follow_redirect", &Wt::Http::Client::followRedirect,
             "Whether 3xx redirects are followed automatically.")
        .def("set_max_redirects", &Wt::Http::Client::setMaxRedirects,
             "max_redirects"_a,
             "Cap on consecutive 3xx hops before the client gives up.\n"
             "Only consulted when `follow_redirect` is True.")
        .def_prop_ro("max_redirects", &Wt::Http::Client::maxRedirects,
             "Current cap on follow_redirect hops.")
        // ---- request-issuing methods ----
        .def("get",
             [](Wt::Http::Client& self, const std::string& url) {
                 return self.get(url);
             },
             "url"_a,
             "Start an async GET. Returns False if the URL was malformed "
             "or the scheme unsupported; True if the request was "
             "scheduled (the done callback will fire when it completes).")
        .def("get",
             [](Wt::Http::Client& self, const std::string& url,
                std::vector<Wt::Http::Message::Header> headers) {
                 return self.get(url, headers);
             },
             "url"_a, "headers"_a,
             "GET with custom request headers.")
        .def("head",
             [](Wt::Http::Client& self, const std::string& url) {
                 return self.head(url);
             },
             "url"_a,
             "Start an async HEAD. Returns True if the request was\n"
             "scheduled. The response delivered to `on_done` has headers\n"
             "but an empty body, per the HEAD contract.")
        .def("post",
             &Wt::Http::Client::post,
             "url"_a, "message"_a,
             "POST. Build the request body as an HttpMessage first.")
        .def("put",
             &Wt::Http::Client::put,
             "url"_a, "message"_a,
             "Start an async PUT with `message` as the request body.")
        .def("delete_request",
             &Wt::Http::Client::deleteRequest,
             "url"_a, "message"_a,
             "Issue a DELETE. Named `delete_request` because `delete` is "
             "a Python keyword.")
        .def("patch",
             &Wt::Http::Client::patch,
             "url"_a, "message"_a,
             "Start an async PATCH with `message` as the request body.")
        .def("request",
             &Wt::Http::Client::request,
             "method"_a, "url"_a, "message"_a,
             "Issue any HTTP method via HttpMethod enum.")
        .def("abort", &Wt::Http::Client::abort,
             "Cancel the in-flight request (if any). done callback will "
             "still fire with an `operation_aborted` error message.")
        // ---- callbacks for the response ----
        //
        // Connecting these uses a custom wrapper rather than
        // `signal.connect(callable)` because asio::error_code isn't
        // exposed as a Python type; we marshal it to an error-message
        // string at the boundary.
        .def("on_done",
             [](Wt::Http::Client& self, nb::callable cb) {
                 int arity = python_arity(cb);
                 auto holder = std::make_shared<nb::object>(std::move(cb));
                 Wt::Signals::connection conn = self.done().connect(
                     [holder, arity](Wt::AsioWrapper::error_code err,
                                     Wt::Http::Message response) {
                         nb::gil_scoped_acquire gil;
                         try {
                             std::string err_str = err ? err.message() : "";
                             if (arity == 0) {
                                 (*holder)();
                             } else {
                                 (*holder)(
                                     err_str,
                                     nb::cast(std::move(response),
                                              nb::rv_policy::move));
                             }
                         } catch (nb::python_error& e) {
                             e.restore();
                             PyErr_WriteUnraisable(holder->ptr());
                         }
                     });
                 connection_registry_add(
                     static_cast<const void*>(&self.done()), conn);
                 return conn;
             },
             "callback"_a,
             "Register an async callback for the request's completion. "
             "Receives `(error_message: str, response: HttpMessage)` — "
             "error_message is '' on success.")
        .def("on_headers_received",
             [](Wt::Http::Client& self, nb::callable cb) {
                 return py_connect<Wt::Signal<Wt::Http::Message>,
                                   Wt::Http::Message>(
                     self.headersReceived(), std::move(cb));
             },
             "callback"_a,
             "Fires once the response headers are in but before the body "
             "is fully read. Receives the HttpMessage with headers + "
             "empty body. Useful for early-rejection of large downloads.")
        .def("on_body_data_received",
             [](Wt::Http::Client& self, nb::callable cb) {
                 return py_connect<Wt::Signal<std::string>, std::string>(
                     self.bodyDataReceived(), std::move(cb));
             },
             "callback"_a,
             "Fires for every chunk of body data received. Combine with "
             "set_maximum_response_size(0) for streaming responses.")
        .def_static("parse_url",
             [](const std::string& url)
                 -> std::optional<Wt::Http::Client::URL> {
                 Wt::Http::Client::URL parsed;
                 if (!Wt::Http::Client::parseUrl(url, parsed)) {
                     return std::nullopt;
                 }
                 return parsed;
             },
             "url"_a,
             "Parse `url` into its components. Returns None if invalid.");

    // Re-attach the nested types as attributes on their natural parent
    // so users can write `wt.Http.Message.Header(...)` and
    // `wt.Http.Client.URL(...)` — matching Wt's C++ `Wt::Http::Message::
    // Header` and `Wt::Http::Client::URL`.
    message_cls.attr("Header") = header_cls;
    client_cls.attr("URL")     = url_cls;
}

}  // namespace witty_for_python
