#!/bin/bash
# Build and test script for mcp-cyoda-client package

set -e  # Exit on any error

echo "🚀 Building and testing mcp-cyoda-client package"
echo "================================================"

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Warning: Not in a virtual environment"
    echo "   Consider running: python -m venv .venv && source .venv/bin/activate"
fi

# Install build dependencies
echo "📦 Installing build dependencies..."
pip install --upgrade build twine

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info/

# Build the package
echo "🔨 Building package..."
python -m build

# Check if build was successful
if [ ! -d "dist" ]; then
    echo "❌ Build failed - no dist directory created"
    exit 1
fi

# List built files
echo "📋 Built files:"
ls -la dist/

# Test installation with pipx (if available)
if command -v pipx &> /dev/null; then
    echo "🧪 Testing installation with pipx..."
    
    # Get the wheel file name
    WHEEL_FILE=$(ls dist/*.whl | head -n 1)
    
    if [ -n "$WHEEL_FILE" ]; then
        echo "   Installing: $WHEEL_FILE"
        pipx install --force "$WHEEL_FILE"
        
        echo "✅ Package installed successfully!"
        echo "   You can now run: mcp-cyoda-client --version"
        echo "   Or test with: mcp-cyoda-client --help"
        
        # Test version command
        echo "🔍 Testing version command..."
        mcp-cyoda-client --version || echo "⚠️  Version command failed (this is expected if dependencies are missing)"
        
    else
        echo "❌ No wheel file found in dist/"
        exit 1
    fi
else
    echo "⚠️  pipx not found - skipping installation test"
    echo "   Install pipx with: pip install pipx"
    echo "   Then test with: pipx install dist/*.whl"
fi

echo ""
echo "🎉 Build completed successfully!"
echo ""
echo "Next steps:"
echo "1. Set your environment variables:"
echo "   export CYODA_CLIENT_ID='your-client-id'"
echo "   export CYODA_CLIENT_SECRET='your-client-secret'"
echo "   export CYODA_HOST='client-<id>.eu.cyoda.net'"
echo ""
echo "2. Test the server:"
echo "   mcp-cyoda-client --help"
echo "   mcp-cyoda-client --transport stdio"
echo ""
echo "3. To publish to PyPI (when ready):"
echo "   twine upload dist/*"
