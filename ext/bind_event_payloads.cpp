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

    nb::class_<Wt::Touch>(m, "Touch",
        "A single finger contact on a touch-capable device. Bundled\n"
        "inside the `touches` / `target_touches` / `changed_touches`\n"
        "lists on a WTouchEvent. Read the four coordinate accessors to\n"
        "get the contact position in different reference frames.")
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

    nb::class_<Wt::WTouchEvent>(m, "WTouchEvent",
        "Payload delivered to touch-related event signals. Splits the\n"
        "active touches into three views: every finger on the screen,\n"
        "only the fingers whose touch started on the target widget, and\n"
        "the subset of fingers that changed state in the event firing.")
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

    nb::class_<Wt::WGestureEvent>(m, "WGestureEvent",
        "Payload for multi-touch pinch and rotate gestures. `scale`\n"
        "compares the current finger spread to the start of the gesture\n"
        "(1.0 means unchanged, >1 a pinch-out, <1 a pinch-in); `rotation`\n"
        "is the angular delta in degrees.")
        .def_prop_ro("scale", &Wt::WGestureEvent::scale,
            "Pinch scale relative to the gesture's start (1.0 = no\n"
            "change, >1 zoomed out, <1 zoomed in).")
        .def_prop_ro("rotation", &Wt::WGestureEvent::rotation,
            "Rotation in degrees relative to the gesture's start.");

    // ---- WScrollEvent ----

    nb::class_<Wt::WScrollEvent>(m, "WScrollEvent",
        "Payload for scroll-position changes. Reports the current scroll\n"
        "offset of the scrolling element together with the viewport\n"
        "dimensions, all in CSS pixels.")
        .def_prop_ro("scroll_x", &Wt::WScrollEvent::scrollX,
            "Horizontal scroll offset in pixels.")
        .def_prop_ro("scroll_y", &Wt::WScrollEvent::scrollY,
            "Vertical scroll offset in pixels.")
        .def_prop_ro("viewport_width", &Wt::WScrollEvent::viewportWidth,
            "Visible viewport width in pixels.")
        .def_prop_ro("viewport_height", &Wt::WScrollEvent::viewportHeight,
            "Visible viewport height in pixels.");

    // ---- WDropEvent ----
    //
    // Delivered when something is dropped onto a widget that has
    // set_accept_drops(True). Carries the drag source (a WObject*), the
    // dragged data's mime type, and either a mouse or touch event
    // describing the drop position.

    nb::enum_<Wt::WDropEvent::OriginalEventType>(m, "DropEventOriginalEventType")
        .value("Mouse", Wt::WDropEvent::OriginalEventType::Mouse)
        .value("Touch", Wt::WDropEvent::OriginalEventType::Touch);

    nb::class_<Wt::WDropEvent>(m, "WDropEvent",
        "Payload delivered to a target widget when something is dropped\n"
        "on it. Carries a reference to the source object, the MIME type\n"
        "of the dragged data, and the underlying pointer event — either\n"
        "a WMouseEvent or a WTouchEvent depending on the input device.\n"
        "\n"
        "Inspect `event_type` first to decide which of `mouse_event` /\n"
        "`touch_event` is populated; the other is None.")
        .def_prop_ro("source", &Wt::WDropEvent::source,
            "The WObject that was the drag source. Don't outlive the slot "
            "call — the pointer's lifetime is the source widget's.")
        .def_prop_ro("mime_type",
            [](const Wt::WDropEvent& e) -> std::string { return e.mimeType(); },
            "MIME type of the dragged data, as published by the drag\n"
            "source.")
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
