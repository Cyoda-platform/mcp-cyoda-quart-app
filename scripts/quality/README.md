# Code Quality System

A comprehensive, modular code quality system for the Cyoda Client Application.

## 🚀 Quick Start

```bash
# Run all quality checks
./scripts/quality_check.sh

# Run checks with automatic fixes
./scripts/quality_check.sh --fix

# Quick check (skip slower tools)
./scripts/quality_check.sh --fast

# Auto-fix common issues
./scripts/auto_fix.sh
```

## 📁 Structure

```
scripts/
├── quality_check.sh          # Main orchestrator script
├── auto_fix.sh              # Automatic fixes for common issues
└── quality/
    ├── common.sh             # Shared utilities and functions
    ├── syntax_check.sh       # Python syntax validation
    ├── style_check.sh        # Code style (flake8)
    ├── format_check.sh       # Code formatting (black)
    ├── import_check.sh       # Import sorting (isort)
    ├── type_check.sh         # Type checking (mypy)
    ├── security_check.sh     # Security scanning (bandit)
    ├── sonar_check.sh        # SonarQube analysis
    └── test_runner.sh        # Test execution with coverage
```

## 🔧 Individual Tools

### Syntax Check
```bash
./scripts/quality/syntax_check.sh
```
Validates Python syntax using `py_compile`.

### Style Check
```bash
./scripts/quality/style_check.sh
```
Checks code style using `flake8` with custom configuration.

### Format Check
```bash
./scripts/quality/format_check.sh           # Check formatting
./scripts/quality/format_check.sh --fix     # Apply formatting
```
Validates and fixes code formatting using `black`.

### Import Check
```bash
./scripts/quality/import_check.sh           # Check imports
./scripts/quality/import_check.sh --fix     # Sort imports
```
Validates and sorts imports using `isort`.

### Type Check
```bash
./scripts/quality/type_check.sh
```
Performs static type checking using `mypy`.

### Security Check
```bash
./scripts/quality/security_check.sh                # Basic scan
./scripts/quality/security_check.sh --detailed     # Detailed report
```
Scans for security vulnerabilities using `bandit`.

### SonarQube Analysis
```bash
./scripts/quality/sonar_check.sh                           # Default (localhost:9000)
./scripts/quality/sonar_check.sh --url http://sonar.com    # Custom URL
./scripts/quality/sonar_check.sh --create-config          # Force config creation
```
Comprehensive code analysis using SonarQube scanner.

### Test Runner
```bash
./scripts/quality/test_runner.sh                    # Run tests
./scripts/quality/test_runner.sh --coverage         # With coverage
./scripts/quality/test_runner.sh --path tests/unit  # Specific path
```
Executes tests with optional coverage analysis.

## 🎯 Main Script Options

### Basic Usage
```bash
./scripts/quality_check.sh [OPTIONS] [CHECKS...]
```

### Options
- `--fix`: Apply automatic fixes where possible
- `--coverage`: Include coverage analysis in tests
- `--sonar-url URL`: Specify SonarQube server URL
- `--detailed`: Show detailed output
- `--fast`: Skip slower checks (sonar, detailed security)
- `--help`: Show help message

### Available Checks
- `syntax`: Python syntax validation
- `style`: Code style checking (flake8)
- `format`: Code formatting (black)
- `imports`: Import sorting (isort)
- `types`: Type checking (mypy)
- `security`: Security scanning (bandit)
- `sonar`: SonarQube analysis
- `tests`: Test execution

### Examples
```bash
# Run all default checks
./scripts/quality_check.sh

# Run specific checks only
./scripts/quality_check.sh syntax style format

# Run with fixes and coverage
./scripts/quality_check.sh --fix --coverage

# Quick development check
./scripts/quality_check.sh --fast syntax style format tests

# Full analysis with SonarQube
./scripts/quality_check.sh --sonar-url http://sonar.company.com
```

## 🔄 Auto-Fix Script

The `auto_fix.sh` script automatically applies common fixes:

1. **Black formatting**: Consistent code style
2. **Import sorting**: Organized imports with isort
3. **Trailing whitespace**: Removes trailing spaces
4. **Basic flake8 fixes**: Simple automated fixes
5. **Final validation**: Runs quality check after fixes

```bash
./scripts/auto_fix.sh
```

## 📊 Tool Configuration

### Black Configuration
- Line length: 88 characters (default)
- Excludes: `.venv`, `__pycache__`, `.pytest_cache`

### Flake8 Configuration
- Max line length: 120 characters
- Ignored: E203, W503, E501
- Excludes: `.venv`, `__pycache__`, `.pytest_cache`

### isort Configuration
- Skips: `.venv`, `__pycache__`, `.pytest_cache`
- Compatible with Black formatting

### MyPy Configuration
Auto-generated `mypy.ini` with:
- Python version: 3.8+
- Ignore missing imports: True
- Show error codes: True
- Exclude: `.venv`, `__pycache__`, `.pytest_cache`, `proto`

### Bandit Configuration
- Format: JSON for parsing
- Skip: B101 (assert usage), B601 (shell usage)
- Exclude: `.venv`, `__pycache__`, `.pytest_cache`

### SonarQube Configuration
Auto-generated `sonar-project.properties` with:
- Project key: `cyoda-client-app`
- Sources: Current directory
- Exclusions: `.venv`, `__pycache__`, `.pytest_cache`, `proto`, `scripts/quality`

## 🚀 Integration

### Pre-commit Hook
```bash
# Add to .git/hooks/pre-commit
#!/bin/bash
./scripts/quality_check.sh --fast --fix
```

### CI/CD Pipeline
```yaml
# Example GitHub Actions
- name: Code Quality Check
  run: ./scripts/quality_check.sh --coverage
```

### Development Workflow
1. Make code changes
2. Run `./scripts/auto_fix.sh` to apply automatic fixes
3. Run `./scripts/quality_check.sh --fast` for quick validation
4. Run full check before committing: `./scripts/quality_check.sh`

## 🛠️ Troubleshooting

### Tool Installation Issues
All scripts automatically install missing tools. If installation fails:
```bash
# Manual installation
pip install black isort flake8 mypy bandit pytest pytest-cov sonar-tools==3.15
```

### SonarQube Connection Issues
- Ensure SonarQube server is running
- Check URL and port
- Use `--url` parameter for custom servers

### Permission Issues
```bash
# Make scripts executable
chmod +x scripts/quality_check.sh scripts/auto_fix.sh scripts/quality/*.sh
```

## 📈 Benefits

✅ **Modular Design**: Each tool in separate script for maintainability
✅ **Auto-Installation**: Tools install automatically when missing
✅ **Flexible Usage**: Run individual tools or comprehensive suite
✅ **Auto-Fix Capability**: Automatic fixes for common issues
✅ **CI/CD Ready**: Easy integration with build pipelines
✅ **Comprehensive Coverage**: Syntax, style, security, types, tests
✅ **Professional Quality**: Enterprise-grade code quality standards
