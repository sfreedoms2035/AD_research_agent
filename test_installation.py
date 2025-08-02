"""
Test script to verify the installation of the Automated Driving Research Agent.
"""

import sys
import subprocess
import json

def test_python_version():
    """Test if Python version is sufficient."""
    print("Testing Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} - Too old, need 3.7+")
        return False

def test_required_packages():
    """Test if required packages are installed."""
    print("\nTesting required packages...")
    
    required_packages = [
        "arxiv",
        "requests",
        "google.generativeai"
    ]
    
    all_good = True
    
    for package in required_packages:
        try:
            if package == "google.generativeai":
                import google.generativeai
                print("✓ google-generativeai - OK")
            else:
                __import__(package)
                print(f"✓ {package} - OK")
        except ImportError as e:
            print(f"✗ {package} - NOT INSTALLED ({e})")
            all_good = False
    
    return all_good

def test_config_file():
    """Test if config file exists and is valid."""
    print("\nTesting configuration file...")
    
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        
        # Check required sections
        required_sections = ["research_settings", "search_terms", "ranking_criteria"]
        for section in required_sections:
            if section in config:
                print(f"✓ {section} - OK")
            else:
                print(f"✗ {section} - MISSING")
                return False
        
        print("✓ config.json - OK")
        return True
        
    except FileNotFoundError:
        print("✗ config.json - NOT FOUND")
        return False
    except json.JSONDecodeError as e:
        print(f"✗ config.json - INVALID JSON ({e})")
        return False
    except Exception as e:
        print(f"✗ config.json - ERROR ({e})")
        return False

def test_main_scripts():
    """Test if main scripts exist."""
    print("\nTesting main scripts...")
    
    required_files = [
        "enhanced_ad_research_agent.py",
        "requirements.txt",
        "README.md"
    ]
    
    all_good = True
    
    for file in required_files:
        try:
            with open(file, "r") as f:
                pass
            print(f"✓ {file} - OK")
        except FileNotFoundError:
            print(f"✗ {file} - NOT FOUND")
            all_good = False
    
    return all_good

def main():
    """Run all tests."""
    print("Automated Driving Research Agent - Installation Test")
    print("=" * 55)
    
    tests = [
        test_python_version,
        test_required_packages,
        test_config_file,
        test_main_scripts
    ]
    
    all_passed = True
    
    for test in tests:
        if not test():
            all_passed = False
    
    print("\n" + "=" * 55)
    if all_passed:
        print("✓ ALL TESTS PASSED - Installation is ready!")
        print("\nNext steps:")
        print("1. Get your API key from Google AI Studio or Kimi")
        print("2. Run: python enhanced_ad_research_agent.py --api-key YOUR_KEY")
    else:
        print("✗ SOME TESTS FAILED - Please check the errors above")
        print("\nTry running: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
