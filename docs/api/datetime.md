# Dates, Times & Timers

> Date/time input widgets and validators, the calendar picker, and the WTimer that fires server-side callbacks on a schedule.

**Classes in this section:**

- [`DateSignal`](#DateSignal)
- [`WDateEdit`](#WDateEdit)
- [`WTimeEdit`](#WTimeEdit)
- [`WCalendar`](#WCalendar)
- [`WDateValidator`](#WDateValidator)
- [`WTimeValidator`](#WTimeValidator)
- [`WTimer`](#WTimer)

---

### DateSignal {#DateSignal}

Signal that emits a date payload. Wt::WDate is bridged through
the datetime caster, so slots receive a Python `datetime.date`
(or `None` for an invalid date). Same connect/emit shape as the
other Signal subclasses.

**Constructors**

- `__init__(self) -> None`
  Construct a free-standing date signal. Useful for tests or
  ad-hoc signal/slot wiring outside the Wt widget tree.

**Methods**

- `connect(self, callable: Callable) -> Connection`
  Subscribe `callable(date)` to this signal. Returns a
  Connection — call `.disconnect()` on it to unsubscribe.

- `emit(self, arg: datetime.date | None, /) -> None`
  Fire the signal with the given date. Each connected slot
  runs synchronously in turn.

- `disconnect_all_slots(self) -> None`
  Disconnect every slot connected through this binding.
  Releases the Python callable references the connections hold.

### WDateEdit {#WDateEdit}

*Inherits:* `WLineEdit`

Line-edit specialised for picking a date. Reads/writes its value
as a Python `datetime.date` via the `date` property, and shows a
calendar popup for date selection. Inherits all of WLineEdit's
text-field plumbing (validators, `changed` signal, etc.).

    picker = container.add_widget(wt.WDateEdit())
    picker.date = date.today()
    picker.bottom = date(2020, 1, 1)
    picker.changed.connect(lambda: log(picker.date))

**Constructors**

- `__init__(self) -> None`
  Construct an empty date edit with no selected date.

**Properties**

- `date: datetime.date | None` *(read/write)*
  The selected date as a `datetime.date`, or `None` if the
  field is empty / unparseable.

- `bottom: datetime.date | None` *(read/write)*
  Earliest accepted date. Dates before this are rejected by
  the built-in validator and the popup grays them out.

- `top: datetime.date | None` *(read/write)*
  Latest accepted date. Companion to `bottom`.

**Methods**

- `set_format(self, format: str) -> None`
  Set the display / parse format string for the date
  (Wt-style format letters, e.g. 'yyyy-MM-dd').

- `format(self) -> str`
  The current display / parse format string.

### WTimeEdit {#WTimeEdit}

*Inherits:* `WLineEdit`

Line-edit specialised for picking a time of day. Mirror of
WDateEdit on the time side — reads/writes a Python `datetime.time`
via the `time` property and inherits the WLineEdit surface.

    picker = container.add_widget(wt.WTimeEdit())
    picker.time = time(9, 30)
    picker.changed.connect(lambda: log(picker.time))

**Constructors**

- `__init__(self) -> None`
  Construct an empty time edit with no selected time.

**Properties**

- `time: datetime.time | None` *(read/write)*
  The selected time as a `datetime.time`, or `None` if the
  field is empty / unparseable.

- `bottom: datetime.time | None` *(read/write)*
  Earliest accepted time. Values before this fail validation.

- `top: datetime.time | None` *(read/write)*
  Latest accepted time. Companion to `bottom`.

**Methods**

- `set_format(self, format: str) -> None`
  Set the display / parse format string for the time
  (e.g. 'HH:mm:ss').

### WCalendar {#WCalendar}

*Inherits:* `WWidget`

Standalone month calendar — a navigable grid that lets the user
select dates and walk through months/years. Use as a top-level
calendar widget; for date-picker behaviour embedded in a text
field, prefer WDateEdit.

    cal = container.add_widget(wt.WCalendar())
    cal.bottom = date(2020, 1, 1)
    cal.activated.connect(lambda d: log('picked', d))

`selection_changed` fires on any change to the selection set;
`activated` fires when the user double-clicks (or otherwise
commits) a single day; `clicked` fires on every single-day click.

**Constructors**

- `__init__(self) -> None`
  Construct an empty calendar showing the current month.

**Properties**

- `current_month: int` *(read-only)*
  The month (1–12) currently displayed.

- `current_year: int` *(read-only)*
  The year currently displayed.

- `bottom: datetime.date | None` *(read/write)*
  Earliest selectable date. Dates before this are rendered
  as un-pickable.

- `top: datetime.date | None` *(read/write)*
  Latest selectable date. Companion to `bottom`.

- `selection_changed: Signal` *(read-only)*
  Fires whenever the set of selected dates changes
  (no-arg signal). Read `selection()` for the new state.

- `activated: DateSignal` *(read-only)*
  DateSignal — fires when the user commits a date
  (typically a double-click). Payload is the activated
  `datetime.date`.

- `clicked: DateSignal` *(read-only)*
  DateSignal — fires on each single-day click,
  regardless of whether the selection changed.

**Methods**

- `select(self, date: datetime.date | None) -> None`
  Add `date` to the selection. In Single selection mode this
  replaces the previous selection; in Extended mode it adds
  to the set.

- `set_selection_mode(self, mode: SelectionMode) -> None`
  Set the selection model (SelectionMode.Single, .Extended,
  or .None_).

- `browse_to_previous_month(self) -> None`
  Scroll the visible month back by one.

- `browse_to_next_month(self) -> None`
  Scroll the visible month forward by one.

- `browse_to_previous_year(self) -> None`
  Scroll the visible year back by one.

- `browse_to_next_year(self) -> None`
  Scroll the visible year forward by one.

### WDateValidator {#WDateValidator}

*Inherits:* `WValidator`

WValidator that accepts dates within an optional [bottom, top]
range, parsed against a configurable format string. Attach to a
WLineEdit (or any WFormWidget) when you want server-side date
validation independent of WDateEdit.

    v = wt.WDateValidator(date(2020, 1, 1), date(2030, 12, 31))
    edit.set_validator(v)
    edit.validated.connect(lambda r: log(r.state))

**Constructors**

- `__init__(self) -> None`
  Construct a validator with no range constraints and the
  default date format.

- `__init__(self, bottom: datetime.date | None, top: datetime.date | None) -> None`
  Construct a validator that requires the parsed date to lie
  between `bottom` and `top` (inclusive).

- `__init__(self, format: str) -> None`
  Construct a validator using `format` as the parse format
  (Wt-style letters, e.g. 'yyyy-MM-dd').

**Properties**

- `bottom: datetime.date | None` *(read/write)*
  Earliest accepted date (inclusive).

- `top: datetime.date | None` *(read/write)*
  Latest accepted date (inclusive).

**Methods**

- `set_format(self, format: str) -> None`
  Set the format string used to parse / display dates.

- `format(self) -> str`
  The current parse format string.

### WTimeValidator {#WTimeValidator}

*Inherits:* `WRegExpValidator`

WValidator that accepts time-of-day values within an optional
[bottom, top] range, parsed against a configurable format string.
Inherits the regex-validator surface internally but the public
knobs you usually care about are `format`, `bottom`, and `top`.

    v = wt.WTimeValidator('HH:mm', time(9, 0), time(17, 0))
    edit.set_validator(v)

**Constructors**

- `__init__(self) -> None`
  Construct a validator with no range constraints and the
  default time format.

- `__init__(self, format: str) -> None`
  Construct a validator using `format` as the parse format
  (e.g. 'HH:mm:ss').

- `__init__(self, format: str, bottom: datetime.time | None, top: datetime.time | None) -> None`
  Construct a validator using `format` and a [bottom, top]
  time range (both inclusive).

**Properties**

- `bottom: datetime.time | None` *(read/write)*
  Earliest accepted time (inclusive).

- `top: datetime.time | None` *(read/write)*
  Latest accepted time (inclusive).

**Methods**

- `set_format(self, format: str) -> None`
  Set the format string used to parse / display times.

- `format(self) -> str`
  The current parse format string.

### WTimer {#WTimer}

*Inherits:* `WObject`

Session-bound timer that fires its `timeout` signal at a fixed
interval. The signal is delivered on the Wt session thread under
the application's update lock, so slots can touch widgets directly
without going through `WServer.post` or an `UpdateLock`.

    from datetime import timedelta
    clock = wt.WTimer()
    clock.interval = timedelta(seconds=1)
    def tick():
        label.text = time.strftime('%H:%M:%S')
    clock.timeout.connect(tick)
    clock.start()

Set `single_shot = True` before `start()` to fire once and stop;
otherwise the timer repeats until `stop()` is called. Reads of
`interval` come back as a `datetime.timedelta`.

**Constructors**

- `__init__(self) -> None`
  Construct an inactive timer with a zero interval. Set
  `interval` (and optionally `single_shot`), connect `timeout`,
  then call `start()`.

**Properties**

- `interval: datetime.timedelta` *(read/write)*
  Time between successive timer firings, as a datetime.timedelta. Re-assigning while the timer is active reschedules it.

- `is_active: bool` *(read-only)*
  True between start() and stop() (or first timeout when single_shot is True).

- `single_shot: bool` *(read/write)*
  When True, the timer fires exactly once and then deactivates.

- `timeout: MouseEventSignal` *(read-only)*
  EventSignal[WMouseEvent] — fires every interval. The event payload is an implementation artefact; slots typically ignore it.

**Methods**

- `start(self) -> None`
  Begin firing the timeout signal at every interval. No-op if the timer is already active.

- `stop(self) -> None`
  Stop a running timer. Safe to call from within a timeout slot.
