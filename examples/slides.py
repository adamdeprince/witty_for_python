"""A 5-page slide-sheet demo for witty_for_python.

Each slide gets the `wfp-slides` family of CSS classes from
`witty_wt_slide_theme.css` (which lives next to this script — the
demo serves it via WServer.add_resource). Navigation is two anchors
sitting in the bottom-left and bottom-right corners of the slide
footer; `prev` and `next` flip the WStackedWidget AND update the
URL fragment (so browser back/forward + reloads land on the right
slide).

Run with:

    python examples/slides.py --docroot . --http-address 127.0.0.1 --http-port 8080

then open http://localhost:8080.

(Or, if you have witty_for_python installed but not the source tree:
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

def _build_slide(index: int, total: int) -> wt.WContainerWidget:
    """Construct one slide widget — header, body via the slide content
    callable, footer with prev/next nav."""
    slide = wt.WContainerWidget()
    slide.style_class = "wfp-slide"

    # Header: just an empty container so the grid template
    # (auto/1fr/auto) reserves the row even when the slide doesn't
    # explicitly fill it.
    header = slide.add_widget(wt.WContainerWidget())
    header.style_class = "wfp-slide-header"

    # Body — the slide's actual content.
    body = slide.add_widget(wt.WContainerWidget())
    body.style_class = "wfp-slide-body"
    name, builder = SLIDES[index]
    builder(body)

    # Footer with prev/next anchors at the bottom corners. The CSS uses
    # `display: flex; justify-content: space-between` on .wfp-slide-footer,
    # so a single prev on the left + single next on the right naturally
    # pin to the corners.
    footer = slide.add_widget(wt.WContainerWidget())
    footer.style_class = "wfp-slide-footer"

    prev = footer.add_widget(wt.WAnchor(
        wt.WLink(f"/{index - 1}" if index > 0 else "/0"),
        "← prev" if index > 0 else " "
    ))
    if index == 0:
        prev.hidden = True

    counter = footer.add_widget(wt.WText(f"{index + 1} / {total}"))
    counter.style_class = "wfp-muted"

    next_ = footer.add_widget(wt.WAnchor(
        wt.WLink(f"/{index + 1}" if index < total - 1 else f"/{index}"),
        "next →" if index < total - 1 else " "
    ))
    if index == total - 1:
        next_.hidden = True

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
    pinned_slides: list[wt.WContainerWidget] = []
    for i in range(len(SLIDES)):
        slide = _build_slide(i, len(SLIDES))
        pinned_slides.append(deck.add_widget(slide))

    # URL ↔ stack-index. Calling set_internal_path with emit_change=False
    # at startup means the initial /N from a deep link lands on the
    # right slide without re-firing the change signal.
    def _go(path: str) -> None:
        # path looks like "/3" or "" for the root.
        try:
            idx = int(path.lstrip("/")) if path else 0
        except ValueError:
            idx = 0
        idx = max(0, min(idx, len(SLIDES) - 1))
        deck.current_index = idx

    # Honour any deep link in the initial URL.
    _go(env.internal_path)
    # And follow browser back/forward + anchor clicks afterwards.
    app.on_internal_path_changed(_go)

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
        f"  Deck:   {len(SLIDES)} slides; ←/→ links in the footer corners.\n"
        f"  Direct: http://{display_host}:{port}/#/3   (deep-link to slide 4)\n",
        flush=True,
    )

    return server.run()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
