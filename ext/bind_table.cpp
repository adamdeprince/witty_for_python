#include "common.hpp"

#include <Wt/WTable.h>
#include <Wt/WTableCell.h>
#include <Wt/WTableColumn.h>
#include <Wt/WTableRow.h>

namespace witty_for_python {

void register_table(nb::module_& m) {
    nb::class_<Wt::WTableCell, Wt::WContainerWidget>(m, "WTableCell",
        "One cell of a WTable, addressed by (row, column). Inherits\n"
        "WContainerWidget — fill it with any widgets you like, the same\n"
        "way you'd populate any other container.\n"
        "\n"
        "    cell = table.element_at(0, 0)\n"
        "    cell.add_widget(wt.WText('Name'))\n"
        "\n"
        "Spans cover adjacent cells: setting `row_span = 2` makes the\n"
        "cell occupy two rows starting at this position.")
        .def_prop_ro("row", &Wt::WTableCell::row,
            "0-based row index of this cell within its WTable.")
        .def_prop_ro("column", &Wt::WTableCell::column,
            "0-based column index of this cell within its WTable.")
        .def_prop_rw("row_span",
            [](const Wt::WTableCell& c) { return c.rowSpan(); },
            [](Wt::WTableCell& c, int n) { c.setRowSpan(n); },
            "Number of rows the cell occupies (HTML `rowspan`). Default 1.")
        .def_prop_rw("column_span",
            [](const Wt::WTableCell& c) { return c.columnSpan(); },
            [](Wt::WTableCell& c, int n) { c.setColumnSpan(n); },
            "Number of columns the cell occupies (HTML `colspan`).\n"
            "Default 1.");

    nb::class_<Wt::WTableRow>(m, "WTableRow",
        "Handle to a row of a WTable. Obtained from `WTable.insert_row`;\n"
        "lets you reach the row's cells without going through the parent\n"
        "table.")
        .def_prop_ro("row_num", &Wt::WTableRow::rowNum,
            "0-based index of this row within its WTable.")
        .def("element_at", &Wt::WTableRow::elementAt,
             "column"_a, nb::rv_policy::reference_internal,
             "Return the WTableCell at `column` in this row. Same cell\n"
             "you'd get from `table.element_at(self.row_num, column)`.");

    nb::class_<Wt::WTableColumn>(m, "WTableColumn",
        "Handle to a column of a WTable. Obtained from\n"
        "`WTable.insert_column` — chiefly useful for setting column-wide\n"
        "styling or width.")
        .def_prop_ro("column_num", &Wt::WTableColumn::columnNum,
            "0-based index of this column within its WTable.");

    nb::class_<Wt::WTable, Wt::WInteractWidget>(m, "WTable",
        "A plain HTML `<table>` widget. Cells grow on demand: ask for\n"
        "`element_at(r, c)` and any missing rows/columns are auto-created.\n"
        "\n"
        "    table = container.add_widget(wt.WTable())\n"
        "    table.element_at(0, 0).add_widget(wt.WText('Header'))\n"
        "    table.element_at(1, 0).add_widget(wt.WText('Row 1'))\n"
        "\n"
        "Use a WTableView with a model when the data is dynamic or large\n"
        "enough that auto-growing cells would be wasteful. WTable is the\n"
        "right pick for hand-laid-out small tables.")
        .def(heap_init<Wt::WTable>(),
             "Construct an empty 0-by-0 table.")
        .def("element_at",
             nb::overload_cast<int, int>(&Wt::WTable::elementAt),
             "row"_a, "column"_a, nb::rv_policy::reference_internal,
             "Return the WTableCell at (row, column), creating empty\n"
             "rows/columns up to that position if they do not exist yet.\n"
             "Then populate it like any other container:\n"
             "\n"
             "    table.element_at(2, 3).add_widget(wt.WText('cell'))")
        .def_prop_ro("row_count", &Wt::WTable::rowCount,
            "Total number of rows currently in the table.")
        .def_prop_ro("column_count", &Wt::WTable::columnCount,
            "Total number of columns currently in the table.")
        .def("clear", &Wt::WTable::clear,
            "Remove every row and column. After this, `row_count` and\n"
            "`column_count` are both 0 and previously-returned cell\n"
            "references are dangling.")
        .def("remove_row", &Wt::WTable::removeRow, "row"_a,
            "Remove the row at the given index. Subsequent rows shift up\n"
            "by one; any cached WTableCell pointers for the removed row\n"
            "become invalid.")
        .def("remove_column", &Wt::WTable::removeColumn, "column"_a,
            "Remove the column at the given index. Subsequent columns\n"
            "shift left by one.")
        .def("insert_row",
             [](Wt::WTable& self, int row) -> Wt::WTableRow* {
                 return self.insertRow(row);  // second arg defaults to nullptr
             },
             "row"_a, nb::rv_policy::reference_internal,
             "Insert a fresh empty row at index `row` (existing rows\n"
             "shift down). Returns the WTableRow handle for the new row.")
        .def("insert_column",
             [](Wt::WTable& self, int column) -> Wt::WTableColumn* {
                 return self.insertColumn(column);
             },
             "column"_a, nb::rv_policy::reference_internal,
             "Insert a fresh empty column at index `column` (existing\n"
             "columns shift right). Returns the WTableColumn handle.");
}

}  // namespace witty_for_python
