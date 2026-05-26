#include "common.hpp"

#include <Wt/WBadge.h>
#include <Wt/WEvent.h>            // WMouseEvent (popup overload)
#include <Wt/WGlobal.h>           // AlignmentFlag, Orientation
#include <Wt/WLineEdit.h>
#include <Wt/WMenu.h>
#include <Wt/WNavigationBar.h>
#include <Wt/WPoint.h>
#include <Wt/WPopupMenu.h>
#include <Wt/WPushButton.h>
#include <Wt/WSplitButton.h>
#include <Wt/WStackedWidget.h>
#include <Wt/WToolBar.h>

#include <memory>
#include <string>

namespace witty_for_python {

void register_chrome(nb::module_& m) {
    // ---- AlignmentFlag enum ----
    //
    // Used by WNavigationBar / WToolBar to place items left or right (and
    // by WBoxLayout / WGridLayout for vertical alignment). We bind only the
    // values that actually appear in current bindings — the rest are
    // available as raw ints if needed for future surface.

    nb::enum_<Wt::AlignmentFlag>(m, "AlignmentFlag", nb::is_arithmetic())
        .value("Left", Wt::AlignmentFlag::Left)
        .value("Right", Wt::AlignmentFlag::Right)
        .value("Center", Wt::AlignmentFlag::Center)
        .value("Justify", Wt::AlignmentFlag::Justify)
        .value("Baseline", Wt::AlignmentFlag::Baseline)
        .value("Top", Wt::AlignmentFlag::Top)
        .value("Middle", Wt::AlignmentFlag::Middle)
        .value("Bottom", Wt::AlignmentFlag::Bottom);

    // ---- WPoint: integer 2-D coordinate, used by WPopupMenu.popup() ----

    nb::class_<Wt::WPoint>(m, "WPoint")
        .def(nb::init<>())
        .def(nb::init<int, int>(), "x"_a, "y"_a)
        .def_prop_rw("x", &Wt::WPoint::x, &Wt::WPoint::setX)
        .def_prop_rw("y", &Wt::WPoint::y, &Wt::WPoint::setY)
        .def("__repr__", [](const Wt::WPoint& p) {
            return "WPoint(x=" + std::to_string(p.x())
                + ", y=" + std::to_string(p.y()) + ")";
        });

    // ---- WPopupMenu: a floating WMenu that pops up at a screen location ----
    //
    // WPopupMenu inherits all of WMenu's surface (add_item, etc.). Construct
    // it standalone — `popup(point|event|widget)` places it on screen, then
    // `triggered` fires with the chosen WMenuItem. Use `set_button(btn)` to
    // attach a popup to a button for the typical menu-button UX, OR call
    // `popup()` yourself from a slot. Calling `popup()` more than once at a
    // time is undefined; rely on `hide_on_select=True` (the default) plus
    // `triggered` to know when the cycle is done.

    nb::class_<Wt::WPopupMenu, Wt::WMenu>(m, "WPopupMenu")
        .def("__init__", [](Wt::WPopupMenu* self) {
            new (self) Wt::WPopupMenu(nullptr);
        })
        .def("popup",
             nb::overload_cast<const Wt::WPoint&>(&Wt::WPopupMenu::popup),
             "point"_a,
             "Show the menu at an absolute screen coordinate (page-relative pixels).")
        .def("popup",
             nb::overload_cast<const Wt::WMouseEvent&>(&Wt::WPopupMenu::popup),
             "event"_a,
             "Show the menu at the location of a mouse event — convenient "
             "from a clicked-handler slot.")
        .def("popup",
             nb::overload_cast<Wt::WWidget*, Wt::Orientation>(&Wt::WPopupMenu::popup),
             "location"_a, "orientation"_a = Wt::Orientation::Vertical,
             "Show the menu anchored to a widget; orientation controls "
             "drop-direction.")
        .def("set_button", &Wt::WPopupMenu::setButton, "button"_a,
             "Wire `button.clicked` to popup() so the menu opens when the "
             "button is clicked. The button is just associated, not owned.")
        .def_prop_rw("hide_on_select",
            &Wt::WPopupMenu::hideOnSelect,
            &Wt::WPopupMenu::setHideOnSelect,
            "When True (default), picking an item hides the popup.")
        .def("set_auto_hide", &Wt::WPopupMenu::setAutoHide,
             "enabled"_a, "auto_hide_delay_ms"_a = 0,
             "When True, the popup hides itself after the mouse leaves it; "
             "`auto_hide_delay_ms` adds a grace period.")
        .def_prop_ro("about_to_hide", &Wt::WPopupMenu::aboutToHide,
                     nb::rv_policy::reference_internal,
                     "Signal[] — fires once when the popup is about to "
                     "close, regardless of how (selection, click-outside, "
                     "auto-hide). Use this for cleanup.")
        .def_prop_ro("triggered", &Wt::WPopupMenu::triggered,
                     nb::rv_policy::reference_internal,
                     "MenuItemSignal — fires when the user picks an item. "
                     "Unlike WMenu.item_selected, this fires only for "
                     "interactive selection (programmatic .select() is "
                     "silent).");

    // ---- WBadge: a small label, typically attached to another widget ----
    //
    // Extends WText, so all text/format APIs apply. The badge renders
    // inline-block by default — handy for "12 unread"-style counts.

    nb::class_<Wt::WBadge, Wt::WText>(m, "WBadge")
        .def(nb::init<>())
        .def(nb::init<const Wt::WString&>(), "text"_a)
        .def_prop_rw("use_default_style",
            &Wt::WBadge::useDefaultStyle,
            &Wt::WBadge::setUseDefaultStyle,
            "When True (default), Wt applies its theme's badge CSS class. "
            "Disable to style purely via your own classes/CSS.");

    // ---- WToolBar: horizontal/vertical row of buttons + separators ----

    nb::class_<Wt::WToolBar, Wt::WWidget>(m, "WToolBar")
        .def(nb::init<>())
        .def("set_orientation", &Wt::WToolBar::setOrientation,
             "orientation"_a,
             "Horizontal or Vertical layout for the buttons. Write-only on "
             "the C++ side; no getter is exposed by Wt.")
        .def_prop_rw("compact",
            &Wt::WToolBar::isCompact,
            &Wt::WToolBar::setCompact,
            "When True, buttons are visually grouped (no internal margins).")
        .def_prop_ro("count", &Wt::WToolBar::count,
            "Number of items (buttons or widgets) currently in the toolbar.")
        .def("add_button",
            // Ownership: move the unique_ptr in, return the raw pointer
            // so the caller keeps a non-owning handle.
            [](Wt::WToolBar& self, std::unique_ptr<Wt::WPushButton> btn,
               Wt::AlignmentFlag alignment) -> Wt::WPushButton* {
                Wt::WPushButton* raw = btn.get();
                self.addButton(std::move(btn), alignment);
                return raw;
            },
            "button"_a, "alignment"_a = Wt::AlignmentFlag::Left,
            nb::rv_policy::reference_internal)
        .def("add_button",
            [](Wt::WToolBar& self, std::unique_ptr<Wt::WSplitButton> btn,
               Wt::AlignmentFlag alignment) -> Wt::WSplitButton* {
                Wt::WSplitButton* raw = btn.get();
                self.addButton(std::move(btn), alignment);
                return raw;
            },
            "button"_a, "alignment"_a = Wt::AlignmentFlag::Left,
            nb::rv_policy::reference_internal,
            "Add a WSplitButton instead of a plain WPushButton. Returns "
            "the same widget for chained access.")
        .def("add_widget",
            [](Wt::WToolBar& self, std::unique_ptr<Wt::WWidget> w,
               Wt::AlignmentFlag alignment) -> Wt::WWidget* {
                Wt::WWidget* raw = w.get();
                self.addWidget(std::move(w), alignment);
                return raw;
            },
            "widget"_a, "alignment"_a = Wt::AlignmentFlag::Left,
            nb::rv_policy::reference_internal)
        .def("add_separator", &Wt::WToolBar::addSeparator,
             "Add a visual divider between groups of items.");

    // ---- WSplitButton: a primary action button with a chevron-dropdown ----
    //
    // Constructs without a menu attached. Build a WPopupMenu, then
    // `split_btn.set_menu(menu)` to wire the dropdown.

    nb::class_<Wt::WSplitButton, Wt::WWidget>(m, "WSplitButton")
        .def(nb::init<>())
        .def(nb::init<const Wt::WString&>(), "label"_a)
        .def_prop_ro("action_button", &Wt::WSplitButton::actionButton,
                     nb::rv_policy::reference_internal,
                     "The primary (left) button — connect `clicked` for the "
                     "default action.")
        .def_prop_ro("drop_down_button", &Wt::WSplitButton::dropDownButton,
                     nb::rv_policy::reference_internal,
                     "The chevron (right) button — clicking it opens the "
                     "attached WPopupMenu.")
        .def("set_menu",
            // Move ownership of the popup menu into the split button.
            [](Wt::WSplitButton& self,
               std::unique_ptr<Wt::WPopupMenu> menu) {
                self.setMenu(std::move(menu));
            },
            "menu"_a,
            "Attach a WPopupMenu as the dropdown. Ownership transfers to "
            "the split button; the Python wrapper becomes a non-owning "
            "alias of whatever the split button now holds.");

    // ---- WNavigationBar: Bootstrap-style top-bar with title, menus,
    //      form fields, and search box ----
    //
    // Built atop WTemplate, themed by WBootstrap5Theme et al. For BS5 the
    // alignment parameter is ignored — use CSS classes (me-auto / ms-auto)
    // for left/right placement; the alignment argument is preserved for
    // older themes and for symmetry with the C++ surface.

    nb::class_<Wt::WNavigationBar, Wt::WTemplate>(m, "WNavigationBar")
        .def(nb::init<>())
        .def("set_title", &Wt::WNavigationBar::setTitle,
             "title"_a, "link"_a = Wt::WLink(),
             "Set the brand/title shown at the left of the nav bar. "
             "Optionally wraps it in a link.")
        .def("set_responsive", &Wt::WNavigationBar::setResponsive,
             "responsive"_a,
             "When True, collapses the contents into a hamburger menu on "
             "narrow viewports (Bootstrap responsive behaviour). Wt has no "
             "getter for this — the flag is write-only on the C++ side.")
        .def("add_menu",
            [](Wt::WNavigationBar& self, std::unique_ptr<Wt::WMenu> menu,
               Wt::AlignmentFlag alignment) -> Wt::WMenu* {
                return self.addMenu(std::move(menu), alignment);
            },
            "menu"_a, "alignment"_a = Wt::AlignmentFlag::Left,
            nb::rv_policy::reference_internal)
        .def("add_form_field",
            [](Wt::WNavigationBar& self, std::unique_ptr<Wt::WWidget> w,
               Wt::AlignmentFlag alignment) -> Wt::WWidget* {
                Wt::WWidget* raw = w.get();
                self.addFormField(std::move(w), alignment);
                return raw;
            },
            "widget"_a, "alignment"_a = Wt::AlignmentFlag::Left,
            nb::rv_policy::reference_internal,
            "Embed a form field (e.g. a small WLineEdit for a search bar). "
            "Distinct from the standalone add_search variant only in styling.")
        .def("add_search",
            [](Wt::WNavigationBar& self, std::unique_ptr<Wt::WLineEdit> field,
               Wt::AlignmentFlag alignment) -> Wt::WLineEdit* {
                Wt::WLineEdit* raw = field.get();
                self.addSearch(std::move(field), alignment);
                return raw;
            },
            "field"_a, "alignment"_a = Wt::AlignmentFlag::Left,
            nb::rv_policy::reference_internal)
        .def("add_widget",
            // WNavigationBar::addWidget returns void; we wrap to return the
            // raw pointer for the same chained-access ergonomics as
            // everywhere else in the binding.
            [](Wt::WNavigationBar& self, std::unique_ptr<Wt::WWidget> w,
               Wt::AlignmentFlag alignment) -> Wt::WWidget* {
                Wt::WWidget* raw = w.get();
                self.addWidget(std::move(w), alignment);
                return raw;
            },
            "widget"_a, "alignment"_a = Wt::AlignmentFlag::Left,
            nb::rv_policy::reference_internal);
}

}  // namespace witty_for_python
