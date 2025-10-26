# 🔍 Database Connection Finder

Scripts to find database connection details in the GraphQL API installation at `/home/ciuser/www/easiio-chatgpt-devai`.

## 📁 Available Scripts

### 1. **Python Script (Recommended)** 🐍
**File:** `find-db-connection.py`

**Features:**
- ✅ Cross-platform (Linux, Windows, macOS)
- 🔍 Advanced pattern matching with regex
- 🎯 Categorizes findings by type
- 🔒 Masks sensitive data (passwords)
- 📊 Analyzes package.json dependencies
- 💾 Can export results to JSON
- 🎨 Colored, formatted output

**Usage:**
```bash
# Basic usage (searches default directory)
python3 find-db-connection.py

# Search custom directory
python3 find-db-connection.py /path/to/your/project

# Save results to JSON file
python3 find-db-connection.py --output results.json

# Help
python3 find-db-connection.py --help
```

### 2. **Shell Script (Linux/macOS)** 🐧
**File:** `find-db-connection.sh`

**Features:**
- ✅ Native bash script for Unix systems
- 🔍 Searches common file types
- 📂 Organized by file type and pattern
- 🎯 Focused on environment and config files

**Usage:**
```bash
# Make executable (if needed)
chmod +x find-db-connection.sh

# Run the script
./find-db-connection.sh
```

### 3. **Windows Batch Script** 🪟
**File:** `find-db-connection.bat`

**Features:**
- ✅ Native Windows batch script
- 🔍 Searches for database patterns
- 📂 Organized file type searches
- 💡 Suggests common Windows paths

**Usage:**
```batch
REM Double-click the file or run from command prompt
find-db-connection.bat
```

## 🎯 What These Scripts Find

### 🌍 Environment Variables
- `DATABASE_URL`
- `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_PORT`
- `MONGODB_URI`, `POSTGRES_URI`, `MYSQL_URI`, `REDIS_URI`

### 🔗 Connection URLs
- `mongodb://user:pass@host:port/dbname`
- `postgresql://user:pass@host:port/dbname`
- `mysql://user:pass@host:port/dbname`
- `redis://user:pass@host:port/dbname`

### ⚙️ Configuration Files
- `.env`, `.env.local`, `.env.production`
- `config.js`, `config.json`, `settings.json`
- `docker-compose.yml`, `Dockerfile`
- `package.json` (database dependencies)

### 💻 Code Patterns
- `mongoose.connect()`
- `createConnection()`
- `new Pool()`, `new Client()`
- Database configuration objects

### 📦 Database Dependencies
- MongoDB: `mongoose`, `mongodb`
- PostgreSQL: `pg`, `postgres`, `typeorm`
- MySQL: `mysql`, `mysql2`, `sequelize`
- Redis: `redis`, `ioredis`
- ORM/ODM: `prisma`, `typeorm`, `sequelize`, `knex`

## 📂 File Types Searched

| Extension | Description |
|-----------|-------------|
| `.env*` | Environment files |
| `.config.*` | Configuration files |
| `.json` | JSON configuration |
| `.js`, `.ts` | JavaScript/TypeScript |
| `.py` | Python files |
| `.php` | PHP files |
| `.yml`, `.yaml` | YAML configuration |
| `.sql` | SQL scripts |
| `docker-compose*` | Docker configurations |
| `Dockerfile*` | Docker files |

## 🔒 Security Features

### Password Masking
The Python script automatically masks sensitive information:
```
Before: PASSWORD=mySecretPassword123
After:  PASSWORD=***MASKED***
```

### Safe File Reading
- Handles permission errors gracefully
- Skips binary files automatically
- Uses safe encoding with error handling

## 📊 Example Output

```
🔍 Database Connection Finder
==================================
Target Directory: /home/ciuser/www/easiio-chatgpt-devai

✅ Target directory found

📊 Analysis Results
==================================================
📁 Directory: /home/ciuser/www/easiio-chatgpt-devai
📄 Files analyzed: 156
🎯 Total matches: 23

🔍 ENV VARS
----------------------------------------
📄 .env (line 12)
   Match: DATABASE_URL=postgresql://***MASKED***@localhost:5432/chatgpt_db
   Context:
    10: # Database Configuration
    11: DB_HOST=localhost
>>> 12: DATABASE_URL=postgresql://***MASKED***@localhost:5432/chatgpt_db
    13: DB_PORT=5432
    14: 

📦 Database Dependencies
----------------------------------------
📄 package.json
   • mongoose: ^7.0.3
   • @prisma/client: ^4.12.0
   • redis: ^4.6.5
```

## 🚀 Quick Start Guide

1. **Choose your platform:**
   - **Linux/macOS:** Use `find-db-connection.py` or `find-db-connection.sh`
   - **Windows:** Use `find-db-connection.py` or `find-db-connection.bat`

2. **Run the script:**
   ```bash
   # Python (recommended for all platforms)
   python3 find-db-connection.py
   
   # Linux/macOS shell
   ./find-db-connection.sh
   
   # Windows batch
   find-db-connection.bat
   ```

3. **Review the output:**
   - Look for environment files (`.env`)
   - Check configuration files (`config.js`, etc.)
   - Examine Docker configurations
   - Review database dependencies in `package.json`

4. **Common locations to check:**
   - Root directory environment files
   - `config/` or `configs/` directories
   - `src/config/` for source configurations
   - Docker compose files
   - Backend/API directories

## 💡 Troubleshooting

### Permission Denied
```bash
# Linux/macOS: Run with elevated permissions
sudo python3 find-db-connection.py

# Windows: Run Command Prompt as Administrator
```

### Directory Not Found
Update the target directory in the script or pass it as an argument:
```bash
# Custom directory
python3 find-db-connection.py /path/to/your/project
```

### No Results Found
- Check if the directory path is correct
- Verify the application uses a database
- Look for alternative configuration methods (environment variables, external config services)
- Check if configurations are in a different location (parent directories, etc.)

## 🎯 Next Steps

Once you find the database connection details:

1. **Document the findings** - Note the database type, host, port, and database name
2. **Test the connection** - Use the found credentials to verify database access
3. **Update configurations** - Modify connection strings as needed for your environment
4. **Secure sensitive data** - Ensure passwords and keys are properly protected

Happy database hunting! 🕵️‍♂️

