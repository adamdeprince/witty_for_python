# Building Wt 4.13 from source

Wt 4.13 isn't packaged in current Ubuntu repositories (the `libwt*` packages are missing or out of date). Build from source into the user prefix `~/.local`.

## Prerequisites

System packages (require sudo):

```bash
sudo apt install -y \
    libboost-dev \
    libboost-system-dev \
    libboost-thread-dev \
    libboost-filesystem-dev \
    libboost-program-options-dev \
    zlib1g-dev
```

On a recent Ubuntu, Boost ≥ 1.74 is fine; we've verified against Boost 1.88.

Toolchain expectations: gcc ≥ 13 (for C++23), CMake ≥ 3.26, Ninja or Make. The build container had gcc 15.2 and CMake 4.3.

## Source

```bash
mkdir -p /home/adam/dev/wt-build && cd /home/adam/dev/wt-build
curl -fsSL -o wt-4.13.2.tar.gz https://github.com/emweb/wt/archive/4.13.2.tar.gz
tar xzf wt-4.13.2.tar.gz
```

## Configure + build + install

```bash
mkdir -p wt-4.13.2/build && cd wt-4.13.2/build
cmake .. -G Ninja \
  -DCMAKE_INSTALL_PREFIX="$HOME/.local" \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_CXX_STANDARD=23 \
  -DBUILD_EXAMPLES=OFF -DBUILD_TESTS=OFF \
  -DCONNECTOR_HTTP=ON -DCONNECTOR_FCGI=OFF \
  -DENABLE_SSL=OFF -DENABLE_HARU=OFF -DENABLE_PANGO=OFF -DENABLE_OPENGL=OFF \
  -DENABLE_SQLITE=OFF -DENABLE_POSTGRES=OFF -DENABLE_MYSQL=OFF \
  -DENABLE_FIREBIRD=OFF -DENABLE_MSSQLSERVER=OFF \
  -DENABLE_QT4=OFF -DENABLE_QT5=OFF -DENABLE_QT6=OFF \
  -DSHARED_LIBS=ON -DMULTI_THREADED=ON \
  -DRUNDIR="$HOME/.local/var/run/wt" \
  -DCONFIGDIR="$HOME/.local/etc/wt" \
  -DWEBUSER="$USER" -DWEBGROUP="$USER"
ninja -j$(nproc)
cmake --install .   # no sudo needed; installs into ~/.local
```

The install drops:

- Headers in `~/.local/include/Wt/`
- Shared libs in `~/.local/lib/libwt*.so`
- CMake package files in `~/.local/lib/cmake/wt/wt-config.cmake` (this is what witty_for_python's `find_package(Wt)` resolves against)
- Resource files in `~/.local/share/Wt/` (Bootstrap themes, JS, CSS)
- A default config in `~/.local/etc/wt/wt_config.xml`

## Why these flags

| Flag | Reason |
|---|---|
| `CMAKE_CXX_STANDARD=23` | Matches witty_for_python's C++23 requirement |
| `BUILD_EXAMPLES=OFF`, `BUILD_TESTS=OFF` | Skip the parts we don't need; ~50% build-time win |
| `CONNECTOR_HTTP=ON` | We need `libwthttp.so` (the standalone HTTP server) |
| `CONNECTOR_FCGI=OFF` | We don't use FastCGI |
| `ENABLE_*=OFF` (DBs, SSL, optional libs) | Each one would require extra system deps for no current benefit. Re-enable individually if you need a feature. |
| `SHARED_LIBS=ON` | Static libs work too, but shared keeps the witty_for_python `.so` small |
| `MULTI_THREADED=ON` | Required for the session worker-thread pool (see [threading.md](threading.md)) |
| `RUNDIR` / `CONFIGDIR` / `WEBUSER` / `WEBGROUP` | Avoid root-owned paths; everything stays under `$HOME` |

## Verifying the install

```bash
ls ~/.local/lib/libwt* | head        # libwt.so, libwthttp.so
ls ~/.local/include/Wt/ | head        # WApplication.h, WContainerWidget.h, …
cat ~/.local/lib/cmake/wt/wt-config.cmake | head    # find_package target
```

## Then build witty_for_python

```bash
cd /path/to/witty_for_python
CMAKE_PREFIX_PATH="$HOME/.local" \
  /path/to/python -m pip install --no-build-isolation -e .
```

CMake auto-detects whether the active Python is the standard build (uses `STABLE_ABI`) or the free-threaded build (uses `FREE_THREADED`). The compiled `.so` has an RPATH baked in pointing at `~/.local/lib`, so `import witty_for_python` works without `LD_LIBRARY_PATH`.

## Running the demos

Wt's HTTP server needs to be told where the static resources are:

```bash
python examples/gallery.py \
    --docroot . \
    --http-address 127.0.0.1 --http-port 8080 \
    --resources-dir "$HOME/.local/share/Wt/resources"
```

The `--resources-dir` flag is required even though `~/.local/etc/wt/wt_config.xml` exists — by default the config file doesn't carry the path.

## Re-enabling features later

If you later need a Wt feature we currently disabled:

- **SSL/HTTPS in wthttp**: `-DENABLE_SSL=ON` + `sudo apt install libssl-dev`
- **PDF rendering (`WPdfImage`)**: `-DENABLE_HARU=ON` + `sudo apt install libhpdf-dev`
- **Raster image rendering**: `-DENABLE_PANGO=ON` (Cairo+Pango), or GraphicsMagick variant
- **DB backends for `Wt::Dbo`**: `-DENABLE_SQLITE=ON` (etc.) + matching dev package

Re-run the cmake configure + ninja + install steps after changing flags. The witty_for_python build will pick up the new Wt without changes on its side.
