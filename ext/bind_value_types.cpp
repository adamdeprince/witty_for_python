#include "common.hpp"

#include <Wt/WAnimation.h>
#include <Wt/WGlobal.h>           // LengthUnit, AnimationEffect, TimingFunction
#include <Wt/WLength.h>

#include <string>

namespace witty_for_python {

void register_value_types(nb::module_& m) {
    // ---- LengthUnit enum ----
    //
    // Used by WLength. Bound up here because it's referenced by many
    // WLength constructors below.

    nb::enum_<Wt::LengthUnit>(m, "LengthUnit")
        .value("FontEm",         Wt::LengthUnit::FontEm)
        .value("FontEx",         Wt::LengthUnit::FontEx)
        .value("Pixel",          Wt::LengthUnit::Pixel)
        .value("Inch",           Wt::LengthUnit::Inch)
        .value("Centimeter",     Wt::LengthUnit::Centimeter)
        .value("Millimeter",     Wt::LengthUnit::Millimeter)
        .value("Point",          Wt::LengthUnit::Point)
        .value("Pica",           Wt::LengthUnit::Pica)
        .value("Percentage",     Wt::LengthUnit::Percentage)
        .value("ViewportWidth",  Wt::LengthUnit::ViewportWidth)
        .value("ViewportHeight", Wt::LengthUnit::ViewportHeight)
        .value("ViewportMin",    Wt::LengthUnit::ViewportMin)
        .value("ViewportMax",    Wt::LengthUnit::ViewportMax);

    // ---- WLength: a CSS-style numeric-value-plus-unit ----
    //
    // Used pervasively in Wt's geometry surface (width, height, margins,
    // column widths, …). Existing bindings in this project accept bare
    // numbers where Wt wants WLength, relying on implicit conversion via
    // the `WLength(double, LengthUnit=Pixel)` constructor; the explicit
    // type is here so callers can also construct percentages, ems, etc.
    //
    // Constructor forms (matching Wt's surface):
    //   - WLength()                        → "auto"
    //   - WLength(value, unit=Pixel)       → numeric with a unit
    //   - WLength(string)                  → parsed CSS length (e.g. "50%")
    //
    // The string-form constructor doubles as the parser for things like
    // "auto", "50%", "12px", "1em" — handy when working with existing
    // CSS values.

    nb::class_<Wt::WLength>(m, "WLength")
        .def(nb::init<>(),
             "Default-construct as 'auto' (no explicit length).")
        .def(nb::init<double, Wt::LengthUnit>(),
             "value"_a, "unit"_a = Wt::LengthUnit::Pixel)
        .def(nb::init<const std::string&>(), "css_text"_a,
             "Parse a CSS length string — e.g. 'auto', '50%', '12px', '1em'.")
        .def_prop_ro("is_auto", &Wt::WLength::isAuto)
        .def_prop_ro("value", &Wt::WLength::value)
        .def_prop_ro("unit", &Wt::WLength::unit)
        .def("to_css_text", &Wt::WLength::cssText,
            "Render as a CSS string Wt's renderer can use.")
        .def("to_pixels", &Wt::WLength::toPixels,
             "font_size"_a = 16.0,
             "Convert to pixels assuming the given root font size (for "
             "em/ex/percentage resolution).")
        .def("__repr__",
            [](const Wt::WLength& l) {
                if (l.isAuto()) return std::string("WLength(auto)");
                return "WLength(" + std::to_string(l.value())
                     + ", " + l.cssText() + ")";
            });

    // ---- AnimationEffect + TimingFunction enums ----

    nb::enum_<Wt::AnimationEffect>(m, "AnimationEffect", nb::is_arithmetic())
        .value("SlideInFromLeft",   Wt::AnimationEffect::SlideInFromLeft)
        .value("SlideInFromRight",  Wt::AnimationEffect::SlideInFromRight)
        .value("SlideInFromBottom", Wt::AnimationEffect::SlideInFromBottom)
        .value("SlideInFromTop",    Wt::AnimationEffect::SlideInFromTop)
        .value("Pop",               Wt::AnimationEffect::Pop)
        .value("Fade",              Wt::AnimationEffect::Fade);

    nb::enum_<Wt::TimingFunction>(m, "TimingFunction")
        .value("Ease",        Wt::TimingFunction::Ease)
        .value("Linear",      Wt::TimingFunction::Linear)
        .value("EaseIn",      Wt::TimingFunction::EaseIn)
        .value("EaseOut",     Wt::TimingFunction::EaseOut)
        .value("EaseInOut",   Wt::TimingFunction::EaseInOut)
        .value("CubicBezier", Wt::TimingFunction::CubicBezier);

    // ---- WAnimation: transition parameters for show/hide ----
    //
    // Used as a parameter to WWidget.animateShow / animateHide / setHidden.
    // Wt also accepts a default-constructed (empty) animation meaning "no
    // transition".

    // The single-effect and two-effect convenience constructors in
    // WAnimation.h are wrapped in `#ifdef WT_TARGET_JAVA` (so they're not
    // visible to our C++ build) — only the default ctor and the WFlags-
    // taking ctor are available. We expose a Python-side single-effect
    // shortcut via the int-flag pattern used elsewhere in the binding.

    nb::class_<Wt::WAnimation>(m, "WAnimation")
        .def(nb::init<>(),
            "Default — an empty animation (no transition).")
        .def("__init__",
            // Construct from a single AnimationEffect (or a bitwise-OR'd
            // int of effects, e.g. SlideInFromLeft | Fade).
            [](Wt::WAnimation* self, int effects,
               Wt::TimingFunction timing, int duration) {
                new (self) Wt::WAnimation(
                    Wt::WFlags<Wt::AnimationEffect>(
                        static_cast<Wt::AnimationEffect>(effects)),
                    timing, duration);
            },
            "effects"_a,
            "timing"_a = Wt::TimingFunction::Linear,
            "duration_ms"_a = 250,
            "Construct from an effect (or `e1 | e2` to combine a slide "
            "with Fade). Timing and duration default to Linear / 250ms.")
        .def_prop_rw("duration",
            &Wt::WAnimation::duration,
            &Wt::WAnimation::setDuration,
            "Length of the animation in milliseconds.")
        .def_prop_rw("timing_function",
            &Wt::WAnimation::timingFunction,
            // setTimingFunction is declared with a four-double cubic-
            // bezier overload too, but Wt's source doesn't ship its
            // definition — we expose only the enum form.
            [](Wt::WAnimation& self, Wt::TimingFunction f) {
                self.setTimingFunction(f);
            })
        .def_prop_ro("empty", &Wt::WAnimation::empty,
            "True for the default (no-effect) animation.");
}

}  // namespace witty_for_python
