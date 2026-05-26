"""Model/view subsystem suite.

Value types (WModelIndex, ItemDataRole) and standalone-instantiable
models (WStringListModel) get full exercise here. Widgets that touch
WApplication::instance() in their constructors (WTableView, WTreeView,
WStandardItemModel — the latter creates an internal root WStandardItem)
are covered only at the binding-surface level; end-to-end render is
exercised by the gallery boot test.
"""

from __future__ import annotations

import pytest
import witty_for_python as wt


# ---- ItemDataRole ---------------------------------------------------------

def test_item_data_role_constants_match_int_values() -> None:
    """Wt declares role constants as `static constexpr const int` in the
    !WT_TARGET_JAVA branch (the one we build). We surface them as Python
    ints, same representation; callers wrap with `ItemDataRole(role)` to
    construct a typed value when an API explicitly wants one."""
    assert wt.ItemDataRole.Display == 0
    assert wt.ItemDataRole.Decoration == 1
    assert wt.ItemDataRole.Edit == 2
    assert wt.ItemDataRole.StyleClass == 3
    assert wt.ItemDataRole.Checked == 4
    assert wt.ItemDataRole.ToolTip == 5
    assert wt.ItemDataRole.Link == 6
    assert wt.ItemDataRole.MimeType == 7
    assert wt.ItemDataRole.Level == 8
    assert wt.ItemDataRole.User == 32


def test_item_data_role_construct_from_int() -> None:
    assert wt.ItemDataRole(42).value == 42


def test_item_data_role_wrap_a_constant() -> None:
    """Wrap an int constant into the typed value for APIs that want one."""
    r = wt.ItemDataRole(wt.ItemDataRole.ToolTip)
    assert r.value == 5
    assert r == wt.ItemDataRole(5)
    assert r != wt.ItemDataRole(wt.ItemDataRole.Edit)


def test_item_data_role_hash_matches_value() -> None:
    """ItemDataRole(5) and ItemDataRole(5) hash to the same int."""
    a = wt.ItemDataRole(5)
    b = wt.ItemDataRole(5)
    assert hash(a) == hash(b)


def test_item_data_role_repr() -> None:
    assert repr(wt.ItemDataRole(7)) == "ItemDataRole(7)"


# ---- WModelIndex ----------------------------------------------------------

def test_default_model_index_is_invalid() -> None:
    """Default-constructed WModelIndex represents the root / sentinel —
    `is_valid` is False, matching Wt's convention."""
    idx = wt.WModelIndex()
    assert idx.is_valid is False


def test_model_index_repr_distinguishes_invalid() -> None:
    assert repr(wt.WModelIndex()) == "WModelIndex(invalid)"


def test_model_index_equality_for_default() -> None:
    """Two default-constructed indexes compare equal (both are the
    invalid root)."""
    assert wt.WModelIndex() == wt.WModelIndex()


def test_model_index_hashable() -> None:
    """Indexes are hashable so callers can stuff them in sets."""
    s = {wt.WModelIndex()}
    s.add(wt.WModelIndex())
    assert len(s) == 1


# ---- WStringListModel -----------------------------------------------------

def test_wstringlistmodel_default_construct() -> None:
    """An empty default-constructed list model has zero rows and zero
    columns (Wt only materialises the single column once at least one
    string is added)."""
    m = wt.WStringListModel()
    assert m.row_count() == 0
    assert m.column_count() == 0
    m.add_string("first")
    assert m.column_count() == 1


def test_wstringlistmodel_construct_from_list() -> None:
    m = wt.WStringListModel(["alpha", "beta", "gamma"])
    assert m.string_list == ["alpha", "beta", "gamma"]
    assert m.row_count() == 3


def test_wstringlistmodel_add_string() -> None:
    m = wt.WStringListModel(["one"])
    m.add_string("two")
    m.add_string("three")
    assert m.string_list == ["one", "two", "three"]


def test_wstringlistmodel_set_string_list_replaces() -> None:
    m = wt.WStringListModel(["a", "b", "c"])
    m.set_string_list(["x", "y"])
    assert m.string_list == ["x", "y"]


def test_wstringlistmodel_inherits_wabstractitemmodel() -> None:
    assert issubclass(wt.WStringListModel, wt.WAbstractListModel)
    assert issubclass(wt.WAbstractListModel, wt.WAbstractItemModel)


# ---- Enum surface ---------------------------------------------------------

def test_selection_behavior_members() -> None:
    assert wt.SelectionBehavior.SelectItems != wt.SelectionBehavior.SelectRows


def test_sort_order_members() -> None:
    assert wt.SortOrder.Ascending != wt.SortOrder.Descending


def test_scroll_hint_members() -> None:
    members = ("EnsureVisible", "PositionAtTop", "PositionAtBottom",
               "PositionAtCenter", "PositionAtLeft", "PositionAtRight",
               "NoScroll")
    for name in members:
        assert hasattr(wt.ScrollHint, name), f"missing ScrollHint.{name}"


# ---- ModelIndexMouseSignal class binding ---------------------------------

def test_model_index_mouse_signal_exposed() -> None:
    assert wt.ModelIndexMouseSignal is not None
    assert hasattr(wt.ModelIndexMouseSignal, "connect")
    assert hasattr(wt.ModelIndexMouseSignal, "disconnect_all_slots")


# ---- Widget class surface (no construction — needs session) --------------

@pytest.mark.parametrize("cls,base", [
    (wt.WStandardItemModel, wt.WAbstractItemModel),
    (wt.WStringListModel,   wt.WAbstractListModel),
    (wt.WTableView,         wt.WAbstractItemView),
    (wt.WTreeView,          wt.WAbstractItemView),
    (wt.WAbstractItemView,  wt.WWidget),
])
def test_modelview_class_inheritance(cls: type, base: type) -> None:
    assert issubclass(cls, base), f"{cls.__name__} must extend {base.__name__}"


@pytest.mark.parametrize("cls,attr", [
    (wt.WAbstractItemModel, "row_count"),
    (wt.WAbstractItemModel, "column_count"),
    (wt.WAbstractItemModel, "has_children"),
    (wt.WAbstractItemModel, "index"),
    (wt.WAbstractItemModel, "display_data"),
    (wt.WAbstractItemModel, "set_header_data"),
    (wt.WStandardItem,      "text"),
    (wt.WStandardItem,      "icon"),
    (wt.WStandardItem,      "style_class"),
    (wt.WStandardItem,      "tool_tip"),
    (wt.WStandardItem,      "set_link"),
    (wt.WStandardItem,      "checkable"),
    (wt.WStandardItem,      "checked"),
    (wt.WStandardItem,      "editable"),
    (wt.WStandardItem,      "append_row"),
    (wt.WStandardItem,      "child"),
    (wt.WStandardItem,      "parent"),
    (wt.WStandardItemModel, "clear"),
    (wt.WStandardItemModel, "invisible_root_item"),
    (wt.WStandardItemModel, "item"),
    (wt.WStandardItemModel, "set_item"),
    (wt.WStandardItemModel, "append_row"),
    (wt.WAbstractItemView,  "model"),
    (wt.WAbstractItemView,  "sort_by_column"),
    (wt.WAbstractItemView,  "sorting_enabled"),
    (wt.WAbstractItemView,  "column_resize_enabled"),
    (wt.WAbstractItemView,  "selection_behavior"),
    (wt.WAbstractItemView,  "selection_mode"),
    (wt.WAbstractItemView,  "clicked"),
    (wt.WAbstractItemView,  "double_clicked"),
    (wt.WAbstractItemView,  "selection_changed"),
    (wt.WTableView,         "scroll_to"),
    (wt.WTreeView,          "set_expanded"),
    (wt.WTreeView,          "expand"),
    (wt.WTreeView,          "collapse"),
    (wt.WTreeView,          "collapse_all"),
    (wt.WTreeView,          "expand_to_depth"),
    (wt.WTreeView,          "root_is_decorated"),
])
def test_modelview_attribute_present(cls: type, attr: str) -> None:
    assert hasattr(cls, attr), f"{cls.__name__} missing: {attr}"


# ---- WSuggestionPopup.set_model surfaced -----------------------------------

def test_suggestion_popup_picks_up_model_setter() -> None:
    """Previously skipped because WAbstractItemModel wasn't bound. Now
    that it is, WSuggestionPopup.set_model lets callers swap the default
    WStringListModel for a richer one (sortable / filterable)."""
    assert hasattr(wt.WSuggestionPopup, "set_model")
    assert hasattr(wt.WSuggestionPopup, "model")
