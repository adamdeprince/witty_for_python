#include "common.hpp"

#include <Wt/WContainerWidget.h>
#include <Wt/WLayout.h>
#include <Wt/WText.h>
#include <Wt/WWidget.h>

namespace witty_for_python {

void register_container(nb::module_& m) {
    nb::class_<Wt::WContainerWidget, Wt::WInteractWidget>(m, "WContainerWidget")
        .def(nb::init<>())
        // Transfer ownership of `widget` to this container. The Python wrapper
        // passed in becomes invalid after this call; use the returned handle
        // (non-owning, lifetime tied to the parent) for any further access.
        // The non-template addWidget(unique_ptr<WWidget>) returns void, so we
        // snapshot the raw pointer before moving.
        .def("add_widget",
             [](Wt::WContainerWidget& self, std::unique_ptr<Wt::WWidget> w)
                 -> Wt::WWidget* {
                 Wt::WWidget* raw = w.get();
                 self.addWidget(std::move(w));
                 return raw;
             },
             "widget"_a,
             nb::rv_policy::reference_internal)
        // String overload: wraps the text in a freshly-constructed WText and
        // adds it. The returned non-owning handle is the WText, so callers
        // can keep using property syntax (`label = c.add_widget("hi"); label.text = "..."`).
        // Python-only convenience (Wt's C++ idiom is `addWidget(make_unique<WText>(s))`).
        .def("add_widget",
             [](Wt::WContainerWidget& self, const Wt::WString& text) -> Wt::WText* {
                 auto t = std::make_unique<Wt::WText>(text);
                 Wt::WText* raw = t.get();
                 self.addWidget(std::move(t));
                 return raw;
             },
             "text"_a,
             nb::rv_policy::reference_internal)
        // Bulk variants of add_widget. Each adds in order and returns a list
        // of the non-owning handles, so a single call can build a row of
        // related widgets that the caller then mutates. Like add_widget,
        // overloaded on iterable element type (widget vs str).
        .def("add_widgets",
             [](Wt::WContainerWidget& self,
                std::vector<std::unique_ptr<Wt::WWidget>> widgets) {
                 std::vector<Wt::WWidget*> out;
                 out.reserve(widgets.size());
                 for (auto& w : widgets) {
                     out.push_back(w.get());
                     self.addWidget(std::move(w));
                 }
                 return out;
             },
             "widgets"_a,
             nb::rv_policy::reference_internal)
        .def("add_widgets",
             [](Wt::WContainerWidget& self,
                const std::vector<Wt::WString>& texts) {
                 std::vector<Wt::WText*> out;
                 out.reserve(texts.size());
                 for (const auto& t : texts) {
                     auto wt = std::make_unique<Wt::WText>(t);
                     out.push_back(wt.get());
                     self.addWidget(std::move(wt));
                 }
                 return out;
             },
             "texts"_a,
             nb::rv_policy::reference_internal)
        .def("clear", &Wt::WContainerWidget::clear)
        .def_prop_ro("count", &Wt::WContainerWidget::count)
        .def("widget", &Wt::WContainerWidget::widget,
             "index"_a, nb::rv_policy::reference_internal)
        .def("remove_widget",
             [](Wt::WContainerWidget& self, Wt::WWidget* w) {
                 // Returns std::unique_ptr<WWidget>; let nanobind own it again
                 // from the Python side so the caller can re-add or drop it.
                 return self.removeWidget(w);
             },
             "widget"_a)
        .def("set_layout",
             [](Wt::WContainerWidget& self, std::unique_ptr<Wt::WLayout> layout) {
                 self.setLayout(std::move(layout));
             },
             "layout"_a);
}

}  // namespace witty_for_python
