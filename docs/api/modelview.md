# Models, Views & Tables

> Wt's MVC machinery: WStandardItemModel and friends for the data side, WTableView / WTreeView for the views, proxy models for sorting and filtering, and the simpler hand-built WTable.

**Classes in this section:**

- [`ItemDataRole`](#ItemDataRole)
- [`WModelIndex`](#WModelIndex)
- [`ModelIndexMouseSignal`](#ModelIndexMouseSignal)
- [`WAbstractItemModel`](#WAbstractItemModel)
- [`WAbstractListModel`](#WAbstractListModel)
- [`WStringListModel`](#WStringListModel)
- [`WStandardItem`](#WStandardItem)
- [`WStandardItemModel`](#WStandardItemModel)
- [`SelectionBehavior`](#SelectionBehavior)
- [`SortOrder`](#SortOrder)
- [`ScrollHint`](#ScrollHint)
- [`WAbstractItemView`](#WAbstractItemView)
- [`WTableView`](#WTableView)
- [`WTreeView`](#WTreeView)
- [`WAbstractProxyModel`](#WAbstractProxyModel)
- [`WIdentityProxyModel`](#WIdentityProxyModel)
- [`WReadOnlyProxyModel`](#WReadOnlyProxyModel)
- [`WSortFilterProxyModel`](#WSortFilterProxyModel)
- [`WTableCell`](#WTableCell)
- [`WTableRow`](#WTableRow)
- [`WTableColumn`](#WTableColumn)
- [`WTable`](#WTable)

---

### ItemDataRole {#ItemDataRole}

Identifies which facet of a cell a view is asking for. Models
store more than just the displayed text per cell — they can
also hold edit values, decorations (icons), tooltips, style
classes, hyperlinks, checkbox state, and so on. Each is a
different ItemDataRole.

    text = model.display_data(model.index(0, 0))
    role = wt.ItemDataRole(wt.ItemDataRole.Display)

The standard roles are exposed as plain int class attributes
(Display, Edit, Decoration, ToolTip, StyleClass, Checked, Link,
…). Wrap one in ItemDataRole(role) when you need the typed
value to pass into a Wt API.

**Constructors**

- `__init__(self, role: int) -> None`
  Construct a role from its integer value. Use the class
  attribute constants (`ItemDataRole.Display`, etc.) rather
  than raw numbers.

**Properties**

- `value: int` *(read-only)*
  The underlying integer role identifier.

**Methods**

- `__eq__(self, arg: ItemDataRole, /) -> bool`

- `__lt__(self, arg: ItemDataRole, /) -> bool`

- `__hash__(self) -> int`

**Dunder methods**

- `__repr__(self) -> str`

### WModelIndex {#WModelIndex}

Lightweight value handle to a single cell of a model, identified
by (row, column, parent). Returned by model methods like
`index(row, col)` and used as input wherever a view or proxy
needs to refer to a cell.

    idx = model.index(2, 0)
    text = model.display_data(idx)

The default-constructed (and the one returned by `parent()` on
a top-level row) is the sentinel 'invalid' index — check
`is_valid` before using it. Comparable and hashable, so it works
as a dict key or set member.

**Constructors**

- `__init__(self) -> None`
  Construct the invalid sentinel index — the same value used
  to mean 'no parent / top level' wherever a parent index is
  expected.

**Properties**

- `row: int` *(read-only)*
  0-based row of the cell this index addresses.

- `column: int` *(read-only)*
  0-based column of the cell this index addresses.

- `is_valid: bool` *(read-only)*
  False for the root / sentinel index returned by parent() on a top-level item.

- `internal_id: int` *(read-only)*
  Model-defined opaque id distinguishing tree nodes that share (row, column). Stable for the lifetime of the model item.

**Methods**

- `parent(self) -> WModelIndex`
  Index of this cell's parent — invalid for top-level rows.

- `child(self, row: int, column: int) -> WModelIndex`
  Child cell at (row, column) of this index. For non-tree models, only the top-level index has children.

- `__eq__(self, arg: WModelIndex, /) -> bool`

- `__lt__(self, arg: WModelIndex, /) -> bool`

- `__hash__(self) -> int`

**Dunder methods**

- `__repr__(self) -> str`

### ModelIndexMouseSignal {#ModelIndexMouseSignal}

Two-argument signal fired by item views on click / double-click,
carrying the WModelIndex of the affected cell and the underlying
WMouseEvent (buttons, modifiers, coordinates).

    def on_click(index, event):
        if index.is_valid:
            print('clicked row', index.row)
    table_view.clicked.connect(on_click)

**Methods**

- `connect(self, callable: Callable) -> Connection`
  Subscribe `callable` to the signal. The callback receives
  (WModelIndex, WMouseEvent). Returns a Connection — call
  `.disconnect()` on it to unsubscribe.

- `disconnect_all_slots(self) -> None`
  Drop every Python subscriber from this signal.

### WAbstractItemModel {#WAbstractItemModel}

*Inherits:* `WObject`

Abstract base for everything an item view can render. Models
expose data as a tree of cells addressed by (row, column,
parent); flat tables are the special case where no row has
children. Views (WTableView, WTreeView, …) attach via
`view.model = some_model` and pull cells through `display_data`
and the role-typed accessors.

Not directly constructible from Python — instantiate a concrete
subclass (WStandardItemModel, WStringListModel) or wrap one in a
proxy. Writes typically go through the concrete subclass
(e.g. WStandardItem mutators); this base only exposes the read
surface and header mutation.

**Methods**

- `row_count(self, parent: WModelIndex = ...) -> int`
  Number of rows under `parent` (top-level when parent is the default invalid index).

- `column_count(self, parent: WModelIndex = ...) -> int`
  Number of columns under `parent` (top-level when parent is
  the default invalid index). For a flat table this is the
  number of columns of the table itself.

- `has_children(self, index: WModelIndex) -> bool`
  True if `index` has any children — i.e. it expands into a
  subtree. Always False for flat list/table models.

- `index(self, row: int, column: int, parent: WModelIndex = ...) -> WModelIndex`
  Build a WModelIndex addressing the cell at (row, column)
  under `parent` (top-level when parent is the default invalid
  index). Returns an invalid index if the coordinates are out
  of range.

- `parent_of(self, index: WModelIndex) -> WModelIndex`
  Parent index of `index`. Invalid for top-level rows. Same
  value as `index.parent()`; provided as a method on the model
  to mirror the C++ API (renamed `parent_of` to avoid colliding
  with Python's `parent` convention elsewhere).

- `display_data(self, index: WModelIndex) -> object`
  The cell's Display-role data stringified — the text a view
  would render for it. Returns None for empty cells. Avoids
  having to deal with the cpp17::any-typed `data()` accessor
  for the common 'just show me what's in the cell' case.

- `set_header_data(self, section: int, value: object) -> bool`
  Set a header label. Accepts str/int/float/bool — anything else is stringified via Python repr.

### WAbstractListModel {#WAbstractListModel}

*Inherits:* `WAbstractItemModel`

Intermediate base for single-column list-shaped models — flat,
no children. Mostly bound so WStringListModel can declare it as
its base; users typically interact with the concrete subclass.

### WStringListModel {#WStringListModel}

*Inherits:* `WAbstractListModel`

Single-column model whose cells hold strings. Pair with a
WTableView or feed it to a combo-box-style widget; the simplest
way to back a UI list with Python data.

    model = wt.WStringListModel(['apples', 'pears', 'plums'])
    view = container.add_widget(wt.WTableView())
    view.model = model
    model.add_string('quinces')

**Constructors**

- `__init__(self) -> None`
  Construct an empty string-list model.

- `__init__(self, strings: Sequence[str]) -> None`
  Construct a model populated with `strings` (one row each,
  in order).

**Properties**

- `string_list: list[str]` *(read-only)*
  The current list of strings as a Python list of WString.

**Methods**

- `set_string_list(self, strings: Sequence[str]) -> None`
  Replace every row with `strings`. Attached views are
  notified and redraw.

- `add_string(self, string: str) -> None`
  Append a single string as a new row at the end.

### WStandardItem {#WStandardItem}

Mutable cell value used by WStandardItemModel. Each cell of a
table — or each node of a tree — is one WStandardItem holding
the display text, optional decoration/styling/tooltip, link,
checkbox state, and any child rows/columns for tree mode.

    item = wt.WStandardItem('Alice')
    item.tool_tip = 'Project lead'
    model.set_item(0, 0, item)
    # mutate in place — the attached view sees the update:
    item.text = 'Alice (PL)'

Items own their children: `set_child` / `append_row` /
`set_item` transfer the Python wrapper into Wt's tree (the
wrapper is re-armed as a non-owning alias, so the same Python
object keeps working but won't double-free).

**Constructors**

- `__init__(self) -> None`
  Construct an empty item with no text.

- `__init__(self, text: str) -> None`
  Construct an item displaying `text`.

**Properties**

- `text: str` *(read/write)*
  The cell's displayed text (the Display-role value).
  Assigning updates attached views on the next round-trip.

- `icon: str` *(read/write)*
  URL of a small icon shown beside the text (when the view's delegate honours ItemDataRole.Decoration).

- `style_class: str` *(read/write)*
  CSS class applied to this cell's rendered element. Useful
  for per-row colouring or highlighting.

- `tool_tip: str` *(read/write)*
  Hover-tooltip text for this cell.

- `checkable: bool` *(read/write)*
  Whether the cell renders with a checkbox. Set True to show
  one; `checked` then controls its state.

- `checked: bool` *(read/write)*
  Checkbox state. Only meaningful when `checkable` is True.

- `tristate: bool` *(read/write)*
  Whether the checkbox can hold an indeterminate state in
  addition to checked/unchecked.

- `editable: bool` *(read/write)*
  Whether the user can edit the cell in place via the view's
  edit delegate.

- `has_children: bool` *(read-only)*
  True if this item has any child rows/columns (i.e. forms a
  subtree).

- `row_count: int` *(read-only)*
  Number of child rows under this item.

- `column_count: int` *(read-only)*
  Number of child columns under this item.

**Methods**

- `set_link(self, link: WLink) -> None`
  Attach a WLink to the cell, so the rendered text becomes
  clickable and navigates to the link's URL or internal path.

- `set_row_count(self, rows: int) -> None`
  Resize the children to have exactly `rows` rows. New rows
  are filled with empty items; excess rows are dropped.

- `set_column_count(self, columns: int) -> None`
  Resize the children to have exactly `columns` columns. New
  columns are filled with empty items; excess are dropped.

- `append_row(self, items: list[WStandardItem]) -> None`
  Append a single child row. Each item's Python wrapper stays usable after the call (re-armed as a non-owning alias).

- `append_column(self, items: list[WStandardItem]) -> None`
  Append a single child column. Each item's Python wrapper
  stays usable after the call (re-armed as a non-owning alias).

- `insert_rows(self, row: int, count: int) -> None`
  Insert `count` empty rows starting at `row`. Existing rows
  at or after that position shift down.

- `insert_columns(self, column: int, count: int) -> None`
  Insert `count` empty columns starting at `column`. Existing
  columns at or after that position shift right.

- `child(self, row: int, column: int = 0) -> WStandardItem`
  The child item at (row, column) — None if absent.

- `parent(self) -> WStandardItem`
  Parent item — None for items in invisibleRootItem().

### WStandardItemModel {#WStandardItemModel}

*Inherits:* `WAbstractItemModel`

General-purpose model backed by a grid (or tree) of
WStandardItem cells. The standard pick when you want to populate
a WTableView or WTreeView from Python data without writing your
own model subclass.

    model = wt.WStandardItemModel(0, 2)
    model.set_header_data(0, 'Name')
    model.set_header_data(1, 'Score')
    model.append_row([wt.WStandardItem('Alice'),
                      wt.WStandardItem('42')])
    view = container.add_widget(wt.WTableView())
    view.model = model

Mutate cells in place by reaching `model.item(row, col)` and
assigning to its `text`, `checked`, etc. — attached views see
the change on the next round-trip.

**Constructors**

- `__init__(self) -> None`
  Construct an empty 0-by-0 model.

- `__init__(self, rows: int, columns: int) -> None`
  Construct a model pre-sized to `rows` x `columns`, with
  empty WStandardItem cells in every position.

**Properties**

- `invisible_root_item: WStandardItem` *(read-only)*
  The internal root item. Manipulate it directly for advanced tree construction; for flat tables prefer model.append_row.

**Methods**

- `clear(self) -> None`
  Drop every item; rowCount and columnCount go to 0.

- `index_from_item(self, item: WStandardItem) -> WModelIndex`
  WModelIndex of the cell holding `item`, or an invalid index
  if the item is not part of this model.

- `item_from_index(self, index: WModelIndex) -> WStandardItem`
  WStandardItem at `index` — the inverse of `index_from_item`.
  Returns None for the invalid index or out-of-range positions.

- `item(self, row: int, column: int = 0) -> WStandardItem`
  Top-level item at (row, column).

- `set_item(self, row: int, column: int, item: WStandardItem) -> None`
  Place an item at (row, column). Transfers ownership; the Python wrapper is re-armed as a non-owning alias.

- `append_row(self, items: list[WStandardItem]) -> None`
  Append a row of top-level items. The list length should
  match `column_count`; transfers ownership of each item, the
  Python wrappers stay usable as non-owning aliases.

- `append_column(self, items: list[WStandardItem]) -> None`
  Append a column of top-level items. The list length should
  match `row_count`; same ownership transfer as append_row.

### SelectionBehavior {#SelectionBehavior}

*Inherits:* `enum.Enum`

Whether item-view selection operates on individual cells or
whole rows.

### SortOrder {#SortOrder}

*Inherits:* `enum.Enum`

Sort direction for column sorts on item views and sort/filter
proxy models.

### ScrollHint {#ScrollHint}

*Inherits:* `enum.Enum`

How a view should align a target cell within its viewport when
asked to scroll to it.

### WAbstractItemView {#WAbstractItemView}

*Inherits:* `WWidget`

Base widget for views that render a WAbstractItemModel. WTableView
and WTreeView both derive from this; the shared surface covers
model attachment, root-index navigation, selection, sorting, and
the click signals.

    view = container.add_widget(wt.WTableView())
    view.model = model
    view.sorting_enabled = True
    view.selection_behavior = wt.SelectionBehavior.SelectRows
    view.clicked.connect(lambda idx, ev: handle_click(idx))

**Properties**

- `model: WAbstractItemModel` *(read/write)*
  The attached model (shared_ptr<WAbstractItemModel>). Assign
  a concrete model — or a proxy wrapping one — to populate the
  view; the view re-renders on changes the model emits.

- `root_index: WModelIndex` *(read-only)*
  Current root WModelIndex — the node whose children the view
  is showing as top-level rows.

- `clicked: ModelIndexMouseSignal` *(read-only)*
  ModelIndexMouseSignal fired when the user clicks a
  cell. Callbacks receive (WModelIndex, WMouseEvent).

- `double_clicked: ModelIndexMouseSignal` *(read-only)*
  ModelIndexMouseSignal fired on double-click. Same
  payload as `clicked`.

- `selection_changed: Signal` *(read-only)*
  No-arg signal fired when the selection changes —
  use to refresh detail panes, enable/disable action
  buttons, etc.

- `sorting_enabled: bool` *(read/write)*
  Whether the column headers act as sort toggles. The model
  (or a wrapping sort/filter proxy) must implement sort() for
  the user clicks to have an effect.

- `column_resize_enabled: bool` *(read/write)*
  Whether the user can drag column dividers to resize columns.

- `selection_behavior: SelectionBehavior` *(read/write)*
  Whether selection targets individual cells or whole rows
  (a SelectionBehavior value).

- `selection_mode: SelectionMode` *(read/write)*
  Single vs. multi-select, etc. (a SelectionMode value).

**Methods**

- `set_root_index(self, root_index: WModelIndex) -> None`
  Show the children of `root_index` as the view's top-level
  rows. Useful for drilling into a sub-tree of a tree model;
  pass an invalid WModelIndex to reset to showing everything.

- `clear_selection(self) -> None`
  Drop every selected cell/row.

- `is_selected(self, index: WModelIndex) -> bool`
  True if `index` is currently part of the selection.

- `sort_by_column(self, column: int, order: SortOrder) -> None`
  Sort visible rows by `column` in the given SortOrder. The
  underlying model must support sort() for this to take
  effect — e.g. when fronted by a WSortFilterProxyModel.

- `set_column_width(self, column: int, width: WLength) -> None`
  Set the rendered width of `column` to the given WLength.

### WTableView {#WTableView}

*Inherits:* `WAbstractItemView`

Model-driven flat table view. Renders the rows directly under
its root index as a scrollable grid, one row of cells per row
of the model. Use with a WStandardItemModel, a WStringListModel,
or any custom WAbstractItemModel.

    view = container.add_widget(wt.WTableView())
    view.model = model
    view.sorting_enabled = True
    view.clicked.connect(on_row_click)

**Constructors**

- `__init__(self) -> None`
  Construct an empty table view. Assign `model` to populate
  it.

**Methods**

- `scroll_to(self, index: WModelIndex, hint: ScrollHint = ScrollHint.EnsureVisible) -> None`
  Scroll so the cell at `index` is positioned per `hint`.
  The default is to bring it into view if it isn't already.

### WTreeView {#WTreeView}

*Inherits:* `WAbstractItemView`

Model-driven tree view. Renders rows hierarchically with
expand/collapse toggles for any item whose `has_children` is
true. Suits hierarchical data: directory trees, org charts,
category browsers.

    view = container.add_widget(wt.WTreeView())
    view.model = standard_model     # any model whose items have children
    view.expand_to_depth(2)
    view.clicked.connect(on_node_click)

**Constructors**

- `__init__(self) -> None`
  Construct an empty tree view. Assign `model` to populate
  it.

**Properties**

- `root_is_decorated: bool` *(read/write)*
  Whether top-level rows show an expand/collapse decoration
  (arrow). Turn off to render top-level rows like a flat list
  with the subtrees hanging off them.

**Methods**

- `set_expanded(self, index: WModelIndex, expanded: bool) -> None`
  Expand or collapse the subtree rooted at `index`.

- `is_expanded(self, index: WModelIndex) -> bool`
  True if the subtree at `index` is currently expanded.

- `expand(self, index: WModelIndex) -> None`
  Expand the subtree at `index`. Equivalent to
  `set_expanded(index, True)`.

- `collapse(self, index: WModelIndex) -> None`
  Collapse the subtree at `index`. Equivalent to
  `set_expanded(index, False)`.

- `collapse_all(self) -> None`
  Collapse every expanded node; only the top-level rows
  remain visible.

- `expand_to_depth(self, depth: int) -> None`
  Expand every node whose distance from the root is less
  than `depth`. Depth 0 means everything stays collapsed;
  depth 1 expands the root's immediate children, and so on.

### WAbstractProxyModel {#WAbstractProxyModel}

*Inherits:* `WAbstractItemModel`

Base class for models that wrap another model and present a
transformed view of it. Sort/filter, read-only-isation, identity
pass-through and similar adapters all derive from this. Set the
underlying model via `source_model`, then attach a view to the
PROXY (not the source) so it sees the transformed rows.

    proxy = wt.WSortFilterProxyModel()
    proxy.source_model = base_model
    table_view.model = proxy

Use `map_from_source` / `map_to_source` to translate WModelIndex
values between the two coordinate systems.

**Properties**

- `source_model: WAbstractItemModel` *(read/write)*
  The wrapped model. Setting it disconnects from the previous
  source and rewires the proxy.

**Methods**

- `map_from_source(self, source_index: WModelIndex) -> WModelIndex`
  Translate a source-model index to the proxy's coordinate
  system (sorted/filtered/etc. position). Returns an invalid
  index if the source row is filtered out.

- `map_to_source(self, proxy_index: WModelIndex) -> WModelIndex`
  Translate a proxy index back to the source model. Required
  when handing a clicked index back to source-specific logic.

### WIdentityProxyModel {#WIdentityProxyModel}

*Inherits:* `WAbstractProxyModel`

Proxy that forwards every call to the source model unchanged.
Useful as a starting point for a custom subclass that only
tweaks one or two methods (a data-role rewriter, for instance),
or as a placeholder when an API requires a proxy but no
transformation is needed yet.

**Constructors**

- `__init__(self) -> None`
  Construct an empty identity proxy; assign `source_model`
  to wire it up.

### WReadOnlyProxyModel {#WReadOnlyProxyModel}

*Inherits:* `WAbstractProxyModel`

Proxy that forwards reads to the source but refuses every
mutation (setData, setHeaderData, insertRows, removeRows, …).
Cheap way to hand a model to a view that must not be allowed to
edit it — e.g. a preview pane that shares its underlying data
with an editable master view.

    readonly = wt.WReadOnlyProxyModel()
    readonly.source_model = shared_model
    preview.model = readonly

**Constructors**

- `__init__(self) -> None`
  Construct an empty read-only proxy; assign `source_model`
  to wire it up.

### WSortFilterProxyModel {#WSortFilterProxyModel}

*Inherits:* `WAbstractProxyModel`

Proxy that hides rows whose `filter_key_column` value does not
match a regex, and optionally re-orders the rows it does keep.
Operates on the rows directly under whatever root index the
view is showing.

    proxy = wt.WSortFilterProxyModel()
    proxy.source_model = people_model
    proxy.filter_key_column = 1                 # surname column
    proxy.set_filter_regexp('.*smith.*')
    proxy.dynamic_sort_filter = True
    proxy.sort(0, wt.SortOrder.Ascending)       # by first name
    table_view.model = proxy

The filter regex is implemented with std::regex (ECMAScript
flavour) and applied as a full-string match — see
`set_filter_regexp` for details.

**Constructors**

- `__init__(self) -> None`
  Construct an empty proxy. Assign `source_model`, then set
  filter/sort parameters as needed.

**Properties**

- `filter_key_column: int` *(read/write)*
  Column index in the source model whose values are matched
  against the filter regex. Default 0.

- `filter_role: ItemDataRole` *(read/write)*
  Data role read from the filter column before matching against
  the regex. Default Display.

- `sort_role: ItemDataRole` *(read/write)*
  Data role read when comparing rows during sort. Default
  Display.

- `sort_column: int` *(read-only)*
  Current sort column, or -1 when sort() has not been called.

- `sort_order: SortOrder` *(read-only)*
  Current SortOrder in effect (Ascending or Descending).

- `dynamic_sort_filter: bool` *(read/write)*
  When True, the proxy re-runs filter + sort whenever the
  source model changes. False (default) requires an explicit
  invalidate() call after modifications.

**Methods**

- `set_filter_regexp(self, pattern: str) -> None`
  Set the regex pattern applied to the filter column. Empty
  string disables filtering. Wt uses std::regex_match (FULL-
  STRING match, not substring search), ECMAScript flavour — to
  search for a substring, wrap with wildcards: `.*foo.*`.
  Re-runs the filter immediately when `dynamic_sort_filter` is
  True; otherwise call `invalidate()` afterward.

- `invalidate(self) -> None`
  Force a re-evaluation of filter + sort against the current
  source data. Needed after source mutations when
  dynamic_sort_filter is False.

- `sort(self, column: int, order: SortOrder = SortOrder.Ascending) -> None`
  Sort by the given column. -1 disables sorting.

### WTableCell {#WTableCell}

*Inherits:* `WContainerWidget`

One cell of a WTable, addressed by (row, column). Inherits
WContainerWidget — fill it with any widgets you like, the same
way you'd populate any other container.

    cell = table.element_at(0, 0)
    cell.add_widget(wt.WText('Name'))

Spans cover adjacent cells: setting `row_span = 2` makes the
cell occupy two rows starting at this position.

**Properties**

- `row: int` *(read-only)*
  0-based row index of this cell within its WTable.

- `column: int` *(read-only)*
  0-based column index of this cell within its WTable.

- `row_span: int` *(read/write)*
  Number of rows the cell occupies (HTML `rowspan`). Default 1.

- `column_span: int` *(read/write)*
  Number of columns the cell occupies (HTML `colspan`).
  Default 1.

### WTableRow {#WTableRow}

Handle to a row of a WTable. Obtained from `WTable.insert_row`;
lets you reach the row's cells without going through the parent
table.

**Properties**

- `row_num: int` *(read-only)*
  0-based index of this row within its WTable.

**Methods**

- `element_at(self, column: int) -> WTableCell`
  Return the WTableCell at `column` in this row. Same cell
  you'd get from `table.element_at(self.row_num, column)`.

### WTableColumn {#WTableColumn}

Handle to a column of a WTable. Obtained from
`WTable.insert_column` — chiefly useful for setting column-wide
styling or width.

**Properties**

- `column_num: int` *(read-only)*
  0-based index of this column within its WTable.

### WTable {#WTable}

*Inherits:* `WInteractWidget`

A plain HTML `<table>` widget. Cells grow on demand: ask for
`element_at(r, c)` and any missing rows/columns are auto-created.

    table = container.add_widget(wt.WTable())
    table.element_at(0, 0).add_widget(wt.WText('Header'))
    table.element_at(1, 0).add_widget(wt.WText('Row 1'))

Use a WTableView with a model when the data is dynamic or large
enough that auto-growing cells would be wasteful. WTable is the
right pick for hand-laid-out small tables.

**Constructors**

- `__init__(self) -> None`
  Construct an empty 0-by-0 table.

**Properties**

- `row_count: int` *(read-only)*
  Total number of rows currently in the table.

- `column_count: int` *(read-only)*
  Total number of columns currently in the table.

**Methods**

- `element_at(self, row: int, column: int) -> WTableCell`
  Return the WTableCell at (row, column), creating empty
  rows/columns up to that position if they do not exist yet.
  Then populate it like any other container:

      table.element_at(2, 3).add_widget(wt.WText('cell'))

- `clear(self) -> None`
  Remove every row and column. After this, `row_count` and
  `column_count` are both 0 and previously-returned cell
  references are dangling.

- `remove_row(self, row: int) -> WTableRow`
  Remove the row at the given index. Subsequent rows shift up
  by one; any cached WTableCell pointers for the removed row
  become invalid.

- `remove_column(self, column: int) -> WTableColumn`
  Remove the column at the given index. Subsequent columns
  shift left by one.

- `insert_row(self, row: int) -> WTableRow`
  Insert a fresh empty row at index `row` (existing rows
  shift down). Returns the WTableRow handle for the new row.

- `insert_column(self, column: int) -> WTableColumn`
  Insert a fresh empty column at index `column` (existing
  columns shift right). Returns the WTableColumn handle.
