#!/usr/bin/env python3
"""Parse .pyi stubs and emit per-topic Markdown + llms.txt index.

Outputs into `docs/api/`:

    index.md          — root overview, links to every topic page
    <topic>.md        — one per topic (see scripts/doc_topics.py for the list)
    llms.txt          — llmstxt.org-style index for LLM agents
    llms-full.txt     — concatenated body of every topic page

Source of truth is the .pyi stubs, which carry the docstrings nanobind pulled
from `ext/bind_*.cpp` plus the type signatures it inferred. Regenerate by
running this script after touching bindings (and re-running stubgen via
`scripts/regenerate_stubs.py`).

    python scripts/build_docs.py [--check]

`--check` runs in CI mode: generates into a temp dir and diffs against the
committed copy, failing if anything is stale.
"""

from __future__ import annotations

import argparse
import ast
import filecmp
import re
import sys
import textwrap
from dataclasses import dataclass, field
from pathlib import Path

from doc_topics import MODULES, TOPICS, topic_for_class


REPO = Path(__file__).resolve().parent.parent
API_DIR = REPO / "docs" / "api"


# ════════════════════════════════════════════════════════════════════════════
# .pyi parser
# ════════════════════════════════════════════════════════════════════════════

@dataclass
class Member:
    """A single class member — method, property, or nested type."""
    kind: str               # "method" | "property" | "setter" | "nested"
    name: str
    signature: str          # rendered "(self, x: int) -> str"
    docstring: str          # may be ""
    decorators: list[str] = field(default_factory=list)
    has_setter: bool = False  # filled in for `property` kind after collation


@dataclass
class ParsedClass:
    name: str               # qualified, e.g. "chart.WAxis" or "WText"
    bases: list[str]
    docstring: str
    members: list[Member]


def _unparse(node: ast.AST | None) -> str:
    if node is None:
        return ""
    return ast.unparse(node)


def _docstring_of(body: list[ast.stmt]) -> str:
    """Pull the docstring out of a function/class/method body, if present."""
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
        v = body[0].value.value
        if isinstance(v, str):
            return inspect_dedent(v)
    return ""


def inspect_dedent(s: str) -> str:
    """Strip leading/trailing whitespace and uniformly dedent."""
    return textwrap.dedent(s).strip("\n")


def _render_args(args: ast.arguments) -> str:
    """Render an ast.arguments back to its Python source — handles defaults,
    keyword-only, *args, **kwargs, positional-only."""
    parts: list[str] = []

    def fmt(arg: ast.arg, default: ast.expr | None) -> str:
        out = arg.arg
        if arg.annotation:
            out += ": " + _unparse(arg.annotation)
        if default is not None:
            out += " = " + _unparse(default)
        return out

    # Positional + positional-or-keyword
    pos = args.posonlyargs + args.args
    defaults = [None] * (len(pos) - len(args.defaults)) + list(args.defaults)
    for arg, default in zip(args.posonlyargs, defaults[:len(args.posonlyargs)]):
        parts.append(fmt(arg, default))
    if args.posonlyargs:
        parts.append("/")
    for arg, default in zip(args.args, defaults[len(args.posonlyargs):]):
        parts.append(fmt(arg, default))

    if args.vararg:
        parts.append("*" + args.vararg.arg + (": " + _unparse(args.vararg.annotation) if args.vararg.annotation else ""))
    elif args.kwonlyargs:
        parts.append("*")

    for arg, default in zip(args.kwonlyargs, args.kw_defaults):
        parts.append(fmt(arg, default))

    if args.kwarg:
        parts.append("**" + args.kwarg.arg + (": " + _unparse(args.kwarg.annotation) if args.kwarg.annotation else ""))

    return ", ".join(parts)


def _parse_function(node: ast.FunctionDef) -> Member:
    decos = [_unparse(d) for d in node.decorator_list]
    is_prop = any(d == "property" for d in decos)
    is_setter = any(d.endswith(".setter") for d in decos)
    is_classmethod = "classmethod" in decos
    is_staticmethod = "staticmethod" in decos
    sig = "(" + _render_args(node.args) + ")"
    if node.returns is not None:
        sig += " -> " + _unparse(node.returns)
    if is_prop:
        kind = "property"
        # Property "signature" is just the return type
        sig = "-> " + _unparse(node.returns) if node.returns else ""
    elif is_setter:
        kind = "setter"
    else:
        kind = "method"
    return Member(
        kind=kind,
        name=node.name,
        signature=sig,
        docstring=_docstring_of(node.body),
        decorators=decos,
    )


def _parse_class(node: ast.ClassDef, *, qualifier: str = "") -> ParsedClass:
    bases = [_unparse(b) for b in node.bases]
    members: list[Member] = []
    setters: set[str] = set()
    nested_classes: list[ParsedClass] = []

    for child in node.body:
        if isinstance(child, ast.FunctionDef):
            m = _parse_function(child)
            if m.kind == "setter":
                setters.add(m.name)
                continue
            members.append(m)
        elif isinstance(child, ast.ClassDef):
            nested_classes.append(_parse_class(child, qualifier=qualifier + node.name + "."))

    # Flag properties that have a setter, so rendering can mark them read/write.
    for m in members:
        if m.kind == "property" and m.name in setters:
            m.has_setter = True

    for nc in nested_classes:
        members.append(Member(
            kind="nested",
            name=nc.name.rsplit(".", 1)[-1],
            signature="class " + nc.name.rsplit(".", 1)[-1],
            docstring=nc.docstring,
        ))

    cls = ParsedClass(
        name=qualifier + node.name,
        bases=bases,
        docstring=_docstring_of(node.body),
        members=members,
    )
    return cls


def parse_pyi(path: Path, prefix: str) -> dict[str, ParsedClass]:
    """Parse one .pyi → {qualified_name: ParsedClass}."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: dict[str, ParsedClass] = {}
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            cls = _parse_class(node, qualifier=prefix)
            out[cls.name] = cls
            # Also index nested classes by their qualified name so the topic
            # mapping can pick e.g. "WLeafletMap.Marker".
            for m in cls.members:
                if m.kind == "nested":
                    nested_qname = cls.name + "." + m.name
                    # Best-effort: re-walk that ast.ClassDef to capture the
                    # nested ParsedClass with its members. We have it via
                    # _parse_class already; pull it out by scanning the node.
                    for child in node.body:
                        if isinstance(child, ast.ClassDef) and child.name == m.name:
                            out[nested_qname] = _parse_class(child, qualifier=cls.name + ".")
                            break
    return out


# ════════════════════════════════════════════════════════════════════════════
# Markdown rendering
# ════════════════════════════════════════════════════════════════════════════

def _slug(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]", "-", name)


def render_class(cls: ParsedClass) -> str:
    """Emit Markdown for one class."""
    out: list[str] = []
    # Short class name for header; full qualified name as anchor.
    short = cls.name.rsplit(".", 1)[-1]
    out.append(f"### {short} {{#{_slug(cls.name)}}}")
    out.append("")
    if cls.bases and cls.bases != ["object"]:
        out.append("*Inherits:* " + ", ".join(f"`{b}`" for b in cls.bases))
        out.append("")
    if cls.docstring:
        out.append(cls.docstring)
        out.append("")

    # Group members. Constructor overloads (multiple `__init__`s) each become
    # their own bullet under Constructors. Similarly for overloaded methods.
    constructors = [m for m in cls.members if m.name == "__init__"]
    properties = [m for m in cls.members if m.kind == "property"]
    methods = [m for m in cls.members
               if m.kind == "method"
               and m.name != "__init__"
               and m.name not in {"__bool__", "__repr__", "__len__"}]
    dunders = [m for m in cls.members
               if m.kind == "method"
               and m.name in {"__bool__", "__repr__", "__len__"}]
    nested = [m for m in cls.members if m.kind == "nested"]

    def render_callable_section(title: str, items: list[Member]) -> None:
        if not items:
            return
        out.append(f"**{title}**")
        out.append("")
        for m in items:
            out.append(f"- `{m.name}{m.signature}`")
            if m.docstring:
                for line in m.docstring.splitlines():
                    out.append(f"  {line}" if line.strip() else "")
            out.append("")

    def render_property_section(items: list[Member]) -> None:
        if not items:
            return
        out.append("**Properties**")
        out.append("")
        for m in items:
            # m.signature for a property is "-> T" (we set this in _parse_function).
            return_type = m.signature.removeprefix("-> ").strip() or "Any"
            mode = "read/write" if m.has_setter else "read-only"
            out.append(f"- `{m.name}: {return_type}` *({mode})*")
            if m.docstring:
                for line in m.docstring.splitlines():
                    out.append(f"  {line}" if line.strip() else "")
            out.append("")

    def render_nested_section(items: list[Member]) -> None:
        if not items:
            return
        out.append("**Nested types**")
        out.append("")
        for m in items:
            out.append(f"- `{m.name}`")
            if m.docstring:
                for line in m.docstring.splitlines():
                    out.append(f"  {line}" if line.strip() else "")
            out.append("")

    render_callable_section("Constructors", constructors)
    render_property_section(properties)
    render_callable_section("Methods", methods)
    render_callable_section("Dunder methods", dunders)
    render_nested_section(nested)

    return "\n".join(out).rstrip() + "\n"


def render_topic(topic: dict, classes_by_name: dict[str, ParsedClass]) -> str:
    """Emit Markdown for one topic page (multiple classes)."""
    out: list[str] = []
    out.append(f"# {topic['title']}")
    out.append("")
    out.append("> " + topic["summary"])
    out.append("")

    # Table of contents — anchors to each class.
    missing: list[str] = []
    resolved: list[ParsedClass] = []
    for qname in topic["classes"]:
        if qname in classes_by_name:
            resolved.append(classes_by_name[qname])
        else:
            missing.append(qname)

    if resolved:
        out.append("**Classes in this section:**")
        out.append("")
        for cls in resolved:
            short = cls.name.rsplit(".", 1)[-1]
            out.append(f"- [`{short}`](#{_slug(cls.name)})")
        out.append("")

    if missing:
        out.append(f"<!-- topic '{topic['id']}' lists unresolved class names: "
                   f"{', '.join(missing)} -->")
        out.append("")

    out.append("---")
    out.append("")

    for cls in resolved:
        out.append(render_class(cls))

    return "\n".join(out)


def render_index() -> str:
    """The `docs/api/index.md` root page."""
    out: list[str] = [
        "# API Reference",
        "",
        "> Python bindings for the Wt (Web Toolkit) C++ library — write "
        "server-side web UIs in widget code.",
        "",
        "This reference is grouped by topic. For an LLM-friendly index in "
        "[llmstxt.org](https://llmstxt.org/) format, see "
        "[llms.txt](llms.txt) (concatenated body in "
        "[llms-full.txt](llms-full.txt)).",
        "",
        "## Topics",
        "",
    ]
    for t in TOPICS:
        out.append(f"### [{t['title']}]({t['id']}.md)")
        out.append("")
        out.append(t["summary"])
        out.append("")
    return "\n".join(out)


def render_llms_txt() -> str:
    """The llmstxt.org-format index."""
    out: list[str] = [
        "# witty_for_python",
        "",
        "> Python bindings for the Wt (Web Toolkit) C++ library — write "
        "server-side web UIs in widget code (containers, signals, "
        "model/view) instead of HTML/JS.",
        "",
        "The wheels are abi3 cp312, ship Wt 4.13 vendored alongside, and "
        "load on Python 3.12 / 3.13 / 3.14. This file is the entry point "
        "for LLM agents; each linked page is a self-contained reference "
        "for one topic.",
        "",
        "## API Reference",
        "",
    ]
    for t in TOPICS:
        out.append(f"- [{t['title']}]({t['id']}.md): {t['summary']}")
    out.append("")
    out.append("## Optional")
    out.append("")
    out.append("- [llms-full.txt](llms-full.txt): every topic page "
               "concatenated into a single file for one-shot ingestion.")
    out.append("")
    return "\n".join(out)


def render_llms_full(topic_md: dict[str, str]) -> str:
    out: list[str] = [
        "# witty_for_python — full API reference",
        "",
        "Concatenation of every topic page; see llms.txt for an index.",
        "",
    ]
    for t in TOPICS:
        out.append("")
        out.append("=" * 76)
        out.append("")
        out.append(topic_md[t["id"]])
    return "\n".join(out)


# ════════════════════════════════════════════════════════════════════════════
# Driver
# ════════════════════════════════════════════════════════════════════════════

def collect_all() -> dict[str, ParsedClass]:
    """Walk every module listed in MODULES and return one big index."""
    classes: dict[str, ParsedClass] = {}
    for relpath, prefix in MODULES:
        path = REPO / relpath
        if not path.exists():
            sys.stderr.write(f"WARNING: missing module {relpath}\n")
            continue
        classes.update(parse_pyi(path, prefix))
    return classes


def report_unmapped(classes: dict[str, ParsedClass]) -> None:
    """Note any class the topic mapping forgot about."""
    unmapped = [qn for qn in classes if topic_for_class(qn) is None]
    if not unmapped:
        return
    sys.stderr.write(
        f"WARNING: {len(unmapped)} class(es) not assigned to any topic — "
        "edit scripts/doc_topics.py to include them:\n")
    for qn in sorted(unmapped):
        sys.stderr.write(f"  - {qn}\n")


def build(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    classes = collect_all()
    report_unmapped(classes)

    topic_md: dict[str, str] = {}
    for t in TOPICS:
        topic_md[t["id"]] = render_topic(t, classes)
        (out_dir / f"{t['id']}.md").write_text(topic_md[t["id"]], encoding="utf-8")

    (out_dir / "index.md").write_text(render_index(), encoding="utf-8")
    (out_dir / "llms.txt").write_text(render_llms_txt(), encoding="utf-8")
    (out_dir / "llms-full.txt").write_text(render_llms_full(topic_md), encoding="utf-8")

    print(f"Wrote {len(TOPICS)} topic pages + index + llms.txt + llms-full.txt "
          f"to {out_dir}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check", action="store_true",
                   help="Compare against committed copy; fail if out of date.")
    args = p.parse_args()

    if args.check:
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            build(tmp)
            mismatched: list[str] = []
            for gen in tmp.rglob("*"):
                rel = gen.relative_to(tmp)
                committed = API_DIR / rel
                if not committed.exists():
                    mismatched.append(f"missing: {rel}")
                elif not filecmp.cmp(gen, committed, shallow=False):
                    mismatched.append(f"stale: {rel}")
            if mismatched:
                sys.stderr.write(
                    "API docs are stale — regenerate with:\n"
                    "    python scripts/build_docs.py\n\n"
                    "Differences:\n")
                for m in mismatched:
                    sys.stderr.write(f"  - {m}\n")
                return 1
            print("API docs are up to date.")
            return 0

    build(API_DIR)
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.exit(main())
