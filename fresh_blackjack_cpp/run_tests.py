# run_tests.py
import subprocess
import sys


def run_test(test_file):
    """Run a test file and capture output"""
    print(f"\nRunning {test_file}...")
    print("-" * 60)

    result = subprocess.run(
        [sys.executable, test_file],
        capture_output=False
    )

    return result.returncode == 0


def main():
    """Run all tests"""
    print("=" * 60)
    print("RUNNING ALL BLACKJACK C++ EXTENSION TESTS")
    print("=" * 60)

    tests = [
        "tests/test_basic.py",
        "tests/test_ev_engine.py",
        "tests/test_integration.py"
    ]

    results = []
    for test in tests:
        success = run_test(test)
        results.append((test, success))

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for test, success in results:
        status = "PASSED" if success else "FAILED"
        print(f"{test}: {status}")

    all_passed = all(success for _, success in results)
    if all_passed:
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()