#pragma once

// Transparent conversion between Wt's date/time value types and Python's
// `datetime` module — same pattern as the WString ↔ str caster in
// common.hpp. With these casters registered, Wt's value types are never
// exposed as their own Python classes; the user just passes / receives
// `datetime.date`, `datetime.time`, `datetime.datetime`.
//
// Invalid / null Wt values (`WDate::isNull()`, etc.) round-trip as
// Python `None`.
//
// Resolution mismatch: Python `datetime.time` carries microseconds
// (0–999_999); `Wt::WTime` carries milliseconds (0–999). Python → Wt
// truncates by `microsecond // 1000`; Wt → Python multiplies by 1000.
// Sub-millisecond precision is lost crossing the boundary.

#include <nanobind/nanobind.h>

#include <Wt/WDate.h>
#include <Wt/WTime.h>
#include <Wt/WDateTime.h>

namespace nanobind::detail {

// Cache the Python datetime module's date / time / datetime classes on
// first use. The handle is a borrowed reference that lives for the
// lifetime of the interpreter (the `datetime` module isn't reloadable in
// any meaningful sense), so a static is fine.
inline ::nanobind::handle _py_date_type() {
    static ::nanobind::object t = ::nanobind::module_::import_("datetime").attr("date");
    return t;
}
inline ::nanobind::handle _py_time_type() {
    static ::nanobind::object t = ::nanobind::module_::import_("datetime").attr("time");
    return t;
}
inline ::nanobind::handle _py_datetime_type() {
    static ::nanobind::object t = ::nanobind::module_::import_("datetime").attr("datetime");
    return t;
}

template <> struct type_caster<Wt::WDate> {
    NB_TYPE_CASTER(Wt::WDate, const_name("datetime.date | None"))

    bool from_python(handle src, uint8_t, cleanup_list*) noexcept {
        if (src.is_none()) { value = Wt::WDate(); return true; }
        try {
            int is = PyObject_IsInstance(src.ptr(), _py_date_type().ptr());
            if (is != 1) return false;
            int y = ::nanobind::cast<int>(src.attr("year"));
            int m = ::nanobind::cast<int>(src.attr("month"));
            int d = ::nanobind::cast<int>(src.attr("day"));
            value = Wt::WDate(y, m, d);
            return true;
        } catch (...) { return false; }
    }

    static handle from_cpp(const Wt::WDate& src, rv_policy, cleanup_list*) noexcept {
        if (src.isNull() || !src.isValid()) {
            return ::nanobind::none().release();
        }
        try {
            ::nanobind::object o = _py_date_type()(src.year(), src.month(), src.day());
            return o.release();
        } catch (...) { return handle(); }
    }
};

template <> struct type_caster<Wt::WTime> {
    NB_TYPE_CASTER(Wt::WTime, const_name("datetime.time | None"))

    bool from_python(handle src, uint8_t, cleanup_list*) noexcept {
        if (src.is_none()) { value = Wt::WTime(); return true; }
        try {
            int is = PyObject_IsInstance(src.ptr(), _py_time_type().ptr());
            if (is != 1) return false;
            int h  = ::nanobind::cast<int>(src.attr("hour"));
            int mi = ::nanobind::cast<int>(src.attr("minute"));
            int s  = ::nanobind::cast<int>(src.attr("second"));
            int us = ::nanobind::cast<int>(src.attr("microsecond"));
            value = Wt::WTime(h, mi, s, us / 1000);
            return true;
        } catch (...) { return false; }
    }

    static handle from_cpp(const Wt::WTime& src, rv_policy, cleanup_list*) noexcept {
        if (src.isNull() || !src.isValid()) {
            return ::nanobind::none().release();
        }
        try {
            int us = src.msec() * 1000;
            ::nanobind::object o = _py_time_type()(
                src.hour(), src.minute(), src.second(), us);
            return o.release();
        } catch (...) { return handle(); }
    }
};

template <> struct type_caster<Wt::WDateTime> {
    NB_TYPE_CASTER(Wt::WDateTime, const_name("datetime.datetime | None"))

    bool from_python(handle src, uint8_t, cleanup_list*) noexcept {
        if (src.is_none()) { value = Wt::WDateTime(); return true; }
        try {
            int is = PyObject_IsInstance(src.ptr(), _py_datetime_type().ptr());
            if (is != 1) return false;
            int y  = ::nanobind::cast<int>(src.attr("year"));
            int mo = ::nanobind::cast<int>(src.attr("month"));
            int d  = ::nanobind::cast<int>(src.attr("day"));
            int h  = ::nanobind::cast<int>(src.attr("hour"));
            int mi = ::nanobind::cast<int>(src.attr("minute"));
            int s  = ::nanobind::cast<int>(src.attr("second"));
            int us = ::nanobind::cast<int>(src.attr("microsecond"));
            value = Wt::WDateTime(Wt::WDate(y, mo, d),
                                  Wt::WTime(h, mi, s, us / 1000));
            return true;
        } catch (...) { return false; }
    }

    static handle from_cpp(const Wt::WDateTime& src, rv_policy, cleanup_list*) noexcept {
        if (src.isNull() || !src.isValid()) {
            return ::nanobind::none().release();
        }
        try {
            Wt::WDate d = src.date();
            Wt::WTime t = src.time();
            int us = t.msec() * 1000;
            ::nanobind::object o = _py_datetime_type()(
                d.year(), d.month(), d.day(),
                t.hour(), t.minute(), t.second(), us);
            return o.release();
        } catch (...) { return handle(); }
    }
};

}  // namespace nanobind::detail
