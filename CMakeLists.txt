cmake_minimum_required(VERSION 3.26)
project(witty_for_python
  LANGUAGES CXX
  VERSION 0.1.0
  DESCRIPTION "Python bindings for the Wt (Web Toolkit) C++ library")

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(CMAKE_CXX_VISIBILITY_PRESET hidden)
set(CMAKE_VISIBILITY_INLINES_HIDDEN ON)

# We ship Wt's libwt.so + libwthttp.so alongside the extension, in
# <package>/_libs/. RPATH points there relative to the extension itself, so
# the wheel is self-contained — `import witty_for_python` doesn't need
# LD_LIBRARY_PATH or any system Wt install.
set(CMAKE_INSTALL_RPATH_USE_LINK_PATH ON)
if(APPLE)
  set(CMAKE_INSTALL_RPATH "@loader_path/_libs")
else()
  set(CMAKE_INSTALL_RPATH "$ORIGIN/_libs")
endif()
# Use the install-time RPATH while building too, so editable installs work
# without re-linking.
set(CMAKE_BUILD_WITH_INSTALL_RPATH ON)

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

# -- Wt (vendored at extern/wt as a git submodule, pinned to release 4.13.2) --
#
# The submodule SHA in .gitmodules + the recorded gitlink is the GPL
# source-traceability anchor: any binary built from this repo links the
# exact Wt source at that pinned commit, and that commit is in our git
# history. There is no system Wt install; we build it in-tree.
if(NOT EXISTS "${CMAKE_SOURCE_DIR}/extern/wt/CMakeLists.txt")
  message(FATAL_ERROR
    "Wt source not found at extern/wt. Did you clone with --recursive? "
    "Run `git submodule update --init --recursive` to fetch it.")
endif()

# Wt's CMake options. Set BEFORE add_subdirectory so they take effect.
set(BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
set(BUILD_TESTS OFF CACHE BOOL "" FORCE)
set(INSTALL_EXAMPLES OFF CACHE BOOL "" FORCE)
set(CONNECTOR_HTTP ON CACHE BOOL "" FORCE)
set(CONNECTOR_FCGI OFF CACHE BOOL "" FORCE)
set(ENABLE_SSL OFF CACHE BOOL "" FORCE)
set(ENABLE_HARU OFF CACHE BOOL "" FORCE)
set(ENABLE_PANGO OFF CACHE BOOL "" FORCE)
set(ENABLE_OPENGL OFF CACHE BOOL "" FORCE)
set(ENABLE_SQLITE OFF CACHE BOOL "" FORCE)
set(ENABLE_POSTGRES OFF CACHE BOOL "" FORCE)
set(ENABLE_MYSQL OFF CACHE BOOL "" FORCE)
set(ENABLE_FIREBIRD OFF CACHE BOOL "" FORCE)
set(ENABLE_MSSQLSERVER OFF CACHE BOOL "" FORCE)
set(ENABLE_QT4 OFF CACHE BOOL "" FORCE)
set(ENABLE_QT5 OFF CACHE BOOL "" FORCE)
set(ENABLE_QT6 OFF CACHE BOOL "" FORCE)
set(SHARED_LIBS ON CACHE BOOL "" FORCE)
set(MULTI_THREADED ON CACHE BOOL "" FORCE)
# Wt's CMake insists on RUNDIR/CONFIGDIR/WEBUSER/WEBGROUP being set. They are
# baked into wt_config.xml templates and the wthttpd defaults, but we will
# never use the installed defaults — runtime values are passed on the wthttpd
# command line (--docroot, --resources-dir, etc.). Set them to obviously-
# placeholder paths so misuse is loud.
set(RUNDIR     "/var/lib/witty_for_python/RUNDIR-unused"     CACHE PATH   "" FORCE)
set(CONFIGDIR  "/var/lib/witty_for_python/CONFIGDIR-unused"  CACHE PATH   "" FORCE)
set(WEBUSER    "nobody"  CACHE STRING "" FORCE)
set(WEBGROUP   "nogroup" CACHE STRING "" FORCE)

# EXCLUDE_FROM_ALL: Wt's targets aren't built by `make all` and Wt's own
# install rules don't fire during `cmake --install`. We build Wt only because
# our extension depends on `wt` / `wthttp` via target_link_libraries, and we
# add our own install rules below that put Wt's .so files where the wheel
# wants them.
add_subdirectory(extern/wt EXCLUDE_FROM_ALL)

set(WITTY_FOR_PYTHON_SOURCES
  ext/module.cpp
  ext/bind_signals.cpp
  ext/bind_application.cpp
  ext/bind_validators.cpp
  ext/bind_container.cpp
  ext/bind_widgets.cpp
  ext/bind_form.cpp
  ext/bind_datetime.cpp
  ext/bind_template.cpp
  ext/bind_navigation.cpp
  ext/bind_resource.cpp
  ext/bind_table.cpp
  ext/bind_layout.cpp
  ext/bind_server.cpp
  ext/bind_themes.cpp
  ext/bind_timer.cpp
  ext/bind_upload.cpp
  ext/bind_extra_form.cpp
  ext/bind_filedrop.cpp
  ext/bind_chrome.cpp
  ext/bind_modelview.cpp
  ext/bind_modelview_proxy.cpp)

# Free-threaded Python (3.13+ with --disable-gil; standard in 3.14+) has no
# GIL — multiple Python threads can execute concurrently. Wt fires slots from
# worker threads, so we opt into nanobind's thread-safe paths when running
# under a free-threaded interpreter. STABLE_ABI and FREE_THREADED are mutually
# exclusive in nanobind. The "t" suffix in the Python ABI tag identifies a
# free-threaded build.
if(Python_SOABI MATCHES "t$" OR Python_SOABI MATCHES "t-")
  message(STATUS "Building witty_for_python for free-threaded Python (${Python_SOABI})")
  nanobind_add_module(_witty_for_python
    FREE_THREADED
    NB_STATIC
    ${WITTY_FOR_PYTHON_SOURCES})
else()
  nanobind_add_module(_witty_for_python
    STABLE_ABI
    NB_STATIC
    ${WITTY_FOR_PYTHON_SOURCES})
endif()

target_include_directories(_witty_for_python PRIVATE
  ext
  # Wt uses pre-target-API `include_directories()`, so the `wt` target doesn't
  # propagate INTERFACE includes via target_link_libraries. Add them by hand:
  #   src/                       — for "#include <Wt/WString.h>" and friends
  #   ${CMAKE_BINARY_DIR}/extern/wt — for the generated WConfig.h
  "${CMAKE_SOURCE_DIR}/extern/wt/src"
  "${CMAKE_BINARY_DIR}/extern/wt")
target_link_libraries(_witty_for_python PRIVATE wt wthttp)

# Wheel install layout:
#   witty_for_python/
#     _witty_for_python.cpython-*.so      ← the extension (this target)
#     _libs/libwt.so, libwthttp.so        ← Wt shared libs (RPATH target)
#     _wt_resources/                       ← Wt's static assets (CSS/JS/themes)
install(TARGETS _witty_for_python
        LIBRARY DESTINATION witty_for_python)
install(TARGETS wt wthttp
        LIBRARY DESTINATION witty_for_python/_libs)
install(DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/extern/wt/resources/"
        DESTINATION witty_for_python/_wt_resources)

# -- TinyMCE (vendored at extern/tinymce as a git submodule, pinned to
#    release tinymce@6.8.4) --
#
# Same forensic story as Wt: the gitlink in our history points at the exact
# TinyMCE source revision. License at that tag is MIT (Tiny later switched
# main to GPLv2+; we are pinned to the MIT-era tag).
#
# TinyMCE has no checked-in build artefacts, so we drive `yarn install` +
# `yarn build` here at configure/build time. The build is slow (~3-5 min,
# downloads + transpiles a large TS/JS tree); we cache its output via a
# stamp file so subsequent CMake builds skip it when nothing changed.
#
# WTextEdit doesn't work without these assets, so we make the build an
# error if yarn isn't on PATH. Set WITTY_FOR_PYTHON_BUILD_TINYMCE=OFF to
# skip (e.g. during a partial dev cycle where you don't need rich text).

option(WITTY_FOR_PYTHON_BUILD_TINYMCE
       "Build TinyMCE from the vendored submodule and bundle it into the wheel"
       ON)

if(WITTY_FOR_PYTHON_BUILD_TINYMCE)
  if(NOT EXISTS "${CMAKE_SOURCE_DIR}/extern/tinymce/package.json")
    message(FATAL_ERROR
      "TinyMCE source not found at extern/tinymce. Run "
      "`git submodule update --init --recursive` to fetch it, or pass "
      "-DWITTY_FOR_PYTHON_BUILD_TINYMCE=OFF to skip (WTextEdit won't work).")
  endif()

  find_program(YARN_EXECUTABLE yarn
    DOC "Path to yarn (TinyMCE build tool)")
  if(NOT YARN_EXECUTABLE)
    message(FATAL_ERROR
      "yarn not found on PATH. Required to build TinyMCE. Install it via "
      "`corepack enable yarn` (Node 16+) or `npm install -g yarn`, or pass "
      "-DWITTY_FOR_PYTHON_BUILD_TINYMCE=OFF.")
  endif()

  set(TINYMCE_SRC_DIR   "${CMAKE_SOURCE_DIR}/extern/tinymce")
  set(TINYMCE_DIST_DIR  "${TINYMCE_SRC_DIR}/modules/tinymce/js/tinymce")
  # The minified core JS is the canonical "yes, build ran" marker.
  set(TINYMCE_DIST_FILE "${TINYMCE_DIST_DIR}/tinymce.min.js")

  add_custom_command(
    OUTPUT  "${TINYMCE_DIST_FILE}"
    COMMAND "${YARN_EXECUTABLE}" install --frozen-lockfile --ignore-scripts
    COMMAND "${YARN_EXECUTABLE}" install --frozen-lockfile
    COMMAND "${YARN_EXECUTABLE}" build
    WORKING_DIRECTORY "${TINYMCE_SRC_DIR}"
    # We don't track every source file (there are thousands); package.json
    # + yarn.lock are the load-bearing inputs for a clean rebuild. Touching
    # those re-fires the build; editing TinyMCE source in-place won't,
    # which is fine because we never expect to modify the submodule.
    DEPENDS "${TINYMCE_SRC_DIR}/package.json"
            "${TINYMCE_SRC_DIR}/yarn.lock"
    COMMENT "Building TinyMCE via yarn (this takes a few minutes)"
    VERBATIM)

  add_custom_target(witty_for_python_tinymce_build ALL
                    DEPENDS "${TINYMCE_DIST_FILE}")

  install(DIRECTORY "${TINYMCE_DIST_DIR}/"
          DESTINATION witty_for_python/_wt_resources/tinymce)
endif()
