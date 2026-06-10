# Resources & I/O

> Server-mounted resources, hyperlinks, file uploads and the drag-and-drop file widget. Pair with the Http submodule for outbound HTTP and the Request/Response handler API.

**Classes in this section:**

- [`ContentDisposition`](#ContentDisposition)
- [`WResource`](#WResource)
- [`WStreamResource`](#WStreamResource)
- [`WMemoryResource`](#WMemoryResource)
- [`WFileResource`](#WFileResource)
- [`CallbackResource`](#CallbackResource)
- [`WLink`](#WLink)
- [`UploadedFile`](#UploadedFile)
- [`WFileUpload`](#WFileUpload)
- [`FilePickerType`](#FilePickerType)
- [`WFileDropWidgetFile`](#WFileDropWidgetFile)
- [`WFileDropWidgetDirectory`](#WFileDropWidgetDirectory)
- [`FileSignal`](#FileSignal)
- [`FileListSignal`](#FileListSignal)
- [`FileSizeSignal`](#FileSizeSignal)
- [`WFileDropWidget`](#WFileDropWidget)

---

### ContentDisposition {#ContentDisposition}

*Inherits:* `enum.Enum`

Controls the `Content-Disposition` header on resource responses
— whether the browser displays the bytes inline, prompts the
user to save them, or leaves the header off. Pair with
`WResource.suggest_file_name` for the save filename.

### WResource {#WResource}

*Inherits:* `WObject`

Abstract base for anything Wt serves over HTTP that isn't the
widget tree itself — file downloads, generated PDFs, JSON APIs,
image data, etc. Mount via `WServer.add_resource(resource,
path)` for server-wide endpoints, or hand to a `WLink` for
session-scoped use (e.g. an inline image).

Two concrete subclasses ship in this binding — WMemoryResource
(in-RAM bytes) and WFileResource (file on disk). For dynamic
endpoints, use `CallbackResource(callable)` which delegates
handle_request to a Python function instead of requiring a
subclass.

**Properties**

- `internal_path: str` *(read/write)*
  Stable internal-path component of the resource's URL.
  Setting one lets you mount the resource at a known route
  rather than a generated hash.

**Methods**

- `suggest_file_name(self, name: str) -> None`
  Set the suggested filename the browser uses when saving the resource (e.g. 'export.csv').

- `set_disposition_type(self, disposition: ContentDisposition) -> None`
  Choose ContentDisposition.Attachment to force a 'Save As'
  prompt, .Inline to display in-page when the MIME type
  supports it, or .None_ to omit the header.

- `set_changed(self) -> None`
  Invalidate any browser-side cache of this resource so the next fetch sees the latest data. Call after set_data() etc.

- `set_invalid_after_changed(self, enabled: bool) -> None`
  When True, every `set_changed` invalidates any URL
  previously handed out — clients with the old URL will get
  404 and must re-fetch the URL. Default False (URL stays
  stable across content updates).

- `set_takes_update_lock(self, enabled: bool) -> None`
  When true, handle_request() acquires the session update lock before serving — required if your subclass touches widget state. Default is false (lock-free serving, faster).

- `generate_url(self) -> str`
  Return a URL at which this resource can be fetched.

### WStreamResource {#WStreamResource}

*Inherits:* `WResource`

Intermediate base for resources that stream their bytes from a
C++ `std::istream`. Bound here only so WFileResource can inherit
MIME-type and buffer-size knobs — for Python use, reach for
WFileResource (file on disk), WMemoryResource (bytes in RAM),
or CallbackResource (write whatever you want directly to the
Response).

**Properties**

- `mime_type: str` *(read/write)*
  Content-Type sent with each response.

**Methods**

- `set_buffer_size(self, size: int) -> None`
  Size in bytes of the chunk used to copy from the underlying
  stream to the HTTP response. Larger reduces syscall
  overhead; smaller improves first-byte latency.

### WMemoryResource {#WMemoryResource}

*Inherits:* `WResource`

WResource backed by an in-memory `bytes` blob. Useful for small
generated payloads (a CSV, a thumbnail) that shouldn't touch the
filesystem.

    payload = wt.WMemoryResource('text/csv', b'name,age\nAlice,30\n')
    server.add_resource(payload, '/export.csv')
    # later: rebuild and notify clients
    payload.data = render_csv(rows)
    payload.set_changed()

**Constructors**

- `__init__(self) -> None`
  Construct an empty memory resource with no MIME type or
  data set — assign both before serving.

- `__init__(self, mime_type: str) -> None`
  Construct a memory resource declaring `mime_type` with no
  data set yet. Assign `data` before mounting.

- `__init__(self, mime_type: str, data: bytes) -> None`
  Construct a memory resource ready to serve `data` as
  `mime_type`.

**Properties**

- `data: bytes` *(read/write)*
  The bytes served. Reading returns a copy as `bytes`;
  assigning replaces the served payload. Call `set_changed`
  afterwards to invalidate any browser cache.

- `mime_type: str` *(read/write)*
  Content-Type returned with the bytes.

### WFileResource {#WFileResource}

*Inherits:* `WStreamResource`

WResource that streams a file on disk. Wt opens the file per
request and copies bytes through to the HTTP response, so the
file can change between fetches without restarting the server.

    server.add_resource(
        wt.WFileResource('application/pdf', '/var/data/report.pdf'),
        '/report.pdf')

**Constructors**

- `__init__(self) -> None`
  Construct an empty file resource with no file or MIME type
  set. Assign both before serving.

- `__init__(self, file_name: str) -> None`
  Construct a file resource pointing at `file_name`. The
  MIME type is left at the inherited default — set
  `mime_type` afterwards.

- `__init__(self, mime_type: str, file_name: str) -> None`
  Construct a file resource that serves `file_name` with
  `mime_type` as its Content-Type.

**Properties**

- `file_name: str` *(read/write)*
  Filesystem path of the file to serve. Assigning swaps the
  source — call `set_changed` afterwards to invalidate caches.

### CallbackResource {#CallbackResource}

*Inherits:* `WResource`

WResource whose `handle_request` delegates to a Python callable.
The Pythonic way to expose a dynamic HTTP endpoint without
subclassing — the equivalent of a Flask/Django view function in
the Wt world.

    def api(req, resp):
        resp.set_mime_type('application/json')
        resp.write(b'{"ok": true}')
    server.add_resource(wt.CallbackResource(api), '/api/ping')

Wt invokes the callable on a worker thread with `(request,
response)`; the binding takes the GIL around the call. The
request/response wrappers are valid only for the duration of
the invocation — don't stash them. Captured state in the
callable (closures, class attrs) persists across requests; the
CallbackResource holds a strong reference to the callable.

**Constructors**

- `__init__(self, callback: Callable) -> None`
  Mount a Python callable as an HTTP endpoint. The callable is invoked as `callback(request, response)` on every request, with the GIL held. Exceptions are routed through `PyErr_WriteUnraisable` rather than crashing Wt's worker.

### WLink {#WLink}

Polymorphic link target — wraps a URL string OR a server-side
WResource. Used by WAnchor, WImage, WPushButton.link, etc.;
Python's implicit conversion lets you pass a bare str or a
WResource and get the corresponding WLink automatically.

    container.add_widget(wt.WAnchor(wt.WLink('https://example.com'), 'Visit'))

    chart = wt.WMemoryResource('image/png', render_png())
    container.add_widget(wt.WImage(wt.WLink(chart), 'Chart'))

For URL fragments that should drive WApplication.internal_path
navigation rather than a full page load, set `internal_path` on
the link or use the `wt.internal_path('/route')` factory.

**Constructors**

- `__init__(self) -> None`
  Construct an empty link with no target.

- `__init__(self, url: str) -> None`
  Construct a link to an external URL or any same-origin path.
  Plain `str` arguments to widgets that take a WLink hit this
  constructor automatically.

- `__init__(self, resource: WResource) -> None`
  Construct a link to a WResource. The resource's URL is
  computed by Wt; clients fetch the dynamic content when the
  link is followed. A `WResource` arg to widgets that take a
  WLink hits this constructor automatically.

**Properties**

- `url: str` *(read/write)*
  The link target as a URL string.

- `internal_path: str` *(read/write)*
  Treat the link as an internal-path navigation rather than an
  external URL. Setting this makes a click update the URL
  fragment and fire `WApplication.on_internal_path_changed`
  instead of reloading the page.

### UploadedFile {#UploadedFile}

One file's worth of metadata + on-disk path for an upload
delivered through WFileUpload (or returned by
WFileDropWidget.File.uploaded_file). The bytes live in a Wt-
managed temp file at `spool_file_name`; read or move them before
the request that produced this record is torn down — Wt deletes
the temp file as part of its cleanup unless
`WFileUpload.steal_spooled_file` has been called.

**Properties**

- `spool_file_name: str` *(read-only)*
  Filesystem path to the spooled temp file holding the upload's bytes. Read this before the request handler returns — Wt deletes the file on cleanup unless steal_spooled_file is called.

- `client_file_name: str` *(read-only)*
  Original filename as reported by the browser. Treat as untrusted user input — do NOT use it as a server-side path unchecked.

- `content_type: str` *(read-only)*
  MIME type reported by the browser. Same caveat: untrusted.

### WFileUpload {#WFileUpload}

*Inherits:* `WWidget`

Classic HTML file-input widget — a button + filename label.
Pick a file, call `upload()` (typically right out of the
`changed` signal), then read the bytes from `spool_file_name`
when `uploaded` fires.

    up = container.add_widget(wt.WFileUpload())
    def kick_off():
        up.upload()
    def on_done():
        if not up.empty:
            shutil.copy(up.spool_file_name, '/store/last')
    up.changed.connect(kick_off)
    up.uploaded.connect(on_done)

Set `multiple = True` and walk `uploaded_files` instead of
`spool_file_name` for multi-file uploads. The bytes land in a
temp file Wt cleans up after the request; copy/move them
elsewhere before that happens. For drag-and-drop or queue-style
uploads use WFileDropWidget instead.

**Constructors**

- `__init__(self) -> None`
  Construct an empty single-file uploader.

**Properties**

- `multiple: bool` *(read/write)*
  When True, the browser allows selecting more than one file. After upload, walk `uploaded_files` instead of `spool_file_name`.

- `file_text_size: int` *(read/write)*
  Approximate visible width of the file-input control in chars.

- `empty: bool` *(read-only)*
  True iff no file has been successfully uploaded.

- `can_upload: bool` *(read-only)*
  True iff a subsequent call to upload() will start a new upload request (vs. being a no-op).

- `spool_file_name: str` *(read-only)*
  Filesystem path to the single-file upload's spool file. For multi-uploads use `uploaded_files`.

- `uploaded_files: list[UploadedFile]` *(read-only)*
  List of UploadedFile records — one per file the browser sent.

- `changed: EventSignal` *(read-only)*
  EventSignal[] — fires when the user picks a file in the browser. Usual slot calls .upload().

- `uploaded: EventSignal` *(read-only)*
  EventSignal[] — fires when an upload finishes, successful or not. Check `empty` to distinguish.

- `file_too_large: 'Wt::JSignal<long>'` *(read-only)*
  JInt64Signal — fires with the rejected file's size in bytes when the user tried to upload more than the configured max-request-size. The upload itself was discarded server-side.

- `data_received: 'Wt::Signal<unsigned long, unsigned long>'` *(read-only)*
  Uint64PairSignal — fires periodically during a long upload with (bytes_received, bytes_total). Wire up before calling upload() and pair with set_progress_bar for a built-in progress UI.

**Methods**

- `upload(self) -> None`
  Start the upload. Typically called from a slot connected to `changed` so picking a file triggers the upload immediately.

- `set_filters(self, accept_attributes: str) -> None`
  Comma-separated MIME types or extensions used as the HTML accept= attribute, e.g. 'image/png,image/jpeg' or '.csv,.tsv'. Hint only — the browser may still let users pick other files, so re-check content_type server-side.

### FilePickerType {#FilePickerType}

*Inherits:* `enum.Enum`

Which native browser picker WFileDropWidget opens when the
user clicks the dropzone — files, folders, or neither.

### WFileDropWidgetFile {#WFileDropWidgetFile}

*Inherits:* `WObject`

Metadata + per-file signals for one file that has been (or is
being) uploaded through a WFileDropWidget. Read the browser-
reported `client_file_name` / `size` / `mime_type` before the
transfer starts; wait on `uploaded` to get `uploaded_file`, which
carries the on-disk path of the spooled bytes.

    def on_done(f):
        print(f.client_file_name, '->', f.uploaded_file.spool_file_name)
    drop.uploaded.connect(on_done)

Owned by the parent WFileDropWidget — pointers handed to signal
callbacks are valid only as long as the widget keeps the file in
its `uploads` list. Don't stash them beyond the callback.

**Properties**

- `client_file_name: str` *(read-only)*
  Original filename reported by the browser. Untrusted — sanitise before use as a server-side path.

- `path: str` *(read-only)*
  Relative path inside the dropped folder, or empty if a single file was dropped.

- `directory: bool` *(read-only)*
  True iff this entry represents a directory (only when the browser supports folder uploads and the user dropped one).

- `mime_type: str` *(read-only)*
  MIME type reported by the browser. Untrusted.

- `size: int` *(read-only)*
  File size in bytes as reported by the browser, before the upload starts.

- `upload_finished: bool` *(read-only)*
  True iff the bytes have arrived server-side.

- `uploaded_file: UploadedFile` *(read-only)*
  The completed upload, as an UploadedFile (with the spool file path). Raises if called before `upload_finished` is True.

- `data_received: 'Wt::Signal<unsigned long, unsigned long>'` *(read-only)*
  Uint64PairSignal — per-file progress ticks (received, total) in bytes.

- `uploaded: Signal` *(read-only)*
  Signal[] — fires when this individual file's upload finishes. WFileDropWidget.uploaded fires too with the File* payload.

- `filter_enabled: bool` *(read/write)*
  Whether the JS filter (set via WFileDropWidget) processes this file before upload. Defaults to True when a filter is set.

- `is_filtered: bool` *(read-only)*
  True iff the JS filter already ran on this file's bytes.

### WFileDropWidgetDirectory {#WFileDropWidgetDirectory}

*Inherits:* `WFileDropWidgetFile`

A File subclass representing a dropped folder rather than a
single file. Only produced when the widget has
`set_accept_directories(True)` and the user drops a folder; check
`isinstance(f, wt.WFileDropWidget.Directory)` from a drop handler
to branch on it. `contents` walks the folder's entries (which may
themselves be Directories for recursive drops).

**Properties**

- `contents: list[WFileDropWidgetFile]` *(read-only)*
  List[File] — children of this folder. For recursive drops these may themselves include further Directory entries.

- `directory: bool` *(read-only)*
  Always True for Directory — shadows File.directory() for ergonomic type discrimination.

### FileSignal {#FileSignal}

Signal carrying a single WFileDropWidget.File pointer. Used by
the widget's `new_upload`, `uploaded`, and `upload_failed`
signals — connect a `callable(file)` to react.

**Methods**

- `connect(self, callable: Callable) -> Connection`
  Subscribe `callable(file)` to the signal. Returns a
  Connection — call `.disconnect()` to stop receiving.

- `disconnect_all_slots(self) -> None`
  Drop every callback previously connected through this binding.

### FileListSignal {#FileListSignal}

Signal carrying a list of WFileDropWidget.File pointers. Used by
the widget's `drop` signal — fires once per drop event with the
freshly-introduced files.

**Methods**

- `connect(self, callable: Callable) -> Connection`
  Subscribe `callable(files)` to the signal. Returns a
  Connection — call `.disconnect()` to stop receiving.

- `disconnect_all_slots(self) -> None`
  Drop every callback previously connected through this binding.

### FileSizeSignal {#FileSizeSignal}

Signal carrying (file, size_bytes). Used by `too_large` when a
dropped file exceeds the configured maximum request size.

**Methods**

- `connect(self, callable: Callable) -> Connection`
  Subscribe `callable(file, size)` to the signal. Returns a
  Connection — call `.disconnect()` to stop receiving.

- `disconnect_all_slots(self) -> None`
  Drop every callback previously connected through this binding.

### WFileDropWidget {#WFileDropWidget}

*Inherits:* `WContainerWidget`

Drag-and-drop upload zone. Drop files (and optionally folders)
onto the widget, or click it to open the browser's native
picker. Files queue up and upload sequentially in the background
so the UI stays responsive; per-file lifecycle signals let you
render a queue / progress list.

    drop = container.add_widget(wt.WFileDropWidget())
    drop.add_widget(wt.WText('Drop files here'))
    def on_drop(files):
        for f in files:
            print('queued:', f.client_file_name)
    drop.drop.connect(on_drop)
    def on_done(f):
        shutil.move(f.uploaded_file.spool_file_name, '/store/' + f.client_file_name)
    drop.uploaded.connect(on_done)

Inherits WContainerWidget — child widgets become the visible
body (instructions, an icon, …). Uploaded bytes land in a temp
spool file; copy or move them somewhere durable before the file
is dropped from `uploads`.

**Constructors**

- `__init__(self) -> None`
  Construct an empty drop zone that accepts files (not
  folders) and shows the browser's file picker on click.

**Properties**

- `uploads: list[WFileDropWidgetFile]` *(read-only)*
  List[File] — all files known to the widget, including ones whose upload is queued, in progress, completed, or cancelled. Pointers reference internal widget state.

- `current_index: int` *(read-only)*
  Index into `uploads` of the file currently being transmitted. Equals len(uploads) when idle.

- `drop_indication_enabled: bool` *(read/write)*
  When True, the widget visually highlights itself during hover. When False the host page is responsible for any drop UI.

- `global_drop_enabled: bool` *(read/write)*
  When True, files dropped anywhere on the page route to this widget. Use sparingly — only one widget per app should set this.

- `on_click_file_picker: FilePickerType` *(read-only)*
  The FilePickerType the widget opens on click.

- `drop: FileListSignal` *(read-only)*
  FileListSignal — fires once per drop with the list of newly-introduced File entries (these get appended to `uploads`). The actual byte transfer is sequential and tracked through `new_upload` / `uploaded`.

- `new_upload: FileSignal` *(read-only)*
  FileSignal — fires immediately before the bytes of the next file in the queue start arriving.

- `uploaded: FileSignal` *(read-only)*
  FileSignal — fires when a single file's upload completes. The File's `uploaded_file` is now valid.

- `too_large: FileSizeSignal` *(read-only)*
  FileSizeSignal — fires with (file, size) when one of the dropped files exceeds the configured max-request-size. That file's upload is skipped; the queue carries on with the next.

- `upload_failed: FileSignal` *(read-only)*
  FileSignal — fires when an upload errors out for reasons other than oversize (e.g. browser disconnect).

**Methods**

- `cancel_upload(self, file: WFileDropWidgetFile) -> None`
  Cancel a queued or in-progress upload. The File stays in `uploads` but is marked cancelled.

- `remove(self, file: WFileDropWidgetFile) -> bool`
  Drop a completed file from `uploads` to free its temp file. Only valid for files at indices strictly before current_index.

- `clean_directory_resources(self) -> None`
  Release Directory bookkeeping once you no longer need it. Files themselves remain.

- `set_accept_drops(self, enable: bool) -> None`
  When True (the default), drag-and-drop is active. Set to
  False to limit input to the click-to-pick path.

- `set_filters(self, accept_attributes: str) -> None`
  Hint to the file-picker dialog: a comma-separated list of MIME types or extensions (e.g. 'image/png,.csv'). Doesn't constrain drag-drop — re-check content_type server-side.

- `set_on_click_file_picker(self, type: FilePickerType) -> None`
  Which browser dialog opens when the user clicks the widget: FilePickerType.FileSelection (default), .DirectorySelection, or .None_ to disable.

- `open_file_picker(self) -> None`
  Programmatically open the file picker as if the user clicked. Useful when wiring the widget to an external button.

- `open_directory_picker(self) -> None`
  Programmatically open the directory picker. Requires that
  `set_accept_directories(True)` has been set.

- `set_accept_directories(self, enable: bool, recursive: bool = False) -> None`
  Allow folder drops. When `recursive` is True, subfolders are also walked. Default is files-only.
