# 🚀 Server Management Commands

Quick reference for starting and managing all Exercise 5 servers.

## 🎯 **One-Command Server Management**

### Start All Servers
```bash
# Option 1: Direct script execution
./start-all-servers.sh

# Option 2: Using npm
npm run start:all
# or
npm run servers:start
```

### Stop All Servers
```bash
# Option 1: Direct script execution
./stop-all-servers.sh

# Option 2: Using npm
npm run stop:all
# or
npm run servers:stop
```

### Check Server Status
```bash
npm run servers:status
```

## 🔧 **Individual Server Commands**

### Trading Agent (Exercise 5)
```bash
# Start trading agent only
npm run start:trading

# Start with observability
npm run exercise5
```

### Original API (Exercise 1-4)
```bash
# Start original API only
npm run start:api
```

### Observability Stack
```bash
# Start Jaeger, Prometheus, Grafana
npm run observability:start

# Stop observability stack
npm run observability:stop

# View logs
npm run observability:logs
```

## 🌐 **Access URLs**

Once servers are running:

| Service | URL | Description |
|---------|-----|-------------|
| **Trading Agent Chat** | http://localhost:8001 | Main Exercise 5 interface |
| **Trading Agent API** | http://localhost:8001/docs | FastAPI documentation |
| **Original API** | http://localhost:8000/docs | Exercise 1-4 API |
| **Jaeger Tracing** | http://localhost:16686 | OpenTelemetry traces |
| **Prometheus** | http://localhost:9090 | Metrics collection |
| **Grafana** | http://localhost:3001 | Dashboards (admin/admin) |

## 🧪 **Quick Tests**

### Health Checks
```bash
# Trading Agent
curl http://localhost:8001/health

# Original API
curl http://localhost:8000/health
```

### Trading Agent Features
```bash
# Get stock quote
curl -X POST http://localhost:8001/quotes \
  -H "Content-Type: application/json" \
  -d '{"symbols":["AAPL"],"user_id":"test"}'

# Execute trade
curl -X POST http://localhost:8001/trades \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","action":"BUY","amount":1000,"user_id":"test"}'

# Get portfolio
curl -X POST http://localhost:8001/portfolio \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test"}'
```

## 🛠️ **Development Commands**

### Setup (First Time)
```bash
# Install all dependencies
npm run setup

# Setup specific components
npm run setup:trading
npm run setup:api
npm run setup:web
```

### Development Mode
```bash
# Start in development mode with hot reloading
npm run dev:trading
npm run dev:api
npm run dev:web
```

### Testing
```bash
# Run all tests
npm test

# Test specific components
npm run test:trading
npm run test:api
npm run test:web
```

### Cleanup
```bash
# Clean all build artifacts
npm run clean

# Clean specific components
npm run clean:trading
npm run clean:api
npm run clean:web
```

## 🐳 **Docker Commands**

### Direct Docker Compose
```bash
# Start all Docker services
docker-compose up -d

# Stop all Docker services
docker-compose down

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart jaeger
```

### Container Management
```bash
# View running containers
docker ps

# View all containers (including stopped)
docker ps -a

# Remove all containers and volumes
docker-compose down -v --remove-orphans
```

## 🔍 **Troubleshooting**

### Port Conflicts
```bash
# Check what's using a port
lsof -i :8001
# or
netstat -tulpn | grep 8001

# Kill process on port
kill -9 $(lsof -ti:8001)
```

### Log Files
```bash
# Trading Agent logs (when using start-all-servers.sh)
tail -f /tmp/trading-agent.log

# Original API logs
tail -f /tmp/api-server.log

# Docker service logs
docker-compose logs -f jaeger
docker-compose logs -f prometheus
```

### Reset Everything
```bash
# Stop all servers
./stop-all-servers.sh

# Clean everything
npm run clean

# Reset Docker
docker-compose down -v --remove-orphans

# Start fresh
./start-all-servers.sh
```

## 📊 **Service Dependencies**

```
Observability Stack (Optional)
├── Jaeger (Port 16686)
├── Prometheus (Port 9090)
└── Grafana (Port 3001)

Trading Agent (Port 8001)
├── Depends on: PostgreSQL (optional)
├── Uses: OpenTelemetry → Jaeger
└── Features: 6 tools, chat UI, API

Original API (Port 8000)
├── Depends on: OpenTelemetry libraries
├── Uses: OpenTelemetry → Jaeger
└── Features: HTTP fetch, DB query, file ops
```

## 🎯 **Recommended Workflow**

### For Demos
1. `./start-all-servers.sh` - Start everything
2. Open http://localhost:8001 - Use the chat interface
3. Open http://localhost:16686 - View traces in Jaeger
4. `./stop-all-servers.sh` - Clean shutdown

### For Development
1. `npm run setup` - First time setup
2. `npm run dev:trading` - Development mode
3. Make changes and test
4. `npm run clean` - Clean when needed

### For Testing
1. `npm run servers:status` - Check current status
2. `npm test` - Run test suite
3. Manual testing via chat UI or curl commands

Happy coding! 🚀
