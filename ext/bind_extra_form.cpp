#include "common.hpp"
#include "signal_helpers.hpp"

#include <Wt/WAbstractItemModel.h>  // for WSuggestionPopup.set_model / .model
#include <Wt/WColor.h>
#include <Wt/WColorPicker.h>
#include <Wt/WFormWidget.h>
#include <Wt/WInPlaceEdit.h>
#include <Wt/WPasswordEdit.h>
#include <Wt/WSignal.h>
#include <Wt/WSuggestionPopup.h>
#include <Wt/WTextEdit.h>

#include <string>

namespace witty_for_python {

void register_extra_form(nb::module_& m) {
    // ---- WColor: an RGBA value type ----
    //
    // Used as the value for WColorPicker.color and elsewhere across the Wt
    // graphics surface. The CSS-name constructor accepts "red", "#a0c0e0",
    // "rgb(160,192,224)", etc.; only #rgb / #rrggbb / rgb()/rgba() parse to
    // RGB components, so red/green/blue accessors only return useful values
    // for those forms (named colors round-trip via CSS, not RGB).

    nb::class_<Wt::WColor>(m, "WColor")
        .def(nb::init<>())
        .def(nb::init<int, int, int, int>(),
             "red"_a, "green"_a, "blue"_a, "alpha"_a = 255)
        .def(nb::init<const Wt::WString&>(), "name"_a)
        .def_prop_ro("red", &Wt::WColor::red)
        .def_prop_ro("green", &Wt::WColor::green)
        .def_prop_ro("blue", &Wt::WColor::blue)
        .def_prop_ro("alpha", &Wt::WColor::alpha)
        .def_prop_ro("is_default", &Wt::WColor::isDefault,
            "True for the default-constructed color (transparent/inherited).")
        .def("set_rgb", &Wt::WColor::setRgb,
             "red"_a, "green"_a, "blue"_a, "alpha"_a = 255)
        .def("set_name", &Wt::WColor::setName, "name"_a);

    // ---- WPasswordEdit: a password input with built-in length/pattern checks ----
    //
    // Inherits WLineEdit; the password-specific knobs (min/max length,
    // pattern, required) configure an internal validator that runs alongside
    // any explicit validator set via WFormWidget.set_validator. Setting a
    // custom validator turns the built-in checks off.

    nb::class_<Wt::WPasswordEdit, Wt::WLineEdit>(m, "WPasswordEdit")
        .def(heap_init<Wt::WPasswordEdit>())
        .def_prop_rw("native_control",
            &Wt::WPasswordEdit::nativeControl,
            &Wt::WPasswordEdit::setNativeControl,
            "Use the browser's native <input type=password> behavior. "
            "Disable for full Wt-styled rendering.")
        .def_prop_rw("min_length",
            &Wt::WPasswordEdit::minLength,
            &Wt::WPasswordEdit::setMinLength,
            "Minimum password length. 0 means no minimum.")
        .def_prop_rw("required",
            &Wt::WPasswordEdit::isRequired,
            &Wt::WPasswordEdit::setRequired,
            "When True, an empty field fails validation.")
        .def_prop_rw("pattern",
            [](const Wt::WPasswordEdit& w) { return w.pattern(); },
            [](Wt::WPasswordEdit& w, const Wt::WString& p) { w.setPattern(p); },
            "Regular expression the password must match. Empty disables.")
        .def_prop_rw("invalid_too_long_text",
            [](const Wt::WPasswordEdit& w) { return w.invalidTooLongText(); },
            [](Wt::WPasswordEdit& w, const Wt::WString& t) {
                w.setInvalidTooLongText(t);
            },
            "Validation message shown when the entered password exceeds "
            "max_length.")
        .def_prop_rw("invalid_too_short_text",
            [](const Wt::WPasswordEdit& w) { return w.invalidTooShortText(); },
            [](Wt::WPasswordEdit& w, const Wt::WString& t) {
                w.setInvalidTooShortText(t);
            },
            "Validation message shown when shorter than min_length.")
        .def_prop_rw("invalid_no_match_text",
            [](const Wt::WPasswordEdit& w) { return w.invalidNoMatchText(); },
            [](Wt::WPasswordEdit& w, const Wt::WString& t) {
                w.setInvalidNoMatchText(t);
            },
            "Validation message when the password doesn't match pattern.")
        .def_prop_rw("invalid_blank_text",
            [](const Wt::WPasswordEdit& w) { return w.invalidBlankText(); },
            [](Wt::WPasswordEdit& w, const Wt::WString& t) {
                w.setInvalidBlankText(t);
            },
            "Validation message when required and left blank.");

    // ---- WInPlaceEdit: text that turns into a line-edit on click ----
    //
    // Bound as a direct WWidget descendant (skipping WCompositeWidget, like
    // other composite widgets in this binding). value_changed fires when the
    // user accepts the edit via the save button or Enter key.

    nb::class_<Wt::WInPlaceEdit, Wt::WWidget>(m, "WInPlaceEdit")
        .def(heap_init<Wt::WInPlaceEdit, const Wt::WString&>(), "text"_a)
        .def(heap_init<Wt::WInPlaceEdit, bool, const Wt::WString&>(),
             "with_buttons"_a, "text"_a,
             "When `with_buttons` is False, the edit auto-saves on blur and "
             "no save/cancel buttons are shown.")
        .def_prop_rw("text",
            [](const Wt::WInPlaceEdit& w) { return w.text(); },
            [](Wt::WInPlaceEdit& w, const Wt::WString& t) { w.setText(t); })
        .def_prop_rw("placeholder_text",
            [](const Wt::WInPlaceEdit& w) { return w.placeholderText(); },
            [](Wt::WInPlaceEdit& w, const Wt::WString& t) {
                w.setPlaceholderText(t);
            })
        .def("set_buttons_enabled", &Wt::WInPlaceEdit::setButtonsEnabled,
             "enabled"_a = true,
             "Show/hide the save/cancel buttons. When hidden, the edit "
             "auto-saves on Enter / blur.")
        .def_prop_ro("line_edit", &Wt::WInPlaceEdit::lineEdit,
                     nb::rv_policy::reference_internal,
                     "The internal WLineEdit, exposed for fine-grained "
                     "styling (placeholder, max length, validator).")
        .def_prop_ro("value_changed", &Wt::WInPlaceEdit::valueChanged,
                     nb::rv_policy::reference_internal,
                     "Signal[str] — fires with the new text when the user "
                     "accepts an edit.");

    // ---- PopupTrigger: when WSuggestionPopup shows itself ----

    nb::enum_<Wt::PopupTrigger>(m, "PopupTrigger", nb::is_flag())
        .value("Editing", Wt::PopupTrigger::Editing)
        .value("DropDownIcon", Wt::PopupTrigger::DropDownIcon);

    // ---- WSuggestionPopup::Options: autocomplete behaviour config ----
    //
    // Default-construct, then set fields; pass to the WSuggestionPopup
    // constructor. Wt's docs cover the meaning of each — typical defaults
    // for a "match anywhere, no list-mode" popup:
    //
    //   opts = wt.WSuggestionPopup.Options()
    //   opts.highlight_begin_tag = "<b>"
    //   opts.highlight_end_tag = "</b>"
    //   opts.list_separator = "\0"       # single-value field (not a list)
    //   opts.whitespace = " \\n"
    //   opts.word_separators = " "
    //   opts.append_replaced_text = ""
    //
    // Empty defaults work for many cases but Wt will warn at runtime if
    // you leave something it considers required blank.

    nb::class_<Wt::WSuggestionPopup::Options> options(m, "Options");
    options
        .def("__init__", [](Wt::WSuggestionPopup::Options* self) {
            // The Options struct has no public C++ default ctor (only Java),
            // so we placement-new zero-initialised and let the user fill in
            // the fields they care about.
            new (self) Wt::WSuggestionPopup::Options{};
            self->listSeparator = '\0';
        })
        .def_rw("highlight_begin_tag",
                &Wt::WSuggestionPopup::Options::highlightBeginTag)
        .def_rw("highlight_end_tag",
                &Wt::WSuggestionPopup::Options::highlightEndTag)
        .def_prop_rw("list_separator",
            [](const Wt::WSuggestionPopup::Options& o) {
                // Expose char as a 1-char string for Python ergonomics.
                return o.listSeparator == '\0'
                    ? std::string()
                    : std::string(1, o.listSeparator);
            },
            [](Wt::WSuggestionPopup::Options& o, const std::string& s) {
                o.listSeparator = s.empty() ? '\0' : s[0];
            },
            "Separator char for list-of-values fields. Empty/`'\\0'` "
            "means the field holds a single value (no list).")
        .def_rw("whitespace",
                &Wt::WSuggestionPopup::Options::whitespace)
        .def_rw("word_separators",
                &Wt::WSuggestionPopup::Options::wordSeparators)
        .def_rw("append_replaced_text",
                &Wt::WSuggestionPopup::Options::appendReplacedText)
        .def_rw("word_start_regexp",
                &Wt::WSuggestionPopup::Options::wordStartRegexp);

    // ---- Signal<int, WFormWidget*> for WSuggestionPopup.activated ----
    //
    // Fires when the user picks a suggestion. The int is the row index in
    // the popup's model; the WFormWidget* is the edit being assisted (so
    // one popup wired to several edits can disambiguate the source).
    // Bound here (not in bind_signals.cpp) because the WFormWidget* payload
    // makes it WSuggestionPopup-specific in practice.

    nb::class_<Wt::Signal<int, Wt::WFormWidget*>>(m, "IntFormWidgetSignal")
        .def("connect",
            [](Wt::Signal<int, Wt::WFormWidget*>& s, nb::callable cb) {
                return py_connect<Wt::Signal<int, Wt::WFormWidget*>,
                                  int, Wt::WFormWidget*>(s, std::move(cb));
            }, "callable"_a)
        .def("disconnect_all_slots",
            [](Wt::Signal<int, Wt::WFormWidget*>& s) {
                connection_registry_disconnect_all(&s);
            });

    // ---- WSuggestionPopup: autocomplete popup attached to one or more
    //      WFormWidgets ----

    auto popup_cls = nb::class_<Wt::WSuggestionPopup, Wt::WWidget>(
        m, "WSuggestionPopup");
    popup_cls
        .def(heap_init<Wt::WSuggestionPopup, const Wt::WSuggestionPopup::Options&>(), "options"_a,
             "Construct with an Options config — see WSuggestionPopup.Options.")
        .def("for_edit",
            // Take triggers as a plain int so callers can OR bit values
            // (PopupTrigger.Editing | PopupTrigger.DropDownIcon) without
            // needing a separate WFlags caster. Same shape as
            // WMessageBox.set_standard_buttons in bind_navigation.cpp.
            [](Wt::WSuggestionPopup& p, Wt::WFormWidget* edit, int triggers) {
                p.forEdit(edit, Wt::WFlags<Wt::PopupTrigger>(
                    static_cast<Wt::PopupTrigger>(triggers)));
            },
            "edit"_a,
            "triggers"_a = static_cast<int>(Wt::PopupTrigger::Editing),
            "Attach this popup to a form widget. The popup will offer "
            "completions while the user edits the field. Pass triggers as "
            "a bitwise OR of PopupTrigger values.")
        .def("remove_edit", &Wt::WSuggestionPopup::removeEdit, "edit"_a)
        .def("show_at", &Wt::WSuggestionPopup::showAt, "edit"_a)
        .def("clear_suggestions", &Wt::WSuggestionPopup::clearSuggestions)
        .def("add_suggestion",
            [](Wt::WSuggestionPopup& p, const Wt::WString& text,
               const Wt::WString& value) {
                p.addSuggestion(text, value);
            },
            "text"_a, "value"_a = Wt::WString(),
            "Add a string to the autocomplete list. If `value` is empty, "
            "the displayed `text` is also inserted on selection.")
        .def_prop_rw("filter_length",
            &Wt::WSuggestionPopup::filterLength,
            &Wt::WSuggestionPopup::setFilterLength,
            "Minimum input length before the popup activates.")
        .def_prop_rw("default_index",
            &Wt::WSuggestionPopup::defaultIndex,
            &Wt::WSuggestionPopup::setDefaultIndex,
            "Row index pre-selected when the popup first opens; -1 for none.")
        .def_prop_ro("current_item", &Wt::WSuggestionPopup::currentItem,
            "Index of the currently-highlighted suggestion; -1 if none.")
        .def("set_drop_down_icon_unfiltered",
             &Wt::WSuggestionPopup::setDropDownIconUnfiltered,
             "unfiltered"_a,
             "When True, clicking the drop-down icon shows all suggestions "
             "regardless of current input. Pairs with PopupTrigger.DropDownIcon.")
        .def("set_auto_select_enabled",
             &Wt::WSuggestionPopup::setAutoSelectEnabled, "enabled"_a)
        .def_prop_ro("activated", &Wt::WSuggestionPopup::activated,
                     nb::rv_policy::reference_internal,
                     "IntFormWidgetSignal — fires when the user picks a "
                     "suggestion. Slot receives (row_index, edit_widget); "
                     "edit_widget is whichever WFormWidget the popup was "
                     "for_edit'd against.")
        // model setter/getter — depends on WAbstractItemModel being bound
        // already (register_modelview runs before register_extra_form in
        // module.cpp). Swap the default WStringListModel for a custom one
        // when you need sorting/filtering on the suggestion list.
        .def("set_model", &Wt::WSuggestionPopup::setModel, "model"_a)
        .def_prop_ro("model", &Wt::WSuggestionPopup::model);

    // Re-attach the Options nested class as WSuggestionPopup.Options for
    // ergonomics: `wt.WSuggestionPopup.Options()` (rather than the bare
    // `wt.Options()` it was registered under).
    popup_cls.attr("Options") = options;

    // ---- WColorPicker: HTML5 <input type=color> ----

    nb::class_<Wt::WColorPicker, Wt::WFormWidget>(m, "WColorPicker")
        .def(heap_init<Wt::WColorPicker>())
        .def(heap_init<Wt::WColorPicker, const Wt::WColor&>(), "color"_a)
        .def_prop_rw("color",
            [](const Wt::WColorPicker& w) { return w.color(); },
            [](Wt::WColorPicker& w, const Wt::WColor& c) { w.setColor(c); })
        .def_prop_ro("color_input", &Wt::WColorPicker::colorInput,
                     nb::rv_policy::reference_internal,
                     "EventSignal[] — fires continuously while the user "
                     "drags through the color picker. Use the inherited "
                     "`changed` signal for commit-only notifications.");

    // ---- WTextEdit: rich-text editor backed by TinyMCE ----
    //
    // Extends WTextArea. TinyMCE itself isn't bundled — the application
    // needs to serve a TinyMCE build alongside Wt's resources. See Wt's
    // docs for placement; the default expects /resources/tinymce/.

    nb::class_<Wt::WTextEdit, Wt::WTextArea>(m, "WTextEdit")
        .def(heap_init<Wt::WTextEdit>())
        .def(heap_init<Wt::WTextEdit, const Wt::WString&>(), "text"_a)
        .def_prop_ro("version", &Wt::WTextEdit::version,
            "TinyMCE version currently configured (3 or 4 depending on "
            "what Wt was built against and what's on disk).")
        .def_prop_rw("style_sheet",
            [](const Wt::WTextEdit& w) { return w.styleSheet(); },
            [](Wt::WTextEdit& w, const std::string& s) { w.setStyleSheet(s); },
            "Comma-separated list of stylesheets applied inside the editor "
            "iframe — also drives the 'styleselect' button options.")
        .def("set_extra_plugins", &Wt::WTextEdit::setExtraPlugins, "plugins"_a,
            "Comma-separated TinyMCE plugin names to load on top of the "
            "default 'safari' plugin.")
        .def("set_tool_bar", &Wt::WTextEdit::setToolBar, "row"_a, "config"_a,
            "Configure a single toolbar row by index (0-based). `config` is "
            "a TinyMCE 'theme_advanced_buttons_N' string, e.g. 'bold,italic,|,bullist'.")
        .def("set_configuration_setting", &Wt::WTextEdit::setConfigurationSetting,
            "name"_a, "value"_a,
            "Forward a setting straight to TinyMCE's init() config. "
            "`value` is anything TinyMCE accepts as JSON.");
}

}  // namespace witty_for_python
