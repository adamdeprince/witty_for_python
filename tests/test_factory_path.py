"""End-to-end factory test: spawn `hello.py`, complete Wt's two-step
handshake so `create_app` actually runs, assert no error in stderr.

`test_gallery_boot.py` checks the bootstrap (first GET /) which returns
~4.5 KB of JS before the application factory runs. Latent bugs in the
factory or in widget binding (e.g. missing `heap_init`, broken
ownership transfer) only surface on the SECOND request, when Wt's
client-side JS handshakes back with `?wtd=…&request=script&…`.

This test does that second request by hand. Stack traces from
`create_app` end up in `server.stderr` as Wt-fatal-error lines — we
fail the test if any appear. See [docs/binding_design.md §4] for the
binding rules this test guards.
"""

from __future__ import annotations

import re
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
HELLO = REPO_ROOT / "examples" / "hello.py"


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


_WTD_RE = re.compile(r"wtd=([A-Za-z0-9_-]+)")


def test_hello_factory_runs(free_port, docroot, wt_resources_dir) -> None:
    proc = subprocess.Popen(
        [
            sys.executable, "-u", str(HELLO),
            "--docroot", str(docroot),
            "--http-address", "127.0.0.1",
            "--http-port", str(free_port),
            "--resources-dir", str(wt_resources_dir),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        assert _wait_for_port("127.0.0.1", free_port), \
            f"server failed to bind 127.0.0.1:{free_port}"

        # Step 1: bootstrap. Pull the wtd session token from the JS.
        with urllib.request.urlopen(
            f"http://127.0.0.1:{free_port}/", timeout=5
        ) as resp:
            body = resp.read().decode("utf-8", "replace")
        m = _WTD_RE.search(body)
        assert m, "no wtd= token in bootstrap response"
        wtd = m.group(1)

        # Step 2: the JS-side handshake URL. Wt invokes `create_app` here.
        # We don't bother parsing the response (it's a JS payload binding
        # the Wt session); we just want it to NOT crash the server. If the
        # factory aborts the worker (via nanobind's `Critical nanobind
        # error: ... abort()`), the connection is closed without a
        # response — treat that as a failure that we'll diagnose from the
        # captured stderr.
        # Issue a script-handshake URL via raw socket. urlllib's
        # connection-handling raises RemoteDisconnected on Wt's session
        # cleanup path; what matters is that the server processed the
        # request without aborting — we read the stderr log for that.
        handshake = (
            f"GET /?wtd={wtd}&request=script&rand=42"
            f"&scrW=1920&scrH=1080&tz=0&htmlHistory=true&deployPath=/ "
            f"HTTP/1.0\r\nHost: 127.0.0.1\r\n"
            f"User-Agent: factory-path-test\r\n"
            f"Connection: close\r\n\r\n"
        )
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect(("127.0.0.1", free_port))
            s.sendall(handshake.encode())
            raw = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                raw += chunk
        # Pull the HTTP status line; tolerate either 200 (factory ran +
        # Wt session cleanup error) or any other.
        first_line = raw.split(b"\r\n", 1)[0]
    finally:
        proc.terminate()
        try:
            out, err = proc.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            out, err = proc.communicate(timeout=3)
    out_s = out.decode("utf-8", "replace")
    err_s = err.decode("utf-8", "replace")

    # The handshake response itself is fine even if the factory failed
    # (Wt sends a JS error payload with HTTP 200). What's diagnostic is
    # the server's own log: a healthy factory leaves NO "fatal error"
    # lines in stderr — Wt logs the Python traceback there if create_app
    # raised.
    combined = out_s + err_s
    assert "Critical nanobind error" not in combined, (
        f"nanobind aborted the worker thread:\n{combined}"
    )
    assert 'fatal error: Traceback' not in combined, (
        f"create_app raised a Python exception:\n{combined}"
    )
    # Sanity: the handshake at least produced an HTTP status line.
    assert first_line.startswith(b"HTTP/1.1 ") or first_line.startswith(b"HTTP/1.0 "), (
        f"no HTTP response from handshake (raw={raw[:200]!r}); "
        f"server stderr:\n{err_s}"
    )
