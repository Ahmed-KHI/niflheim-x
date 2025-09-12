#!/usr/bin/env python3
"""
Quick verification script for Niflheim_x framework.
Run this after cloning to ensure everything works correctly.
"""

import sys
import subprocess


def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"🔍 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False


def main():
    """Run verification checks."""
    print("🚀 Niflheim_x Framework Verification")
    print("=" * 50)
    
    checks = [
        ("python -c 'import niflheim_x; print(f\"Niflheim_x v{niflheim_x.__version__} imported successfully\")'", 
         "Import framework"),
        ("python -c 'from niflheim_x import Agent, DictMemory; print(\"Core components imported\")'", 
         "Import core components"),
        ("python -c 'from niflheim_x.llms import OpenAIAdapter, AnthropicAdapter; print(\"LLM adapters imported\")'", 
         "Import LLM adapters"),
        ("python -c 'from niflheim_x.core.tools import tool; print(\"Tool system imported\")'", 
         "Import tool system"),
    ]
    
    success_count = 0
    for cmd, desc in checks:
        if run_command(cmd, desc):
            success_count += 1
    
    print("\n" + "=" * 50)
    if success_count == len(checks):
        print("🎉 ALL CHECKS PASSED! Framework is ready to use.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -e .")
        print("2. Run tests: pytest tests/")
        print("3. Check examples: python examples/simple_qa_bot.py")
    else:
        print(f"⚠️  {len(checks) - success_count} checks failed. Please check your setup.")
        
    return success_count == len(checks)


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
