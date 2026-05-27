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

    nb::enum_<ch::SeriesType>(chart, "SeriesType")
        .value("Point", ch::SeriesType::Point)
        .value("Line",  ch::SeriesType::Line)
        .value("Curve", ch::SeriesType::Curve)
        .value("Bar",   ch::SeriesType::Bar);

    nb::enum_<ch::MarkerType>(chart, "MarkerType")
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

    nb::enum_<ch::FillRangeType>(chart, "FillRangeType")
        .value("None_",        ch::FillRangeType::None)
        .value("MinimumValue", ch::FillRangeType::MinimumValue)
        .value("MaximumValue", ch::FillRangeType::MaximumValue)
        .value("ZeroValue",    ch::FillRangeType::ZeroValue);

    nb::enum_<ch::ChartType>(chart, "ChartType")
        .value("Category", ch::ChartType::Category)
        .value("Scatter",  ch::ChartType::Scatter);

    nb::enum_<ch::LegendLocation>(chart, "LegendLocation")
        .value("Inside",  ch::LegendLocation::Inside)
        .value("Outside", ch::LegendLocation::Outside);

    nb::enum_<ch::AxisScale>(chart, "AxisScale")
        .value("Discrete", ch::AxisScale::Discrete)
        .value("Linear",   ch::AxisScale::Linear)
        .value("Log",      ch::AxisScale::Log)
        .value("Date",     ch::AxisScale::Date)
        .value("DateTime", ch::AxisScale::DateTime);

    nb::enum_<ch::AxisValue>(chart, "AxisValue", nb::is_arithmetic())
        .value("Minimum", ch::AxisValue::Minimum)
        .value("Maximum", ch::AxisValue::Maximum)
        .value("Zero",    ch::AxisValue::Zero)
        .value("Both",    ch::AxisValue::Both);

    nb::enum_<ch::Axis>(chart, "Axis")
        .value("X",  ch::Axis::X)
        .value("Y",  ch::Axis::Y)
        .value("Y2", ch::Axis::Y2);

    nb::enum_<ch::LabelOption>(chart, "LabelOption", nb::is_arithmetic())
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

    nb::class_<ch::WAxis>(chart, "WAxis")
        .def_prop_rw("visible",
            &ch::WAxis::isVisible,
            &ch::WAxis::setVisible)
        .def("set_location", &ch::WAxis::setLocation, "value"_a,
             "Where on the perpendicular axis this one sits — Minimum, "
             "Maximum, Zero, or Both.")
        .def("set_scale", &ch::WAxis::setScale, "scale"_a)
        .def_prop_ro("scale", &ch::WAxis::scale)
        .def("set_minimum", &ch::WAxis::setMinimum, "minimum"_a)
        .def_prop_ro("minimum", &ch::WAxis::minimum)
        .def("set_maximum", &ch::WAxis::setMaximum, "maximum"_a)
        .def_prop_ro("maximum", &ch::WAxis::maximum)
        .def("set_range", &ch::WAxis::setRange, "minimum"_a, "maximum"_a)
        .def("set_auto_limits",
            [](ch::WAxis& self, int locations) {
                self.setAutoLimits(Wt::WFlags<ch::AxisValue>(
                    static_cast<ch::AxisValue>(locations)));
            },
            "locations"_a,
            "AxisValue bitmask of which limits should auto-fit data.")
        .def("set_title", &ch::WAxis::setTitle, "title"_a)
        .def_prop_ro("title", &ch::WAxis::title);

    // ---- WDataSeries ----
    //
    // One curve / bar series in a cartesian chart. Constructed
    // standalone, then handed to `chart.add_series(series)` which moves
    // ownership in. The series can be styled (pen, brush, marker) before
    // OR after attaching to a chart.

    nb::class_<ch::WDataSeries>(chart, "WDataSeries")
        .def("__init__",
            [](ch::WDataSeries* self, int model_column,
               ch::SeriesType type, ch::Axis axis) {
                new (self) ch::WDataSeries(model_column, type, axis);
            },
            "model_column"_a, "type"_a = ch::SeriesType::Point,
            "axis"_a = ch::Axis::Y1,
            "Construct a series reading values from `model_column` of the "
            "chart's model, rendered with the given style on the given "
            "Y axis (Y1 or Y2).")
        .def_prop_rw("type",
            &ch::WDataSeries::type,
            &ch::WDataSeries::setType)
        .def_prop_rw("model_column",
            &ch::WDataSeries::modelColumn,
            &ch::WDataSeries::setModelColumn)
        .def_prop_rw("x_series_column",
            &ch::WDataSeries::XSeriesColumn,
            &ch::WDataSeries::setXSeriesColumn,
            "Override the model column used for X values; default -1 = "
            "use the chart-wide X-series column.")
        .def_prop_rw("stacked",
            &ch::WDataSeries::isStacked,
            &ch::WDataSeries::setStacked)
        .def("bind_to_y_axis", &ch::WDataSeries::bindToYAxis, "y_axis"_a)
        .def("set_pen", &ch::WDataSeries::setPen, "pen"_a)
        .def("set_brush", &ch::WDataSeries::setBrush, "brush"_a)
        .def("set_fill_range", &ch::WDataSeries::setFillRange, "fill_range"_a)
        .def("set_marker", &ch::WDataSeries::setMarker, "marker"_a)
        .def("set_marker_size", &ch::WDataSeries::setMarkerSize, "size"_a)
        .def("set_marker_pen", &ch::WDataSeries::setMarkerPen, "pen"_a)
        .def("set_marker_brush", &ch::WDataSeries::setMarkerBrush, "brush"_a)
        .def("set_bar_width", &ch::WDataSeries::setBarWidth, "width"_a)
        .def("set_hidden", &ch::WDataSeries::setHidden, "hidden"_a)
        .def_prop_ro("is_hidden", &ch::WDataSeries::isHidden);

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

    nb::class_<ch::WAbstractChart, Wt::WInteractWidget>(chart, "WAbstractChart")
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
        .def("set_title", &ch::WAbstractChart::setTitle, "title"_a)
        .def_prop_ro("title", &ch::WAbstractChart::title)
        .def("set_background", &ch::WAbstractChart::setBackground,
             "background"_a)
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

    nb::class_<ch::WCartesianChart, ch::WAbstractChart>(chart, "WCartesianChart")
        .def(nb::init<>())
        .def(nb::init<ch::ChartType>(), "type"_a)
        .def_prop_rw("type",
            &ch::WCartesianChart::type,
            &ch::WCartesianChart::setType)
        .def_prop_rw("legend_enabled",
            &ch::WCartesianChart::isLegendEnabled,
            &ch::WCartesianChart::setLegendEnabled,
            "When True, render a legend listing each series.")
        .def("set_legend_location", &ch::WCartesianChart::setLegendLocation,
             "side"_a, "alignment"_a, "location"_a)
        .def("add_series",
            // Ownership transfers via unique_ptr; the wrapper becomes
            // non-owning. Return the raw pointer so users can keep
            // styling the series afterwards.
            [](ch::WCartesianChart& self,
               std::unique_ptr<ch::WDataSeries> series) -> ch::WDataSeries* {
                ch::WDataSeries* raw = series.get();
                self.addSeries(std::move(series));
                return raw;
            },
            "series"_a,
            nb::rv_policy::reference_internal)
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

    nb::class_<ch::WPieChart, ch::WAbstractChart>(chart, "WPieChart")
        .def(nb::init<>())
        .def("set_labels_column", &ch::WPieChart::setLabelsColumn,
             "column"_a)
        .def_prop_ro("labels_column", &ch::WPieChart::labelsColumn)
        .def("set_data_column", &ch::WPieChart::setDataColumn,
             "column"_a)
        .def_prop_ro("data_column", &ch::WPieChart::dataColumn)
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
             "enabled"_a)
        .def("set_start_angle", &ch::WPieChart::setStartAngle,
             "degrees"_a,
             "Angle (in degrees) where the first slice begins. 0° points "
             "right; 90° points up (counter-clockwise convention).");

}

}  // namespace witty_for_python
