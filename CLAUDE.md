# Claude Code entry point

See [AGENTS.md](AGENTS.md). Same content, named for the convention Codex/cross-AI tools use. Everything substantive lives in `docs/`:

- [docs/overview.md](docs/overview.md) — project goals + architecture
- [docs/binding_design.md](docs/binding_design.md) — **rules for adding to or changing the bindings** (read first)
- [docs/signal_slot.md](docs/signal_slot.md) — signal/slot architecture
- [docs/threading.md](docs/threading.md) — threading model, free-threaded 3.14t status
- [docs/building_wt.md](docs/building_wt.md) — Wt 4.13 from-source recipe

This project deliberately keeps its design knowledge in the repo, not in Claude-specific memory, so multiple AI tools (Codex, Claude Code, etc.) can read the same canonical source.
