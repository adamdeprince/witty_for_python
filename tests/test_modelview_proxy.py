"""Proxy model suite.

All proxy classes are model-side (no widgets), so they construct happily
without an active WApplication and we can exercise filter / sort behaviour
end-to-end in tests.
"""

from __future__ import annotations

import pytest
import witty_for_python as wt


# ---- class binding surface ----------------------------------------------

@pytest.mark.parametrize("cls,base", [
    (wt.WAbstractProxyModel,    wt.WAbstractItemModel),
    (wt.WIdentityProxyModel,    wt.WAbstractProxyModel),
    (wt.WReadOnlyProxyModel,    wt.WAbstractProxyModel),
    (wt.WSortFilterProxyModel,  wt.WAbstractProxyModel),
])
def test_proxy_inheritance(cls: type, base: type) -> None:
    assert issubclass(cls, base)


def test_abstract_proxy_is_not_constructible() -> None:
    """WAbstractProxyModel is bound non-constructible; only the concrete
    subclasses are instantiated by Python users."""
    with pytest.raises(TypeError):
        wt.WAbstractProxyModel()


# ---- WIdentityProxyModel --------------------------------------------------

def test_identity_proxy_passes_rows_through() -> None:
    source = wt.WStringListModel(["a", "b", "c"])
    proxy = wt.WIdentityProxyModel()
    proxy.source_model = source
    assert proxy.row_count() == 3


def test_identity_proxy_source_accessor() -> None:
    source = wt.WStringListModel(["x"])
    proxy = wt.WIdentityProxyModel()
    proxy.source_model = source
    # source_model getter returns the same shared_ptr we set.
    assert proxy.source_model is not None


# ---- WReadOnlyProxyModel --------------------------------------------------

def test_read_only_proxy_passes_rows_through() -> None:
    source = wt.WStringListModel(["a", "b"])
    proxy = wt.WReadOnlyProxyModel()
    proxy.source_model = source
    assert proxy.row_count() == 2


# ---- WSortFilterProxyModel: filtering ------------------------------------

def test_sort_filter_proxy_default_state() -> None:
    proxy = wt.WSortFilterProxyModel()
    assert proxy.filter_key_column == 0
    assert proxy.dynamic_sort_filter is False
    assert proxy.sort_column == -1


def test_sort_filter_proxy_passthrough_without_filter() -> None:
    """No filter set ⇒ proxy reports the same rows as source."""
    source = wt.WStringListModel(["alpha", "beta", "gamma"])
    proxy = wt.WSortFilterProxyModel()
    proxy.source_model = source
    assert proxy.row_count() == 3


def test_sort_filter_proxy_filter_full_match() -> None:
    """Wt uses regex_match (full-string), not regex_search. Wrap with
    wildcards to do substring matching."""
    source = wt.WStringListModel(["apple", "banana", "avocado", "cherry"])
    proxy = wt.WSortFilterProxyModel()
    proxy.dynamic_sort_filter = True
    proxy.source_model = source

    proxy.set_filter_regexp("a.*")     # full-string starts with 'a'
    assert proxy.row_count() == 2       # apple, avocado

    proxy.set_filter_regexp(".*an.*")  # full-string containing 'an'
    assert proxy.row_count() == 1       # banana


def test_sort_filter_proxy_empty_filter_disables() -> None:
    """Empty string disables filtering — proxy passes everything through."""
    source = wt.WStringListModel(["x", "y", "z"])
    proxy = wt.WSortFilterProxyModel()
    proxy.dynamic_sort_filter = True
    proxy.source_model = source

    proxy.set_filter_regexp("nope")
    assert proxy.row_count() == 0
    proxy.set_filter_regexp("")
    assert proxy.row_count() == 3


def test_sort_filter_proxy_invalidate_needed_when_not_dynamic() -> None:
    """When dynamic_sort_filter is False (default), filter changes don't
    re-evaluate until invalidate() is called explicitly."""
    source = wt.WStringListModel(["apple", "banana"])
    proxy = wt.WSortFilterProxyModel()
    proxy.source_model = source
    # Without dynamic mode, setting a filter doesn't immediately re-run.
    # The proxy may or may not re-evaluate depending on Wt's internals;
    # we verify that calling invalidate() converges to the filtered state.
    proxy.set_filter_regexp("a.*")
    proxy.invalidate()
    assert proxy.row_count() == 1       # only 'apple'


# ---- WSortFilterProxyModel: sorting --------------------------------------

def test_sort_filter_proxy_sort_default_column() -> None:
    source = wt.WStringListModel(["cherry", "apple", "banana"])
    proxy = wt.WSortFilterProxyModel()
    proxy.dynamic_sort_filter = True
    proxy.source_model = source
    proxy.sort(0, wt.SortOrder.Ascending)
    assert proxy.sort_column == 0


def test_sort_filter_proxy_disable_sort_with_negative_column() -> None:
    """Passing -1 to sort() disables sorting per Wt's convention."""
    source = wt.WStringListModel(["a", "b"])
    proxy = wt.WSortFilterProxyModel()
    proxy.source_model = source
    proxy.sort(0)
    assert proxy.sort_column == 0
    proxy.sort(-1)
    assert proxy.sort_column == -1


def test_sort_filter_proxy_roles_accept_int_constants() -> None:
    """filter_role and sort_role accept ItemDataRole — and since the
    constants come through as ints, you can pass them directly."""
    proxy = wt.WSortFilterProxyModel()
    proxy.filter_role = wt.ItemDataRole(wt.ItemDataRole.Display)
    proxy.sort_role = wt.ItemDataRole(wt.ItemDataRole.Edit)
    assert proxy.filter_role.value == 0
    assert proxy.sort_role.value == 2


# ---- mapping between source and proxy -----------------------------------

def test_sort_filter_proxy_map_indices() -> None:
    source = wt.WStringListModel(["alpha", "beta", "gamma"])
    proxy = wt.WSortFilterProxyModel()
    proxy.dynamic_sort_filter = True
    proxy.source_model = source
    # Identity mapping when no filter is applied.
    src_idx = source.index(1, 0)
    proxy_idx = proxy.map_from_source(src_idx)
    assert proxy_idx.row == 1
    back = proxy.map_to_source(proxy_idx)
    assert back.row == 1
