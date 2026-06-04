#include "common.hpp"

#include <Wt/WGlobal.h>      // Wt::TextFormat
#include <Wt/WTemplate.h>
#include <Wt/WWidget.h>

#include <memory>
#include <string>

namespace witty_for_python {

void register_template(nb::module_& m) {
    // ---- TextFormat enum ----
    //
    // Used by WTemplate::bind_string, WMessageBox::set_text, and others.
    // First user-visible appearance is here — relocate if more callers
    // need it before another binding file is touched.

    nb::enum_<Wt::TextFormat>(m, "TextFormat",
        "How a piece of text should be interpreted when rendered.\n"
        "`XHTML` is sanitised XHTML — tags allowed but checked for\n"
        "common XSS vectors. `UnsafeXHTML` is raw, unfiltered XHTML —\n"
        "use only with content you trust completely. `Plain` escapes\n"
        "everything so the string appears verbatim in the page.")
        .value("XHTML",       Wt::TextFormat::XHTML)
        .value("UnsafeXHTML", Wt::TextFormat::UnsafeXHTML)
        .value("Plain",       Wt::TextFormat::Plain);

    nb::enum_<Wt::TemplateWidgetIdMode>(m, "TemplateWidgetIdMode",
        "Policy WTemplate uses when stamping ids on bound widgets.\n"
        "`None_` leaves the widget's id alone; `SetObjectName` sets the\n"
        "Wt object name to the bind var; `SetId` sets the DOM `id`\n"
        "attribute to it.")
        .value("None_",         Wt::TemplateWidgetIdMode::None)
        .value("SetObjectName", Wt::TemplateWidgetIdMode::SetObjectName)
        .value("SetId",         Wt::TemplateWidgetIdMode::SetId);

    // ---- WTemplate ----

    nb::class_<Wt::WTemplate, Wt::WInteractWidget>(m, "WTemplate",
        "Renders an XHTML template with `${var}` placeholders that get\n"
        "replaced by bound strings, integers, or live child widgets.\n"
        "Separates layout (the template text) from behavior (the bound\n"
        "widgets and their signal handlers).\n"
        "\n"
        "    tpl = container.add_widget(wt.WTemplate(\n"
        "        '<div>${greeting}, ${name}! ${ok-button}</div>'))\n"
        "    tpl.bind_string('greeting', 'Hello')\n"
        "    tpl.bind_string('name', user_name)\n"
        "    tpl.bind_widget('ok-button', wt.WPushButton('OK')\n"
        "    ).clicked.connect(submit)\n"
        "\n"
        "Templates also support conditional blocks: a region wrapped in\n"
        "`${<flag>}…${</flag>}` renders only when `set_condition('flag',\n"
        "True)` has been called.")
        .def(heap_init<Wt::WTemplate>(),
             "Construct an empty template. Set `template_text` later.")
        .def(heap_init<Wt::WTemplate, const Wt::WString&>(), "text"_a,
             "Construct a template using `text` as the source markup.")
        .def_prop_rw("template_text",
            [](const Wt::WTemplate& t) { return t.templateText(); },
            [](Wt::WTemplate& t, const Wt::WString& text) {
                t.setTemplateText(text);
            },
            "The template source. Assigning re-renders on the next\n"
            "round-trip, preserving any current bindings.")
        .def("set_template_text", &Wt::WTemplate::setTemplateText,
             "text"_a, "format"_a = Wt::TextFormat::XHTML,
             "Replace the template source. `format` controls how `text`\n"
             "itself is sanitised (the default XHTML strips XSS-prone\n"
             "constructs from the template body).")

        // bind_widget: transfers ownership of `widget` into the template
        // and re-arms the Python wrapper as a non-owning alias.
        .def("bind_widget",
             [](Wt::WTemplate& self, const std::string& var_name,
                nb::object py_widget) -> nb::object {
                 auto w = nb::cast<std::unique_ptr<Wt::WWidget>>(py_widget);
                 self.bindWidget(var_name, std::move(w));
                 nb::inst_set_state(py_widget, /*ready*/ true,
                                    /*destruct*/ false);
                 return py_widget;
             },
             "var_name"_a, "widget"_a,
             "Substitute `${var_name}` in the template with a live\n"
             "`widget`. Takes ownership and re-arms the Python wrapper\n"
             "as a non-owning alias; returns the same wrapper for fluent\n"
             "chaining:\n"
             "\n"
             "    tpl.bind_widget('ok', wt.WPushButton('OK')).clicked.connect(go)")

        // bind_string is the *substitution* path — the value is inlined into
        // the template's rendered text, not added as a child widget. Use
        // bind_widget when you want a widget (e.g. to wire signals to it).
        .def("bind_string",
             [](Wt::WTemplate& self, const std::string& var_name,
                const Wt::WString& value, Wt::TextFormat format) {
                 self.bindString(var_name, value, format);
             },
             "var_name"_a, "value"_a, "format"_a = Wt::TextFormat::XHTML,
             "Substitute `${var_name}` with `value`, rendered according\n"
             "to `format`. Use this for static text content; pick\n"
             "`bind_widget` instead when you need a widget to wire\n"
             "signals to.")

        .def("bind_int", &Wt::WTemplate::bindInt,
             "var_name"_a, "value"_a,
             "Substitute `${var_name}` with the decimal rendering of\n"
             "`value`.")

        .def("bind_empty", &Wt::WTemplate::bindEmpty, "var_name"_a,
             "Bind `${var_name}` to nothing — useful for clearing a\n"
             "placeholder without removing the surrounding template\n"
             "markup.")

        .def("resolve_widget", &Wt::WTemplate::resolveWidget,
             "var_name"_a, nb::rv_policy::reference_internal,
             "Return a non-owning handle to the widget currently bound\n"
             "to `var_name`, or None if no widget is bound there.")

        .def_prop_rw("widget_id_mode",
            [](const Wt::WTemplate& t) { return t.widgetIdMode(); },
            [](Wt::WTemplate& t, Wt::TemplateWidgetIdMode mode) {
                t.setWidgetIdMode(mode);
            },
            "Controls how bound widgets pick up the bind variable as an\n"
            "id. See TemplateWidgetIdMode.")

        .def("clear", &Wt::WTemplate::clear,
             "Drop every binding and condition. The template source\n"
             "stays as-is.")
        .def("refresh", &Wt::WTemplate::refresh,
             "Force a re-render. Normally called automatically after\n"
             "bindings change; useful when external state the template\n"
             "depends on has shifted.")

        // Condition system: ${<if-name>}...${</if-name>} blocks in the
        // template render only when the corresponding condition is true.
        .def("set_condition", &Wt::WTemplate::setCondition,
             "name"_a, "value"_a,
             "Set the value of a named condition flag. Regions wrapped\n"
             "in `${<name>}…${</name>}` render only while the flag is\n"
             "True.")
        .def("condition_value", &Wt::WTemplate::conditionValue, "name"_a,
             "Read the current value of a named condition flag.");
}

}  // namespace witty_for_python
