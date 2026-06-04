#include "common.hpp"
#include "signal_helpers.hpp"

#include <Wt/WDialog.h>
#include <Wt/WFlags.h>
#include <Wt/WGlobal.h>      // Wt::DialogCode, Wt::StandardButton
#include <Wt/WGroupBox.h>
#include <Wt/WMenu.h>
#include <Wt/WMenuItem.h>
#include <Wt/WMessageBox.h>
#include <Wt/WPanel.h>
#include <Wt/WPushButton.h>
#include <Wt/WStackedWidget.h>
#include <Wt/WTabWidget.h>
#include <Wt/WWidget.h>

#include <memory>
#include <string>

namespace witty_for_python {

void register_navigation(nb::module_& m) {
    // ---- Enums ----

    nb::enum_<Wt::DialogCode>(m, "DialogCode",
        "Outcome of a closed WDialog. `Accepted` if `accept()` was\n"
        "called, `Rejected` if `reject()` was called or the dialog was\n"
        "dismissed via Escape / close button.")
        .value("Rejected", Wt::DialogCode::Rejected)
        .value("Accepted", Wt::DialogCode::Accepted);

    // StandardButton is a bit-flag enum; expose as arithmetic so users can
    // OR values together in Python (`Ok | Cancel`) and pass the resulting
    // int to set_standard_buttons().
    nb::enum_<Wt::StandardButton>(m, "StandardButton", nb::is_arithmetic(),
        "Bit-flag enum identifying the standard buttons a WMessageBox\n"
        "can show. Combine with `|` to request several at once:\n"
        "\n"
        "    box.set_standard_buttons(wt.StandardButton.Ok | wt.StandardButton.Cancel)")
        .value("None_", Wt::StandardButton::None)
        .value("Ok", Wt::StandardButton::Ok)
        .value("Cancel", Wt::StandardButton::Cancel)
        .value("Yes", Wt::StandardButton::Yes)
        .value("No", Wt::StandardButton::No)
        .value("Abort", Wt::StandardButton::Abort)
        .value("Retry", Wt::StandardButton::Retry)
        .value("Ignore", Wt::StandardButton::Ignore)
        .value("YesAll", Wt::StandardButton::YesAll)
        .value("NoAll", Wt::StandardButton::NoAll);

    // ---- Enum-payload signals ----

    nb::class_<Wt::Signal<Wt::DialogCode>>(m, "DialogCodeSignal",
        "Signal payload type for WDialog's `finished` — fires with a\n"
        "DialogCode when the dialog closes.")
        .def("connect",
            [](Wt::Signal<Wt::DialogCode>& s, nb::callable cb) {
                return py_connect<Wt::Signal<Wt::DialogCode>,
                                  Wt::DialogCode>(s, std::move(cb));
            }, "callable"_a,
            "Subscribe `callable` to the signal. Returns a Connection;\n"
            "call `.disconnect()` on it to stop receiving.")
        .def("disconnect_all_slots",
            [](Wt::Signal<Wt::DialogCode>& s) {
                connection_registry_disconnect_all(&s);
            },
            "Disconnect every Python callback currently bound to this\n"
            "signal.");

    nb::class_<Wt::Signal<Wt::StandardButton>>(m, "StandardButtonSignal",
        "Signal payload type for WMessageBox's `button_clicked` — fires\n"
        "with the StandardButton the user picked.")
        .def("connect",
            [](Wt::Signal<Wt::StandardButton>& s, nb::callable cb) {
                return py_connect<Wt::Signal<Wt::StandardButton>,
                                  Wt::StandardButton>(s, std::move(cb));
            }, "callable"_a,
            "Subscribe `callable` to the signal. Returns a Connection;\n"
            "call `.disconnect()` on it to stop receiving.")
        .def("disconnect_all_slots",
            [](Wt::Signal<Wt::StandardButton>& s) {
                connection_registry_disconnect_all(&s);
            },
            "Disconnect every Python callback currently bound to this\n"
            "signal.");

    // ---- WStackedWidget ----

    nb::class_<Wt::WStackedWidget, Wt::WContainerWidget>(m, "WStackedWidget",
        "Container that shows exactly one of its children at a time.\n"
        "Each child added becomes a `page`; switch via `current_index`\n"
        "or `set_current_widget`. Pair with WMenu for wizard-style or\n"
        "tabbed navigation that doesn't use WTabWidget's chrome.\n"
        "\n"
        "    stack = container.add_widget(wt.WStackedWidget())\n"
        "    stack.add_widget(wt.WText('First page'))\n"
        "    stack.add_widget(wt.WText('Second page'))\n"
        "    stack.current_index = 1")
        .def(heap_init<Wt::WStackedWidget>(),
             "Construct an empty stacked widget.")
        .def_prop_rw("current_index",
            [](const Wt::WStackedWidget& w) { return w.currentIndex(); },
            [](Wt::WStackedWidget& w, int i) { w.setCurrentIndex(i); },
            "Index of the visible page (0-based). All other children\n"
            "are hidden but kept alive.")
        .def("set_current_widget", &Wt::WStackedWidget::setCurrentWidget,
             "widget"_a,
             "Show `widget`, which must already be a child of this\n"
             "stack.");

    // ---- WMenuItem ----

    nb::class_<Wt::WMenuItem, Wt::WContainerWidget>(m, "WMenuItem",
        "A single entry in a WMenu. Has a label and optionally a\n"
        "`contents` widget that is shown in the menu's associated stack\n"
        "when this item is selected. Items can be checkable, closeable,\n"
        "or link to an internal/external URL.\n"
        "\n"
        "    menu.add_item(wt.WMenuItem('Inbox', wt.WText('No messages.')))")
        .def(heap_init<Wt::WMenuItem, const Wt::WString&>(), "label"_a,
             "Construct a menu item with the given label and no contents\n"
             "widget. Useful for menus that only fire `item_selected`.")
        .def(nb::new_(
                [](const Wt::WString& label,
                   std::unique_ptr<Wt::WWidget> contents) {
                    return std::make_unique<Wt::WMenuItem>(
                        label, std::move(contents));
                }), "label"_a, "contents"_a,
             "Construct a menu item with both a label and a contents\n"
             "widget. When the menu is paired with a WStackedWidget, the\n"
             "contents widget is shown in that stack on selection.")
        .def_prop_rw("text",
            [](const Wt::WMenuItem& w) { return w.text(); },
            [](Wt::WMenuItem& w, const Wt::WString& t) { w.setText(t); },
            "The item's label.")
        .def("set_link", &Wt::WMenuItem::setLink, "link"_a,
             "Turn the item into a hyperlink — clicking it navigates to\n"
             "the given WLink instead of (or in addition to) emitting\n"
             "selection.")
        .def_prop_rw("checkable",
            [](const Wt::WMenuItem& w) { return w.isCheckable(); },
            [](Wt::WMenuItem& w, bool c) { w.setCheckable(c); },
            "Whether the item shows a check mark when selected — turns\n"
            "it into a toggleable menu entry.")
        .def_prop_rw("checked",
            [](const Wt::WMenuItem& w) { return w.isChecked(); },
            [](Wt::WMenuItem& w, bool b) { w.setChecked(b); },
            "The checked state, for a checkable item.")
        .def("select", &Wt::WMenuItem::select,
             "Select this item programmatically, as if the user had\n"
             "clicked it. Fires `item_selected` on the parent menu.")
        .def("set_selectable", &Wt::WMenuItem::setSelectable, "selectable"_a,
             "Whether the item responds to clicks. Disable for section\n"
             "headers or dividers.")
        .def("set_closeable", &Wt::WMenuItem::setCloseable, "closeable"_a,
             "Whether the item shows a close button. The user can then\n"
             "remove it from the menu by clicking that button.");

    // Signal<WMenuItem*> for WMenu::itemSelected
    nb::class_<Wt::Signal<Wt::WMenuItem*>>(m, "MenuItemSignal",
        "Signal payload type for WMenu's `item_selected` — fires with\n"
        "the WMenuItem the user picked.")
        .def("connect",
            [](Wt::Signal<Wt::WMenuItem*>& s, nb::callable cb) {
                return py_connect<Wt::Signal<Wt::WMenuItem*>,
                                  Wt::WMenuItem*>(s, std::move(cb));
            }, "callable"_a,
            "Subscribe `callable` to the signal. Returns a Connection;\n"
            "call `.disconnect()` on it to stop receiving.")
        .def("disconnect_all_slots",
            [](Wt::Signal<Wt::WMenuItem*>& s) {
                connection_registry_disconnect_all(&s);
            },
            "Disconnect every Python callback currently bound to this\n"
            "signal.");

    // ---- WMenu ----

    // WMenu, WTabWidget, WPanel, WDialog all inherit via WCompositeWidget,
    // which derives directly from WWidget — they skip WInteractWidget. We
    // therefore use WWidget as the Python-visible base.
    nb::class_<Wt::WMenu, Wt::WWidget>(m, "WMenu",
        "A list of selectable items (sidebar nav, vertical or horizontal\n"
        "menu, tab strip…). Pair with a WStackedWidget at construction\n"
        "time to have the selected item's `contents` show up in the\n"
        "stack automatically.\n"
        "\n"
        "    stack = container.add_widget(wt.WStackedWidget())\n"
        "    menu = container.add_widget(wt.WMenu(stack))\n"
        "    menu.add_item(wt.WMenuItem('Home', wt.WText('Welcome!')))\n"
        "    menu.add_item(wt.WMenuItem('About', wt.WText('About us.')))\n"
        "    menu.item_selected.connect(lambda item: print(item.text))")
        .def(heap_init<Wt::WMenu>(),
             "Construct a menu without an associated content stack.")
        .def(heap_init<Wt::WMenu, Wt::WStackedWidget*>(), "contents_stack"_a,
             "Construct a menu wired to the given WStackedWidget — when\n"
             "the user picks an item, the corresponding `contents` widget\n"
             "is made the visible page of `contents_stack`.")
        // String overload — wraps the label in a fresh WMenuItem.
        // Python-only convenience; Wt has no addItem(WString) on WMenu.
        // Listed BEFORE the widget overload so `menu.add_item("hi")` doesn't
        // route through the `nb::object → unique_ptr` cast that would
        // `std::bad_cast` on a str.
        .def("add_item",
            [](Wt::WMenu& self, const Wt::WString& label) {
                return self.addItem(std::make_unique<Wt::WMenuItem>(label));
            },
            "label"_a, nb::rv_policy::reference_internal,
            "Convenience for `add_item(WMenuItem(label))`. Returns a\n"
            "non-owning handle to the freshly-constructed item.")
        // Widget overload — re-arm pattern: takes the Python wrapper,
        // transfers ownership, marks the wrapper non-owning, returns it.
        .def("add_item",
            [](Wt::WMenu& self, nb::object py_item) -> nb::object {
                auto it = nb::cast<std::unique_ptr<Wt::WMenuItem>>(py_item);
                self.addItem(std::move(it));
                nb::inst_set_state(py_item, /*ready*/ true,
                                   /*destruct*/ false);
                return py_item;
            },
            "item"_a,
            "Transfer ownership of `item` to the menu and return the\n"
            "same Python wrapper, re-armed as a non-owning alias.")
        // Bulk add of pre-built items.
        .def("add_items",
            [](Wt::WMenu& self, nb::list py_items) -> nb::list {
                nb::list out;
                for (nb::handle h : py_items) {
                    nb::object py_it = nb::borrow(h);
                    auto it = nb::cast<std::unique_ptr<Wt::WMenuItem>>(py_it);
                    self.addItem(std::move(it));
                    nb::inst_set_state(py_it, /*ready*/ true,
                                       /*destruct*/ false);
                    out.append(py_it);
                }
                return out;
            },
            "items"_a,
            "Bulk version of the widget-taking `add_item`. Returns the\n"
            "same wrappers, each re-armed as a non-owning alias.")
        // Bulk add of labels — each is wrapped in a fresh WMenuItem.
        .def("add_items",
            [](Wt::WMenu& self, const std::vector<Wt::WString>& labels) {
                for (const auto& l : labels) {
                    self.addItem(std::make_unique<Wt::WMenuItem>(l));
                }
            },
            "labels"_a,
            "Bulk version of the string-taking `add_item`. Wraps each\n"
            "label in a fresh WMenuItem.")
        .def("select",
             nb::overload_cast<int>(&Wt::WMenu::select),
             "index"_a,
             "Programmatically select the item at position `index`.\n"
             "Fires `item_selected`.")
        .def("current_item", &Wt::WMenu::currentItem,
             nb::rv_policy::reference_internal,
             "Return a non-owning handle to the currently-selected item,\n"
             "or None if nothing is selected.")
        .def_prop_ro("item_selected", &Wt::WMenu::itemSelected,
                     nb::rv_policy::reference_internal,
                     "Fires with the WMenuItem the user selected (a\n"
                     "MenuItemSignal).");

    // ---- WTabWidget ----

    nb::class_<Wt::WTabWidget, Wt::WWidget>(m, "WTabWidget",
        "Tab strip on top of a stacked content area. Each `add_tab`\n"
        "registers one tab whose contents are the widget you pass.\n"
        "\n"
        "    tabs = container.add_widget(wt.WTabWidget())\n"
        "    tabs.add_tab(wt.WText('General settings.'), 'General')\n"
        "    tabs.add_tab(wt.WText('Account settings.'), 'Account')\n"
        "    tabs.current_changed.connect(lambda i: print('on tab', i))")
        .def(heap_init<Wt::WTabWidget>(),
             "Construct an empty tab widget.")
        // add_tab returns a WMenuItem (the new tab handle) via Wt's API;
        // we still re-arm the child wrapper so `tabs.add_tab(c, "t")` then
        // using `c` continues to work.
        .def("add_tab",
            [](Wt::WTabWidget& self, nb::object py_child,
               const Wt::WString& label) {
                auto child = nb::cast<std::unique_ptr<Wt::WWidget>>(py_child);
                auto* item = self.addTab(std::move(child), label);
                nb::inst_set_state(py_child, /*ready*/ true,
                                   /*destruct*/ false);
                return item;
            },
            "child"_a, "label"_a,
            nb::rv_policy::reference_internal,
            "Add a new tab whose content is `child` and whose label is\n"
            "`label`. Takes ownership of `child` (the Python wrapper is\n"
            "re-armed as a non-owning alias). Returns the WMenuItem that\n"
            "represents the new tab — useful for further per-tab tweaks.")
        .def_prop_ro("count", &Wt::WTabWidget::count,
            "Number of tabs currently in the widget.")
        .def("index_of", &Wt::WTabWidget::indexOf, "widget"_a,
             "Return the tab index whose contents are `widget`, or -1\n"
             "if `widget` is not a tab's content.")
        .def_prop_rw("current_index",
            [](const Wt::WTabWidget& w) { return w.currentIndex(); },
            [](Wt::WTabWidget& w, int i) { w.setCurrentIndex(i); },
            "Index of the visible tab.")
        .def("set_tab_enabled", &Wt::WTabWidget::setTabEnabled,
             "index"_a, "enable"_a,
             "Enable or disable the tab at `index`. Disabled tabs render\n"
             "greyed out and can't be selected.")
        .def("set_tab_hidden", &Wt::WTabWidget::setTabHidden,
             "index"_a, "hidden"_a,
             "Hide or show the tab at `index`. Hidden tabs keep their\n"
             "contents but don't appear in the tab strip.")
        .def("set_tab_closeable", &Wt::WTabWidget::setTabCloseable,
             "index"_a, "closeable"_a,
             "Whether the tab at `index` shows a close (×) button.")
        .def("set_tab_text", &Wt::WTabWidget::setTabText, "index"_a, "label"_a,
             "Set the label shown on the tab at `index`.")
        .def("tab_text", &Wt::WTabWidget::tabText, "index"_a,
             "Return the current label of the tab at `index`.")
        .def_prop_ro("current_changed", &Wt::WTabWidget::currentChanged,
                     nb::rv_policy::reference_internal,
                     "Fires with the new int index whenever the active\n"
                     "tab changes.");

    // ---- WPanel / WGroupBox ----

    nb::class_<Wt::WPanel, Wt::WWidget>(m, "WPanel",
        "A titled box holding a single central widget. Optionally\n"
        "collapsible (the user can fold it down to just the title bar).\n"
        "\n"
        "    panel = container.add_widget(wt.WPanel())\n"
        "    panel.title = 'Details'\n"
        "    panel.collapsible = True\n"
        "    panel.set_central_widget(wt.WText('More info here.'))")
        .def(heap_init<Wt::WPanel>(),
             "Construct an empty panel.")
        .def_prop_rw("title",
            [](const Wt::WPanel& w) { return w.title(); },
            [](Wt::WPanel& w, const Wt::WString& t) { w.setTitle(t); },
            "Text shown in the title bar.")
        .def("set_title_bar", &Wt::WPanel::setTitleBar, "enable"_a,
             "Whether the title bar is rendered. Disabling hides both\n"
             "the title and the collapse toggle.")
        .def_prop_ro("title_bar", &Wt::WPanel::titleBar,
            "Non-owning handle to the title-bar widget — useful for\n"
            "adding extra controls (e.g. action buttons) next to the\n"
            "title.")
        .def_prop_rw("collapsible",
            [](const Wt::WPanel& w) { return w.isCollapsible(); },
            [](Wt::WPanel& w, bool on) { w.setCollapsible(on); },
            "Whether the panel can be collapsed by the user. Enabling\n"
            "adds an expand/collapse toggle to the title bar.")
        .def_prop_rw("collapsed",
            [](const Wt::WPanel& w) { return w.isCollapsed(); },
            [](Wt::WPanel& w, bool on) { w.setCollapsed(on); },
            "The current collapsed state. Only meaningful when\n"
            "`collapsible` is True.")
        .def("collapse", &Wt::WPanel::collapse,
             "Fold the panel down to just its title bar.")
        .def("expand", &Wt::WPanel::expand,
             "Restore the panel to its full size.")
        .def("set_central_widget",
            [](Wt::WPanel& self, nb::object py_widget) {
                auto w = nb::cast<std::unique_ptr<Wt::WWidget>>(py_widget);
                self.setCentralWidget(std::move(w));
                nb::inst_set_state(py_widget, /*ready*/ true,
                                   /*destruct*/ false);
            },
            "widget"_a,
            "Install `widget` as the panel's single content widget,\n"
            "replacing any previous one. The panel takes ownership; the\n"
            "Python wrapper is re-armed as a non-owning alias.");

    nb::class_<Wt::WGroupBox, Wt::WContainerWidget>(m, "WGroupBox",
        "A container with a border and a caption — renders as HTML\n"
        "`<fieldset>` with a `<legend>`. Use to visually group a few\n"
        "related form widgets.\n"
        "\n"
        "    group = container.add_widget(wt.WGroupBox('Address'))\n"
        "    group.add_widget(wt.WLineEdit())\n"
        "    group.add_widget(wt.WLineEdit())")
        .def(heap_init<Wt::WGroupBox>(),
             "Construct an untitled group box.")
        .def(heap_init<Wt::WGroupBox, const Wt::WString&>(), "title"_a,
             "Construct a group box captioned `title`.")
        .def_prop_rw("title",
            [](const Wt::WGroupBox& w) { return w.title(); },
            [](Wt::WGroupBox& w, const Wt::WString& t) { w.setTitle(t); },
            "Caption text — the `<legend>`.");

    // ---- WDialog + WMessageBox ----
    //
    // WDialog inherits WPopupWidget → WCompositeWidget → WWidget; we present
    // it under WWidget on the Python side.

    nb::class_<Wt::WDialog, Wt::WWidget>(m, "WDialog",
        "A pop-up window with a title bar, content area, and footer.\n"
        "Modal by default. Build up the `contents` container, call\n"
        "`show()`, and react via the `finished` signal (which fires with\n"
        "a DialogCode).\n"
        "\n"
        "    dlg = wt.WDialog('Confirm')\n"
        "    dlg.contents.add_widget(wt.WText('Really delete?'))\n"
        "    ok = dlg.footer.add_widget(wt.WPushButton('OK'))\n"
        "    cancel = dlg.footer.add_widget(wt.WPushButton('Cancel'))\n"
        "    ok.clicked.connect(dlg.accept)\n"
        "    cancel.clicked.connect(dlg.reject)\n"
        "    dlg.finished.connect(lambda code: print(code))\n"
        "    dlg.show()")
        .def(heap_init<Wt::WDialog>(),
             "Construct a dialog with no title.")
        .def(heap_init<Wt::WDialog, const Wt::WString&>(), "window_title"_a,
             "Construct a dialog with the given title bar caption.")
        .def_prop_rw("window_title",
            [](const Wt::WDialog& w) { return w.windowTitle(); },
            [](Wt::WDialog& w, const Wt::WString& t) { w.setWindowTitle(t); },
            "Caption shown in the dialog's title bar.")
        .def_prop_rw("modal",
            [](const Wt::WDialog& w) { return w.isModal(); },
            [](Wt::WDialog& w, bool m) { w.setModal(m); },
            "Whether the dialog blocks interaction with the rest of the\n"
            "page while it's shown.")
        .def_prop_rw("closable",
            [](const Wt::WDialog& w) { return w.closable(); },
            [](Wt::WDialog& w, bool c) { w.setClosable(c); },
            "Whether the title bar shows a close (×) button that rejects\n"
            "the dialog.")
        .def("set_resizable", &Wt::WDialog::setResizable, "resizable"_a,
             "Whether the user can drag the dialog's edges to resize it.")
        .def("show", &Wt::WDialog::show,
             "Display the dialog. If modal, blocks page interaction\n"
             "until accepted, rejected, or closed.")
        .def("accept", &Wt::WDialog::accept,
             "Close with `DialogCode.Accepted`. Convenient slot for an\n"
             "OK button's `clicked` signal.")
        .def("reject", &Wt::WDialog::reject,
             "Close with `DialogCode.Rejected`. Convenient slot for a\n"
             "Cancel button's `clicked` signal.")
        .def("done", &Wt::WDialog::done, "result"_a,
             "Close with an explicit DialogCode.")
        .def("reject_when_escape_pressed",
             &Wt::WDialog::rejectWhenEscapePressed,
             "enable"_a = true,
             "Whether pressing Escape rejects the dialog.")
        // contents / title_bar_widget / footer are behaviorless getters of
        // stable inner containers — expose as read-only attributes.
        .def_prop_ro("contents", &Wt::WDialog::contents,
                     nb::rv_policy::reference_internal,
                     "Non-owning handle to the dialog's content container.\n"
                     "Add the dialog body widgets here.")
        .def_prop_ro("title_bar_widget", &Wt::WDialog::titleBar,
                     nb::rv_policy::reference_internal,
                     "Non-owning handle to the title-bar container. Use\n"
                     "to inject custom controls into the title strip.")
        .def_prop_ro("footer", &Wt::WDialog::footer,
                     nb::rv_policy::reference_internal,
                     "Non-owning handle to the footer container. Conventional\n"
                     "place for the OK / Cancel buttons.")
        .def_prop_ro("result", &Wt::WDialog::result,
            "Final DialogCode after `accept` / `reject` / `done`.")
        .def_prop_ro("finished", &Wt::WDialog::finished,
                     nb::rv_policy::reference_internal,
                     "Fires with the DialogCode when the dialog closes\n"
                     "(a DialogCodeSignal).");

    nb::class_<Wt::WMessageBox, Wt::WDialog>(m, "WMessageBox",
        "Standard alert/confirm dialog — a WDialog preset with a message\n"
        "and a row of standard buttons.\n"
        "\n"
        "    box = wt.WMessageBox()\n"
        "    box.window_title = 'Confirm'\n"
        "    box.text = 'Discard unsaved changes?'\n"
        "    box.set_standard_buttons(wt.StandardButton.Yes | wt.StandardButton.No)\n"
        "    box.button_clicked.connect(lambda btn: print(btn))\n"
        "    box.show()")
        .def(heap_init<Wt::WMessageBox>(),
             "Construct an empty message box. Set `text` and `set_standard\n"
             "_buttons` before showing.")
        .def_prop_rw("text",
            [](const Wt::WMessageBox& w) { return w.text(); },
            [](Wt::WMessageBox& w, const Wt::WString& t) { w.setText(t); },
            "Message body shown in the dialog.")
        .def("set_standard_buttons",
            [](Wt::WMessageBox& m, int flags) {
                m.setStandardButtons(Wt::WFlags<Wt::StandardButton>(
                    static_cast<Wt::StandardButton>(flags)));
            },
            "buttons"_a,
            "Configure which buttons to display. `buttons` is an int\n"
            "made by OR-ing StandardButton values together — e.g.\n"
            "`StandardButton.Ok | StandardButton.Cancel`.")
        .def_prop_ro("button_result", &Wt::WMessageBox::buttonResult,
            "The StandardButton the user clicked, available after the\n"
            "box has closed.")
        .def_prop_ro("button_clicked", &Wt::WMessageBox::buttonClicked,
                     nb::rv_policy::reference_internal,
                     "Fires with the StandardButton that was clicked (a\n"
                     "StandardButtonSignal).");
}

}  // namespace witty_for_python
