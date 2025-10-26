# Exercise 5: AI Stock Trading Agent

A comprehensive stock trading agent that demonstrates all Exercise 1-6 skills in a real-world application.

## 🎯 **Exercise Skills Demonstrated**

### **Exercise 1: Typed Tools with Pydantic**
- ✅ **Comprehensive Input/Output Schemas** - All tools use Pydantic models for validation
- ✅ **Good vs Bad Input Demo** - `/demo/validate-input` endpoint shows validation in action
- ✅ **Type Safety** - Full type checking with proper error messages

### **Exercise 2: Tool Registry with Metadata**
- ✅ **Central Registry** - All tools registered with metadata and permissions
- ✅ **Tool Discovery** - `/tools` endpoint lists all available tools
- ✅ **Rich Metadata** - Description, category, version, permissions, statistics

### **Exercise 3: Add Reliability (Retry/Timeout)**
- ✅ **Exponential Backoff** - With jitter for all external API calls
- ✅ **Circuit Breaker** - Prevents cascading failures
- ✅ **Configurable Retry** - Different strategies for different operations
- ✅ **Timeout Handling** - Prevents hanging operations

### **Exercise 4: Observability with OpenTelemetry**
- ✅ **Distributed Tracing** - Full trace coverage with Jaeger integration
- ✅ **Rich Span Attributes** - tool.name, latency_ms, status, retries
- ✅ **Error Tracking** - Exception details and stack traces
- ✅ **Performance Monitoring** - Execution time and success rates

### **Exercise 5: Permission & Sandboxing**
- ✅ **Permission Levels** - PUBLIC, AUTHENTICATED, TRADER, ADMIN, SYSTEM
- ✅ **Sandboxed Execution** - File operations restricted to safe directories
- ✅ **Rate Limiting** - Per-tool and per-user limits
- ✅ **Operation Allowlists** - Granular control over allowed operations

### **Exercise 6: Full Agent Flow**
- ✅ **Complete Pipeline** - User Query → Agent → Registry → Tools → Results → Logs + Traces
- ✅ **AI-Powered Decisions** - LLM integration for trading recommendations
- ✅ **End-to-End Workflow** - Portfolio analysis → Market data → AI recommendations → Trade execution → Reporting

## 🏗 **Architecture Overview**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │────│  Tool Registry  │────│   Trading Tools │
│  (Exercise 6)   │    │  (Exercise 2)   │    │  (Exercise 1)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐             │
         │              │  Reliability    │             │
         └──────────────│  (Exercise 3)   │─────────────┘
                        └─────────────────┘
                                 │
                        ┌─────────────────┐
                        │ Observability   │
                        │ (Exercise 4)    │
                        └─────────────────┘
                                 │
                        ┌─────────────────┐
                        │  Permissions    │
                        │ (Exercise 5)    │
                        └─────────────────┘
```

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.8+
- Docker & Docker Compose
- PostgreSQL (via Docker)
- Optional: OpenAI or Anthropic API key for LLM features

### **1. Start Observability Stack**
```bash
# Start PostgreSQL, Jaeger, Prometheus, Grafana
npm run observability:start
```

### **2. Start Trading Agent**
```bash
# Option A: Using npm script
npm run start:trading

# Option B: Direct execution
cd apps/trading-agent
./run.sh
```

### **3. Run Complete Demo**
```bash
# Demonstrates all Exercise 1-6 skills
npm run demo:trading
```

## 📊 **Key Endpoints**

### **Core Trading Operations**
- `POST /quotes` - Get stock quotes (Exercise 1: Typed Tools)
- `POST /trade` - Execute trades (Exercise 5: Permissions)
- `GET /portfolio` - View portfolio positions
- `POST /recommendations` - Get AI trading recommendations (Exercise 6: Full Agent Flow)

### **Agent Orchestration**
- `POST /agent/auto-trade` - Complete AI trading workflow (Exercise 6)

### **Tool Registry & Metadata**
- `GET /tools` - List all registered tools (Exercise 2)
- `GET /tools/{name}` - Get detailed tool information
- `GET /stats` - Registry statistics and performance metrics

### **File Operations & Reporting**
- `POST /reports/daily` - Generate daily trading reports (Exercise 2: File Operations)
- `POST /files` - Sandboxed file operations (Exercise 5: Sandboxing)

### **Demonstrations**
- `POST /demo/validate-input` - Exercise 1 validation demo
- `GET /health` - System health with observability

## 🎮 **Demo Scenarios**

### **Exercise 1: Input Validation Demo**
```bash
curl -X POST http://localhost:8001/demo/validate-input \
  -H "Content-Type: application/json" \
  -d '{}'
```

### **Exercise 2: Tool Registry Exploration**
```bash
# List all tools
curl http://localhost:8001/tools

# Get detailed tool info
curl http://localhost:8001/tools/stock_quote
```

### **Exercise 3: Reliability Testing**
```bash
# This will trigger retry logic for invalid symbols
curl -X POST http://localhost:8001/quotes \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["AAPL", "INVALID_SYMBOL", "GOOGL"]}'
```

### **Exercise 4: Observability**
- **Jaeger UI**: http://localhost:16686
- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090

### **Exercise 5: Permission Testing**
```bash
# Allowed file operation
curl -X POST http://localhost:8001/files \
  -H "Content-Type: application/json" \
  -d '{"operation": "write", "file_path": "test.txt", "content": "Hello World"}'

# Blocked operation (delete not allowed)
curl -X POST http://localhost:8001/files \
  -H "Content-Type: application/json" \
  -d '{"operation": "delete", "file_path": "test.txt"}'
```

### **Exercise 6: Full Agent Flow**
```bash
curl -X POST "http://localhost:8001/agent/auto-trade?user_id=default_trader&risk_tolerance=moderate"
```

## 🛠 **Configuration**

### **Environment Variables**
```bash
# Database
DATABASE_URL="postgresql://trader:trading123@localhost:5432/trading_db"

# LLM Integration (optional)
OPENAI_API_KEY="your-openai-key"
ANTHROPIC_API_KEY="your-anthropic-key"
LLM_PROVIDER="openai"  # or "anthropic" or leave empty for mock

# Observability
OTEL_SERVICE_NAME="trading-agent"
OTEL_SERVICE_VERSION="1.0.0"

# File Operations
REPORTS_DIR="reports"
```

### **Database Schema**
The agent uses PostgreSQL with the following key tables:
- `portfolio` - Current stock holdings
- `cash_balance` - Available cash
- `transactions` - All trading history
- `daily_reports` - Generated reports
- `stock_quotes` - Cached market data
- `agent_decisions` - LLM decision logs

## 🔧 **Tool Categories**

### **Market Data Tools**
- `stock_quote` - Real-time stock quotes with retry logic

### **Trading Tools**
- `execute_trade` - Buy/sell with portfolio validation (TRADER permission required)

### **Portfolio Tools**
- `get_portfolio` - Current positions and performance

### **Analysis Tools**
- `get_trading_recommendations` - AI-powered recommendations (LLM integration)

### **Reporting Tools**
- `generate_daily_report` - Comprehensive daily reports
- `file_operations` - Sandboxed file access

## 📈 **AI Trading Logic**

The agent follows this decision-making process:

1. **Portfolio Analysis** - Current positions, cash allocation, performance
2. **Market Data Collection** - Real-time quotes for major stocks
3. **AI Analysis** - LLM processes market conditions and portfolio state
4. **Risk Assessment** - Evaluates recommendations against risk tolerance
5. **Trade Execution** - Executes high-confidence recommendations
6. **Reporting** - Generates comprehensive daily reports

### **Risk Management**
- Maintains 10% cash allocation target
- Maximum 20% position size per stock
- Minimum $1,000 per trade
- Confidence threshold of 60% for execution

## 🔍 **Monitoring & Debugging**

### **Jaeger Traces**
View detailed execution traces at http://localhost:16686:
- Service dependencies
- Tool execution times
- Error propagation
- Retry attempts

### **Application Logs**
```bash
# View real-time logs
docker-compose logs -f trading-postgres
docker-compose logs -f jaeger
```

### **Performance Metrics**
```bash
# Get registry statistics
curl http://localhost:8001/stats
```

## 🧪 **Testing**

### **Manual Testing**
```bash
# Run complete demo
python demo_all_exercises.py

# Test individual components
curl http://localhost:8001/health
curl http://localhost:8001/tools
```

### **Load Testing**
```bash
# Generate multiple concurrent requests
for i in {1..10}; do
  curl -X POST http://localhost:8001/quotes \
    -H "Content-Type: application/json" \
    -d '{"symbols": ["AAPL", "GOOGL"]}' &
done
```

## 🎓 **Learning Outcomes**

After completing Exercise 5, you will have hands-on experience with:

1. **Production-Ready Tool Design** - Type safety, validation, error handling
2. **Scalable Architecture** - Registry pattern, dependency injection, modularity
3. **Reliability Engineering** - Retry strategies, circuit breakers, timeouts
4. **Observability Best Practices** - Distributed tracing, metrics, logging
5. **Security Implementation** - Permissions, sandboxing, input validation
6. **AI Agent Orchestration** - LLM integration, decision workflows, automation

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Database Connection Failed**
   ```bash
   # Ensure PostgreSQL is running
   docker-compose ps postgres
   
   # Check logs
   docker-compose logs postgres
   ```

2. **LLM Integration Not Working**
   - Set `LLM_PROVIDER=""` to use mock responses
   - Verify API keys are set correctly

3. **Observability Stack Issues**
   ```bash
   # Restart observability services
   npm run observability:stop
   npm run observability:start
   ```

4. **Port Conflicts**
   - Trading Agent: 8001
   - Original API: 8000
   - PostgreSQL: 5432
   - Jaeger UI: 16686

## 📚 **Next Steps**

1. **Extend Tool Registry** - Add more trading tools (options, futures, crypto)
2. **Enhanced AI** - Multi-model ensemble, backtesting, paper trading
3. **Advanced Observability** - Custom metrics, alerting, dashboards
4. **Production Deployment** - Kubernetes, CI/CD, monitoring
5. **Web Interface** - React dashboard for portfolio management

---

**🎯 This Exercise 5 demonstrates a complete, production-ready AI agent system that integrates all the skills from Exercises 1-6 in a real-world stock trading application.**
