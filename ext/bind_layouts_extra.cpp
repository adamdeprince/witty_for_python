#include "common.hpp"

#include <Wt/WBorderLayout.h>
#include <Wt/WFitLayout.h>
#include <Wt/WGlobal.h>           // LayoutPosition
#include <Wt/WLayout.h>

#include <memory>

namespace witty_for_python {

void register_layouts_extra(nb::module_& m) {
    // ---- LayoutPosition enum ----
    //
    // Used by WBorderLayout to place widgets into one of five regions:
    // North/South/East/West/Center.

    nb::enum_<Wt::LayoutPosition>(m, "LayoutPosition")
        .value("North",  Wt::LayoutPosition::North)
        .value("East",   Wt::LayoutPosition::East)
        .value("South",  Wt::LayoutPosition::South)
        .value("West",   Wt::LayoutPosition::West)
        .value("Center", Wt::LayoutPosition::Center);

    // ---- WBorderLayout: five-region container layout ----
    //
    // Classic "BorderLayout" — North/South stretch horizontally at top and
    // bottom, West/East stretch vertically on the sides, Center fills the
    // remaining middle area. Place a widget into each region via
    // add_widget(widget, position); unspecified regions collapse to zero.

    nb::class_<Wt::WBorderLayout, Wt::WLayout>(m, "WBorderLayout")
        .def(heap_init<Wt::WBorderLayout>())
        .def("add_widget",
            [](Wt::WBorderLayout& self, nb::object py_widget,
               Wt::LayoutPosition position) -> nb::object {
                auto w = nb::cast<std::unique_ptr<Wt::WWidget>>(py_widget);
                self.addWidget(std::move(w), position);
                nb::inst_set_state(py_widget, /*ready*/ true,
                                   /*destruct*/ false);
                return py_widget;
            },
            "widget"_a, "position"_a);

    // ---- WFitLayout: single-child layout that fills the parent ----
    //
    // Wraps exactly one widget and makes it fill the entire parent. Useful
    // when you want a single child to behave as if it had `width=100%`
    // and `height=100%` without writing the CSS.

    nb::class_<Wt::WFitLayout, Wt::WLayout>(m, "WFitLayout")
        .def(heap_init<Wt::WFitLayout>())
        .def("add_widget",
            [](Wt::WFitLayout& self, nb::object py_widget) -> nb::object {
                auto w = nb::cast<std::unique_ptr<Wt::WWidget>>(py_widget);
                self.addWidget(std::move(w));
                nb::inst_set_state(py_widget, /*ready*/ true,
                                   /*destruct*/ false);
                return py_widget;
            },
            "widget"_a,
            "Set the single fitted child. Replacing it requires calling "
            "the inherited removeWidget on the previous one first.");
}

}  // namespace witty_for_python
