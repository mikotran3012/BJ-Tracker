#!/usr/bin/env python3
# setup.py - Phase 2.2: Complete Basic Strategy Tables
import sys
from setuptools import setup, Extension
import pybind11

print("🎯 Building bjlogic_cpp with complete basic strategy tables...")
print("PyBind11 version:", pybind11.__version__)
print("PyBind11 include path:", pybind11.get_include())

# Define the extension with all source files
bjlogic_extension = Extension(
    'bjlogic_cpp',
    sources=[
        'cpp_src/hand_calc.cpp',        # Keep this (compatibility)
        'cpp_src/bjlogic_core.cpp',     # Core logic implementation
        'cpp_src/basic_strategy.cpp',   # New: Complete strategy tables
        'cpp_src/enhanced_bindings.cpp' # Enhanced bindings
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
    version="2.2.0",
    description="Advanced Blackjack C++ extension - Phase 2.2 Complete Strategy",
    ext_modules=[bjlogic_extension],
    zip_safe=False,
)