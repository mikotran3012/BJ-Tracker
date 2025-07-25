#!/usr/bin/env python3
"""
Minimal, clean setup.py for blackjack C++ extension.
This should work without any configuration issues.
"""

from pathlib import Path
import multiprocessing
import platform
from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension, build_ext

# ---------------------------------------------------------------------------
# Compiler and linker flags
# ---------------------------------------------------------------------------

def get_compile_flags():
    """Return platform-specific C++ compiler flags."""
    if platform.system() == "Windows":
        return ["/O2", "/DNDEBUG", "/fp:fast", "/std:c++17"]
    flags = ["-O3", "-ffast-math", "-march=native", "-DNDEBUG"]
    if platform.system() == "Darwin":
        flags.extend(["-mmacosx-version-min=10.9", "-stdlib=libc++"])
    else:
        flags.append("-fopenmp")
    return flags


def get_linker_flags():
    """Return platform-specific linker flags."""
    system = platform.system()
    if system == "Linux":
        return ["-lgomp"]
    if system == "Darwin":
        return []
    if system == "Windows":
        return []
    return []

# ---------------------------------------------------------------------------
# Extension configuration
# ---------------------------------------------------------------------------

source_files = [str(p) for p in sorted(Path("cpp_src").glob("*.cpp"))]

ext_modules = [
    Pybind11Extension(
        "bjlogic_cpp",
        sources=source_files,
        include_dirs=["cpp_src"],
        cxx_std=17,
        extra_compile_args=get_compile_flags(),
        extra_link_args=get_linker_flags(),
    )
]

class ParallelBuildExt(build_ext):
    """Enable parallel compilation using all CPU cores."""

    def build_extensions(self):
        if self.parallel is None:
            self.parallel = multiprocessing.cpu_count()
        super().build_extensions()

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

setup(
    name="bjlogic_cpp",
    version="0.1.0",
    long_description=Path("README.md").read_text() if Path("README.md").exists() else "",
    ext_modules=ext_modules,
    cmdclass={"build_ext": ParallelBuildExt},
    zip_safe=False,
    python_requires=">=3.10",
)