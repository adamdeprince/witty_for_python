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
    nb::class_<Wt::WLayout>(m, "WLayout",
        "Abstract base of every layout manager. A layout is installed\n"
        "into a WContainerWidget via `container.set_layout(layout)` and\n"
        "from then on decides how the container's children are sized\n"
        "and positioned — the container's own `add_widget` order is\n"
        "ignored. Use the concrete subclasses (WHBoxLayout, WVBoxLayout,\n"
        "WGridLayout, WBorderLayout, WFitLayout) instead of this type.");

    nb::enum_<Wt::LayoutDirection>(m, "LayoutDirection",
        "Direction in which a WBoxLayout places its children — horizontal\n"
        "(LeftToRight / RightToLeft) or vertical (TopToBottom /\n"
        "BottomToTop).")
        .value("LeftToRight", Wt::LayoutDirection::LeftToRight)
        .value("RightToLeft", Wt::LayoutDirection::RightToLeft)
        .value("TopToBottom", Wt::LayoutDirection::TopToBottom)
        .value("BottomToTop", Wt::LayoutDirection::BottomToTop);

    nb::class_<Wt::WBoxLayout, Wt::WLayout>(m, "WBoxLayout",
        "Linear layout — places children in a single row or column\n"
        "depending on its LayoutDirection. The two thin subclasses\n"
        "WHBoxLayout and WVBoxLayout are usually more convenient.\n"
        "\n"
        "Each child has a `stretch` weight that determines how\n"
        "extra space is divided up; stretch 0 means natural size, and\n"
        "higher values get a proportionally larger share.")
        .def(heap_init<Wt::WBoxLayout, Wt::LayoutDirection>(), "direction"_a,
             "Construct a box layout with the given LayoutDirection.")
        // Re-arm pattern: transfer ownership, then mark the wrapper
        // non-owning and return it for fluent chaining. See §4.2.
        .def("add_widget",
             [](Wt::WBoxLayout& self, nb::object py_widget, int stretch)
                 -> nb::object {
                 auto w = nb::cast<std::unique_ptr<Wt::WWidget>>(py_widget);
                 self.addWidget(std::move(w), stretch);
                 nb::inst_set_state(py_widget, /*ready*/ true,
                                    /*destruct*/ false);
                 return py_widget;
             },
             "widget"_a, "stretch"_a = 0,
             "Append `widget` to the layout with the given stretch\n"
             "weight. Takes ownership; the Python wrapper is re-armed as\n"
             "a non-owning alias and returned for fluent chaining:\n"
             "\n"
             "    layout.add_widget(wt.WPushButton('Go')).clicked.connect(go)")
        // Bulk variant of add_widget. Loops the single form with default
        // stretch=0; per-widget stretch values require the single-call form.
        // Python-only convenience.
        .def("add_widgets",
             [](Wt::WBoxLayout& self, nb::list py_widgets) -> nb::list {
                 nb::list out;
                 for (nb::handle h : py_widgets) {
                     nb::object py_w = nb::borrow(h);
                     auto w = nb::cast<std::unique_ptr<Wt::WWidget>>(py_w);
                     self.addWidget(std::move(w), 0);
                     nb::inst_set_state(py_w, /*ready*/ true,
                                        /*destruct*/ false);
                     out.append(py_w);
                 }
                 return out;
             },
             "widgets"_a,
             "Bulk version of `add_widget` with stretch=0 for every\n"
             "child. Use the single-call form if you need per-widget\n"
             "stretch values.")
        .def("add_stretch", &Wt::WBoxLayout::addStretch, "stretch"_a = 1,
             "Insert a flexible spacer with the given stretch weight.\n"
             "Useful for pushing the next widget to one end of the row\n"
             "or column.")
        .def("add_spacing",
             [](Wt::WBoxLayout& self, double px) { self.addSpacing(Wt::WLength(px)); },
             "size_px"_a,
             "Insert a fixed-size gap of `size_px` pixels.");

    nb::class_<Wt::WHBoxLayout, Wt::WBoxLayout>(m, "WHBoxLayout",
        "Horizontal box layout — children are arranged left-to-right.\n"
        "Equivalent to `WBoxLayout(LayoutDirection.LeftToRight)`.\n"
        "\n"
        "    row = wt.WHBoxLayout()\n"
        "    container.set_layout(row)\n"
        "    row.add_widget(wt.WText('Label:'))\n"
        "    row.add_widget(wt.WLineEdit(), 1)")
        .def(heap_init<Wt::WHBoxLayout>(),
             "Construct an empty horizontal box layout.");

    nb::class_<Wt::WVBoxLayout, Wt::WBoxLayout>(m, "WVBoxLayout",
        "Vertical box layout — children are arranged top-to-bottom.\n"
        "Equivalent to `WBoxLayout(LayoutDirection.TopToBottom)`.\n"
        "\n"
        "    col = wt.WVBoxLayout()\n"
        "    container.set_layout(col)\n"
        "    col.add_widget(wt.WText('Header'))\n"
        "    col.add_widget(wt.WText('Body'), 1)")
        .def(heap_init<Wt::WVBoxLayout>(),
             "Construct an empty vertical box layout.");

    nb::class_<Wt::WGridLayout, Wt::WLayout>(m, "WGridLayout",
        "Two-dimensional grid layout — children sit at explicit (row,\n"
        "column) coordinates and can span multiple cells. Rows and\n"
        "columns auto-size from their contents unless given an explicit\n"
        "stretch weight.\n"
        "\n"
        "    grid = wt.WGridLayout()\n"
        "    container.set_layout(grid)\n"
        "    grid.add_widget(wt.WText('Name:'),  0, 0)\n"
        "    grid.add_widget(wt.WLineEdit(),     0, 1)\n"
        "    grid.add_widget(wt.WText('Notes:'), 1, 0)\n"
        "    grid.add_widget(wt.WTextArea(),     1, 1)\n"
        "    grid.set_column_stretch(1, 1)")
        .def(heap_init<Wt::WGridLayout>(),
             "Construct an empty grid layout.")
        .def("add_widget",
             [](Wt::WGridLayout& self, nb::object py_widget,
                int row, int column, int row_span, int column_span)
                 -> nb::object {
                 auto w = nb::cast<std::unique_ptr<Wt::WWidget>>(py_widget);
                 // The 6-arg overload requires an alignment; default to none.
                 self.addWidget(std::move(w), row, column,
                                row_span, column_span,
                                Wt::WFlags<Wt::AlignmentFlag>());
                 nb::inst_set_state(py_widget, /*ready*/ true,
                                    /*destruct*/ false);
                 return py_widget;
             },
             "widget"_a, "row"_a, "column"_a,
             "row_span"_a = 1, "column_span"_a = 1,
             "Place `widget` at the given grid coordinates, optionally\n"
             "spanning several rows or columns. Takes ownership; the\n"
             "Python wrapper is re-armed as a non-owning alias and\n"
             "returned for fluent chaining.")
        .def("set_row_stretch", &Wt::WGridLayout::setRowStretch,
             "row"_a, "stretch"_a,
             "Set the stretch weight for `row`. Rows with positive\n"
             "stretch absorb extra vertical space proportionally.")
        .def("set_column_stretch", &Wt::WGridLayout::setColumnStretch,
             "column"_a, "stretch"_a,
             "Set the stretch weight for `column`. Columns with positive\n"
             "stretch absorb extra horizontal space proportionally.")
        .def_prop_ro("row_count", &Wt::WGridLayout::rowCount,
            "Number of rows the grid currently uses.")
        .def_prop_ro("column_count", &Wt::WGridLayout::columnCount,
            "Number of columns the grid currently uses.");
}

}  // namespace witty_for_python
