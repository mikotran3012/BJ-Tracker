#!/usr/bin/env python3
# setup.py - Clean version for Phase 2.1 Migration
import sys
from setuptools import setup, Extension
import pybind11

print("🔧 Building bjlogic_cpp with enhanced features...")
print("PyBind11 version:", pybind11.__version__)
print("PyBind11 include path:", pybind11.get_include())

# Define the extension with all source files
bjlogic_extension = Extension(
    'bjlogic_cpp',
    sources=[
        'cpp_src/hand_calc.cpp',        # Keep this (compatibility)
        'cpp_src/bjlogic_core.cpp',     # Add this (new core logic)
        'cpp_src/enhanced_bindings.cpp' # Replace minimal_bindings.cpp
    ],
    include_dirs=[
        pybind11.get_include(),  # PyBind11 headers
        'cpp_src',              # Our header files
    ],
    language='c++',
    extra_compile_args=['/std:c++17', '/EHsc'] if sys.platform == 'win32' else ['-std=c++17'],
)

setup(
    name="bjlogic_cpp",
    version="2.1.0",
    description="Advanced Blackjack C++ extension - Phase 2.1 Migration",
    ext_modules=[bjlogic_extension],
    zip_safe=False,
)