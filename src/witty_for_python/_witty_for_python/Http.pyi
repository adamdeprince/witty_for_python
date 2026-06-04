"""
Wt::Http — HTTP types shared by WResource handlers (Request, Response) and the outbound client (Message, Client, Method, Header).
"""

from collections.abc import Callable, Sequence
import enum
from typing import TypeAlias, overload

import witty_for_python._witty_for_python


class Request:
    """
    Read-only view of an incoming HTTP request, passed to your
    `WResource.handle_request` callback. Exposes the parsed URL
    path, query/form parameters, headers, cookies, and the raw body
    stream.

    Only valid for the duration of the callback that received it —
    the underlying C++ object lives on a worker-thread stack and
    vanishes when handle_request returns. Don't stash references.
    """

    @property
    def method(self) -> str:
        """HTTP method as a string ('GET', 'POST', 'PUT', ...)."""

    @property
    def path(self) -> str:
        """The deploy path at which this request was received."""

    @property
    def path_info(self) -> str:
        """Additional path info beyond the deploy path."""

    @property
    def query_string(self) -> str:
        """
        Raw query string portion of the URL (after '?'),
        without the leading '?'.
        """

    @property
    def url_scheme(self) -> str:
        """
        'http' or 'https' depending on how the client
        connected.
        """

    @property
    def content_type(self) -> str:
        """
        Value of the request's Content-Type header, or
        empty if not set.
        """

    @property
    def content_length(self) -> int:
        """
        Declared body length in bytes (from the
        Content-Length header).
        """

    @property
    def user_agent(self) -> str:
        """Value of the request's User-Agent header."""

    @property
    def client_address(self) -> str:
        """
        Client IP address (or the X-Forwarded-For value if
        Wt is configured to trust the proxy).
        """

    @property
    def host_name(self) -> str:
        """Host header value from the request."""

    @property
    def server_name(self) -> str:
        """Configured server name."""

    @property
    def server_port(self) -> str:
        """Server port the request arrived on."""

    def get_parameter(self, name: str) -> str | None:
        """First value for query/POST parameter `name`, or None."""

    def get_parameter_values(self, name: str) -> list[str]:
        """All values for a parameter (e.g. `?n=a&n=b` → ['a','b'])."""

    @property
    def parameters(self) -> dict[str, list[str]]:
        """All query/POST parameters as a dict[str, list[str]]."""

    def header_value(self, field: str) -> str:
        """Header value (empty string if absent)."""

    def cookie_value(self, name: str) -> str | None:
        """Cookie value, or None if absent."""

    @property
    def cookies(self) -> dict[str, str]:
        """All cookies as a dict[str, str]."""

    def body(self) -> bytes:
        """
        Read the entire request body as `bytes`. For application/x-www-form-urlencoded or multipart/form-data Wt has already consumed the stream and exposes the values via `get_parameter` instead.
        """

class Response:
    """
    Write-only handle for building the response from a WResource
    callback. Set the status, MIME type, and any headers BEFORE
    calling `write` — once the first byte of body goes out, headers
    are flushed to the wire and any subsequent `add_header` becomes
    a no-op.

        def handle(req, resp):
            resp.set_mime_type('application/json')
            resp.write(b'{"ok": true}')
    """

    def set_status(self, status: int) -> None:
        """Set the HTTP status code (default 200)."""

    def set_content_length(self, length: int) -> None:
        """
        Set the Content-Length header. Optional — Wt computes one
        from the body bytes you write if you skip it.
        """

    def set_mime_type(self, mime_type: str) -> None:
        """Set the Content-Type. After this (or any write) headers are committed."""

    def add_header(self, name: str, value: str) -> None:
        """
        Append a header — allows duplicates (e.g. Set-Cookie). For
        replace-on-conflict semantics use `insert_header`.
        """

    def insert_header(self, name: str, value: str) -> None:
        """Set an HTTP header, replacing any earlier value with the same name."""

    @overload
    def write(self, data: bytes) -> None:
        """Write `bytes` to the response body."""

    @overload
    def write(self, data: str) -> None:
        """Write a `str` (UTF-8) to the response body."""

class Method(enum.Enum):
    """
    HTTP method selector for the generic `Client.request(method,
    url, message)` call. The method-specific helpers (`get`, `post`,
    …) cover the common cases without needing this enum.
    """

    Get = 0

    Post = 1

    Put = 2

    Delete = 3

    Patch = 4

    Head = 5

class Header:
    """
    A single HTTP header (name, value) pair. Exposed both flat as
    `wt.Http.Header` and re-attached as `wt.Http.Message.Header` for
    the nested form. Used as the list element returned by
    `Message.headers` and accepted by Client's per-call `headers`
    parameter.
    """

    @overload
    def __init__(self) -> None:
        """Construct an empty header with no name or value."""

    @overload
    def __init__(self, name: str, value: str) -> None:
        """Construct a header from a `name` / `value` pair."""

    @property
    def name(self) -> str:
        """The header field name (e.g. 'Content-Type')."""

    @name.setter
    def name(self, arg: str, /) -> None: ...

    @property
    def value(self) -> str:
        """The header field value."""

    @value.setter
    def value(self, arg: str, /) -> None: ...

class Message:
    """
    An HTTP message — headers plus body — usable in both directions.
    For outbound requests (POST/PUT/PATCH), build it via the empty
    constructor and accumulate headers and body bytes through
    `add_header` / `add_body_text`. For responses delivered to the
    `Client.on_done` callback, read `status`, `headers`, and `body`.

        body = wt.Http.Message()
        body.add_header('Content-Type', 'application/json')
        body.add_body_text('{"hello": 42}')
        client.post('https://api.example.com/x', body)
    """

    @overload
    def __init__(self) -> None:
        """Construct an empty message with status=-1 and no headers."""

    @overload
    def __init__(self, headers: Sequence[Header], status: int = -1) -> None:
        """Construct with headers and an optional status code."""

    @property
    def status(self) -> int:
        """
        HTTP status code on the response side. For a request, the status field is meaningless (the server sets it).
        """

    @property
    def headers(self) -> list[Header]:
        """
        All headers as a list[HttpHeader]. Note: header names may appear more than once; use get_header for the first match.
        """

    def get_header(self, name: str) -> str | None:
        """First header value with the given name, or None if absent."""

    @property
    def body(self) -> str:
        """
        Response body as a string. For very large or streaming responses, see HttpClient.on_body_data_received and HttpClient.set_maximum_response_size(0).
        """

    def set_header(self, name: str, value: str) -> None:
        """
        Set a header on the outbound request (replaces any prior value with the same name).
        """

    def add_header(self, name: str, value: str) -> None:
        """
        Append a header (HTTP allows duplicates for some headers, e.g. Set-Cookie).
        """

    def add_body_text(self, text: str) -> None:
        """Append to the outbound request body."""

    def set_status(self, status: int) -> None:
        """
        Override the status code. Only meaningful when constructing
        a synthetic response — outbound requests get their status
        from the remote server.
        """

    class Header:
        """
        A single HTTP header (name, value) pair. Exposed both flat as
        `wt.Http.Header` and re-attached as `wt.Http.Message.Header` for
        the nested form. Used as the list element returned by
        `Message.headers` and accepted by Client's per-call `headers`
        parameter.
        """

        @overload
        def __init__(self) -> None:
            """Construct an empty header with no name or value."""

        @overload
        def __init__(self, name: str, value: str) -> None:
            """Construct a header from a `name` / `value` pair."""

        @property
        def name(self) -> str:
            """The header field name (e.g. 'Content-Type')."""

        @name.setter
        def name(self, arg: str, /) -> None: ...

        @property
        def value(self) -> str:
            """The header field value."""

        @value.setter
        def value(self, arg: str, /) -> None: ...

class ClientURL:
    """
    Parsed components of a URL, as produced by `Client.parse_url`.
    All fields are read-only views of the parse result; build a URL
    string yourself if you need to mutate it.
    """

    @property
    def protocol(self) -> str:
        """Scheme part of the URL (e.g. 'http', 'https')."""

    @property
    def auth(self) -> str:
        """
        Userinfo segment (the 'user:pass' between '://' and '@'),
        or empty if absent.
        """

    @property
    def host(self) -> str:
        """Hostname or IP address from the URL authority."""

    @property
    def port(self) -> int:
        """Port number, or the protocol default if not explicit."""

    @property
    def path(self) -> str:
        """Path + query string portion of the URL."""

class Client(witty_for_python._witty_for_python.WObject):
    """
    Asynchronous outbound HTTP client. Issue a request with `get`,
    `post`, etc.; the response arrives later on the same I/O service
    via the `on_done` callback.

        client = wt.Http.Client()
        def on_done(err, response):
            if err:
                log.error('fetch failed: %s', err)
                return
            print(response.status, response.body)
        client.on_done(on_done)
        client.get('https://example.com/api')

    Connect callbacks BEFORE calling the request methods — they fire
    asynchronously and a fast localhost response can arrive before
    control returns. For streaming responses, set
    `set_maximum_response_size(0)` and wire `on_body_data_received`
    to consume bytes incrementally.
    """

    def __init__(self) -> None:
        """
        Construct using the current WApplication's I/O service. Call from within a WApplication context (e.g. inside a create_app factory or a slot fired by a session).
        """

    def set_timeout_seconds(self, seconds: float) -> None:
        """
        Per-I/O-operation timeout. Resets on each progress event, so total request time can exceed this. Default 10 seconds.
        """

    @property
    def timeout_seconds(self) -> float:
        """Current per-I/O-operation timeout in seconds."""

    def set_maximum_response_size(self, bytes: int) -> None:
        """
        Cap on the in-memory response size (DoS guard). Default 64 KiB. A value of 0 disables the limit AND prevents the body from being accumulated into the HttpMessage — use on_body_data_received to process chunks incrementally.
        """

    @property
    def maximum_response_size(self) -> int:
        """
        Current in-memory response cap in bytes. 0 means unlimited
        and disables body accumulation — read chunks via
        `on_body_data_received`.
        """

    def set_ssl_certificate_verification_enabled(self, enabled: bool) -> None:
        """
        Verify the server's TLS certificate (https only). Default True — only disable for testing against self-signed certs.
        """

    @property
    def ssl_certificate_verification_enabled(self) -> bool:
        """Whether the client is currently verifying TLS certificates."""

    def set_ssl_verify_file(self, path: str) -> None:
        """
        Use a single PEM-encoded CA bundle file as the trust root
        for TLS verification. Pairs with
        `set_ssl_certificate_verification_enabled(True)`.
        """

    def set_ssl_verify_path(self, path: str) -> None:
        """
        Use a directory of PEM-encoded CA certificates as the trust
        root for TLS verification.
        """

    def set_follow_redirect(self, follow: bool) -> None:
        """
        When True, the client transparently follows 3xx responses
        up to `max_redirects` times. Off by default — the redirect
        response is delivered to `on_done` as-is.
        """

    @property
    def follow_redirect(self) -> bool:
        """Whether 3xx redirects are followed automatically."""

    def set_max_redirects(self, max_redirects: int) -> None:
        """
        Cap on consecutive 3xx hops before the client gives up.
        Only consulted when `follow_redirect` is True.
        """

    @property
    def max_redirects(self) -> int:
        """Current cap on follow_redirect hops."""

    @overload
    def get(self, url: str) -> bool:
        """
        Start an async GET. Returns False if the URL was malformed or the scheme unsupported; True if the request was scheduled (the done callback will fire when it completes).
        """

    @overload
    def get(self, url: str, headers: Sequence[Header]) -> bool:
        """GET with custom request headers."""

    def head(self, url: str) -> bool:
        """
        Start an async HEAD. Returns True if the request was
        scheduled. The response delivered to `on_done` has headers
        but an empty body, per the HEAD contract.
        """

    def post(self, url: str, message: Message) -> bool:
        """POST. Build the request body as an HttpMessage first."""

    def put(self, url: str, message: Message) -> bool:
        """Start an async PUT with `message` as the request body."""

    def delete_request(self, url: str, message: Message) -> bool:
        """
        Issue a DELETE. Named `delete_request` because `delete` is a Python keyword.
        """

    def patch(self, url: str, message: Message) -> bool:
        """Start an async PATCH with `message` as the request body."""

    def request(self, method: Method, url: str, message: Message) -> bool:
        """Issue any HTTP method via HttpMethod enum."""

    def abort(self) -> None:
        """
        Cancel the in-flight request (if any). done callback will still fire with an `operation_aborted` error message.
        """

    def on_done(self, callback: Callable) -> witty_for_python._witty_for_python.Connection:
        r"""
        Register an async callback for the request's completion. Receives `(error_message: str, response: HttpMessage)` — error_message is \'\' on success.
        """

    def on_headers_received(self, callback: Callable) -> witty_for_python._witty_for_python.Connection:
        """
        Fires once the response headers are in but before the body is fully read. Receives the HttpMessage with headers + empty body. Useful for early-rejection of large downloads.
        """

    def on_body_data_received(self, callback: Callable) -> witty_for_python._witty_for_python.Connection:
        """
        Fires for every chunk of body data received. Combine with set_maximum_response_size(0) for streaming responses.
        """

    @staticmethod
    def parse_url(url: str) -> ClientURL | None:
        """Parse `url` into its components. Returns None if invalid."""

    URL: TypeAlias = ClientURL
