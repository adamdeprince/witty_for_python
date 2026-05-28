#include "common.hpp"

#include <Wt/WAbstractProxyModel.h>
#include <Wt/WIdentityProxyModel.h>
#include <Wt/WModelIndex.h>           // ItemDataRole + SortOrder
#include <Wt/WReadOnlyProxyModel.h>
#include <Wt/WSortFilterProxyModel.h>

#include <memory>
#include <regex>
#include <string>

namespace witty_for_python {

void register_modelview_proxy(nb::module_& m) {
    // ---- WAbstractProxyModel (abstract base) ----
    //
    // Proxy models sit between a source WAbstractItemModel and one or more
    // views, transforming what the view sees without disturbing the source
    // (sorted, filtered, read-only, aggregated, …). The set_source_model
    // call wires the chain up; views attach to the proxy, not the source.
    //
    // Bound non-constructible — concrete subclasses are what callers
    // instantiate.

    nb::class_<Wt::WAbstractProxyModel, Wt::WAbstractItemModel>(
        m, "WAbstractProxyModel")
        .def_prop_rw("source_model",
            // The shared_ptr getter is on the value side; the setter is
            // virtual on each subclass — Wt resolves it polymorphically.
            [](const Wt::WAbstractProxyModel& self) {
                return self.sourceModel();
            },
            [](Wt::WAbstractProxyModel& self,
               const std::shared_ptr<Wt::WAbstractItemModel>& m) {
                self.setSourceModel(m);
            },
            "The wrapped model. Setting it disconnects from the previous "
            "source and rewires the proxy.")
        .def("map_from_source", &Wt::WAbstractProxyModel::mapFromSource,
             "source_index"_a,
             "Translate a source-model index to the proxy's coordinate "
             "system (sorted/filtered/etc. position).")
        .def("map_to_source", &Wt::WAbstractProxyModel::mapToSource,
             "proxy_index"_a,
             "Translate a proxy index back to the source model. Required "
             "when handing a clicked index back to source-specific logic.");

    // ---- WIdentityProxyModel: pass-through ----
    //
    // Forwards every method to the source unchanged. Useful as a base for
    // a custom proxy subclass that overrides one or two methods (e.g. a
    // role re-mapper) — and on its own as a placeholder.

    nb::class_<Wt::WIdentityProxyModel, Wt::WAbstractProxyModel>(
        m, "WIdentityProxyModel")
        .def(heap_init<Wt::WIdentityProxyModel>());

    // ---- WReadOnlyProxyModel: strips edit capability ----
    //
    // Forwards every read to the source; refuses every setData /
    // setHeaderData / insert / remove. Cheap way to expose a model to a
    // view that must not edit it (e.g. a preview pane).

    nb::class_<Wt::WReadOnlyProxyModel, Wt::WAbstractProxyModel>(
        m, "WReadOnlyProxyModel")
        .def(heap_init<Wt::WReadOnlyProxyModel>());

    // ---- WSortFilterProxyModel: sorts and filters rows ----
    //
    // The headline proxy. Hook a source model, set a column to filter on,
    // give it a regex, optionally specify the sort role/column — the view
    // sees only matching rows in the requested order.
    //
    // The C++ setFilterRegExp takes a unique_ptr<std::regex>; from Python
    // we accept a string and build the std::regex internally. Pass the
    // empty string to disable filtering.

    nb::class_<Wt::WSortFilterProxyModel, Wt::WAbstractProxyModel>(
        m, "WSortFilterProxyModel")
        .def(heap_init<Wt::WSortFilterProxyModel>())
        .def_prop_rw("filter_key_column",
            &Wt::WSortFilterProxyModel::filterKeyColumn,
            &Wt::WSortFilterProxyModel::setFilterKeyColumn,
            "Column index in the source model whose values are matched "
            "against the filter regex. Default 0.")
        .def("set_filter_regexp",
            // Build a unique_ptr<std::regex> inside the lambda; pass nullptr
            // when the pattern is empty so the proxy disables filtering
            // entirely (rather than matching everything against `^$`).
            [](Wt::WSortFilterProxyModel& self, const std::string& pattern) {
                if (pattern.empty()) {
                    self.setFilterRegExp(nullptr);
                } else {
                    self.setFilterRegExp(std::make_unique<std::regex>(pattern));
                }
            },
            "pattern"_a,
            "Set the regex pattern applied to the filter column. Empty "
            "string disables filtering. Wt uses std::regex_match (FULL-"
            "STRING match, not substring search), ECMAScript flavour — to "
            "search for a substring, wrap with wildcards: `.*foo.*`. "
            "Re-runs the filter immediately when `dynamic_sort_filter` is "
            "True; otherwise call `invalidate()` afterward.")
        .def_prop_rw("filter_role",
            &Wt::WSortFilterProxyModel::filterRole,
            &Wt::WSortFilterProxyModel::setFilterRole,
            "Data role read from the filter column before matching against "
            "the regex. Default Display.")
        .def_prop_rw("sort_role",
            &Wt::WSortFilterProxyModel::sortRole,
            &Wt::WSortFilterProxyModel::setSortRole,
            "Data role read when comparing rows during sort. Default "
            "Display.")
        .def_prop_ro("sort_column", &Wt::WSortFilterProxyModel::sortColumn,
            "Current sort column, or -1 when sort() has not been called.")
        .def_prop_ro("sort_order", &Wt::WSortFilterProxyModel::sortOrder)
        .def_prop_rw("dynamic_sort_filter",
            &Wt::WSortFilterProxyModel::dynamicSortFilter,
            &Wt::WSortFilterProxyModel::setDynamicSortFilter,
            "When True, the proxy re-runs filter + sort whenever the "
            "source model changes. False (default) requires an explicit "
            "invalidate() call after modifications.")
        .def("invalidate", &Wt::WSortFilterProxyModel::invalidate,
            "Force a re-evaluation of filter + sort against the current "
            "source data. Needed after source mutations when "
            "dynamic_sort_filter is False.")
        .def("sort",
             [](Wt::WSortFilterProxyModel& self, int column,
                Wt::SortOrder order) {
                 self.sort(column, order);
             },
             "column"_a, "order"_a = Wt::SortOrder::Ascending,
             "Sort by the given column. -1 disables sorting.");
}

}  // namespace witty_for_python
