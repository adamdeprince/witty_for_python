#include "common.hpp"

#include <Wt/WContainerWidget.h>
#include <Wt/WLayout.h>
#include <Wt/WText.h>
#include <Wt/WWidget.h>

namespace witty_for_python {

void register_container(nb::module_& m) {
    nb::class_<Wt::WContainerWidget, Wt::WInteractWidget>(m, "WContainerWidget",
        "A `<div>`-style box that holds child widgets in document order.\n"
        "The default container for composing UIs — every Wt application\n"
        "starts with a root WContainerWidget (`app.root`) and adds\n"
        "widgets into it.\n"
        "\n"
        "    page = app.root\n"
        "    page.add_widget(wt.WText('Welcome.'))\n"
        "    page.add_widget(wt.WPushButton('Click me')).clicked.connect(say_hi)\n"
        "\n"
        "Children render stacked top-to-bottom unless a `layout` is\n"
        "installed via `set_layout` (then the layout class decides). The\n"
        "container owns its children: when it's destroyed, every widget\n"
        "added to it is destroyed too.")
        .def(heap_init<Wt::WContainerWidget>(),
             "Construct an empty container with no children and no layout.")
        // String overload: wraps the text in a freshly-constructed WText
        // and adds it. Python-only convenience (Wt's C++ idiom is
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
             nb::rv_policy::reference_internal,
             "Convenience for `add_widget(WText(text))`. Wraps `text` in\n"
             "a freshly-constructed WText and adds it; returns a\n"
             "non-owning handle to the WText so you can mutate it later.\n"
             "\n"
             "    label = container.add_widget('Loading…')\n"
             "    # later, after data arrives:\n"
             "    label.text = 'Loaded 42 rows.'\n"
             "\n"
             "If you need any setting on the WText other than its text\n"
             "(e.g. CSS class, format), build the WText yourself and use\n"
             "the widget-taking overload below.")
        // The unique_ptr cast invokes nanobind's relinquish check: it
        // rejects nb::init<>-built widgets (internal storage) so we don't
        // hand Wt a pointer it would later `delete` on memory it doesn't
        // own. After relinquish the wrapper is `state_relinquished` and
        // any attribute access raises — re-arm it (ready=true so methods
        // work, destruct=false so Python won't double-free what Wt's
        // widget tree now owns).
        .def("add_widget",
             [](Wt::WContainerWidget& self, nb::object py_widget) -> nb::object {
                 auto w = nb::cast<std::unique_ptr<Wt::WWidget>>(py_widget);
                 self.addWidget(std::move(w));
                 nb::inst_set_state(py_widget, /*ready*/ true,
                                    /*destruct*/ false);
                 return py_widget;
             },
             "widget"_a,
             "Transfer ownership of `widget` to this container and\n"
             "return the same Python wrapper (subtype preserved), re-armed\n"
             "as a non-owning alias. Chain straight off the return:\n"
             "\n"
             "    container.add_widget(wt.WPushButton('Save')).clicked.connect(save)\n"
             "\n"
             "Or keep the typed handle for later mutation:\n"
             "\n"
             "    edit = container.add_widget(wt.WLineEdit())\n"
             "    edit.placeholder = 'Email…'\n"
             "\n"
             "From the moment of transfer, the container is responsible\n"
             "for destroying the widget — garbage-collecting the Python\n"
             "wrapper does NOT delete the C++ object (Wt's widget tree\n"
             "does, on container teardown).")
        // Bulk variants — the text overload builds WTexts and returns
        // non-owning pointers (reference_internal). The widget overload
        // returns the SAME Python wrappers, each re-armed as non-owning
        // aliases — same identity/subtype preservation as the single-arg
        // add_widget.
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
             nb::rv_policy::reference_internal,
             "Bulk version of `add_widget(str)`. Wraps each string in a\n"
             "WText and adds them in order. Returns the list of handles.\n"
             "\n"
             "    rows = container.add_widgets(['Apples', 'Pears', 'Plums'])\n"
             "    rows[0].text = 'Granny Smith'           # mutate one")
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
             "widgets"_a,
             "Bulk version of `add_widget(widget)`. Transfers ownership\n"
             "of each widget to this container in order. Returns the\n"
             "same Python wrappers, each re-armed as a non-owning alias\n"
             "(identity and subtype preserved).\n"
             "\n"
             "    items = [wt.WPushButton(label) for label in choices]\n"
             "    container.add_widgets(items)            # one round-trip\n"
             "    for btn in items:                       # still typed + usable\n"
             "        btn.clicked.connect(lambda b=btn: pick(b.text))")
        .def("clear", &Wt::WContainerWidget::clear,
             "Remove and destroy every child widget. After this returns\n"
             "the container has no children and `count` is 0; any Python\n"
             "wrappers still referencing the removed widgets are now\n"
             "dangling — calling methods on them raises.")
        .def_prop_ro("count", &Wt::WContainerWidget::count,
             "Number of direct child widgets currently in the container.")
        .def("widget", &Wt::WContainerWidget::widget,
             "index"_a, nb::rv_policy::reference_internal,
             "Return a non-owning handle to the child at position\n"
             "`index` (0-based). Useful for inspecting children when\n"
             "you didn't keep handles from `add_widget`. The static\n"
             "type is WWidget; use `isinstance` to narrow.")
        .def("remove_widget",
             [](Wt::WContainerWidget& self, Wt::WWidget* w) {
                 // removeWidget() returns unique_ptr<WWidget>; letting nanobind
                 // own it again means Python is responsible for destruction
                 // (or for re-attaching via add_widget elsewhere).
                 return self.removeWidget(w);
             },
             "widget"_a,
             "Detach `widget` from this container and return ownership\n"
             "to Python. The widget is NOT destroyed — it's left dangling\n"
             "until either the returned reference is dropped (Python\n"
             "destroys it) or it's re-attached to a different container\n"
             "via `add_widget`.\n"
             "\n"
             "    moved = src.remove_widget(some_btn)\n"
             "    dst.add_widget(moved)                  # re-parented")
        .def("set_layout",
             [](Wt::WContainerWidget& self, nb::object py_layout) {
                 auto l = nb::cast<std::unique_ptr<Wt::WLayout>>(py_layout);
                 self.setLayout(std::move(l));
                 nb::inst_set_state(py_layout, /*ready*/ true,
                                    /*destruct*/ false);
             },
             "layout"_a,
             "Install `layout` as the container's layout manager. Once\n"
             "set, the layout (not the container's add_widget order)\n"
             "decides how children are positioned — use the layout's own\n"
             "add_widget / add_item methods after this. Same ownership\n"
             "transfer as add_widget: the container takes the C++ object,\n"
             "the Python wrapper is re-armed as a non-owning alias.\n"
             "\n"
             "    layout = wt.WVBoxLayout()\n"
             "    container.set_layout(layout)\n"
             "    layout.add_widget(wt.WText('top'))\n"
             "    layout.add_widget(wt.WText('bottom'))");
}

}  // namespace witty_for_python
