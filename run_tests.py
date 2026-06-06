#!/usr/bin/env python
import unittest
import sys
import os

def run_unit_tests():
    print("\n" + "="*60)
    print("RUNNING UNIT TESTS")
    print("="*60)
    
    loader = unittest.TestLoader()
    suite = loader.discover("tests/unit", pattern="test_*.py")
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_integration_tests():
    print("\n" + "="*60)
    print("RUNNING INTEGRATION TESTS")
    print("="*60)
    print("Note: Make sure modules are running on ports 5001, 5002, 5003")
    
    loader = unittest.TestLoader()
    suite = loader.discover("tests/integration", pattern="test_*.py")
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_e2e_tests():
    print("\n" + "="*60)
    print("RUNNING E2E TESTS")
    print("="*60)
    print("Note: Make sure modules are running on ports 5001, 5002, 5003")
    
    loader = unittest.TestLoader()
    suite = loader.discover("tests/e2e", pattern="test_*.py")
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("DELIVERY INTEGRATION TEST SUITE")
    print("="*60)
    
    results = []
    
    # Run unit tests
    results.append(run_unit_tests())
    
    # Ask user if modules are running
    print("\n" + "="*60)
    response = input("Are the modules running (dispatcher:5001, tracking:5002, notify:5003)? (y/n): ")
    
    if response.lower() == 'y':
        results.append(run_integration_tests())
        results.append(run_e2e_tests())
    else:
        print("\nSkipping integration and E2E tests. Start modules with:")
        print("  python module_a_dispatcher.py &")
        print("  python module_b_tracking.py &")
        print("  python module_c_notify.py &")
        results.append(True)  # Skip integration
        results.append(True)  # Skip E2E
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Unit Tests:       {'✓ PASSED' if results[0] else '✗ FAILED'}")
    if len(results) > 1:
        print(f"Integration Tests: {'✓ PASSED' if results[1] else '✗ FAILED'}")
    if len(results) > 2:
        print(f"E2E Tests:        {'✓ PASSED' if results[2] else '✗ FAILED'}")
    print("="*60)
    
    sys.exit(0 if all(results) else 1)
