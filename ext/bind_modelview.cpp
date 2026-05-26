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
    //
    // Wt's ItemDataRole is a value class wrapping an int, with named
    // static constants for the standard roles (Display, Edit, Decoration,
    // ToolTip, StyleClass, Checked, Link, …). Bound as a class with class-
    // attribute statics matching Wt's surface — so callers say
    // `wt.ItemDataRole.Display` rather than the bare int 0.

    auto role_cls = nb::class_<Wt::ItemDataRole>(m, "ItemDataRole")
        .def(nb::init<int>(), "role"_a)
        .def_prop_ro("value", &Wt::ItemDataRole::value)
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
    //
    // Value type that addresses a cell in a model: (row, column, parent).
    // Invalid indices (returned for top-level parent queries) have
    // `is_valid` False. Comparable + hashable so Python users can store
    // indexes in sets / dict keys.

    nb::class_<Wt::WModelIndex>(m, "WModelIndex")
        .def(nb::init<>())
        .def_prop_ro("row", &Wt::WModelIndex::row)
        .def_prop_ro("column", &Wt::WModelIndex::column)
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
        m, "ModelIndexMouseSignal")
        .def("connect",
            [](Wt::Signal<Wt::WModelIndex, Wt::WMouseEvent>& s,
               nb::callable cb) {
                return py_connect<
                    Wt::Signal<Wt::WModelIndex, Wt::WMouseEvent>,
                    Wt::WModelIndex, Wt::WMouseEvent>(s, std::move(cb));
            }, "callable"_a)
        .def("disconnect_all_slots",
            [](Wt::Signal<Wt::WModelIndex, Wt::WMouseEvent>& s) {
                connection_registry_disconnect_all(&s);
            });

    // ---- WAbstractItemModel (abstract base) ----
    //
    // Bound non-constructible. Concrete subclasses (WStandardItemModel,
    // WStringListModel) are what Python users instantiate. The interface
    // exposes the read-side surface most consumers need; cpp17::any-typed
    // data() and setData() are NOT bound (write goes through WStandardItem;
    // read goes through `display_data` below, which calls Wt::asString
    // internally).

    nb::class_<Wt::WAbstractItemModel, Wt::WObject>(m, "WAbstractItemModel")
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
            "parent"_a = Wt::WModelIndex())
        .def("has_children",
            &Wt::WAbstractItemModel::hasChildren, "index"_a)
        .def("index",
            [](const Wt::WAbstractItemModel& self, int row, int col,
               const Wt::WModelIndex& parent) {
                return self.index(row, col, parent);
            },
            "row"_a, "column"_a, "parent"_a = Wt::WModelIndex())
        .def("parent_of",
            // Renamed: `parent` collides with Python keyword usage on
            // ItemDataRole's other signatures and is awkward as a method
            // name. Callers can also reach this via WModelIndex.parent().
            [](const Wt::WAbstractItemModel& self,
               const Wt::WModelIndex& index) {
                return self.parent(index);
            },
            "index"_a)
        .def("display_data",
            // Convenience: fetch the Display-role value as a string.
            // Sidesteps the cpp17::any binding for the common case of
            // reading text shown in a WTableView column.
            [](const Wt::WAbstractItemModel& self,
               const Wt::WModelIndex& index) {
                return any_to_python(self.data(index, Wt::ItemDataRole::Display));
            },
            "index"_a)
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
        m, "WAbstractListModel");

    // ---- WStringListModel: a flat list of strings ----

    nb::class_<Wt::WStringListModel, Wt::WAbstractListModel>(m, "WStringListModel")
        .def(nb::init<>())
        .def(nb::init<const std::vector<Wt::WString>&>(), "strings"_a)
        .def("set_string_list", &Wt::WStringListModel::setStringList,
             "strings"_a)
        .def("add_string", &Wt::WStringListModel::addString, "string"_a)
        .def_prop_ro("string_list",
            [](const Wt::WStringListModel& self) {
                return self.stringList();
            });

    // ---- WStandardItem ----
    //
    // The unit of content in a WStandardItemModel. Each cell of a table /
    // each node of a tree is one WStandardItem. Items own their children:
    // `set_child(row, col, item)` transfers ownership; the Python wrapper
    // around the moved-in item becomes non-owning.

    nb::class_<Wt::WStandardItem>(m, "WStandardItem")
        .def(nb::init<>())
        .def(nb::init<const Wt::WString&>(), "text"_a)
        .def_prop_rw("text",
            [](const Wt::WStandardItem& self) { return self.text(); },
            [](Wt::WStandardItem& self, const Wt::WString& t) { self.setText(t); })
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
            })
        .def_prop_rw("tool_tip",
            [](const Wt::WStandardItem& self) { return self.toolTip(); },
            [](Wt::WStandardItem& self, const Wt::WString& t) {
                self.setToolTip(t);
            })
        .def("set_link", &Wt::WStandardItem::setLink, "link"_a)
        .def_prop_rw("checkable",
            &Wt::WStandardItem::isCheckable, &Wt::WStandardItem::setCheckable)
        .def_prop_rw("checked",
            &Wt::WStandardItem::isChecked, &Wt::WStandardItem::setChecked)
        .def_prop_rw("tristate",
            &Wt::WStandardItem::isTristate, &Wt::WStandardItem::setTristate)
        .def_prop_rw("editable",
            &Wt::WStandardItem::isEditable, &Wt::WStandardItem::setEditable)
        .def_prop_ro("has_children", &Wt::WStandardItem::hasChildren)
        .def_prop_ro("row_count", &Wt::WStandardItem::rowCount)
        .def_prop_ro("column_count", &Wt::WStandardItem::columnCount)
        .def("set_row_count", &Wt::WStandardItem::setRowCount, "rows"_a)
        .def("set_column_count", &Wt::WStandardItem::setColumnCount,
             "columns"_a)
        .def("append_row",
            // Take ownership of every item in the row.
            [](Wt::WStandardItem& self,
               std::vector<std::unique_ptr<Wt::WStandardItem>> items) {
                self.appendRow(std::move(items));
            },
            "items"_a,
            "Append a single child row. Each item's Python wrapper becomes "
            "non-owning after the call — fetch back via `child(row, col)` "
            "if you need to keep editing.")
        .def("append_column",
            [](Wt::WStandardItem& self,
               std::vector<std::unique_ptr<Wt::WStandardItem>> items) {
                self.appendColumn(std::move(items));
            },
            "items"_a)
        // insertRows / insertColumns are overloaded (count form +
        // unique_ptr-vector form). We bind only the count form here; the
        // vector form is redundant with append_row.
        .def("insert_rows",
            nb::overload_cast<int, int>(&Wt::WStandardItem::insertRows),
            "row"_a, "count"_a)
        .def("insert_columns",
            nb::overload_cast<int, int>(&Wt::WStandardItem::insertColumns),
            "column"_a, "count"_a)
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
        m, "WStandardItemModel")
        .def(nb::init<>())
        .def(nb::init<int, int>(), "rows"_a, "columns"_a)
        .def("clear", &Wt::WStandardItemModel::clear,
            "Drop every item; rowCount and columnCount go to 0.")
        .def_prop_ro("invisible_root_item",
            &Wt::WStandardItemModel::invisibleRootItem,
            nb::rv_policy::reference_internal,
            "The internal root item. Manipulate it directly for advanced "
            "tree construction; for flat tables prefer model.append_row.")
        .def("index_from_item",
            &Wt::WStandardItemModel::indexFromItem,
            "item"_a)
        .def("item_from_index",
            nb::overload_cast<const Wt::WModelIndex&>(
                &Wt::WStandardItemModel::itemFromIndex, nb::const_),
            "index"_a,
            nb::rv_policy::reference_internal)
        .def("item",
            [](const Wt::WStandardItemModel& self, int row, int col) {
                return self.item(row, col);
            },
            "row"_a, "column"_a = 0,
            nb::rv_policy::reference_internal,
            "Top-level item at (row, column).")
        .def("set_item",
            [](Wt::WStandardItemModel& self, int row, int col,
               std::unique_ptr<Wt::WStandardItem> item) {
                self.setItem(row, col, std::move(item));
            },
            "row"_a, "column"_a, "item"_a,
            "Place an item at (row, column). Transfers ownership; the "
            "Python wrapper becomes non-owning.")
        .def("append_row",
            [](Wt::WStandardItemModel& self,
               std::vector<std::unique_ptr<Wt::WStandardItem>> items) {
                self.appendRow(std::move(items));
            },
            "items"_a,
            "Append a row of items. Equivalent to invisible_root_item."
            "append_row.")
        .def("append_column",
            [](Wt::WStandardItemModel& self,
               std::vector<std::unique_ptr<Wt::WStandardItem>> items) {
                self.appendColumn(std::move(items));
            },
            "items"_a);

    // ---- SelectionBehavior + SortOrder enums ----
    //
    // Bound BEFORE WAbstractItemView so the def_prop_rw for selection_behavior
    // (which takes SelectionBehavior) can find the Python type. SortOrder is
    // used by sort_by_column.

    nb::enum_<Wt::SelectionBehavior>(m, "SelectionBehavior")
        .value("SelectItems", Wt::SelectionBehavior::Items)
        .value("SelectRows", Wt::SelectionBehavior::Rows);

    nb::enum_<Wt::SortOrder>(m, "SortOrder")
        .value("Ascending", Wt::SortOrder::Ascending)
        .value("Descending", Wt::SortOrder::Descending);

    nb::enum_<Wt::ScrollHint>(m, "ScrollHint")
        .value("EnsureVisible", Wt::ScrollHint::EnsureVisible)
        .value("PositionAtTop", Wt::ScrollHint::PositionAtTop)
        .value("PositionAtBottom", Wt::ScrollHint::PositionAtBottom)
        .value("PositionAtCenter", Wt::ScrollHint::PositionAtCenter)
        .value("PositionAtLeft", Wt::ScrollHint::PositionAtLeft)
        .value("PositionAtRight", Wt::ScrollHint::PositionAtRight)
        .value("NoScroll", Wt::ScrollHint::NoScroll);

    // ---- WAbstractItemView (widget base for views) ----
    //
    // Bind as inheriting WWidget per the project convention for
    // WCompositeWidget descendants. WTableView and WTreeView both inherit
    // this base.

    nb::class_<Wt::WAbstractItemView, Wt::WWidget>(m, "WAbstractItemView")
        .def_prop_rw("model",
            [](const Wt::WAbstractItemView& self) { return self.model(); },
            [](Wt::WAbstractItemView& self,
               const std::shared_ptr<Wt::WAbstractItemModel>& model) {
                self.setModel(model);
            })
        .def("set_root_index", &Wt::WAbstractItemView::setRootIndex,
             "root_index"_a)
        .def_prop_ro("root_index", &Wt::WAbstractItemView::rootIndex)
        .def("clear_selection", &Wt::WAbstractItemView::clearSelection)
        .def("is_selected", &Wt::WAbstractItemView::isSelected, "index"_a)
        .def("sort_by_column", &Wt::WAbstractItemView::sortByColumn,
             "column"_a, "order"_a)
        .def_prop_ro("clicked", &Wt::WAbstractItemView::clicked,
                     nb::rv_policy::reference_internal)
        .def_prop_ro("double_clicked", &Wt::WAbstractItemView::doubleClicked,
                     nb::rv_policy::reference_internal)
        .def_prop_ro("selection_changed",
                     &Wt::WAbstractItemView::selectionChanged,
                     nb::rv_policy::reference_internal)
        .def("set_column_width", &Wt::WAbstractItemView::setColumnWidth,
             "column"_a, "width"_a)
        .def_prop_rw("sorting_enabled",
            [](const Wt::WAbstractItemView& self) {
                return self.isSortingEnabled();
            },
            [](Wt::WAbstractItemView& self, bool enabled) {
                self.setSortingEnabled(enabled);
            })
        .def_prop_rw("column_resize_enabled",
            [](const Wt::WAbstractItemView& self) {
                return self.isColumnResizeEnabled();
            },
            [](Wt::WAbstractItemView& self, bool enabled) {
                self.setColumnResizeEnabled(enabled);
            })
        .def_prop_rw("selection_behavior",
            &Wt::WAbstractItemView::selectionBehavior,
            &Wt::WAbstractItemView::setSelectionBehavior)
        .def_prop_rw("selection_mode",
            &Wt::WAbstractItemView::selectionMode,
            &Wt::WAbstractItemView::setSelectionMode);

    // ---- WTableView ----

    nb::class_<Wt::WTableView, Wt::WAbstractItemView>(m, "WTableView")
        .def(nb::init<>())
        .def("scroll_to",
             nb::overload_cast<const Wt::WModelIndex&, Wt::ScrollHint>(
                 &Wt::WTableView::scrollTo),
             "index"_a, "hint"_a = Wt::ScrollHint::EnsureVisible);

    // ---- WTreeView ----

    nb::class_<Wt::WTreeView, Wt::WAbstractItemView>(m, "WTreeView")
        .def(nb::init<>())
        .def("set_expanded", &Wt::WTreeView::setExpanded,
             "index"_a, "expanded"_a)
        .def("is_expanded", &Wt::WTreeView::isExpanded, "index"_a)
        .def("expand", &Wt::WTreeView::expand, "index"_a)
        .def("collapse", &Wt::WTreeView::collapse, "index"_a)
        .def("collapse_all", &Wt::WTreeView::collapseAll)
        .def("expand_to_depth", &Wt::WTreeView::expandToDepth, "depth"_a)
        .def_prop_rw("root_is_decorated",
            &Wt::WTreeView::rootIsDecorated,
            &Wt::WTreeView::setRootIsDecorated);

}

}  // namespace witty_for_python
