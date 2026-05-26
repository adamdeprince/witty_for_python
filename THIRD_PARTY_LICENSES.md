# Third-Party Software Bundled With witty_for_python

`witty_for_python` wheels redistribute binary or asset artefacts produced
from two external open-source projects. Each is vendored as a git
submodule under `extern/` so the exact source corresponding to any
binary we ship can be traced to a specific upstream commit.

| Component | Version          | Upstream                                  | License                  | Bundled as                                                  |
| --------- | ---------------- | ----------------------------------------- | ------------------------ | ----------------------------------------------------------- |
| Wt        | 4.13.2           | <https://github.com/emweb/wt>             | GPL-2.0-only (with the   | `<wheel>/witty_for_python/_libs/libwt.so`,                  |
|           |                  |                                           | "Wt OSS exception")      | `libwthttp.so`; static assets at `_wt_resources/`           |
| TinyMCE   | 6.8.4            | <https://github.com/tinymce/tinymce>      | MIT (at tag `tinymce@6.8.4`; | Built JS/CSS at `_wt_resources/tinymce/`                |
|           |                  |                                           | later versions of TinyMCE   |                                                          |
|           |                  |                                           | are GPL-2.0-or-later)       |                                                          |

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
