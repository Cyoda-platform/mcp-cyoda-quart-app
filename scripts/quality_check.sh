#!/bin/bash
#
# Comprehensive Code Quality Checker
# Orchestrates all code quality checks using modular scripts.
#

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
QUALITY_DIR="$SCRIPT_DIR/quality"

# Source common utilities
source "$QUALITY_DIR/common.sh"

# Available checks
declare -A CHECKS=(
    ["syntax"]="$QUALITY_DIR/syntax_check.sh"
    ["style"]="$QUALITY_DIR/style_check.sh"
    ["format"]="$QUALITY_DIR/format_check.sh"
    ["imports"]="$QUALITY_DIR/import_check.sh"
    ["types"]="$QUALITY_DIR/type_check.sh"
    ["security"]="$QUALITY_DIR/security_check.sh"
    ["tests"]="$QUALITY_DIR/test_runner.sh"
    ["advanced"]="$QUALITY_DIR/advanced_analysis.sh"
)

# Default check order
DEFAULT_CHECKS=("syntax" "style" "format" "imports" "types" "security" "tests" "advanced")

usage() {
    echo "Usage: $0 [OPTIONS] [CHECKS...]"
    echo ""
    echo "OPTIONS:"
    echo "  --fix           Apply automatic fixes where possible"
    echo "  --coverage      Include coverage analysis in tests"
    echo "  --detailed      Show detailed output"
    echo "  --fast          Skip slower checks (sonar, detailed security)"
    echo "  --help          Show this help message"
    echo ""
    echo "CHECKS (run in order if specified, otherwise run default set):"
    echo "  syntax          Python syntax validation"
    echo "  style           Code style checking (flake8)"
    echo "  format          Code formatting (black)"
    echo "  imports         Import sorting (isort)"
    echo "  types           Type checking (mypy)"
    echo "  security        Security scanning (bandit)"
    echo "  sonar           SonarQube analysis"
    echo "  tests           Test execution"
    echo ""
    echo "Examples:"
    echo "  $0                          # Run all default checks"
    echo "  $0 --fix                    # Run checks and apply fixes"
    echo "  $0 syntax style format      # Run only specified checks"
    echo "  $0 --coverage tests         # Run tests with coverage"
    echo "  $0 --fast                   # Quick check (skip sonar)"
}

main() {
    local fix_mode=false
    local coverage=false
    local detailed=false
    local fast_mode=false
    local checks_to_run=()
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --fix)
                fix_mode=true
                shift
                ;;
            --coverage)
                coverage=true
                shift
                ;;
            --detailed)
                detailed=true
                shift
                ;;
            --fast)
                fast_mode=true
                shift
                ;;
            --help|-h)
                usage
                exit 0
                ;;
            syntax|style|format|imports|types|security|tests)
                checks_to_run+=("$1")
                shift
                ;;
            *)
                echo "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done
    
    # Use default checks if none specified
    if [ ${#checks_to_run[@]} -eq 0 ]; then
        checks_to_run=("${DEFAULT_CHECKS[@]}")
        

    fi
    
    # Print header
    echo -e "${BLUE}🔧 Cyoda Client Application - Comprehensive Code Quality Check${NC}"
    echo -e "${BLUE}=============================================================${NC}"
    echo ""
    
    # Show environment info
    check_venv
    echo ""
    
    # Track results
    local total_checks=0
    local passed_checks=0
    local failed_checks=0
    local skipped_checks=0
    
    # Run each check
    for check in "${checks_to_run[@]}"; do
        if [[ ! -v CHECKS[$check] ]]; then
            echo -e "${RED}❌ Unknown check: $check${NC}"
            continue
        fi
        
        local script="${CHECKS[$check]}"
        if [ ! -f "$script" ]; then
            echo -e "${RED}❌ Script not found: $script${NC}"
            continue
        fi
        
        # Make script executable
        chmod +x "$script"
        
        # Build arguments for the script
        local script_args=()
        
        case $check in
            format|imports)
                if [ "$fix_mode" = true ]; then
                    script_args+=("--fix")
                fi
                ;;
            security)
                if [ "$detailed" = true ]; then
                    script_args+=("--detailed")
                fi
                ;;

            tests)
                if [ "$coverage" = true ]; then
                    script_args+=("--coverage")
                fi
                ;;
        esac
        
        # Run the check
        echo -e "${BLUE}Running $check check...${NC}"
        if "$script" "${script_args[@]}"; then
            ((passed_checks++))
        else
            ((failed_checks++))
        fi
        
        ((total_checks++))
        echo ""
    done
    
    # Print summary
    echo -e "${BLUE}📊 Summary${NC}"
    echo -e "${BLUE}==========${NC}"
    echo -e "Total checks: $total_checks"
    echo -e "${GREEN}Passed: $passed_checks${NC}"
    
    if [ $failed_checks -gt 0 ]; then
        echo -e "${RED}Failed: $failed_checks${NC}"
    fi
    
    if [ $skipped_checks -gt 0 ]; then
        echo -e "${YELLOW}Skipped: $skipped_checks${NC}"
    fi
    
    echo ""
    
    if [ $failed_checks -eq 0 ]; then
        echo -e "${GREEN}🎉 All checks passed!${NC}"
        return 0
    else
        echo -e "${RED}❌ Some checks failed - review the issues above${NC}"
        
        if [ "$fix_mode" = false ]; then
            echo ""
            echo "💡 Tip: Run with --fix to automatically apply fixes where possible"
        fi
        
        return 1
    fi
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
