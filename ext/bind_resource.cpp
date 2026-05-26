#include "common.hpp"

#include <Wt/WFileResource.h>
#include <Wt/WLink.h>
#include <Wt/WMemoryResource.h>
#include <Wt/WResource.h>
#include <Wt/WStreamResource.h>

#include <memory>
#include <string>
#include <vector>

namespace witty_for_python {

void register_resource(nb::module_& m) {
    // ---- ContentDisposition enum ----

    nb::enum_<Wt::ContentDisposition>(m, "ContentDisposition")
        .value("None_", Wt::ContentDisposition::None)
        .value("Attachment", Wt::ContentDisposition::Attachment)
        .value("Inline", Wt::ContentDisposition::Inline);

    // ---- WResource (abstract base) ----
    //
    // Bound as a *non*-constructible class because handleRequest() is pure
    // virtual; only the concrete subclasses (WMemoryResource, WFileResource)
    // are instantiable from Python. Subclassing WResource in Python to
    // override handleRequest would need a nanobind trampoline binding
    // Wt::Http::Request / Response — not done here. For dynamic content,
    // use WMemoryResource and re-call set_data() + set_changed().

    nb::class_<Wt::WResource, Wt::WObject>(m, "WResource")
        .def("suggest_file_name",
             [](Wt::WResource& r, const Wt::WString& name) {
                 r.suggestFileName(name);
             },
             "name"_a,
             "Set the suggested filename the browser uses when saving the "
             "resource (e.g. 'export.csv').")
        .def("set_disposition_type", &Wt::WResource::setDispositionType,
             "disposition"_a)
        .def("set_changed", &Wt::WResource::setChanged,
             "Invalidate any browser-side cache of this resource so the "
             "next fetch sees the latest data. Call after set_data() etc.")
        .def_prop_rw("internal_path",
            [](const Wt::WResource& r) { return r.internalPath(); },
            [](Wt::WResource& r, const std::string& p) { r.setInternalPath(p); })
        .def("set_invalid_after_changed", &Wt::WResource::setInvalidAfterChanged,
             "enabled"_a)
        .def("set_takes_update_lock", &Wt::WResource::setTakesUpdateLock,
             "enabled"_a,
             "When true, handle_request() acquires the session update lock "
             "before serving — required if your subclass touches widget "
             "state. Default is false (lock-free serving, faster).")
        .def("generate_url", &Wt::WResource::generateUrl,
             "Return a URL at which this resource can be fetched.");

    // ---- WStreamResource (intermediate) ----
    //
    // Bound as a base for WFileResource. Not directly constructed from
    // Python — its purpose is to be subclassed in C++ to feed bytes from
    // a std::istream. Users wanting streaming should hand a path to
    // WFileResource (file-on-disk) or use WMemoryResource (already-in-RAM).

    nb::class_<Wt::WStreamResource, Wt::WResource>(m, "WStreamResource")
        .def_prop_rw("mime_type",
            [](const Wt::WStreamResource& r) { return r.mimeType(); },
            [](Wt::WStreamResource& r, const std::string& m) { r.setMimeType(m); })
        .def("set_buffer_size", &Wt::WStreamResource::setBufferSize,
             "size"_a);

    // ---- WMemoryResource: serve in-memory bytes ----
    //
    // The data is set via Python `bytes`. To update what gets served:
    //
    //     r.data = new_bytes
    //     r.set_changed()           # invalidate cached version
    //
    // Construction takes a MIME type and optional initial bytes.

    nb::class_<Wt::WMemoryResource, Wt::WResource>(m, "WMemoryResource")
        .def(nb::init<>())
        .def(nb::init<const std::string&>(), "mime_type"_a)
        .def("__init__",
             [](Wt::WMemoryResource* self, const std::string& mime,
                nb::bytes data) {
                 const auto* p = reinterpret_cast<const unsigned char*>(data.c_str());
                 new (self) Wt::WMemoryResource(mime,
                     std::vector<unsigned char>(p, p + data.size()));
             },
             "mime_type"_a, "data"_a)
        .def_prop_rw("data",
            // Getter — return a Python `bytes` snapshot of the stored data.
            [](const Wt::WMemoryResource& r) {
                const auto& v = r.data();
                return nb::bytes(reinterpret_cast<const char*>(v.data()), v.size());
            },
            // Setter — accept Python `bytes`; set_changed() is the user's
            // call to invalidate the cached version.
            [](Wt::WMemoryResource& r, nb::bytes data) {
                const auto* p = reinterpret_cast<const unsigned char*>(data.c_str());
                r.setData(std::vector<unsigned char>(p, p + data.size()));
            })
        .def_prop_rw("mime_type",
            [](const Wt::WMemoryResource& r) { return r.mimeType(); },
            [](Wt::WMemoryResource& r, const std::string& m) { r.setMimeType(m); });

    // ---- WFileResource: serve a file from disk ----

    nb::class_<Wt::WFileResource, Wt::WStreamResource>(m, "WFileResource")
        .def(nb::init<>())
        .def(nb::init<const std::string&>(), "file_name"_a)
        .def(nb::init<const std::string&, const std::string&>(),
             "mime_type"_a, "file_name"_a)
        .def_prop_rw("file_name",
            [](const Wt::WFileResource& r) { return r.fileName(); },
            [](Wt::WFileResource& r, const std::string& f) { r.setFileName(f); });

    // ---- WLink (single binding) ----
    //
    // Lives here (not in bind_widgets.cpp) because it needs WResource bound
    // before its `shared_ptr<WResource>` implicit constructor can be
    // registered. Both implicit constructors mean any endpoint that takes a
    // WLink (WAnchor, WImage, the `link` setters) transparently accepts
    //   - a `str` (becomes a URL link), or
    //   - a `WResource` (becomes a resource link).

    nb::class_<Wt::WLink>(m, "WLink")
        .def(nb::init<>())
        .def(nb::init_implicit<const std::string&>(), "url"_a)
        .def(nb::init_implicit<std::shared_ptr<Wt::WResource>>(),
             "resource"_a)
        .def_prop_rw("url",
            [](const Wt::WLink& l) { return l.url(); },
            [](Wt::WLink& l, const std::string& u) { l.setUrl(u); });
}

}  // namespace witty_for_python
