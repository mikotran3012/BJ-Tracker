#!/usr/bin/env python3
# setup.py - Phase 2.3+: Building Advanced EV Engine (Step by Step)
import sys
import os
from setuptools import setup, Extension
import pybind11

print("🎯 Building bjlogic_cpp with Advanced EV Engine (Step by Step)...")
print("PyBind11 version:", pybind11.__version__)
print("Python version:", sys.version)

# Determine compiler flags based on platform
if sys.platform == 'win32':
    extra_compile_args = ['/std:c++17', '/EHsc', '/O2']
    extra_link_args = []
else:
    extra_compile_args = ['-std=c++17', '-O3', '-march=native']
    extra_link_args = []

# Define the extension with core files + basic advanced EV engine
bjlogic_extension = Extension(
    'bjlogic_cpp',
    sources=[
        'cpp_src/hand_calc.cpp',
        'cpp_src/bjlogic_core.cpp',
        'cpp_src/basic_strategy.cpp',
        'cpp_src/card_counting.cpp',
        'cpp_src/advanced_ev_engine.cpp',
        'cpp_src/enhanced_bindings.cpp',
        'cpp_src/recursive_dealer_engine.cpp',
        'cpp_src/advanced_ev_bindings.cpp',
    ],
    include_dirs=[
        pybind11.get_include(),
        'cpp_src',
    ],
    language='c++',
    extra_compile_args=extra_compile_args,
    extra_link_args=extra_link_args,
)

setup(
    name="bjlogic_cpp",
    version="2.3.1",
    description="Advanced Blackjack C++ Extension - Step by Step Build",
    author="Advanced Blackjack Analytics Team",
    ext_modules=[bjlogic_extension],
    zip_safe=False,
    python_requires='>=3.7',
)