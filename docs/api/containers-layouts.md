# Containers & Layouts

> Container widgets and the layout managers that arrange their children — boxes, grids, borders, fit-to-parent.

**Classes in this section:**

- [`WContainerWidget`](#WContainerWidget)
- [`WLayout`](#WLayout)
- [`LayoutDirection`](#LayoutDirection)
- [`WBoxLayout`](#WBoxLayout)
- [`WHBoxLayout`](#WHBoxLayout)
- [`WVBoxLayout`](#WVBoxLayout)
- [`WGridLayout`](#WGridLayout)
- [`LayoutPosition`](#LayoutPosition)
- [`WBorderLayout`](#WBorderLayout)
- [`WFitLayout`](#WFitLayout)

---

### WContainerWidget {#WContainerWidget}

*Inherits:* `WInteractWidget`

A `<div>`-style box that holds child widgets in document order.
The default container for composing UIs — every Wt application
starts with a root WContainerWidget (`app.root`) and adds
widgets into it.

    page = app.root
    page.add_widget(wt.WText('Welcome.'))
    page.add_widget(wt.WPushButton('Click me')).clicked.connect(say_hi)

Children render stacked top-to-bottom unless a `layout` is
installed via `set_layout` (then the layout class decides). The
container owns its children: when it's destroyed, every widget
added to it is destroyed too.

**Constructors**

- `__init__(self) -> None`
  Construct an empty container with no children and no layout.

**Properties**

- `count: int` *(read-only)*
  Number of direct child widgets currently in the container.

**Methods**

- `add_widget(self, text: str) -> WText`
  Convenience for `add_widget(WText(text))`. Wraps `text` in
  a freshly-constructed WText and adds it; returns a
  non-owning handle to the WText so you can mutate it later.

      label = container.add_widget('Loading…')
      # later, after data arrives:
      label.text = 'Loaded 42 rows.'

  If you need any setting on the WText other than its text
  (e.g. CSS class, format), build the WText yourself and use
  the widget-taking overload below.

- `add_widget(self, widget: _T_Widget) -> _T_Widget`
  Transfer ownership of `widget` to this container and
  return the same Python wrapper (subtype preserved), re-armed
  as a non-owning alias. Chain straight off the return:

      container.add_widget(wt.WPushButton('Save')).clicked.connect(save)

  Or keep the typed handle for later mutation:

      edit = container.add_widget(wt.WLineEdit())
      edit.placeholder = 'Email…'

  From the moment of transfer, the container is responsible
  for destroying the widget — garbage-collecting the Python
  wrapper does NOT delete the C++ object (Wt's widget tree
  does, on container teardown).

- `add_widgets(self, texts: Sequence[str]) -> list[WText]`
  Bulk version of `add_widget(str)`. Wraps each string in a
  WText and adds them in order. Returns the list of handles.

      rows = container.add_widgets(['Apples', 'Pears', 'Plums'])
      rows[0].text = 'Granny Smith'           # mutate one

- `add_widgets(self, widgets: list[_T_Widget]) -> list[_T_Widget]`
  Bulk version of `add_widget(widget)`. Transfers ownership
  of each widget to this container in order. Returns the
  same Python wrappers, each re-armed as a non-owning alias
  (identity and subtype preserved).

      items = [wt.WPushButton(label) for label in choices]
      container.add_widgets(items)            # one round-trip
      for btn in items:                       # still typed + usable
          btn.clicked.connect(lambda b=btn: pick(b.text))

- `clear(self) -> None`
  Remove and destroy every child widget. After this returns
  the container has no children and `count` is 0; any Python
  wrappers still referencing the removed widgets are now
  dangling — calling methods on them raises.

- `widget(self, index: int) -> WWidget`
  Return a non-owning handle to the child at position
  `index` (0-based). Useful for inspecting children when
  you didn't keep handles from `add_widget`. The static
  type is WWidget; use `isinstance` to narrow.

- `remove_widget(self, widget: WWidget) -> WWidget`
  Detach `widget` from this container and return ownership
  to Python. The widget is NOT destroyed — it's left dangling
  until either the returned reference is dropped (Python
  destroys it) or it's re-attached to a different container
  via `add_widget`.

      moved = src.remove_widget(some_btn)
      dst.add_widget(moved)                  # re-parented

- `set_layout(self, layout: WLayout) -> None`
  Install `layout` as the container's layout manager. Once
  set, the layout (not the container's add_widget order)
  decides how children are positioned — use the layout's own
  add_widget / add_item methods after this. Same ownership
  transfer as add_widget: the container takes the C++ object,
  the Python wrapper is re-armed as a non-owning alias.

      layout = wt.WVBoxLayout()
      container.set_layout(layout)
      layout.add_widget(wt.WText('top'))
      layout.add_widget(wt.WText('bottom'))

### WLayout {#WLayout}

Abstract base of every layout manager. A layout is installed
into a WContainerWidget via `container.set_layout(layout)` and
from then on decides how the container's children are sized
and positioned — the container's own `add_widget` order is
ignored. Use the concrete subclasses (WHBoxLayout, WVBoxLayout,
WGridLayout, WBorderLayout, WFitLayout) instead of this type.

### LayoutDirection {#LayoutDirection}

*Inherits:* `enum.Enum`

Direction in which a WBoxLayout places its children — horizontal
(LeftToRight / RightToLeft) or vertical (TopToBottom /
BottomToTop).

### WBoxLayout {#WBoxLayout}

*Inherits:* `WLayout`

Linear layout — places children in a single row or column
depending on its LayoutDirection. The two thin subclasses
WHBoxLayout and WVBoxLayout are usually more convenient.

Each child has a `stretch` weight that determines how
extra space is divided up; stretch 0 means natural size, and
higher values get a proportionally larger share.

**Constructors**

- `__init__(self, direction: LayoutDirection) -> None`
  Construct a box layout with the given LayoutDirection.

**Methods**

- `add_widget(self, widget: _T_Widget, stretch: int = 0) -> _T_Widget`
  Append `widget` to the layout with the given stretch
  weight. Takes ownership; the Python wrapper is re-armed as
  a non-owning alias and returned for fluent chaining:

      layout.add_widget(wt.WPushButton('Go')).clicked.connect(go)

- `add_widgets(self, widgets: list[_T_Widget]) -> list[_T_Widget]`
  Bulk version of `add_widget` with stretch=0 for every
  child. Use the single-call form if you need per-widget
  stretch values.

- `add_stretch(self, stretch: int = 1) -> None`
  Insert a flexible spacer with the given stretch weight.
  Useful for pushing the next widget to one end of the row
  or column.

- `add_spacing(self, size_px: float) -> None`
  Insert a fixed-size gap of `size_px` pixels.

### WHBoxLayout {#WHBoxLayout}

*Inherits:* `WBoxLayout`

Horizontal box layout — children are arranged left-to-right.
Equivalent to `WBoxLayout(LayoutDirection.LeftToRight)`.

    row = wt.WHBoxLayout()
    container.set_layout(row)
    row.add_widget(wt.WText('Label:'))
    row.add_widget(wt.WLineEdit(), 1)

**Constructors**

- `__init__(self) -> None`
  Construct an empty horizontal box layout.

### WVBoxLayout {#WVBoxLayout}

*Inherits:* `WBoxLayout`

Vertical box layout — children are arranged top-to-bottom.
Equivalent to `WBoxLayout(LayoutDirection.TopToBottom)`.

    col = wt.WVBoxLayout()
    container.set_layout(col)
    col.add_widget(wt.WText('Header'))
    col.add_widget(wt.WText('Body'), 1)

**Constructors**

- `__init__(self) -> None`
  Construct an empty vertical box layout.

### WGridLayout {#WGridLayout}

*Inherits:* `WLayout`

Two-dimensional grid layout — children sit at explicit (row,
column) coordinates and can span multiple cells. Rows and
columns auto-size from their contents unless given an explicit
stretch weight.

    grid = wt.WGridLayout()
    container.set_layout(grid)
    grid.add_widget(wt.WText('Name:'),  0, 0)
    grid.add_widget(wt.WLineEdit(),     0, 1)
    grid.add_widget(wt.WText('Notes:'), 1, 0)
    grid.add_widget(wt.WTextArea(),     1, 1)
    grid.set_column_stretch(1, 1)

**Constructors**

- `__init__(self) -> None`
  Construct an empty grid layout.

**Properties**

- `row_count: int` *(read-only)*
  Number of rows the grid currently uses.

- `column_count: int` *(read-only)*
  Number of columns the grid currently uses.

**Methods**

- `add_widget(self, widget: _T_Widget, row: int, column: int, row_span: int = 1, column_span: int = 1) -> _T_Widget`
  Place `widget` at the given grid coordinates, optionally
  spanning several rows or columns. Takes ownership; the
  Python wrapper is re-armed as a non-owning alias and
  returned for fluent chaining.

- `set_row_stretch(self, row: int, stretch: int) -> None`
  Set the stretch weight for `row`. Rows with positive
  stretch absorb extra vertical space proportionally.

- `set_column_stretch(self, column: int, stretch: int) -> None`
  Set the stretch weight for `column`. Columns with positive
  stretch absorb extra horizontal space proportionally.

### LayoutPosition {#LayoutPosition}

*Inherits:* `enum.Enum`

Slot identifier for WBorderLayout's five regions. North and
South stretch across the top and bottom; West and East stretch
down the sides; Center fills whatever is left in the middle.

### WBorderLayout {#WBorderLayout}

*Inherits:* `WLayout`

Classic BorderLayout — up to five children, one per region
(North, South, East, West, Center). North and South stretch
across the top and bottom; West and East stretch vertically on
the sides; Center fills the remaining space. Regions left empty
collapse to zero.

    layout = wt.WBorderLayout()
    container.set_layout(layout)
    layout.add_widget(wt.WText('Header'), wt.LayoutPosition.North)
    layout.add_widget(wt.WText('Body'),   wt.LayoutPosition.Center)
    layout.add_widget(wt.WText('Footer'), wt.LayoutPosition.South)

**Constructors**

- `__init__(self) -> None`
  Construct an empty border layout.

**Methods**

- `add_widget(self, widget: _T_Widget, position: LayoutPosition) -> _T_Widget`
  Place `widget` into the named region. Takes ownership; the
  Python wrapper is re-armed as a non-owning alias and
  returned for fluent chaining. Only one widget per region —
  calling add_widget with a position that's already taken
  replaces the current occupant.

### WFitLayout {#WFitLayout}

*Inherits:* `WLayout`

Single-child layout — the one widget you add expands to fill
the entire parent container. Equivalent to setting the child's
CSS to `width: 100%; height: 100%` without writing the CSS.

    fit = wt.WFitLayout()
    container.set_layout(fit)
    fit.add_widget(wt.WTextArea())

**Constructors**

- `__init__(self) -> None`
  Construct an empty fit layout.

**Methods**

- `add_widget(self, widget: _T_Widget) -> _T_Widget`
  Install `widget` as the single fitted child. Takes
  ownership; the Python wrapper is re-armed as a non-owning
  alias and returned for fluent chaining. Replacing the child
  requires calling the inherited removeWidget on the previous
  one first.
