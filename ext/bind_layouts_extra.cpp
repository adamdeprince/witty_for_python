#include "common.hpp"

#include <Wt/WBorderLayout.h>
#include <Wt/WFitLayout.h>
#include <Wt/WGlobal.h>           // LayoutPosition
#include <Wt/WLayout.h>

#include <memory>

namespace witty_for_python {

void register_layouts_extra(nb::module_& m) {
    // ---- LayoutPosition enum ----

    nb::enum_<Wt::LayoutPosition>(m, "LayoutPosition",
        "Slot identifier for WBorderLayout's five regions. North and\n"
        "South stretch across the top and bottom; West and East stretch\n"
        "down the sides; Center fills whatever is left in the middle.")
        .value("North",  Wt::LayoutPosition::North)
        .value("East",   Wt::LayoutPosition::East)
        .value("South",  Wt::LayoutPosition::South)
        .value("West",   Wt::LayoutPosition::West)
        .value("Center", Wt::LayoutPosition::Center);

    // ---- WBorderLayout: five-region container layout ----

    nb::class_<Wt::WBorderLayout, Wt::WLayout>(m, "WBorderLayout",
        "Classic BorderLayout — up to five children, one per region\n"
        "(North, South, East, West, Center). North and South stretch\n"
        "across the top and bottom; West and East stretch vertically on\n"
        "the sides; Center fills the remaining space. Regions left empty\n"
        "collapse to zero.\n"
        "\n"
        "    layout = wt.WBorderLayout()\n"
        "    container.set_layout(layout)\n"
        "    layout.add_widget(wt.WText('Header'), wt.LayoutPosition.North)\n"
        "    layout.add_widget(wt.WText('Body'),   wt.LayoutPosition.Center)\n"
        "    layout.add_widget(wt.WText('Footer'), wt.LayoutPosition.South)")
        .def(heap_init<Wt::WBorderLayout>(),
             "Construct an empty border layout.")
        .def("add_widget",
            [](Wt::WBorderLayout& self, nb::object py_widget,
               Wt::LayoutPosition position) -> nb::object {
                auto w = nb::cast<std::unique_ptr<Wt::WWidget>>(py_widget);
                self.addWidget(std::move(w), position);
                nb::inst_set_state(py_widget, /*ready*/ true,
                                   /*destruct*/ false);
                return py_widget;
            },
            "widget"_a, "position"_a,
            "Place `widget` into the named region. Takes ownership; the\n"
            "Python wrapper is re-armed as a non-owning alias and\n"
            "returned for fluent chaining. Only one widget per region —\n"
            "calling add_widget with a position that's already taken\n"
            "replaces the current occupant.");

    // ---- WFitLayout: single-child layout that fills the parent ----

    nb::class_<Wt::WFitLayout, Wt::WLayout>(m, "WFitLayout",
        "Single-child layout — the one widget you add expands to fill\n"
        "the entire parent container. Equivalent to setting the child's\n"
        "CSS to `width: 100%; height: 100%` without writing the CSS.\n"
        "\n"
        "    fit = wt.WFitLayout()\n"
        "    container.set_layout(fit)\n"
        "    fit.add_widget(wt.WTextArea())")
        .def(heap_init<Wt::WFitLayout>(),
             "Construct an empty fit layout.")
        .def("add_widget",
            [](Wt::WFitLayout& self, nb::object py_widget) -> nb::object {
                auto w = nb::cast<std::unique_ptr<Wt::WWidget>>(py_widget);
                self.addWidget(std::move(w));
                nb::inst_set_state(py_widget, /*ready*/ true,
                                   /*destruct*/ false);
                return py_widget;
            },
            "widget"_a,
            "Install `widget` as the single fitted child. Takes\n"
            "ownership; the Python wrapper is re-armed as a non-owning\n"
            "alias and returned for fluent chaining. Replacing the child\n"
            "requires calling the inherited removeWidget on the previous\n"
            "one first.");
}

}  // namespace witty_for_python
