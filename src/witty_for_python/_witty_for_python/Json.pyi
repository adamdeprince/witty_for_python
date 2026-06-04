"""
Wt's JSON value model — Object, Array, Value, plus parse() and serialize() helpers. Pythonic shorthand: Object accepts a dict at construction, Array accepts a list; both expose to_dict()/to_list() for the reverse.

Number-type caveat: Wt::Json::Value collapses int and float storage to a single Type.Number tag. On the to_python side every JSON number comes back as Python float — there is no way to recover whether the source was written as `1` or `1.0`. If you need int/float discrimination preserved, use Python's stdlib `json` (or ujson / simdjson) and only convert to wt.Json at the boundary where you hand data into a Wt API.
"""

import enum
from typing import overload


class Type(enum.Enum):
    Null = 0

    String = 1

    Bool = 2

    Number = 3

    Object = 4

    Array = 5

class Object:
    """
    Wt's JSON object — a string-keyed map of Json.Value. Bridges to
    Python via `Object(dict)` for construction and `.to_dict()` for
    reading. Values nest recursively (dicts and lists in, dicts and
    lists out).

        payload = wt.Json.Object({'name': 'Ada', 'tags': ['admin']})
        payload.contains('name')              # True
        payload.to_dict()                     # round-trips
    """

    @overload
    def __init__(self) -> None:
        """Default-construct an empty JSON object."""

    @overload
    def __init__(self, values: dict) -> None:
        """
        Construct from a Python dict. Values can be None / bool / int / float / str / nested dict / nested list.
        """

    @property
    def empty(self) -> bool:
        """True when the object has no keys."""

    def __len__(self) -> int:
        """Number of keys in the object."""

    def contains(self, name: str) -> bool:
        """True if `name` is a key in the object."""

    def to_dict(self) -> dict:
        """Recursive Python-native view of this Object."""

class Array:
    """
    Wt's JSON array — an ordered list of Json.Value. Mirror of
    Json.Object on the sequence side: construct from a Python list,
    read back with `.to_list()`.

        tags = wt.Json.Array(['admin', 'editor', 'viewer'])
        len(tags)                              # 3
        tags.to_list()                         # ['admin', ...]
    """

    @overload
    def __init__(self) -> None:
        """Default-construct an empty JSON array."""

    @overload
    def __init__(self, items: list) -> None:
        """
        Construct from a Python list. Items can be any JSON-compatible Python value (same set as Object accepts).
        """

    def __len__(self) -> int:
        """Number of elements in the array."""

    def to_list(self) -> list:
        """Recursive Python-native view of this Array."""

class Value:
    """
    Polymorphic JSON value. Holds one of: null, bool, number,
    string, object, or array (see Json.Type). Convert from any
    JSON-compatible Python value at construction; read back with
    `.to_python()`.

        v = wt.Json.Value({'n': 1, 'xs': [1, 2, 3]})
        v.type                                 # Type.Object
        v.to_python()                          # {'n': 1.0, ...}

    Numbers always come back as Python floats — see the parent
    submodule docstring for the lossy int/float caveat.
    """

    @overload
    def __init__(self) -> None:
        """Default-construct a Null value."""

    @overload
    def __init__(self, value: object | None) -> None:
        """
        Construct from a Python value. Pass any JSON-compatible Python value (None / bool / int / float / str / dict / list).
        """

    @property
    def type(self) -> Type:
        """The Json.Type tag of the contained value."""

    @property
    def is_null(self) -> bool:
        """
        True when this value is JSON null. Equivalent to
        `type == Type.Null`.
        """

    def to_python(self) -> object:
        """Recursive Python-native view of this Value."""

def parse(input: str) -> Object:
    """
    Parse a JSON document into a Json.Object. Use `.to_dict()` on the result for a Python-native view.
    """

def parse_value(input: str) -> Value:
    """
    Parse a JSON document into a Json.Value (handles top-level primitives / arrays / objects equally).
    """

def serialize(obj: Object, indentation: int = 1) -> str:
    """Serialize a Json.Object to a JSON string."""

def serialize_array(arr: Array, indentation: int = 1) -> str:
    """
    Serialize a Json.Array to a JSON string. Counterpart of
    `serialize` for top-level array documents.
    """

def from_python(value: object) -> Value:
    """Convert a Python value to a Json.Value. Recursive for dicts and lists."""

def to_python(value: Value) -> object:
    """Convert a Json.Value to a Python native value. Inverse of from_python."""
