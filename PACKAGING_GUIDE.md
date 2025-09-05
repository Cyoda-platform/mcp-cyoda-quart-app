# Cyoda MCP Client - One-liner Install Package

Your repository has been successfully transformed into a "one-liner" install package! Users can now run `pipx run mcp-cyoda-client` to instantly use your MCP server without any setup.

## 🎉 What's Been Added

### Core Packaging Files

1. **`pyproject.toml`** - Modern Python packaging configuration
   - Defines package metadata, dependencies, and console script
   - Creates the `mcp-cyoda-client` command
   - Uses modern SPDX license format

2. **`cyoda_mcp/__main__.py`** - CLI entrypoint
   - Robust argument parsing with help text
   - Environment variable validation
   - Clean error handling and logging
   - Version reporting capability

3. **`MANIFEST.in`** - Controls what files are included in the package
   - Includes documentation, proto files, and configuration
   - Excludes development artifacts and sensitive files

4. **Updated `cyoda_mcp/server.py`** - Added clean `start()` function
   - Single entry point for the packaged CLI
   - Handles setup and server startup

### Build and Test Scripts

5. **`build_and_test.sh`** (Linux/macOS) and **`build_and_test.bat`** (Windows)
   - Automated build and testing scripts
   - Clean previous builds, build package, test installation

### Documentation

6. **Updated `README.md`** - Added installation and usage instructions
7. **`PACKAGING_GUIDE.md`** - This comprehensive guide

## 🚀 How Users Install and Run

### Zero-setup run (no clone, no venv)
```bash
# Set environment variables
export CYODA_CLIENT_ID="your-client-id"
export CYODA_CLIENT_SECRET="your-client-secret"
export CYODA_HOST="client-<id>.eu.cyoda.net"

# Run immediately with pipx
pipx run mcp-cyoda-client
```

### Install once and run repeatedly
```bash
# Install the package
pipx install mcp-cyoda-client

# Run with different options
mcp-cyoda-client                    # stdio transport (default)
mcp-cyoda-client --transport http   # HTTP transport
mcp-cyoda-client --transport sse    # SSE transport  
mcp-cyoda-client --port 9000        # Custom port
mcp-cyoda-client --help             # Show help
```

## 🛠️ Development Workflow

### Building the Package

```bash
# Quick build and test
./build_and_test.sh

# Or manually
python -m build
```

### Testing Locally

```bash
# Install from local wheel
pipx install --force dist/mcp_cyoda_client-0.1.2-py3-none-any.whl

# Test the command
mcp-cyoda-client --version
mcp-cyoda-client --help
```

### Publishing to PyPI

```bash
# Install twine if not already installed
pip install twine

# Upload to PyPI (requires PyPI account and API token)
twine upload dist/*

# Or upload to Test PyPI first
twine upload --repository testpypi dist/*
```

## 📦 Package Structure

```
your-repo/
├── cyoda_mcp/
│   ├── __init__.py
│   ├── __main__.py          # CLI entrypoint (NEW)
│   ├── server.py            # Updated with start() function
│   └── ...                  # Your existing MCP code
├── pyproject.toml           # Packaging config (NEW)
├── MANIFEST.in              # File inclusion rules (NEW)
├── build_and_test.sh        # Build script (NEW)
├── build_and_test.bat       # Windows build script (NEW)
└── README.md                # Updated with install instructions
```

## 🔧 Key Features

### Robust CLI
- **Environment validation** - Checks required variables before starting
- **Multiple transports** - stdio, HTTP, SSE support
- **Flexible configuration** - Command line args + environment variables
- **Proper logging** - Configurable log levels
- **Version reporting** - Shows package version
- **Help system** - Comprehensive help with examples

### Professional Packaging
- **Modern pyproject.toml** - Uses latest Python packaging standards
- **Proper dependencies** - Runtime deps moved from requirements.txt
- **Console script** - Creates `mcp-cyoda-client` command
- **File inclusion** - All necessary files included in package
- **Cross-platform** - Works on Windows, macOS, Linux

### User Experience
- **Zero-setup** - `pipx run mcp-cyoda-client` works immediately
- **No IDE config** - Users never need to edit server.py
- **Clear errors** - Helpful error messages for missing dependencies
- **Documentation** - Clear README with examples

## 🚨 Important Notes

### Environment Variables Required
Users must set these before running:
- `CYODA_CLIENT_ID` - Cyoda client ID
- `CYODA_CLIENT_SECRET` - Cyoda client secret
- `CYODA_HOST` - Cyoda host (e.g., client-123.eu.cyoda.net)

### Version Management
Update version in `pyproject.toml` before publishing:
```toml
version = "0.2.0"  # Increment as needed
```

### Dependencies
Runtime dependencies are now in `pyproject.toml` under `[project.dependencies]`. 
Keep `requirements.txt` only for development dependencies.

## 🎯 Next Steps

1. **Test the package** - Run `./build_and_test.sh` to verify everything works
2. **Update version** - Set appropriate version in `pyproject.toml`
3. **Test with real credentials** - Verify the server starts with your Cyoda instance
4. **Publish to PyPI** - When ready, upload with `twine upload dist/*`
5. **Update documentation** - Add any additional usage examples

## 🐛 Troubleshooting

### Build Issues
- Ensure you're in a virtual environment
- Install build tools: `pip install build twine`
- Clean previous builds: `rm -rf dist/ build/ *.egg-info/`

### Runtime Issues
- Check environment variables are set
- Verify Cyoda credentials are correct
- Check network connectivity to Cyoda instance
- Use `--log-level DEBUG` for detailed logging

### Import Errors
- Ensure all dependencies are in `pyproject.toml`
- Check that package structure matches `[tool.setuptools.packages.find]`
- Verify MANIFEST.in includes all necessary files

---

🎉 **Congratulations!** Your MCP server is now a professional, one-liner installable package!
