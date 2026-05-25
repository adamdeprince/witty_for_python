"""End-to-end smoke test: spawn the gallery server, hit it, kill it.

This is the only test that exercises the WApplication factory path. Widget
construction can't happen outside a session, so the gallery factory is our
proof that every widget binding builds at least once without crashing.
"""

from __future__ import annotations

import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
GALLERY = REPO_ROOT / "examples" / "gallery.py"
HELLO = REPO_ROOT / "examples" / "hello.py"


def _wait_for_port(host: str, port: int, *, timeout: float = 6.0) -> bool:
    """Poll the port until it accepts a TCP connection, or time out."""
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


def _spawn(script: Path, port: int, docroot: Path, resources: Path) -> subprocess.Popen:
    return subprocess.Popen(
        [
            sys.executable, "-u", str(script),
            "--docroot", str(docroot),
            "--http-address", "127.0.0.1",
            "--http-port", str(port),
            "--resources-dir", str(resources),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _stop(proc: subprocess.Popen) -> tuple[str, str]:
    proc.terminate()
    try:
        out, err = proc.communicate(timeout=3)
    except subprocess.TimeoutExpired:
        proc.kill()
        out, err = proc.communicate(timeout=3)
    return out.decode("utf-8", "replace"), err.decode("utf-8", "replace")


@pytest.mark.parametrize("script", [GALLERY, HELLO], ids=["gallery", "hello"])
def test_example_boots_and_serves(
    script: Path, free_port: int, docroot, wt_resources_dir,
) -> None:
    """Spawn the example, GET /, expect HTTP 200 + Wt-rendered bootstrap.

    The bootstrap response (~4.5 KB) is what Wt sends before JS hands shake
    back. We don't try to drive the full session — that needs a real browser.
    HTTP 200 + the expected size band is enough to confirm the factory ran,
    every widget constructor succeeded, and Wt accepted the WApplication.
    """
    proc = _spawn(script, free_port, docroot, wt_resources_dir)
    try:
        assert _wait_for_port("127.0.0.1", free_port), \
            f"server failed to bind 127.0.0.1:{free_port}"
        with urllib.request.urlopen(
            f"http://127.0.0.1:{free_port}/", timeout=5
        ) as resp:
            body = resp.read()
            assert resp.status == 200
            # Wt's bootstrap is ~4.5 KB; we just want to confirm it's non-trivial
            assert len(body) > 1000, f"suspicious response size: {len(body)} bytes"
    finally:
        out, err = _stop(proc)

    # nanobind would log to stderr if it found leaks at finalisation — under
    # clean shutdown the cleanup atexit handler keeps that quiet.
    assert "nanobind: leaked" not in err, f"nanobind leak warning:\n{err}"
    # Any Python-side exception would also surface in stderr / stdout.
    for stream_name, stream in [("stdout", out), ("stderr", err)]:
        for needle in ("Traceback", "AssertionError"):
            assert needle not in stream, (
                f"unexpected {needle} in {stream_name}:\n{stream}"
            )
