#!/usr/bin/env python3
# setup.py - Fixed version with correct include paths
import sys
from setuptools import setup, Extension
import pybind11

print("PyBind11 version:", pybind11.__version__)
print("PyBind11 include path:", pybind11.get_include())
print("PyBind11 cmake path:", pybind11.get_cmake_dir())

# Define the extension with correct include paths
bjlogic_extension = Extension(
    'bjlogic_cpp',
    sources=[
        'cpp_src/hand_calc.cpp',
        'cpp_src/minimal_bindings.cpp'
    ],
    include_dirs=[
        pybind11.get_include(),  # This is the correct way to get PyBind11 includes
        'cpp_src',
    ],
    language='c++',
    extra_compile_args=['/std:c++17', '/EHsc'] if sys.platform == 'win32' else ['-std=c++17'],
)

setup(
    name="bjlogic_cpp",
    version="1.0.0",
    description="Blackjack C++ extension that actually works",
    ext_modules=[bjlogic_extension],
    zip_safe=False,
)