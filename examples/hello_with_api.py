"""Hello-world Wt UI + a curl-able HTTP endpoint, side by side.

Run with:

    python examples/hello_with_api.py --docroot . --http-address 0.0.0.0 --http-port 8080

Then point a browser at <http://localhost:8080> for the UI, and
`curl http://localhost:8080/api/state` for the JSON endpoint.

The endpoint is a `WMemoryResource` mounted on the server. It serves
the same bytes to every client (no per-session state); when the UI
mutates the underlying state it calls `resource.set_changed()` so the
next curl sees the new value.

For dynamic resources whose response is computed per-request, Wt's
intended pattern is a `WResource` subclass overriding
`handle_request(req, resp)`. That requires a Python-side trampoline
nanobind binding which `witty_for_python` does not yet ship — for now,
mutate `WMemoryResource.data` from the UI thread and call
`set_changed()`.
"""

from __future__ import annotations

import json
import sys

import witty_for_python as wt


# Process-wide state the UI mutates and the resource publishes.
_state = {"counter": 0, "message": "hello, world"}


def _serialize() -> bytes:
    return json.dumps(_state, indent=2).encode("utf-8")


# The resource itself. Initial payload is the empty state.
_api = wt.WMemoryResource("application/json", _serialize())


def _publish() -> None:
    """Push the current state to the resource and invalidate caches."""
    _api.data = _serialize()
    _api.set_changed()


def create_app(env: wt.WEnvironment) -> wt.WApplication:
    app = wt.WApplication(env)
    app.title = "hello + /api/state"
    root = app.root

    root.add_widget("<h2>Hello, witty_for_python!</h2>")
    root.add_widget(
        "<p>Try the curl-able endpoint at "
        "<code><a href='/api/state'>/api/state</a></code>. "
        "Click the buttons below; the JSON reflects the latest state.</p>"
    )

    message = root.add_widget(wt.WLineEdit())
    message.text = _state["message"]
    message.placeholder = "Type a new message"

    bump = root.add_widget(wt.WPushButton("Bump counter"))
    set_msg = root.add_widget(wt.WPushButton("Set message"))

    def on_bump() -> None:
        _state["counter"] += 1
        _publish()
    bump.clicked.connect(on_bump)

    def on_set_msg() -> None:
        _state["message"] = message.text
        _publish()
    set_msg.clicked.connect(on_set_msg)

    return app


def main(argv: list[str]) -> int:
    if not any(a == "--resources-dir" or a.startswith("--resources-dir=")
               for a in argv[1:]):
        argv = argv + ["--resources-dir", wt.resources_dir]

    server = wt.WServer()
    server.set_server_configuration(argv)
    server.add_entry_point(wt.EntryPointType.Application, create_app)
    server.add_resource(_api, "/api/state")
    return server.run()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
