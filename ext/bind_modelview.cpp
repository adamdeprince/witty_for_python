#include "common.hpp"
#include "signal_helpers.hpp"

#include <Wt/WAbstractItemModel.h>
#include <Wt/WAbstractItemView.h>
#include <Wt/WAbstractListModel.h>
#include <Wt/WAny.h>            // cpp17::any + asString
#include <Wt/WEvent.h>
#include <Wt/WGlobal.h>         // SelectionBehavior, SortOrder
#include <Wt/WLength.h>
#include <Wt/WLink.h>          // WStandardItem::setLink
#include <Wt/WModelIndex.h>
#include <Wt/WSignal.h>
#include <Wt/WStandardItem.h>
#include <Wt/WStandardItemModel.h>
#include <Wt/WStringListModel.h>
#include <Wt/WTableView.h>
#include <Wt/WTreeView.h>

#include <Wt/cpp17/any.hpp>

#include <memory>
#include <string>
#include <vector>

namespace witty_for_python {

namespace {

// Convert a Python value (str / int / float / bool) to a Wt::cpp17::any.
// The model classes' data/setData/header methods are cpp17::any-typed; for
// the common cases we cover str (→ WString — the value used by ItemDataRole.
// Display) and the simple numeric scalars. Falls back to WString-via-repr
// for unknown types, which is good enough for header labels & display data
// in v1.
Wt::cpp17::any python_to_any(nb::handle value) {
    if (value.is_none()) return Wt::cpp17::any{};
    PyObject* p = value.ptr();
    if (PyUnicode_Check(p)) {
        return Wt::cpp17::any(nb::cast<Wt::WString>(value));
    }
    if (PyBool_Check(p)) {
        return Wt::cpp17::any(nb::cast<bool>(value));
    }
    if (PyLong_Check(p)) {
        return Wt::cpp17::any(nb::cast<long long>(value));
    }
    if (PyFloat_Check(p)) {
        return Wt::cpp17::any(nb::cast<double>(value));
    }
    // Fallback: stringify via Python repr — at least the display role
    // shows something sensible rather than an empty cell.
    return Wt::cpp17::any(Wt::WString(nb::cast<std::string>(nb::str(value))));
}

// Convert a Wt::cpp17::any back to a Python value. For Display data we
// stringify via Wt::asString(); other types come through as Python str
// (the common case for WTableView rendering). Empty any → None.
nb::object any_to_python(const Wt::cpp17::any& v) {
    if (!v.has_value()) return nb::none();
    return nb::cast(Wt::asString(v).toUTF8());
}

}  // namespace

void register_modelview(nb::module_& m) {
    // ---- ItemDataRole ----

    auto role_cls = nb::class_<Wt::ItemDataRole>(m, "ItemDataRole",
        "Identifies which facet of a cell a view is asking for. Models\n"
        "store more than just the displayed text per cell — they can\n"
        "also hold edit values, decorations (icons), tooltips, style\n"
        "classes, hyperlinks, checkbox state, and so on. Each is a\n"
        "different ItemDataRole.\n"
        "\n"
        "    text = model.display_data(model.index(0, 0))\n"
        "    role = wt.ItemDataRole(wt.ItemDataRole.Display)\n"
        "\n"
        "The standard roles are exposed as plain int class attributes\n"
        "(Display, Edit, Decoration, ToolTip, StyleClass, Checked, Link,\n"
        "…). Wrap one in ItemDataRole(role) when you need the typed\n"
        "value to pass into a Wt API.")
        .def(nb::init<int>(), "role"_a,
             "Construct a role from its integer value. Use the class\n"
             "attribute constants (`ItemDataRole.Display`, etc.) rather\n"
             "than raw numbers.")
        .def_prop_ro("value", &Wt::ItemDataRole::value,
             "The underlying integer role identifier.")
        .def("__eq__",
            [](const Wt::ItemDataRole& a, const Wt::ItemDataRole& b) {
                return a == b;
            }, nb::is_operator())
        .def("__lt__",
            [](const Wt::ItemDataRole& a, const Wt::ItemDataRole& b) {
                return a < b;
            }, nb::is_operator())
        .def("__hash__",
            [](const Wt::ItemDataRole& r) { return r.value(); })
        .def("__repr__",
            [](const Wt::ItemDataRole& r) {
                return "ItemDataRole(" + std::to_string(r.value()) + ")";
            });

    // Static role constants — exposed as plain Python ints, matching Wt's
    // own representation. The `#if !WT_TARGET_JAVA` branch in Wt's header
    // declares these as `static constexpr const int Display = 0` etc., so
    // `Wt::ItemDataRole::Display` IS the integer 0; we just pass that
    // through. Callers wanting a typed value wrap explicitly:
    //
    //   wt.ItemDataRole(wt.ItemDataRole.Display)
    //
    // Storing them as int (rather than nb::cast'd ItemDataRole instances)
    // avoids holding extra value-typed objects alive past interpreter
    // shutdown — keeps the leak-detector quiet for the clean-exit path
    // that the gallery boot test asserts. The numbers stay authoritative
    // by going through Wt's symbolic names, not hardcoded literals.
    role_cls.attr("Display")           = int(Wt::ItemDataRole::Display);
    role_cls.attr("Decoration")        = int(Wt::ItemDataRole::Decoration);
    role_cls.attr("Edit")              = int(Wt::ItemDataRole::Edit);
    role_cls.attr("StyleClass")        = int(Wt::ItemDataRole::StyleClass);
    role_cls.attr("Checked")           = int(Wt::ItemDataRole::Checked);
    role_cls.attr("ToolTip")           = int(Wt::ItemDataRole::ToolTip);
    role_cls.attr("Link")              = int(Wt::ItemDataRole::Link);
    role_cls.attr("MimeType")          = int(Wt::ItemDataRole::MimeType);
    role_cls.attr("Level")             = int(Wt::ItemDataRole::Level);
    role_cls.attr("MarkerPenColor")    = int(Wt::ItemDataRole::MarkerPenColor);
    role_cls.attr("MarkerBrushColor")  = int(Wt::ItemDataRole::MarkerBrushColor);
    role_cls.attr("MarkerScaleFactor") = int(Wt::ItemDataRole::MarkerScaleFactor);
    role_cls.attr("MarkerType")        = int(Wt::ItemDataRole::MarkerType);
    role_cls.attr("BarPenColor")       = int(Wt::ItemDataRole::BarPenColor);
    role_cls.attr("BarBrushColor")     = int(Wt::ItemDataRole::BarBrushColor);
    role_cls.attr("User")              = int(Wt::ItemDataRole::User);

    // ---- WModelIndex ----

    nb::class_<Wt::WModelIndex>(m, "WModelIndex",
        "Lightweight value handle to a single cell of a model, identified\n"
        "by (row, column, parent). Returned by model methods like\n"
        "`index(row, col)` and used as input wherever a view or proxy\n"
        "needs to refer to a cell.\n"
        "\n"
        "    idx = model.index(2, 0)\n"
        "    text = model.display_data(idx)\n"
        "\n"
        "The default-constructed (and the one returned by `parent()` on\n"
        "a top-level row) is the sentinel 'invalid' index — check\n"
        "`is_valid` before using it. Comparable and hashable, so it works\n"
        "as a dict key or set member.")
        .def(nb::init<>(),
             "Construct the invalid sentinel index — the same value used\n"
             "to mean 'no parent / top level' wherever a parent index is\n"
             "expected.")
        .def_prop_ro("row", &Wt::WModelIndex::row,
            "0-based row of the cell this index addresses.")
        .def_prop_ro("column", &Wt::WModelIndex::column,
            "0-based column of the cell this index addresses.")
        .def_prop_ro("is_valid", &Wt::WModelIndex::isValid,
            "False for the root / sentinel index returned by parent() on "
            "a top-level item.")
        .def_prop_ro("internal_id", &Wt::WModelIndex::internalId,
            "Model-defined opaque id distinguishing tree nodes that share "
            "(row, column). Stable for the lifetime of the model item.")
        .def("parent", &Wt::WModelIndex::parent,
            "Index of this cell's parent — invalid for top-level rows.")
        .def("child", &Wt::WModelIndex::child, "row"_a, "column"_a,
            "Child cell at (row, column) of this index. For non-tree "
            "models, only the top-level index has children.")
        .def("__eq__",
            [](const Wt::WModelIndex& a, const Wt::WModelIndex& b) {
                return a == b;
            }, nb::is_operator())
        .def("__lt__",
            [](const Wt::WModelIndex& a, const Wt::WModelIndex& b) {
                return a < b;
            }, nb::is_operator())
        .def("__hash__",
            [](const Wt::WModelIndex& i) {
                // Mix row, column, internal id — same fields Wt's own
                // Hash struct uses.
                std::size_t h = std::hash<int>()(i.row());
                h ^= std::hash<int>()(i.column()) + 0x9e3779b9 + (h << 6) + (h >> 2);
                h ^= std::hash<std::uint64_t>()(i.internalId())
                       + 0x9e3779b9 + (h << 6) + (h >> 2);
                return h;
            })
        .def("__repr__",
            [](const Wt::WModelIndex& i) {
                if (!i.isValid()) return std::string("WModelIndex(invalid)");
                return "WModelIndex(row=" + std::to_string(i.row())
                     + ", column=" + std::to_string(i.column()) + ")";
            });

    // ---- ModelIndexMouseSignal (Signal<WModelIndex, WMouseEvent>) ----
    //
    // Used by WAbstractItemView.clicked / doubleClicked. Bound here (not in
    // bind_signals.cpp) because WModelIndex must be a registered class
    // before nanobind can cast the payload.

    nb::class_<Wt::Signal<Wt::WModelIndex, Wt::WMouseEvent>>(
        m, "ModelIndexMouseSignal",
        "Two-argument signal fired by item views on click / double-click,\n"
        "carrying the WModelIndex of the affected cell and the underlying\n"
        "WMouseEvent (buttons, modifiers, coordinates).\n"
        "\n"
        "    def on_click(index, event):\n"
        "        if index.is_valid:\n"
        "            print('clicked row', index.row)\n"
        "    table_view.clicked.connect(on_click)")
        .def("connect",
            [](Wt::Signal<Wt::WModelIndex, Wt::WMouseEvent>& s,
               nb::callable cb) {
                return py_connect<
                    Wt::Signal<Wt::WModelIndex, Wt::WMouseEvent>,
                    Wt::WModelIndex, Wt::WMouseEvent>(s, std::move(cb));
            }, "callable"_a,
            "Subscribe `callable` to the signal. The callback receives\n"
            "(WModelIndex, WMouseEvent). Returns a Connection — call\n"
            "`.disconnect()` on it to unsubscribe.")
        .def("disconnect_all_slots",
            [](Wt::Signal<Wt::WModelIndex, Wt::WMouseEvent>& s) {
                connection_registry_disconnect_all(&s);
            },
            "Drop every Python subscriber from this signal.");

    // ---- WAbstractItemModel (abstract base) ----
    //
    // Bound non-constructible. Concrete subclasses (WStandardItemModel,
    // WStringListModel) are what Python users instantiate. The interface
    // exposes the read-side surface most consumers need; cpp17::any-typed
    // data() and setData() are NOT bound (write goes through WStandardItem;
    // read goes through `display_data` below, which calls Wt::asString
    // internally).

    nb::class_<Wt::WAbstractItemModel, Wt::WObject>(m, "WAbstractItemModel",
        "Abstract base for everything an item view can render. Models\n"
        "expose data as a tree of cells addressed by (row, column,\n"
        "parent); flat tables are the special case where no row has\n"
        "children. Views (WTableView, WTreeView, …) attach via\n"
        "`view.model = some_model` and pull cells through `display_data`\n"
        "and the role-typed accessors.\n"
        "\n"
        "Not directly constructible from Python — instantiate a concrete\n"
        "subclass (WStandardItemModel, WStringListModel) or wrap one in a\n"
        "proxy. Writes typically go through the concrete subclass\n"
        "(e.g. WStandardItem mutators); this base only exposes the read\n"
        "surface and header mutation.")
        .def("row_count",
            [](const Wt::WAbstractItemModel& self,
               const Wt::WModelIndex& parent) {
                return self.rowCount(parent);
            },
            "parent"_a = Wt::WModelIndex(),
            "Number of rows under `parent` (top-level when parent is the "
            "default invalid index).")
        .def("column_count",
            [](const Wt::WAbstractItemModel& self,
               const Wt::WModelIndex& parent) {
                return self.columnCount(parent);
            },
            "parent"_a = Wt::WModelIndex(),
            "Number of columns under `parent` (top-level when parent is\n"
            "the default invalid index). For a flat table this is the\n"
            "number of columns of the table itself.")
        .def("has_children",
            &Wt::WAbstractItemModel::hasChildren, "index"_a,
            "True if `index` has any children — i.e. it expands into a\n"
            "subtree. Always False for flat list/table models.")
        .def("index",
            [](const Wt::WAbstractItemModel& self, int row, int col,
               const Wt::WModelIndex& parent) {
                return self.index(row, col, parent);
            },
            "row"_a, "column"_a, "parent"_a = Wt::WModelIndex(),
            "Build a WModelIndex addressing the cell at (row, column)\n"
            "under `parent` (top-level when parent is the default invalid\n"
            "index). Returns an invalid index if the coordinates are out\n"
            "of range.")
        .def("parent_of",
            // Renamed: `parent` collides with Python keyword usage on
            // ItemDataRole's other signatures and is awkward as a method
            // name. Callers can also reach this via WModelIndex.parent().
            [](const Wt::WAbstractItemModel& self,
               const Wt::WModelIndex& index) {
                return self.parent(index);
            },
            "index"_a,
            "Parent index of `index`. Invalid for top-level rows. Same\n"
            "value as `index.parent()`; provided as a method on the model\n"
            "to mirror the C++ API (renamed `parent_of` to avoid colliding\n"
            "with Python's `parent` convention elsewhere).")
        .def("display_data",
            // Convenience: fetch the Display-role value as a string.
            // Sidesteps the cpp17::any binding for the common case of
            // reading text shown in a WTableView column.
            [](const Wt::WAbstractItemModel& self,
               const Wt::WModelIndex& index) {
                return any_to_python(self.data(index, Wt::ItemDataRole::Display));
            },
            "index"_a,
            "The cell's Display-role data stringified — the text a view\n"
            "would render for it. Returns None for empty cells. Avoids\n"
            "having to deal with the cpp17::any-typed `data()` accessor\n"
            "for the common 'just show me what's in the cell' case.")
        .def("set_header_data",
            [](Wt::WAbstractItemModel& self, int section, nb::handle value) {
                return self.setHeaderData(section, python_to_any(value));
            },
            "section"_a, "value"_a,
            "Set a header label. Accepts str/int/float/bool — anything else "
            "is stringified via Python repr.");

    // WAbstractListModel and WAbstractTableModel are intermediate bases.
    // We bind WAbstractListModel because WStringListModel inherits it; the
    // table base is internal so far.
    nb::class_<Wt::WAbstractListModel, Wt::WAbstractItemModel>(
        m, "WAbstractListModel",
        "Intermediate base for single-column list-shaped models — flat,\n"
        "no children. Mostly bound so WStringListModel can declare it as\n"
        "its base; users typically interact with the concrete subclass.");

    // ---- WStringListModel: a flat list of strings ----

    nb::class_<Wt::WStringListModel, Wt::WAbstractListModel>(m, "WStringListModel",
        "Single-column model whose cells hold strings. Pair with a\n"
        "WTableView or feed it to a combo-box-style widget; the simplest\n"
        "way to back a UI list with Python data.\n"
        "\n"
        "    model = wt.WStringListModel(['apples', 'pears', 'plums'])\n"
        "    view = container.add_widget(wt.WTableView())\n"
        "    view.model = model\n"
        "    model.add_string('quinces')")
        .def(heap_init<Wt::WStringListModel>(),
             "Construct an empty string-list model.")
        .def(heap_init<Wt::WStringListModel,
                       const std::vector<Wt::WString>&>(), "strings"_a,
             "Construct a model populated with `strings` (one row each,\n"
             "in order).")
        .def("set_string_list", &Wt::WStringListModel::setStringList,
             "strings"_a,
             "Replace every row with `strings`. Attached views are\n"
             "notified and redraw.")
        .def("add_string", &Wt::WStringListModel::addString, "string"_a,
             "Append a single string as a new row at the end.")
        .def_prop_ro("string_list",
            [](const Wt::WStringListModel& self) {
                return self.stringList();
            },
            "The current list of strings as a Python list of WString.");

    // ---- WStandardItem ----

    nb::class_<Wt::WStandardItem>(m, "WStandardItem",
        "Mutable cell value used by WStandardItemModel. Each cell of a\n"
        "table — or each node of a tree — is one WStandardItem holding\n"
        "the display text, optional decoration/styling/tooltip, link,\n"
        "checkbox state, and any child rows/columns for tree mode.\n"
        "\n"
        "    item = wt.WStandardItem('Alice')\n"
        "    item.tool_tip = 'Project lead'\n"
        "    model.set_item(0, 0, item)\n"
        "    # mutate in place — the attached view sees the update:\n"
        "    item.text = 'Alice (PL)'\n"
        "\n"
        "Items own their children: `set_child` / `append_row` /\n"
        "`set_item` transfer the Python wrapper into Wt's tree (the\n"
        "wrapper is re-armed as a non-owning alias, so the same Python\n"
        "object keeps working but won't double-free).")
        .def(heap_init<Wt::WStandardItem>(),
             "Construct an empty item with no text.")
        .def(heap_init<Wt::WStandardItem, const Wt::WString&>(), "text"_a,
             "Construct an item displaying `text`.")
        .def_prop_rw("text",
            [](const Wt::WStandardItem& self) { return self.text(); },
            [](Wt::WStandardItem& self, const Wt::WString& t) { self.setText(t); },
            "The cell's displayed text (the Display-role value).\n"
            "Assigning updates attached views on the next round-trip.")
        .def_prop_rw("icon",
            [](const Wt::WStandardItem& self) { return self.icon(); },
            [](Wt::WStandardItem& self, const std::string& uri) {
                self.setIcon(uri);
            },
            "URL of a small icon shown beside the text (when the view's "
            "delegate honours ItemDataRole.Decoration).")
        .def_prop_rw("style_class",
            [](const Wt::WStandardItem& self) { return self.styleClass(); },
            [](Wt::WStandardItem& self, const Wt::WString& s) {
                self.setStyleClass(s);
            },
            "CSS class applied to this cell's rendered element. Useful\n"
            "for per-row colouring or highlighting.")
        .def_prop_rw("tool_tip",
            [](const Wt::WStandardItem& self) { return self.toolTip(); },
            [](Wt::WStandardItem& self, const Wt::WString& t) {
                self.setToolTip(t);
            },
            "Hover-tooltip text for this cell.")
        .def("set_link", &Wt::WStandardItem::setLink, "link"_a,
             "Attach a WLink to the cell, so the rendered text becomes\n"
             "clickable and navigates to the link's URL or internal path.")
        .def_prop_rw("checkable",
            &Wt::WStandardItem::isCheckable, &Wt::WStandardItem::setCheckable,
            "Whether the cell renders with a checkbox. Set True to show\n"
            "one; `checked` then controls its state.")
        .def_prop_rw("checked",
            &Wt::WStandardItem::isChecked, &Wt::WStandardItem::setChecked,
            "Checkbox state. Only meaningful when `checkable` is True.")
        .def_prop_rw("tristate",
            &Wt::WStandardItem::isTristate, &Wt::WStandardItem::setTristate,
            "Whether the checkbox can hold an indeterminate state in\n"
            "addition to checked/unchecked.")
        .def_prop_rw("editable",
            &Wt::WStandardItem::isEditable, &Wt::WStandardItem::setEditable,
            "Whether the user can edit the cell in place via the view's\n"
            "edit delegate.")
        .def_prop_ro("has_children", &Wt::WStandardItem::hasChildren,
            "True if this item has any child rows/columns (i.e. forms a\n"
            "subtree).")
        .def_prop_ro("row_count", &Wt::WStandardItem::rowCount,
            "Number of child rows under this item.")
        .def_prop_ro("column_count", &Wt::WStandardItem::columnCount,
            "Number of child columns under this item.")
        .def("set_row_count", &Wt::WStandardItem::setRowCount, "rows"_a,
             "Resize the children to have exactly `rows` rows. New rows\n"
             "are filled with empty items; excess rows are dropped.")
        .def("set_column_count", &Wt::WStandardItem::setColumnCount,
             "columns"_a,
             "Resize the children to have exactly `columns` columns. New\n"
             "columns are filled with empty items; excess are dropped.")
        .def("append_row",
            [](Wt::WStandardItem& self, nb::list py_items) {
                std::vector<std::unique_ptr<Wt::WStandardItem>> items;
                items.reserve(nb::len(py_items));
                for (nb::handle h : py_items) {
                    nb::object py_it = nb::borrow(h);
                    items.push_back(
                        nb::cast<std::unique_ptr<Wt::WStandardItem>>(py_it));
                    nb::inst_set_state(py_it, /*ready*/ true,
                                       /*destruct*/ false);
                }
                self.appendRow(std::move(items));
            },
            "items"_a,
            "Append a single child row. Each item's Python wrapper stays "
            "usable after the call (re-armed as a non-owning alias).")
        .def("append_column",
            [](Wt::WStandardItem& self, nb::list py_items) {
                std::vector<std::unique_ptr<Wt::WStandardItem>> items;
                items.reserve(nb::len(py_items));
                for (nb::handle h : py_items) {
                    nb::object py_it = nb::borrow(h);
                    items.push_back(
                        nb::cast<std::unique_ptr<Wt::WStandardItem>>(py_it));
                    nb::inst_set_state(py_it, /*ready*/ true,
                                       /*destruct*/ false);
                }
                self.appendColumn(std::move(items));
            },
            "items"_a,
            "Append a single child column. Each item's Python wrapper\n"
            "stays usable after the call (re-armed as a non-owning alias).")
        // insertRows / insertColumns are overloaded (count form +
        // unique_ptr-vector form). We bind only the count form here; the
        // vector form is redundant with append_row.
        .def("insert_rows",
            nb::overload_cast<int, int>(&Wt::WStandardItem::insertRows),
            "row"_a, "count"_a,
            "Insert `count` empty rows starting at `row`. Existing rows\n"
            "at or after that position shift down.")
        .def("insert_columns",
            nb::overload_cast<int, int>(&Wt::WStandardItem::insertColumns),
            "column"_a, "count"_a,
            "Insert `count` empty columns starting at `column`. Existing\n"
            "columns at or after that position shift right.")
        .def("child",
            [](Wt::WStandardItem& self, int row, int col) {
                return self.child(row, col);
            },
            "row"_a, "column"_a = 0,
            nb::rv_policy::reference_internal,
            "The child item at (row, column) — None if absent.")
        .def("parent",
            &Wt::WStandardItem::parent,
            nb::rv_policy::reference_internal,
            "Parent item — None for items in invisibleRootItem().");

    // ---- WStandardItemModel ----

    nb::class_<Wt::WStandardItemModel, Wt::WAbstractItemModel>(
        m, "WStandardItemModel",
        "General-purpose model backed by a grid (or tree) of\n"
        "WStandardItem cells. The standard pick when you want to populate\n"
        "a WTableView or WTreeView from Python data without writing your\n"
        "own model subclass.\n"
        "\n"
        "    model = wt.WStandardItemModel(0, 2)\n"
        "    model.set_header_data(0, 'Name')\n"
        "    model.set_header_data(1, 'Score')\n"
        "    model.append_row([wt.WStandardItem('Alice'),\n"
        "                      wt.WStandardItem('42')])\n"
        "    view = container.add_widget(wt.WTableView())\n"
        "    view.model = model\n"
        "\n"
        "Mutate cells in place by reaching `model.item(row, col)` and\n"
        "assigning to its `text`, `checked`, etc. — attached views see\n"
        "the change on the next round-trip.")
        .def(heap_init<Wt::WStandardItemModel>(),
             "Construct an empty 0-by-0 model.")
        .def(heap_init<Wt::WStandardItemModel, int, int>(), "rows"_a, "columns"_a,
             "Construct a model pre-sized to `rows` x `columns`, with\n"
             "empty WStandardItem cells in every position.")
        .def("clear", &Wt::WStandardItemModel::clear,
            "Drop every item; rowCount and columnCount go to 0.")
        .def_prop_ro("invisible_root_item",
            &Wt::WStandardItemModel::invisibleRootItem,
            nb::rv_policy::reference_internal,
            "The internal root item. Manipulate it directly for advanced "
            "tree construction; for flat tables prefer model.append_row.")
        .def("index_from_item",
            &Wt::WStandardItemModel::indexFromItem,
            "item"_a,
            "WModelIndex of the cell holding `item`, or an invalid index\n"
            "if the item is not part of this model.")
        .def("item_from_index",
            nb::overload_cast<const Wt::WModelIndex&>(
                &Wt::WStandardItemModel::itemFromIndex, nb::const_),
            "index"_a,
            nb::rv_policy::reference_internal,
            "WStandardItem at `index` — the inverse of `index_from_item`.\n"
            "Returns None for the invalid index or out-of-range positions.")
        .def("item",
            [](const Wt::WStandardItemModel& self, int row, int col) {
                return self.item(row, col);
            },
            "row"_a, "column"_a = 0,
            nb::rv_policy::reference_internal,
            "Top-level item at (row, column).")
        .def("set_item",
            [](Wt::WStandardItemModel& self, int row, int col,
               nb::object py_item) {
                auto it = nb::cast<std::unique_ptr<Wt::WStandardItem>>(py_item);
                self.setItem(row, col, std::move(it));
                nb::inst_set_state(py_item, /*ready*/ true,
                                   /*destruct*/ false);
            },
            "row"_a, "column"_a, "item"_a,
            "Place an item at (row, column). Transfers ownership; the "
            "Python wrapper is re-armed as a non-owning alias.")
        .def("append_row",
            [](Wt::WStandardItemModel& self, nb::list py_items) {
                std::vector<std::unique_ptr<Wt::WStandardItem>> items;
                items.reserve(nb::len(py_items));
                for (nb::handle h : py_items) {
                    nb::object py_it = nb::borrow(h);
                    items.push_back(
                        nb::cast<std::unique_ptr<Wt::WStandardItem>>(py_it));
                    nb::inst_set_state(py_it, /*ready*/ true,
                                       /*destruct*/ false);
                }
                self.appendRow(std::move(items));
            },
            "items"_a,
            "Append a row of top-level items. The list length should\n"
            "match `column_count`; transfers ownership of each item, the\n"
            "Python wrappers stay usable as non-owning aliases.")
        .def("append_column",
            [](Wt::WStandardItemModel& self, nb::list py_items) {
                std::vector<std::unique_ptr<Wt::WStandardItem>> items;
                items.reserve(nb::len(py_items));
                for (nb::handle h : py_items) {
                    nb::object py_it = nb::borrow(h);
                    items.push_back(
                        nb::cast<std::unique_ptr<Wt::WStandardItem>>(py_it));
                    nb::inst_set_state(py_it, /*ready*/ true,
                                       /*destruct*/ false);
                }
                self.appendColumn(std::move(items));
            },
            "items"_a,
            "Append a column of top-level items. The list length should\n"
            "match `row_count`; same ownership transfer as append_row.");

    // ---- SelectionBehavior + SortOrder enums ----
    //
    // Bound BEFORE WAbstractItemView so the def_prop_rw for selection_behavior
    // (which takes SelectionBehavior) can find the Python type. SortOrder is
    // used by sort_by_column.

    nb::enum_<Wt::SelectionBehavior>(m, "SelectionBehavior",
        "Whether item-view selection operates on individual cells or\n"
        "whole rows.")
        .value("SelectItems", Wt::SelectionBehavior::Items,
               "Clicks select individual cells; the selection model holds\n"
               "WModelIndex values pointing to specific (row, column)\n"
               "pairs.")
        .value("SelectRows", Wt::SelectionBehavior::Rows,
               "Clicks select the whole row; visually the entire row\n"
               "highlights.");

    nb::enum_<Wt::SortOrder>(m, "SortOrder",
        "Sort direction for column sorts on item views and sort/filter\n"
        "proxy models.")
        .value("Ascending", Wt::SortOrder::Ascending,
               "Smallest / earliest first.")
        .value("Descending", Wt::SortOrder::Descending,
               "Largest / latest first.");

    nb::enum_<Wt::ScrollHint>(m, "ScrollHint",
        "How a view should align a target cell within its viewport when\n"
        "asked to scroll to it.")
        .value("EnsureVisible", Wt::ScrollHint::EnsureVisible,
               "Scroll only as much as needed to make the target visible;\n"
               "no scroll if it already is.")
        .value("PositionAtTop", Wt::ScrollHint::PositionAtTop,
               "Scroll so the target sits at the top of the viewport.")
        .value("PositionAtBottom", Wt::ScrollHint::PositionAtBottom,
               "Scroll so the target sits at the bottom of the viewport.")
        .value("PositionAtCenter", Wt::ScrollHint::PositionAtCenter,
               "Scroll so the target sits in the vertical middle of the\n"
               "viewport.")
        .value("PositionAtLeft", Wt::ScrollHint::PositionAtLeft,
               "Scroll so the target column aligns with the left edge.")
        .value("PositionAtRight", Wt::ScrollHint::PositionAtRight,
               "Scroll so the target column aligns with the right edge.")
        .value("NoScroll", Wt::ScrollHint::NoScroll,
               "Do not scroll at all.");

    // ---- WAbstractItemView (widget base for views) ----
    //
    // Bind as inheriting WWidget per the project convention for
    // WCompositeWidget descendants. WTableView and WTreeView both inherit
    // this base.

    nb::class_<Wt::WAbstractItemView, Wt::WWidget>(m, "WAbstractItemView",
        "Base widget for views that render a WAbstractItemModel. WTableView\n"
        "and WTreeView both derive from this; the shared surface covers\n"
        "model attachment, root-index navigation, selection, sorting, and\n"
        "the click signals.\n"
        "\n"
        "    view = container.add_widget(wt.WTableView())\n"
        "    view.model = model\n"
        "    view.sorting_enabled = True\n"
        "    view.selection_behavior = wt.SelectionBehavior.SelectRows\n"
        "    view.clicked.connect(lambda idx, ev: handle_click(idx))")
        .def_prop_rw("model",
            [](const Wt::WAbstractItemView& self) { return self.model(); },
            [](Wt::WAbstractItemView& self,
               const std::shared_ptr<Wt::WAbstractItemModel>& model) {
                self.setModel(model);
            },
            "The attached model (shared_ptr<WAbstractItemModel>). Assign\n"
            "a concrete model — or a proxy wrapping one — to populate the\n"
            "view; the view re-renders on changes the model emits.")
        .def("set_root_index", &Wt::WAbstractItemView::setRootIndex,
             "root_index"_a,
             "Show the children of `root_index` as the view's top-level\n"
             "rows. Useful for drilling into a sub-tree of a tree model;\n"
             "pass an invalid WModelIndex to reset to showing everything.")
        .def_prop_ro("root_index", &Wt::WAbstractItemView::rootIndex,
            "Current root WModelIndex — the node whose children the view\n"
            "is showing as top-level rows.")
        .def("clear_selection", &Wt::WAbstractItemView::clearSelection,
            "Drop every selected cell/row.")
        .def("is_selected", &Wt::WAbstractItemView::isSelected, "index"_a,
            "True if `index` is currently part of the selection.")
        .def("sort_by_column", &Wt::WAbstractItemView::sortByColumn,
             "column"_a, "order"_a,
             "Sort visible rows by `column` in the given SortOrder. The\n"
             "underlying model must support sort() for this to take\n"
             "effect — e.g. when fronted by a WSortFilterProxyModel.")
        .def_prop_ro("clicked", &Wt::WAbstractItemView::clicked,
                     nb::rv_policy::reference_internal,
                     "ModelIndexMouseSignal fired when the user clicks a\n"
                     "cell. Callbacks receive (WModelIndex, WMouseEvent).")
        .def_prop_ro("double_clicked", &Wt::WAbstractItemView::doubleClicked,
                     nb::rv_policy::reference_internal,
                     "ModelIndexMouseSignal fired on double-click. Same\n"
                     "payload as `clicked`.")
        .def_prop_ro("selection_changed",
                     &Wt::WAbstractItemView::selectionChanged,
                     nb::rv_policy::reference_internal,
                     "No-arg signal fired when the selection changes —\n"
                     "use to refresh detail panes, enable/disable action\n"
                     "buttons, etc.")
        .def("set_column_width", &Wt::WAbstractItemView::setColumnWidth,
             "column"_a, "width"_a,
             "Set the rendered width of `column` to the given WLength.")
        .def_prop_rw("sorting_enabled",
            [](const Wt::WAbstractItemView& self) {
                return self.isSortingEnabled();
            },
            [](Wt::WAbstractItemView& self, bool enabled) {
                self.setSortingEnabled(enabled);
            },
            "Whether the column headers act as sort toggles. The model\n"
            "(or a wrapping sort/filter proxy) must implement sort() for\n"
            "the user clicks to have an effect.")
        .def_prop_rw("column_resize_enabled",
            [](const Wt::WAbstractItemView& self) {
                return self.isColumnResizeEnabled();
            },
            [](Wt::WAbstractItemView& self, bool enabled) {
                self.setColumnResizeEnabled(enabled);
            },
            "Whether the user can drag column dividers to resize columns.")
        .def_prop_rw("selection_behavior",
            &Wt::WAbstractItemView::selectionBehavior,
            &Wt::WAbstractItemView::setSelectionBehavior,
            "Whether selection targets individual cells or whole rows\n"
            "(a SelectionBehavior value).")
        .def_prop_rw("selection_mode",
            &Wt::WAbstractItemView::selectionMode,
            &Wt::WAbstractItemView::setSelectionMode,
            "Single vs. multi-select, etc. (a SelectionMode value).");

    // ---- WTableView ----

    nb::class_<Wt::WTableView, Wt::WAbstractItemView>(m, "WTableView",
        "Model-driven flat table view. Renders the rows directly under\n"
        "its root index as a scrollable grid, one row of cells per row\n"
        "of the model. Use with a WStandardItemModel, a WStringListModel,\n"
        "or any custom WAbstractItemModel.\n"
        "\n"
        "    view = container.add_widget(wt.WTableView())\n"
        "    view.model = model\n"
        "    view.sorting_enabled = True\n"
        "    view.clicked.connect(on_row_click)")
        .def(heap_init<Wt::WTableView>(),
             "Construct an empty table view. Assign `model` to populate\n"
             "it.")
        .def("scroll_to",
             nb::overload_cast<const Wt::WModelIndex&, Wt::ScrollHint>(
                 &Wt::WTableView::scrollTo),
             "index"_a, "hint"_a = Wt::ScrollHint::EnsureVisible,
             "Scroll so the cell at `index` is positioned per `hint`.\n"
             "The default is to bring it into view if it isn't already.");

    // ---- WTreeView ----

    nb::class_<Wt::WTreeView, Wt::WAbstractItemView>(m, "WTreeView",
        "Model-driven tree view. Renders rows hierarchically with\n"
        "expand/collapse toggles for any item whose `has_children` is\n"
        "true. Suits hierarchical data: directory trees, org charts,\n"
        "category browsers.\n"
        "\n"
        "    view = container.add_widget(wt.WTreeView())\n"
        "    view.model = standard_model     # any model whose items have children\n"
        "    view.expand_to_depth(2)\n"
        "    view.clicked.connect(on_node_click)")
        .def(heap_init<Wt::WTreeView>(),
             "Construct an empty tree view. Assign `model` to populate\n"
             "it.")
        .def("set_expanded", &Wt::WTreeView::setExpanded,
             "index"_a, "expanded"_a,
             "Expand or collapse the subtree rooted at `index`.")
        .def("is_expanded", &Wt::WTreeView::isExpanded, "index"_a,
             "True if the subtree at `index` is currently expanded.")
        .def("expand", &Wt::WTreeView::expand, "index"_a,
             "Expand the subtree at `index`. Equivalent to\n"
             "`set_expanded(index, True)`.")
        .def("collapse", &Wt::WTreeView::collapse, "index"_a,
             "Collapse the subtree at `index`. Equivalent to\n"
             "`set_expanded(index, False)`.")
        .def("collapse_all", &Wt::WTreeView::collapseAll,
             "Collapse every expanded node; only the top-level rows\n"
             "remain visible.")
        .def("expand_to_depth", &Wt::WTreeView::expandToDepth, "depth"_a,
             "Expand every node whose distance from the root is less\n"
             "than `depth`. Depth 0 means everything stays collapsed;\n"
             "depth 1 expands the root's immediate children, and so on.")
        .def_prop_rw("root_is_decorated",
            &Wt::WTreeView::rootIsDecorated,
            &Wt::WTreeView::setRootIsDecorated,
            "Whether top-level rows show an expand/collapse decoration\n"
            "(arrow). Turn off to render top-level rows like a flat list\n"
            "with the subtrees hanging off them.");

}

}  // namespace witty_for_python
