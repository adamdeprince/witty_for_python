"""End-to-end test for `wt.CallbackResource` — Python callable serving HTTP.

Spawns a small Wt server with the example's CallbackResource pattern,
hits the endpoint with several requests, asserts the callback observed
the request data correctly and the response made it back to the client.
This is the only test that exercises the `Wt::Http::Request` /
`Wt::Http::Response` bindings end-to-end.
"""

from __future__ import annotations

import json
import socket
import subprocess
import sys
import time
from pathlib import Path
from textwrap import dedent

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent


def _wait_for_port(host: str, port: int, *, timeout: float = 6.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.25)
            try:
                s.connect((host, port))
                return True
            except OSError:
                time.sleep(0.1)
    return False


def _http_get(host: str, port: int, path: str, *, retries: int = 5) -> bytes:
    """Tiny HTTP/1.0 GET via raw socket. Returns the response body
    (everything after the empty line separator). Retries on transient
    refusals — wthttpd briefly closes new connections while it's
    processing the prior one."""
    last_exc: Exception | None = None
    for attempt in range(retries):
        if attempt > 0:
            time.sleep(0.2 * attempt)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect((host, port))
                s.sendall(
                    f"GET {path} HTTP/1.0\r\n"
                    f"Host: {host}\r\n"
                    f"User-Agent: callback-resource-test\r\n"
                    f"Connection: close\r\n\r\n".encode()
                )
                raw = b""
                while True:
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    raw += chunk
        except (ConnectionRefusedError, ConnectionResetError, OSError) as e:
            last_exc = e
            continue
        if raw:
            head, _, body = raw.partition(b"\r\n\r\n")
            return body
    if last_exc is not None:
        raise last_exc
    return b""


def test_callback_resource_serves_dynamic_response(
    tmp_path: Path, free_port: int, docroot: Path, wt_resources_dir: Path,
) -> None:
    """`wt.CallbackResource(callable)` mounted at `/api/echo` should:
       - invoke the callable on each request,
       - hand it a working `HttpRequest` (method / parameters / etc.)
         and `HttpResponse` (set_mime_type / write),
       - serve the callable's return back to the client."""
    script = tmp_path / "server.py"
    script.write_text(dedent("""\
        import json
        import sys
        import witty_for_python as wt

        hits = [0]

        def echo(req, resp):
            hits[0] += 1
            resp.set_mime_type("application/json")
            resp.write(json.dumps({
                "method": req.method,
                "query": dict(req.parameters),
                "hits": hits[0],
                "path": req.path,
            }).encode())

        def create_app(env):
            app = wt.WApplication(env)
            return app

        argv = sys.argv + ["--resources-dir", wt.resources_dir]
        server = wt.WServer()
        server.set_server_configuration(argv)
        server.add_entry_point(wt.EntryPointType.Application, create_app)
        server.add_resource(wt.CallbackResource(echo), "/api/echo")
        sys.exit(server.run())
    """))

    proc = subprocess.Popen(
        [
            sys.executable, "-u", str(script),
            "--docroot", str(docroot),
            "--http-address", "127.0.0.1",
            "--http-port", str(free_port),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        assert _wait_for_port("127.0.0.1", free_port), "server failed to bind"
        body1 = _http_get(
            "127.0.0.1", free_port, "/api/echo?name=alice&n=1&n=2")
        body2 = _http_get("127.0.0.1", free_port, "/api/echo")
        body3 = _http_get("127.0.0.1", free_port, "/api/echo")
    finally:
        proc.terminate()
        try:
            out, err = proc.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            out, err = proc.communicate(timeout=3)

    err_s = err.decode("utf-8", "replace")
    assert "Critical nanobind error" not in err_s, err_s
    assert "fatal error: Traceback" not in err_s, err_s

    j1 = json.loads(body1)
    j2 = json.loads(body2)
    j3 = json.loads(body3)
    assert j1["method"] == "GET"
    assert j1["query"] == {"name": ["alice"], "n": ["1", "2"]}
    assert j1["path"] == "/api/echo"
    # hits counter should grow across requests (proves state persists in
    # the closure rather than being a per-request copy).
    assert j1["hits"] == 1
    assert j2["hits"] == 2
    assert j3["hits"] == 3
