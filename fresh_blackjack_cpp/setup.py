#!/usr/bin/env python3
# setup.py - Phase 2.3: Advanced Card Counting & Probability Engine
import sys
import os
from setuptools import setup, Extension
import pybind11

print("🎯 Building bjlogic_cpp with advanced card counting & probability engine...")
print("PyBind11 version:", pybind11.__version__)
print("Python version:", sys.version)

# Determine compiler flags based on platform
if sys.platform == 'win32':
    extra_compile_args = ['/std:c++17', '/EHsc', '/O2']
    extra_link_args = []
else:
    extra_compile_args = ['-std=c++17', '-O3', '-march=native']
    extra_link_args = []

# Define the extension with all source files
bjlogic_extension = Extension(
    'bjlogic_cpp',
    sources=[
        'cpp_src/hand_calc.cpp',  # Legacy compatibility
        'cpp_src/bjlogic_core.cpp',  # Core logic implementation
        'cpp_src/basic_strategy.cpp',  # Complete strategy tables
        'cpp_src/card_counting.cpp',  # NEW: Card counting implementation
        'cpp_src/enhanced_bindings.cpp',  # Enhanced bindings
        'cpp_src/counting_bindings.cpp'  # NEW: Counting bindings
    ],
    include_dirs=[
        pybind11.get_include(),  # PyBind11 headers
        'cpp_src',  # Our header files
    ],
    language='c++',
    extra_compile_args=extra_compile_args,
    extra_link_args=extra_link_args,
)

setup(
    name="bjlogic_cpp",
    version="2.3.0",
    description="Advanced Blackjack C++ Extension - Phase 2.3 Card Counting & Probability",
    long_description="""
    Professional-grade blackjack analysis library with:
    - Complete basic strategy tables for all rule variations
    - Advanced card counting systems (Hi-Lo, Hi-Opt I/II, Omega II, Zen, Uston APC)
    - Real-time probability calculations with deck composition tracking
    - Monte Carlo simulation engine for strategy validation
    - Performance-optimized C++ core with Python interface
    - Strategy deviation analysis and EV calculations
    """,
    author="Blackjack Analytics Team",
    ext_modules=[bjlogic_extension],
    zip_safe=False,
    python_requires='>=3.7',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Games/Entertainment",
        "Topic :: Scientific/Engineering :: Mathematics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: C++",
    ],
    keywords="blackjack card-counting probability casino strategy",
)

# Post-build verification
if __name__ == "__main__":
    import subprocess
    import sys

    # Check if we're in build mode
    if len(sys.argv) > 1 and 'build' in sys.argv[1]:
        print("\n🔧 Building extension...")

        # After successful build, run quick verification
        try:
            print("✅ Build completed successfully!")
            print("\n🧪 Running quick verification...")

            # Import and test
            import bjlogic_cpp

            message = bjlogic_cpp.test_counting_extension()
            print(f"✅ Extension test: {message}")

            # Test basic functionality
            counter = bjlogic_cpp.CardCounter("Hi-Lo", 6)
            counter.process_cards([10, 10, 5, 6])
            print(f"✅ Card counting test: RC={counter.get_running_count()}, TC={counter.get_true_count():.2f}")

            print("\n🎉 Phase 2.3 extension successfully built and verified!")

        except Exception as e:
            print(f"⚠️  Build verification failed: {e}")
            print("Extension built but may need testing")