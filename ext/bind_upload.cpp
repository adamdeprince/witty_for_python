#include "common.hpp"

#include <Wt/Http/Request.h>
#include <Wt/WFileUpload.h>

namespace witty_for_python {

void register_upload(nb::module_& m) {
    // ---- Http::UploadedFile: metadata + path of a single uploaded file ----
    //
    // Returned by WFileUpload.uploaded_files for multi-file uploads. The
    // spool file is a temp file Wt manages; read it from disk before the
    // request is destroyed (or call WFileUpload.steal_spooled_file to take
    // ownership and prevent Wt from cleaning it up).

    nb::class_<Wt::Http::UploadedFile>(m, "UploadedFile")
        .def_prop_ro("spool_file_name",
            [](const Wt::Http::UploadedFile& f) { return f.spoolFileName(); },
            "Filesystem path to the spooled temp file holding the upload's "
            "bytes. Read this before the request handler returns — Wt deletes "
            "the file on cleanup unless steal_spooled_file is called.")
        .def_prop_ro("client_file_name",
            [](const Wt::Http::UploadedFile& f) { return f.clientFileName(); },
            "Original filename as reported by the browser. Treat as untrusted "
            "user input — do NOT use it as a server-side path unchecked.")
        .def_prop_ro("content_type",
            [](const Wt::Http::UploadedFile& f) { return f.contentType(); },
            "MIME type reported by the browser. Same caveat: untrusted.");

    // ---- WFileUpload: the upload widget itself ----
    //
    // Lifecycle:
    //   1. Connect a slot to `changed` so something happens when the user
    //      picks a file. Typical pattern is to call `upload()` from that
    //      slot — modern browsers handle the upload silently via XHR.
    //   2. Connect a slot to `uploaded` to react when the bytes have
    //      arrived; read them from `spool_file_name` (single upload) or
    //      walk `uploaded_files` (multi).
    //
    // Bound signals: `changed`, `uploaded` (both EventSignal<>),
    // `file_too_large` (JInt64Signal — fires with the offending size in
    // bytes), and `data_received` (Uint64PairSignal — fires periodically
    // during a long upload with (received, total) byte counts).

    nb::class_<Wt::WFileUpload, Wt::WWidget>(m, "WFileUpload")
        .def(heap_init<Wt::WFileUpload>())
        .def_prop_rw("multiple",
            &Wt::WFileUpload::multiple,
            &Wt::WFileUpload::setMultiple,
            "When True, the browser allows selecting more than one file. "
            "After upload, walk `uploaded_files` instead of `spool_file_name`.")
        .def_prop_rw("file_text_size",
            &Wt::WFileUpload::fileTextSize,
            &Wt::WFileUpload::setFileTextSize,
            "Approximate visible width of the file-input control in chars.")
        .def_prop_ro("empty", &Wt::WFileUpload::empty,
            "True iff no file has been successfully uploaded.")
        .def_prop_ro("can_upload", &Wt::WFileUpload::canUpload,
            "True iff a subsequent call to upload() will start a new upload "
            "request (vs. being a no-op).")
        .def_prop_ro("spool_file_name",
            [](const Wt::WFileUpload& u) { return u.spoolFileName(); },
            "Filesystem path to the single-file upload's spool file. For "
            "multi-uploads use `uploaded_files`.")
        .def_prop_ro("uploaded_files",
            [](const Wt::WFileUpload& u) {
                // Copy out — the underlying vector is owned by the widget
                // and may be invalidated on later uploads.
                return std::vector<Wt::Http::UploadedFile>(
                    u.uploadedFiles().begin(), u.uploadedFiles().end());
            },
            "List of UploadedFile records — one per file the browser sent.")
        .def("upload", &Wt::WFileUpload::upload,
             "Start the upload. Typically called from a slot connected to "
             "`changed` so picking a file triggers the upload immediately.")
        .def("set_filters", &Wt::WFileUpload::setFilters, "accept_attributes"_a,
             "Comma-separated MIME types or extensions used as the HTML "
             "accept= attribute, e.g. 'image/png,image/jpeg' or '.csv,.tsv'. "
             "Hint only — the browser may still let users pick other files, "
             "so re-check content_type server-side.")
        .def_prop_ro("changed", &Wt::WFileUpload::changed,
                     nb::rv_policy::reference_internal,
                     "EventSignal[] — fires when the user picks a file in "
                     "the browser. Usual slot calls .upload().")
        .def_prop_ro("uploaded", &Wt::WFileUpload::uploaded,
                     nb::rv_policy::reference_internal,
                     "EventSignal[] — fires when an upload finishes, "
                     "successful or not. Check `empty` to distinguish.")
        .def_prop_ro("file_too_large", &Wt::WFileUpload::fileTooLarge,
                     nb::rv_policy::reference_internal,
                     "JInt64Signal — fires with the rejected file's size "
                     "in bytes when the user tried to upload more than the "
                     "configured max-request-size. The upload itself was "
                     "discarded server-side.")
        .def_prop_ro("data_received", &Wt::WFileUpload::dataReceived,
                     nb::rv_policy::reference_internal,
                     "Uint64PairSignal — fires periodically during a long "
                     "upload with (bytes_received, bytes_total). Wire up "
                     "before calling upload() and pair with set_progress_bar "
                     "for a built-in progress UI.");
}

}  // namespace witty_for_python
