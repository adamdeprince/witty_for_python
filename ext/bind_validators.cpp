#include "common.hpp"
#include "signal_helpers.hpp"

#include <Wt/WDoubleValidator.h>
#include <Wt/WEmailValidator.h>
#include <Wt/WFormWidget.h>
#include <Wt/WGlobal.h>            // Wt::ValidationState
#include <Wt/WIntValidator.h>
#include <Wt/WLengthValidator.h>
#include <Wt/WRegExpValidator.h>
#include <Wt/WStackedValidator.h>
#include <Wt/WValidator.h>

#include <memory>
#include <string>

namespace witty_for_python {

void register_validators(nb::module_& m) {
    // ---- ValidationState enum ----

    nb::enum_<Wt::ValidationState>(m, "ValidationState")
        .value("Invalid", Wt::ValidationState::Invalid)
        .value("InvalidEmpty", Wt::ValidationState::InvalidEmpty)
        .value("Valid", Wt::ValidationState::Valid);

    // ---- ValidationResult (= Wt::WValidator::Result) ----
    //
    // Bound at module scope rather than nested under WValidator for the same
    // reason we expose `Coordinates` at the top level: it's a tiny value type
    // and `wt.ValidationResult` reads better than `wt.WValidator.Result`.

    nb::class_<Wt::WValidator::Result>(m, "ValidationResult")
        .def(nb::init<>())
        .def(nb::init<Wt::ValidationState>(), "state"_a)
        .def(nb::init<Wt::ValidationState, const Wt::WString&>(),
             "state"_a, "message"_a)
        .def_prop_ro("state", &Wt::WValidator::Result::state)
        .def_prop_ro("message", &Wt::WValidator::Result::message)
        .def("__repr__", [](const Wt::WValidator::Result& r) {
            const char* state_name = "?";
            switch (r.state()) {
                case Wt::ValidationState::Invalid:      state_name = "Invalid"; break;
                case Wt::ValidationState::InvalidEmpty: state_name = "InvalidEmpty"; break;
                case Wt::ValidationState::Valid:        state_name = "Valid"; break;
            }
            std::string out = "ValidationResult(state=";
            out += state_name;
            std::string msg = r.message().toUTF8();
            if (!msg.empty()) {
                out += ", message=";
                out += msg;
            }
            out += ")";
            return out;
        });

    // ---- Signal<ValidationResult> for WFormWidget::validated() ----

    nb::class_<Wt::Signal<Wt::WValidator::Result>>(m, "ValidationResultSignal")
        .def("connect",
            [](Wt::Signal<Wt::WValidator::Result>& s, nb::callable cb) {
                return py_connect<Wt::Signal<Wt::WValidator::Result>,
                                  Wt::WValidator::Result>(s, std::move(cb));
            }, "callable"_a)
        .def("disconnect_all_slots",
            [](Wt::Signal<Wt::WValidator::Result>& s) {
                connection_registry_disconnect_all(&s);
            });

    // ---- WValidator (base) ----
    //
    // Bound concretely (not as an abstract trampoline) — the user-facing
    // operation is `v.validate(text) -> ValidationResult` plus the mandatory
    // / blank-text knobs that every subclass inherits.

    nb::class_<Wt::WValidator>(m, "WValidator")
        .def_prop_rw("mandatory",
            [](const Wt::WValidator& v) { return v.isMandatory(); },
            [](Wt::WValidator& v, bool b) { v.setMandatory(b); })
        .def_prop_rw("invalid_blank_text",
            [](const Wt::WValidator& v) { return v.invalidBlankText(); },
            [](Wt::WValidator& v, const Wt::WString& t) { v.setInvalidBlankText(t); })
        .def("validate", &Wt::WValidator::validate, "input"_a);

    // ---- WIntValidator ----

    nb::class_<Wt::WIntValidator, Wt::WValidator>(m, "WIntValidator")
        .def(heap_init<Wt::WIntValidator>())
        .def(heap_init<Wt::WIntValidator, int, int>(), "minimum"_a, "maximum"_a)
        .def_prop_rw("bottom",
            [](const Wt::WIntValidator& v) { return v.bottom(); },
            [](Wt::WIntValidator& v, int b) { v.setBottom(b); })
        .def_prop_rw("top",
            [](const Wt::WIntValidator& v) { return v.top(); },
            [](Wt::WIntValidator& v, int t) { v.setTop(t); })
        .def("set_range", &Wt::WIntValidator::setRange,
             "bottom"_a, "top"_a)
        .def_prop_rw("invalid_not_a_number_text",
            [](const Wt::WIntValidator& v) { return v.invalidNotANumberText(); },
            [](Wt::WIntValidator& v, const Wt::WString& t) { v.setInvalidNotANumberText(t); })
        .def_prop_rw("invalid_too_small_text",
            [](const Wt::WIntValidator& v) { return v.invalidTooSmallText(); },
            [](Wt::WIntValidator& v, const Wt::WString& t) { v.setInvalidTooSmallText(t); })
        .def_prop_rw("invalid_too_large_text",
            [](const Wt::WIntValidator& v) { return v.invalidTooLargeText(); },
            [](Wt::WIntValidator& v, const Wt::WString& t) { v.setInvalidTooLargeText(t); })
        .def_prop_rw("ignore_trailing_spaces",
            [](Wt::WIntValidator& v) { return v.ignoreTrailingSpaces(); },
            [](Wt::WIntValidator& v, bool b) { v.setIgnoreTrailingSpaces(b); });

    // ---- WDoubleValidator ----

    nb::class_<Wt::WDoubleValidator, Wt::WValidator>(m, "WDoubleValidator")
        .def(heap_init<Wt::WDoubleValidator>())
        .def(heap_init<Wt::WDoubleValidator, double, double>(), "minimum"_a, "maximum"_a)
        .def_prop_rw("bottom",
            [](const Wt::WDoubleValidator& v) { return v.bottom(); },
            [](Wt::WDoubleValidator& v, double b) { v.setBottom(b); })
        .def_prop_rw("top",
            [](const Wt::WDoubleValidator& v) { return v.top(); },
            [](Wt::WDoubleValidator& v, double t) { v.setTop(t); })
        .def("set_range", &Wt::WDoubleValidator::setRange,
             "bottom"_a, "top"_a)
        .def_prop_rw("invalid_not_a_number_text",
            [](const Wt::WDoubleValidator& v) { return v.invalidNotANumberText(); },
            [](Wt::WDoubleValidator& v, const Wt::WString& t) { v.setInvalidNotANumberText(t); })
        .def_prop_rw("invalid_too_small_text",
            [](const Wt::WDoubleValidator& v) { return v.invalidTooSmallText(); },
            [](Wt::WDoubleValidator& v, const Wt::WString& t) { v.setInvalidTooSmallText(t); })
        .def_prop_rw("invalid_too_large_text",
            [](const Wt::WDoubleValidator& v) { return v.invalidTooLargeText(); },
            [](Wt::WDoubleValidator& v, const Wt::WString& t) { v.setInvalidTooLargeText(t); });

    // ---- WLengthValidator ----

    nb::class_<Wt::WLengthValidator, Wt::WValidator>(m, "WLengthValidator")
        .def(heap_init<Wt::WLengthValidator>())
        .def(heap_init<Wt::WLengthValidator, int, int>(), "minimum_length"_a, "maximum_length"_a)
        .def_prop_rw("minimum_length",
            [](const Wt::WLengthValidator& v) { return v.minimumLength(); },
            [](Wt::WLengthValidator& v, int n) { v.setMinimumLength(n); })
        .def_prop_rw("maximum_length",
            [](const Wt::WLengthValidator& v) { return v.maximumLength(); },
            [](Wt::WLengthValidator& v, int n) { v.setMaximumLength(n); })
        .def_prop_rw("invalid_too_short_text",
            [](const Wt::WLengthValidator& v) { return v.invalidTooShortText(); },
            [](Wt::WLengthValidator& v, const Wt::WString& t) { v.setInvalidTooShortText(t); })
        .def_prop_rw("invalid_too_long_text",
            [](const Wt::WLengthValidator& v) { return v.invalidTooLongText(); },
            [](Wt::WLengthValidator& v, const Wt::WString& t) { v.setInvalidTooLongText(t); });

    // ---- WRegExpValidator ----

    nb::class_<Wt::WRegExpValidator, Wt::WValidator>(m, "WRegExpValidator")
        .def(heap_init<Wt::WRegExpValidator>())
        .def(heap_init<Wt::WRegExpValidator, const Wt::WString&>(), "pattern"_a)
        .def_prop_rw("pattern",
            [](const Wt::WRegExpValidator& v) { return v.regExpPattern(); },
            [](Wt::WRegExpValidator& v, const Wt::WString& p) { v.setRegExp(p); })
        .def_prop_rw("invalid_no_match_text",
            [](const Wt::WRegExpValidator& v) { return v.invalidNoMatchText(); },
            [](Wt::WRegExpValidator& v, const Wt::WString& t) { v.setInvalidNoMatchText(t); });

    // ---- WEmailValidator ----

    nb::class_<Wt::WEmailValidator, Wt::WValidator>(m, "WEmailValidator")
        .def(heap_init<Wt::WEmailValidator>())
        .def_prop_rw("multiple",
            [](const Wt::WEmailValidator& v) { return v.multiple(); },
            [](Wt::WEmailValidator& v, bool m) { v.setMultiple(m); })
        .def_prop_rw("pattern",
            [](const Wt::WEmailValidator& v) { return v.pattern(); },
            [](Wt::WEmailValidator& v, const Wt::WString& p) { v.setPattern(p); })
        .def_prop_rw("invalid_not_an_email_address_text",
            [](const Wt::WEmailValidator& v) { return v.invalidNotAnEmailAddressText(); },
            [](Wt::WEmailValidator& v, const Wt::WString& t) {
                v.setInvalidNotAnEmailAddressText(t);
            });

    // ---- WStackedValidator ----

    nb::class_<Wt::WStackedValidator, Wt::WValidator>(m, "WStackedValidator")
        .def(heap_init<Wt::WStackedValidator>())
        .def("add_validator",
            [](Wt::WStackedValidator& self, std::shared_ptr<Wt::WValidator> v) {
                self.addValidator(v);
            }, "validator"_a)
        .def("insert_validator",
            [](Wt::WStackedValidator& self, int index, std::shared_ptr<Wt::WValidator> v) {
                self.insertValidator(index, v);
            }, "index"_a, "validator"_a)
        .def("remove_validator",
            [](Wt::WStackedValidator& self, std::shared_ptr<Wt::WValidator> v) {
                self.removeValidator(v);
            }, "validator"_a)
        .def_prop_ro("size", &Wt::WStackedValidator::size)
        .def("clear", &Wt::WStackedValidator::clear);

}

}  // namespace witty_for_python
