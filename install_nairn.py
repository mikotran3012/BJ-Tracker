# install_nairn.py
"""
Installation script for Nairn EV Calculator integration.
Automates the setup process and verifies installation.
"""

import os
import sys
import shutil
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 6):
        print("❌ Python 3.6 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} is compatible")
    return True


def check_dependencies():
    """Check if required dependencies are available."""
    dependencies = ['tkinter', 'threading', 'pathlib']
    missing = []

    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep} is available")
        except ImportError:
            missing.append(dep)
            print(f"❌ {dep} is missing")

    if missing:
        print(f"\nMissing dependencies: {', '.join(missing)}")
        if 'tkinter' in missing:
            print("Install tkinter with: sudo apt-get install python3-tk (Linux) or ensure GUI support")
        return False

    return True


def create_file_from_content(filename, content):
    """Create a file with the given content."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Created {filename}")
        return True
    except Exception as e:
        print(f"❌ Failed to create {filename}: {e}")
        return False


def get_nairn_calculator_content():
    """Return the content for nairn_ev_calculator.py"""
    # Note: In a real deployment, this would be read from the artifact
    # For now, we'll provide a placeholder that instructs to copy from artifact
    return '''# nairn_ev_calculator.py
"""
PLACEHOLDER FILE - REPLACE WITH ACTUAL CONTENT

To complete installation:
1. Copy the full content from the "Nairn EV Calculator" artifact
2. Paste it into this file, replacing this placeholder
3. Save the file

The artifact contains approximately 1000+ lines of John Nairn's adapted algorithms.
"""

print("ERROR: This is a placeholder file. Please copy the actual Nairn EV calculator content from the artifact.")
print("See installation instructions in the README or documentation.")

# Placeholder classes to prevent import errors during installation
class NairnRules:
    pass

class BlackjackTrackerNairnIntegration:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Please install the actual Nairn calculator content")

def analyze_with_nairn_algorithm(*args, **kwargs):
    raise NotImplementedError("Please install the actual Nairn calculator content")

def create_nairn_calculator(*args, **kwargs):
    raise NotImplementedError("Please install the actual Nairn calculator content")
'''


def get_integration_content():
    """Return the content for nairn_integration.py"""
    # This would also be from the artifact in a real deployment
    return '''# nairn_integration.py
"""
PLACEHOLDER FILE - REPLACE WITH ACTUAL CONTENT

To complete installation:
1. Copy the full content from the "Nairn Integration Module" artifact  
2. Paste it into this file, replacing this placeholder
3. Save the file

The artifact contains the UI integration and event handling code.
"""

print("ERROR: This is a placeholder file. Please copy the actual integration content from the artifact.")

def integrate_nairn_with_app(*args, **kwargs):
    raise NotImplementedError("Please install the actual integration content")

class NairnEVPanel:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Please install the actual integration content")
'''


def install_files():
    """Install the Nairn calculator files."""
    print("\n📁 Installing Nairn EV Calculator files...")

    files_to_create = [
        ('nairn_ev_calculator.py', get_nairn_calculator_content()),
        ('nairn_integration.py', get_integration_content()),
    ]

    success = True
    for filename, content in files_to_create:
        if os.path.exists(filename):
            backup_name = f"{filename}.backup"
            shutil.copy2(filename, backup_name)
            print(f"📋 Backed up existing {filename} to {backup_name}")

        if not create_file_from_content(filename, content):
            success = False

    return success


def create_readme():
    """Create a README file with installation and usage instructions."""
    readme_content = '''# Nairn EV Calculator Integration

## Overview
This integration adds John Nairn's exact blackjack EV algorithms to your BlackjackTrackerApp.

## Installation Status
✅ Files created (with placeholders)
❌ Content needs to be copied from artifacts

## Complete Installation Steps

### Step 1: Copy Algorithm Content
1. Open `nairn_ev_calculator.py`
2. Delete all placeholder content
3. Copy the ENTIRE content from the "Nairn EV Calculator" artifact
4. Paste into the file and save

### Step 2: Copy Integration Content  
1. Open `nairn_integration.py`
2. Delete all placeholder content
3. Copy the ENTIRE content from the "Nairn Integration Module" artifact
4. Paste into the file and save

### Step 3: Test Installation
```bash
python test_nairn_integration.py
```

### Step 4: Integrate with Your App
Add this to your main app file:

```python
from nairn_integration import integrate_nairn_with_app

class BlackjackTrackerApp:
    def __init__(self):
        # Your existing code...
        self.setup_nairn_integration()

    def setup_nairn_integration(self):
        if hasattr(self, 'right_frame'):
            self.nairn_panel = integrate_nairn_with_app(self, self.right_frame)
```

## Features
- ⚡ Real-time EV analysis using Nairn's exact algorithms
- 🔥 Breakthrough splitting calculations (11,000 years → seconds)
- 📊 Composition-dependent recommendations
- 🎯 Griffin card removal effects for counting
- 🖥️ Clean UI integration with your existing app

## Files
- `nairn_ev_calculator.py` - Core Nairn algorithms (1000+ lines)
- `nairn_integration.py` - UI integration and event handling
- `test_nairn_integration.py` - Test suite
- `install_nairn.py` - This installation script

## Troubleshooting
If you see "placeholder file" errors:
1. You need to copy the actual content from the artifacts
2. The placeholder files prevent import errors during installation
3. Follow Steps 1-2 above to complete the installation

## Support
- Test your installation with: `python test_nairn_integration.py`
- Check that all imports work before integrating with your main app
- The Nairn panel will appear automatically once properly integrated
'''

    create_file_from_content('README_NAIRN.md', readme_content)


def create_test_file():
    """Create the test file."""
    # This would contain the test content from the artifact
    test_content = '''# test_nairn_integration.py
"""
PLACEHOLDER TEST FILE

Copy the actual test content from the "Nairn Integration Test" artifact
to complete the installation and run proper tests.
"""

print("Please copy the actual test content from the artifact.")
print("This placeholder prevents import errors during installation.")

def run_all_tests():
    print("Placeholder test - copy actual content from artifact")
    return False

if __name__ == "__main__":
    run_all_tests()
'''

    create_file_from_content('test_nairn_integration.py', test_content)


def main():
    """Main installation function."""
    print("🚀 NAIRN EV CALCULATOR INSTALLATION")
    print("=" * 50)

    print("\n🔍 Checking system requirements...")
    if not check_python_version():
        return False

    if not check_dependencies():
        return False

    print("\n📦 Installing files...")
    if not install_files():
        print("❌ File installation failed")
        return False

    create_test_file()
    create_readme()

    print("\n✅ Installation completed!")
    print("\n⚠️  IMPORTANT: Installation is not complete yet!")
    print("You must copy the actual content from the artifacts:")
    print("1. Copy content from 'Nairn EV Calculator' artifact to nairn_ev_calculator.py")
    print("2. Copy content from 'Nairn Integration Module' artifact to nairn_integration.py")
    print("3. Copy content from 'Nairn Integration Test' artifact to test_nairn_integration.py")
    print("\n📖 See README_NAIRN.md for detailed instructions")
    print("\n🧪 After copying content, test with:")
    print("   python test_nairn_integration.py")

    return True


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)