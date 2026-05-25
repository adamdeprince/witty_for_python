cmake_minimum_required(VERSION 3.26)
project(pywitty
  LANGUAGES CXX
  VERSION 0.1.0
  DESCRIPTION "Python bindings for the Wt (Web Toolkit) C++ library")

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(CMAKE_CXX_VISIBILITY_PRESET hidden)
set(CMAKE_VISIBILITY_INLINES_HIDDEN ON)

# Bake the link-time library directories into the extension's RPATH so users
# do not need to set LD_LIBRARY_PATH at runtime when Wt is in a non-default
# prefix (e.g. ~/.local).
set(CMAKE_INSTALL_RPATH_USE_LINK_PATH ON)

if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  set(CMAKE_BUILD_TYPE Release CACHE STRING "" FORCE)
endif()

# -- Python (used by nanobind to build a CPython extension module) --
find_package(Python 3.10
  REQUIRED COMPONENTS Interpreter Development.Module
  OPTIONAL_COMPONENTS Development.SABIModule)

# -- nanobind (located via the installed Python package) --
execute_process(
  COMMAND "${Python_EXECUTABLE}" -m nanobind --cmake_dir
  OUTPUT_STRIP_TRAILING_WHITESPACE
  OUTPUT_VARIABLE nanobind_ROOT)
find_package(nanobind CONFIG REQUIRED)

# -- Wt (system install: libwt-dev libwthttp-dev, brew wt, etc.) --
find_package(Wt REQUIRED COMPONENTS Wt HTTP)

set(PYWITTY_SOURCES
  ext/module.cpp
  ext/bind_signals.cpp
  ext/bind_application.cpp
  ext/bind_container.cpp
  ext/bind_widgets.cpp
  ext/bind_form.cpp
  ext/bind_navigation.cpp
  ext/bind_table.cpp
  ext/bind_layout.cpp
  ext/bind_server.cpp)

  # Free-threaded Python (3.13+ with --disable-gil; standard in 3.14+) has no
  # GIL — multiple Python threads can execute concurrently. Wt fires slots
  # from worker threads, so we want to opt into nanobind's thread-safe paths
  # when running under a free-threaded interpreter. nanobind auto-disables
  # STABLE_ABI in that case (the two flags are mutually exclusive). The "t"
  # suffix in the Python ABI tag identifies a free-threaded build.
if(Python_SOABI MATCHES "t$" OR Python_SOABI MATCHES "t-")
  message(STATUS "Building witty_for_python for free-threaded Python (${Python_SOABI})")
  nanobind_add_module(_witty_for_python
    FREE_THREADED
    NB_STATIC
    ${PYWITTY_SOURCES})
else()
  nanobind_add_module(_witty_for_python
    STABLE_ABI
    NB_STATIC
    ${PYWITTY_SOURCES})
endif()

target_include_directories(_witty_for_python PRIVATE ext)
target_link_libraries(_witty_for_python PRIVATE Wt::Wt Wt::HTTP)

install(TARGETS _witty_for_python LIBRARY DESTINATION witty_for_python)
