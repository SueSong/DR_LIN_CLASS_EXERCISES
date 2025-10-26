@echo off
REM Database Connection Finder Script (Windows)
REM Searches for database connection details in a GraphQL API installation

setlocal enabledelayedexpansion

set TARGET_DIR=C:\ciuser\www\easiio-chatgpt-devai
set SCRIPT_NAME=Database Connection Finder

echo 🔍 %SCRIPT_NAME%
echo ==================================
echo Target Directory: %TARGET_DIR%
echo.

REM Check if target directory exists
if not exist "%TARGET_DIR%" (
    echo ❌ Target directory does not exist: %TARGET_DIR%
    echo Please verify the path and try again.
    echo.
    echo 💡 Common Windows paths to check:
    echo    • C:\inetpub\wwwroot\easiio-chatgpt-devai
    echo    • C:\xampp\htdocs\easiio-chatgpt-devai
    echo    • C:\wamp\www\easiio-chatgpt-devai
    echo    • C:\Users\%USERNAME%\Documents\easiio-chatgpt-devai
    pause
    exit /b 1
)

echo ✅ Target directory found
echo.

echo 🚀 Starting Database Connection Search...
echo.

REM Function to search for patterns in files
echo 🔎 Searching for Environment Files
echo =====================================
for /r "%TARGET_DIR%" %%f in (*.env* .env*) do (
    if exist "%%f" (
        echo 📄 %%f
        echo    Content preview:
        type "%%f" 2>nul | findstr /i "DATABASE DB_ MONGO POSTGRES MYSQL REDIS" | more +0
        echo.
    )
)

echo 🔎 Searching for Configuration Files
echo ====================================
for /r "%TARGET_DIR%" %%f in (*.config.* config.* settings.* *.settings.*) do (
    if exist "%%f" (
        echo 📄 %%f
        type "%%f" 2>nul | findstr /i "database db host user password port" | more +0
        echo.
    )
)

echo 🔎 Searching for Package.json Files
echo ===================================
for /r "%TARGET_DIR%" %%f in (package.json) do (
    if exist "%%f" (
        echo 📄 %%f
        echo    Database-related dependencies:
        type "%%f" 2>nul | findstr /i "mongo postgres mysql redis sqlite prisma typeorm sequelize"
        echo.
    )
)

echo 🔎 Searching for Docker Files
echo =============================
for /r "%TARGET_DIR%" %%f in (docker-compose* Dockerfile*) do (
    if exist "%%f" (
        echo 📄 %%f
        echo    Database-related content:
        type "%%f" 2>nul | findstr /i "database db mongo postgres mysql redis"
        echo.
    )
)

echo 🔎 Searching for JavaScript/TypeScript Files
echo ============================================
for /r "%TARGET_DIR%" %%f in (*.js *.ts) do (
    if exist "%%f" (
        findstr /l /i "DATABASE_URL DB_HOST connectionString mongoose.connect createConnection" "%%f" >nul 2>&1
        if !errorlevel! equ 0 (
            echo 📄 %%f
            findstr /n /i "DATABASE_URL DB_HOST connectionString mongoose.connect createConnection" "%%f"
            echo.
        )
    )
)

echo 🔎 Searching for JSON Configuration Files
echo =========================================
for /r "%TARGET_DIR%" %%f in (*.json) do (
    if exist "%%f" (
        findstr /l /i "host user password database port connectionString" "%%f" >nul 2>&1
        if !errorlevel! equ 0 (
            echo 📄 %%f
            findstr /n /i "host user password database port connectionString" "%%f"
            echo.
        )
    )
)

echo 🔎 Searching for YAML Files
echo ===========================
for /r "%TARGET_DIR%" %%f in (*.yml *.yaml) do (
    if exist "%%f" (
        findstr /l /i "database db host user password port" "%%f" >nul 2>&1
        if !errorlevel! equ 0 (
            echo 📄 %%f
            findstr /n /i "database db host user password port" "%%f"
            echo.
        )
    )
)

echo 🔎 Searching for Python Files
echo =============================
for /r "%TARGET_DIR%" %%f in (*.py) do (
    if exist "%%f" (
        findstr /l /i "DATABASE_URL SQLALCHEMY_DATABASE_URI pymongo psycopg2" "%%f" >nul 2>&1
        if !errorlevel! equ 0 (
            echo 📄 %%f
            findstr /n /i "DATABASE_URL SQLALCHEMY_DATABASE_URI pymongo psycopg2" "%%f"
            echo.
        )
    )
)

echo 🔎 Searching for PHP Files
echo ==========================
for /r "%TARGET_DIR%" %%f in (*.php) do (
    if exist "%%f" (
        findstr /l /i "DB_HOST DB_USER DB_PASSWORD mysqli PDO" "%%f" >nul 2>&1
        if !errorlevel! equ 0 (
            echo 📄 %%f
            findstr /n /i "DB_HOST DB_USER DB_PASSWORD mysqli PDO" "%%f"
            echo.
        )
    )
)

echo 📋 Search Summary
echo =================
echo ✅ Search completed for: %TARGET_DIR%
echo.
echo 🔍 What to look for in the results:
echo    • Environment files ^(.env, .env.local, etc.^)
echo    • Configuration files ^(config.js, settings.json, etc.^)
echo    • Docker compose files with database services
echo    • Connection strings in code files
echo    • Database URLs in environment variables
echo.
echo 💡 Common database connection patterns:
echo    • DATABASE_URL=postgresql://user:pass@host:port/dbname
echo    • MONGODB_URI=mongodb://user:pass@host:port/dbname
echo    • DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT
echo.
echo 🔒 Note: Some files may require elevated permissions to read.
echo If you see access denied errors, try running as Administrator.
echo.
pause

