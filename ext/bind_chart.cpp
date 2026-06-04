#include "common.hpp"

#include <Wt/Chart/WAbstractChart.h>
#include <Wt/Chart/WAxis.h>
#include <Wt/Chart/WCartesianChart.h>
#include <Wt/Chart/WChartGlobal.h>
#include <Wt/Chart/WDataSeries.h>
#include <Wt/Chart/WPieChart.h>
#include <Wt/WAbstractItemModel.h>     // setModel parameter type
#include <Wt/WBrush.h>
#include <Wt/WPen.h>

#include <memory>
#include <vector>

namespace witty_for_python {

namespace ch = Wt::Chart;

void register_chart(nb::module_& m) {
    // Charts live in their own submodule — Wt itself groups them in the
    // `Wt::Chart` namespace, so mirroring that as `witty_for_python.chart`
    // keeps the top-level package uncluttered and matches Wt's docs:
    //
    //   from witty_for_python import chart
    //   c = chart.WCartesianChart(chart.ChartType.Scatter)

    nb::module_ chart = m.def_submodule("chart",
        "Wt's chart subsystem — WCartesianChart, WPieChart, WAxis, "
        "WDataSeries, and the supporting enums. Built atop WPaintedWidget.");

    // ---- Enums (WChartGlobal) ----

    nb::enum_<ch::SeriesType>(chart, "SeriesType",
        "How a WDataSeries renders its values — discrete markers "
        "(Point), straight-line segments (Line), smoothed curve "
        "(Curve), or grouped bars (Bar).")
        .value("Point", ch::SeriesType::Point)
        .value("Line",  ch::SeriesType::Line)
        .value("Curve", ch::SeriesType::Curve)
        .value("Bar",   ch::SeriesType::Bar);

    nb::enum_<ch::MarkerType>(chart, "MarkerType",
        "Glyph shape rendered at each data point of a Point or Line "
        "series. None_ suppresses markers; Custom uses the path supplied "
        "via the chart's custom-marker API (not yet bound).")
        .value("None_",            ch::MarkerType::None)
        .value("Square",           ch::MarkerType::Square)
        .value("Circle",           ch::MarkerType::Circle)
        .value("Cross",            ch::MarkerType::Cross)
        .value("XCross",           ch::MarkerType::XCross)
        .value("Triangle",         ch::MarkerType::Triangle)
        .value("Custom",           ch::MarkerType::Custom)
        .value("Star",             ch::MarkerType::Star)
        .value("InvertedTriangle", ch::MarkerType::InvertedTriangle)
        .value("Asterisk",         ch::MarkerType::Asterisk)
        .value("Diamond",          ch::MarkerType::Diamond);

    nb::enum_<ch::FillRangeType>(chart, "FillRangeType",
        "Where the area-fill of a Line / Curve series stops. "
        "MinimumValue fills down to the bottom of the plot, "
        "MaximumValue up to the top, ZeroValue to the y=0 axis, None_ "
        "disables filling.")
        .value("None_",        ch::FillRangeType::None)
        .value("MinimumValue", ch::FillRangeType::MinimumValue)
        .value("MaximumValue", ch::FillRangeType::MaximumValue)
        .value("ZeroValue",    ch::FillRangeType::ZeroValue);

    nb::enum_<ch::ChartType>(chart, "ChartType",
        "Cartesian chart axis convention. Category treats X-values as "
        "discrete labels (one column per row); Scatter treats X-values "
        "as numeric (one numeric column shared across series).")
        .value("Category", ch::ChartType::Category)
        .value("Scatter",  ch::ChartType::Scatter);

    nb::enum_<ch::LegendLocation>(chart, "LegendLocation",
        "Whether the legend is drawn inside the plot area (Inside) or "
        "in a separate strip outside it (Outside).")
        .value("Inside",  ch::LegendLocation::Inside)
        .value("Outside", ch::LegendLocation::Outside);

    nb::enum_<ch::AxisScale>(chart, "AxisScale",
        "Scale type for a WAxis. Discrete numbers each row; Linear / "
        "Log are numeric; Date / DateTime treat values as calendar "
        "instants and pick sensible tick spacing.")
        .value("Discrete", ch::AxisScale::Discrete)
        .value("Linear",   ch::AxisScale::Linear)
        .value("Log",      ch::AxisScale::Log)
        .value("Date",     ch::AxisScale::Date)
        .value("DateTime", ch::AxisScale::DateTime);

    nb::enum_<ch::AxisValue>(chart, "AxisValue", nb::is_arithmetic(),
        "Reference values on a perpendicular axis where this axis can "
        "sit (location flag) or where auto-fitting should apply "
        "(auto-limits bitmask). Bitwise-OR Minimum | Maximum for "
        "auto-fit on both ends.")
        .value("Minimum", ch::AxisValue::Minimum)
        .value("Maximum", ch::AxisValue::Maximum)
        .value("Zero",    ch::AxisValue::Zero)
        .value("Both",    ch::AxisValue::Both);

    nb::enum_<ch::Axis>(chart, "Axis",
        "Identifies one of the axes of a cartesian chart — X (bottom), "
        "Y (primary, left), or Y2 (secondary, right).")
        .value("X",  ch::Axis::X)
        .value("Y",  ch::Axis::Y)
        .value("Y2", ch::Axis::Y2);

    nb::enum_<ch::LabelOption>(chart, "LabelOption", nb::is_arithmetic(),
        "Pie-chart label placement / content flags. Bitwise-OR to "
        "combine — e.g. `Outside | TextLabel | TextPercentage` shows "
        "label text and percentage just outside each slice.")
        .value("None_",          ch::LabelOption::None)
        .value("Inside",         ch::LabelOption::Inside)
        .value("Outside",        ch::LabelOption::Outside)
        .value("TextLabel",      ch::LabelOption::TextLabel)
        .value("TextPercentage", ch::LabelOption::TextPercentage);


    // ---- WAxis ----
    //
    // Configures one axis of a WCartesianChart. Not constructed by user
    // code — fetched from the chart via `chart.axis(Axis.X)` and mutated
    // in place. We expose it as a reference-internal accessor in the
    // chart class below.

    nb::class_<ch::WAxis>(chart, "WAxis",
        "Configures one axis of a WCartesianChart — title, scale, "
        "min/max range, visibility, and where it sits relative to the "
        "perpendicular axis. Don't construct directly; obtain via "
        "`chart.axis(Axis.X)` (or Y / Y2) and mutate in place.\n"
        "\n"
        "    chart.axis(chart_mod.Axis.X).set_title('Time (s)')\n"
        "    chart.axis(chart_mod.Axis.Y).set_range(0, 100)")
        .def_prop_rw("visible",
            &ch::WAxis::isVisible,
            &ch::WAxis::setVisible,
            "Whether the axis line, ticks, and labels render at all.")
        .def("set_location", &ch::WAxis::setLocation, "value"_a,
             "Where on the perpendicular axis this one sits — Minimum, "
             "Maximum, Zero, or Both.")
        .def("set_scale", &ch::WAxis::setScale, "scale"_a,
             "Set the axis scale — Linear, Log, Date, DateTime, Discrete.")
        .def_prop_ro("scale", &ch::WAxis::scale,
             "Current AxisScale.")
        .def("set_minimum", &ch::WAxis::setMinimum, "minimum"_a,
             "Pin the axis lower bound. Overrides auto-fitting on that "
             "end.")
        .def_prop_ro("minimum", &ch::WAxis::minimum,
             "Current lower bound (computed if auto-fitting is on).")
        .def("set_maximum", &ch::WAxis::setMaximum, "maximum"_a,
             "Pin the axis upper bound.")
        .def_prop_ro("maximum", &ch::WAxis::maximum,
             "Current upper bound.")
        .def("set_range", &ch::WAxis::setRange, "minimum"_a, "maximum"_a,
             "Pin both ends in one call. Equivalent to set_minimum + "
             "set_maximum.")
        .def("set_auto_limits",
            [](ch::WAxis& self, int locations) {
                self.setAutoLimits(Wt::WFlags<ch::AxisValue>(
                    static_cast<ch::AxisValue>(locations)));
            },
            "locations"_a,
            "AxisValue bitmask of which limits should auto-fit data.")
        .def("set_title", &ch::WAxis::setTitle, "title"_a,
             "Set the axis label.")
        .def_prop_ro("title", &ch::WAxis::title,
             "Current axis label.");

    // ---- WDataSeries ----
    //
    // One curve / bar series in a cartesian chart. Constructed
    // standalone, then handed to `chart.add_series(series)` which moves
    // ownership in. The series can be styled (pen, brush, marker) before
    // OR after attaching to a chart.

    nb::class_<ch::WDataSeries>(chart, "WDataSeries",
        "One series (curve, bar group, marker set) in a cartesian\n"
        "chart. Construct standalone, style it, then transfer ownership\n"
        "to the chart with `add_series`.\n"
        "\n"
        "    s = chart_mod.WDataSeries(2, chart_mod.SeriesType.Line,\n"
        "                              chart_mod.Axis.Y)\n"
        "    s.set_pen(wt.WPen(wt.WColor('crimson')))\n"
        "    s.set_marker(chart_mod.MarkerType.Circle)\n"
        "    chart.add_series(s)\n"
        "\n"
        "Series read values from a column of the chart's WAbstractItem-\n"
        "Model (typically a WStandardItemModel).")
        .def(nb::new_(
                [](int model_column, ch::SeriesType type, ch::Axis axis) {
                    return std::make_unique<ch::WDataSeries>(
                        model_column, type, axis);
                }),
            "model_column"_a, "type"_a = ch::SeriesType::Point,
            "axis"_a = ch::Axis::Y1,
            "Construct a series reading values from `model_column` of the "
            "chart's model, rendered with the given style on the given "
            "Y axis (Y1 or Y2).")
        .def_prop_rw("type",
            &ch::WDataSeries::type,
            &ch::WDataSeries::setType,
            "Render style — SeriesType.Point / Line / Curve / Bar.")
        .def_prop_rw("model_column",
            &ch::WDataSeries::modelColumn,
            &ch::WDataSeries::setModelColumn,
            "Column in the model from which Y values are read.")
        .def_prop_rw("x_series_column",
            &ch::WDataSeries::XSeriesColumn,
            &ch::WDataSeries::setXSeriesColumn,
            "Override the model column used for X values; default -1 = "
            "use the chart-wide X-series column.")
        .def_prop_rw("stacked",
            &ch::WDataSeries::isStacked,
            &ch::WDataSeries::setStacked,
            "When True, this series stacks on top of preceding stacked "
            "series instead of starting from the baseline.")
        .def("bind_to_y_axis", &ch::WDataSeries::bindToYAxis, "y_axis"_a,
             "Switch the series between the primary (Y1) and secondary "
             "(Y2) Y axes by index.")
        .def("set_pen", &ch::WDataSeries::setPen, "pen"_a,
             "Stroke style for lines / curve / bar outlines.")
        .def("set_brush", &ch::WDataSeries::setBrush, "brush"_a,
             "Fill style for area-filled lines / bars.")
        .def("set_fill_range", &ch::WDataSeries::setFillRange, "fill_range"_a,
             "Set where Line / Curve series fill stops — to the bottom "
             "(MinimumValue), top (MaximumValue), y=0 (ZeroValue), or "
             "no fill (None_).")
        .def("set_marker", &ch::WDataSeries::setMarker, "marker"_a,
             "Glyph drawn at each data point (MarkerType.Circle, "
             "Square, …).")
        .def("set_marker_size", &ch::WDataSeries::setMarkerSize, "size"_a,
             "Marker glyph radius in pixels.")
        .def("set_marker_pen", &ch::WDataSeries::setMarkerPen, "pen"_a,
             "Stroke style applied just to markers (independent of the "
             "series line pen).")
        .def("set_marker_brush", &ch::WDataSeries::setMarkerBrush, "brush"_a,
             "Fill style for markers.")
        .def("set_bar_width", &ch::WDataSeries::setBarWidth, "width"_a,
             "Bar width as a proportion of the X-axis interval between "
             "categories (Bar series only).")
        .def("set_hidden", &ch::WDataSeries::setHidden, "hidden"_a,
             "Hide / show the series without removing it from the chart.")
        .def_prop_ro("is_hidden", &ch::WDataSeries::isHidden,
             "True if the series is currently hidden.");

    // ---- WAbstractChart ----
    //
    // Base class for WCartesianChart and WPieChart. In C++ this inherits
    // WPaintedWidget, but Python-side we already exposed WPaintedWidget
    // as our trampoline subclass PyPaintedWidget — `Wt::WPaintedWidget`
    // itself isn't a registered Python type. So we bind WAbstractChart
    // as a direct child of WInteractWidget instead; charts won't pass
    // `isinstance(x, wt.WPaintedWidget)` but they're full WInteractWidgets
    // (clickable, signal-emitting, mountable). We re-bind `update()` here
    // explicitly so chart users can request a repaint without needing
    // the WPaintedWidget surface.

    nb::class_<ch::WAbstractChart, Wt::WInteractWidget>(chart, "WAbstractChart",
        "Common base for chart widgets — WCartesianChart and WPieChart.\n"
        "Holds the data model, title, background, and plot-area\n"
        "padding. Backed in C++ by WPaintedWidget; in this binding the\n"
        "Python-visible inheritance is WInteractWidget, so charts are\n"
        "clickable and addable but won't pass\n"
        "`isinstance(x, WPaintedWidget)`.\n"
        "\n"
        "Every chart needs a WStandardItemModel (or any\n"
        "WAbstractItemModel) as its data source.")
        .def("update",
            [](ch::WAbstractChart& self) { self.update(); },
            "Schedule a repaint. Wt batches paint events; call after "
            "mutating the underlying model if dynamic-sort-filter isn't on.")
        .def("set_model",
            // Disambiguate the WAbstractItemModel-taking overload.
            [](ch::WAbstractChart& self,
               const std::shared_ptr<Wt::WAbstractItemModel>& model) {
                self.setModel(model);
            },
            "model"_a,
            "Set the data source. Any WAbstractItemModel (incl. "
            "WStandardItemModel + proxies) works; the chart consults the "
            "Display role on each cell.")
        .def("set_title", &ch::WAbstractChart::setTitle, "title"_a,
             "Set the chart's overall title, rendered above the plot.")
        .def_prop_ro("title", &ch::WAbstractChart::title,
             "Current chart title.")
        .def("set_background", &ch::WAbstractChart::setBackground,
             "background"_a,
             "Brush used to fill the chart's full bounding rect (behind "
             "the plot area).")
        .def("set_plot_area_padding",
            [](ch::WAbstractChart& self, int padding, int sides) {
                self.setPlotAreaPadding(padding,
                    Wt::WFlags<Wt::Side>(
                        static_cast<Wt::Side>(sides)));
            },
            "padding"_a, "sides"_a,
            "Pixels of padding between the chart's plot area and its "
            "outer edge. `sides` is an int OR of Side bit-flag values. "
            "Use 0xFF (=all four sides) to set padding on every edge.")
        .def_prop_rw("auto_layout_enabled",
            &ch::WAbstractChart::isAutoLayoutEnabled,
            &ch::WAbstractChart::setAutoLayoutEnabled,
            "When True, Wt computes plot-area padding to fit labels; "
            "False uses set_plot_area_padding values verbatim.");

    // ---- WCartesianChart ----

    nb::class_<ch::WCartesianChart, ch::WAbstractChart>(chart, "WCartesianChart",
        "X/Y chart — line, scatter, bar, or combinations thereof.\n"
        "Configure the chart type (Category or Scatter), attach a\n"
        "WStandardItemModel, then add one or more WDataSeries.\n"
        "\n"
        "    model = wt.WStandardItemModel(10, 2)\n"
        "    for r in range(10):\n"
        "        model.set_data(r, 0, r)\n"
        "        model.set_data(r, 1, r * r)\n"
        "    chart = container.add_widget(\n"
        "        chart_mod.WCartesianChart(chart_mod.ChartType.Scatter))\n"
        "    chart.set_model(model)\n"
        "    chart.x_series_column = 0\n"
        "    chart.add_series(chart_mod.WDataSeries(1, chart_mod.SeriesType.Line))\n"
        "\n"
        "Per-axis settings (range, scale, title) live on the WAxis\n"
        "objects reachable via `chart.axis(Axis.X / Y / Y2)`.")
        .def(heap_init<ch::WCartesianChart>(),
             "Construct an empty cartesian chart of the default type.")
        .def(heap_init<ch::WCartesianChart, ch::ChartType>(), "type"_a,
             "Construct an empty chart of the given ChartType.")
        .def_prop_rw("type",
            &ch::WCartesianChart::type,
            &ch::WCartesianChart::setType,
            "Category or Scatter — controls how X values are interpreted.")
        .def_prop_rw("legend_enabled",
            &ch::WCartesianChart::isLegendEnabled,
            &ch::WCartesianChart::setLegendEnabled,
            "When True, render a legend listing each series.")
        .def("set_legend_location", &ch::WCartesianChart::setLegendLocation,
             "side"_a, "alignment"_a, "location"_a,
             "Place the legend. `side` is a Side enum (Left / Right / "
             "Top / Bottom), `alignment` is an AlignmentFlag, `location` "
             "is a LegendLocation (Inside / Outside the plot area).")
        .def("add_series",
            // Re-arm pattern: transfer ownership, mark wrapper non-owning,
            // return the SAME Python object for fluent chaining.
            [](ch::WCartesianChart& self, nb::object py_series) -> nb::object {
                auto s = nb::cast<std::unique_ptr<ch::WDataSeries>>(py_series);
                self.addSeries(std::move(s));
                nb::inst_set_state(py_series, /*ready*/ true,
                                   /*destruct*/ false);
                return py_series;
            },
            "series"_a,
            "Transfer ownership of `series` to the chart and return the "
            "same Python wrapper (re-armed as a non-owning alias). "
            "Chain further configuration off the returned reference.")
        .def_prop_rw("x_series_column",
            &ch::WCartesianChart::XSeriesColumn,
            &ch::WCartesianChart::setXSeriesColumn,
            "Column in the model holding X values for every series. "
            "-1 = use row index as X.")
        .def("set_bar_margin", &ch::WCartesianChart::setBarMargin,
             "margin"_a,
             "Spacing (in proportion of bar width) between bar groups in "
             "a bar chart. 0 = bars touch; 0.1 = small gap.")
        .def("axis",
            // axis() is overloaded for X / Y / Y2 (and individual
            // X/Y indexes for multi-axis charts); take just the enum form.
            [](ch::WCartesianChart& self, ch::Axis axis) -> ch::WAxis& {
                return self.axis(axis);
            },
            "axis"_a,
            nb::rv_policy::reference_internal,
            "Mutable reference to the named axis — set range / scale / "
            "title via the returned WAxis.");

    // ---- WPieChart ----

    nb::class_<ch::WPieChart, ch::WAbstractChart>(chart, "WPieChart",
        "Pie chart driven by one numeric data column and one label\n"
        "column of a WStandardItemModel. Each row of the model becomes a\n"
        "slice; segment sizes are proportional to the data-column value.\n"
        "\n"
        "    model = wt.WStandardItemModel(3, 2)\n"
        "    for row, (label, value) in enumerate([('A', 30), ('B', 45),\n"
        "                                          ('C', 25)]):\n"
        "        model.set_data(row, 0, label)\n"
        "        model.set_data(row, 1, value)\n"
        "    pie = container.add_widget(chart_mod.WPieChart())\n"
        "    pie.set_model(model)\n"
        "    pie.set_labels_column(0)\n"
        "    pie.set_data_column(1)\n"
        "    pie.set_display_labels(chart_mod.LabelOption.Outside\n"
        "                           | chart_mod.LabelOption.TextLabel)")
        .def(heap_init<ch::WPieChart>(),
             "Construct an empty pie chart. Attach a model and assign "
             "labels / data columns before it can render anything.")
        .def("set_labels_column", &ch::WPieChart::setLabelsColumn,
             "column"_a,
             "Index of the model column whose Display strings become "
             "slice labels.")
        .def_prop_ro("labels_column", &ch::WPieChart::labelsColumn,
             "Current labels-column index.")
        .def("set_data_column", &ch::WPieChart::setDataColumn,
             "column"_a,
             "Index of the model column whose numeric values determine "
             "slice sizes.")
        .def_prop_ro("data_column", &ch::WPieChart::dataColumn,
             "Current data-column index.")
        .def("set_display_labels",
            [](ch::WPieChart& self, int options) {
                self.setDisplayLabels(Wt::WFlags<ch::LabelOption>(
                    static_cast<ch::LabelOption>(options)));
            },
            "options"_a,
            "LabelOption bitmask. e.g. Inside | TextLabel shows the label "
            "text inside each segment; | TextPercentage adds the share %.")
        .def("set_explode", &ch::WPieChart::setExplode,
             "model_row"_a, "factor"_a,
             "Pull the segment for `model_row` away from the centre by "
             "`factor` × pie radius (0.0 = none).")
        .def("set_perspective_enabled", &ch::WPieChart::setPerspectiveEnabled,
             "enabled"_a, "height"_a = 1.0,
             "Render a 3-D-ish tilted pie. `height` is the foreshortening.")
        .def("set_shadow_enabled", &ch::WPieChart::setShadowEnabled,
             "enabled"_a,
             "When True, draw a drop shadow beneath the pie.")
        .def("set_start_angle", &ch::WPieChart::setStartAngle,
             "degrees"_a,
             "Angle (in degrees) where the first slice begins. 0° points "
             "right; 90° points up (counter-clockwise convention).");

}

}  // namespace witty_for_python
