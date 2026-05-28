#include "common.hpp"

#include <Wt/WBoxLayout.h>
#include <Wt/WGlobal.h>      // Wt::LayoutDirection, Wt::AlignmentFlag
#include <Wt/WGridLayout.h>
#include <Wt/WHBoxLayout.h>
#include <Wt/WLayout.h>
#include <Wt/WLength.h>
#include <Wt/WVBoxLayout.h>
#include <Wt/WWidget.h>

namespace witty_for_python {

void register_layout(nb::module_& m) {
    nb::class_<Wt::WLayout>(m, "WLayout");

    nb::enum_<Wt::LayoutDirection>(m, "LayoutDirection")
        .value("LeftToRight", Wt::LayoutDirection::LeftToRight)
        .value("RightToLeft", Wt::LayoutDirection::RightToLeft)
        .value("TopToBottom", Wt::LayoutDirection::TopToBottom)
        .value("BottomToTop", Wt::LayoutDirection::BottomToTop);

    nb::class_<Wt::WBoxLayout, Wt::WLayout>(m, "WBoxLayout")
        .def(heap_init<Wt::WBoxLayout, Wt::LayoutDirection>(), "direction"_a)
        .def("add_widget",
             [](Wt::WBoxLayout& self, std::unique_ptr<Wt::WWidget> w, int stretch) {
                 self.addWidget(std::move(w), stretch);
             },
             "widget"_a, "stretch"_a = 0)
        // Bulk variant of add_widget. Loops the single form with default
        // stretch=0; per-widget stretch values require the single-call form.
        // Python-only convenience.
        .def("add_widgets",
             [](Wt::WBoxLayout& self,
                std::vector<std::unique_ptr<Wt::WWidget>> widgets) {
                 for (auto& w : widgets) self.addWidget(std::move(w), 0);
             },
             "widgets"_a)
        .def("add_stretch", &Wt::WBoxLayout::addStretch, "stretch"_a = 1)
        .def("add_spacing",
             [](Wt::WBoxLayout& self, double px) { self.addSpacing(Wt::WLength(px)); },
             "size_px"_a);

    nb::class_<Wt::WHBoxLayout, Wt::WBoxLayout>(m, "WHBoxLayout")
        .def(heap_init<Wt::WHBoxLayout>());

    nb::class_<Wt::WVBoxLayout, Wt::WBoxLayout>(m, "WVBoxLayout")
        .def(heap_init<Wt::WVBoxLayout>());

    nb::class_<Wt::WGridLayout, Wt::WLayout>(m, "WGridLayout")
        .def(heap_init<Wt::WGridLayout>())
        .def("add_widget",
             [](Wt::WGridLayout& self, std::unique_ptr<Wt::WWidget> w,
                int row, int column, int row_span, int column_span) {
                 // The 6-arg overload requires an alignment; default to none.
                 self.addWidget(std::move(w), row, column,
                                row_span, column_span,
                                Wt::WFlags<Wt::AlignmentFlag>());
             },
             "widget"_a, "row"_a, "column"_a,
             "row_span"_a = 1, "column_span"_a = 1)
        .def("set_row_stretch", &Wt::WGridLayout::setRowStretch,
             "row"_a, "stretch"_a)
        .def("set_column_stretch", &Wt::WGridLayout::setColumnStretch,
             "column"_a, "stretch"_a)
        .def_prop_ro("row_count", &Wt::WGridLayout::rowCount)
        .def_prop_ro("column_count", &Wt::WGridLayout::columnCount);
}

}  // namespace witty_for_python
