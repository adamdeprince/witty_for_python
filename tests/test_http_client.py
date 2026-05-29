"""Surface tests for `wt.Http.Client` and `wt.Http.Message`.

Fully exercising `Http.Client.get()` end-to-end requires a live
WApplication event loop (the client's I/O completion runs through Wt's
worker pool, and the done callback only fires within an application
context). That's not testable in pytest without a browser session
driving the WebSocket handshake. See `examples/http_client_demo.py`
for a runnable demonstration of the round trip.

This test verifies:
  - `Http.Message` can be constructed and accumulates headers + body
    (request-direction usage),
  - `Http.Message` round-trips via the constructor that accepts a
    header list and a status code (response-direction shape),
  - `Http.Client` can be instantiated and the request-issuing methods
    exist with the expected signatures,
  - `Http.Client.parse_url` works,
  - the `Http.Method` enum is wired,
  - the nested-types aliases work (`Http.Message.Header`,
    `Http.Client.URL`).
"""

from __future__ import annotations

import pytest

import witty_for_python as wt


def test_http_message_outbound_build() -> None:
    """Build a request body the way you'd hand it to client.post()."""
    msg = wt.Http.Message()
    msg.add_header("Content-Type", "application/json")
    msg.add_header("X-Custom", "foo")
    msg.add_body_text('{"k": "v"}')

    headers = msg.headers
    assert [(h.name, h.value) for h in headers] == [
        ("Content-Type", "application/json"),
        ("X-Custom", "foo"),
    ]
    assert msg.body == '{"k": "v"}'
    # Outbound status is meaningless but the field exists.
    assert msg.status == -1


def test_http_message_inbound_shape() -> None:
    """The response side: status + headers + body via the headers-list ctor."""
    msg = wt.Http.Message(
        [wt.Http.Header("Content-Type", "text/plain"),
         wt.Http.Header("Cache-Control", "no-store")],
        200,
    )
    assert msg.status == 200
    assert msg.get_header("Content-Type") == "text/plain"
    assert msg.get_header("Missing") is None


def test_http_message_set_header_replaces() -> None:
    msg = wt.Http.Message()
    msg.set_header("X", "1")
    msg.set_header("X", "2")
    assert msg.get_header("X") == "2"


def test_http_message_add_header_duplicates() -> None:
    """add_header allows duplicates (HTTP permits it for Set-Cookie etc.)."""
    msg = wt.Http.Message()
    msg.add_header("Set-Cookie", "a=1")
    msg.add_header("Set-Cookie", "b=2")
    assert [h.value for h in msg.headers if h.name == "Set-Cookie"] == ["a=1", "b=2"]


def test_http_client_construct_and_callbacks_wired() -> None:
    """Standalone construction — verifies the binding's ctor + that on_*
    callbacks accept a callable. No actual request is fired here."""
    client = wt.Http.Client()
    assert client.timeout_seconds > 0
    assert client.maximum_response_size > 0

    # Setters should round-trip.
    client.set_timeout_seconds(2.5)
    assert client.timeout_seconds == pytest.approx(2.5)

    client.set_maximum_response_size(1024)
    assert client.maximum_response_size == 1024

    # Connecting a callback returns a Connection — exercises py_connect
    # for the headers/body signals.
    def noop(*args):
        pass
    c1 = client.on_done(noop)
    c2 = client.on_headers_received(noop)
    c3 = client.on_body_data_received(noop)
    assert all(c is not None for c in (c1, c2, c3))


def test_http_client_parse_url() -> None:
    parsed = wt.Http.Client.parse_url("https://user:pw@example.com:8443/x")
    assert parsed is not None
    assert parsed.protocol == "https"
    assert parsed.host == "example.com"
    assert parsed.port == 8443
    assert parsed.path == "/x"

    assert wt.Http.Client.parse_url("not a url") is None


def test_http_method_enum() -> None:
    for name in ("Get", "Post", "Put", "Delete", "Patch", "Head"):
        assert hasattr(wt.Http.Method, name)


def test_nested_aliases() -> None:
    """`wt.Http.Message.Header` and `wt.Http.Client.URL` are re-attached
    for symmetry with Wt's nested C++ class structure."""
    assert wt.Http.Message.Header is wt.Http.Header
    assert wt.Http.Client.URL is wt.Http.ClientURL
