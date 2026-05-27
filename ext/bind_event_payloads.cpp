#include "common.hpp"

#include <Wt/WEvent.h>             // WDropEvent, WTouchEvent, WScrollEvent,
                                   // WGestureEvent, Touch
#include <Wt/WObject.h>

#include <string>
#include <vector>

namespace witty_for_python {

void register_event_payloads(nb::module_& m) {
    // ---- Touch (nested in Wt at file scope; struct describing a single
    //      finger contact, used inside WTouchEvent) ----
    //
    // Wt declares Touch outside any class but documents it as a helper of
    // WTouchEvent. We expose it as `wt.Touch` for the natural cross-
    // reference from WTouchEvent.touches/target_touches/changed_touches.

    nb::class_<Wt::Touch>(m, "Touch")
        .def("document", &Wt::Touch::document,
             "Touch position relative to the document, as Coordinates.")
        .def("window", &Wt::Touch::window,
             "Touch position relative to the visible window.")
        .def("screen", &Wt::Touch::screen,
             "Touch position relative to the physical screen.")
        .def("widget", &Wt::Touch::widget,
             "Touch position relative to the target widget.");

    // ---- WTouchEvent ----
    //
    // Payload of touch-related event signals. Currently not wired into any
    // bound widget — Wt's touch surface (touchStarted/Moved/Ended on
    // WAbstractItemView, WInteractWidget's touch signals) is bindable but
    // not yet bound. The class is exposed so user code that receives one
    // via a future binding can read it.

    nb::class_<Wt::WTouchEvent>(m, "WTouchEvent")
        .def_prop_ro("touches",
            [](const Wt::WTouchEvent& e) { return e.touches(); },
            "List[Touch] — every finger currently touching the screen.")
        .def_prop_ro("target_touches",
            [](const Wt::WTouchEvent& e) { return e.targetTouches(); },
            "List[Touch] — fingers whose touch started inside this widget.")
        .def_prop_ro("changed_touches",
            [](const Wt::WTouchEvent& e) { return e.changedTouches(); },
            "List[Touch] — fingers whose state changed in this event.");

    // ---- WGestureEvent ----
    //
    // Pinch / rotate gestures. `scale` is relative to 1 (>1 = pinch out);
    // `rotation` is degrees relative to the start of the gesture.

    nb::class_<Wt::WGestureEvent>(m, "WGestureEvent")
        .def_prop_ro("scale", &Wt::WGestureEvent::scale)
        .def_prop_ro("rotation", &Wt::WGestureEvent::rotation);

    // ---- WScrollEvent ----

    nb::class_<Wt::WScrollEvent>(m, "WScrollEvent")
        .def_prop_ro("scroll_x", &Wt::WScrollEvent::scrollX)
        .def_prop_ro("scroll_y", &Wt::WScrollEvent::scrollY)
        .def_prop_ro("viewport_width", &Wt::WScrollEvent::viewportWidth)
        .def_prop_ro("viewport_height", &Wt::WScrollEvent::viewportHeight);

    // ---- WDropEvent ----
    //
    // Delivered when something is dropped onto a widget that has
    // set_accept_drops(True). Carries the drag source (a WObject*), the
    // dragged data's mime type, and either a mouse or touch event
    // describing the drop position.

    nb::enum_<Wt::WDropEvent::OriginalEventType>(m, "DropEventOriginalEventType")
        .value("Mouse", Wt::WDropEvent::OriginalEventType::Mouse)
        .value("Touch", Wt::WDropEvent::OriginalEventType::Touch);

    nb::class_<Wt::WDropEvent>(m, "WDropEvent")
        .def_prop_ro("source", &Wt::WDropEvent::source,
            "The WObject that was the drag source. Don't outlive the slot "
            "call — the pointer's lifetime is the source widget's.")
        .def_prop_ro("mime_type",
            [](const Wt::WDropEvent& e) -> std::string { return e.mimeType(); })
        .def_prop_ro("event_type", &Wt::WDropEvent::originalEventType,
            "DropEventOriginalEventType — whether the drop originated from "
            "a mouse or a touch event.")
        .def_prop_ro("mouse_event",
            // Returns a raw const pointer that may be null if the original
            // event was a touch. nanobind passes it through as Optional.
            [](const Wt::WDropEvent& e) { return e.mouseEvent(); },
            nb::rv_policy::reference,
            "The originating WMouseEvent, or None when event_type is Touch.")
        .def_prop_ro("touch_event",
            [](const Wt::WDropEvent& e) { return e.touchEvent(); },
            nb::rv_policy::reference,
            "The originating WTouchEvent, or None when event_type is Mouse.");
}

}  // namespace witty_for_python
