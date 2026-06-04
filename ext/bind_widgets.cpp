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

    nb::class_<Wt::WText, Wt::WInteractWidget>(m, "WText",
        "Static text content. Renders a span of XHTML in the page; the\n"
        "simplest building block for displaying text or inline markup.\n"
        "\n"
        "    label = container.add_widget(wt.WText('Loading…'))\n"
        "    label.text = 'Loaded 42 rows.'\n"
        "\n"
        "Text is interpreted as XHTML by default — passing untrusted\n"
        "user input is XSS-unsafe. Wrap with HTML escaping before\n"
        "assigning, or use a future PlainText TextFormat binding.")
        .def(heap_init<Wt::WText>(),
             "Construct an empty WText with no content. Set `text` later.")
        .def(heap_init<Wt::WText, const Wt::WString&>(), "text"_a,
             "Construct a WText displaying `text` (interpreted as XHTML).")
        .def_prop_rw("text",
            [](const Wt::WText& w) { return w.text(); },
            [](Wt::WText& w, const Wt::WString& t) { w.setText(t); },
            "The widget's displayed text (XHTML). Assigning re-renders\n"
            "the widget on the next client round-trip; no need to call\n"
            "any refresh method.");

    nb::class_<Wt::WPushButton, Wt::WFormWidget>(m, "WPushButton",
        "A clickable button. Connect to `clicked` for an action button,\n"
        "or set `link` for navigation (the button renders as a styled\n"
        "anchor).\n"
        "\n"
        "    container.add_widget(wt.WPushButton('Save')).clicked.connect(save)\n"
        "\n"
        "    home = container.add_widget(wt.WPushButton('Home'))\n"
        "    home.link = wt.WLink('/')")
        .def(heap_init<Wt::WPushButton>(),
             "Construct an empty button with no caption.")
        .def(heap_init<Wt::WPushButton, const Wt::WString&>(), "text"_a,
             "Construct a button captioned `text`.")
        .def_prop_rw("text",
            [](const Wt::WPushButton& w) { return w.text(); },
            [](Wt::WPushButton& w, const Wt::WString& t) { w.setText(t); },
            "The button's caption (XHTML).")
        .def_prop_rw("link",
            [](const Wt::WPushButton& w) { return w.link(); },
            [](Wt::WPushButton& w, const Wt::WLink& l) { w.setLink(l); },
            "URL the button navigates to when clicked. Setting a link\n"
            "makes the button render as an anchor under the hood; if you\n"
            "want pure action behavior, leave `link` unset and connect\n"
            "to `clicked` instead.");

    nb::class_<Wt::WLineEdit, Wt::WFormWidget>(m, "WLineEdit",
        "Single-line text input.\n"
        "\n"
        "    edit = container.add_widget(wt.WLineEdit())\n"
        "    edit.placeholder = 'Email…'\n"
        "    edit.max_length = 64\n"
        "    container.add_widget(wt.WPushButton('Send')).clicked.connect(\n"
        "        lambda: send(edit.text))")
        .def(heap_init<Wt::WLineEdit>(),
             "Construct an empty line edit.")
        .def(heap_init<Wt::WLineEdit, const Wt::WString&>(), "text"_a,
             "Construct a line edit with initial value `text`.")
        .def_prop_rw("text",
            [](const Wt::WLineEdit& w) { return w.text(); },
            [](Wt::WLineEdit& w, const Wt::WString& t) { w.setText(t); },
            "The current input value. Reads what the user has typed;\n"
            "assigning replaces the current contents.")
        .def_prop_rw("placeholder",
            [](const Wt::WLineEdit& w) { return w.placeholderText(); },
            [](Wt::WLineEdit& w, const Wt::WString& t) { w.setPlaceholderText(t); },
            "Greyed-out hint shown when the field is empty (the standard\n"
            "browser `placeholder` attribute).")
        .def_prop_rw("max_length",
            [](const Wt::WLineEdit& w) { return w.maxLength(); },
            [](Wt::WLineEdit& w, int n) { w.setMaxLength(n); },
            "Maximum number of characters the browser will accept.\n"
            "Negative (the default) means no limit. Enforced client-side\n"
            "only — re-validate server-side if it matters.")
        .def_prop_ro("text_input", &Wt::WLineEdit::textInput,
                     nb::rv_policy::reference_internal,
                     "Per-keystroke signal (`EventSignal<>`). Fires as\n"
                     "the user types, before the change is committed.\n"
                     "Use `changed` instead for the standard\n"
                     "blur/Enter-fires-once semantics.");

    nb::class_<Wt::WCheckBox, Wt::WFormWidget>(m, "WCheckBox",
        "Bistable boolean control with an optional caption.\n"
        "\n"
        "    container.add_widget(wt.WCheckBox('Subscribe')).on_check.connect(subscribe)\n"
        "\n"
        "    box = container.add_widget(wt.WCheckBox('Remember me'))\n"
        "    box.checked = True\n"
        "    box.on_check.connect(lambda: store('remember', True))\n"
        "    box.on_uncheck.connect(lambda: store('remember', False))\n"
        "\n"
        "Inherits all WFormWidget validation/state plumbing — wire to\n"
        "`set_validator` if the value participates in a form submit.")
        .def(heap_init<Wt::WCheckBox>(),
             "Construct an unlabelled checkbox in the unchecked state.")
        .def(heap_init<Wt::WCheckBox, const Wt::WString&>(), "text"_a,
             "Construct a labelled checkbox; `text` renders next to the box.")
        .def_prop_rw("checked",
            [](const Wt::WCheckBox& w) { return w.isChecked(); },
            [](Wt::WCheckBox& w, bool c) { w.setChecked(c); },
            "The current boolean state. Assigning programmatically does\n"
            "NOT fire `on_check`/`on_uncheck` — those are user-input\n"
            "events.")
        .def_prop_ro("on_check",
            [](Wt::WCheckBox& w) -> Wt::EventSignal<>& { return w.checked(); },
            nb::rv_policy::reference_internal,
            "Fires when the user checks the box. No-arg signal.\n"
            "Programmatic `checked = True` does not fire it.")
        .def_prop_ro("on_uncheck",
            [](Wt::WCheckBox& w) -> Wt::EventSignal<>& { return w.unChecked(); },
            nb::rv_policy::reference_internal,
            "Fires when the user unchecks the box. Mirror of `on_check`.");

    nb::class_<Wt::WAnchor, Wt::WContainerWidget>(m, "WAnchor",
        "A hyperlink. Inherits WContainerWidget so the visible body can\n"
        "be arbitrary widgets, not just text — wrap an image to make a\n"
        "clickable banner, etc.\n"
        "\n"
        "    container.add_widget(wt.WAnchor(wt.WLink('https://example.com'), 'Visit'))\n"
        "\n"
        "    container.add_widget(wt.WAnchor(wt.WLink('/landing'))).add_widget(\n"
        "        wt.WImage(wt.WLink('/banner.png'), 'Promo'))")
        .def(heap_init<Wt::WAnchor>(),
             "Construct an empty anchor with no link or content.")
        .def(heap_init<Wt::WAnchor, const Wt::WLink&>(), "link"_a,
             "Construct an anchor pointing to `link` with no visible text.\n"
             "Useful when the body will be set up via `add_widget`.")
        .def(heap_init<Wt::WAnchor, const Wt::WLink&, const Wt::WString&>(),
             "link"_a, "text"_a,
             "Construct an anchor whose visible body is the plain text\n"
             "`text` and which targets `link` on click.")
        .def_prop_rw("link",
            [](const Wt::WAnchor& w) { return w.link(); },
            [](Wt::WAnchor& w, const Wt::WLink& l) { w.setLink(l); },
            "The hyperlink target. A WLink wraps a URL string, an\n"
            "internal-path reference, or a server-side WResource.");

    nb::class_<Wt::WImage, Wt::WInteractWidget>(m, "WImage",
        "An `<img>` element. The image source can be any WLink — a URL\n"
        "string, a static resource path, or a dynamically-served\n"
        "WResource (e.g. a WPdfImage or chart rendered to PNG).\n"
        "\n"
        "    container.add_widget(\n"
        "        wt.WImage(wt.WLink('/logo.png'), 'Logo')\n"
        "    ).clicked.connect(zoom_logo)\n"
        "\n"
        "    server.add_resource(MyChartResource(), '/chart.png')\n"
        "    container.add_widget(wt.WImage(wt.WLink('/chart.png'), 'Live chart'))")
        .def(heap_init<Wt::WImage>(),
             "Construct an empty image with no source.")
        .def(heap_init<Wt::WImage, const Wt::WLink&>(), "link"_a,
             "Construct an image sourced from `link` with no alt text.\n"
             "Set `alt_text` afterwards for accessibility.")
        .def(heap_init<Wt::WImage, const Wt::WLink&, const Wt::WString&>(),
             "link"_a, "alt_text"_a,
             "Construct an image sourced from `link` with the given\n"
             "alt text (used by screen readers and shown if the image\n"
             "fails to load).")
        .def_prop_rw("image_link",
            [](const Wt::WImage& w) { return w.imageLink(); },
            [](Wt::WImage& w, const Wt::WLink& l) { w.setImageLink(l); },
            "The image source. Assigning swaps the displayed image on\n"
            "the next client round-trip.")
        .def_prop_rw("alt_text",
            [](const Wt::WImage& w) { return w.alternateText(); },
            [](Wt::WImage& w, const Wt::WString& t) { w.setAlternateText(t); },
            "Text shown if the image fails to load and read aloud by\n"
            "screen readers. Set it on any image whose meaning matters.");
}

}  // namespace witty_for_python
