# 🤖 Exercise 6: RAG-Enhanced Chatbot with Knowledge Base

## 🎯 **Learning Objectives**

This exercise builds upon Exercise 2 to create a sophisticated RAG (Retrieval-Augmented Generation) chatbot system that demonstrates:

1. **Vector Database Integration** - PostgreSQL with pgvector extension
2. **Document Processing** - PDF and text file ingestion
3. **Semantic Search** - ChromaDB for similarity search
4. **RAG Pipeline** - Retrieval-Augmented Generation workflow
5. **Knowledge Management** - Admin console for content management
6. **Full-Stack Architecture** - FastAPI backend + React frontend
7. **Containerization** - Docker services with proper port management

## 🏗️ **System Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                    Exercise 6 RAG System                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   Admin Console │    │   Chat Frontend │                │
│  │   (React)       │    │   (React)       │                │
│  │   Port: 3002    │    │   Port: 3003    │                │
│  └─────────────────┘    └─────────────────┘                │
│           │                       │                        │
│           └───────────┬───────────┘                        │
│                       │                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              FastAPI Backend                            │ │
│  │              Port: 8002                                 │ │
│  │                                                         │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │ │
│  │  │   RAG       │  │ Knowledge   │  │ Document    │    │ │
│  │  │ Pipeline    │  │ Base API    │  │ Processing  │    │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘    │ │
│  └─────────────────────────────────────────────────────────┘ │
│           │                       │                        │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   ChromaDB      │    │  PostgreSQL     │                │
│  │   (Vector Store)│    │  + pgvector     │                │
│  │   Port: 8000    │    │  Port: 5433     │                │
│  └─────────────────┘    └─────────────────┘                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 📁 **Project Structure**

```
exercise_6/
├── README.md
├── docker-compose.yml
├── .env.example
├── .gitignore
│
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI application
│   │   ├── config.py          # Configuration settings
│   │   ├── database.py        # Database connections
│   │   │
│   │   ├── models/            # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── knowledge_base.py
│   │   │   ├── documents.py
│   │   │   └── qa_pairs.py
│   │   │
│   │   ├── schemas/           # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── knowledge_base.py
│   │   │   ├── documents.py
│   │   │   ├── qa_pairs.py
│   │   │   └── chat.py
│   │   │
│   │   ├── api/              # API routes
│   │   │   ├── __init__.py
│   │   │   ├── knowledge_base.py
│   │   │   ├── documents.py
│   │   │   ├── qa_pairs.py
│   │   │   └── chat.py
│   │   │
│   │   ├── services/         # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── document_processor.py
│   │   │   ├── vector_store.py
│   │   │   ├── rag_pipeline.py
│   │   │   └── llm_service.py
│   │   │
│   │   └── utils/           # Utilities
│   │       ├── __init__.py
│   │       ├── file_handler.py
│   │       └── embeddings.py
│   │
│   ├── requirements.txt
│   ├── Dockerfile
│   └── run.sh
│
├── frontend/                  # React Frontend
│   ├── admin/                # Admin Console
│   │   ├── package.json
│   │   ├── src/
│   │   │   ├── components/
│   │   │   │   ├── KnowledgeBase/
│   │   │   │   ├── Documents/
│   │   │   │   ├── QAPairs/
│   │   │   │   └── Dashboard/
│   │   │   ├── pages/
│   │   │   ├── services/
│   │   │   └── App.tsx
│   │   └── Dockerfile
│   │
│   └── chat/                 # Chat Interface
│       ├── package.json
│       ├── src/
│       │   ├── components/
│       │   │   ├── ChatInterface/
│       │   │   ├── MessageList/
│       │   │   └── InputBox/
│       │   ├── services/
│       │   └── App.tsx
│       └── Dockerfile
│
├── database/                 # Database initialization
│   ├── init.sql
│   └── migrations/
│
├── docs/                    # Documentation
│   ├── API.md
│   ├── SETUP.md
│   └── ARCHITECTURE.md
│
└── scripts/                # Utility scripts
    ├── setup.sh
    ├── start.sh
    └── cleanup.sh
```

## 🔧 **Technology Stack**

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL + pgvector** - Vector database for embeddings
- **ChromaDB** - Vector similarity search
- **SQLAlchemy** - ORM for database operations
- **Pydantic** - Data validation and serialization
- **LangChain** - RAG pipeline framework
- **OpenAI/Anthropic** - LLM integration
- **PyPDF2/pdfplumber** - PDF processing
- **sentence-transformers** - Text embeddings

### Frontend
- **React 18** - Modern React with hooks
- **TypeScript** - Type-safe JavaScript
- **Material-UI (MUI)** - Component library
- **React Query** - Data fetching and caching
- **React Router** - Client-side routing
- **Axios** - HTTP client

### Infrastructure
- **Docker & Docker Compose** - Containerization
- **Nginx** - Reverse proxy (optional)
- **Redis** - Caching (optional)

## 🚀 **Key Features**

### 1. **Knowledge Base Management**
- Upload PDF and text documents
- Automatic text extraction and chunking
- Metadata management (title, tags, categories)
- Document versioning and updates
- Bulk import/export capabilities

### 2. **Q&A Pair Management**
- Manual Q&A pair creation
- Bulk import from CSV/JSON
- Question variations and synonyms
- Answer templates and formatting
- Search and filter capabilities

### 3. **RAG Pipeline**
- Document chunking with overlap
- Embedding generation using sentence-transformers
- Vector similarity search with ChromaDB
- Context ranking and selection
- LLM-powered response generation
- Source attribution and citations

### 4. **Chat Interface**
- Real-time chat interface
- Message history and persistence
- Source document references
- Confidence scoring
- Feedback collection
- Export conversation history

### 5. **Admin Console**
- Dashboard with analytics
- Knowledge base statistics
- Document management interface
- Q&A pair editor
- System configuration
- User management (future)

## 🐳 **Docker Configuration**

### Port Allocation (No Conflicts)
```yaml
services:
  postgres-rag:     # Port 5433 (avoiding 5432)
  chromadb:         # Port 8000
  backend:          # Port 8002
  admin-frontend:   # Port 3002
  chat-frontend:    # Port 3003
```

## 📚 **Learning Progression**

### **Phase 1: Foundation (Week 1)**
- Set up Docker environment
- Create PostgreSQL with pgvector
- Implement basic FastAPI structure
- Create database models and schemas

### **Phase 2: Document Processing (Week 2)**
- Implement PDF/text file processing
- Create document chunking algorithms
- Set up embedding generation
- Integrate ChromaDB for vector storage

### **Phase 3: RAG Pipeline (Week 3)**
- Build retrieval system
- Implement context ranking
- Integrate LLM for generation
- Create response formatting

### **Phase 4: Frontend Development (Week 4)**
- Build admin console interface
- Create chat interface
- Implement file upload functionality
- Add real-time features

### **Phase 5: Integration & Polish (Week 5)**
- End-to-end testing
- Performance optimization
- Error handling and validation
- Documentation and deployment

## 🎓 **Skills Demonstrated**

1. **Vector Databases** - PostgreSQL with pgvector extension
2. **Semantic Search** - ChromaDB integration and similarity search
3. **Document Processing** - PDF parsing and text extraction
4. **RAG Architecture** - Retrieval-Augmented Generation pipeline
5. **Full-Stack Development** - FastAPI + React integration
6. **Database Design** - Relational and vector data modeling
7. **File Handling** - Upload, processing, and storage
8. **API Design** - RESTful APIs with proper documentation
9. **Containerization** - Multi-service Docker setup
10. **Real-time Features** - WebSocket integration for chat

## 🔄 **RAG Workflow**

```
User Query → Embedding → Vector Search → Context Retrieval → 
LLM Generation → Response + Sources → User Interface
```

1. **Query Processing**: Convert user question to embeddings
2. **Retrieval**: Search ChromaDB for relevant document chunks
3. **Ranking**: Score and rank retrieved contexts
4. **Augmentation**: Combine query with retrieved context
5. **Generation**: Use LLM to generate contextual response
6. **Attribution**: Include source references and confidence scores

## 🎯 **Success Metrics**

- **Functional**: All CRUD operations work for documents and Q&A
- **Performance**: Sub-2-second response times for queries
- **Accuracy**: Relevant context retrieval with proper citations
- **Usability**: Intuitive admin interface and chat experience
- **Scalability**: Handle 1000+ documents and concurrent users

## 🚦 **Getting Started**

1. **Clone and Setup**:
   ```bash
   cd exercise_6
   cp .env.example .env
   # Edit .env with your configurations
   ```

2. **Start Services**:
   ```bash
   docker-compose up -d
   ./scripts/setup.sh
   ```

3. **Access Interfaces**:
   - Admin Console: http://localhost:3002
   - Chat Interface: http://localhost:3003
   - API Docs: http://localhost:8002/docs

4. **Load Sample Data**:
   ```bash
   ./scripts/load_sample_data.sh
   ```

This exercise provides a comprehensive introduction to modern RAG systems while building upon the foundational concepts from previous exercises! 🚀
