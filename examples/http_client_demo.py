"""Outbound HTTP from a Wt UI — click a button, fetch a URL, show the response.

Run with:

    python examples/http_client_demo.py --docroot . --http-address 0.0.0.0 --http-port 8080

Then open http://localhost:8080. Type a URL and click Fetch; the
status, content-type, and body show up below.

This demonstrates the *client-side* HTTP binding:

  - `wt.Http.Client`: outbound async HTTP client (GET/POST/PUT/PATCH/DELETE).
  - `wt.Http.Message`: the request body you send AND the response object
    you read on completion.

For the *server-side* counterpart (incoming requests to YOUR Wt app),
see `examples/hello_with_api.py` which uses `wt.CallbackResource` plus
`wt.Http.Request` / `wt.Http.Response`.
"""

from __future__ import annotations

import sys

import witty_for_python as wt


def create_app(env: wt.WEnvironment) -> wt.WApplication:
    app = wt.WApplication(env)
    app.title = "Http.Client demo"
    root = app.root

    root.add_widget("<h2>Outbound HTTP from inside Wt</h2>")
    root.add_widget(
        "<p>Type a URL and click Fetch. The request is issued through "
        "<code>wt.Http.Client</code>; when the response arrives the UI "
        "updates with status / content-type / body. Try "
        "<code>https://httpbin.org/get?hello=world</code> for a quick "
        "round-trip, or your own internal service.</p>"
    )

    url = root.add_widget(wt.WLineEdit())
    url.text = "https://httpbin.org/get?hello=world"
    url.set_width(420)

    fetch = root.add_widget(wt.WPushButton("Fetch"))
    root.add_widget(wt.WBreak())

    status_label = root.add_widget(wt.WText(""))
    root.add_widget(wt.WBreak())
    ctype_label = root.add_widget(wt.WText(""))
    root.add_widget(wt.WBreak())
    body_label = root.add_widget(wt.WText(""))

    # Keep the client alive across requests by stashing it on the app.
    # The Http.Client instance pins its done callback (via the binding's
    # connection registry), so a fresh one per request would lose state.
    client = wt.Http.Client()
    client.set_timeout_seconds(10)
    # Hold one ref on the Python side so the wrapper outlives this scope.
    app._client = client  # type: ignore[attr-defined]

    def on_fetch() -> None:
        target = url.text
        status_label.text = f"Fetching {target}…"
        ctype_label.text = ""
        body_label.text = ""
        # defer_rendering blocks the *next* server-initiated update until
        # resume_rendering fires — but for plain click handlers Wt
        # already drives the UI repaint after on_done runs, so we don't
        # need it here. Defer is for the case where the request must
        # complete before create_app itself returns.
        if not client.get(target):
            status_label.text = f"Invalid URL: {target}"

    fetch.clicked.connect(on_fetch)

    def on_done(err: str, response: wt.Http.Message) -> None:
        if err:
            status_label.text = f"Error: {err}"
            return
        status_label.text = f"Status: {response.status}"
        ctype = response.get_header("Content-Type") or "(no Content-Type)"
        ctype_label.text = f"Content-Type: {ctype}"
        body = response.body
        # Truncate for the UI — full body is still in `response.body`.
        if len(body) > 2000:
            body = body[:2000] + " …(truncated)"
        body_label.text = f"<pre>{body}</pre>"
        # The Wt event loop normally repaints after a slot returns, but
        # the Http.Client done callback runs asynchronously (it's not the
        # response to a user event), so we have to push the update.
        wt.WApplication.instance().trigger_update()

    client.on_done(on_done)

    return app


def main(argv: list[str]) -> int:
    if not any(a == "--resources-dir" or a.startswith("--resources-dir=")
               for a in argv[1:]):
        argv = argv + ["--resources-dir", wt.resources_dir]
    server = wt.WServer()
    server.set_server_configuration(argv)
    server.add_entry_point(wt.EntryPointType.Application, create_app)
    return server.run()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
