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
    // Bound non-constructible — concrete subclasses are what callers
    // instantiate.

    nb::class_<Wt::WAbstractProxyModel, Wt::WAbstractItemModel>(
        m, "WAbstractProxyModel",
        "Base class for models that wrap another model and present a\n"
        "transformed view of it. Sort/filter, read-only-isation, identity\n"
        "pass-through and similar adapters all derive from this. Set the\n"
        "underlying model via `source_model`, then attach a view to the\n"
        "PROXY (not the source) so it sees the transformed rows.\n"
        "\n"
        "    proxy = wt.WSortFilterProxyModel()\n"
        "    proxy.source_model = base_model\n"
        "    table_view.model = proxy\n"
        "\n"
        "Use `map_from_source` / `map_to_source` to translate WModelIndex\n"
        "values between the two coordinate systems.")
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
            "The wrapped model. Setting it disconnects from the previous\n"
            "source and rewires the proxy.")
        .def("map_from_source", &Wt::WAbstractProxyModel::mapFromSource,
             "source_index"_a,
             "Translate a source-model index to the proxy's coordinate\n"
             "system (sorted/filtered/etc. position). Returns an invalid\n"
             "index if the source row is filtered out.")
        .def("map_to_source", &Wt::WAbstractProxyModel::mapToSource,
             "proxy_index"_a,
             "Translate a proxy index back to the source model. Required\n"
             "when handing a clicked index back to source-specific logic.");

    // ---- WIdentityProxyModel: pass-through ----

    nb::class_<Wt::WIdentityProxyModel, Wt::WAbstractProxyModel>(
        m, "WIdentityProxyModel",
        "Proxy that forwards every call to the source model unchanged.\n"
        "Useful as a starting point for a custom subclass that only\n"
        "tweaks one or two methods (a data-role rewriter, for instance),\n"
        "or as a placeholder when an API requires a proxy but no\n"
        "transformation is needed yet.")
        .def(heap_init<Wt::WIdentityProxyModel>(),
             "Construct an empty identity proxy; assign `source_model`\n"
             "to wire it up.");

    // ---- WReadOnlyProxyModel: strips edit capability ----

    nb::class_<Wt::WReadOnlyProxyModel, Wt::WAbstractProxyModel>(
        m, "WReadOnlyProxyModel",
        "Proxy that forwards reads to the source but refuses every\n"
        "mutation (setData, setHeaderData, insertRows, removeRows, …).\n"
        "Cheap way to hand a model to a view that must not be allowed to\n"
        "edit it — e.g. a preview pane that shares its underlying data\n"
        "with an editable master view.\n"
        "\n"
        "    readonly = wt.WReadOnlyProxyModel()\n"
        "    readonly.source_model = shared_model\n"
        "    preview.model = readonly")
        .def(heap_init<Wt::WReadOnlyProxyModel>(),
             "Construct an empty read-only proxy; assign `source_model`\n"
             "to wire it up.");

    // ---- WSortFilterProxyModel: sorts and filters rows ----

    nb::class_<Wt::WSortFilterProxyModel, Wt::WAbstractProxyModel>(
        m, "WSortFilterProxyModel",
        "Proxy that hides rows whose `filter_key_column` value does not\n"
        "match a regex, and optionally re-orders the rows it does keep.\n"
        "Operates on the rows directly under whatever root index the\n"
        "view is showing.\n"
        "\n"
        "    proxy = wt.WSortFilterProxyModel()\n"
        "    proxy.source_model = people_model\n"
        "    proxy.filter_key_column = 1                 # surname column\n"
        "    proxy.set_filter_regexp('.*smith.*')\n"
        "    proxy.dynamic_sort_filter = True\n"
        "    proxy.sort(0, wt.SortOrder.Ascending)       # by first name\n"
        "    table_view.model = proxy\n"
        "\n"
        "The filter regex is implemented with std::regex (ECMAScript\n"
        "flavour) and applied as a full-string match — see\n"
        "`set_filter_regexp` for details.")
        .def(heap_init<Wt::WSortFilterProxyModel>(),
             "Construct an empty proxy. Assign `source_model`, then set\n"
             "filter/sort parameters as needed.")
        .def_prop_rw("filter_key_column",
            &Wt::WSortFilterProxyModel::filterKeyColumn,
            &Wt::WSortFilterProxyModel::setFilterKeyColumn,
            "Column index in the source model whose values are matched\n"
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
            "Set the regex pattern applied to the filter column. Empty\n"
            "string disables filtering. Wt uses std::regex_match (FULL-\n"
            "STRING match, not substring search), ECMAScript flavour — to\n"
            "search for a substring, wrap with wildcards: `.*foo.*`.\n"
            "Re-runs the filter immediately when `dynamic_sort_filter` is\n"
            "True; otherwise call `invalidate()` afterward.")
        .def_prop_rw("filter_role",
            &Wt::WSortFilterProxyModel::filterRole,
            &Wt::WSortFilterProxyModel::setFilterRole,
            "Data role read from the filter column before matching against\n"
            "the regex. Default Display.")
        .def_prop_rw("sort_role",
            &Wt::WSortFilterProxyModel::sortRole,
            &Wt::WSortFilterProxyModel::setSortRole,
            "Data role read when comparing rows during sort. Default\n"
            "Display.")
        .def_prop_ro("sort_column", &Wt::WSortFilterProxyModel::sortColumn,
            "Current sort column, or -1 when sort() has not been called.")
        .def_prop_ro("sort_order", &Wt::WSortFilterProxyModel::sortOrder,
            "Current SortOrder in effect (Ascending or Descending).")
        .def_prop_rw("dynamic_sort_filter",
            &Wt::WSortFilterProxyModel::dynamicSortFilter,
            &Wt::WSortFilterProxyModel::setDynamicSortFilter,
            "When True, the proxy re-runs filter + sort whenever the\n"
            "source model changes. False (default) requires an explicit\n"
            "invalidate() call after modifications.")
        .def("invalidate", &Wt::WSortFilterProxyModel::invalidate,
            "Force a re-evaluation of filter + sort against the current\n"
            "source data. Needed after source mutations when\n"
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
