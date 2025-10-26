# 🤖 AI Trading Agent - Quick Start Guide

## 🚀 How to Start the Chat UI

### Option 1: From your current directory (class_1)
```bash
cd /Volumes/KINGSTON/vic_ai_trainning_class/class_1/monorepo/apps/trading-agent
source venv/bin/activate
python -m uvicorn app:app --host 0.0.0.0 --port 8001 --reload
```

### Option 2: From the monorepo directory
```bash
cd /Volumes/KINGSTON/vic_ai_trainning_class/class_1/monorepo
npm run start:trading
```

### Option 3: Using the shell script
```bash
cd /Volumes/KINGSTON/vic_ai_trainning_class/class_1/monorepo
bash start-trading.sh
```

## 🌐 Access the Chat UI

Once the server is running, open your browser to:
- **Main Chat Interface**: http://localhost:8001/
- **API Documentation**: http://localhost:8001/docs

## 🎯 New Trading Features

### 🤖 **AI Auto-Trading**
Let the AI analyze the market and execute trades automatically:
- **Command**: "Trade for me" or "Execute trades automatically"
- **What it does**: 
  - Gets current market data
  - Asks LLM for trading recommendations
  - Executes trades based on AI advice
  - Maintains 10% cash balance for flexibility
  - Shows detailed reasoning

### 💰 **Manual Trading**
Execute specific trades with natural language:
- **Buy Examples**: 
  - "Buy 100 shares of AAPL"
  - "Buy $1000 worth of GOOGL"
  - "Purchase 50 MSFT"
- **Sell Examples**:
  - "Sell 50 shares of AAPL"
  - "Sell all my GOOGL"
  - "Sell $500 worth of MSFT"

### 📊 **All Available Commands**
- `"Get quotes for AAPL, GOOGL"` - Stock quotes
- `"Show my portfolio"` - Portfolio overview
- `"Get AI trading recommendations"` - AI analysis without trading
- `"Trade for me"` - AI auto-trading
- `"Buy 100 shares of AAPL"` - Manual buy order
- `"Sell 50 GOOGL"` - Manual sell order
- `"Generate daily report"` - Trading summary
- `"Show available tools"` - System tools
- `"What's the system status?"` - Health check

## 🎮 Quick Action Buttons

The chat interface includes quick action buttons:
- 📊 **Stock Quotes** - Get market data
- 💼 **Portfolio** - View positions
- 🧠 **AI Advice** - Get recommendations
- 🤖 **Auto Trade** - Let AI trade for you
- 💰 **Buy Stock** - Execute buy order
- 📄 **Report** - Generate summary
- 🔧 **Tools** - Show system tools

## 🔧 System Features

### ✅ **What's Working**
- Real-time stock quotes (mock data)
- Portfolio management
- AI-powered trading recommendations
- Manual and automatic trade execution
- Comprehensive observability with OpenTelemetry
- Permission-based tool access
- Sandboxed file operations
- Retry logic and error handling

### ⚠️ **Current Limitations**
- Database connection needs setup (PostgreSQL role "trader")
- LLM integration in mock mode (needs OpenAI/Anthropic API key)
- Stock quotes are simulated (for demo purposes)

## 🎓 **Exercise Skills Demonstrated**

1. **Exercise 1**: Typed Tools with Pydantic validation
2. **Exercise 2**: Tool Registry with metadata and permissions
3. **Exercise 3**: Reliability with retry/timeout/circuit breakers
4. **Exercise 4**: OpenTelemetry observability and tracing
5. **Exercise 5**: Permission system and sandboxing
6. **Exercise 6**: Full AI agent workflow with chat interface

## 🎯 **Perfect for Class Demo!**

This trading agent showcases all the exercise skills in a real-world application with:
- Beautiful web-based chat interface
- Natural language processing
- AI-powered decision making
- Comprehensive error handling
- Full observability stack
- Production-ready architecture

**Happy Trading!** 🚀📈
