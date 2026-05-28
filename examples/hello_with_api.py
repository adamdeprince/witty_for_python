"""Hello-world Wt UI + a curl-able HTTP endpoint, side by side.

Run with:

    python examples/hello_with_api.py --docroot . --http-address 0.0.0.0 --http-port 8080

Then point a browser at <http://localhost:8080> for the UI, and
`curl http://localhost:8080/api/state` for the dynamic JSON endpoint.

The endpoint is a `wt.CallbackResource` — a thin C++ adaptor that
forwards every request to a Python callable on the Wt worker thread
(with the GIL acquired). The callback gets a `HttpRequest` (method,
query params, headers, body, …) and a `HttpResponse` (status,
mime-type, write) — both valid only for the duration of the call.
"""

from __future__ import annotations

import json
import sys

import witty_for_python as wt


# Process-wide state the UI mutates and the endpoint publishes.
_state = {"counter": 0, "message": "hello, world"}


def handle_state(req: wt.HttpRequest, resp: wt.HttpResponse) -> None:
    """Serve the current state. Echoes a few request fields too, so the
    demo doubles as a quick check that headers/params/body land in
    Python correctly."""
    body = {
        **_state,
        "request": {
            "method": req.method,
            "query": dict(req.parameters),
            "client": req.client_address,
            "user_agent": req.user_agent,
        },
    }
    resp.set_mime_type("application/json")
    resp.write(json.dumps(body, indent=2).encode())


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
    bump.clicked.connect(on_bump)

    def on_set_msg() -> None:
        _state["message"] = message.text
    set_msg.clicked.connect(on_set_msg)

    return app


def main(argv: list[str]) -> int:
    if not any(a == "--resources-dir" or a.startswith("--resources-dir=")
               for a in argv[1:]):
        argv = argv + ["--resources-dir", wt.resources_dir]

    server = wt.WServer()
    server.set_server_configuration(argv)
    server.add_entry_point(wt.EntryPointType.Application, create_app)
    server.add_resource(wt.CallbackResource(handle_state), "/api/state")
    return server.run()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
