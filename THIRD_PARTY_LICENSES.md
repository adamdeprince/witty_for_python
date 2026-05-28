# Third-Party Software Bundled With witty_for_python

`witty_for_python` wheels redistribute binary or asset artefacts
produced from a handful of external open-source projects. The
projects we vendor at source level (Wt, TinyMCE) live as git
submodules under `extern/` so the exact source corresponding to any
binary we ship is traceable to a specific upstream commit. Other
libraries we link against at build time (Boost, libharu, libpng,
zlib) are pulled from the build environment's system packages; their
shared objects get bundled into the wheel by `auditwheel repair`
during the manylinux release pipeline.

## Projects we vendor at source

| Component | Version          | Upstream                                  | License                                            | Bundled as                                                  |
| --------- | ---------------- | ----------------------------------------- | -------------------------------------------------- | ----------------------------------------------------------- |
| Wt        | 4.13.2           | <https://github.com/emweb/wt>             | GPL-2.0-only (with the "Wt OSS exception")         | `<wheel>/witty_for_python/_libs/libwt.so`, `libwthttp.so`; static assets at `_wt_resources/` |
| TinyMCE   | 6.8.4            | <https://github.com/tinymce/tinymce>      | MIT (at tag `tinymce@6.8.4`; later versions are GPL-2.0-or-later) | Built JS/CSS at `_wt_resources/tinymce/`                    |

## Native libraries linked transitively (bundled by `auditwheel`)

These are not vendored in our git tree — they come from the build
environment's system packages — but the resulting `.so` files end up
inside the wheel under `witty_for_python/_libs/` after the
`auditwheel repair` step that runs during the manylinux build.

| Component | Upstream                          | License                                                   | Why we link it                                                       |
| --------- | --------------------------------- | --------------------------------------------------------- | -------------------------------------------------------------------- |
| Boost     | <https://www.boost.org>           | Boost Software License 1.0 (permissive, GPL-compatible)   | Wt links Boost.Thread / Boost.Filesystem / Boost.Program_options.    |
| libharu   | <https://github.com/libharu/libharu> | zlib/libpng license (permissive, GPL-compatible)        | Enabled via `ENABLE_HARU=ON` in our CMake; backs `WPdfImage`.        |
| libpng    | <http://www.libpng.org>           | libpng license (permissive, GPL-compatible)               | Pulled in by libharu for PNG embedding inside generated PDFs.        |
| zlib      | <https://www.zlib.net>            | zlib license (permissive, GPL-compatible)                 | Pulled in by libharu / Boost / Wt's HTTP connector for compression.  |

All four are permissively licensed and combine cleanly with our
GPL-2.0-only project; the wheel can be redistributed under our
project's license without additional restrictions from these libraries.

## System libraries we do NOT bundle

The "manylinux" platform tag we target (manylinux_2_28) defines a
baseline ABI that every supported Linux distribution provides natively:
`libc`, `libm`, `libstdc++`, `libgcc_s`, `ld-linux`, plus a small set
of always-present runtime libraries. The wheel relies on the user's OS
for these — bundling them would defeat the platform-tag contract.

## Wt

Wt is licensed under the [GNU General Public License version 2][gpl2].
The full text accompanies the Wt source under
`extern/wt/COPYING.GPL2`. The "Wt OSS license" is functionally GPLv2 —
see [Wt's licensing page][wt-licensing] for the dual-license arrangement
Emweb offers for commercial users. `witty_for_python` itself is
GPL-2.0-only; if you need to use witty_for_python under a commercial
license you must contact both Emweb (for Wt) and the author of
witty_for_python independently.

The wheel ships only Wt's binary artefacts (`libwt.so`, `libwthttp.so`)
and its static resource tree (CSS, JS, themes, icons under
`_wt_resources/`). The pinned source is at
`extern/wt`, version `4.13.2`. To obtain the source of the Wt redistributed
in this wheel, clone this repository with `--recursive`, or fetch the same
tag directly from [emweb/wt][wt-upstream].

## Boost

[Boost][boost-upstream] is the Boost Software License 1.0, a
permissive license (similar to MIT) that's explicitly listed as
GPL-compatible by the FSF. Wt's threading, filesystem, and
command-line-parsing layers use it; our `libwt.so` / `libwthttp.so`
both have a runtime dependency on `libboost_thread`,
`libboost_filesystem`, and (for wthttpd) `libboost_program_options`.

We don't vendor Boost's source — it's a fluid moving target and the
distribution-maintained packages on the manylinux build image are the
right thing to use. License text: <https://www.boost.org/users/license.html>.

## libharu

[libharu][libharu-upstream] (Haru Free PDF Library) is what backs
`WPdfImage`. It's distributed under the zlib/libpng license — a very
short permissive license that's GPL-compatible. The full text is at
the project's `LICENSE` file:

```
This software is provided 'as-is', without any express or implied
warranty. In no event will the authors be held liable for any damages
arising from the use of this software.

Permission is granted to anyone to use this software for any purpose,
including commercial applications, and to alter it and redistribute
it freely, subject to the following restrictions:

 1. The origin of this software must not be misrepresented; you must
    not claim that you wrote the original software.
 2. Altered source versions must be plainly marked as such, and must
    not be misrepresented as being the original software.
 3. This notice may not be removed or altered from any source
    distribution.
```

## libpng + zlib

Both [libpng][libpng-upstream] and [zlib][zlib-upstream] are
permissively licensed (libpng license / zlib license respectively),
both GPL-compatible. libpng is pulled in by libharu for PNG image
embedding inside generated PDFs; zlib is used pervasively across Wt
+ libharu for compression.

## TinyMCE

[TinyMCE][tinymce-upstream] is a rich-text WYSIWYG editor; Wt's
`WTextEdit` widget wraps it. The wheel bundles the official community
build of TinyMCE 6.8.4 — produced by running `yarn build` against the
vendored source at `extern/tinymce` (tag `tinymce@6.8.4`).

At tag `tinymce@6.8.4` the project is licensed under the MIT license;
the full text is reproduced at `extern/tinymce/LICENSE.TXT` and at
`_wt_resources/tinymce/license.txt` inside the installed wheel. (Tiny
later switched the main development branch to GPL-2.0-or-later; we are
not currently tracking that.)

To obtain the source of the TinyMCE redistributed in this wheel, clone
this repository with `--recursive` and inspect `extern/tinymce`, or
fetch the matching tag directly from [tinymce/tinymce][tinymce-upstream].

## Other build-time dependencies

`scikit-build-core`, `nanobind`, `cmake`, and `ninja` are
build-time-only — the wheel does not redistribute any code from them.
Their licenses are not reproduced here.

[gpl2]: https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
[wt-licensing]: https://www.webtoolkit.eu/wt/license
[wt-upstream]: https://github.com/emweb/wt
[tinymce-upstream]: https://github.com/tinymce/tinymce
[boost-upstream]: https://www.boost.org
[libharu-upstream]: https://github.com/libharu/libharu
[libpng-upstream]: http://www.libpng.org
[zlib-upstream]: https://www.zlib.net
