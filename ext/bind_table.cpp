#include "common.hpp"

#include <Wt/WTable.h>
#include <Wt/WTableCell.h>
#include <Wt/WTableColumn.h>
#include <Wt/WTableRow.h>

namespace witty_for_python {

void register_table(nb::module_& m) {
    nb::class_<Wt::WTableCell, Wt::WContainerWidget>(m, "WTableCell")
        .def_prop_ro("row", &Wt::WTableCell::row)
        .def_prop_ro("column", &Wt::WTableCell::column)
        .def_prop_rw("row_span",
            [](const Wt::WTableCell& c) { return c.rowSpan(); },
            [](Wt::WTableCell& c, int n) { c.setRowSpan(n); })
        .def_prop_rw("column_span",
            [](const Wt::WTableCell& c) { return c.columnSpan(); },
            [](Wt::WTableCell& c, int n) { c.setColumnSpan(n); });

    nb::class_<Wt::WTableRow>(m, "WTableRow")
        .def_prop_ro("row_num", &Wt::WTableRow::rowNum)
        .def("element_at", &Wt::WTableRow::elementAt,
             "column"_a, nb::rv_policy::reference_internal);

    nb::class_<Wt::WTableColumn>(m, "WTableColumn")
        .def_prop_ro("column_num", &Wt::WTableColumn::columnNum);

    nb::class_<Wt::WTable, Wt::WInteractWidget>(m, "WTable")
        .def(heap_init<Wt::WTable>())
        .def("element_at",
             nb::overload_cast<int, int>(&Wt::WTable::elementAt),
             "row"_a, "column"_a, nb::rv_policy::reference_internal)
        .def_prop_ro("row_count", &Wt::WTable::rowCount)
        .def_prop_ro("column_count", &Wt::WTable::columnCount)
        .def("clear", &Wt::WTable::clear)
        .def("remove_row", &Wt::WTable::removeRow, "row"_a)
        .def("remove_column", &Wt::WTable::removeColumn, "column"_a)
        .def("insert_row",
             [](Wt::WTable& self, int row) -> Wt::WTableRow* {
                 return self.insertRow(row);  // second arg defaults to nullptr
             },
             "row"_a, nb::rv_policy::reference_internal)
        .def("insert_column",
             [](Wt::WTable& self, int column) -> Wt::WTableColumn* {
                 return self.insertColumn(column);
             },
             "column"_a, nb::rv_policy::reference_internal);
}

}  // namespace witty_for_python
