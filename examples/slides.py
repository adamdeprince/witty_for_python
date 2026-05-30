"""A 5-page slide-sheet demo for witty_for_python.

Each slide uses the `wfp-slides` CSS classes from
`witty_wt_slide_theme.css` (which lives next to this script — the
demo serves it via `WServer.add_resource`). Navigation is two
buttons in the bottom-left and bottom-right corners; clicking them
flips a `WStackedWidget` IN-PLACE — no URL change, no page reload,
no second session. Wt's AJAX layer pushes the DOM diff over the
existing session's websocket.

Run with:

    python examples/slides.py --docroot . --http-address 127.0.0.1 --http-port 8080

then open http://localhost:8080.

(If you have witty_for_python installed but not the source tree:
copy `examples/slides.py` + `examples/witty_wt_slide_theme.css` to
the same directory and `python slides.py --docroot . ...`. The CSS
lives next to the script; `examples/` is intentionally NOT shipped
inside the wheel.)
"""

from __future__ import annotations

import sys
from pathlib import Path

import witty_for_python as wt


HERE = Path(__file__).resolve().parent
CSS_PATH = HERE / "witty_wt_slide_theme.css"


# ---- Slide content -------------------------------------------------------
#
# Each slide is a callable taking a fresh WContainerWidget and filling it.
# Add or remove entries to change the deck length — the navigation chrome
# discovers slide count from this list.

def slide_1_title(body: wt.WContainerWidget) -> None:
    body.add_widget(
        '<div class="wfp-kicker">witty_for_python</div>'
        '<h1 class="wfp-slide-title">Wt, in Python.</h1>'
        '<p class="wfp-slide-subtitle">A 5-slide tour of what the bindings'
        ' get you, driven from the keyboard.</p>'
        '<p style="margin-top: 1em" class="wfp-muted">'
        'Press the <code>next →</code> link in the lower-right corner to'
        ' advance.</p>'
    )


def slide_2_what(body: wt.WContainerWidget) -> None:
    body.add_widget(
        '<div class="wfp-kicker">What it is</div>'
        '<h2 class="wfp-slide-title" style="font-size: clamp(28px, 3vw, 40px)">'
        'Python bindings for the Wt C++ web framework, generated with'
        ' nanobind.</h2>'
        '<ul style="margin-top: 1.2em">'
        '<li>Build a full server-rendered UI in pure Python.</li>'
        '<li>Construct widgets, lay them out, connect signals, return'
        ' a <code>WApplication</code> from a factory.</li>'
        '<li>Wheels bundle Wt 4.13.2 + TinyMCE — no external Wt install.</li>'
        '</ul>'
    )


def slide_3_code(body: wt.WContainerWidget) -> None:
    body.add_widget(
        '<div class="wfp-kicker">A working app, in 12 lines</div>'
        '<pre class="wfp-code">'
        'import witty_for_python as wt\n\n'
        'def create_app(env):\n'
        '    app = wt.WApplication(env)\n'
        '    button = app.root.add_widget(wt.WPushButton("Click me"))\n'
        '    label  = app.root.add_widget(wt.WText(""))\n'
        '    button.clicked.connect(lambda: setattr(label, "text", "clicked!"))\n'
        '    return app\n\n'
        'server = wt.WServer()\n'
        'server.set_server_configuration(["app", "--http-port=8080"])\n'
        'server.add_entry_point(wt.EntryPointType.Application, create_app)\n'
        'server.run()'
        '</pre>'
    )


def slide_4_features(body: wt.WContainerWidget) -> None:
    body.add_widget(
        '<div class="wfp-kicker">What ships</div>'
        '<h2 class="wfp-slide-title" style="font-size: clamp(28px, 3vw, 40px)">'
        '90+ widget classes, three submodules.</h2>'
    )
    grid = body.add_widget(wt.WContainerWidget())
    grid.style_class = "wfp-three-col"
    grid.add_widget(
        '<div class="wfp-card">'
        '<div class="wfp-card-title">Widgets</div>'
        'Forms, layouts, tables, dialogs, menus, model/view, navigation,'
        ' file drop, themes, painting, charts.'
        '</div>'
    )
    grid.add_widget(
        '<div class="wfp-card">'
        '<div class="wfp-card-title"><code>wt.Http</code></div>'
        'Outbound HTTP client + server-side request/response for'
        ' <code>CallbackResource</code>-mounted endpoints.'
        '</div>'
    )
    grid.add_widget(
        '<div class="wfp-card">'
        '<div class="wfp-card-title"><code>wt.chart</code> / <code>wt.Json</code></div>'
        'Cartesian and pie charts; a Wt::Json binding for Leaflet map'
        ' options and anything else that wants structured JSON.'
        '</div>'
    )


def slide_5_close(body: wt.WContainerWidget) -> None:
    body.add_widget(
        '<div class="wfp-kicker">That\'s the deck</div>'
        '<h1 class="wfp-slide-title">Try it.</h1>'
        '<p class="wfp-slide-subtitle">Run any of the examples in'
        ' <code>examples/</code> to see the bindings in motion.</p>'
        '<div class="wfp-callout" style="margin-top: 1.5em">'
        '<code>python examples/gallery.py --docroot . --http-port 8080</code>'
        ' walks ~every binding in a single page.'
        '</div>'
    )


SLIDES: list[tuple[str, callable]] = [
    ("Title",     slide_1_title),
    ("What",      slide_2_what),
    ("Hello",     slide_3_code),
    ("Features",  slide_4_features),
    ("Close",     slide_5_close),
]


# ---- Wt app --------------------------------------------------------------

def _build_slide(
    index: int,
    total: int,
    on_prev: callable,
    on_next: callable,
) -> wt.WContainerWidget:
    """Construct one slide widget — header, body via the slide content
    callable, footer with prev/next buttons whose clicked signals
    flip the parent WStackedWidget via the passed-in callbacks."""
    slide = wt.WContainerWidget()
    slide.style_class = "wfp-slide"

    # Header: empty container so the grid template (auto/1fr/auto)
    # reserves the row even when the slide doesn't explicitly fill it.
    header = slide.add_widget(wt.WContainerWidget())
    header.style_class = "wfp-slide-header"

    # Body — the slide's actual content.
    body = slide.add_widget(wt.WContainerWidget())
    body.style_class = "wfp-slide-body"
    _, builder = SLIDES[index]
    builder(body)

    # Footer with prev/next buttons at the bottom corners. The CSS uses
    # `display: flex; justify-content: space-between` on .wfp-slide-footer,
    # so a single prev on the left + single next on the right naturally
    # pin to the corners.
    footer = slide.add_widget(wt.WContainerWidget())
    footer.style_class = "wfp-slide-footer"

    # In-app navigation: the buttons emit Wt's `clicked` signal, which
    # we route to the deck-flipping callback. No URL navigation, no
    # second session — Wt's AJAX layer pushes the DOM diff to the
    # existing session over its websocket. WPushButton is used (not
    # WAnchor) because anchors imply a navigation, and we want pure
    # in-app click handlers.
    prev = footer.add_widget(wt.WPushButton("← prev"))
    prev.style_class = "wfp-nav-prev"
    if index == 0:
        prev.hidden = True
    prev.clicked.connect(on_prev)

    counter = footer.add_widget(wt.WText(f"{index + 1} / {total}"))
    counter.style_class = "wfp-muted"

    next_ = footer.add_widget(wt.WPushButton("next →"))
    next_.style_class = "wfp-nav-next"
    if index == total - 1:
        next_.hidden = True
    next_.clicked.connect(on_next)

    return slide


def create_app(env: wt.WEnvironment) -> wt.WApplication:
    app = wt.WApplication(env)
    app.title = "witty_for_python — slide deck"
    # The theme expects `wfp-slides` on body (it scopes everything under
    # that selector). Wt's `body_html_class` hook would be cleaner but
    # isn't bound — the root container's class_ propagates via Wt's
    # `<div class="…" id="Wt-app">` instead, which the CSS selectors
    # also match (`.wfp-slides .Wt-domRoot`).
    app.root.style_class = "wfp-slides"

    # Pull in the CSS the user wrote. We mounted it on the server below
    # under /witty_wt_slide_theme.css; use_style_sheet drops a
    # <link rel="stylesheet" href="..."> into <head>.
    app.use_style_sheet(wt.WLink("/witty_wt_slide_theme.css"))

    # The deck stage centres the slides on the page (CSS uses
    # `place-items: center` on .wfp-slide-stage).
    stage = app.root.add_widget(wt.WContainerWidget())
    stage.style_class = "wfp-slide-stage"

    deck = stage.add_widget(wt.WStackedWidget())
    total = len(SLIDES)

    # Build each slide. We pass each one a pair of callbacks that
    # know which direction to flip the stack — capturing the slide's
    # index in the closure avoids relying on `deck.current_index`
    # being correct when the click fires (e.g., if the user
    # rapid-clicks past a slide).
    def make_handlers(i: int) -> tuple[callable, callable]:
        def prev() -> None:
            deck.current_index = max(0, i - 1)
        def nxt() -> None:
            deck.current_index = min(total - 1, i + 1)
        return prev, nxt

    for i in range(total):
        on_prev, on_next = make_handlers(i)
        deck.add_widget(_build_slide(i, total, on_prev, on_next))

    return app


def main(argv: list[str]) -> int:
    if not any(a == "--resources-dir" or a.startswith("--resources-dir=")
               for a in argv[1:]):
        argv = argv + ["--resources-dir", wt.resources_dir]

    if not CSS_PATH.is_file():
        sys.stderr.write(
            f"slide theme CSS not found at {CSS_PATH}\n"
            "Put `witty_wt_slide_theme.css` next to this script.\n"
        )
        return 2

    server = wt.WServer()
    server.set_server_configuration(argv)
    server.add_entry_point(wt.EntryPointType.Application, create_app)

    # Serve the CSS file. We could host it via Wt's docroot, but
    # WMemoryResource + add_resource is self-contained: no copy of the
    # CSS into the docroot, the file's contents are read once at
    # startup and served from RAM thereafter.
    css = wt.WMemoryResource("text/css", CSS_PATH.read_bytes())
    server.add_resource(css, "/witty_wt_slide_theme.css")

    # Tell the user where to look. Pull host/port out of argv if they
    # passed them (default printout assumes 0.0.0.0:8080).
    host = "127.0.0.1"
    port = "8080"
    for i, a in enumerate(argv[1:]):
        if a == "--http-address" and i + 2 < len(argv):
            host = argv[i + 2]
        elif a.startswith("--http-address="):
            host = a.split("=", 1)[1]
        elif a == "--http-port" and i + 2 < len(argv):
            port = argv[i + 2]
        elif a.startswith("--http-port="):
            port = a.split("=", 1)[1]
    display_host = "localhost" if host in ("0.0.0.0", "127.0.0.1") else host
    print(
        f"\n  Slide deck ready.\n"
        f"  Open:   http://{display_host}:{port}/\n"
        f"  Deck:   {len(SLIDES)} slides; ←/→ buttons in the footer corners.\n"
        f"  Each button click flips the WStackedWidget in place — no\n"
        f"  page reload, no new session.\n",
        flush=True,
    )

    return server.run()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
