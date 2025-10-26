# AI Agent Training Class - Monorepo

A comprehensive monorepo for AI Agent Training Class containing FastAPI backend with advanced tools and Next.js frontend with agent console.

## 🏗️ Architecture

```
monorepo/
├── apps/
│   ├── api/                    # FastAPI Backend
│   │   ├── tools/              # Tool implementations
│   │   │   ├── http_fetch.py   # HTTP client with retry/rate limiting
│   │   │   ├── db_query.py     # Safe database queries
│   │   │   └── file_ops.py     # Sandboxed file operations
│   │   ├── observability/      # OpenTelemetry setup
│   │   │   └── otel.py         # Tracing and metrics
│   │   ├── tests/              # Comprehensive test suite
│   │   └── app.py              # Main FastAPI application
│   └── web/                    # Next.js Frontend
│       └── src/                # Agent console (Week 4 enhancement)
└── packages/
    └── agent/                  # Shared agent package
        ├── schema/             # Pydantic schemas
        └── router/             # Tool registry and retry logic
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+**
- **Node.js 18+**
- **npm 8+**

### Installation

1. **Clone and setup the monorepo:**
   ```bash
   cd monorepo
   npm install
   npm run setup
   ```

2. **Start development servers:**
   ```bash
   npm run dev
   ```

   This starts:
   - FastAPI backend on `http://localhost:8000`
   - Next.js frontend on `http://localhost:3000`

### Individual Services

**Backend only:**
```bash
cd apps/api
pip install -r requirements.txt
python -m uvicorn app:app --reload
```

**Frontend only:**
```bash
cd apps/web
npm install
npm run dev
```

## 🛠️ Tools & Features

### HTTP Fetch Tool
- ✅ Timeout protection (30s default)
- ✅ Exponential backoff retry (3 attempts)
- ✅ Rate limiting (10 req/sec default)
- ✅ User-Agent identification
- ✅ Private IP blocking
- ✅ Request/response validation

### Database Query Tool
- ✅ Read-only SQL whitelist
- ✅ Parameter schema validation
- ✅ Query sanitization
- ✅ Connection pooling
- ✅ SQLite demo database

### File Operations Tool
- ✅ Workspace sandbox protection
- ✅ Path traversal prevention
- ✅ File size limits (10MB default)
- ✅ Extension filtering
- ✅ CRUD operations (read, write, list, delete, copy, move, mkdir)

### Observability
- ✅ OpenTelemetry tracing
- ✅ Metrics collection
- ✅ Span attributes (tool.name, retries, latency_ms, status)
- ✅ Console and Jaeger exporters
- ✅ Auto-instrumentation (FastAPI, HTTPX, SQLAlchemy)

## 🧪 Testing

### Run all tests:
```bash
npm run test
```

### Backend tests (pytest + Hypothesis):
```bash
cd apps/api
python -m pytest tests/ -v
```

### Test coverage includes:
- Unit tests for all tools
- Property-based testing with Hypothesis
- Integration tests for API endpoints
- Mock external dependencies

## 📊 API Endpoints

### Health & Status
- `GET /` - Basic health check
- `GET /health` - Detailed health status

### Tool Endpoints
- `POST /tools/http-fetch` - HTTP fetch operations
- `POST /tools/db-query` - Database queries
- `POST /tools/file-ops` - File operations

### Example Usage

**HTTP Fetch:**
```bash
curl -X POST http://localhost:8000/tools/http-fetch \
  -H "Content-Type: application/json" \
  -d '{"url": "https://api.github.com/users/octocat"}'
```

**Database Query:**
```bash
curl -X POST http://localhost:8000/tools/db-query \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT * FROM users WHERE age > 25"}'
```

**File Operations:**
```bash
curl -X POST http://localhost:8000/tools/file-ops \
  -H "Content-Type: application/json" \
  -d '{"operation": "write", "path": "test.txt", "content": "Hello World!"}'
```

## 🎯 Agent Console (Week 4 Preview)

The Next.js frontend provides a modern agent console with:

### Current Features (Week 1)
- 📊 Real-time tool execution logs
- 📈 Performance metrics dashboard
- 🔧 Tool configuration overview
- 🎨 Modern UI with Tailwind CSS

### Coming in Week 4
- 💬 Interactive agent chat interface
- 🛠️ Tool execution playground
- 📊 Advanced monitoring and analytics
- 🔄 Visual workflow builder

## 🏗️ Development

### Project Structure

**Backend (`apps/api/`):**
- `app.py` - FastAPI application with CORS and lifecycle management
- `tools/` - Tool implementations with comprehensive error handling
- `observability/` - OpenTelemetry setup with custom metrics
- `tests/` - pytest test suite with fixtures and property-based testing

**Frontend (`apps/web/`):**
- Modern Next.js 14 with App Router
- TypeScript for type safety
- Tailwind CSS for styling
- Radix UI components for accessibility

**Shared Package (`packages/agent/`):**
- `schema/` - Pydantic models with JSON Schema generation
- `router/` - Tool registry with permissions and retry logic

### Code Quality

**Backend:**
- Type hints throughout
- Comprehensive error handling
- Structured logging
- Security best practices

**Frontend:**
- TypeScript strict mode
- ESLint configuration
- Component-based architecture
- Responsive design

## 🔒 Security Features

- **Path Traversal Protection** - Prevents access outside workspace
- **SQL Injection Prevention** - Whitelist-based query validation
- **Private IP Blocking** - Prevents SSRF attacks
- **File Extension Filtering** - Blocks dangerous file types
- **Rate Limiting** - Prevents abuse
- **Input Validation** - Pydantic schema validation

## 📈 Monitoring & Observability

### Metrics Collected
- Tool execution counts
- Success/error rates
- Response times
- Retry attempts
- Resource usage

### Tracing
- End-to-end request tracing
- Tool execution spans
- Database query tracing
- HTTP request tracing

### Logging
- Structured JSON logs
- Correlation IDs
- Error tracking
- Performance monitoring

## 🚀 Deployment

### Environment Variables
```bash
# API Configuration
OTEL_SERVICE_NAME=ai-agent-training-api
OTEL_SERVICE_VERSION=1.0.0
JAEGER_ENDPOINT=http://localhost:14268/api/traces
OTEL_CONSOLE_EXPORT=true

# Database
DATABASE_URL=sqlite:///data/demo.db

# Security
WORKSPACE_ROOT=/app/workspace
MAX_FILE_SIZE=10485760
```

### Docker Support (Coming Soon)
- Multi-stage builds
- Production optimizations
- Health checks
- Resource limits

## 🤝 Contributing

1. Follow the existing code style
2. Add tests for new features
3. Update documentation
4. Ensure all tests pass

## 📚 Learning Objectives

This monorepo demonstrates:

1. **Tool Architecture** - Modular, testable tool implementations
2. **Security Practices** - Input validation, sandboxing, rate limiting
3. **Observability** - Comprehensive monitoring and tracing
4. **Testing Strategies** - Unit, integration, and property-based testing
5. **Modern Development** - TypeScript, async/await, type safety
6. **API Design** - RESTful endpoints with proper error handling

## 🔮 Roadmap

### Week 2: Advanced Tool Development
- Custom tool creation
- Tool composition
- Advanced error handling

### Week 3: Agent Intelligence
- LLM integration
- Tool selection logic
- Context management

### Week 4: Production Console
- Full agent chat interface
- Workflow automation
- Advanced monitoring

---

**Built for AI Agent Training Class** 🤖✨
