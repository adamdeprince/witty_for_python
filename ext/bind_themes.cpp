#include "common.hpp"

#include <Wt/WBootstrap2Theme.h>
#include <Wt/WBootstrap3Theme.h>
#include <Wt/WBootstrap5Theme.h>
#include <Wt/WCssTheme.h>
#include <Wt/WTheme.h>

#include <memory>
#include <string>

namespace witty_for_python {

void register_themes(nb::module_& m) {
    // ---- WTheme: abstract base ----
    //
    // Bound as non-constructible — the public API consists of metadata
    // accessors. Concrete subclasses (WCssTheme, WBootstrap5Theme) are what
    // applications actually attach via WApplication.theme. Python users
    // wanting to roll their own theme would need a nanobind trampoline
    // override for the pure-virtual hooks (name, disabledClass, activeClass,
    // utilityCssClass, canStyleAnchorAsButton, canBorderBoxElement) —
    // not bound here.

    nb::class_<Wt::WTheme, Wt::WObject>(m, "WTheme")
        .def("name", &Wt::WTheme::name,
             "Theme identifier — e.g. 'polished', 'bootstrap5'.")
        .def("resources_url", &Wt::WTheme::resourcesUrl,
             "URL prefix where the theme's CSS / asset files are served from.");

    // ---- WCssTheme: a name-based plain-CSS theme ----
    //
    // 'default' and 'polished' ship as Wt's built-in CSS themes — they're
    // selected by passing those names to the constructor.

    nb::class_<Wt::WCssTheme, Wt::WTheme>(m, "WCssTheme")
        .def(heap_init<Wt::WCssTheme, const std::string&>(), "name"_a,
             "Construct a plain-CSS theme — pass 'default' or 'polished' to "
             "use Wt's built-in styles, or any name that matches a CSS file "
             "you serve at <resources>/themes/<name>/wt.css.");

    // ---- WBootstrap5Theme: the Bootstrap 5 visual style ----
    //
    // Mostly just instantiated and handed to WApplication.theme. Bootstrap's
    // CSS + JS get auto-served from the bundled Wt resources directory.

    nb::class_<Wt::WBootstrap5Theme, Wt::WTheme>(m, "WBootstrap5Theme")
        .def(heap_init<Wt::WBootstrap5Theme>(),
             "Construct a Bootstrap 5 theme. Attach it to an application "
             "with `app.theme = wt.WBootstrap5Theme()`.");

    // ---- Legacy Bootstrap themes ----
    //
    // WBootstrap2Theme + WBootstrap3Theme. Wt bundles these for apps
    // that haven't migrated to Bootstrap 5 yet. The asset trees live
    // alongside Bootstrap 5 in the bundled `_wt_resources/themes/`
    // directory.

    nb::class_<Wt::WBootstrap2Theme, Wt::WTheme>(m, "WBootstrap2Theme")
        .def(heap_init<Wt::WBootstrap2Theme>(),
             "Bootstrap 2 theme. Useful for older apps; new code should "
             "prefer WBootstrap5Theme.");

    nb::class_<Wt::WBootstrap3Theme, Wt::WTheme>(m, "WBootstrap3Theme")
        .def(heap_init<Wt::WBootstrap3Theme>(),
             "Bootstrap 3 theme. Useful for apps tracking the Bootstrap-3 "
             "ecosystem; new code should prefer WBootstrap5Theme.");
}

}  // namespace witty_for_python
