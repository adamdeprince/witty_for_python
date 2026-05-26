#include "common.hpp"

#include <Wt/WAnchor.h>
#include <Wt/WCheckBox.h>
#include <Wt/WImage.h>
#include <Wt/WLineEdit.h>
#include <Wt/WLink.h>
#include <Wt/WPushButton.h>
#include <Wt/WText.h>

namespace witty_for_python {

void register_widgets(nb::module_& m) {
    // WLink itself (with both str and shared_ptr<WResource> implicit
    // constructors) is bound in bind_resource.cpp — register_resource runs
    // before register_widgets in module.cpp so by the time we use WLink as
    // a parameter type below, the Python class is already established.

    nb::class_<Wt::WText, Wt::WInteractWidget>(m, "WText")
        .def(nb::init<>())
        .def(nb::init<const Wt::WString&>(), "text"_a)
        .def_prop_rw("text",
            [](const Wt::WText& w) { return w.text(); },
            [](Wt::WText& w, const Wt::WString& t) { w.setText(t); });

    nb::class_<Wt::WPushButton, Wt::WFormWidget>(m, "WPushButton")
        .def(nb::init<>())
        .def(nb::init<const Wt::WString&>(), "text"_a)
        .def_prop_rw("text",
            [](const Wt::WPushButton& w) { return w.text(); },
            [](Wt::WPushButton& w, const Wt::WString& t) { w.setText(t); })
        .def_prop_rw("link",
            [](const Wt::WPushButton& w) { return w.link(); },
            [](Wt::WPushButton& w, const Wt::WLink& l) { w.setLink(l); });

    nb::class_<Wt::WLineEdit, Wt::WFormWidget>(m, "WLineEdit")
        .def(nb::init<>())
        .def(nb::init<const Wt::WString&>(), "text"_a)
        .def_prop_rw("text",
            [](const Wt::WLineEdit& w) { return w.text(); },
            [](Wt::WLineEdit& w, const Wt::WString& t) { w.setText(t); })
        .def_prop_rw("placeholder",
            [](const Wt::WLineEdit& w) { return w.placeholderText(); },
            [](Wt::WLineEdit& w, const Wt::WString& t) { w.setPlaceholderText(t); })
        .def_prop_rw("max_length",
            [](const Wt::WLineEdit& w) { return w.maxLength(); },
            [](Wt::WLineEdit& w, int n) { w.setMaxLength(n); })
        .def_prop_ro("text_input", &Wt::WLineEdit::textInput,
                     nb::rv_policy::reference_internal);

    nb::class_<Wt::WCheckBox, Wt::WFormWidget>(m, "WCheckBox")
        .def(nb::init<>())
        .def(nb::init<const Wt::WString&>(), "text"_a)
        .def_prop_rw("checked",
            [](const Wt::WCheckBox& w) { return w.isChecked(); },
            [](Wt::WCheckBox& w, bool c) { w.setChecked(c); })
        .def_prop_ro("on_check",
            [](Wt::WCheckBox& w) -> Wt::EventSignal<>& { return w.checked(); },
            nb::rv_policy::reference_internal)
        .def_prop_ro("on_uncheck",
            [](Wt::WCheckBox& w) -> Wt::EventSignal<>& { return w.unChecked(); },
            nb::rv_policy::reference_internal);

    nb::class_<Wt::WAnchor, Wt::WContainerWidget>(m, "WAnchor")
        .def(nb::init<>())
        .def(nb::init<const Wt::WLink&>(), "link"_a)
        .def(nb::init<const Wt::WLink&, const Wt::WString&>(), "link"_a, "text"_a)
        .def_prop_rw("link",
            [](const Wt::WAnchor& w) { return w.link(); },
            [](Wt::WAnchor& w, const Wt::WLink& l) { w.setLink(l); });

    nb::class_<Wt::WImage, Wt::WInteractWidget>(m, "WImage")
        .def(nb::init<>())
        .def(nb::init<const Wt::WLink&>(), "link"_a)
        .def(nb::init<const Wt::WLink&, const Wt::WString&>(),
             "link"_a, "alt_text"_a)
        .def_prop_rw("image_link",
            [](const Wt::WImage& w) { return w.imageLink(); },
            [](Wt::WImage& w, const Wt::WLink& l) { w.setImageLink(l); })
        .def_prop_rw("alt_text",
            [](const Wt::WImage& w) { return w.alternateText(); },
            [](Wt::WImage& w, const Wt::WString& t) { w.setAlternateText(t); });
}

}  // namespace witty_for_python
