# Charts (submodule)

> The `witty_for_python.chart` subsystem — Cartesian and pie charts driven by a WStandardItemModel data source.

**Classes in this section:**

- [`SeriesType`](#chart.SeriesType)
- [`MarkerType`](#chart.MarkerType)
- [`FillRangeType`](#chart.FillRangeType)
- [`ChartType`](#chart.ChartType)
- [`LegendLocation`](#chart.LegendLocation)
- [`AxisScale`](#chart.AxisScale)
- [`AxisValue`](#chart.AxisValue)
- [`Axis`](#chart.Axis)
- [`LabelOption`](#chart.LabelOption)
- [`WAxis`](#chart.WAxis)
- [`WDataSeries`](#chart.WDataSeries)
- [`WAbstractChart`](#chart.WAbstractChart)
- [`WCartesianChart`](#chart.WCartesianChart)
- [`WPieChart`](#chart.WPieChart)

---

### SeriesType {#chart.SeriesType}

*Inherits:* `enum.Enum`

How a WDataSeries renders its values — discrete markers (Point), straight-line segments (Line), smoothed curve (Curve), or grouped bars (Bar).

### MarkerType {#chart.MarkerType}

*Inherits:* `enum.Enum`

Glyph shape rendered at each data point of a Point or Line series. None_ suppresses markers; Custom uses the path supplied via the chart's custom-marker API (not yet bound).

### FillRangeType {#chart.FillRangeType}

*Inherits:* `enum.Enum`

Where the area-fill of a Line / Curve series stops. MinimumValue fills down to the bottom of the plot, MaximumValue up to the top, ZeroValue to the y=0 axis, None_ disables filling.

### ChartType {#chart.ChartType}

*Inherits:* `enum.Enum`

Cartesian chart axis convention. Category treats X-values as discrete labels (one column per row); Scatter treats X-values as numeric (one numeric column shared across series).

### LegendLocation {#chart.LegendLocation}

*Inherits:* `enum.Enum`

Whether the legend is drawn inside the plot area (Inside) or in a separate strip outside it (Outside).

### AxisScale {#chart.AxisScale}

*Inherits:* `enum.Enum`

Scale type for a WAxis. Discrete numbers each row; Linear / Log are numeric; Date / DateTime treat values as calendar instants and pick sensible tick spacing.

### AxisValue {#chart.AxisValue}

*Inherits:* `enum.IntEnum`

Reference values on a perpendicular axis where this axis can sit (location flag) or where auto-fitting should apply (auto-limits bitmask). Bitwise-OR Minimum | Maximum for auto-fit on both ends.

### Axis {#chart.Axis}

*Inherits:* `enum.Enum`

Identifies one of the axes of a cartesian chart — X (bottom), Y (primary, left), or Y2 (secondary, right).

### LabelOption {#chart.LabelOption}

*Inherits:* `enum.IntEnum`

Pie-chart label placement / content flags. Bitwise-OR to combine — e.g. `Outside | TextLabel | TextPercentage` shows label text and percentage just outside each slice.

### WAxis {#chart.WAxis}

Configures one axis of a WCartesianChart — title, scale, min/max range, visibility, and where it sits relative to the perpendicular axis. Don't construct directly; obtain via `chart.axis(Axis.X)` (or Y / Y2) and mutate in place.

    chart.axis(chart_mod.Axis.X).set_title('Time (s)')
    chart.axis(chart_mod.Axis.Y).set_range(0, 100)

**Properties**

- `visible: bool` *(read/write)*
  Whether the axis line, ticks, and labels render at all.

- `scale: AxisScale` *(read-only)*
  Current AxisScale.

- `minimum: float` *(read-only)*
  Current lower bound (computed if auto-fitting is on).

- `maximum: float` *(read-only)*
  Current upper bound.

- `title: str` *(read-only)*
  Current axis label.

**Methods**

- `set_location(self, value: AxisValue) -> None`
  Where on the perpendicular axis this one sits — Minimum, Maximum, Zero, or Both.

- `set_scale(self, scale: AxisScale) -> None`
  Set the axis scale — Linear, Log, Date, DateTime, Discrete.

- `set_minimum(self, minimum: float) -> None`
  Pin the axis lower bound. Overrides auto-fitting on that end.

- `set_maximum(self, maximum: float) -> None`
  Pin the axis upper bound.

- `set_range(self, minimum: float, maximum: float) -> None`
  Pin both ends in one call. Equivalent to set_minimum + set_maximum.

- `set_auto_limits(self, locations: int) -> None`
  AxisValue bitmask of which limits should auto-fit data.

- `set_title(self, title: str) -> None`
  Set the axis label.

### WDataSeries {#chart.WDataSeries}

One series (curve, bar group, marker set) in a cartesian
chart. Construct standalone, style it, then transfer ownership
to the chart with `add_series`.

    s = chart_mod.WDataSeries(2, chart_mod.SeriesType.Line,
                              chart_mod.Axis.Y)
    s.set_pen(wt.WPen(wt.WColor('crimson')))
    s.set_marker(chart_mod.MarkerType.Circle)
    chart.add_series(s)

Series read values from a column of the chart's WAbstractItem-
Model (typically a WStandardItemModel).

**Constructors**

- `__init__(self, model_column: int, type: SeriesType = SeriesType.Point, axis: Axis = Axis.Y) -> None`
  Construct a series reading values from `model_column` of the chart's model, rendered with the given style on the given Y axis (Y1 or Y2).

**Properties**

- `type: SeriesType` *(read/write)*
  Render style — SeriesType.Point / Line / Curve / Bar.

- `model_column: int` *(read/write)*
  Column in the model from which Y values are read.

- `x_series_column: int` *(read/write)*
  Override the model column used for X values; default -1 = use the chart-wide X-series column.

- `stacked: bool` *(read/write)*
  When True, this series stacks on top of preceding stacked series instead of starting from the baseline.

- `is_hidden: bool` *(read-only)*
  True if the series is currently hidden.

**Methods**

- `bind_to_y_axis(self, y_axis: int) -> None`
  Switch the series between the primary (Y1) and secondary (Y2) Y axes by index.

- `set_pen(self, pen: witty_for_python._witty_for_python.WPen) -> None`
  Stroke style for lines / curve / bar outlines.

- `set_brush(self, brush: witty_for_python._witty_for_python.WBrush) -> None`
  Fill style for area-filled lines / bars.

- `set_fill_range(self, fill_range: FillRangeType) -> None`
  Set where Line / Curve series fill stops — to the bottom (MinimumValue), top (MaximumValue), y=0 (ZeroValue), or no fill (None_).

- `set_marker(self, marker: MarkerType) -> None`
  Glyph drawn at each data point (MarkerType.Circle, Square, …).

- `set_marker_size(self, size: float) -> None`
  Marker glyph radius in pixels.

- `set_marker_pen(self, pen: witty_for_python._witty_for_python.WPen) -> None`
  Stroke style applied just to markers (independent of the series line pen).

- `set_marker_brush(self, brush: witty_for_python._witty_for_python.WBrush) -> None`
  Fill style for markers.

- `set_bar_width(self, width: float) -> None`
  Bar width as a proportion of the X-axis interval between categories (Bar series only).

- `set_hidden(self, hidden: bool) -> None`
  Hide / show the series without removing it from the chart.

### WAbstractChart {#chart.WAbstractChart}

*Inherits:* `witty_for_python._witty_for_python.WInteractWidget`

Common base for chart widgets — WCartesianChart and WPieChart.
Holds the data model, title, background, and plot-area
padding. Backed in C++ by WPaintedWidget; in this binding the
Python-visible inheritance is WInteractWidget, so charts are
clickable and addable but won't pass
`isinstance(x, WPaintedWidget)`.

Every chart needs a WStandardItemModel (or any
WAbstractItemModel) as its data source.

**Properties**

- `title: str` *(read-only)*
  Current chart title.

- `auto_layout_enabled: bool` *(read/write)*
  When True, Wt computes plot-area padding to fit labels; False uses set_plot_area_padding values verbatim.

**Methods**

- `update(self) -> None`
  Schedule a repaint. Wt batches paint events; call after mutating the underlying model if dynamic-sort-filter isn't on.

- `set_model(self, model: witty_for_python._witty_for_python.WAbstractItemModel) -> None`
  Set the data source. Any WAbstractItemModel (incl. WStandardItemModel + proxies) works; the chart consults the Display role on each cell.

- `set_title(self, title: str) -> None`
  Set the chart's overall title, rendered above the plot.

- `set_background(self, background: witty_for_python._witty_for_python.WBrush) -> None`
  Brush used to fill the chart's full bounding rect (behind the plot area).

- `set_plot_area_padding(self, padding: int, sides: int) -> None`
  Pixels of padding between the chart's plot area and its outer edge. `sides` is an int OR of Side bit-flag values. Use 0xFF (=all four sides) to set padding on every edge.

### WCartesianChart {#chart.WCartesianChart}

*Inherits:* `WAbstractChart`

X/Y chart — line, scatter, bar, or combinations thereof.
Configure the chart type (Category or Scatter), attach a
WStandardItemModel, then add one or more WDataSeries.

    model = wt.WStandardItemModel(10, 2)
    for r in range(10):
        model.set_data(r, 0, r)
        model.set_data(r, 1, r * r)
    chart = container.add_widget(
        chart_mod.WCartesianChart(chart_mod.ChartType.Scatter))
    chart.set_model(model)
    chart.x_series_column = 0
    chart.add_series(chart_mod.WDataSeries(1, chart_mod.SeriesType.Line))

Per-axis settings (range, scale, title) live on the WAxis
objects reachable via `chart.axis(Axis.X / Y / Y2)`.

**Constructors**

- `__init__(self) -> None`
  Construct an empty cartesian chart of the default type.

- `__init__(self, type: ChartType) -> None`
  Construct an empty chart of the given ChartType.

**Properties**

- `type: ChartType` *(read/write)*
  Category or Scatter — controls how X values are interpreted.

- `legend_enabled: bool` *(read/write)*
  When True, render a legend listing each series.

- `x_series_column: int` *(read/write)*
  Column in the model holding X values for every series. -1 = use row index as X.

**Methods**

- `set_legend_location(self, side: LegendLocation, alignment: 'Wt::Side', location: witty_for_python._witty_for_python.AlignmentFlag) -> None`
  Place the legend. `side` is a Side enum (Left / Right / Top / Bottom), `alignment` is an AlignmentFlag, `location` is a LegendLocation (Inside / Outside the plot area).

- `add_series(self, series: _T_Series) -> _T_Series`
  Transfer ownership of `series` to the chart and return the same Python wrapper (re-armed as a non-owning alias). Chain further configuration off the returned reference.

- `set_bar_margin(self, margin: float) -> None`
  Spacing (in proportion of bar width) between bar groups in a bar chart. 0 = bars touch; 0.1 = small gap.

- `axis(self, axis: Axis) -> WAxis`
  Mutable reference to the named axis — set range / scale / title via the returned WAxis.

### WPieChart {#chart.WPieChart}

*Inherits:* `WAbstractChart`

Pie chart driven by one numeric data column and one label
column of a WStandardItemModel. Each row of the model becomes a
slice; segment sizes are proportional to the data-column value.

    model = wt.WStandardItemModel(3, 2)
    for row, (label, value) in enumerate([('A', 30), ('B', 45),
                                          ('C', 25)]):
        model.set_data(row, 0, label)
        model.set_data(row, 1, value)
    pie = container.add_widget(chart_mod.WPieChart())
    pie.set_model(model)
    pie.set_labels_column(0)
    pie.set_data_column(1)
    pie.set_display_labels(chart_mod.LabelOption.Outside
                           | chart_mod.LabelOption.TextLabel)

**Constructors**

- `__init__(self) -> None`
  Construct an empty pie chart. Attach a model and assign labels / data columns before it can render anything.

**Properties**

- `labels_column: int` *(read-only)*
  Current labels-column index.

- `data_column: int` *(read-only)*
  Current data-column index.

**Methods**

- `set_labels_column(self, column: int) -> None`
  Index of the model column whose Display strings become slice labels.

- `set_data_column(self, column: int) -> None`
  Index of the model column whose numeric values determine slice sizes.

- `set_display_labels(self, options: int) -> None`
  LabelOption bitmask. e.g. Inside | TextLabel shows the label text inside each segment; | TextPercentage adds the share %.

- `set_explode(self, model_row: int, factor: float) -> None`
  Pull the segment for `model_row` away from the centre by `factor` × pie radius (0.0 = none).

- `set_perspective_enabled(self, enabled: bool, height: float = 1.0) -> None`
  Render a 3-D-ish tilted pie. `height` is the foreshortening.

- `set_shadow_enabled(self, enabled: bool) -> None`
  When True, draw a drop shadow beneath the pie.

- `set_start_angle(self, degrees: float) -> None`
  Angle (in degrees) where the first slice begins. 0° points right; 90° points up (counter-clockwise convention).
