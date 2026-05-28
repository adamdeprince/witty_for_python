"""Wt::Json suite — Object / Array / Value / parse / serialize.

These are pure value types; full round-trip exercise without any session.
The construction-from-dict / construction-from-list flows are the
ergonomic story: Python users hand a dict to Json.Object and a list to
Json.Array; nested structures recurse automatically.
"""

from __future__ import annotations

import math
import pytest
import witty_for_python as wt


# ---- Type enum -------------------------------------------------------------

def test_type_enum_members() -> None:
    for name in ("Null", "String", "Bool", "Number", "Object", "Array"):
        assert hasattr(wt.Json.Type, name)


# ---- Json.Object -----------------------------------------------------------

def test_object_default_construct_empty() -> None:
    o = wt.Json.Object()
    assert len(o) == 0
    assert o.empty is True


def test_object_construct_from_dict() -> None:
    o = wt.Json.Object({"name": "Alice", "age": 30, "active": True})
    assert len(o) == 3
    assert o.contains("name")
    assert not o.contains("missing")


def test_object_round_trip_preserves_primitives() -> None:
    """str, bool, None survive intact. Numbers come back as float
    regardless of input — Wt::Json::Value can't recover int/float
    distinction (it's a JSON-language limit on Wt's side). See
    module docstring."""
    o = wt.Json.Object({"s": "hi", "i": 42, "f": 3.14,
                        "b": True, "n": None})
    back = o.to_dict()
    assert back["s"] == "hi"
    assert back["i"] == 42.0           # came back as float
    assert isinstance(back["i"], float)
    assert back["f"] == 3.14
    assert back["b"] is True
    assert back["n"] is None


def test_object_round_trip_preserves_nesting() -> None:
    src = {
        "level1": {
            "level2": {
                "items": [1, 2, 3, {"deeper": "value"}],
            },
        },
    }
    o = wt.Json.Object(src)
    assert o.to_dict() == src


def test_object_numbers_always_return_float() -> None:
    """All JSON numbers come back as Python float — the int/float
    distinction is lost inside Wt::Json::Value. Test documents the
    behaviour so the contract is explicit."""
    o = wt.Json.Object({"int_val": 42, "float_val": 0.5,
                        "exact_float": 1.0})
    back = o.to_dict()
    for k in ("int_val", "float_val", "exact_float"):
        assert isinstance(back[k], float), f"{k} should be float"
    assert back["int_val"] == 42.0
    assert back["float_val"] == 0.5
    assert back["exact_float"] == 1.0


# ---- Json.Array ------------------------------------------------------------

def test_array_default_empty() -> None:
    a = wt.Json.Array()
    assert len(a) == 0


def test_array_from_list_round_trip() -> None:
    """Numbers come back as floats — same Wt::Json::Value limitation as
    for Object."""
    a = wt.Json.Array([1, "two", 3.14, True, None, [4, 5]])
    back = a.to_list()
    assert back == [1.0, "two", 3.14, True, None, [4.0, 5.0]]


def test_array_of_dicts() -> None:
    a = wt.Json.Array([{"x": 1}, {"x": 2}])
    assert a.to_list() == [{"x": 1.0}, {"x": 2.0}]


# ---- Json.Value ------------------------------------------------------------

def test_value_default_is_null() -> None:
    v = wt.Json.Value()
    assert v.type == wt.Json.Type.Null
    assert v.is_null is True


def test_value_from_python_primitives() -> None:
    assert wt.Json.Value("hello").type == wt.Json.Type.String
    assert wt.Json.Value(42).type == wt.Json.Type.Number
    assert wt.Json.Value(0.5).type == wt.Json.Type.Number
    assert wt.Json.Value(True).type == wt.Json.Type.Bool
    assert wt.Json.Value(None).type == wt.Json.Type.Null


def test_value_from_python_dict_becomes_object() -> None:
    v = wt.Json.Value({"x": 1, "y": 2})
    assert v.type == wt.Json.Type.Object


def test_value_from_python_list_becomes_array() -> None:
    v = wt.Json.Value([1, 2, 3])
    assert v.type == wt.Json.Type.Array


def test_value_to_python_round_trip() -> None:
    """Round-trip preserves str / bool / None / nested structure. Numbers
    always come back as float (see module docstring)."""
    for src in ("text", True, False, None):
        assert wt.Json.Value(src).to_python() == src
    # Numbers: int input → float output, float input → float output.
    assert wt.Json.Value(42).to_python() == 42.0
    assert wt.Json.Value(0.5).to_python() == 0.5
    # Containers recurse — numbers inside also become float.
    assert wt.Json.Value({"x": 1}).to_python() == {"x": 1.0}
    assert wt.Json.Value([1, 2, 3]).to_python() == [1.0, 2.0, 3.0]


# ---- parse + serialize -----------------------------------------------------

def test_parse_simple_object() -> None:
    o = wt.Json.parse('{"name": "witty", "count": 42}')
    d = o.to_dict()
    assert d["name"] == "witty"
    assert d["count"] == 42.0   # numbers always come back as float


def test_parse_value_handles_top_level_array() -> None:
    """parse_value handles non-object roots; parse only handles objects."""
    v = wt.Json.parse_value("[1, 2, 3]")
    assert v.type == wt.Json.Type.Array
    assert v.to_python() == [1.0, 2.0, 3.0]


def test_serialize_round_trip() -> None:
    """Serialize → parse → to_dict converges. Numbers come back as float
    (see module docstring), so we compare against the float-shaped form."""
    src = {"a": 1, "b": [2, 3], "c": {"d": "x"}}
    o = wt.Json.Object(src)
    text = wt.Json.serialize(o, 0)   # 0 = no pretty-printing
    reparsed = wt.Json.parse(text).to_dict()
    assert reparsed == {"a": 1.0, "b": [2.0, 3.0], "c": {"d": "x"}}


def test_serialize_array_helper() -> None:
    a = wt.Json.Array([1, 2, 3])
    text = wt.Json.serialize_array(a, 0)
    assert "1" in text and "2" in text and "3" in text


# ---- module-level helpers --------------------------------------------------

def test_from_python_and_to_python() -> None:
    src = {"key": "value", "list": [1, 2]}
    v = wt.Json.from_python(src)
    assert v.type == wt.Json.Type.Object
    assert wt.Json.to_python(v) == src


def test_from_python_rejects_unsupported_type() -> None:
    """A Python object that isn't JSON-compatible (e.g. a complex number)
    raises rather than silently producing garbage."""
    with pytest.raises(RuntimeError):
        wt.Json.from_python(complex(1, 2))


# ---- WLeafletMap class binding surface ------------------------------------

def test_wleafletmap_class_present() -> None:
    assert wt.WLeafletMap is not None


def test_wleafletmap_inherits_wwidget() -> None:
    assert issubclass(wt.WLeafletMap, wt.WWidget)


@pytest.mark.parametrize("attr", [
    "set_options", "add_tile_layer", "pan_to", "zoom_level",
    "position", "zoom_level_changed", "Coordinate",
])
def test_wleafletmap_attribute_present(attr: str) -> None:
    assert hasattr(wt.WLeafletMap, attr), f"WLeafletMap missing: {attr}"


def test_leaflet_coordinate_round_trip() -> None:
    c = wt.LeafletMapCoordinate(40.7128, -74.0060)
    assert c.latitude == pytest.approx(40.7128)
    assert c.longitude == pytest.approx(-74.0060)


# ---- JIntSignal class surface ---------------------------------------------

def test_jint_signal_exposed() -> None:
    assert hasattr(wt, "JIntSignal")
    assert hasattr(wt.JIntSignal, "connect")
    assert hasattr(wt.JIntSignal, "disconnect_all_slots")
