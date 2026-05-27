"""Chart subsystem suite (wt.chart module).

Most of Wt's chart classes inherit WPaintedWidget, so the concrete
WCartesianChart and WPieChart need an active WApplication session at
construction. We exercise the chart-only value types (WDataSeries, enums)
that don't need a session, plus the binding surface of the widget
classes. End-to-end rendering is exercised by the gallery boot test.
"""

from __future__ import annotations

import pytest
import witty_for_python as wt


# ---- chart submodule is reachable ----------------------------------------

def test_chart_submodule_exposed() -> None:
    assert wt.chart is not None
    # It's a Python module that nanobind populated.
    assert hasattr(wt.chart, "WCartesianChart")


# ---- Enums ---------------------------------------------------------------

@pytest.mark.parametrize("name", ["Point", "Line", "Curve", "Bar"])
def test_series_type_members(name: str) -> None:
    assert hasattr(wt.chart.SeriesType, name)


def test_marker_type_members() -> None:
    members = ("None_", "Square", "Circle", "Cross", "XCross", "Triangle",
               "Custom", "Star", "InvertedTriangle", "Asterisk", "Diamond")
    for name in members:
        assert hasattr(wt.chart.MarkerType, name)


def test_chart_type_members() -> None:
    assert wt.chart.ChartType.Category != wt.chart.ChartType.Scatter


def test_axis_scale_members() -> None:
    for name in ("Discrete", "Linear", "Log", "Date", "DateTime"):
        assert hasattr(wt.chart.AxisScale, name)


def test_axis_enum_members() -> None:
    """Wt::Chart::Axis uses X=0, Y=Y1=1, Y2=2. We bind X / Y / Y2 — Y1 is
    an alias for Y in C++ so only one of them appears in Python."""
    assert wt.chart.Axis.X != wt.chart.Axis.Y
    assert wt.chart.Axis.Y != wt.chart.Axis.Y2


def test_label_option_members() -> None:
    for name in ("None_", "Inside", "Outside", "TextLabel", "TextPercentage"):
        assert hasattr(wt.chart.LabelOption, name)


def test_legend_location_members() -> None:
    assert wt.chart.LegendLocation.Inside != wt.chart.LegendLocation.Outside


# ---- WDataSeries (constructible standalone — pure value carrier) ---------

def test_wdataseries_construct_defaults() -> None:
    s = wt.chart.WDataSeries(0)
    assert s.model_column == 0
    assert s.type == wt.chart.SeriesType.Point


def test_wdataseries_explicit_type_and_axis() -> None:
    s = wt.chart.WDataSeries(2, wt.chart.SeriesType.Bar, wt.chart.Axis.Y2)
    assert s.type == wt.chart.SeriesType.Bar
    assert s.model_column == 2


def test_wdataseries_style_setters() -> None:
    """Setters don't need a chart session — the series carries style
    state that's applied when it lands inside a chart."""
    s = wt.chart.WDataSeries(0)
    s.set_pen(wt.WPen(wt.WColor(255, 100, 50)))
    s.set_brush(wt.WBrush(wt.WColor(255, 100, 50)))
    s.set_marker(wt.chart.MarkerType.Circle)
    s.set_marker_size(8.0)
    s.set_fill_range(wt.chart.FillRangeType.ZeroValue)


def test_wdataseries_stacked_round_trip() -> None:
    s = wt.chart.WDataSeries(0)
    assert s.stacked is False
    s.stacked = True
    assert s.stacked is True


def test_wdataseries_hidden_round_trip() -> None:
    s = wt.chart.WDataSeries(0)
    assert s.is_hidden is False
    s.set_hidden(True)
    assert s.is_hidden is True


# ---- Class binding surface (no construction — needs session) ------------

@pytest.mark.parametrize("cls,base", [
    (wt.chart.WAbstractChart,    wt.WInteractWidget),
    (wt.chart.WCartesianChart,   wt.chart.WAbstractChart),
    (wt.chart.WPieChart,         wt.chart.WAbstractChart),
])
def test_chart_class_inheritance(cls: type, base: type) -> None:
    assert issubclass(cls, base)


@pytest.mark.parametrize("cls,attr", [
    (wt.chart.WAbstractChart,  "update"),
    (wt.chart.WAbstractChart,  "set_model"),
    (wt.chart.WAbstractChart,  "set_title"),
    (wt.chart.WAbstractChart,  "set_background"),
    (wt.chart.WAbstractChart,  "set_plot_area_padding"),
    (wt.chart.WAbstractChart,  "auto_layout_enabled"),
    (wt.chart.WCartesianChart, "add_series"),
    (wt.chart.WCartesianChart, "x_series_column"),
    (wt.chart.WCartesianChart, "type"),
    (wt.chart.WCartesianChart, "legend_enabled"),
    (wt.chart.WCartesianChart, "set_bar_margin"),
    (wt.chart.WCartesianChart, "axis"),
    (wt.chart.WPieChart,       "set_labels_column"),
    (wt.chart.WPieChart,       "set_data_column"),
    (wt.chart.WPieChart,       "set_display_labels"),
    (wt.chart.WPieChart,       "set_explode"),
    (wt.chart.WPieChart,       "set_perspective_enabled"),
    (wt.chart.WPieChart,       "set_shadow_enabled"),
    (wt.chart.WPieChart,       "set_start_angle"),
])
def test_chart_attribute_present(cls: type, attr: str) -> None:
    assert hasattr(cls, attr), f"{cls.__name__} missing: {attr}"


# ---- WAxis class surface --------------------------------------------------

@pytest.mark.parametrize("attr", [
    "visible", "set_location", "set_scale", "scale", "set_minimum",
    "minimum", "set_maximum", "maximum", "set_range", "set_auto_limits",
    "set_title", "title",
])
def test_waxis_attribute_present(attr: str) -> None:
    assert hasattr(wt.chart.WAxis, attr)
