#include "common.hpp"
#include "signal_helpers.hpp"

#include <Wt/WFileDropWidget.h>

#include <cstdint>
#include <vector>

namespace witty_for_python {

void register_filedrop(nb::module_& m) {
    using File = Wt::WFileDropWidget::File;
    using Directory = Wt::WFileDropWidget::Directory;

    // ---- FilePickerType enum ----

    nb::enum_<Wt::FilePickerType>(m, "FilePickerType",
        "Which native browser picker WFileDropWidget opens when the\n"
        "user clicks the dropzone — files, folders, or neither.")
        .value("None_", Wt::FilePickerType::None)
        .value("FileSelection", Wt::FilePickerType::FileSelection)
        .value("DirectorySelection", Wt::FilePickerType::DirectorySelection);

    // ---- WFileDropWidget::File ----
    //
    // The C++ object is owned by WFileDropWidget — Python wrappers around
    // File* are non-owning views. The widget destroys File instances when
    // `remove()` is called or when the widget itself is destroyed; the
    // signal payloads we expose deliver pointers that are valid only for
    // the duration of the slot call. Don't stash them for later.
    //
    // The File class is registered as a top-level Python class
    // `WFileDropWidgetFile` and re-attached as `WFileDropWidget.File` below
    // for the natural nested form.

    auto file_cls = nb::class_<File, Wt::WObject>(m, "WFileDropWidgetFile",
        "Metadata + per-file signals for one file that has been (or is\n"
        "being) uploaded through a WFileDropWidget. Read the browser-\n"
        "reported `client_file_name` / `size` / `mime_type` before the\n"
        "transfer starts; wait on `uploaded` to get `uploaded_file`, which\n"
        "carries the on-disk path of the spooled bytes.\n"
        "\n"
        "    def on_done(f):\n"
        "        print(f.client_file_name, '->', f.uploaded_file.spool_file_name)\n"
        "    drop.uploaded.connect(on_done)\n"
        "\n"
        "Owned by the parent WFileDropWidget — pointers handed to signal\n"
        "callbacks are valid only as long as the widget keeps the file in\n"
        "its `uploads` list. Don't stash them beyond the callback.");
    file_cls
        .def_prop_ro("client_file_name", &File::clientFileName,
            "Original filename reported by the browser. Untrusted — sanitise "
            "before use as a server-side path.")
        .def_prop_ro("path", &File::path,
            "Relative path inside the dropped folder, or empty if a single "
            "file was dropped.")
        .def_prop_ro("directory", &File::directory,
            "True iff this entry represents a directory (only when the "
            "browser supports folder uploads and the user dropped one).")
        .def_prop_ro("mime_type", &File::mimeType,
            "MIME type reported by the browser. Untrusted.")
        .def_prop_ro("size", &File::size,
            "File size in bytes as reported by the browser, before the "
            "upload starts.")
        .def_prop_ro("upload_finished", &File::uploadFinished,
            "True iff the bytes have arrived server-side.")
        .def_prop_ro("uploaded_file",
            [](const File& f) -> const Wt::Http::UploadedFile& {
                // Throws if upload_finished is False. Wt's exception is
                // forwarded as a Python RuntimeError via nanobind.
                return f.uploadedFile();
            },
            nb::rv_policy::reference_internal,
            "The completed upload, as an UploadedFile (with the spool file "
            "path). Raises if called before `upload_finished` is True.")
        .def_prop_ro("data_received", &File::dataReceived,
            nb::rv_policy::reference_internal,
            "Uint64PairSignal — per-file progress ticks "
            "(received, total) in bytes.")
        .def_prop_ro("uploaded", &File::uploaded,
            nb::rv_policy::reference_internal,
            "Signal[] — fires when this individual file's upload finishes. "
            "WFileDropWidget.uploaded fires too with the File* payload.")
        .def_prop_rw("filter_enabled",
            &File::filterEnabled, &File::setFilterEnabled,
            "Whether the JS filter (set via WFileDropWidget) processes this "
            "file before upload. Defaults to True when a filter is set.")
        .def_prop_ro("is_filtered", &File::isFiltered,
            "True iff the JS filter already ran on this file's bytes.");

    // ---- WFileDropWidget::Directory (File subclass) ----
    //
    // Bound minimally so isinstance(f, wt.WFileDropWidget.Directory) works
    // when the drop signal hands you a folder rather than a flat file. The
    // `contents()` accessor walks the folder's File entries (also non-owning
    // — pointers belong to the widget).

    auto dir_cls = nb::class_<Directory, File>(m, "WFileDropWidgetDirectory",
        "A File subclass representing a dropped folder rather than a\n"
        "single file. Only produced when the widget has\n"
        "`set_accept_directories(True)` and the user drops a folder; check\n"
        "`isinstance(f, wt.WFileDropWidget.Directory)` from a drop handler\n"
        "to branch on it. `contents` walks the folder's entries (which may\n"
        "themselves be Directories for recursive drops).")
        .def_prop_ro("contents",
            [](const Directory& d) {
                // Copy out the const-ref vector so Python gets a list it
                // can iterate freely.
                return std::vector<File*>(d.contents().begin(),
                                          d.contents().end());
            },
            "List[File] — children of this folder. For recursive drops "
            "these may themselves include further Directory entries.")
        .def_prop_ro("directory",
            [](const Directory&) { return true; },
            "Always True for Directory — shadows File.directory() for "
            "ergonomic type discrimination.");

    // ---- Signal types whose payload is File* or vector<File*> ----
    //
    // nb::rv_policy on the inner type defaults to reference (non-owning) for
    // raw pointer payloads, which is what we want — these pointers belong to
    // the widget. Bound here (not in bind_signals.cpp) because File must be
    // registered first.

    nb::class_<Wt::Signal<File*>>(m, "FileSignal",
        "Signal carrying a single WFileDropWidget.File pointer. Used by\n"
        "the widget's `new_upload`, `uploaded`, and `upload_failed`\n"
        "signals — connect a `callable(file)` to react.")
        .def("connect",
            [](Wt::Signal<File*>& s, nb::callable cb) {
                return py_connect<Wt::Signal<File*>, File*>(s, std::move(cb));
            }, "callable"_a,
            "Subscribe `callable(file)` to the signal. Returns a\n"
            "Connection — call `.disconnect()` to stop receiving.")
        .def("disconnect_all_slots",
            [](Wt::Signal<File*>& s) {
                connection_registry_disconnect_all(&s);
            },
            "Drop every callback previously connected through this binding.");

    nb::class_<Wt::Signal<std::vector<File*>>>(m, "FileListSignal",
        "Signal carrying a list of WFileDropWidget.File pointers. Used by\n"
        "the widget's `drop` signal — fires once per drop event with the\n"
        "freshly-introduced files.")
        .def("connect",
            [](Wt::Signal<std::vector<File*>>& s, nb::callable cb) {
                return py_connect<Wt::Signal<std::vector<File*>>,
                                  std::vector<File*>>(s, std::move(cb));
            }, "callable"_a,
            "Subscribe `callable(files)` to the signal. Returns a\n"
            "Connection — call `.disconnect()` to stop receiving.")
        .def("disconnect_all_slots",
            [](Wt::Signal<std::vector<File*>>& s) {
                connection_registry_disconnect_all(&s);
            },
            "Drop every callback previously connected through this binding.");

    nb::class_<Wt::Signal<File*, std::uint64_t>>(m, "FileSizeSignal",
        "Signal carrying (file, size_bytes). Used by `too_large` when a\n"
        "dropped file exceeds the configured maximum request size.")
        .def("connect",
            [](Wt::Signal<File*, std::uint64_t>& s, nb::callable cb) {
                return py_connect<Wt::Signal<File*, std::uint64_t>,
                                  File*, std::uint64_t>(s, std::move(cb));
            }, "callable"_a,
            "Subscribe `callable(file, size)` to the signal. Returns a\n"
            "Connection — call `.disconnect()` to stop receiving.")
        .def("disconnect_all_slots",
            [](Wt::Signal<File*, std::uint64_t>& s) {
                connection_registry_disconnect_all(&s);
            },
            "Drop every callback previously connected through this binding.");

    // ---- WFileDropWidget ----
    //
    // Drop-zone for uploading files (and optionally folders) by drag-drop or
    // by clicking the widget to open the browser's native picker. Unlike
    // WFileUpload, the drop widget uploads files sequentially in the
    // background and emits per-file lifecycle signals so the UI can show a
    // queue.
    //
    // Inherits WContainerWidget — content placed inside the widget (a label,
    // an icon, instructions) is shown as the dropzone's body.

    auto drop_cls = nb::class_<Wt::WFileDropWidget, Wt::WContainerWidget>(
        m, "WFileDropWidget",
        "Drag-and-drop upload zone. Drop files (and optionally folders)\n"
        "onto the widget, or click it to open the browser's native\n"
        "picker. Files queue up and upload sequentially in the background\n"
        "so the UI stays responsive; per-file lifecycle signals let you\n"
        "render a queue / progress list.\n"
        "\n"
        "    drop = container.add_widget(wt.WFileDropWidget())\n"
        "    drop.add_widget(wt.WText('Drop files here'))\n"
        "    def on_drop(files):\n"
        "        for f in files:\n"
        "            print('queued:', f.client_file_name)\n"
        "    drop.drop.connect(on_drop)\n"
        "    def on_done(f):\n"
        "        shutil.move(f.uploaded_file.spool_file_name, '/store/' + f.client_file_name)\n"
        "    drop.uploaded.connect(on_done)\n"
        "\n"
        "Inherits WContainerWidget — child widgets become the visible\n"
        "body (instructions, an icon, …). Uploaded bytes land in a temp\n"
        "spool file; copy or move them somewhere durable before the file\n"
        "is dropped from `uploads`.");
    drop_cls
        .def(heap_init<Wt::WFileDropWidget>(),
             "Construct an empty drop zone that accepts files (not\n"
             "folders) and shows the browser's file picker on click.")
        .def_prop_ro("uploads", &Wt::WFileDropWidget::uploads,
                     "List[File] — all files known to the widget, including "
                     "ones whose upload is queued, in progress, completed, "
                     "or cancelled. Pointers reference internal widget state.")
        .def_prop_ro("current_index", &Wt::WFileDropWidget::currentIndex,
                     "Index into `uploads` of the file currently being "
                     "transmitted. Equals len(uploads) when idle.")
        .def("cancel_upload", &Wt::WFileDropWidget::cancelUpload, "file"_a,
             "Cancel a queued or in-progress upload. The File stays in "
             "`uploads` but is marked cancelled.")
        .def("remove", &Wt::WFileDropWidget::remove, "file"_a,
             "Drop a completed file from `uploads` to free its temp file. "
             "Only valid for files at indices strictly before current_index.")
        .def("clean_directory_resources",
             &Wt::WFileDropWidget::cleanDirectoryResources,
             "Release Directory bookkeeping once you no longer need it. "
             "Files themselves remain.")
        .def("set_accept_drops", &Wt::WFileDropWidget::setAcceptDrops,
             "enable"_a,
             "When True (the default), drag-and-drop is active. Set to\n"
             "False to limit input to the click-to-pick path.")
        .def("set_filters", &Wt::WFileDropWidget::setFilters,
             "accept_attributes"_a,
             "Hint to the file-picker dialog: a comma-separated list of "
             "MIME types or extensions (e.g. 'image/png,.csv'). Doesn't "
             "constrain drag-drop — re-check content_type server-side.")
        .def_prop_rw("drop_indication_enabled",
            &Wt::WFileDropWidget::dropIndicationEnabled,
            &Wt::WFileDropWidget::setDropIndicationEnabled,
            "When True, the widget visually highlights itself during hover. "
            "When False the host page is responsible for any drop UI.")
        .def_prop_rw("global_drop_enabled",
            &Wt::WFileDropWidget::globalDropEnabled,
            &Wt::WFileDropWidget::setGlobalDropEnabled,
            "When True, files dropped anywhere on the page route to this "
            "widget. Use sparingly — only one widget per app should set this.")
        .def("set_on_click_file_picker",
             &Wt::WFileDropWidget::setOnClickFilePicker, "type"_a,
             "Which browser dialog opens when the user clicks the widget: "
             "FilePickerType.FileSelection (default), .DirectorySelection, "
             "or .None_ to disable.")
        .def_prop_ro("on_click_file_picker",
                     &Wt::WFileDropWidget::onClickFilePicker,
                     "The FilePickerType the widget opens on click.")
        .def("open_file_picker", &Wt::WFileDropWidget::openFilePicker,
             "Programmatically open the file picker as if the user clicked. "
             "Useful when wiring the widget to an external button.")
        .def("open_directory_picker",
             &Wt::WFileDropWidget::openDirectoryPicker,
             "Programmatically open the directory picker. Requires that\n"
             "`set_accept_directories(True)` has been set.")
        .def("set_accept_directories",
             &Wt::WFileDropWidget::setAcceptDirectories,
             "enable"_a, "recursive"_a = false,
             "Allow folder drops. When `recursive` is True, subfolders are "
             "also walked. Default is files-only.")
        // ---- signals ----
        .def_prop_ro("drop", &Wt::WFileDropWidget::drop,
                     nb::rv_policy::reference_internal,
                     "FileListSignal — fires once per drop with the list of "
                     "newly-introduced File entries (these get appended to "
                     "`uploads`). The actual byte transfer is sequential and "
                     "tracked through `new_upload` / `uploaded`.")
        .def_prop_ro("new_upload", &Wt::WFileDropWidget::newUpload,
                     nb::rv_policy::reference_internal,
                     "FileSignal — fires immediately before the bytes of "
                     "the next file in the queue start arriving.")
        .def_prop_ro("uploaded", &Wt::WFileDropWidget::uploaded,
                     nb::rv_policy::reference_internal,
                     "FileSignal — fires when a single file's upload "
                     "completes. The File's `uploaded_file` is now valid.")
        .def_prop_ro("too_large", &Wt::WFileDropWidget::tooLarge,
                     nb::rv_policy::reference_internal,
                     "FileSizeSignal — fires with (file, size) when one of "
                     "the dropped files exceeds the configured max-request-"
                     "size. That file's upload is skipped; the queue carries "
                     "on with the next.")
        .def_prop_ro("upload_failed", &Wt::WFileDropWidget::uploadFailed,
                     nb::rv_policy::reference_internal,
                     "FileSignal — fires when an upload errors out for "
                     "reasons other than oversize (e.g. browser disconnect).");

    // Re-attach the File class as WFileDropWidget.File for the natural
    // nested form, mirroring how WSuggestionPopup.Options is exposed.
    drop_cls.attr("File") = file_cls;
    drop_cls.attr("Directory") = dir_cls;
}

}  // namespace witty_for_python
