#include "common.hpp"

#include <Wt/Json/Array.h>
#include <Wt/Json/Object.h>
#include <Wt/Json/Parser.h>
#include <Wt/Json/Serializer.h>
#include <Wt/Json/Value.h>

#include <stdexcept>
#include <string>
#include <utility>

namespace witty_for_python {

namespace {

// Forward declaration — the converters are mutually recursive.
Wt::Json::Value py_to_json_value(nb::handle val);
nb::object json_value_to_py(const Wt::Json::Value& val);

// Convert a Python value (None / bool / int / float / str / dict / list /
// tuple) into a Wt::Json::Value. Recursive for dicts and lists.
Wt::Json::Value py_to_json_value(nb::handle val) {
    if (val.is_none()) {
        return Wt::Json::Value();   // Null
    }
    PyObject* p = val.ptr();

    // Bool must come before int — PyBool is a PyLong subclass.
    if (PyBool_Check(p)) {
        return Wt::Json::Value(nb::cast<bool>(val));
    }
    if (PyLong_Check(p)) {
        // Wt's Value supports int / long / long long. Pick long long
        // to cover the full Python int range up to 2^63.
        return Wt::Json::Value(nb::cast<long long>(val));
    }
    if (PyFloat_Check(p)) {
        return Wt::Json::Value(nb::cast<double>(val));
    }
    if (PyUnicode_Check(p)) {
        return Wt::Json::Value(Wt::WString::fromUTF8(nb::cast<std::string>(val)));
    }
    if (PyDict_Check(p)) {
        Wt::Json::Object obj;
        for (auto item : nb::borrow<nb::dict>(val)) {
            std::string key = nb::cast<std::string>(item.first);
            obj[key] = py_to_json_value(item.second);
        }
        return Wt::Json::Value(std::move(obj));
    }
    if (PyList_Check(p) || PyTuple_Check(p)) {
        Wt::Json::Array arr;
        for (nb::handle item : val) {
            arr.push_back(py_to_json_value(item));
        }
        return Wt::Json::Value(std::move(arr));
    }
    // We're built against the limited ABI which hides PyTypeObject's
    // members; fall back to the type-name attribute fetched via the
    // CPython C API.
    throw std::runtime_error(
        "Wt::Json::Value: don't know how to convert Python value to JSON "
        "— supported types are None, bool, int, float, str, dict, list, "
        "tuple.");
}

// Reverse direction — produces a native Python value.
nb::object json_value_to_py(const Wt::Json::Value& val) {
    using Wt::Json::Type;
    switch (val.type()) {
    case Type::Null:
        return nb::none();
    case Type::Bool: {
        bool b = static_cast<bool>(val);
        return nb::cast(b);
    }
    case Type::String:
        return nb::cast(std::string(val));
    case Type::Number: {
        // ALWAYS return Python float for JSON numbers. Wt::Json::Value
        // collapses int / float storage to a single Type::Number tag —
        // we can't recover the original syntactic form, and a heuristic
        // ("looks integer-valued => return int") silently mangles
        // float-shaped data on round-trip (e.g. {"price": 1.0} would
        // come back as {"price": 1}).
        //
        // Real JSON tools (Python's stdlib `json`, ujson, simdjson)
        // discriminate int from float by the presence of a decimal point
        // in the source text — that information is lost the moment a
        // value lands inside Wt::Json::Value. If you need int/float
        // discrimination, use one of those libraries for parse/serialize
        // and only convert to wt.Json when handing data into a Wt API.
        double d = static_cast<double>(val);
        return nb::cast(d);
    }
    case Type::Object: {
        const Wt::Json::Object& obj = val;
        nb::dict d;
        for (const auto& [k, v] : obj) {
            d[nb::cast(k)] = json_value_to_py(v);
        }
        return d;
    }
    case Type::Array: {
        const Wt::Json::Array& arr = val;
        nb::list l;
        for (const auto& v : arr) {
            l.append(json_value_to_py(v));
        }
        return l;
    }
    }
    return nb::none();   // unreachable but quiets the compiler
}

}  // namespace

void register_json(nb::module_& m) {
    // Mirror Wt's Wt::Json namespace as a Python submodule.
    nb::module_ json = m.def_submodule("Json",
        "Wt's JSON value model — Object, Array, Value, plus parse() and "
        "serialize() helpers. Pythonic shorthand: Object accepts a dict at "
        "construction, Array accepts a list; both expose to_dict()/to_list() "
        "for the reverse.\n\n"
        "Number-type caveat: Wt::Json::Value collapses int and float "
        "storage to a single Type.Number tag. On the to_python side every "
        "JSON number comes back as Python float — there is no way to "
        "recover whether the source was written as `1` or `1.0`. If you "
        "need int/float discrimination preserved, use Python's stdlib "
        "`json` (or ujson / simdjson) and only convert to wt.Json at the "
        "boundary where you hand data into a Wt API.");

    // ---- Type enum ----

    nb::enum_<Wt::Json::Type>(json, "Type")
        .value("Null",   Wt::Json::Type::Null)
        .value("String", Wt::Json::Type::String)
        .value("Bool",   Wt::Json::Type::Bool)
        .value("Number", Wt::Json::Type::Number)
        .value("Object", Wt::Json::Type::Object)
        .value("Array",  Wt::Json::Type::Array);

    // ---- Json::Object ----
    //
    // Inherits std::map<std::string, Value> in C++. We expose it as a
    // distinct Python class (rather than the map base) since users pass
    // it to APIs as a typed parameter (e.g. WLeafletMap.add_tile_layer).
    // The convenient construction path: pass a Python dict; nested
    // dicts / lists / primitives are recursed automatically.

    nb::class_<Wt::Json::Object>(json, "Object",
        "Wt's JSON object — a string-keyed map of Json.Value. Bridges to\n"
        "Python via `Object(dict)` for construction and `.to_dict()` for\n"
        "reading. Values nest recursively (dicts and lists in, dicts and\n"
        "lists out).\n"
        "\n"
        "    payload = wt.Json.Object({'name': 'Ada', 'tags': ['admin']})\n"
        "    payload.contains('name')              # True\n"
        "    payload.to_dict()                     # round-trips")
        .def("__init__", [](Wt::Json::Object* self) {
            new (self) Wt::Json::Object();
        },
            "Default-construct an empty JSON object.")
        .def("__init__",
            [](Wt::Json::Object* self, nb::dict d) {
                new (self) Wt::Json::Object();
                for (auto item : d) {
                    std::string key = nb::cast<std::string>(item.first);
                    (*self)[key] = py_to_json_value(item.second);
                }
            },
            "values"_a,
            "Construct from a Python dict. Values can be None / bool / int "
            "/ float / str / nested dict / nested list.")
        .def_prop_ro("empty",
            [](const Wt::Json::Object& o) { return o.empty(); },
            "True when the object has no keys.")
        .def("__len__",
            [](const Wt::Json::Object& o) { return o.size(); },
            "Number of keys in the object.")
        .def("contains",
            [](const Wt::Json::Object& o, const std::string& name) {
                return o.contains(name);
            },
            "name"_a,
            "True if `name` is a key in the object.")
        .def("to_dict",
            // Round-trip back to a Python dict.
            [](const Wt::Json::Object& o) {
                nb::dict d;
                for (const auto& [k, v] : o) {
                    d[nb::cast(k)] = json_value_to_py(v);
                }
                return d;
            },
            "Recursive Python-native view of this Object.");

    // ---- Json::Array ----

    nb::class_<Wt::Json::Array>(json, "Array",
        "Wt's JSON array — an ordered list of Json.Value. Mirror of\n"
        "Json.Object on the sequence side: construct from a Python list,\n"
        "read back with `.to_list()`.\n"
        "\n"
        "    tags = wt.Json.Array(['admin', 'editor', 'viewer'])\n"
        "    len(tags)                              # 3\n"
        "    tags.to_list()                         # ['admin', ...]")
        .def("__init__", [](Wt::Json::Array* self) {
            new (self) Wt::Json::Array();
        },
            "Default-construct an empty JSON array.")
        .def("__init__",
            [](Wt::Json::Array* self, nb::list items) {
                new (self) Wt::Json::Array();
                for (nb::handle item : items) {
                    self->push_back(py_to_json_value(item));
                }
            },
            "items"_a,
            "Construct from a Python list. Items can be any JSON-compatible "
            "Python value (same set as Object accepts).")
        .def("__len__",
            [](const Wt::Json::Array& a) { return a.size(); },
            "Number of elements in the array.")
        .def("to_list",
            [](const Wt::Json::Array& a) {
                nb::list l;
                for (const auto& v : a) {
                    l.append(json_value_to_py(v));
                }
                return l;
            },
            "Recursive Python-native view of this Array.");

    // ---- Json::Value ----
    //
    // The polymorphic JSON value. Construct from any Python value; read
    // the contained payload via `.type` plus `.to_python()`.

    nb::class_<Wt::Json::Value>(json, "Value",
        "Polymorphic JSON value. Holds one of: null, bool, number,\n"
        "string, object, or array (see Json.Type). Convert from any\n"
        "JSON-compatible Python value at construction; read back with\n"
        "`.to_python()`.\n"
        "\n"
        "    v = wt.Json.Value({'n': 1, 'xs': [1, 2, 3]})\n"
        "    v.type                                 # Type.Object\n"
        "    v.to_python()                          # {'n': 1.0, ...}\n"
        "\n"
        "Numbers always come back as Python floats — see the parent\n"
        "submodule docstring for the lossy int/float caveat.")
        .def(nb::init<>(),
            "Default-construct a Null value.")
        .def("__init__",
            // nb::object explicitly accepts None — nb::handle plus the
            // implicit overload-resolution rules ends up rejecting it.
            [](Wt::Json::Value* self, nb::object py_val) {
                new (self) Wt::Json::Value(py_to_json_value(py_val));
            },
            "value"_a.none(),
            "Construct from a Python value. Pass any JSON-compatible "
            "Python value (None / bool / int / float / str / dict / list).")
        .def_prop_ro("type",
            [](const Wt::Json::Value& v) { return v.type(); },
            "The Json.Type tag of the contained value.")
        .def_prop_ro("is_null",
            [](const Wt::Json::Value& v) { return v.isNull(); },
            "True when this value is JSON null. Equivalent to\n"
            "`type == Type.Null`.")
        .def("to_python",
            [](const Wt::Json::Value& v) { return json_value_to_py(v); },
            "Recursive Python-native view of this Value.");

    // ---- Parse / serialize helpers ----

    json.def("parse",
        [](const std::string& input) {
            Wt::Json::Object result;
            Wt::Json::parse(input, result);
            return result;
        },
        "input"_a,
        "Parse a JSON document into a Json.Object. Use `.to_dict()` on "
        "the result for a Python-native view.");

    json.def("parse_value",
        [](const std::string& input) {
            Wt::Json::Value result;
            Wt::Json::parse(input, result);
            return result;
        },
        "input"_a,
        "Parse a JSON document into a Json.Value (handles top-level "
        "primitives / arrays / objects equally).");

    json.def("serialize",
        [](const Wt::Json::Object& obj, int indentation) {
            return Wt::Json::serialize(obj, indentation);
        },
        "obj"_a, "indentation"_a = 1,
        "Serialize a Json.Object to a JSON string.");

    json.def("serialize_array",
        [](const Wt::Json::Array& arr, int indentation) {
            return Wt::Json::serialize(arr, indentation);
        },
        "arr"_a, "indentation"_a = 1,
        "Serialize a Json.Array to a JSON string. Counterpart of\n"
        "`serialize` for top-level array documents.");

    // ---- Free-standing converters (Python dict ⇄ Json::Object) ----
    //
    // Convenience for callers who prefer functional style over the
    // Object(dict) constructor.

    json.def("from_python",
        [](nb::handle val) -> Wt::Json::Value {
            return py_to_json_value(val);
        },
        "value"_a,
        "Convert a Python value to a Json.Value. Recursive for dicts "
        "and lists.");

    json.def("to_python",
        [](const Wt::Json::Value& v) { return json_value_to_py(v); },
        "value"_a,
        "Convert a Json.Value to a Python native value. Inverse of "
        "from_python.");
}

}  // namespace witty_for_python
