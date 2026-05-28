#include "common.hpp"

#include <Wt/WContainerWidget.h>
#include <Wt/WLayout.h>
#include <Wt/WText.h>
#include <Wt/WWidget.h>

namespace witty_for_python {

void register_container(nb::module_& m) {
    nb::class_<Wt::WContainerWidget, Wt::WInteractWidget>(m, "WContainerWidget")
        .def(heap_init<Wt::WContainerWidget>())
        // String overload: wraps the text in a freshly-constructed WText
        // and adds it. The returned non-owning handle is the WText, so the
        // caller can mutate it (e.g. `label = c.add_widget("hi"); label.text = "..."`).
        // Python-only convenience (Wt's C++ idiom is
        // `addWidget(make_unique<WText>(s))`). Registered BEFORE the widget
        // overload so a str argument doesn't get routed into the
        // `nb::object → unique_ptr` cast (which would `std::bad_cast`).
        .def("add_widget",
             [](Wt::WContainerWidget& self, const Wt::WString& text) -> Wt::WText* {
                 auto t = std::make_unique<Wt::WText>(text);
                 Wt::WText* raw = t.get();
                 self.addWidget(std::move(t));
                 return raw;
             },
             "text"_a,
             nb::rv_policy::reference_internal)
        // Transfer ownership of `widget` to this container. The container
        // takes the C++ instance via unique_ptr; the Python wrapper is
        // re-armed as a non-owning alias so methods on it still work but
        // it won't try to delete the C++ object on GC. We return the SAME
        // Python wrapper (refcount-incremented):
        //
        //     btn = wt.WPushButton("Click")
        //     same = container.add_widget(btn)
        //     assert same is btn                       # identity preserved
        //     assert isinstance(same, wt.WPushButton)  # subtype preserved
        //     same.text = "Now this still works"       # wrapper still usable
        //
        // Returning the original nb::object also keeps full static type
        // information at the call site, vs. erasing it to WWidget.
        .def("add_widget",
             [](Wt::WContainerWidget& self, nb::object py_widget) -> nb::object {
                 // The unique_ptr cast invokes nanobind's relinquish check:
                 // it rejects nb::init<>-built widgets (internal storage)
                 // so we don't hand Wt a pointer it would later `delete`
                 // on memory it doesn't own.
                 auto w = nb::cast<std::unique_ptr<Wt::WWidget>>(py_widget);
                 self.addWidget(std::move(w));
                 // After relinquish the wrapper is `state_relinquished` and
                 // any attribute access raises. Re-arm it: ready=true so
                 // methods work, destruct=false so Python won't double-free
                 // what Wt's widget tree now owns.
                 nb::inst_set_state(py_widget, /*ready*/ true,
                                    /*destruct*/ false);
                 return py_widget;
             },
             "widget"_a)
        // Bulk variants of add_widget. The text overload constructs WTexts
        // and returns non-owning pointers (reference_internal). The widget
        // overload returns the SAME Python wrappers that were passed in,
        // each re-armed as non-owning aliases — same identity/subtype
        // preservation as the single-arg add_widget.
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
        .def("add_widgets",
             [](Wt::WContainerWidget& self, nb::list py_widgets) -> nb::list {
                 nb::list out;
                 for (nb::handle h : py_widgets) {
                     nb::object py_w = nb::borrow(h);
                     auto w = nb::cast<std::unique_ptr<Wt::WWidget>>(py_w);
                     self.addWidget(std::move(w));
                     nb::inst_set_state(py_w, /*ready*/ true,
                                        /*destruct*/ false);
                     out.append(py_w);
                 }
                 return out;
             },
             "widgets"_a)
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
             [](Wt::WContainerWidget& self, nb::object py_layout) {
                 auto l = nb::cast<std::unique_ptr<Wt::WLayout>>(py_layout);
                 self.setLayout(std::move(l));
                 nb::inst_set_state(py_layout, /*ready*/ true,
                                    /*destruct*/ false);
             },
             "layout"_a);
}

}  // namespace witty_for_python
