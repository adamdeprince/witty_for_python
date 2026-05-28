#pragma once

#include <nanobind/nanobind.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/vector.h>
#include <nanobind/stl/unique_ptr.h>
#include <nanobind/stl/shared_ptr.h>
#include <nanobind/stl/function.h>
#include <nanobind/stl/chrono.h>

#include <Wt/WString.h>

// Bring in datetime casters so every binding file sees Wt::WDate / WTime /
// WDateTime as Python `datetime.date` / `time` / `datetime`.
#include "datetime_caster.hpp"

#include <string>

namespace nb = nanobind;

// Transparently convert Wt::WString <-> Python str. Wt uses WString everywhere
// for i18n; surfacing it as native str keeps the Python API ergonomic.
namespace nanobind::detail {
template <> struct type_caster<Wt::WString> {
    NB_TYPE_CASTER(Wt::WString, const_name("str"))

    bool from_python(handle src, uint8_t, cleanup_list*) noexcept {
        if (!PyUnicode_Check(src.ptr())) return false;
        Py_ssize_t size = 0;
        const char* str = PyUnicode_AsUTF8AndSize(src.ptr(), &size);
        if (!str) { PyErr_Clear(); return false; }
        value = Wt::WString::fromUTF8(std::string(str, static_cast<size_t>(size)));
        return true;
    }

    static handle from_cpp(const Wt::WString& src, rv_policy, cleanup_list*) noexcept {
        std::string utf8 = src.toUTF8();
        return PyUnicode_FromStringAndSize(
            utf8.data(), static_cast<Py_ssize_t>(utf8.size()));
    }
};
}  // namespace nanobind::detail

namespace witty_for_python {

using namespace nb::literals;

void register_signals(nb::module_& m);
void register_application(nb::module_& m);
void register_validators(nb::module_& m);
void register_container(nb::module_& m);
void register_widgets(nb::module_& m);
void register_form(nb::module_& m);
void register_datetime(nb::module_& m);
void register_template(nb::module_& m);
void register_navigation(nb::module_& m);
void register_resource(nb::module_& m);
void register_themes(nb::module_& m);
void register_timer(nb::module_& m);
void register_upload(nb::module_& m);
void register_extra_form(nb::module_& m);
void register_filedrop(nb::module_& m);
void register_chrome(nb::module_& m);
void register_modelview(nb::module_& m);
void register_modelview_proxy(nb::module_& m);
void register_value_types(nb::module_& m);
void register_event_payloads(nb::module_& m);
void register_misc_ui(nb::module_& m);
void register_layouts_extra(nb::module_& m);
void register_media(nb::module_& m);
void register_painting_types(nb::module_& m);
void register_painting(nb::module_& m);
void register_chart(nb::module_& m);
void register_niche_widgets(nb::module_& m);
void register_json(nb::module_& m);
void register_table(nb::module_& m);
void register_layout(nb::module_& m);
void register_server(nb::module_& m);

}  // namespace witty_for_python
