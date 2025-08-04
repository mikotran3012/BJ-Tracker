#!/usr/bin/env python3
# setup.py - FIXED VERSION for Advanced EV Engine Build
import sys
import os
from setuptools import setup, Extension
import pybind11
from pybind11.setup_helpers import Pybind11Extension, build_ext

print("🎯 Building bjlogic_cpp with Advanced EV Engine (FIXED VERSION)...")
print("PyBind11 version:", pybind11.__version__)
print("Python version:", sys.version)

# Check if source files exist
source_files = [
    'cpp_src/bjlogic_core.cpp',
    'cpp_src/basic_strategy.cpp',
    'cpp_src/card_counting.cpp',
    'cpp_src/advanced_ev_engine.cpp',
    'cpp_src/recursive_dealer_engine.cpp',
    'cpp_src/enhanced_bindings.cpp',
]

# Check for optional files (but exclude advanced_ev_bindings.cpp to avoid duplicates)
optional_files = [
    'cpp_src/hand_calc.cpp',
    # 'cpp_src/advanced_ev_bindings.cpp',  # EXCLUDED - causes duplicate definitions
]

# Only include files that exist
existing_sources = []
for file in source_files:
    if os.path.exists(file):
        existing_sources.append(file)
        print(f"✅ Found: {file}")
    else:
        print(f"❌ Missing: {file}")

for file in optional_files:
    if os.path.exists(file):
        existing_sources.append(file)
        print(f"✅ Optional found: {file}")
    else:
        print(f"⚠️  Optional missing: {file}")

# Warn about excluded files
if os.path.exists('cpp_src/advanced_ev_bindings.cpp'):
    print("⚠️  EXCLUDED: cpp_src/advanced_ev_bindings.cpp (to avoid duplicate definitions)")

# Determine compiler flags based on platform
if sys.platform == 'win32':
    extra_compile_args = [
        '/std:c++17',
        '/EHsc',
        '/O2',
        '/DNOMINMAX',  # Prevent Windows min/max macro conflicts
        '/D_USE_MATH_DEFINES'  # Enable math constants
    ]
    extra_link_args = []
else:
    extra_compile_args = [
        '-std=c++17',
        '-O3',
        '-fPIC',
        '-Wall',
        '-Wextra',
        '-Wno-unused-parameter'
    ]
    extra_link_args = ['-lm']  # Link math library

# Define the extension
bjlogic_extension = Pybind11Extension(
    'bjlogic_cpp',
    sources=existing_sources,
    include_dirs=[
        'cpp_src',
    ],
    language='c++',
    cxx_std=17,
    extra_compile_args=extra_compile_args,
    extra_link_args=extra_link_args,
)

setup(
    name="bjlogic_cpp",
    version="2.3.1+fixed",
    description="Advanced Blackjack C++ Extension - FIXED BUILD",
    author="Advanced Blackjack Analytics Team",
    ext_modules=[bjlogic_extension],
    cmdclass={'build_ext': build_ext},
    zip_safe=False,
    python_requires='>=3.7',
    install_requires=['pybind11>=2.6.0'],
)