# 🚀 Windows Setup Guide for Exercise 5

This guide provides Windows-specific batch scripts to run the AI Agent Training Exercise 5.

## 📋 Prerequisites

1. **Docker Desktop** - Download from [docker.com](https://www.docker.com/products/docker-desktop/)
2. **Python 3.8+** - Download from [python.org](https://www.python.org/downloads/)
3. **Node.js 18+** - Download from [nodejs.org](https://nodejs.org/)
4. **Git** - Download from [git-scm.com](https://git-scm.com/)

## 🎯 Quick Start (Recommended)

### Option 1: Start Everything at Once
```batch
# Run this from the monorepo directory
start-all-servers.bat
```

This script will:
- ✅ Check all prerequisites
- 🛑 Stop any existing servers
- 🔭 Start observability stack (Jaeger, Prometheus, Grafana)
- 🎯 Start Trading Agent server
- 🔧 Optionally start Original API server
- 🌐 Open the Trading Agent Chat UI in your browser

## 🔧 Individual Scripts

### 1. Setup Observability Stack
```batch
setup-observability.bat
```
Starts Jaeger, Prometheus, Grafana, PostgreSQL, and Redis in Docker containers.

### 2. Start Trading Agent (Exercise 5)
```batch
start-trading.bat
```
Starts the main Exercise 5 Trading Agent server at http://localhost:8001

### 3. Fix Original API Dependencies
```batch
setup-api-dependencies.bat
```
Installs missing OpenTelemetry dependencies for the Original API server.

## 🎮 Access Points

Once servers are running:

| Service | URL | Description |
|---------|-----|-------------|
| **Trading Agent Chat UI** | http://localhost:8001 | Main Exercise 5 interface |
| **Trading Agent API** | http://localhost:8001/docs | FastAPI documentation |
| **Jaeger Tracing** | http://localhost:16686 | View OpenTelemetry traces |
| **Prometheus** | http://localhost:9090 | Metrics collection |
| **Grafana** | http://localhost:3001 | Dashboards (admin/admin) |
| **Original API** | http://localhost:8000/docs | Exercise 1-4 API |

## 🧪 Testing Commands

Open Command Prompt and test:

```batch
# Health check
curl http://localhost:8001/health

# Get stock quote
curl -X POST http://localhost:8001/quotes -H "Content-Type: application/json" -d "{\"symbols\":[\"AAPL\"],\"user_id\":\"test\"}"

# Execute trade
curl -X POST http://localhost:8001/trades -H "Content-Type: application/json" -d "{\"symbol\":\"AAPL\",\"action\":\"BUY\",\"amount\":1000,\"user_id\":\"test\"}"
```

## 🛠️ Troubleshooting

### Docker Issues
- Make sure Docker Desktop is running
- Try restarting Docker Desktop
- Run `docker info` to verify Docker is working

### Port Conflicts
- Check if ports 8000, 8001, 3000, 5432, 6379, 9090, 16686 are free
- Use `netstat -an | findstr :8001` to check specific ports
- Kill processes: `taskkill /f /pid <PID>`

### Python/Dependencies Issues
- Make sure Python is in your PATH
- Try running `python --version` and `pip --version`
- If virtual environment fails, try running as Administrator

### Missing curl
If `curl` is not available, install it or use PowerShell:
```powershell
Invoke-RestMethod -Uri http://localhost:8001/health
```

## 🛑 Stopping Servers

### Stop All Services
```batch
# Stop Docker services
docker-compose down

# Or use the task manager to close server windows
```

### Stop Individual Services
- Close the Command Prompt windows running the servers
- Or press `Ctrl+C` in each server window

## 📊 Exercise 5 Features

The Windows setup includes all Exercise 5 features:

1. **Exercise 1**: Typed Tools with Pydantic validation
2. **Exercise 2**: Tool Registry with metadata and permissions
3. **Exercise 3**: Reliability with retry logic and circuit breakers
4. **Exercise 4**: Observability with OpenTelemetry tracing
5. **Exercise 5**: Permission system and sandboxing
6. **Exercise 6**: Full agent flow with LLM integration

## 🎯 Demo Flow

1. Run `start-all-servers.bat`
2. Open http://localhost:8001 in your browser
3. Try the chat interface:
   - Ask for stock quotes: "Get quotes for AAPL, GOOGL"
   - Request trades: "Buy 100 shares of AAPL"
   - Get AI recommendations: "What should I trade today?"
4. View traces at http://localhost:16686
5. Check metrics at http://localhost:9090

## 🆘 Support

If you encounter issues:

1. Check the Command Prompt windows for error messages
2. Verify all prerequisites are installed
3. Try running individual scripts to isolate the problem
4. Check Docker Desktop is running and healthy
5. Ensure no other applications are using the required ports

Happy coding! 🚀


