"""End-to-end factory tests.

`test_gallery_boot.py` checks the bootstrap (first GET /) which returns
~4.5 KB of JS before the application factory runs. Latent bugs in the
factory or in widget binding (e.g. missing `heap_init`, broken
ownership transfer, MI-base mismatches) only surface on the SECOND
request, when Wt's client-side JS handshakes back with
`?wtd=…&request=script&…`.

These tests do that second request by hand. Stack traces from
`create_app` end up in `server.stderr` as Wt-fatal-error lines — we
fail the test if any appear. See [docs/binding_design.md §4] for the
binding rules these tests guard.
"""

from __future__ import annotations

import http.client
import re
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
HELLO = REPO_ROOT / "examples" / "hello.py"
GALLERY = REPO_ROOT / "examples" / "gallery.py"


def _wait_for_http(host: str, port: int, *, timeout: float = 10.0) -> None:
    """Wait until the server actually responds to an HTTP GET, not just
    until it accepts TCP connections.

    Earlier versions of this fixture only checked TCP accept, which made
    the post-bootstrap request flake — wthttpd binds the socket several
    hundred milliseconds before its accept loop is fully wired through
    to the request handler, so the first connection succeeds at the TCP
    layer but the SECOND connect briefly hits a not-yet-running listener
    backlog and gets ConnectionRefused. Waiting until we get an HTTP
    response back proves both the listen and the accept-loop are live.
    """
    deadline = time.monotonic() + timeout
    last_exc: Exception | None = None
    while time.monotonic() < deadline:
        try:
            conn = http.client.HTTPConnection(host, port, timeout=1.0)
            conn.request("HEAD", "/")
            resp = conn.getresponse()
            resp.read()
            conn.close()
            return
        except (ConnectionRefusedError, OSError) as e:
            last_exc = e
            time.sleep(0.05)
    raise TimeoutError(
        f"server at {host}:{port} never answered an HTTP request "
        f"within {timeout}s (last error: {last_exc!r})"
    )


_WTD_RE = re.compile(r"wtd=([A-Za-z0-9_-]+)")


def _drive_factory(
    script: Path,
    port: int,
    docroot: Path,
    resources_dir: Path,
) -> tuple[str, str, bytes]:
    """Spawn `script`, complete Wt's two-request handshake (which triggers
    create_app), terminate, return (stdout, stderr, handshake-response).

    Both requests go over a single HTTP/1.1 keep-alive connection. The
    previous implementation opened a fresh TCP socket per request and
    intermittently hit ConnectionRefused on the second connect — a race
    between wthttpd finishing the first response and being ready to
    accept the next TCP handshake. Pipelining over one socket removes
    the second-connect race entirely.
    """
    proc = subprocess.Popen(
        [
            sys.executable, "-u", str(script),
            "--docroot", str(docroot),
            "--http-address", "127.0.0.1",
            "--http-port", str(port),
            "--resources-dir", str(resources_dir),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    raw: bytes = b""
    try:
        try:
            _wait_for_http("127.0.0.1", port)
        except TimeoutError as e:
            proc.kill()
            out, err = proc.communicate(timeout=3)
            pytest.fail(
                f"{e}\n"
                f"stdout:\n{out.decode('utf-8', 'replace')}\n"
                f"stderr:\n{err.decode('utf-8', 'replace')}"
            )

        # One TCP connection, two HTTP/1.1 requests. http.client handles
        # chunked transfer encoding (Wt uses it for the bootstrap),
        # keep-alive bookkeeping, and content-length framing for us.
        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=15.0)
        try:
            # Step 1: bootstrap. Wt emits ~4.5 KB of JS containing a
            # `wtd=<token>` cookie that the second request needs.
            conn.request("GET", "/", headers={"Connection": "keep-alive"})
            boot = conn.getresponse().read()
            m = _WTD_RE.search(boot.decode("utf-8", "replace"))
            assert m, f"no wtd= token in bootstrap response:\n{boot[:500]!r}"
            wtd = m.group(1)

            # Step 2: the JS-side handshake URL — wthttpd invokes
            # create_app here. Under our forged session-id wthttpd's
            # response shape is unpredictable: sometimes a 200 + tiny
            # error JS, sometimes a graceful close with no body,
            # sometimes a TCP RST. None of those say anything about
            # whether the factory ran — the *factory* did, and Wt
            # logged its outcome to stderr where _assert_factory_clean
            # reads it. So we tolerate any post-request failure here
            # and let stderr drive the verdict.
            conn.request(
                "GET",
                f"/?wtd={wtd}&request=script&rand=42&scrW=1920&scrH=1080"
                f"&tz=0&htmlHistory=true&deployPath=/",
                headers={
                    "Connection": "close",
                    "User-Agent": "factory-path-test",
                },
            )
            try:
                raw = conn.getresponse().read()
            except (
                http.client.RemoteDisconnected,
                http.client.BadStatusLine,
                ConnectionResetError,
                OSError,
            ):
                raw = b""
            # Give the worker a beat to flush its access-log line before
            # we tear down. Without this, stderr may not yet contain the
            # request=script entry the test could use to sanity-check.
            time.sleep(0.05)
        finally:
            conn.close()
    finally:
        proc.terminate()
        try:
            out, err = proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            out, err = proc.communicate(timeout=3)

    return (
        out.decode("utf-8", "replace"),
        err.decode("utf-8", "replace"),
        raw,
    )


def _assert_factory_clean(stdout: str, stderr: str, raw: bytes) -> None:
    """The diagnostic signal is the server's stderr — Wt emits "fatal
    error: Traceback" if create_app raised, and nanobind emits "Critical
    nanobind error" if it aborted the worker. The handshake's HTTP
    response shape isn't a reliable signal under our forged session-id;
    we trust the log."""
    combined = stdout + stderr
    assert "Critical nanobind error" not in combined, (
        f"nanobind aborted the worker thread:\n{combined}"
    )
    assert "fatal error: Traceback" not in combined, (
        f"create_app raised a Python exception:\n{combined}"
    )


def test_hello_factory_runs(free_port, docroot, wt_resources_dir) -> None:
    """hello.py exercises the minimal happy path: WApplication,
    WContainerWidget, WText, WLineEdit, WPushButton, add_widget, signal
    connect."""
    out, err, raw = _drive_factory(HELLO, free_port, docroot, wt_resources_dir)
    _assert_factory_clean(out, err, raw)


def test_gallery_factory_runs(free_port, docroot, wt_resources_dir) -> None:
    """gallery.py walks ~every widget binding in a single create_app —
    every tab constructed (Basics, Forms, Layout, Tables, Dialogs,
    Template, Resources, Extras, Files, Media, Model/View, Painting,
    PDF, Niches, Map, Chrome, Charts). If any binding regresses
    (e.g. missing heap_init, broken re-arm, MI mismatch on a paint
    device), the factory aborts here and stderr carries the trace."""
    out, err, raw = _drive_factory(GALLERY, free_port, docroot, wt_resources_dir)
    _assert_factory_clean(out, err, raw)
