"""
Wt::Http — HTTP types shared by WResource handlers (Request, Response) and the outbound client (Message, Client, Method, Header).
"""

from collections.abc import Callable, Sequence
import enum
from typing import TypeAlias, overload

import witty_for_python._witty_for_python


class Request:
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
    def query_string(self) -> str: ...

    @property
    def url_scheme(self) -> str: ...

    @property
    def content_type(self) -> str: ...

    @property
    def content_length(self) -> int: ...

    @property
    def user_agent(self) -> str: ...

    @property
    def client_address(self) -> str: ...

    @property
    def host_name(self) -> str: ...

    @property
    def server_name(self) -> str: ...

    @property
    def server_port(self) -> str: ...

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
    def set_status(self, status: int) -> None:
        """Set the HTTP status code (default 200)."""

    def set_content_length(self, length: int) -> None: ...

    def set_mime_type(self, mime_type: str) -> None:
        """Set the Content-Type. After this (or any write) headers are committed."""

    def add_header(self, name: str, value: str) -> None: ...

    def insert_header(self, name: str, value: str) -> None:
        """Set an HTTP header, replacing any earlier value with the same name."""

    @overload
    def write(self, data: bytes) -> None:
        """Write `bytes` to the response body."""

    @overload
    def write(self, data: str) -> None:
        """Write a `str` (UTF-8) to the response body."""

class Method(enum.Enum):
    Get = 0

    Post = 1

    Put = 2

    Delete = 3

    Patch = 4

    Head = 5

class Header:
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, name: str, value: str) -> None: ...

    @property
    def name(self) -> str: ...

    @name.setter
    def name(self, arg: str, /) -> None: ...

    @property
    def value(self) -> str: ...

    @value.setter
    def value(self, arg: str, /) -> None: ...

class Message:
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

    def set_status(self, status: int) -> None: ...

    class Header:
        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, name: str, value: str) -> None: ...

        @property
        def name(self) -> str: ...

        @name.setter
        def name(self, arg: str, /) -> None: ...

        @property
        def value(self) -> str: ...

        @value.setter
        def value(self, arg: str, /) -> None: ...

class ClientURL:
    @property
    def protocol(self) -> str: ...

    @property
    def auth(self) -> str: ...

    @property
    def host(self) -> str: ...

    @property
    def port(self) -> int: ...

    @property
    def path(self) -> str: ...

class Client(witty_for_python._witty_for_python.WObject):
    def __init__(self) -> None:
        """
        Construct using the current WApplication's I/O service. Call from within a WApplication context (e.g. inside a create_app factory or a slot fired by a session).
        """

    def set_timeout_seconds(self, seconds: float) -> None:
        """
        Per-I/O-operation timeout. Resets on each progress event, so total request time can exceed this. Default 10 seconds.
        """

    @property
    def timeout_seconds(self) -> float: ...

    def set_maximum_response_size(self, bytes: int) -> None:
        """
        Cap on the in-memory response size (DoS guard). Default 64 KiB. A value of 0 disables the limit AND prevents the body from being accumulated into the HttpMessage — use on_body_data_received to process chunks incrementally.
        """

    @property
    def maximum_response_size(self) -> int: ...

    def set_ssl_certificate_verification_enabled(self, enabled: bool) -> None:
        """
        Verify the server's TLS certificate (https only). Default True — only disable for testing against self-signed certs.
        """

    @property
    def ssl_certificate_verification_enabled(self) -> bool: ...

    def set_ssl_verify_file(self, path: str) -> None: ...

    def set_ssl_verify_path(self, path: str) -> None: ...

    def set_follow_redirect(self, follow: bool) -> None: ...

    @property
    def follow_redirect(self) -> bool: ...

    def set_max_redirects(self, max_redirects: int) -> None: ...

    @property
    def max_redirects(self) -> int: ...

    @overload
    def get(self, url: str) -> bool:
        """
        Start an async GET. Returns False if the URL was malformed or the scheme unsupported; True if the request was scheduled (the done callback will fire when it completes).
        """

    @overload
    def get(self, url: str, headers: Sequence[Header]) -> bool:
        """GET with custom request headers."""

    def head(self, url: str) -> bool: ...

    def post(self, url: str, message: Message) -> bool:
        """POST. Build the request body as an HttpMessage first."""

    def put(self, url: str, message: Message) -> bool: ...

    def delete_request(self, url: str, message: Message) -> bool:
        """
        Issue a DELETE. Named `delete_request` because `delete` is a Python keyword.
        """

    def patch(self, url: str, message: Message) -> bool: ...

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
