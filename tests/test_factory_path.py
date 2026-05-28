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


def _drive_factory(
    script: Path,
    port: int,
    docroot: Path,
    resources_dir: Path,
) -> tuple[str, str, bytes]:
    """Spawn `script`, complete Wt's two-request handshake (which triggers
    create_app), terminate, return (stdout, stderr, handshake-response).
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
    try:
        if not _wait_for_port("127.0.0.1", port):
            proc.kill()
            out, err = proc.communicate(timeout=3)
            pytest.fail(
                f"server failed to bind 127.0.0.1:{port}\n"
                f"stdout:\n{out.decode('utf-8', 'replace')}\n"
                f"stderr:\n{err.decode('utf-8', 'replace')}"
            )

        # Step 1: bootstrap. Pull the wtd session token from the JS.
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect(("127.0.0.1", port))
            s.sendall(
                b"GET / HTTP/1.0\r\nHost: 127.0.0.1\r\n"
                b"Connection: close\r\n\r\n"
            )
            boot = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                boot += chunk
        m = _WTD_RE.search(boot.decode("utf-8", "replace"))
        assert m, f"no wtd= token in bootstrap response:\n{boot[:500]!r}"
        wtd = m.group(1)

        # Step 2: the JS-side handshake URL — Wt invokes `create_app` here.
        # urllib's connection-handling raises RemoteDisconnected on Wt's
        # session-cleanup path, so we use a raw socket and trust the stderr
        # log to tell us whether the factory ran.
        handshake = (
            f"GET /?wtd={wtd}&request=script&rand=42"
            f"&scrW=1920&scrH=1080&tz=0&htmlHistory=true&deployPath=/ "
            f"HTTP/1.0\r\nHost: 127.0.0.1\r\n"
            f"User-Agent: factory-path-test\r\n"
            f"Connection: close\r\n\r\n"
        )
        # The handshake occasionally races with wthttpd's session
        # bookkeeping — between bootstrap and handshake the server may
        # briefly refuse TCP connections, or accept then close without
        # responding. Retry with growing backoff; the factory running is
        # what we care about, and the request is idempotent.
        raw = b""
        last_exc: Exception | None = None
        for attempt in range(8):
            if attempt > 0:
                time.sleep(0.25 * attempt)
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(15)
                    s.connect(("127.0.0.1", port))
                    s.sendall(handshake.encode())
                    raw = b""
                    while True:
                        chunk = s.recv(4096)
                        if not chunk:
                            break
                        raw += chunk
            except (ConnectionRefusedError, ConnectionResetError, OSError) as e:
                last_exc = e
                raw = b""
                continue
            if raw:
                break
        if not raw and last_exc is not None:
            raise last_exc
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
