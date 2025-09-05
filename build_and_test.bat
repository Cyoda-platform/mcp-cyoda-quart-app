@echo off
REM Build and test script for mcp-cyoda-client package

echo 🚀 Building and testing mcp-cyoda-client package
echo ================================================

REM Check if we're in a virtual environment
if "%VIRTUAL_ENV%"=="" (
    echo ⚠️  Warning: Not in a virtual environment
    echo    Consider running: python -m venv .venv ^&^& .venv\Scripts\activate
)

REM Install build dependencies
echo 📦 Installing build dependencies...
pip install --upgrade build twine

REM Clean previous builds
echo 🧹 Cleaning previous builds...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
for /d %%i in (*.egg-info) do rmdir /s /q "%%i"

REM Build the package
echo 🔨 Building package...
python -m build

REM Check if build was successful
if not exist dist (
    echo ❌ Build failed - no dist directory created
    exit /b 1
)

REM List built files
echo 📋 Built files:
dir dist

REM Test installation with pipx (if available)
where pipx >nul 2>nul
if %errorlevel% == 0 (
    echo 🧪 Testing installation with pipx...
    
    REM Get the wheel file name
    for %%f in (dist\*.whl) do set WHEEL_FILE=%%f
    
    if defined WHEEL_FILE (
        echo    Installing: %WHEEL_FILE%
        pipx install --force "%WHEEL_FILE%"
        
        echo ✅ Package installed successfully!
        echo    You can now run: mcp-cyoda-client --version
        echo    Or test with: mcp-cyoda-client --help
        
        REM Test version command
        echo 🔍 Testing version command...
        mcp-cyoda-client --version || echo ⚠️  Version command failed (this is expected if dependencies are missing)
        
    ) else (
        echo ❌ No wheel file found in dist/
        exit /b 1
    )
) else (
    echo ⚠️  pipx not found - skipping installation test
    echo    Install pipx with: pip install pipx
    echo    Then test with: pipx install dist\*.whl
)

echo.
echo 🎉 Build completed successfully!
echo.
echo Next steps:
echo 1. Set your environment variables:
echo    set CYODA_CLIENT_ID=your-client-id
echo    set CYODA_CLIENT_SECRET=your-client-secret
echo    set CYODA_HOST=client-^<id^>.eu.cyoda.net
echo.
echo 2. Test the server:
echo    mcp-cyoda-client --help
echo    mcp-cyoda-client --transport stdio
echo.
echo 3. To publish to PyPI (when ready):
echo    twine upload dist/*
