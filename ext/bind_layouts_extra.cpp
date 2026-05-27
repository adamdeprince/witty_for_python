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
        .def(nb::init<>())
        .def("add_widget",
            // Ownership: move in, return raw pointer for chained access
            // (matching the pattern used elsewhere in the binding).
            [](Wt::WBorderLayout& self,
               std::unique_ptr<Wt::WWidget> w,
               Wt::LayoutPosition position) -> Wt::WWidget* {
                Wt::WWidget* raw = w.get();
                self.addWidget(std::move(w), position);
                return raw;
            },
            "widget"_a, "position"_a,
            nb::rv_policy::reference_internal);

    // ---- WFitLayout: single-child layout that fills the parent ----
    //
    // Wraps exactly one widget and makes it fill the entire parent. Useful
    // when you want a single child to behave as if it had `width=100%`
    // and `height=100%` without writing the CSS.

    nb::class_<Wt::WFitLayout, Wt::WLayout>(m, "WFitLayout")
        .def(nb::init<>())
        .def("add_widget",
            [](Wt::WFitLayout& self,
               std::unique_ptr<Wt::WWidget> w) -> Wt::WWidget* {
                Wt::WWidget* raw = w.get();
                self.addWidget(std::move(w));
                return raw;
            },
            "widget"_a,
            nb::rv_policy::reference_internal,
            "Set the single fitted child. Replacing it requires calling "
            "the inherited removeWidget on the previous one first.");
}

}  // namespace witty_for_python
