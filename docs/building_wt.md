# How Wt is built

witty_for_python vendors Wt as a git submodule at `extern/wt`, pinned to a specific commit. The wheel build compiles that pinned Wt source into shared libraries and bundles them alongside the Python extension. Users do **not** install Wt themselves — `git clone --recursive` + `pip install` is the whole flow.

## The pin

`extern/wt` is a git submodule pointing at <https://github.com/emweb/wt> at a specific tag (currently `4.13.2`). The exact commit is recorded in our git history via the gitlink — every binary witty_for_python produces is forensically traceable to the Wt source at that commit.

```
.gitmodules:
[submodule "extern/wt"]
    path = extern/wt
    url = https://github.com/emweb/wt.git
```

## Cloning

```bash
git clone --recursive git@github.com:adamdeprince/witty_for_python.git
# or, if you already cloned without --recursive:
git submodule update --init --recursive
```

## What gets built

`CMakeLists.txt` invokes `add_subdirectory(extern/wt EXCLUDE_FROM_ALL)` after pre-setting Wt's CMake options:

| Flag | Value | Reason |
|---|---|---|
| `BUILD_EXAMPLES` | OFF | Don't waste time on Wt's own examples. |
| `BUILD_TESTS` | OFF | Same. |
| `CONNECTOR_HTTP` | ON | Need `libwthttp.so` (the built-in HTTP server). |
| `CONNECTOR_FCGI` | OFF | No FastCGI. |
| `ENABLE_SSL` | OFF | No OpenSSL dependency. Re-enable for HTTPS wthttpd. |
| `ENABLE_HARU` | OFF | No PDF rendering. |
| `ENABLE_PANGO` | OFF | No Cairo/Pango raster image rendering. |
| `ENABLE_OPENGL` | OFF | No server-side GL. |
| `ENABLE_SQLITE` / `POSTGRES` / `MYSQL` / `FIREBIRD` / `MSSQLSERVER` | OFF | No DB backends (we don't bind `Wt::Dbo`). |
| `ENABLE_QT4` / `QT5` / `QT6` | OFF | No Qt integration. |
| `SHARED_LIBS` | ON | We ship `.so` files, not statically link. |
| `MULTI_THREADED` | ON | Required for the session worker-thread pool. |

`EXCLUDE_FROM_ALL` means Wt's CMake targets aren't built by `make all` and its install rules don't fire on `cmake --install`. The `wt` and `wthttp` libraries get built only because our extension depends on them, and **our own** `install(TARGETS wt wthttp …)` rule puts them where the wheel wants them.

## System dependencies (build-time)

You still need Boost dev headers and zlib dev — Wt's source `#include`s them.

```bash
sudo apt install -y \
    libboost-dev libboost-system-dev libboost-thread-dev \
    libboost-filesystem-dev libboost-program-options-dev \
    zlib1g-dev
```

Plus a C++23 compiler (gcc ≥ 13 or clang ≥ 17) and CMake ≥ 3.26.

Runtime requirements: the build's Boost shared libraries (`libboost_system.so.*`, `libboost_thread.so.*`, etc.) must be present at *runtime* on whatever machine runs the extension. On the build machine this is automatic; for distributing wheels to other machines, the wheel would need a manylinux-style bundling step — out of scope for now.

## Wheel install layout

```
witty_for_python/
├── _witty_for_python.cpython-*.so   the bound extension
├── _libs/
│   ├── libwt.so.4.13.2
│   ├── libwt.so                     symlink
│   ├── libwthttp.so.4.13.2
│   └── libwthttp.so                 symlink
└── _wt_resources/                   Wt static assets (themes, JS, CSS)
    ├── themes/
    ├── form.css
    └── ...
```

The extension is linked with `RUNPATH=$ORIGIN/_libs` so `dlopen` finds the bundled Wt libraries automatically. `witty_for_python.resources_dir` exposes the path to `_wt_resources/` so application code (and the bundled examples) can pass it to wthttpd as `--resources-dir` without the user having to know where it lives.

## Running an app

```bash
python examples/gallery.py --docroot . \
    --http-address 127.0.0.1 --http-port 8080
```

No `--resources-dir` needed — the example fills it in from `witty_for_python.resources_dir`. Pass `--resources-dir <other-path>` to override.

## Bumping the Wt pin

```bash
cd extern/wt
git fetch
git checkout <new-tag>
cd ../..
git add extern/wt
git commit -m "Bump Wt to <new-tag>"
```

Then rebuild and run the tests. Wt API drift between minor versions has been low but not zero — when bumping, run `pytest` and walk the gallery in a browser.

## Re-enabling Wt features later

Need a Wt feature we currently disabled? Flip the relevant `set(... ON CACHE BOOL "" FORCE)` line in `CMakeLists.txt` and install the matching system dev package:

- HTTPS in wthttp: `ENABLE_SSL=ON` + `libssl-dev`
- PDF (`WPdfImage`): `ENABLE_HARU=ON` + `libhpdf-dev`
- Raster image: `ENABLE_PANGO=ON` (Cairo+Pango) or GraphicsMagick variant
- DB backends for `Wt::Dbo`: `ENABLE_SQLITE=ON` (etc.) + the matching DB client dev package

Rebuild witty_for_python after changing the flag.
