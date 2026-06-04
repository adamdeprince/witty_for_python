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

    nb::enum_<Wt::AlignmentFlag>(m, "AlignmentFlag", nb::is_arithmetic(),
        "Bit flags for positioning items inside containers that support\n"
        "left/right justification (WNavigationBar, WToolBar) or horizontal/\n"
        "vertical alignment (WBoxLayout, WGridLayout). The arithmetic trait\n"
        "lets the values be OR'd together where Wt accepts a combined flag\n"
        "set.")
        .value("Left", Wt::AlignmentFlag::Left)
        .value("Right", Wt::AlignmentFlag::Right)
        .value("Center", Wt::AlignmentFlag::Center)
        .value("Justify", Wt::AlignmentFlag::Justify)
        .value("Baseline", Wt::AlignmentFlag::Baseline)
        .value("Top", Wt::AlignmentFlag::Top)
        .value("Middle", Wt::AlignmentFlag::Middle)
        .value("Bottom", Wt::AlignmentFlag::Bottom);

    // ---- WPoint: integer 2-D coordinate, used by WPopupMenu.popup() ----

    nb::class_<Wt::WPoint>(m, "WPoint",
        "Integer (x, y) coordinate pair in page-relative pixels.\n"
        "Used as the position argument to `WPopupMenu.popup(point)`.\n"
        "\n"
        "    menu.popup(wt.WPoint(120, 80))")
        .def(nb::init<>(),
             "Construct a point at the origin (0, 0).")
        .def(nb::init<int, int>(), "x"_a, "y"_a,
             "Construct a point at (`x`, `y`).")
        .def_prop_rw("x", &Wt::WPoint::x, &Wt::WPoint::setX,
            "Horizontal coordinate in pixels.")
        .def_prop_rw("y", &Wt::WPoint::y, &Wt::WPoint::setY,
            "Vertical coordinate in pixels.")
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

    nb::class_<Wt::WPopupMenu, Wt::WMenu>(m, "WPopupMenu",
        "Floating menu that appears at a screen location on demand.\n"
        "Inherits the full WMenu surface (add_item, etc.) so building\n"
        "entries works the same; what's added is the ability to summon\n"
        "the menu at a point, at a mouse event, or anchored to a widget.\n"
        "\n"
        "    menu = wt.WPopupMenu()\n"
        "    menu.add_item('Cut')\n"
        "    menu.add_item('Copy')\n"
        "    container.add_widget(wt.WPushButton('Edit')).clicked.connect(\n"
        "        lambda e: menu.popup(e))\n"
        "    menu.triggered.connect(lambda item: handle(item.text))\n"
        "\n"
        "Pair with `set_button(btn)` for the typical menu-button UX, or\n"
        "call `popup(...)` yourself from a slot. With `hide_on_select`\n"
        "left at its default of True, `triggered` is the signal you watch\n"
        "for to know the user picked something.")
        .def(nb::new_([]() {
            return std::make_unique<Wt::WPopupMenu>(nullptr);
        }),
             "Construct a standalone popup menu with no items. Use the\n"
             "inherited `add_item` to populate it.")
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

    nb::class_<Wt::WBadge, Wt::WText>(m, "WBadge",
        "Small inline label, typically appended to another widget for\n"
        "counts or status pills (e.g. '12 unread'). Inherits WText, so\n"
        "set the displayed value via the `text` property.\n"
        "\n"
        "    btn = container.add_widget(wt.WPushButton('Inbox'))\n"
        "    btn.add_widget(wt.WBadge('12'))")
        .def(heap_init<Wt::WBadge>(),
             "Construct an empty badge with no caption.")
        .def(heap_init<Wt::WBadge, const Wt::WString&>(), "text"_a,
             "Construct a badge displaying `text`.")
        .def_prop_rw("use_default_style",
            &Wt::WBadge::useDefaultStyle,
            &Wt::WBadge::setUseDefaultStyle,
            "When True (default), Wt applies its theme's badge CSS class. "
            "Disable to style purely via your own classes/CSS.");

    // ---- WToolBar: horizontal/vertical row of buttons + separators ----

    nb::class_<Wt::WToolBar, Wt::WWidget>(m, "WToolBar",
        "A row (or column) of buttons with optional separators between\n"
        "groups. Add buttons via `add_button`; mix in arbitrary widgets\n"
        "with `add_widget` for non-button controls.\n"
        "\n"
        "    bar = container.add_widget(wt.WToolBar())\n"
        "    bar.add_button(wt.WPushButton('Save')).clicked.connect(save)\n"
        "    bar.add_separator()\n"
        "    bar.add_button(wt.WPushButton('Quit')).clicked.connect(app.quit)")
        .def(heap_init<Wt::WToolBar>(),
             "Construct an empty toolbar with horizontal orientation.")
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
        // Re-arm pattern: transfer ownership, mark wrapper non-owning, return
        // the SAME Python object for fluent chaining (identity + subtype
        // preserved). See docs/binding_design.md §4.2. Polymorphic on
        // WPushButton vs WSplitButton — Wt has separate overloads.
        .def("add_button",
            [](Wt::WToolBar& self, nb::object py_btn,
               Wt::AlignmentFlag alignment) -> nb::object {
                if (nb::isinstance<Wt::WSplitButton>(py_btn)) {
                    auto btn = nb::cast<std::unique_ptr<Wt::WSplitButton>>(py_btn);
                    self.addButton(std::move(btn), alignment);
                } else {
                    auto btn = nb::cast<std::unique_ptr<Wt::WPushButton>>(py_btn);
                    self.addButton(std::move(btn), alignment);
                }
                nb::inst_set_state(py_btn, /*ready*/ true,
                                   /*destruct*/ false);
                return py_btn;
            },
            "button"_a, "alignment"_a = Wt::AlignmentFlag::Left,
            "Transfer ownership of `button` to the toolbar (a WPushButton\n"
            "or WSplitButton) and return the same Python wrapper, re-armed\n"
            "as a non-owning alias for chaining. `alignment` controls\n"
            "left/right placement when the theme supports it.\n"
            "\n"
            "    bar.add_button(wt.WPushButton('Help'),\n"
            "                   wt.AlignmentFlag.Right).clicked.connect(open_help)")
        .def("add_widget",
            [](Wt::WToolBar& self, nb::object py_widget,
               Wt::AlignmentFlag alignment) -> nb::object {
                auto w = nb::cast<std::unique_ptr<Wt::WWidget>>(py_widget);
                self.addWidget(std::move(w), alignment);
                nb::inst_set_state(py_widget, /*ready*/ true,
                                   /*destruct*/ false);
                return py_widget;
            },
            "widget"_a, "alignment"_a = Wt::AlignmentFlag::Left,
            "Add an arbitrary widget (not necessarily a button) to the\n"
            "toolbar at the given alignment. Same ownership-transfer +\n"
            "re-arm pattern as `add_button`.")
        .def("add_separator", &Wt::WToolBar::addSeparator,
             "Add a visual divider between groups of items.");

    // ---- WSplitButton: a primary action button with a chevron-dropdown ----
    //
    // Constructs without a menu attached. Build a WPopupMenu, then
    // `split_btn.set_menu(menu)` to wire the dropdown.

    nb::class_<Wt::WSplitButton, Wt::WWidget>(m, "WSplitButton",
        "A primary action button with a small chevron next to it that\n"
        "opens a dropdown menu — the typical 'Save / Save As…' split\n"
        "button found in toolbars. Build a WPopupMenu, attach it via\n"
        "`set_menu`, then wire `action_button.clicked` for the default\n"
        "action.\n"
        "\n"
        "    sb = bar.add_button(wt.WSplitButton('Save'))\n"
        "    sb.action_button.clicked.connect(save_default)\n"
        "    menu = wt.WPopupMenu()\n"
        "    menu.add_item('Save As…')\n"
        "    menu.add_item('Save All')\n"
        "    sb.set_menu(menu)")
        .def(heap_init<Wt::WSplitButton>(),
             "Construct an unlabelled split button with no menu attached.")
        .def(heap_init<Wt::WSplitButton, const Wt::WString&>(), "label"_a,
             "Construct a split button captioned `label` with no menu\n"
             "attached. Use `set_menu` to wire the dropdown.")
        .def_prop_ro("action_button", &Wt::WSplitButton::actionButton,
                     nb::rv_policy::reference_internal,
                     "The primary (left) button — connect `clicked` for the "
                     "default action.")
        .def_prop_ro("drop_down_button", &Wt::WSplitButton::dropDownButton,
                     nb::rv_policy::reference_internal,
                     "The chevron (right) button — clicking it opens the "
                     "attached WPopupMenu.")
        .def("set_menu",
            [](Wt::WSplitButton& self, nb::object py_menu) {
                auto m = nb::cast<std::unique_ptr<Wt::WPopupMenu>>(py_menu);
                self.setMenu(std::move(m));
                nb::inst_set_state(py_menu, /*ready*/ true,
                                   /*destruct*/ false);
            },
            "menu"_a,
            "Attach a WPopupMenu as the dropdown. Ownership transfers to "
            "the split button; the Python wrapper becomes a non-owning "
            "alias of the menu the split button now holds.");

    // ---- WNavigationBar: Bootstrap-style top-bar with title, menus,
    //      form fields, and search box ----
    //
    // Built atop WTemplate, themed by WBootstrap5Theme et al. For BS5 the
    // alignment parameter is ignored — use CSS classes (me-auto / ms-auto)
    // for left/right placement; the alignment argument is preserved for
    // older themes and for symmetry with the C++ surface.

    nb::class_<Wt::WNavigationBar, Wt::WTemplate>(m, "WNavigationBar",
        "A page-top navigation bar in the Bootstrap idiom: brand on the\n"
        "left, menus and form fields stacked horizontally, optional\n"
        "search box. Collapses into a hamburger menu on narrow viewports\n"
        "when `set_responsive(True)` is set.\n"
        "\n"
        "    nav = app.root.add_widget(wt.WNavigationBar())\n"
        "    nav.set_title('My App', wt.WLink('/'))\n"
        "    nav.set_responsive(True)\n"
        "    menu = wt.WMenu()\n"
        "    menu.add_item('Home')\n"
        "    menu.add_item('About')\n"
        "    nav.add_menu(menu)")
        .def(heap_init<Wt::WNavigationBar>(),
             "Construct an empty navigation bar. Use `set_title` /\n"
             "`add_menu` / `add_search` to populate it.")
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
            [](Wt::WNavigationBar& self, nb::object py_menu,
               Wt::AlignmentFlag alignment) -> nb::object {
                auto m = nb::cast<std::unique_ptr<Wt::WMenu>>(py_menu);
                self.addMenu(std::move(m), alignment);
                nb::inst_set_state(py_menu, /*ready*/ true,
                                   /*destruct*/ false);
                return py_menu;
            },
            "menu"_a, "alignment"_a = Wt::AlignmentFlag::Left,
            "Embed a WMenu in the nav bar. Ownership transfers; the\n"
            "Python wrapper is re-armed as a non-owning alias of the menu\n"
            "the bar now holds.")
        .def("add_form_field",
            [](Wt::WNavigationBar& self, nb::object py_widget,
               Wt::AlignmentFlag alignment) -> nb::object {
                auto w = nb::cast<std::unique_ptr<Wt::WWidget>>(py_widget);
                self.addFormField(std::move(w), alignment);
                nb::inst_set_state(py_widget, /*ready*/ true,
                                   /*destruct*/ false);
                return py_widget;
            },
            "widget"_a, "alignment"_a = Wt::AlignmentFlag::Left,
            "Embed a form field (e.g. a small WLineEdit for a search bar). "
            "Distinct from the standalone add_search variant only in styling.")
        .def("add_search",
            [](Wt::WNavigationBar& self, nb::object py_field,
               Wt::AlignmentFlag alignment) -> nb::object {
                auto f = nb::cast<std::unique_ptr<Wt::WLineEdit>>(py_field);
                self.addSearch(std::move(f), alignment);
                nb::inst_set_state(py_field, /*ready*/ true,
                                   /*destruct*/ false);
                return py_field;
            },
            "field"_a, "alignment"_a = Wt::AlignmentFlag::Left,
            "Add a styled search box (a WLineEdit) to the nav bar.\n"
            "Functionally similar to `add_form_field` but themed as a\n"
            "search input.")
        .def("add_widget",
            [](Wt::WNavigationBar& self, nb::object py_widget,
               Wt::AlignmentFlag alignment) -> nb::object {
                auto w = nb::cast<std::unique_ptr<Wt::WWidget>>(py_widget);
                self.addWidget(std::move(w), alignment);
                nb::inst_set_state(py_widget, /*ready*/ true,
                                   /*destruct*/ false);
                return py_widget;
            },
            "widget"_a, "alignment"_a = Wt::AlignmentFlag::Left,
            "Add an arbitrary widget to the nav bar at the given\n"
            "alignment. Same ownership-transfer + re-arm pattern as\n"
            "`add_menu`.");
}

}  // namespace witty_for_python
