"""Minimal witty_for_python hello-world.

Run with:

    python examples/hello.py --docroot . --http-address 0.0.0.0 --http-port 8080

Then point a browser at http://localhost:8080.
"""

from __future__ import annotations

import sys

import witty_for_python as wt


def create_app(env: wt.WEnvironment) -> wt.WApplication:
    app = wt.WApplication(env)
    app.title = "witty_for_python hello"

    root = app.root

    # Ownership transfers into `root` on add_widget — rebind to the returned
    # non-owning handle so we can keep using the widget below.
    greeting = root.add_widget(wt.WText("Hello, witty_for_python!"))

    name = root.add_widget(wt.WLineEdit())
    name.placeholder = "Your name"

    button = root.add_widget(wt.WPushButton("Greet"))

    def on_click() -> None:
        who = name.text or "anonymous"
        greeting.text = f"Hello, {who}!"

    button.clicked.connect(on_click)
    return app


def main(argv: list[str]) -> int:
    server = wt.WServer()
    server.set_server_configuration(argv)
    server.add_entry_point(wt.EntryPointType.Application, create_app)
    return server.run()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
