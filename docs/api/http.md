# HTTP (submodule)

> The `witty_for_python.Http` subsystem — the Request/Response pair passed to WResource handlers, and the outbound HTTP Client/Message types.

**Classes in this section:**

- [`Request`](#Http.Request)
- [`Response`](#Http.Response)
- [`Method`](#Http.Method)
- [`Header`](#Http.Header)
- [`Message`](#Http.Message)
- [`Header`](#Http.Message.Header)
- [`ClientURL`](#Http.ClientURL)
- [`Client`](#Http.Client)

---

### Request {#Http.Request}

Read-only view of an incoming HTTP request, passed to your
`WResource.handle_request` callback. Exposes the parsed URL
path, query/form parameters, headers, cookies, and the raw body
stream.

Only valid for the duration of the callback that received it —
the underlying C++ object lives on a worker-thread stack and
vanishes when handle_request returns. Don't stash references.

**Properties**

- `method: str` *(read-only)*
  HTTP method as a string ('GET', 'POST', 'PUT', ...).

- `path: str` *(read-only)*
  The deploy path at which this request was received.

- `path_info: str` *(read-only)*
  Additional path info beyond the deploy path.

- `query_string: str` *(read-only)*
  Raw query string portion of the URL (after '?'),
  without the leading '?'.

- `url_scheme: str` *(read-only)*
  'http' or 'https' depending on how the client
  connected.

- `content_type: str` *(read-only)*
  Value of the request's Content-Type header, or
  empty if not set.

- `content_length: int` *(read-only)*
  Declared body length in bytes (from the
  Content-Length header).

- `user_agent: str` *(read-only)*
  Value of the request's User-Agent header.

- `client_address: str` *(read-only)*
  Client IP address (or the X-Forwarded-For value if
  Wt is configured to trust the proxy).

- `host_name: str` *(read-only)*
  Host header value from the request.

- `server_name: str` *(read-only)*
  Configured server name.

- `server_port: str` *(read-only)*
  Server port the request arrived on.

- `parameters: dict[str, list[str]]` *(read-only)*
  All query/POST parameters as a dict[str, list[str]].

- `cookies: dict[str, str]` *(read-only)*
  All cookies as a dict[str, str].

**Methods**

- `get_parameter(self, name: str) -> str | None`
  First value for query/POST parameter `name`, or None.

- `get_parameter_values(self, name: str) -> list[str]`
  All values for a parameter (e.g. `?n=a&n=b` → ['a','b']).

- `header_value(self, field: str) -> str`
  Header value (empty string if absent).

- `cookie_value(self, name: str) -> str | None`
  Cookie value, or None if absent.

- `body(self) -> bytes`
  Read the entire request body as `bytes`. For application/x-www-form-urlencoded or multipart/form-data Wt has already consumed the stream and exposes the values via `get_parameter` instead.

### Response {#Http.Response}

Write-only handle for building the response from a WResource
callback. Set the status, MIME type, and any headers BEFORE
calling `write` — once the first byte of body goes out, headers
are flushed to the wire and any subsequent `add_header` becomes
a no-op.

    def handle(req, resp):
        resp.set_mime_type('application/json')
        resp.write(b'{"ok": true}')

**Methods**

- `set_status(self, status: int) -> None`
  Set the HTTP status code (default 200).

- `set_content_length(self, length: int) -> None`
  Set the Content-Length header. Optional — Wt computes one
  from the body bytes you write if you skip it.

- `set_mime_type(self, mime_type: str) -> None`
  Set the Content-Type. After this (or any write) headers are committed.

- `add_header(self, name: str, value: str) -> None`
  Append a header — allows duplicates (e.g. Set-Cookie). For
  replace-on-conflict semantics use `insert_header`.

- `insert_header(self, name: str, value: str) -> None`
  Set an HTTP header, replacing any earlier value with the same name.

- `write(self, data: bytes) -> None`
  Write `bytes` to the response body.

- `write(self, data: str) -> None`
  Write a `str` (UTF-8) to the response body.

### Method {#Http.Method}

*Inherits:* `enum.Enum`

HTTP method selector for the generic `Client.request(method,
url, message)` call. The method-specific helpers (`get`, `post`,
…) cover the common cases without needing this enum.

### Header {#Http.Header}

A single HTTP header (name, value) pair. Exposed both flat as
`wt.Http.Header` and re-attached as `wt.Http.Message.Header` for
the nested form. Used as the list element returned by
`Message.headers` and accepted by Client's per-call `headers`
parameter.

**Constructors**

- `__init__(self) -> None`
  Construct an empty header with no name or value.

- `__init__(self, name: str, value: str) -> None`
  Construct a header from a `name` / `value` pair.

**Properties**

- `name: str` *(read/write)*
  The header field name (e.g. 'Content-Type').

- `value: str` *(read/write)*
  The header field value.

### Message {#Http.Message}

An HTTP message — headers plus body — usable in both directions.
For outbound requests (POST/PUT/PATCH), build it via the empty
constructor and accumulate headers and body bytes through
`add_header` / `add_body_text`. For responses delivered to the
`Client.on_done` callback, read `status`, `headers`, and `body`.

    body = wt.Http.Message()
    body.add_header('Content-Type', 'application/json')
    body.add_body_text('{"hello": 42}')
    client.post('https://api.example.com/x', body)

**Constructors**

- `__init__(self) -> None`
  Construct an empty message with status=-1 and no headers.

- `__init__(self, headers: Sequence[Header], status: int = -1) -> None`
  Construct with headers and an optional status code.

**Properties**

- `status: int` *(read-only)*
  HTTP status code on the response side. For a request, the status field is meaningless (the server sets it).

- `headers: list[Header]` *(read-only)*
  All headers as a list[HttpHeader]. Note: header names may appear more than once; use get_header for the first match.

- `body: str` *(read-only)*
  Response body as a string. For very large or streaming responses, see HttpClient.on_body_data_received and HttpClient.set_maximum_response_size(0).

**Methods**

- `get_header(self, name: str) -> str | None`
  First header value with the given name, or None if absent.

- `set_header(self, name: str, value: str) -> None`
  Set a header on the outbound request (replaces any prior value with the same name).

- `add_header(self, name: str, value: str) -> None`
  Append a header (HTTP allows duplicates for some headers, e.g. Set-Cookie).

- `add_body_text(self, text: str) -> None`
  Append to the outbound request body.

- `set_status(self, status: int) -> None`
  Override the status code. Only meaningful when constructing
  a synthetic response — outbound requests get their status
  from the remote server.

**Nested types**

- `Header`
  A single HTTP header (name, value) pair. Exposed both flat as
  `wt.Http.Header` and re-attached as `wt.Http.Message.Header` for
  the nested form. Used as the list element returned by
  `Message.headers` and accepted by Client's per-call `headers`
  parameter.

### Header {#Http.Message.Header}

A single HTTP header (name, value) pair. Exposed both flat as
`wt.Http.Header` and re-attached as `wt.Http.Message.Header` for
the nested form. Used as the list element returned by
`Message.headers` and accepted by Client's per-call `headers`
parameter.

**Constructors**

- `__init__(self) -> None`
  Construct an empty header with no name or value.

- `__init__(self, name: str, value: str) -> None`
  Construct a header from a `name` / `value` pair.

**Properties**

- `name: str` *(read/write)*
  The header field name (e.g. 'Content-Type').

- `value: str` *(read/write)*
  The header field value.

### ClientURL {#Http.ClientURL}

Parsed components of a URL, as produced by `Client.parse_url`.
All fields are read-only views of the parse result; build a URL
string yourself if you need to mutate it.

**Properties**

- `protocol: str` *(read-only)*
  Scheme part of the URL (e.g. 'http', 'https').

- `auth: str` *(read-only)*
  Userinfo segment (the 'user:pass' between '://' and '@'),
  or empty if absent.

- `host: str` *(read-only)*
  Hostname or IP address from the URL authority.

- `port: int` *(read-only)*
  Port number, or the protocol default if not explicit.

- `path: str` *(read-only)*
  Path + query string portion of the URL.

### Client {#Http.Client}

*Inherits:* `witty_for_python._witty_for_python.WObject`

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

**Constructors**

- `__init__(self) -> None`
  Construct using the current WApplication's I/O service. Call from within a WApplication context (e.g. inside a create_app factory or a slot fired by a session).

**Properties**

- `timeout_seconds: float` *(read-only)*
  Current per-I/O-operation timeout in seconds.

- `maximum_response_size: int` *(read-only)*
  Current in-memory response cap in bytes. 0 means unlimited
  and disables body accumulation — read chunks via
  `on_body_data_received`.

- `ssl_certificate_verification_enabled: bool` *(read-only)*
  Whether the client is currently verifying TLS certificates.

- `follow_redirect: bool` *(read-only)*
  Whether 3xx redirects are followed automatically.

- `max_redirects: int` *(read-only)*
  Current cap on follow_redirect hops.

**Methods**

- `set_timeout_seconds(self, seconds: float) -> None`
  Per-I/O-operation timeout. Resets on each progress event, so total request time can exceed this. Default 10 seconds.

- `set_maximum_response_size(self, bytes: int) -> None`
  Cap on the in-memory response size (DoS guard). Default 64 KiB. A value of 0 disables the limit AND prevents the body from being accumulated into the HttpMessage — use on_body_data_received to process chunks incrementally.

- `set_ssl_certificate_verification_enabled(self, enabled: bool) -> None`
  Verify the server's TLS certificate (https only). Default True — only disable for testing against self-signed certs.

- `set_ssl_verify_file(self, path: str) -> None`
  Use a single PEM-encoded CA bundle file as the trust root
  for TLS verification. Pairs with
  `set_ssl_certificate_verification_enabled(True)`.

- `set_ssl_verify_path(self, path: str) -> None`
  Use a directory of PEM-encoded CA certificates as the trust
  root for TLS verification.

- `set_follow_redirect(self, follow: bool) -> None`
  When True, the client transparently follows 3xx responses
  up to `max_redirects` times. Off by default — the redirect
  response is delivered to `on_done` as-is.

- `set_max_redirects(self, max_redirects: int) -> None`
  Cap on consecutive 3xx hops before the client gives up.
  Only consulted when `follow_redirect` is True.

- `get(self, url: str) -> bool`
  Start an async GET. Returns False if the URL was malformed or the scheme unsupported; True if the request was scheduled (the done callback will fire when it completes).

- `get(self, url: str, headers: Sequence[Header]) -> bool`
  GET with custom request headers.

- `head(self, url: str) -> bool`
  Start an async HEAD. Returns True if the request was
  scheduled. The response delivered to `on_done` has headers
  but an empty body, per the HEAD contract.

- `post(self, url: str, message: Message) -> bool`
  POST. Build the request body as an HttpMessage first.

- `put(self, url: str, message: Message) -> bool`
  Start an async PUT with `message` as the request body.

- `delete_request(self, url: str, message: Message) -> bool`
  Issue a DELETE. Named `delete_request` because `delete` is a Python keyword.

- `patch(self, url: str, message: Message) -> bool`
  Start an async PATCH with `message` as the request body.

- `request(self, method: Method, url: str, message: Message) -> bool`
  Issue any HTTP method via HttpMethod enum.

- `abort(self) -> None`
  Cancel the in-flight request (if any). done callback will still fire with an `operation_aborted` error message.

- `on_done(self, callback: Callable) -> witty_for_python._witty_for_python.Connection`
  Register an async callback for the request's completion. Receives `(error_message: str, response: HttpMessage)` — error_message is \'\' on success.

- `on_headers_received(self, callback: Callable) -> witty_for_python._witty_for_python.Connection`
  Fires once the response headers are in but before the body is fully read. Receives the HttpMessage with headers + empty body. Useful for early-rejection of large downloads.

- `on_body_data_received(self, callback: Callable) -> witty_for_python._witty_for_python.Connection`
  Fires for every chunk of body data received. Combine with set_maximum_response_size(0) for streaming responses.

- `parse_url(url: str) -> ClientURL | None`
  Parse `url` into its components. Returns None if invalid.
