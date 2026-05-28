"""
Wt's chart subsystem — WCartesianChart, WPieChart, WAxis, WDataSeries, and the supporting enums. Built atop WPaintedWidget.
"""

import enum
from typing import overload

import witty_for_python._witty_for_python


class SeriesType(enum.Enum):
    Point = 0

    Line = 1

    Curve = 2

    Bar = 3

class MarkerType(enum.Enum):
    Square = 1

    Circle = 2

    Cross = 3

    XCross = 4

    Triangle = 5

    Custom = 6

    Star = 7

    InvertedTriangle = 8

    Asterisk = 9

    Diamond = 10

class FillRangeType(enum.Enum):
    MinimumValue = 1

    MaximumValue = 2

    ZeroValue = 3

class ChartType(enum.Enum):
    Category = 0

    Scatter = 1

class LegendLocation(enum.Enum):
    Inside = 0

    Outside = 1

class AxisScale(enum.Enum):
    Discrete = 0

    Linear = 1

    Log = 2

    Date = 3

    DateTime = 4

class AxisValue(enum.IntEnum):
    Minimum = 1

    Maximum = 2

    Zero = 4

    Both = 8

class Axis(enum.Enum):
    X = 0

    Y = 1

    Y2 = 2

class LabelOption(enum.IntEnum):
    Inside = 1

    Outside = 2

    TextLabel = 16

    TextPercentage = 32

class WAxis:
    @property
    def visible(self) -> bool: ...

    @visible.setter
    def visible(self, arg: bool, /) -> None: ...

    def set_location(self, value: AxisValue) -> None:
        """
        Where on the perpendicular axis this one sits — Minimum, Maximum, Zero, or Both.
        """

    def set_scale(self, scale: AxisScale) -> None: ...

    @property
    def scale(self) -> AxisScale: ...

    def set_minimum(self, minimum: float) -> None: ...

    @property
    def minimum(self) -> float: ...

    def set_maximum(self, maximum: float) -> None: ...

    @property
    def maximum(self) -> float: ...

    def set_range(self, minimum: float, maximum: float) -> None: ...

    def set_auto_limits(self, locations: int) -> None:
        """AxisValue bitmask of which limits should auto-fit data."""

    def set_title(self, title: str) -> None: ...

    @property
    def title(self) -> str: ...

class WDataSeries:
    def __init__(self, model_column: int, type: SeriesType = SeriesType.Point, axis: Axis = Axis.Y) -> None:
        """
        Construct a series reading values from `model_column` of the chart's model, rendered with the given style on the given Y axis (Y1 or Y2).
        """

    @property
    def type(self) -> SeriesType: ...

    @type.setter
    def type(self, arg: SeriesType, /) -> None: ...

    @property
    def model_column(self) -> int: ...

    @model_column.setter
    def model_column(self, arg: int, /) -> None: ...

    @property
    def x_series_column(self) -> int:
        """
        Override the model column used for X values; default -1 = use the chart-wide X-series column.
        """

    @x_series_column.setter
    def x_series_column(self, arg: int, /) -> None: ...

    @property
    def stacked(self) -> bool: ...

    @stacked.setter
    def stacked(self, arg: bool, /) -> None: ...

    def bind_to_y_axis(self, y_axis: int) -> None: ...

    def set_pen(self, pen: witty_for_python._witty_for_python.WPen) -> None: ...

    def set_brush(self, brush: witty_for_python._witty_for_python.WBrush) -> None: ...

    def set_fill_range(self, fill_range: FillRangeType) -> None: ...

    def set_marker(self, marker: MarkerType) -> None: ...

    def set_marker_size(self, size: float) -> None: ...

    def set_marker_pen(self, pen: witty_for_python._witty_for_python.WPen) -> None: ...

    def set_marker_brush(self, brush: witty_for_python._witty_for_python.WBrush) -> None: ...

    def set_bar_width(self, width: float) -> None: ...

    def set_hidden(self, hidden: bool) -> None: ...

    @property
    def is_hidden(self) -> bool: ...

class WAbstractChart(witty_for_python._witty_for_python.WInteractWidget):
    def update(self) -> None:
        """
        Schedule a repaint. Wt batches paint events; call after mutating the underlying model if dynamic-sort-filter isn't on.
        """

    def set_model(self, model: witty_for_python._witty_for_python.WAbstractItemModel) -> None:
        """
        Set the data source. Any WAbstractItemModel (incl. WStandardItemModel + proxies) works; the chart consults the Display role on each cell.
        """

    def set_title(self, title: str) -> None: ...

    @property
    def title(self) -> str: ...

    def set_background(self, background: witty_for_python._witty_for_python.WBrush) -> None: ...

    def set_plot_area_padding(self, padding: int, sides: int) -> None:
        """
        Pixels of padding between the chart's plot area and its outer edge. `sides` is an int OR of Side bit-flag values. Use 0xFF (=all four sides) to set padding on every edge.
        """

    @property
    def auto_layout_enabled(self) -> bool:
        """
        When True, Wt computes plot-area padding to fit labels; False uses set_plot_area_padding values verbatim.
        """

    @auto_layout_enabled.setter
    def auto_layout_enabled(self, arg: bool, /) -> None: ...

class WCartesianChart(WAbstractChart):
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, type: ChartType) -> None: ...

    @property
    def type(self) -> ChartType: ...

    @type.setter
    def type(self, arg: ChartType, /) -> None: ...

    @property
    def legend_enabled(self) -> bool:
        """When True, render a legend listing each series."""

    @legend_enabled.setter
    def legend_enabled(self, arg: bool, /) -> None: ...

    def set_legend_location(self, side: LegendLocation, alignment: "Wt::Side", location: witty_for_python._witty_for_python.AlignmentFlag) -> None: ...

    def add_series(self, series: WDataSeries) -> WDataSeries: ...

    @property
    def x_series_column(self) -> int:
        """
        Column in the model holding X values for every series. -1 = use row index as X.
        """

    @x_series_column.setter
    def x_series_column(self, arg: int, /) -> None: ...

    def set_bar_margin(self, margin: float) -> None:
        """
        Spacing (in proportion of bar width) between bar groups in a bar chart. 0 = bars touch; 0.1 = small gap.
        """

    def axis(self, axis: Axis) -> WAxis:
        """
        Mutable reference to the named axis — set range / scale / title via the returned WAxis.
        """

class WPieChart(WAbstractChart):
    def __init__(self) -> None: ...

    def set_labels_column(self, column: int) -> None: ...

    @property
    def labels_column(self) -> int: ...

    def set_data_column(self, column: int) -> None: ...

    @property
    def data_column(self) -> int: ...

    def set_display_labels(self, options: int) -> None:
        """
        LabelOption bitmask. e.g. Inside | TextLabel shows the label text inside each segment; | TextPercentage adds the share %.
        """

    def set_explode(self, model_row: int, factor: float) -> None:
        """
        Pull the segment for `model_row` away from the centre by `factor` × pie radius (0.0 = none).
        """

    def set_perspective_enabled(self, enabled: bool, height: float = 1.0) -> None:
        """Render a 3-D-ish tilted pie. `height` is the foreshortening."""

    def set_shadow_enabled(self, enabled: bool) -> None: ...

    def set_start_angle(self, degrees: float) -> None:
        """
        Angle (in degrees) where the first slice begins. 0° points right; 90° points up (counter-clockwise convention).
        """
