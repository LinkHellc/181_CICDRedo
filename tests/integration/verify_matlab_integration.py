"""Functional verification for MATLAB integration.

This script tests the actual MATLAB integration functionality.

Usage:
    python tests/integration/verify_matlab_integration.py
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from integrations.matlab import MatlabIntegration
from core.models import StageConfig, BuildContext


def test_matlab_engine_startup():
    """Test 1: MATLAB engine startup"""
    print("\n[TEST 1] MATLAB Engine Startup")
    print("-" * 50)

    messages = []
    def log_callback(msg):
        messages.append(msg)
        print(f"  [LOG] {msg}")

    matlab = MatlabIntegration(log_callback=log_callback)

    print("Starting MATLAB engine...")
    start_time = time.time()

    success = matlab.start_engine()

    elapsed = time.time() - start_time

    if success and matlab.is_running():
        print(f"[PASS] Engine started successfully in {elapsed:.2f}s")
        matlab.stop_engine()
        return True
    else:
        print("[FAIL] Engine failed to start")
        return False


def test_matlab_version():
    """Test 2: MATLAB version check"""
    print("\n[TEST 2] MATLAB Version Compatibility")
    print("-" * 50)

    messages = []
    def log_callback(msg):
        messages.append(msg)
        print(f"  [LOG] {msg}")

    matlab = MatlabIntegration(log_callback=log_callback)

    print("Checking MATLAB version...")

    try:
        matlab.start_engine()

        # Try to get version
        version = matlab.engine.version()
        print(f"[INFO] MATLAB Version: {version}")

        # Check if version is acceptable
        if any(year in str(version) for year in ["20", "21", "22", "23", "24"]):
            print("[PASS] MATLAB version is compatible")
            matlab.stop_engine()
            return True
        else:
            print(f"[WARN] Version {version} may not be compatible")
            matlab.stop_engine()
            return True  # Don't fail on version warning

    except Exception as e:
        print(f"[FAIL] Version check failed: {e}")
        return False


def test_matlab_simple_execution():
    """Test 3: Simple MATLAB command execution"""
    print("\n[TEST 3] Simple MATLAB Command Execution")
    print("-" * 50)

    messages = []
    def log_callback(msg):
        messages.append(msg)
        print(f"  [LOG] {msg}")

    matlab = MatlabIntegration(log_callback=log_callback)

    print("Starting engine...")
    if not matlab.start_engine():
        print("[FAIL] Could not start engine")
        return False

    print("Executing simple command: 2 + 2...")
    try:
        result = matlab.engine.eval("2 + 2", nargout=1)
        print(f"[INFO] Result: {result}")

        if result == 4:
            print("[PASS] Command execution successful")
            matlab.stop_engine()
            return True
        else:
            print(f"[FAIL] Unexpected result: {result}")
            matlab.stop_engine()
            return False

    except Exception as e:
        print(f"[FAIL] Command execution failed: {e}")
        matlab.stop_engine()
        return False


def test_context_manager():
    """Test 4: Context manager usage"""
    print("\n[TEST 4] Context Manager Usage")
    print("-" * 50)

    messages = []
    def log_callback(msg):
        messages.append(msg)
        print(f"  [LOG] {msg}")

    print("Testing with context manager...")

    try:
        with MatlabIntegration(log_callback=log_callback) as matlab:
            if matlab.is_running():
                print("[INFO] Engine running inside context")
                result = matlab.engine.eval("sqrt(16)", nargout=1)
                print(f"[INFO] sqrt(16) = {result}")

                if result == 4.0:
                    print("[PASS] Context manager works correctly")
                    return True

        print("[FAIL] Context manager test failed")
        return False

    except Exception as e:
        print(f"[FAIL] Context manager error: {e}")
        return False


def test_output_file_validation():
    """Test 5: Output file validation logic"""
    print("\n[TEST 5] Output File Validation Logic")
    print("-" * 50)

    from stages.matlab_gen import _validate_output_files

    messages = []
    def log_callback(msg):
        messages.append(msg)
        print(f"  [LOG] {msg}")

    context = BuildContext(
        config={},
        state={},
        log_callback=log_callback
    )

    # Test with non-existent directory
    print("Testing with non-existent directory...")
    result = _validate_output_files("/nonexistent/path", context)

    if not result["valid"]:
        print("[PASS] Correctly detected non-existent directory")
        print(f"       Message: {result['message']}")
    else:
        print("[FAIL] Should have detected non-existent directory")
        return False

    # Test with temporary directory
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"\nTesting with temporary directory: {temp_dir}")

        # Create code directory
        code_dir = Path(temp_dir) / "20_Code"
        code_dir.mkdir()

        # Create test files
        (code_dir / "test1.c").touch()
        (code_dir / "test2.c").touch()
        (code_dir / "test.h").touch()
        (code_dir / "Rte_TmsApp.h").touch()  # Should be in exclude list

        result = _validate_output_files(temp_dir, context)

        if result["valid"]:
            print("[PASS] File validation successful")
            print(f"       C files: {len(result['output_files']['c_files'])}")
            print(f"       H files: {len(result['output_files']['h_files'])}")
            print(f"       Exclude: {result['output_files']['exclude']}")
            return True
        else:
            print(f"[FAIL] Validation failed: {result['message']}")
            return False


def test_stage_executor():
    """Test 6: Stage executor integration"""
    print("\n[TEST 6] Stage Executor Integration")
    print("-" * 50)

    from core.workflow import STAGE_EXECUTORS

    if "matlab_gen" in STAGE_EXECUTORS:
        print("[PASS] matlab_gen executor registered in STAGE_EXECUTORS")
        print(f"       Executor type: {type(STAGE_EXECUTORS['matlab_gen']).__name__}")
        return True
    else:
        print("[FAIL] matlab_gen executor not found in STAGE_EXECUTORS")
        print(f"       Available executors: {list(STAGE_EXECUTORS.keys())}")
        return False


def main():
    """Run all verification tests"""
    print("=" * 50)
    print("MATLAB Integration Functional Verification")
    print("=" * 50)

    # Check MATLAB Engine API first
    try:
        import matlab.engine
        print("[INFO] MATLAB Engine API is available")
    except ImportError:
        print("[ERROR] MATLAB Engine API not installed!")
        print("\nPlease install it first:")
        print("1. Open MATLAB")
        print("2. Run: cd(fullfile(matlabroot, 'extern', 'engines', 'python'))")
        print("3. Run: system('python setup.py install')")
        return False

    # Run tests
    tests = [
        test_matlab_engine_startup,
        test_matlab_version,
        test_matlab_simple_execution,
        test_context_manager,
        test_output_file_validation,
        test_stage_executor,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n[ERROR] Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)

    # Summary
    print("\n" + "=" * 50)
    print("VERIFICATION SUMMARY")
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("\n[SUCCESS] All tests passed!")
        return True
    else:
        print(f"\n[FAILURE] {total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
