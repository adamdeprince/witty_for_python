# Form Validation

> Validators attached to WFormWidget inputs. Each rejects with a ValidationResult; the form widget exposes a `validated` signal.

**Classes in this section:**

- [`ValidationState`](#ValidationState)
- [`ValidationResult`](#ValidationResult)
- [`ValidationResultSignal`](#ValidationResultSignal)
- [`WValidator`](#WValidator)
- [`WIntValidator`](#WIntValidator)
- [`WDoubleValidator`](#WDoubleValidator)
- [`WLengthValidator`](#WLengthValidator)
- [`WRegExpValidator`](#WRegExpValidator)
- [`WEmailValidator`](#WEmailValidator)
- [`WStackedValidator`](#WStackedValidator)

---

### ValidationState {#ValidationState}

*Inherits:* `enum.Enum`

Outcome of a validator's check on the current input.

    Valid         — input acceptable, OK to submit.
    InvalidEmpty  — input is empty, validator marks it mandatory.
    Invalid       — input present but doesn't satisfy the rule.

InvalidEmpty is split out from Invalid because the typical UX
shows a different message for 'required field missing' than for
'wrong format'.

### ValidationResult {#ValidationResult}

Verdict from `WValidator.validate(input)` — a (state, message)
pair. The message is the localized text shown to the user when
the input is rejected.

    r = validator.validate('not-an-int')
    if r.state != wt.ValidationState.Valid:
        label.text = r.message

**Constructors**

- `__init__(self) -> None`
  Construct a result with state=Valid and no message.

- `__init__(self, state: ValidationState) -> None`
  Construct a result with the given state and no message.

- `__init__(self, state: ValidationState, message: str) -> None`
  Construct a result with the given state and an explanatory
  message (typically a localized 'too short' / 'invalid'
  string to show next to the input).

**Properties**

- `state: ValidationState` *(read-only)*
  The ValidationState verdict.

- `message: str` *(read-only)*
  The localized human-readable message; empty when state is Valid.

**Dunder methods**

- `__repr__(self) -> str`

### ValidationResultSignal {#ValidationResultSignal}

Signal carrying a ValidationResult payload. Surfaced via
`WFormWidget.validated` — fires after the form widget's
validator has run.

    edit.validated.connect(lambda r: label.text = r.message)

**Methods**

- `connect(self, callable: Callable) -> Connection`
  Subscribe `callable(result)` to validation events. Returns
  a Connection; call its `.disconnect()` to stop receiving.

- `disconnect_all_slots(self) -> None`
  Drop every connection opened through `connect`. Mostly an
  internal shutdown hook — most code doesn't need this.

### WValidator {#WValidator}

Base class for input validators. Concrete subclasses (WIntValidator,
WDoubleValidator, WRegExpValidator, …) inherit the `mandatory` flag
and the empty-input message. Validators are normally attached to a
WFormWidget via `form_widget.set_validator(v)`; the form widget then
fires `validated` after each input change.

    edit = container.add_widget(wt.WLineEdit())
    v = wt.WIntValidator(0, 100)
    v.mandatory = True
    edit.set_validator(v)
    edit.validated.connect(lambda r: print(r))

**Properties**

- `mandatory: bool` *(read/write)*
  Whether empty input counts as Invalid (specifically as
  InvalidEmpty). False (the default) makes empty input Valid.

- `invalid_blank_text: str` *(read/write)*
  The message shown when `mandatory` is True and the input
  is empty. Replaces the default 'this field is required'.

**Methods**

- `validate(self, input: str) -> ValidationResult`
  Run the validation rule against `input` and return a
  ValidationResult. Pure function — does NOT mutate either
  the validator or the form widget; safe to call from anywhere.

### WIntValidator {#WIntValidator}

*Inherits:* `WValidator`

Accepts an integer in an optional [bottom, top] range.

    edit.set_validator(wt.WIntValidator(0, 100))

**Constructors**

- `__init__(self) -> None`
  Construct a validator with no range limits.

- `__init__(self, minimum: int, maximum: int) -> None`
  Construct a validator that accepts integers in [minimum,
  maximum] inclusive.

**Properties**

- `bottom: int` *(read/write)*
  Lowest accepted value (inclusive).

- `top: int` *(read/write)*
  Highest accepted value (inclusive).

- `invalid_not_a_number_text: str` *(read/write)*
  Message shown when the input isn't a valid integer at all.

- `invalid_too_small_text: str` *(read/write)*
  Message shown when the integer is below `bottom`.

- `invalid_too_large_text: str` *(read/write)*
  Message shown when the integer exceeds `top`.

- `ignore_trailing_spaces: bool` *(read/write)*
  Whether trailing whitespace in the input is stripped before
  parsing. Useful when users paste numbers with stray spaces.

**Methods**

- `set_range(self, bottom: int, top: int) -> None`
  Set both bounds atomically.

### WDoubleValidator {#WDoubleValidator}

*Inherits:* `WValidator`

Accepts a floating-point number in an optional [bottom, top] range.

    edit.set_validator(wt.WDoubleValidator(0.0, 1.0))

**Constructors**

- `__init__(self) -> None`
  Construct a validator with no range limits.

- `__init__(self, minimum: float, maximum: float) -> None`
  Construct a validator that accepts floats in [minimum,
  maximum] inclusive.

**Properties**

- `bottom: float` *(read/write)*
  Lowest accepted value (inclusive).

- `top: float` *(read/write)*
  Highest accepted value (inclusive).

- `invalid_not_a_number_text: str` *(read/write)*
  Message shown when the input isn't a valid number.

- `invalid_too_small_text: str` *(read/write)*
  Message shown when the value is below `bottom`.

- `invalid_too_large_text: str` *(read/write)*
  Message shown when the value exceeds `top`.

**Methods**

- `set_range(self, bottom: float, top: float) -> None`
  Set both bounds atomically.

### WLengthValidator {#WLengthValidator}

*Inherits:* `WValidator`

Accepts text whose length (in characters) falls within an
optional [minimum_length, maximum_length] range. Useful for
things like 'username 3–20 chars'.

    edit.set_validator(wt.WLengthValidator(3, 20))

**Constructors**

- `__init__(self) -> None`
  Construct a validator with no length limits.

- `__init__(self, minimum_length: int, maximum_length: int) -> None`
  Construct a validator with the given length bounds (inclusive).

**Properties**

- `minimum_length: int` *(read/write)*
  Shortest accepted length (inclusive).

- `maximum_length: int` *(read/write)*
  Longest accepted length (inclusive).

- `invalid_too_short_text: str` *(read/write)*
  Message shown when the input is shorter than `minimum_length`.

- `invalid_too_long_text: str` *(read/write)*
  Message shown when the input exceeds `maximum_length`.

### WRegExpValidator {#WRegExpValidator}

*Inherits:* `WValidator`

Accepts text matching a regular-expression pattern. Useful for
phone numbers, postal codes, custom formats.

    edit.set_validator(wt.WRegExpValidator(r'\d{5}'))     # US ZIP

**Constructors**

- `__init__(self) -> None`
  Construct a validator with no pattern (matches anything).

- `__init__(self, pattern: str) -> None`
  Construct a validator that requires the input to match
  `pattern` end-to-end.

**Properties**

- `pattern: str` *(read/write)*
  The regex pattern. Wt uses its own regex syntax (close to
  PCRE); test on the form to confirm matching behavior.

- `invalid_no_match_text: str` *(read/write)*
  Message shown when the input doesn't match `pattern`.

### WEmailValidator {#WEmailValidator}

*Inherits:* `WValidator`

Accepts a syntactically-valid email address (or a comma-separated
list when `multiple` is True). Doesn't verify the address actually
exists — that needs an out-of-band confirm step.

    edit.set_validator(wt.WEmailValidator())

**Constructors**

- `__init__(self) -> None`
  Construct an email validator with the default RFC-5322-ish
  pattern accepting a single address.

**Properties**

- `multiple: bool` *(read/write)*
  Accept a comma-separated list of addresses instead of just one.

- `pattern: str` *(read/write)*
  Override the built-in regex with a custom pattern.

- `invalid_not_an_email_address_text: str` *(read/write)*
  Message shown when the input doesn't look like an email address.

### WStackedValidator {#WStackedValidator}

*Inherits:* `WValidator`

Composite validator that runs a sequence of sub-validators in
order; the first one that rejects wins. Useful for combining
concerns (length AND pattern, range AND custom rule).

    stacked = wt.WStackedValidator()
    stacked.add_validator(wt.WLengthValidator(8, 64))
    stacked.add_validator(wt.WRegExpValidator(r'.*[A-Z].*'))
    edit.set_validator(stacked)

**Constructors**

- `__init__(self) -> None`
  Construct an empty stacked validator.

**Properties**

- `size: int` *(read-only)*
  Number of sub-validators currently in the chain.

**Methods**

- `add_validator(self, validator: WValidator) -> None`
  Append `validator` to the end of the chain.

- `insert_validator(self, index: int, validator: WValidator) -> None`
  Insert `validator` at `index` so it runs before later ones.

- `remove_validator(self, validator: WValidator) -> None`
  Remove `validator` from the chain. No-op if it isn't there.

- `clear(self) -> None`
  Drop every sub-validator.
