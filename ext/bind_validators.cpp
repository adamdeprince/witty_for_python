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

    nb::enum_<Wt::ValidationState>(m, "ValidationState",
        "Outcome of a validator's check on the current input.\n"
        "\n"
        "    Valid         — input acceptable, OK to submit.\n"
        "    InvalidEmpty  — input is empty, validator marks it mandatory.\n"
        "    Invalid       — input present but doesn't satisfy the rule.\n"
        "\n"
        "InvalidEmpty is split out from Invalid because the typical UX\n"
        "shows a different message for 'required field missing' than for\n"
        "'wrong format'.")
        .value("Invalid", Wt::ValidationState::Invalid)
        .value("InvalidEmpty", Wt::ValidationState::InvalidEmpty)
        .value("Valid", Wt::ValidationState::Valid);

    // ---- ValidationResult (= Wt::WValidator::Result) ----
    //
    // Bound at module scope rather than nested under WValidator for the same
    // reason we expose `Coordinates` at the top level: it's a tiny value type
    // and `wt.ValidationResult` reads better than `wt.WValidator.Result`.

    nb::class_<Wt::WValidator::Result>(m, "ValidationResult",
        "Verdict from `WValidator.validate(input)` — a (state, message)\n"
        "pair. The message is the localized text shown to the user when\n"
        "the input is rejected.\n"
        "\n"
        "    r = validator.validate('not-an-int')\n"
        "    if r.state != wt.ValidationState.Valid:\n"
        "        label.text = r.message")
        .def(nb::init<>(),
             "Construct a result with state=Valid and no message.")
        .def(nb::init<Wt::ValidationState>(), "state"_a,
             "Construct a result with the given state and no message.")
        .def(nb::init<Wt::ValidationState, const Wt::WString&>(),
             "state"_a, "message"_a,
             "Construct a result with the given state and an explanatory\n"
             "message (typically a localized 'too short' / 'invalid'\n"
             "string to show next to the input).")
        .def_prop_ro("state", &Wt::WValidator::Result::state,
             "The ValidationState verdict.")
        .def_prop_ro("message", &Wt::WValidator::Result::message,
             "The localized human-readable message; empty when state is Valid.")
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

    nb::class_<Wt::Signal<Wt::WValidator::Result>>(m, "ValidationResultSignal",
        "Signal carrying a ValidationResult payload. Surfaced via\n"
        "`WFormWidget.validated` — fires after the form widget's\n"
        "validator has run.\n"
        "\n"
        "    edit.validated.connect(lambda r: label.text = r.message)")
        .def("connect",
            [](Wt::Signal<Wt::WValidator::Result>& s, nb::callable cb) {
                return py_connect<Wt::Signal<Wt::WValidator::Result>,
                                  Wt::WValidator::Result>(s, std::move(cb));
            }, "callable"_a,
            "Subscribe `callable(result)` to validation events. Returns\n"
            "a Connection; call its `.disconnect()` to stop receiving.")
        .def("disconnect_all_slots",
            [](Wt::Signal<Wt::WValidator::Result>& s) {
                connection_registry_disconnect_all(&s);
            },
            "Drop every connection opened through `connect`. Mostly an\n"
            "internal shutdown hook — most code doesn't need this.");

    // ---- WValidator (base) ----
    //
    // Bound concretely (not as an abstract trampoline) — the user-facing
    // operation is `v.validate(text) -> ValidationResult` plus the mandatory
    // / blank-text knobs that every subclass inherits.

    nb::class_<Wt::WValidator>(m, "WValidator",
        "Base class for input validators. Concrete subclasses (WIntValidator,\n"
        "WDoubleValidator, WRegExpValidator, …) inherit the `mandatory` flag\n"
        "and the empty-input message. Validators are normally attached to a\n"
        "WFormWidget via `form_widget.set_validator(v)`; the form widget then\n"
        "fires `validated` after each input change.\n"
        "\n"
        "    edit = container.add_widget(wt.WLineEdit())\n"
        "    v = wt.WIntValidator(0, 100)\n"
        "    v.mandatory = True\n"
        "    edit.set_validator(v)\n"
        "    edit.validated.connect(lambda r: print(r))")
        .def_prop_rw("mandatory",
            [](const Wt::WValidator& v) { return v.isMandatory(); },
            [](Wt::WValidator& v, bool b) { v.setMandatory(b); },
            "Whether empty input counts as Invalid (specifically as\n"
            "InvalidEmpty). False (the default) makes empty input Valid.")
        .def_prop_rw("invalid_blank_text",
            [](const Wt::WValidator& v) { return v.invalidBlankText(); },
            [](Wt::WValidator& v, const Wt::WString& t) { v.setInvalidBlankText(t); },
            "The message shown when `mandatory` is True and the input\n"
            "is empty. Replaces the default 'this field is required'.")
        .def("validate", &Wt::WValidator::validate, "input"_a,
            "Run the validation rule against `input` and return a\n"
            "ValidationResult. Pure function — does NOT mutate either\n"
            "the validator or the form widget; safe to call from anywhere.");

    // ---- WIntValidator ----

    nb::class_<Wt::WIntValidator, Wt::WValidator>(m, "WIntValidator",
        "Accepts an integer in an optional [bottom, top] range.\n"
        "\n"
        "    edit.set_validator(wt.WIntValidator(0, 100))")
        .def(heap_init<Wt::WIntValidator>(),
             "Construct a validator with no range limits.")
        .def(heap_init<Wt::WIntValidator, int, int>(), "minimum"_a, "maximum"_a,
             "Construct a validator that accepts integers in [minimum,\n"
             "maximum] inclusive.")
        .def_prop_rw("bottom",
            [](const Wt::WIntValidator& v) { return v.bottom(); },
            [](Wt::WIntValidator& v, int b) { v.setBottom(b); },
            "Lowest accepted value (inclusive).")
        .def_prop_rw("top",
            [](const Wt::WIntValidator& v) { return v.top(); },
            [](Wt::WIntValidator& v, int t) { v.setTop(t); },
            "Highest accepted value (inclusive).")
        .def("set_range", &Wt::WIntValidator::setRange,
             "bottom"_a, "top"_a,
             "Set both bounds atomically.")
        .def_prop_rw("invalid_not_a_number_text",
            [](const Wt::WIntValidator& v) { return v.invalidNotANumberText(); },
            [](Wt::WIntValidator& v, const Wt::WString& t) { v.setInvalidNotANumberText(t); },
            "Message shown when the input isn't a valid integer at all.")
        .def_prop_rw("invalid_too_small_text",
            [](const Wt::WIntValidator& v) { return v.invalidTooSmallText(); },
            [](Wt::WIntValidator& v, const Wt::WString& t) { v.setInvalidTooSmallText(t); },
            "Message shown when the integer is below `bottom`.")
        .def_prop_rw("invalid_too_large_text",
            [](const Wt::WIntValidator& v) { return v.invalidTooLargeText(); },
            [](Wt::WIntValidator& v, const Wt::WString& t) { v.setInvalidTooLargeText(t); },
            "Message shown when the integer exceeds `top`.")
        .def_prop_rw("ignore_trailing_spaces",
            [](Wt::WIntValidator& v) { return v.ignoreTrailingSpaces(); },
            [](Wt::WIntValidator& v, bool b) { v.setIgnoreTrailingSpaces(b); },
            "Whether trailing whitespace in the input is stripped before\n"
            "parsing. Useful when users paste numbers with stray spaces.");

    // ---- WDoubleValidator ----

    nb::class_<Wt::WDoubleValidator, Wt::WValidator>(m, "WDoubleValidator",
        "Accepts a floating-point number in an optional [bottom, top] range.\n"
        "\n"
        "    edit.set_validator(wt.WDoubleValidator(0.0, 1.0))")
        .def(heap_init<Wt::WDoubleValidator>(),
             "Construct a validator with no range limits.")
        .def(heap_init<Wt::WDoubleValidator, double, double>(), "minimum"_a, "maximum"_a,
             "Construct a validator that accepts floats in [minimum,\n"
             "maximum] inclusive.")
        .def_prop_rw("bottom",
            [](const Wt::WDoubleValidator& v) { return v.bottom(); },
            [](Wt::WDoubleValidator& v, double b) { v.setBottom(b); },
            "Lowest accepted value (inclusive).")
        .def_prop_rw("top",
            [](const Wt::WDoubleValidator& v) { return v.top(); },
            [](Wt::WDoubleValidator& v, double t) { v.setTop(t); },
            "Highest accepted value (inclusive).")
        .def("set_range", &Wt::WDoubleValidator::setRange,
             "bottom"_a, "top"_a,
             "Set both bounds atomically.")
        .def_prop_rw("invalid_not_a_number_text",
            [](const Wt::WDoubleValidator& v) { return v.invalidNotANumberText(); },
            [](Wt::WDoubleValidator& v, const Wt::WString& t) { v.setInvalidNotANumberText(t); },
            "Message shown when the input isn't a valid number.")
        .def_prop_rw("invalid_too_small_text",
            [](const Wt::WDoubleValidator& v) { return v.invalidTooSmallText(); },
            [](Wt::WDoubleValidator& v, const Wt::WString& t) { v.setInvalidTooSmallText(t); },
            "Message shown when the value is below `bottom`.")
        .def_prop_rw("invalid_too_large_text",
            [](const Wt::WDoubleValidator& v) { return v.invalidTooLargeText(); },
            [](Wt::WDoubleValidator& v, const Wt::WString& t) { v.setInvalidTooLargeText(t); },
            "Message shown when the value exceeds `top`.");

    // ---- WLengthValidator ----

    nb::class_<Wt::WLengthValidator, Wt::WValidator>(m, "WLengthValidator",
        "Accepts text whose length (in characters) falls within an\n"
        "optional [minimum_length, maximum_length] range. Useful for\n"
        "things like 'username 3–20 chars'.\n"
        "\n"
        "    edit.set_validator(wt.WLengthValidator(3, 20))")
        .def(heap_init<Wt::WLengthValidator>(),
             "Construct a validator with no length limits.")
        .def(heap_init<Wt::WLengthValidator, int, int>(),
             "minimum_length"_a, "maximum_length"_a,
             "Construct a validator with the given length bounds (inclusive).")
        .def_prop_rw("minimum_length",
            [](const Wt::WLengthValidator& v) { return v.minimumLength(); },
            [](Wt::WLengthValidator& v, int n) { v.setMinimumLength(n); },
            "Shortest accepted length (inclusive).")
        .def_prop_rw("maximum_length",
            [](const Wt::WLengthValidator& v) { return v.maximumLength(); },
            [](Wt::WLengthValidator& v, int n) { v.setMaximumLength(n); },
            "Longest accepted length (inclusive).")
        .def_prop_rw("invalid_too_short_text",
            [](const Wt::WLengthValidator& v) { return v.invalidTooShortText(); },
            [](Wt::WLengthValidator& v, const Wt::WString& t) { v.setInvalidTooShortText(t); },
            "Message shown when the input is shorter than `minimum_length`.")
        .def_prop_rw("invalid_too_long_text",
            [](const Wt::WLengthValidator& v) { return v.invalidTooLongText(); },
            [](Wt::WLengthValidator& v, const Wt::WString& t) { v.setInvalidTooLongText(t); },
            "Message shown when the input exceeds `maximum_length`.");

    // ---- WRegExpValidator ----

    nb::class_<Wt::WRegExpValidator, Wt::WValidator>(m, "WRegExpValidator",
        "Accepts text matching a regular-expression pattern. Useful for\n"
        "phone numbers, postal codes, custom formats.\n"
        "\n"
        "    edit.set_validator(wt.WRegExpValidator(r'\\d{5}'))     # US ZIP")
        .def(heap_init<Wt::WRegExpValidator>(),
             "Construct a validator with no pattern (matches anything).")
        .def(heap_init<Wt::WRegExpValidator, const Wt::WString&>(), "pattern"_a,
             "Construct a validator that requires the input to match\n"
             "`pattern` end-to-end.")
        .def_prop_rw("pattern",
            [](const Wt::WRegExpValidator& v) { return v.regExpPattern(); },
            [](Wt::WRegExpValidator& v, const Wt::WString& p) { v.setRegExp(p); },
            "The regex pattern. Wt uses its own regex syntax (close to\n"
            "PCRE); test on the form to confirm matching behavior.")
        .def_prop_rw("invalid_no_match_text",
            [](const Wt::WRegExpValidator& v) { return v.invalidNoMatchText(); },
            [](Wt::WRegExpValidator& v, const Wt::WString& t) { v.setInvalidNoMatchText(t); },
            "Message shown when the input doesn't match `pattern`.");

    // ---- WEmailValidator ----

    nb::class_<Wt::WEmailValidator, Wt::WValidator>(m, "WEmailValidator",
        "Accepts a syntactically-valid email address (or a comma-separated\n"
        "list when `multiple` is True). Doesn't verify the address actually\n"
        "exists — that needs an out-of-band confirm step.\n"
        "\n"
        "    edit.set_validator(wt.WEmailValidator())")
        .def(heap_init<Wt::WEmailValidator>(),
             "Construct an email validator with the default RFC-5322-ish\n"
             "pattern accepting a single address.")
        .def_prop_rw("multiple",
            [](const Wt::WEmailValidator& v) { return v.multiple(); },
            [](Wt::WEmailValidator& v, bool m) { v.setMultiple(m); },
            "Accept a comma-separated list of addresses instead of just one.")
        .def_prop_rw("pattern",
            [](const Wt::WEmailValidator& v) { return v.pattern(); },
            [](Wt::WEmailValidator& v, const Wt::WString& p) { v.setPattern(p); },
            "Override the built-in regex with a custom pattern.")
        .def_prop_rw("invalid_not_an_email_address_text",
            [](const Wt::WEmailValidator& v) { return v.invalidNotAnEmailAddressText(); },
            [](Wt::WEmailValidator& v, const Wt::WString& t) {
                v.setInvalidNotAnEmailAddressText(t);
            },
            "Message shown when the input doesn't look like an email address.");

    // ---- WStackedValidator ----

    nb::class_<Wt::WStackedValidator, Wt::WValidator>(m, "WStackedValidator",
        "Composite validator that runs a sequence of sub-validators in\n"
        "order; the first one that rejects wins. Useful for combining\n"
        "concerns (length AND pattern, range AND custom rule).\n"
        "\n"
        "    stacked = wt.WStackedValidator()\n"
        "    stacked.add_validator(wt.WLengthValidator(8, 64))\n"
        "    stacked.add_validator(wt.WRegExpValidator(r'.*[A-Z].*'))\n"
        "    edit.set_validator(stacked)")
        .def(heap_init<Wt::WStackedValidator>(),
             "Construct an empty stacked validator.")
        .def("add_validator",
            [](Wt::WStackedValidator& self, std::shared_ptr<Wt::WValidator> v) {
                self.addValidator(v);
            }, "validator"_a,
            "Append `validator` to the end of the chain.")
        .def("insert_validator",
            [](Wt::WStackedValidator& self, int index, std::shared_ptr<Wt::WValidator> v) {
                self.insertValidator(index, v);
            }, "index"_a, "validator"_a,
            "Insert `validator` at `index` so it runs before later ones.")
        .def("remove_validator",
            [](Wt::WStackedValidator& self, std::shared_ptr<Wt::WValidator> v) {
                self.removeValidator(v);
            }, "validator"_a,
            "Remove `validator` from the chain. No-op if it isn't there.")
        .def_prop_ro("size", &Wt::WStackedValidator::size,
            "Number of sub-validators currently in the chain.")
        .def("clear", &Wt::WStackedValidator::clear,
            "Drop every sub-validator.");

}

}  // namespace witty_for_python
