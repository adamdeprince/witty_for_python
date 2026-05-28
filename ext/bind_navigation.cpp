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

    nb::enum_<Wt::DialogCode>(m, "DialogCode")
        .value("Rejected", Wt::DialogCode::Rejected)
        .value("Accepted", Wt::DialogCode::Accepted);

    // StandardButton is a bit-flag enum; expose as arithmetic so users can
    // OR values together in Python (`Ok | Cancel`) and pass the resulting
    // int to set_standard_buttons().
    nb::enum_<Wt::StandardButton>(m, "StandardButton", nb::is_arithmetic())
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

    nb::class_<Wt::Signal<Wt::DialogCode>>(m, "DialogCodeSignal")
        .def("connect",
            [](Wt::Signal<Wt::DialogCode>& s, nb::callable cb) {
                return py_connect<Wt::Signal<Wt::DialogCode>,
                                  Wt::DialogCode>(s, std::move(cb));
            }, "callable"_a)
        .def("disconnect_all_slots",
            [](Wt::Signal<Wt::DialogCode>& s) {
                connection_registry_disconnect_all(&s);
            });

    nb::class_<Wt::Signal<Wt::StandardButton>>(m, "StandardButtonSignal")
        .def("connect",
            [](Wt::Signal<Wt::StandardButton>& s, nb::callable cb) {
                return py_connect<Wt::Signal<Wt::StandardButton>,
                                  Wt::StandardButton>(s, std::move(cb));
            }, "callable"_a)
        .def("disconnect_all_slots",
            [](Wt::Signal<Wt::StandardButton>& s) {
                connection_registry_disconnect_all(&s);
            });

    // ---- WStackedWidget ----

    nb::class_<Wt::WStackedWidget, Wt::WContainerWidget>(m, "WStackedWidget")
        .def(heap_init<Wt::WStackedWidget>())
        .def_prop_rw("current_index",
            [](const Wt::WStackedWidget& w) { return w.currentIndex(); },
            [](Wt::WStackedWidget& w, int i) { w.setCurrentIndex(i); })
        .def("set_current_widget", &Wt::WStackedWidget::setCurrentWidget,
             "widget"_a);

    // ---- WMenuItem ----

    nb::class_<Wt::WMenuItem, Wt::WContainerWidget>(m, "WMenuItem")
        .def(heap_init<Wt::WMenuItem, const Wt::WString&>(), "label"_a)
        .def(nb::new_(
                [](const Wt::WString& label,
                   std::unique_ptr<Wt::WWidget> contents) {
                    return std::make_unique<Wt::WMenuItem>(
                        label, std::move(contents));
                }), "label"_a, "contents"_a)
        .def_prop_rw("text",
            [](const Wt::WMenuItem& w) { return w.text(); },
            [](Wt::WMenuItem& w, const Wt::WString& t) { w.setText(t); })
        .def("set_link", &Wt::WMenuItem::setLink, "link"_a)
        .def_prop_rw("checkable",
            [](const Wt::WMenuItem& w) { return w.isCheckable(); },
            [](Wt::WMenuItem& w, bool c) { w.setCheckable(c); })
        .def_prop_rw("checked",
            [](const Wt::WMenuItem& w) { return w.isChecked(); },
            [](Wt::WMenuItem& w, bool b) { w.setChecked(b); })
        .def("select", &Wt::WMenuItem::select)
        .def("set_selectable", &Wt::WMenuItem::setSelectable, "selectable"_a)
        .def("set_closeable", &Wt::WMenuItem::setCloseable, "closeable"_a);

    // Signal<WMenuItem*> for WMenu::itemSelected
    nb::class_<Wt::Signal<Wt::WMenuItem*>>(m, "MenuItemSignal")
        .def("connect",
            [](Wt::Signal<Wt::WMenuItem*>& s, nb::callable cb) {
                return py_connect<Wt::Signal<Wt::WMenuItem*>,
                                  Wt::WMenuItem*>(s, std::move(cb));
            }, "callable"_a)
        .def("disconnect_all_slots",
            [](Wt::Signal<Wt::WMenuItem*>& s) {
                connection_registry_disconnect_all(&s);
            });

    // ---- WMenu ----

    // WMenu, WTabWidget, WPanel, WDialog all inherit via WCompositeWidget,
    // which derives directly from WWidget — they skip WInteractWidget. We
    // therefore use WWidget as the Python-visible base.
    nb::class_<Wt::WMenu, Wt::WWidget>(m, "WMenu")
        .def(heap_init<Wt::WMenu>())
        .def(heap_init<Wt::WMenu, Wt::WStackedWidget*>(), "contents_stack"_a)
        // String overload — wraps the label in a fresh WMenuItem.
        // Python-only convenience; Wt has no addItem(WString) on WMenu.
        // Listed BEFORE the widget overload so `menu.add_item("hi")` doesn't
        // route through the `nb::object → unique_ptr` cast that would
        // `std::bad_cast` on a str.
        .def("add_item",
            [](Wt::WMenu& self, const Wt::WString& label) {
                return self.addItem(std::make_unique<Wt::WMenuItem>(label));
            },
            "label"_a, nb::rv_policy::reference_internal)
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
            "item"_a)
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
            "items"_a)
        // Bulk add of labels — each is wrapped in a fresh WMenuItem.
        .def("add_items",
            [](Wt::WMenu& self, const std::vector<Wt::WString>& labels) {
                for (const auto& l : labels) {
                    self.addItem(std::make_unique<Wt::WMenuItem>(l));
                }
            },
            "labels"_a)
        .def("select",
             nb::overload_cast<int>(&Wt::WMenu::select),
             "index"_a)
        .def("current_item", &Wt::WMenu::currentItem,
             nb::rv_policy::reference_internal)
        .def_prop_ro("item_selected", &Wt::WMenu::itemSelected,
                     nb::rv_policy::reference_internal);

    // ---- WTabWidget ----

    nb::class_<Wt::WTabWidget, Wt::WWidget>(m, "WTabWidget")
        .def(heap_init<Wt::WTabWidget>())
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
            nb::rv_policy::reference_internal)
        .def_prop_ro("count", &Wt::WTabWidget::count)
        .def("index_of", &Wt::WTabWidget::indexOf, "widget"_a)
        .def_prop_rw("current_index",
            [](const Wt::WTabWidget& w) { return w.currentIndex(); },
            [](Wt::WTabWidget& w, int i) { w.setCurrentIndex(i); })
        .def("set_tab_enabled", &Wt::WTabWidget::setTabEnabled,
             "index"_a, "enable"_a)
        .def("set_tab_hidden", &Wt::WTabWidget::setTabHidden,
             "index"_a, "hidden"_a)
        .def("set_tab_closeable", &Wt::WTabWidget::setTabCloseable,
             "index"_a, "closeable"_a)
        .def("set_tab_text", &Wt::WTabWidget::setTabText, "index"_a, "label"_a)
        .def("tab_text", &Wt::WTabWidget::tabText, "index"_a)
        .def_prop_ro("current_changed", &Wt::WTabWidget::currentChanged,
                     nb::rv_policy::reference_internal);

    // ---- WPanel / WGroupBox ----

    nb::class_<Wt::WPanel, Wt::WWidget>(m, "WPanel")
        .def(heap_init<Wt::WPanel>())
        .def_prop_rw("title",
            [](const Wt::WPanel& w) { return w.title(); },
            [](Wt::WPanel& w, const Wt::WString& t) { w.setTitle(t); })
        .def("set_title_bar", &Wt::WPanel::setTitleBar, "enable"_a)
        .def_prop_ro("title_bar", &Wt::WPanel::titleBar)
        .def_prop_rw("collapsible",
            [](const Wt::WPanel& w) { return w.isCollapsible(); },
            [](Wt::WPanel& w, bool on) { w.setCollapsible(on); })
        .def_prop_rw("collapsed",
            [](const Wt::WPanel& w) { return w.isCollapsed(); },
            [](Wt::WPanel& w, bool on) { w.setCollapsed(on); })
        .def("collapse", &Wt::WPanel::collapse)
        .def("expand", &Wt::WPanel::expand)
        .def("set_central_widget",
            [](Wt::WPanel& self, nb::object py_widget) {
                auto w = nb::cast<std::unique_ptr<Wt::WWidget>>(py_widget);
                self.setCentralWidget(std::move(w));
                nb::inst_set_state(py_widget, /*ready*/ true,
                                   /*destruct*/ false);
            },
            "widget"_a);

    nb::class_<Wt::WGroupBox, Wt::WContainerWidget>(m, "WGroupBox")
        .def(heap_init<Wt::WGroupBox>())
        .def(heap_init<Wt::WGroupBox, const Wt::WString&>(), "title"_a)
        .def_prop_rw("title",
            [](const Wt::WGroupBox& w) { return w.title(); },
            [](Wt::WGroupBox& w, const Wt::WString& t) { w.setTitle(t); });

    // ---- WDialog + WMessageBox ----
    //
    // WDialog inherits WPopupWidget → WCompositeWidget → WWidget; we present
    // it under WWidget on the Python side.

    nb::class_<Wt::WDialog, Wt::WWidget>(m, "WDialog")
        .def(heap_init<Wt::WDialog>())
        .def(heap_init<Wt::WDialog, const Wt::WString&>(), "window_title"_a)
        .def_prop_rw("window_title",
            [](const Wt::WDialog& w) { return w.windowTitle(); },
            [](Wt::WDialog& w, const Wt::WString& t) { w.setWindowTitle(t); })
        .def_prop_rw("modal",
            [](const Wt::WDialog& w) { return w.isModal(); },
            [](Wt::WDialog& w, bool m) { w.setModal(m); })
        .def_prop_rw("closable",
            [](const Wt::WDialog& w) { return w.closable(); },
            [](Wt::WDialog& w, bool c) { w.setClosable(c); })
        .def("set_resizable", &Wt::WDialog::setResizable, "resizable"_a)
        .def("show", &Wt::WDialog::show)
        .def("accept", &Wt::WDialog::accept)
        .def("reject", &Wt::WDialog::reject)
        .def("done", &Wt::WDialog::done, "result"_a)
        .def("reject_when_escape_pressed",
             &Wt::WDialog::rejectWhenEscapePressed,
             "enable"_a = true)
        // contents / title_bar_widget / footer are behaviorless getters of
        // stable inner containers — expose as read-only attributes.
        .def_prop_ro("contents", &Wt::WDialog::contents,
                     nb::rv_policy::reference_internal)
        .def_prop_ro("title_bar_widget", &Wt::WDialog::titleBar,
                     nb::rv_policy::reference_internal)
        .def_prop_ro("footer", &Wt::WDialog::footer,
                     nb::rv_policy::reference_internal)
        .def_prop_ro("result", &Wt::WDialog::result)
        .def_prop_ro("finished", &Wt::WDialog::finished,
                     nb::rv_policy::reference_internal);

    nb::class_<Wt::WMessageBox, Wt::WDialog>(m, "WMessageBox")
        .def(heap_init<Wt::WMessageBox>())
        .def_prop_rw("text",
            [](const Wt::WMessageBox& w) { return w.text(); },
            [](Wt::WMessageBox& w, const Wt::WString& t) { w.setText(t); })
        .def("set_standard_buttons",
            [](Wt::WMessageBox& m, int flags) {
                m.setStandardButtons(Wt::WFlags<Wt::StandardButton>(
                    static_cast<Wt::StandardButton>(flags)));
            },
            "buttons"_a)
        .def_prop_ro("button_result", &Wt::WMessageBox::buttonResult)
        .def_prop_ro("button_clicked", &Wt::WMessageBox::buttonClicked,
                     nb::rv_policy::reference_internal);
}

}  // namespace witty_for_python
