#!/bin/bash

# Database Connection Finder Script
# Searches for database connection details in a GraphQL API installation

set -e

TARGET_DIR="/home/ciuser/www/easiio-chatgpt-devai"
SCRIPT_NAME="Database Connection Finder"

echo "🔍 $SCRIPT_NAME"
echo "=================================="
echo "Target Directory: $TARGET_DIR"
echo ""

# Check if target directory exists
if [ ! -d "$TARGET_DIR" ]; then
    echo "❌ Target directory does not exist: $TARGET_DIR"
    echo "Please verify the path and try again."
    exit 1
fi

echo "✅ Target directory found"
echo ""

# Function to search for patterns and display results
search_pattern() {
    local pattern="$1"
    local description="$2"
    local files_found=0
    
    echo "🔎 Searching for: $description"
    echo "Pattern: $pattern"
    echo "----------------------------------------"
    
    # Search in common file types
    find "$TARGET_DIR" -type f \( \
        -name "*.env*" -o \
        -name "*.config.*" -o \
        -name "*.json" -o \
        -name "*.js" -o \
        -name "*.ts" -o \
        -name "*.py" -o \
        -name "*.php" -o \
        -name "*.yml" -o \
        -name "*.yaml" -o \
        -name "*.toml" -o \
        -name "*.ini" -o \
        -name "*.conf" -o \
        -name "docker-compose*" -o \
        -name "Dockerfile*" -o \
        -name "*.sql" \
    \) 2>/dev/null | while read -r file; do
        if grep -l "$pattern" "$file" 2>/dev/null; then
            echo "📁 File: $file"
            grep -n --color=always "$pattern" "$file" 2>/dev/null | head -5
            echo ""
            files_found=$((files_found + 1))
        fi
    done
    
    if [ $files_found -eq 0 ]; then
        echo "❌ No matches found"
    fi
    echo ""
}

# Function to search for database-related files
search_db_files() {
    echo "📂 Database-related Files"
    echo "========================="
    
    find "$TARGET_DIR" -type f \( \
        -name "*database*" -o \
        -name "*db*" -o \
        -name "*sql*" -o \
        -name "*mongo*" -o \
        -name "*redis*" -o \
        -name "*postgres*" -o \
        -name "*mysql*" \
    \) 2>/dev/null | head -20 | while read -r file; do
        echo "📄 $file"
    done
    echo ""
}

# Function to search for environment files
search_env_files() {
    echo "🌍 Environment Files"
    echo "==================="
    
    find "$TARGET_DIR" -type f -name "*.env*" 2>/dev/null | while read -r file; do
        echo "📄 $file"
        if [ -r "$file" ]; then
            echo "   Content preview:"
            head -10 "$file" 2>/dev/null | sed 's/^/   /'
        else
            echo "   (Permission denied)"
        fi
        echo ""
    done
}

# Function to search for configuration files
search_config_files() {
    echo "⚙️  Configuration Files"
    echo "======================"
    
    find "$TARGET_DIR" -type f \( \
        -name "config.*" -o \
        -name "*.config.*" -o \
        -name "settings.*" -o \
        -name "*.settings.*" \
    \) 2>/dev/null | head -10 | while read -r file; do
        echo "📄 $file"
        if [ -r "$file" ]; then
            echo "   Content preview:"
            head -5 "$file" 2>/dev/null | sed 's/^/   /'
        fi
        echo ""
    done
}

# Start searching
echo "🚀 Starting Database Connection Search..."
echo ""

# Search for common database connection patterns
search_pattern "DATABASE_URL\|DB_HOST\|DB_USER\|DB_PASSWORD\|DB_NAME\|DB_PORT" "Database Environment Variables"

search_pattern "mongodb://\|postgresql://\|mysql://\|redis://\|sqlite:" "Database Connection URLs"

search_pattern "host.*=\|user.*=\|password.*=\|database.*=\|port.*=" "Database Connection Parameters"

search_pattern "\"host\"\|\"user\"\|\"password\"\|\"database\"\|\"port\"" "JSON Database Configuration"

search_pattern "connectionString\|connection_string\|dbConfig\|databaseConfig" "Database Configuration Objects"

search_pattern "mongoose\.connect\|createConnection\|Pool\|Client" "Database Connection Code"

search_pattern "MONGO_URI\|MONGODB_URI\|POSTGRES_URI\|MYSQL_URI\|REDIS_URI" "Database URI Environment Variables"

# Search for specific files
search_db_files
search_env_files
search_config_files

# Search for Docker configurations
echo "🐳 Docker Configurations"
echo "========================"
find "$TARGET_DIR" -name "docker-compose*" -o -name "Dockerfile*" 2>/dev/null | while read -r file; do
    echo "📄 $file"
    if [ -r "$file" ]; then
        echo "   Database-related content:"
        grep -n -i "database\|db\|mongo\|postgres\|mysql\|redis" "$file" 2>/dev/null | head -5 | sed 's/^/   /'
    fi
    echo ""
done

# Search for package.json and dependencies
echo "📦 Package Dependencies"
echo "======================"
find "$TARGET_DIR" -name "package.json" 2>/dev/null | while read -r file; do
    echo "📄 $file"
    if [ -r "$file" ]; then
        echo "   Database-related dependencies:"
        grep -A 20 -B 5 "dependencies\|devDependencies" "$file" 2>/dev/null | \
        grep -i "mongo\|postgres\|mysql\|redis\|sqlite\|prisma\|typeorm\|sequelize" | \
        head -10 | sed 's/^/   /'
    fi
    echo ""
done

# Search for GraphQL schema files
echo "🔗 GraphQL Schema Files"
echo "======================"
find "$TARGET_DIR" -name "*.graphql" -o -name "*.gql" -o -name "*schema*" 2>/dev/null | head -10 | while read -r file; do
    echo "📄 $file"
done
echo ""

# Summary
echo "📋 Search Summary"
echo "================="
echo "✅ Search completed for: $TARGET_DIR"
echo ""
echo "🔍 What to look for in the results:"
echo "   • Environment files (.env, .env.local, etc.)"
echo "   • Configuration files (config.js, settings.json, etc.)"
echo "   • Docker compose files with database services"
echo "   • Connection strings in code files"
echo "   • Database URLs in environment variables"
echo ""
echo "💡 Common database connection patterns:"
echo "   • DATABASE_URL=postgresql://user:pass@host:port/dbname"
echo "   • MONGODB_URI=mongodb://user:pass@host:port/dbname"
echo "   • DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT"
echo ""
echo "🔒 Note: Some files may require elevated permissions to read."
echo "If you see 'Permission denied', try running with sudo."

