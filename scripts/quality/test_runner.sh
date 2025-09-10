#!/bin/bash
# 
# Test Runner
# Executes test suites and generates coverage reports.
# 

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source common utilities
source "$SCRIPT_DIR/common.sh"

main() {
    local coverage=false
    local test_path="tests/"
    local verbose=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --coverage)
                coverage=true
                shift
                ;;
            --path)
                test_path="$2"
                shift 2
                ;;
            --verbose|-v)
                verbose=true
                shift
                ;;
            *)
                echo "Usage: $0 [--coverage] [--path TEST_PATH] [--verbose]"
                echo "  --coverage      Generate coverage report"
                echo "  --path PATH     Test path (default: tests/)"
                echo "  --verbose       Verbose output"
                exit 1
                ;;
        esac
    done
    
    print_header "Test Execution"
    
    cd "$PROJECT_ROOT"
    
    # Check if test directory exists
    if [ ! -d "$test_path" ]; then
        print_status "WARN" "Test directory not found: $test_path"
        return 1
    fi
    
    # Install pytest if missing
    if ! command_exists pytest; then
        echo "📦 Installing pytest..."
        if ! python -m pip install pytest pytest-asyncio pytest-cov &> /dev/null; then
            print_status "ERROR" "Failed to install pytest"
            return 1
        fi
    fi
    
    # Build pytest command
    local pytest_cmd="python -m pytest"
    local pytest_args="--tb=short"
    
    if [ "$verbose" = true ]; then
        pytest_args="$pytest_args -v"
    fi
    
    if [ "$coverage" = true ]; then
        pytest_args="$pytest_args --cov=. --cov-report=xml --cov-report=html --cov-report=term"
        echo "Running tests with coverage analysis..."
    else
        echo "Running tests..."
    fi
    
    # Add test path
    pytest_args="$pytest_args $test_path"
    
    # Run tests
    local test_output
    test_output=$($pytest_cmd $pytest_args 2>&1)
    local exit_code=$?
    
    # Parse results
    if [ $exit_code -eq 0 ]; then
        local test_count
        test_count=$(echo "$test_output" | grep -o "[0-9]\+ passed" | grep -o "[0-9]\+" || echo "0")
        
        print_status "PASS" "All tests passed ($test_count tests)"
        
        if [ "$coverage" = true ]; then
            # Extract coverage percentage
            local coverage_pct
            coverage_pct=$(echo "$test_output" | grep -o "TOTAL.*[0-9]\+%" | grep -o "[0-9]\+%" || echo "unknown")
            echo "   Coverage: $coverage_pct"
            
            if [ -f "htmlcov/index.html" ]; then
                echo "   HTML coverage report: htmlcov/index.html"
            fi
            
            if [ -f "coverage.xml" ]; then
                echo "   XML coverage report: coverage.xml"
            fi
        fi
        
        return 0
    else
        local failed_count
        failed_count=$(echo "$test_output" | grep -o "[0-9]\+ failed" | grep -o "[0-9]\+" || echo "0")
        local passed_count
        passed_count=$(echo "$test_output" | grep -o "[0-9]\+ passed" | grep -o "[0-9]\+" || echo "0")
        
        print_status "ERROR" "Tests failed ($failed_count failed, $passed_count passed)"
        
        # Show failure details
        echo ""
        echo "Test failures:"
        echo "$test_output" | grep -A 3 "FAILED" | head -15
        
        return 1
    fi
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
