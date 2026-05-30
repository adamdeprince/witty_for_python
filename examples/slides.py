"""witty_for_python slide-sheet demo.

Six slides exercising different parts of the binding:

  1. Title (HTML)
  2. What-it-is (HTML)
  3. Hello-world code, syntax-highlighted via Prism.js loaded with
     `app.require()`
  4. Features grid (HTML)
  5. Live-data chart: a `wt.chart.WCartesianChart` whose model is
     mutated by a server-side `wt.WTimer` and pushed to the client
     via `app.enable_updates()`
  6. Closing slide with a `wt.WQrCode` linking to /slides.pdf — a
     `CallbackResource` that paints each slide's text onto a
     `WPdfImage` page

Navigation is two `WPushButton`s at the bottom corners that flip a
`WStackedWidget` in place — no URL change, no second session.

Run with:

    python examples/slides.py --docroot . --http-address 127.0.0.1 --http-port 8080

(If you have witty_for_python installed but not the source tree,
copy `examples/slides.py` + `examples/witty_wt_slide_theme.css` to
the same directory. The CSS lives next to the script; `examples/`
is intentionally NOT shipped inside the wheel.)
"""

from __future__ import annotations

import math
import sys
import time
from datetime import timedelta as _timedelta
from pathlib import Path

import witty_for_python as wt


HERE = Path(__file__).resolve().parent
CSS_PATH = HERE / "witty_wt_slide_theme.css"
REPO_URL = "https://github.com/adamdeprince/witty_for_python"

# Slide-5's WTimer / model / chart need to outlive create_app's frame.
# nanobind-bound classes have no __dict__, so we can't stash them on
# the WApplication. Park them in a module-level dict keyed by session
# id — fine for one-session-at-a-time demo use.
_SLIDE5_PINS: dict[str, tuple] = {}

# Pinned Prism.js: core + Python language pack + the default light
# theme. Loaded via app.require() (JS) + app.use_style_sheet (CSS).
# The `prism-core` build doesn't include any languages by default, so
# the python component has to load too. Both files are CDN-hosted; the
# version pin keeps the slides reproducible across viewers.
PRISM_VERSION = "1.29.0"
PRISM_CORE_JS  = f"https://cdn.jsdelivr.net/npm/prismjs@{PRISM_VERSION}/components/prism-core.min.js"
PRISM_PYTHON_JS = f"https://cdn.jsdelivr.net/npm/prismjs@{PRISM_VERSION}/components/prism-python.min.js"
PRISM_CSS      = f"https://cdn.jsdelivr.net/npm/prismjs@{PRISM_VERSION}/themes/prism.min.css"


# ---- Slide content ---------------------------------------------------------
#
# Each slide is (title, builder, plain_text). The builder fills a
# WContainerWidget with the rendered slide body. `plain_text` is what
# the PDF exporter draws — HTML doesn't survive being painted with
# WPainter.drawText, so we keep a parallel text form per slide.

def slide_1_title(body: wt.WContainerWidget) -> None:
    body.add_widget(
        '<div class="wfp-kicker">witty_for_python</div>'
        '<h1 class="wfp-slide-title">Wt, in Python.</h1>'
        '<p class="wfp-slide-subtitle">A 6-slide tour of what the bindings'
        ' get you, driven from the keyboard.</p>'
        '<p style="margin-top: 1em" class="wfp-muted">'
        'Press <code>next →</code> in the lower-right to advance.</p>'
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


CODE_SAMPLE = (
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
)


def slide_3_code(body: wt.WContainerWidget) -> None:
    body.add_widget(
        '<div class="wfp-kicker">A working app, in 12 lines</div>'
    )
    # Prism wants `<pre><code class="language-python">…</code></pre>`.
    # The <code> child is mandatory — the highlighter walks the DOM
    # looking for <code> elements with a language- class.
    body.add_widget(
        '<pre class="wfp-code"><code class="language-python">'
        + _html_escape(CODE_SAMPLE)
        + '</code></pre>'
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


# Slide 5 is special — it sets up a live-updating chart driven from the
# server side. The model + timer + WCartesianChart all live in closures
# on the WApplication, so the timer's clicked-slot can mutate them and
# Wt's AJAX layer pushes the DOM diff to the connected browser. Without
# `app.enable_updates(True)` the chart would only refresh on the next
# client-initiated round-trip; with it, the chart breathes.

def slide_5_live(
    body: wt.WContainerWidget,
    app: wt.WApplication,
) -> None:
    body.add_widget(
        '<div class="wfp-kicker">Server-pushed updates</div>'
        '<h2 class="wfp-slide-title" style="font-size: clamp(28px, 3vw, 40px)">'
        'A timer mutates a chart\'s model;'
        ' <code>app.enable_updates()</code> pushes the DOM diff.</h2>'
    )

    # Two-column model: x (sample index), y (sin wave). 60 points = a
    # ~6-second history window at 100ms per tick. Enough motion that
    # the audience can see "yes, this is updating live."
    POINTS = 60
    model = wt.WStandardItemModel(POINTS, 2)
    model.set_header_data(0, "t")
    model.set_header_data(1, "sin(t)")
    for i in range(POINTS):
        model.set_item(i, 0, wt.WStandardItem(str(i)))
        model.set_item(i, 1, wt.WStandardItem("0"))

    chart = body.add_widget(wt.chart.WCartesianChart())
    chart.set_model(model)
    chart.x_series_column = 0
    chart.type = wt.chart.ChartType.Scatter
    series = wt.chart.WDataSeries(1, wt.chart.SeriesType.Line, wt.chart.Axis.Y)
    chart.add_series(series)
    chart.set_width(800)
    chart.set_height(360)

    # Server-side ticker. WTimer fires on a JS-side setInterval but the
    # slot it triggers runs server-side; combined with enable_updates
    # the chart re-renders on each tick.
    start = time.monotonic()
    state = {"phase": 0.0}

    timer = wt.WTimer()
    timer.interval = _timedelta(milliseconds=100)

    def on_tick() -> None:
        # Shift every point one step left; new value at the right edge.
        state["phase"] += 0.15
        for i in range(POINTS - 1):
            old = model.item(i + 1, 1)
            model.set_item(i, 1, wt.WStandardItem(old.text if old else "0"))
        new_y = math.sin(state["phase"]) + 0.4 * math.sin(state["phase"] * 2.7)
        model.set_item(POINTS - 1, 1, wt.WStandardItem(f"{new_y:.4f}"))
        # `app.trigger_update()` flushes server-initiated changes to the
        # client. Required because the chart change is happening outside
        # any user event.
        app.trigger_update()

    timer.timeout.connect(on_tick)
    timer.start()
    # nanobind-bound classes don't carry a Python __dict__, so we can't
    # stash references on `app` itself. Park them in a module-level
    # registry keyed by the session id — entries leak forever, but a
    # single-presenter slide deck only ever holds one. For a long-
    # running multi-session app this should plug into a `WApplication`
    # destruction hook (not bound).
    _SLIDE5_PINS[app.session_id] = (timer, model, chart, state)


def slide_6_close(body: wt.WContainerWidget) -> None:
    body.add_widget(
        '<div class="wfp-kicker">That\'s the deck</div>'
        '<h1 class="wfp-slide-title">Try it.</h1>'
        '<p class="wfp-slide-subtitle">Scan the QR for the repo; or '
        'download the deck as PDF.</p>'
    )

    row = body.add_widget(wt.WContainerWidget())
    # Use the theme's two-column utility class for prev/next-style
    # corner layout. Inline margin would need `set_attribute_value`
    # which isn't bound — the .wfp-two-col selector is enough.
    row.style_class = "wfp-two-col"

    qr = row.add_widget(wt.WQrCode(REPO_URL, 6.0))
    qr.set_width(220)
    qr.set_height(220)

    side = row.add_widget(wt.WContainerWidget())
    side.add_widget(
        f'<p class="wfp-muted" style="font-size: 0.9em">'
        f'Repo: <a href="{REPO_URL}">{REPO_URL.replace("https://", "")}</a></p>'
        f'<p class="wfp-muted" style="font-size: 0.9em; margin-top: 0.7em">'
        f'PDF of this deck: <a href="/slides.pdf" target="_blank">/slides.pdf</a></p>'
        f'<div class="wfp-callout" style="margin-top: 1em">'
        f'<code>python examples/gallery.py --docroot . --http-port 8080</code>'
        f' walks ~every binding in a single page.</div>'
    )


# Title, builder, plain-text used by the PDF exporter.
SLIDES: list[tuple[str, callable, str]] = [
    ("witty_for_python",
     slide_1_title,
     "witty_for_python\n\nWt, in Python.\n\n"
     "A 6-slide tour of what the bindings get you, "
     "driven from the keyboard."),
    ("What it is",
     slide_2_what,
     "What it is\n\n"
     "Python bindings for the Wt C++ web framework, "
     "generated with nanobind.\n\n"
     "- Build a full server-rendered UI in pure Python.\n"
     "- Construct widgets, lay them out, connect signals, "
     "return a WApplication from a factory.\n"
     "- Wheels bundle Wt 4.13.2 + TinyMCE - no external Wt install."),
    ("Hello, witty",
     slide_3_code,
     "A working app, in 12 lines\n\n" + CODE_SAMPLE),
    ("What ships",
     slide_4_features,
     "What ships\n\n"
     "90+ widget classes, three submodules.\n\n"
     "Widgets:  forms, layouts, tables, dialogs, menus, "
     "model/view, navigation, file drop, themes, painting, charts.\n\n"
     "wt.Http:  outbound HTTP client + server-side request/response "
     "for CallbackResource-mounted endpoints.\n\n"
     "wt.chart / wt.Json:  cartesian and pie charts; Wt::Json for "
     "Leaflet map options and anything that wants structured JSON."),
    ("Live data",
     slide_5_live,
     "Server-pushed updates\n\n"
     "A WTimer mutates a chart's model; "
     "app.enable_updates() pushes the DOM diff. "
     "Open the slide live to see it tick."),
    ("Close",
     slide_6_close,
     "That's the deck.\n\n"
     f"Repo: {REPO_URL}\n"
     "PDF: /slides.pdf"),
]


# ---- Helpers ---------------------------------------------------------------

def _html_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
    )


# ---- Wt app construction --------------------------------------------------

def _build_slide(
    index: int,
    total: int,
    on_prev: callable,
    on_next: callable,
    app: wt.WApplication,
) -> wt.WContainerWidget:
    """Construct one slide widget.

    The live-data slide (slide 5) needs the WApplication for
    enable_updates / trigger_update, so we pass `app` through.
    """
    slide = wt.WContainerWidget()
    slide.style_class = "wfp-slide"

    slide.add_widget(wt.WContainerWidget()).style_class = "wfp-slide-header"

    body = slide.add_widget(wt.WContainerWidget())
    body.style_class = "wfp-slide-body"
    _, builder, _ = SLIDES[index]
    # The live-data builder takes (body, app); the others take (body).
    # Dispatch by introspecting the callable's positional-arg count.
    try:
        import inspect
        nparams = len(inspect.signature(builder).parameters)
    except (TypeError, ValueError):
        nparams = 1
    if nparams >= 2:
        builder(body, app)
    else:
        builder(body)

    footer = slide.add_widget(wt.WContainerWidget())
    footer.style_class = "wfp-slide-footer"

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
    app.root.style_class = "wfp-slides"

    # Local theme + Prism's syntax-highlighting theme.
    app.use_style_sheet(wt.WLink("/witty_wt_slide_theme.css"))
    app.use_style_sheet(wt.WLink(PRISM_CSS))

    # Prism JS — core then the Python language pack. require() defers
    # any subsequent do_javascript() until both have loaded.
    app.require(PRISM_CORE_JS,   "Prism")
    app.require(PRISM_PYTHON_JS, "Prism.languages.python")

    # Allow server-initiated updates (needed for the live-data slide
    # 5's timer to push chart mutations to the client without waiting
    # for the client to poll).
    app.enable_updates(True)

    stage = app.root.add_widget(wt.WContainerWidget())
    stage.style_class = "wfp-slide-stage"

    deck = stage.add_widget(wt.WStackedWidget())
    total = len(SLIDES)

    def make_handlers(i: int) -> tuple[callable, callable]:
        def prev() -> None:
            deck.current_index = max(0, i - 1)
            _rehighlight(app)
        def nxt() -> None:
            deck.current_index = min(total - 1, i + 1)
            _rehighlight(app)
        return prev, nxt

    for i in range(total):
        on_prev, on_next = make_handlers(i)
        deck.add_widget(_build_slide(i, total, on_prev, on_next, app))

    # The code slide is index 2 (the third), so it's already rendered
    # at load. Prism's auto-highlight runs once on DOMContentLoaded —
    # which fires before the WStackedWidget content is in the DOM. Run
    # highlight again after Wt's initial render lands.
    app.do_javascript(
        "if (window.Prism) Prism.highlightAll();",
        after_loaded=True,
    )

    return app


def _rehighlight(app: wt.WApplication) -> None:
    """Re-run Prism on any newly-visible <code class='language-…'>
    blocks. Wt's WStackedWidget keeps non-active children in the DOM
    (so Prism would have highlighted them on first load), but if a
    code block were ever LATE-added we'd need this. Cheap, idempotent,
    safer to call than to omit."""
    app.do_javascript(
        "if (window.Prism) Prism.highlightAll();",
        after_loaded=True,
    )


# ---- PDF export endpoint --------------------------------------------------

def build_slides_pdf() -> wt.WPdfImage:
    """Paint the deck onto a tall single-page PDF.

    WPdfImage is a single-page surface — Wt has no `newPage()` on it.
    For a multi-slide PDF we stack the slides vertically on one tall
    page; PDF viewers scroll, so the reading experience is fine.

    WPainter.drawText doesn't render HTML, so we use the plain-text
    form stashed alongside each slide builder.

    Returns the WPdfImage, ready to be handed to `WServer.add_resource`
    (WPdfImage inherits WResource — Wt serves it directly, no custom
    handler needed).
    """
    # A4 in PostScript points (1 pt = 1/72 inch). One slide block per
    # page-height, separated by a thin horizontal rule.
    PAGE_W = 595.0
    BLOCK_H = 842.0
    MARGIN = 60.0
    total_height = BLOCK_H * len(SLIDES)

    pdf = wt.WPdfImage(
        wt.WLength(PAGE_W, wt.LengthUnit.Point),
        wt.WLength(total_height, wt.LengthUnit.Point),
    )

    # WFont.set_size takes a WLength (we don't expose the enum form).
    # Pick concrete point sizes — they're what looks right in a PDF
    # viewer anyway.
    def _font(family: wt.FontFamily, size_pt: float) -> wt.WFont:
        f = wt.WFont()
        f.set_family(family)
        f.set_size(wt.WLength(size_pt, wt.LengthUnit.Point))
        return f
    title_font   = _font(wt.FontFamily.Serif,     32)
    body_font    = _font(wt.FontFamily.SansSerif, 14)
    counter_font = _font(wt.FontFamily.SansSerif,  9)

    painter = wt.WPainter(pdf)

    align_top_left  = int(wt.AlignmentFlag.Left  | wt.AlignmentFlag.Top)
    align_top_right = int(wt.AlignmentFlag.Right | wt.AlignmentFlag.Top)

    # WPainter.drawText word-wraps a single string within its WRectF
    # but treats `\n` as plain text — to get multi-line output we draw
    # one line at a time, advancing y manually. Pick a line height
    # that matches the font and we get reasonable spacing.
    BODY_LINE_H = 18.0

    for slide_idx, (title, _builder, text) in enumerate(SLIDES):
        y0 = slide_idx * BLOCK_H

        # Title.
        painter.set_font(title_font)
        painter.draw_text(
            MARGIN, y0 + MARGIN,
            PAGE_W - 2 * MARGIN, 56,
            align_top_left,
            title,
        )

        # Body — split on newlines, draw each line. WPainter word-wraps
        # within a single drawText call but ignores \n; one call per
        # paragraph is the simplest way to keep formatting.
        painter.set_font(body_font)
        y_cursor = y0 + MARGIN + 80
        for line in text.split("\n"):
            if not line.strip():
                y_cursor += BODY_LINE_H * 0.5
                continue
            painter.draw_text(
                MARGIN, y_cursor,
                PAGE_W - 2 * MARGIN, BODY_LINE_H * 2,
                align_top_left,
                line,
            )
            y_cursor += BODY_LINE_H

        # Page footer.
        painter.set_font(counter_font)
        painter.draw_text(
            MARGIN, y0 + BLOCK_H - MARGIN,
            PAGE_W - 2 * MARGIN, 20,
            align_top_right,
            f"{slide_idx + 1} / {len(SLIDES)}",
        )

    # Destroy the painter so libharu finalises the page. WPdfImage
    # holds the byte buffer; mounting it via add_resource hands the
    # bytes to clients on demand.
    del painter
    return pdf


# ---- main -----------------------------------------------------------------

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

    # Local CSS.
    css = wt.WMemoryResource("text/css", CSS_PATH.read_bytes())
    server.add_resource(css, "/witty_wt_slide_theme.css")

    # PDF export endpoint. WPdfImage inherits WResource — paint the
    # slides onto it once at startup, then hand it to Wt for serving.
    # Every GET /slides.pdf gets the same painted bytes; the slides
    # don't change between requests.
    pdf = build_slides_pdf()
    pdf.suggest_file_name("witty_for_python-slides.pdf")
    server.add_resource(pdf, "/slides.pdf")

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
        f"  Deck:   {len(SLIDES)} slides; ←/→ buttons in the corners.\n"
        f"          Slide 5 is live: a server-side timer pushes chart\n"
        f"          updates over Wt's AJAX channel.\n"
        f"  PDF:    http://{display_host}:{port}/slides.pdf  (download)\n",
        flush=True,
    )

    return server.run()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
