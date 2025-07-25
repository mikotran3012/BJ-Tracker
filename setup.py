# setup.py
"""
Build system for blackjack C++ extension using PyBind11.
Handles cross-platform compilation and optimization.
"""

from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup, Extension
import pybind11
import platform
import os
import sys


# =============================================================================
# COMPILER OPTIMIZATION FLAGS
# =============================================================================

def get_compiler_flags():
    """Get optimized compiler flags for the current platform."""
    base_flags = [
        '-std=c++17',
        '-O3',  # Maximum optimization
        '-DNDEBUG',  # Remove debug assertions
        '-ffast-math',  # Aggressive math optimizations
        '-march=native',  # Use CPU-specific instructions
    ]

    if platform.system() == "Windows":
        # MSVC flags
        return [
            '/O2',  # Maximum optimization
            '/DNDEBUG',  # Remove debug
            '/fp:fast',  # Fast floating point
            '/std:c++17',  # C++17 standard
        ]
    elif platform.system() == "Darwin":  # macOS
        # Clang flags for macOS
        base_flags.extend([
            '-mmacosx-version-min=10.9',
            '-stdlib=libc++',
        ])
    else:  # Linux and others
        # GCC flags
        base_flags.extend([
            '-fopenmp',  # OpenMP parallelization
            '-funroll-loops',  # Loop unrolling
            '-fomit-frame-pointer',
        ])

    return base_flags


def get_linker_flags():
    """Get linker flags for the current platform."""
    if platform.system() == "Linux":
        return ['-lgomp']  # Link OpenMP
    return []


# =============================================================================
# EXTENSION DEFINITION
# =============================================================================

# Define the C++ extension
bjlogic_extension = Pybind11Extension(
    "bjlogic_cpp",
    sources=[
        "cpp_src/bjlogic_core.cpp_src",
        "cpp_src/bjlogic_dealer.cpp_src",
        "cpp_src/bjlogic_ev.cpp_src",
        "cpp_src/bjlogic_deck.cpp_src",
        "cpp_src/bjlogic_nairn.cpp_src",
        "cpp_src/bjlogic_bindings.cpp_src",
    ],
    include_dirs=[
        pybind11.get_cmake_dir(),
        "cpp_src/",
    ],
    cxx_std=17,
    extra_compile_args=get_compiler_flags(),
    extra_link_args=get_linker_flags(),
    define_macros=[
        ('VERSION_INFO', '"dev"'),
        ('PYBIND11_DETAILED_ERROR_MESSAGES', None),
    ],
)


# Custom build_ext class for additional optimizations
class OptimizedBuildExt(build_ext):
    """Custom build extension with additional optimizations."""

    def build_extensions(self):
        # Enable parallel compilation if available
        if hasattr(self.compiler, 'compiler_so'):
            if '-j' not in self.compiler.compiler_so:
                import multiprocessing
                self.parallel = multiprocessing.cpu_count()

        # Platform-specific optimizations
        if platform.system() == "Linux":
            # Enable Link Time Optimization
            for ext in self.extensions:
                ext.extra_compile_args.append('-flto')
                ext.extra_link_args.append('-flto')

        super().build_extensions()


# =============================================================================
# SETUP CONFIGURATION
# =============================================================================

setup(
    name="blackjack-tracker-cpp_src",
    version="1.0.0",
    author="AI Assistant",
    author_email="ai@example.com",
    description="High-performance blackjack logic with C++ backend",
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    ext_modules=[bjlogic_extension],
    cmdclass={"build_ext": OptimizedBuildExt},
    zip_safe=False,
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.19.0",
        "pybind11>=2.6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-benchmark",
            "cProfile",
            "line_profiler",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-cov",
            "hypothesis",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: C++",
        "Topic :: Games/Entertainment",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
)

# =============================================================================
# CMAKE BUILD SYSTEM (Alternative)
# =============================================================================

# CMakeLists.txt content (save as separate file)
CMAKE_CONTENT = """
cmake_minimum_required(VERSION 3.12)
project(bjlogic_cpp)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Optimization flags
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

set(CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG -ffast-math -march=native")

# Find Python and PyBind11
find_package(pybind11 REQUIRED)

# Source files
set(SOURCES
    cpp_src/bjlogic_core.cpp_src
    cpp_src/bjlogic_dealer.cpp_src
    cpp_src/bjlogic_ev.cpp_src
    cpp_src/bjlogic_deck.cpp_src
    cpp_src/bjlogic_nairn.cpp_src
    cpp_src/bjlogic_bindings.cpp_src
)

# Create PyBind11 module
pybind11_add_module(bjlogic_cpp ${SOURCES})

# Compiler-specific optimizations
if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    target_compile_options(bjlogic_cpp PRIVATE -fopenmp -funroll-loops)
    target_link_libraries(bjlogic_cpp PRIVATE gomp)
elseif(CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
    target_compile_options(bjlogic_cpp PRIVATE -fopenmp=libomp)
    target_link_libraries(bjlogic_cpp PRIVATE omp)
endif()

# Link Time Optimization
if(CMAKE_BUILD_TYPE STREQUAL "Release")
    set_property(TARGET bjlogic_cpp PROPERTY INTERPROCEDURAL_OPTIMIZATION TRUE)
endif()

# Install target
install(TARGETS bjlogic_cpp DESTINATION .)
"""

# Write CMakeLists.txt if it doesn't exist
if not os.path.exists("CMakeLists.txt"):
    with open("CMakeLists.txt", "w") as f:
        f.write(CMAKE_CONTENT)

# =============================================================================
# MAKEFILE (Alternative build method)
# =============================================================================

MAKEFILE_CONTENT = """
# Makefile for blackjack C++ extension
# Usage: make all

CXX = g++
PYTHON = python3
PIP = pip3

# Compiler flags
CXXFLAGS = -std=c++17 -O3 -DNDEBUG -ffast-math -march=native -fopenmp
LDFLAGS = -lgomp

# Python and PyBind11 includes
PYTHON_INCLUDES = $(shell $(PYTHON) -m pybind11 --includes)
PYTHON_SUFFIX = $(shell $(PYTHON)-config --extension-suffix)

# Source files
SOURCES = cpp_src/bjlogic_core.cpp_src cpp_src/bjlogic_dealer.cpp_src cpp_src/bjlogic_ev.cpp_src cpp_src/bjlogic_deck.cpp_src cpp_src/bjlogic_nairn.cpp_src cpp_src/bjlogic_bindings.cpp_src

# Target
TARGET = bjlogic_cpp$(PYTHON_SUFFIX)

.PHONY: all clean install test benchmark

all: $(TARGET)

$(TARGET): $(SOURCES)
	$(CXX) $(CXXFLAGS) $(PYTHON_INCLUDES) -shared -fPIC $^ -o $@ $(LDFLAGS)

clean:
	rm -f $(TARGET)
	rm -rf build/
	rm -rf *.egg-info/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

install: $(TARGET)
	$(PIP) install -e .

test: $(TARGET)
	$(PYTHON) -m pytest tests/ -v

benchmark: $(TARGET)
	$(PYTHON) benchmark_cpp_vs_python.py

# Development targets
dev-install:
	$(PIP) install -e .[dev]

dev-build:
	$(PYTHON) setup.py build_ext --inplace

profile:
	$(PYTHON) -m cProfile -o profile.stats performance_profiler.py
	$(PYTHON) -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats(20)"

memory-test:
	$(PYTHON) -m memory_profiler benchmark_memory.py

# Help target
help:
	@echo "Available targets:"
	@echo "  all          - Build the C++ extension"
	@echo "  clean        - Remove build artifacts"
	@echo "  install      - Install the package"
	@echo "  test         - Run tests"
	@echo "  benchmark    - Run performance benchmarks"
	@echo "  dev-install  - Install with development dependencies"
	@echo "  dev-build    - Build extension in-place for development"
	@echo "  profile      - Profile the application"
	@echo "  memory-test  - Run memory usage tests"
"""

# Write Makefile if it doesn't exist
if not os.path.exists("Makefile"):
    with open("Makefile", "w") as f:
        f.write(MAKEFILE_CONTENT)


# =============================================================================
# BUILD VERIFICATION SCRIPT
# =============================================================================

def verify_build():
    """Verify that the C++ extension builds and works correctly."""
    print("Verifying C++ extension build...")

    try:
        # Try to import the compiled module
        import bjlogic_cpp
        print("✅ C++ module imported successfully")

        # Test basic functionality
        hand_result = bjlogic_cpp.calculate_hand_value([1, 10])
        assert hand_result['total'] == 21
        assert hand_result['is_blackjack'] == True
        print("✅ Hand calculation working")

        # Test basic strategy
        action = bjlogic_cpp.basic_strategy_decision(
            [10, 6], 10, {'num_decks': 6, 'dealer_hits_soft_17': False}
        )
        assert action in ['hit', 'stand', 'double', 'split', 'surrender']
        print("✅ Basic strategy working")

        # Test performance (should be much faster than Python)
        import time
        start = time.perf_counter()
        for _ in range(1000):
            bjlogic_cpp.calculate_hand_value([8, 8])
        cpp_time = time.perf_counter() - start

        print(f"✅ Performance test: 1000 calculations in {cpp_time:.4f}s")

    except ImportError as e:
        print(f"❌ Failed to import C++ module: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing C++ module: {e}")
        return False

    return True


if __name__ == "__main__":
    print("Build system for Blackjack C++ extension")
    print("Run 'python setup.py build_ext --inplace' to build")
    print("Run 'python setup.py verify' to test the build")

    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        success = verify_build()
        sys.exit(0 if success else 1)