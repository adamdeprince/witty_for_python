# Application & Core Types

> The per-session WApplication, the base widget classes every concrete widget inherits, the threading-aware UpdateLock, and the WServer entry point.

**Classes in this section:**

- [`WApplication`](#WApplication)
- [`WEnvironment`](#WEnvironment)
- [`WObject`](#WObject)
- [`WWidget`](#WWidget)
- [`WInteractWidget`](#WInteractWidget)
- [`WFormWidget`](#WFormWidget)
- [`UpdateLock`](#UpdateLock)
- [`WServer`](#WServer)
- [`EntryPointType`](#EntryPointType)

---

### WApplication {#WApplication}

*Inherits:* `WObject`

The per-session Wt application instance. One WApplication is
constructed per browser session by the factory you pass to
WServer.add_entry_point, and lives until that session ends.
It owns the page's root container, the URL state, and the
server→client update channel.

    def create_app(env):
        app = wt.WApplication(env)
        app.title = 'Hello'
        app.root.add_widget(wt.WText('Welcome.'))
        app.root.add_widget(wt.WPushButton('Quit')).clicked.connect(app.quit)
        return app

    server = wt.WServer()
    server.set_server_configuration(sys.argv)
    server.add_entry_point(wt.EntryPointType.Application, create_app)
    server.run()

Inside a session, `WApplication.instance()` returns the current
WApplication on any Wt-managed thread — useful for code that
doesn't have a direct reference to it.

**Constructors**

- `__init__(self, environment: WEnvironment) -> None`
  Construct the per-session application from the WEnvironment
  passed into your factory. The first thing your entry-point
  factory typically does.

**Properties**

- `root: WContainerWidget` *(read-only)*
  The top-level WContainerWidget — start `add_widget`-
  ing UI here. Owned by the application; lives as long
  as the session does.

- `environment: WEnvironment` *(read-only)*
  The captured WEnvironment from construction time.
  Use for read-only browser/session info.

- `title: str` *(read/write)*
  The page's `<title>` text. Assigning updates the browser
  tab on the next round-trip.

- `internal_path: str` *(read-only)*
  The current URL fragment / internal path. Mirrors what's
  shown after the `#` in the browser address bar.

- `session_id: str` *(read-only)*
  Opaque per-session string. Pass to `WServer.post` to
  schedule cross-thread work back into this session.

- `theme: WTheme` *(read/write)*
  The active theme (shared_ptr<WTheme>). Set during entry-
  point setup to change the default look-and-feel:

      app.theme = wt.WBootstrap5Theme()

**Methods**

- `set_internal_path(self, path: str, emit_change: bool = False) -> None`
  Change the URL fragment (the part after `#`) without
  a full page reload. Pass `emit_change=True` to also fire
  `on_internal_path_changed` — useful when you want both
  the URL update AND the route handler to run.

- `on_internal_path_changed(self, callback: Callable) -> Connection`
  Subscribe to URL-fragment changes — browser back/forward,
  or `set_internal_path(..., emit_change=True)`.

      def route(path):
          if path == '/about': show_about()
          elif path.startswith('/user/'): show_user(path)
      app.on_internal_path_changed(route)

  Returns a Connection — call `.disconnect()` on it to stop
  receiving.

- `redirect(self, url: str) -> None`
  Tell the browser to navigate to `url`. Effective on the
  next round-trip; the current session terminates if `url`
  leaves the application.

- `quit(self) -> None`
  End the session cleanly. The page stays loaded but stops
  talking to the server; the application instance is
  destroyed shortly after.

- `trigger_update(self) -> None`
  Force a server-initiated update push to the connected
  client. Combine with `WServer.post` for cross-thread
  updates — only effective after `enable_updates(True)`.

- `require(self, url: str, symbol: str = '') -> bool`
  Load an external JavaScript library before the page is
  rendered. Subsequent `do_javascript` calls are deferred
  until the library has loaded. Pass `symbol` (e.g. 'jQuery')
  to skip the load if it's already defined on `window`.
  Returns True if the library was scheduled to load, False
  if `symbol` was already present.

- `do_javascript(self, javascript: str, after_loaded: bool = True) -> None`
  Send arbitrary JS to the client. With `after_loaded=True`
  (default), the JS runs after all `require`'d libraries
  have loaded; with `False`, inline before the DOM finishes.

- `enable_updates(self, enabled: bool = True) -> None`
  Allow server-initiated updates. Without this, mutations
  from background threads (WTimer, WServer.post) only reach
  the browser on the next client-initiated round-trip; with
  it, `trigger_update` pushes them immediately. Enable once
  during entry-point setup if you do any background work.

- `use_style_sheet(self, link: WLink, media: str = 'all') -> None`
  Add an external stylesheet. `link` is a WLink (URL string
  or a WResource); `media` is the CSS media query (default
  'all'). The `<link>` tag is appended to `<head>`.

- `defer_rendering(self) -> None`
  Suspend rendering of the current event response until
  `resume_rendering` is called. Use when an async operation
  (HttpClient request, WServer.post background work) must
  complete before the page can be delivered.

- `resume_rendering(self) -> None`
  Resume rendering after a prior `defer_rendering`. Call
  from the callback that signals 'we're ready'.

- `instance() -> WApplication`
  Return the WApplication for the current Wt-managed
  thread, or None if not inside a session. Useful for
  code that doesn't carry an explicit `app` reference.

### WEnvironment {#WEnvironment}

Per-session snapshot of the browser environment Wt captured at
WApplication construction time. Read inside your entry-point
factory to branch on browser type, initial URL, etc.

    def make_app(env):
        app = wt.WApplication(env)
        if not env.supports_cookies:
            app.root.add_widget(wt.WText('Cookies required.'))
            return app
        ...
        return app

Read-only after construction. Server-driven changes (the user
navigating internally) come through `WApplication.on_internal_
path_changed`, not via this object.

**Properties**

- `user_agent: str` *(read-only)*
  Raw `User-Agent` header from the initial request.

- `host_name: str` *(read-only)*
  `Host` header from the initial request (no scheme, no port).

- `url_scheme: str` *(read-only)*
  `'http'` or `'https'`, based on the initial request.

- `internal_path: str` *(read-only)*
  URL fragment / internal path the user arrived at — e.g.
  `/dashboard/42` for a deep-link. Use this to restore state
  on first paint; subsequent fragment changes arrive via
  `WApplication.on_internal_path_changed`.

- `supports_cookies: bool` *(read-only)*
  True if the browser accepted Wt's probe cookie. False means
  session state can only survive in the URL — plan accordingly.

- `server_signature: str` *(read-only)*
  The server name as reported in the Server response header.
  Cosmetic — only useful for diagnostic banners.

### WObject {#WObject}

Root of the Wt object hierarchy. Every widget, validator,
layout, and resource inherits from this. The Python-facing
surface is small — its main purpose is to provide `bind_safe`
for safely posting cross-thread callbacks that reference an
object that may be destroyed before the callback fires.

**Methods**

- `bind_safe(self, function: Callable[[], None]) -> Callable[[], None]`
  Wrap `function` so it no-ops if this WObject has been
  destroyed by the time it runs. Canonical use is bridging a
  background-thread callback back into the UI session via
  `WServer.post`:

      def refresh():
          label.text = compute()
      server.post(session_id, label.bind_safe(refresh))

  If `label` is gone (e.g. the user navigated away and the
  session was cleaned up) by the time post fires, the wrapped
  call is a no-op instead of a use-after-free.

### WWidget {#WWidget}

*Inherits:* `WObject`

Base class for everything that renders into the DOM. Defines
the universal widget surface: sizing, visibility, CSS-class
manipulation, tooltips, and animated show/hide. Concrete
widgets (WText, WPushButton, …) inherit from this via
WInteractWidget / WFormWidget / WContainerWidget.

**Properties**

- `hidden: bool` *(read/write)*
  Whether the widget is hidden via CSS `display: none`.
  Hidden widgets still exist in the DOM and keep their state.
  For animated transitions use `animate_show` / `animate_hide`.

- `style_class: str` *(read/write)*
  The widget's full `class` attribute as a single string.
  Assigning REPLACES every class — use `add_style_class` /
  `remove_style_class` to mutate one at a time.

- `id: str` *(read/write)*
  The DOM `id` attribute. Wt assigns auto-generated ids by
  default; setting one is useful for CSS / external JS that
  needs to target the element by name. Keep ids globally
  unique in the page.

- `tool_tip: str` *(read/write)*
  Hover-tooltip text (sets the DOM `title` attribute).

**Methods**

- `set_width(self, px: float) -> None`
  Set the widget's CSS width in pixels. Pass a float; Wt
  converts to a WLength internally. For non-px units, use
  the WLength constructor directly.

- `set_height(self, px: float) -> None`
  Set the widget's CSS height in pixels (companion to
  `set_width`).

- `animate_show(self, animation: WAnimation) -> None`
  Show the widget with a transition. Pass a WAnimation
  describing the effect:

      panel.animate_show(wt.WAnimation(
          wt.AnimationEffect.SlideInFromBottom, 300))

- `animate_hide(self, animation: WAnimation) -> None`
  Hide with a transition. Inverse of animate_show; pass the
  same WAnimation form.

- `add_style_class(self, class_name: str) -> None`
  Append `class_name` to the widget's `class` attribute if
  not already present.

      container.add_widget(wt.WText('Alert!')).add_style_class('warning')

- `remove_style_class(self, class_name: str) -> None`
  Remove `class_name` from the widget's `class` attribute.
  No-op if it isn't there.

### WInteractWidget {#WInteractWidget}

*Inherits:* `WWidget`

Widget surface for things the user can interact with via mouse
or keyboard. Adds the standard input signals to WWidget — every
concrete widget that isn't purely decorative inherits from this.

    container.add_widget(wt.WText('Click me')).clicked.connect(handler)

**Properties**

- `clicked: MouseEventSignal` *(read-only)*
  Fires on left-button click. Signal payload is a
  WMouseEvent (button info, coordinates, modifiers).

- `double_clicked: MouseEventSignal` *(read-only)*
  Fires on left-button double-click (in addition to
  two `clicked` events). WMouseEvent payload.

- `mouse_over: MouseEventSignal` *(read-only)*
  Fires when the cursor enters the widget's bounds.

- `mouse_out: MouseEventSignal` *(read-only)*
  Fires when the cursor leaves the widget's bounds.

- `key_pressed: KeyEventSignal` *(read-only)*
  Fires on each printable-key press while the widget
  has focus. WKeyEvent payload. Use `key_went_down`
  instead to catch non-printable keys (arrows, F-keys).

- `key_went_down: KeyEventSignal` *(read-only)*
  Fires on every key press (printable AND control).
  WKeyEvent payload — check `.key` for the symbolic
  name when handling non-printables.

- `enter_pressed: EventSignal` *(read-only)*
  Convenience signal that fires when the user presses
  Enter while the widget has focus. Typical use is
  submit-on-enter on a form input.

### WFormWidget {#WFormWidget}

*Inherits:* `WInteractWidget`

Common surface for HTML form inputs — text fields, checkboxes,
selects, etc. Adds the `enabled` flag, focus control, the
`changed` signal, and validator wiring on top of WInteractWidget.

    edit = container.add_widget(wt.WLineEdit())
    edit.set_validator(wt.WRegExpValidator(r'\d+'))
    edit.enabled = False    # render disabled
    edit.changed.connect(lambda: log(edit.text))

**Properties**

- `enabled: bool` *(read/write)*
  Whether the input accepts user interaction. Disabled inputs
  render greyed out and don't fire `changed`.

- `changed: EventSignal` *(read-only)*
  Fires when the user commits a change (blur for text
  fields, toggle for checkboxes, Enter for selects).
  Compare with WLineEdit's `text_input` which fires
  on every keystroke.

- `validator: WValidator` *(read-only)*
  The currently-attached validator (shared_ptr), or None.

- `validated: ValidationResultSignal` *(read-only)*
  Fires after the validator has run, with a WValidator
  .Result payload — inspect `.state` for Valid /
  InvalidEmpty / Invalid.

**Methods**

- `set_focus(self) -> None`
  Move keyboard focus to this widget. Effect happens on the
  next client round-trip.

- `set_validator(self, validator: WValidator) -> None`
  Attach a validator (WIntValidator, WRegExpValidator, …)
  that decides whether the current input is acceptable. The
  validator's verdict surfaces via `validated`.

### UpdateLock {#UpdateLock}

RAII lock for cross-thread access to a WApplication. Acquire
to mutate widgets from a non-Wt thread without going through
WServer.post; release happens automatically when the wrapper
is GC'd.

    with wt.update_lock(app):
        label.text = computed_value
        app.trigger_update()

`WServer.post` is the recommended path for most cross-thread
work — UpdateLock is the lower-level escape hatch. The
Pythonic context-manager wrapper is `witty_for_python.update_lock(app)`.

**Constructors**

- `__init__(self, application: WApplication) -> None`
  Acquire the application's update lock. Check `bool(lock)`
  to confirm — acquisition can fail if the application is
  being torn down.

**Dunder methods**

- `__bool__(self) -> bool`
  True if the lock was successfully acquired, False if the
  application is being torn down.

### WServer {#WServer}

Process-wide HTTP server hosting one or more Wt entry points.
Construct one, configure it via `set_server_configuration` (which
parses options out of argv — docroot, listen address, port, …),
register entry points with `add_entry_point`, then call `run` to
enter the event loop.

    def create_app(env):
        app = wt.WApplication(env)
        app.root.add_widget(wt.WText('Hello.'))
        return app

    server = wt.WServer()
    server.set_server_configuration(sys.argv)
    server.add_entry_point(wt.EntryPointType.Application, create_app)
    server.run()

`post(session_id, fn)` and `post_all(fn)` are the recommended
way to push work from a background thread into a Wt session's
event loop — Wt acquires the session's update lock around `fn`,
so widget mutations inside it are safe. Combine with
`WObject.bind_safe` to make the callback no-op if its target
widget has been destroyed in the meantime.

**Constructors**

- `__init__(self) -> None`
  Construct a server with no configuration. Call
  `set_server_configuration` and `add_entry_point` before
  `run`.

- `__init__(self, application_path: str) -> None`
  Construct a server tagged with `application_path` — used by
  Wt's logging to identify which app this server hosts.

**Methods**

- `set_server_configuration(self, argv: Sequence[str], wt_config: str = '') -> None`
  Parse Wt's standard command-line options out of `argv` (the
  same flags `wthttpd` accepts: --docroot, --http-address,
  --http-port, etc.). Pass `sys.argv` directly. `wt_config`
  optionally points at a wt_config.xml; empty for defaults.

- `add_entry_point(self, type: EntryPointType, factory: object, path: str = '/', favicon: str = '') -> None`
  Register a Python callable as the entry point at `path`.
  Each new browser session triggers `factory(env)` on a Wt
  worker thread; return the per-session WApplication.
  `favicon` optionally overrides the default /favicon.ico.

      def create_app(env):
          app = wt.WApplication(env)
          app.root.add_widget(wt.WText('Hello.'))
          return app
      server.add_entry_point(wt.EntryPointType.Application,
                             create_app)

- `add_resource(self, resource: WResource, path: str) -> None`
  Mount `resource` at the given URL path on this server. The path is process-wide (independent of any session). Returns nothing; clients fetch via `http://<server>/<path>`.

- `start(self) -> bool`
  Start listening without blocking. Returns immediately —
  use `wait_for_shutdown` or your own signal loop afterwards.
  For the simple case, prefer `run` which does both.

- `stop(self) -> None`
  Stop accepting new connections and tear down existing
  sessions cleanly. Counterpart to `start`.

- `run(self) -> None`
  Start the server and block until shutdown is requested.
  Releases the GIL while inside the event loop so Python
  factory callbacks fired on Wt worker threads can re-acquire
  it. Returns the exit code (0 on clean shutdown).

- `is_running(self) -> bool`
  True iff the server is currently accepting requests.

- `wait_for_shutdown() -> int`
  Block the calling thread until a shutdown signal arrives
  (SIGINT / SIGTERM). Pair with `start` for non-blocking
  startup, or use `run` to combine both in one call.

- `post(self, session_id: str, function: Callable[[], None], fallback: Callable[[], None] | None = None) -> None`
  Schedule `function` to run inside the given session's event
  loop, with the session's update lock held — making widget
  mutations safe. This is the recommended cross-thread path
  for pushing updates from a background worker.

      def refresh():
          label.text = compute()
          app.trigger_update()
      server.post(session_id, label.bind_safe(refresh))

  Wrap the callback with `WObject.bind_safe` so it no-ops if
  the target widget has been destroyed before the post fires.
  If the session is gone entirely, `fallback` is called (if
  given). Returns immediately; thread-safe.

- `post_all(self, function: Callable[[], None]) -> None`
  Schedule `function` to run inside every currently-active
  session, each with its own update lock held. Thread-safe.
  Useful for broadcast-style updates (e.g. 'system going down
  in 5 minutes').

### EntryPointType {#EntryPointType}

*Inherits:* `enum.Enum`

Selects the deployment mode for an entry point added via
`WServer.add_entry_point`. `Application` is the standard mode —
Wt owns the page and renders into it. `WidgetSet` embeds Wt
widgets into an existing host page that Wt does not own.
`StaticResource` serves a single resource (file/blob) without
spinning up a session.
