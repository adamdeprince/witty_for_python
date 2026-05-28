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

    nb::enum_<Wt::TextFormat>(m, "TextFormat")
        .value("XHTML",       Wt::TextFormat::XHTML)
        .value("UnsafeXHTML", Wt::TextFormat::UnsafeXHTML)
        .value("Plain",       Wt::TextFormat::Plain);

    nb::enum_<Wt::TemplateWidgetIdMode>(m, "TemplateWidgetIdMode")
        .value("None_",         Wt::TemplateWidgetIdMode::None)
        .value("SetObjectName", Wt::TemplateWidgetIdMode::SetObjectName)
        .value("SetId",         Wt::TemplateWidgetIdMode::SetId);

    // ---- WTemplate ----

    nb::class_<Wt::WTemplate, Wt::WInteractWidget>(m, "WTemplate")
        .def(heap_init<Wt::WTemplate>())
        .def(heap_init<Wt::WTemplate, const Wt::WString&>(), "text"_a)
        .def_prop_rw("template_text",
            [](const Wt::WTemplate& t) { return t.templateText(); },
            [](Wt::WTemplate& t, const Wt::WString& text) {
                t.setTemplateText(text);
            })
        .def("set_template_text", &Wt::WTemplate::setTemplateText,
             "text"_a, "format"_a = Wt::TextFormat::XHTML)

        // bind_widget: transfers ownership of `widget` into the template
        // and re-arms the Python wrapper as a non-owning alias (so its
        // methods still work, but it won't double-free what the template
        // owns). Returns the SAME Python wrapper for fluent chaining:
        // `template.bind_widget("ok", wt.WPushButton("ok")).clicked.connect(fn)`.
        // See docs/binding_design.md §4.2 for the pattern.
        .def("bind_widget",
             [](Wt::WTemplate& self, const std::string& var_name,
                nb::object py_widget) -> nb::object {
                 auto w = nb::cast<std::unique_ptr<Wt::WWidget>>(py_widget);
                 self.bindWidget(var_name, std::move(w));
                 nb::inst_set_state(py_widget, /*ready*/ true,
                                    /*destruct*/ false);
                 return py_widget;
             },
             "var_name"_a, "widget"_a)

        // bind_string is the *substitution* path — the value is inlined into
        // the template's rendered text, not added as a child widget. Use
        // bind_widget when you want a widget (e.g. to wire signals to it).
        .def("bind_string",
             [](Wt::WTemplate& self, const std::string& var_name,
                const Wt::WString& value, Wt::TextFormat format) {
                 self.bindString(var_name, value, format);
             },
             "var_name"_a, "value"_a, "format"_a = Wt::TextFormat::XHTML)

        .def("bind_int", &Wt::WTemplate::bindInt,
             "var_name"_a, "value"_a)

        .def("bind_empty", &Wt::WTemplate::bindEmpty, "var_name"_a)

        .def("resolve_widget", &Wt::WTemplate::resolveWidget,
             "var_name"_a, nb::rv_policy::reference_internal)

        .def_prop_rw("widget_id_mode",
            [](const Wt::WTemplate& t) { return t.widgetIdMode(); },
            [](Wt::WTemplate& t, Wt::TemplateWidgetIdMode mode) {
                t.setWidgetIdMode(mode);
            })

        .def("clear", &Wt::WTemplate::clear)
        .def("refresh", &Wt::WTemplate::refresh)

        // Condition system: ${<if-name>}...${</if-name>} blocks in the
        // template render only when the corresponding condition is true.
        .def("set_condition", &Wt::WTemplate::setCondition,
             "name"_a, "value"_a)
        .def("condition_value", &Wt::WTemplate::conditionValue, "name"_a);
}

}  // namespace witty_for_python
