# JSON (submodule)

> Small JSON value model exposed by the `witty_for_python.Json` subsystem — used by a handful of bindings (e.g. WLeafletMap options) that take structured JSON config.

**Classes in this section:**

- [`Type`](#Json.Type)
- [`Object`](#Json.Object)
- [`Array`](#Json.Array)
- [`Value`](#Json.Value)

---

### Type {#Json.Type}

*Inherits:* `enum.Enum`

### Object {#Json.Object}

Wt's JSON object — a string-keyed map of Json.Value. Bridges to
Python via `Object(dict)` for construction and `.to_dict()` for
reading. Values nest recursively (dicts and lists in, dicts and
lists out).

    payload = wt.Json.Object({'name': 'Ada', 'tags': ['admin']})
    payload.contains('name')              # True
    payload.to_dict()                     # round-trips

**Constructors**

- `__init__(self) -> None`
  Default-construct an empty JSON object.

- `__init__(self, values: dict) -> None`
  Construct from a Python dict. Values can be None / bool / int / float / str / nested dict / nested list.

**Properties**

- `empty: bool` *(read-only)*
  True when the object has no keys.

**Methods**

- `contains(self, name: str) -> bool`
  True if `name` is a key in the object.

- `to_dict(self) -> dict`
  Recursive Python-native view of this Object.

**Dunder methods**

- `__len__(self) -> int`
  Number of keys in the object.

### Array {#Json.Array}

Wt's JSON array — an ordered list of Json.Value. Mirror of
Json.Object on the sequence side: construct from a Python list,
read back with `.to_list()`.

    tags = wt.Json.Array(['admin', 'editor', 'viewer'])
    len(tags)                              # 3
    tags.to_list()                         # ['admin', ...]

**Constructors**

- `__init__(self) -> None`
  Default-construct an empty JSON array.

- `__init__(self, items: list) -> None`
  Construct from a Python list. Items can be any JSON-compatible Python value (same set as Object accepts).

**Methods**

- `to_list(self) -> list`
  Recursive Python-native view of this Array.

**Dunder methods**

- `__len__(self) -> int`
  Number of elements in the array.

### Value {#Json.Value}

Polymorphic JSON value. Holds one of: null, bool, number,
string, object, or array (see Json.Type). Convert from any
JSON-compatible Python value at construction; read back with
`.to_python()`.

    v = wt.Json.Value({'n': 1, 'xs': [1, 2, 3]})
    v.type                                 # Type.Object
    v.to_python()                          # {'n': 1.0, ...}

Numbers always come back as Python floats — see the parent
submodule docstring for the lossy int/float caveat.

**Constructors**

- `__init__(self) -> None`
  Default-construct a Null value.

- `__init__(self, value: object | None) -> None`
  Construct from a Python value. Pass any JSON-compatible Python value (None / bool / int / float / str / dict / list).

**Properties**

- `type: Type` *(read-only)*
  The Json.Type tag of the contained value.

- `is_null: bool` *(read-only)*
  True when this value is JSON null. Equivalent to
  `type == Type.Null`.

**Methods**

- `to_python(self) -> object`
  Recursive Python-native view of this Value.
