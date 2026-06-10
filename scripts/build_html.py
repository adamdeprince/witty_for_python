#!/usr/bin/env python3
"""Build the HTML documentation site from the Markdown sources.

Reads `docs/api/*.md` (and other curated `.md` under `docs/`), converts each
to an HTML body via pandoc, then wraps with the Jinja2 template in
`docs/templates/page.html.j2` to produce a complete page.

Outputs into `html/`:

    index.html                  — top-level landing page (built from docs/overview.md
                                  if present, else a generated stub)
    api/index.html              — API root
    api/<topic>.html            — one per topic
    assets/style.css            — stylesheet (copied verbatim)

`html/` is gitignored. Re-run after editing Markdown.

    python scripts/build_html.py

Requires `pandoc` on PATH and `Jinja2` installed in the current environment.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from doc_topics import TOPICS


REPO = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO / "docs"
API_DIR = DOCS_DIR / "api"
TEMPLATES_DIR = DOCS_DIR / "templates"
OUT_DIR = REPO / "html"


def pandoc_to_html(md_text: str) -> str:
    """Run pandoc to convert Markdown → HTML body fragment."""
    result = subprocess.run(
        ["pandoc",
         "--from=markdown+pipe_tables+autolink_bare_uris+fenced_code_blocks+"
         "header_attributes+raw_html",
         "--to=html5",
         "--no-highlight"],
        input=md_text, capture_output=True, text=True, check=True,
    )
    return result.stdout


CLASS_HEADER_RE = re.compile(r'<h3 id="([^"]+)">([^<]+)</h3>')


def extract_class_anchors(body_html: str) -> list[dict]:
    """For a topic page, scrape (anchor_id, displayed_name) for each <h3 id=…>.

    The Jinja sidebar uses these to render in-page jumps to each class.
    """
    out = []
    for m in CLASS_HEADER_RE.finditer(body_html):
        out.append({"anchor": m.group(1), "name": m.group(2)})
    return out


def render_page(env, *, page_kind: str, page_title: str, body_html: str,
                topic_id: str = "", root: str = "../") -> str:
    template = env.get_template("page.html.j2")
    class_anchors = extract_class_anchors(body_html) if page_kind == "topic" else []
    return template.render(
        page_kind=page_kind,
        page_title=page_title,
        body=body_html,
        topics=TOPICS,
        topic_id=topic_id,
        class_anchors=class_anchors,
        root=root,
    )


def title_from_md(md_text: str, fallback: str) -> str:
    """Extract the first H1 line as the page title."""
    for line in md_text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def build_home(env) -> str:
    """Top-level landing page.

    Uses docs/overview.md if present (the project's existing handcrafted
    overview), otherwise a minimal stub pointing to the API reference.
    """
    overview = DOCS_DIR / "overview.md"
    if overview.exists():
        body = pandoc_to_html(overview.read_text(encoding="utf-8"))
        title = title_from_md(overview.read_text(encoding="utf-8"), "witty_for_python")
    else:
        body = pandoc_to_html(
            "# witty_for_python\n\n"
            "Python bindings for the Wt (Web Toolkit) C++ library.\n\n"
            "See the [API reference](api/index.html) for details.\n"
        )
        title = "witty_for_python"
    return render_page(env, page_kind="home", page_title=title,
                       body_html=body, root="")


def build_api_index(env) -> str:
    md_path = API_DIR / "index.md"
    md = md_path.read_text(encoding="utf-8")
    body = pandoc_to_html(md)
    return render_page(env, page_kind="api-index",
                       page_title=title_from_md(md, "API Reference"),
                       body_html=body, root="../")


def build_topic(env, topic: dict) -> str:
    md_path = API_DIR / f"{topic['id']}.md"
    md = md_path.read_text(encoding="utf-8")
    body = pandoc_to_html(md)
    return render_page(env, page_kind="topic",
                       page_title=topic["title"],
                       body_html=body, topic_id=topic["id"], root="../")


def build() -> None:
    if not shutil.which("pandoc"):
        sys.stderr.write("ERROR: pandoc not found on PATH.\n")
        sys.exit(2)

    # Output skeleton.
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir()
    (OUT_DIR / "api").mkdir()
    (OUT_DIR / "assets").mkdir()

    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(["html"]),
        keep_trailing_newline=True,
    )

    # Pages.
    (OUT_DIR / "index.html").write_text(build_home(env), encoding="utf-8")
    (OUT_DIR / "api" / "index.html").write_text(
        build_api_index(env), encoding="utf-8")
    for topic in TOPICS:
        (OUT_DIR / "api" / f"{topic['id']}.html").write_text(
            build_topic(env, topic), encoding="utf-8")

    # Assets (verbatim copy).
    style_src = TEMPLATES_DIR / "style.css"
    if style_src.exists():
        shutil.copy(style_src, OUT_DIR / "assets" / "style.css")

    # Copy any easter-egg or doc-illustration PNGs under docs/api/img/ →
    # html/assets/img/ (paths in .md should match).
    img_src = API_DIR / "img"
    if img_src.is_dir():
        shutil.copytree(img_src, OUT_DIR / "assets" / "img")

    print(f"Built site in {OUT_DIR} ({len(TOPICS)} topic pages + index + home)")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.parse_args()
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    build()
    return 0


if __name__ == "__main__":
    sys.exit(main())
