-- Exercise 6 RAG Chatbot Database Initialization
-- PostgreSQL with pgvector extension for vector similarity search

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Set timezone
SET timezone = 'UTC';

-- Create custom types
CREATE TYPE document_status AS ENUM ('processing', 'completed', 'failed', 'archived');
CREATE TYPE qa_pair_status AS ENUM ('active', 'inactive', 'archived');
CREATE TYPE chat_message_type AS ENUM ('user', 'assistant', 'system');

-- =============================================================================
-- KNOWLEDGE BASE TABLES
-- =============================================================================

-- Knowledge base categories/collections
CREATE TABLE knowledge_bases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Documents table for uploaded files
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    knowledge_base_id UUID REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    filename VARCHAR(500) NOT NULL,
    original_filename VARCHAR(500) NOT NULL,
    file_path TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    mime_type VARCHAR(100),
    status document_status DEFAULT 'processing',
    title VARCHAR(500),
    author VARCHAR(255),
    language VARCHAR(10) DEFAULT 'en',
    tags TEXT[],
    metadata JSONB DEFAULT '{}',
    processing_error TEXT,
    processed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Document chunks for RAG retrieval
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    content_hash VARCHAR(64) NOT NULL, -- SHA-256 hash for deduplication
    token_count INTEGER,
    char_count INTEGER DEFAULT LENGTH(content),
    embedding vector(1536), -- OpenAI text-embedding-3-small dimension
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT unique_document_chunk UNIQUE (document_id, chunk_index),
    CONSTRAINT positive_chunk_index CHECK (chunk_index >= 0),
    CONSTRAINT non_empty_content CHECK (LENGTH(TRIM(content)) > 0)
);

-- Q&A pairs for direct question-answer matching
CREATE TABLE qa_pairs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    knowledge_base_id UUID REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    question_variations TEXT[], -- Alternative phrasings of the question
    answer_format VARCHAR(50) DEFAULT 'text', -- text, markdown, html
    confidence_score DECIMAL(3,2) DEFAULT 1.0,
    status qa_pair_status DEFAULT 'active',
    tags TEXT[],
    source_url TEXT,
    source_document_id UUID REFERENCES documents(id) ON DELETE SET NULL,
    question_embedding vector(1536), -- OpenAI embedding for question
    answer_embedding vector(1536), -- OpenAI embedding for answer
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_confidence CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    CONSTRAINT non_empty_question CHECK (LENGTH(TRIM(question)) > 0),
    CONSTRAINT non_empty_answer CHECK (LENGTH(TRIM(answer)) > 0)
);

-- =============================================================================
-- CHAT AND CONVERSATION TABLES
-- =============================================================================

-- Chat sessions/conversations
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_name VARCHAR(255),
    knowledge_base_id UUID REFERENCES knowledge_bases(id) ON DELETE SET NULL,
    user_id VARCHAR(255), -- For future user management
    is_active BOOLEAN DEFAULT true,
    metadata JSONB DEFAULT '{}',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP WITH TIME ZONE,
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Individual chat messages
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    message_type chat_message_type NOT NULL,
    content TEXT NOT NULL,
    sources JSONB DEFAULT '[]', -- Array of source references
    confidence_score DECIMAL(3,2),
    processing_time_ms INTEGER,
    token_count INTEGER,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_confidence CHECK (confidence_score IS NULL OR (confidence_score >= 0.0 AND confidence_score <= 1.0)),
    CONSTRAINT non_empty_content CHECK (LENGTH(TRIM(content)) > 0)
);

-- =============================================================================
-- ANALYTICS AND FEEDBACK TABLES
-- =============================================================================

-- User feedback on responses
CREATE TABLE message_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_id UUID REFERENCES chat_messages(id) ON DELETE CASCADE,
    feedback_type VARCHAR(20) NOT NULL, -- thumbs_up, thumbs_down, report
    feedback_text TEXT,
    user_id VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_feedback_type CHECK (feedback_type IN ('thumbs_up', 'thumbs_down', 'report', 'custom'))
);

-- Search analytics for improving retrieval
CREATE TABLE search_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query TEXT NOT NULL,
    knowledge_base_id UUID REFERENCES knowledge_bases(id) ON DELETE SET NULL,
    results_count INTEGER DEFAULT 0,
    top_similarity_score DECIMAL(5,4),
    processing_time_ms INTEGER,
    user_id VARCHAR(255),
    session_id UUID REFERENCES chat_sessions(id) ON DELETE SET NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

-- Knowledge bases indexes
CREATE INDEX idx_knowledge_bases_active ON knowledge_bases(is_active);
CREATE INDEX idx_knowledge_bases_created ON knowledge_bases(created_at DESC);

-- Documents indexes
CREATE INDEX idx_documents_kb_id ON documents(knowledge_base_id);
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_created ON documents(created_at DESC);
CREATE INDEX idx_documents_filename ON documents(filename);
CREATE INDEX idx_documents_tags ON documents USING GIN(tags);

-- Document chunks indexes
CREATE INDEX idx_chunks_document_id ON document_chunks(document_id);
CREATE INDEX idx_chunks_content_hash ON document_chunks(content_hash);
CREATE INDEX idx_chunks_embedding ON document_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Q&A pairs indexes
CREATE INDEX idx_qa_pairs_kb_id ON qa_pairs(knowledge_base_id);
CREATE INDEX idx_qa_pairs_status ON qa_pairs(status);
CREATE INDEX idx_qa_pairs_tags ON qa_pairs USING GIN(tags);
CREATE INDEX idx_qa_pairs_question_text ON qa_pairs USING GIN(to_tsvector('english', question));
CREATE INDEX idx_qa_pairs_answer_text ON qa_pairs USING GIN(to_tsvector('english', answer));
CREATE INDEX idx_qa_pairs_question_embedding ON qa_pairs USING ivfflat (question_embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_qa_pairs_answer_embedding ON qa_pairs USING ivfflat (answer_embedding vector_cosine_ops) WITH (lists = 100);

-- Chat sessions indexes
CREATE INDEX idx_chat_sessions_kb_id ON chat_sessions(knowledge_base_id);
CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX idx_chat_sessions_active ON chat_sessions(is_active);
CREATE INDEX idx_chat_sessions_activity ON chat_sessions(last_activity_at DESC);

-- Chat messages indexes
CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_type ON chat_messages(message_type);
CREATE INDEX idx_chat_messages_created ON chat_messages(created_at DESC);

-- Analytics indexes
CREATE INDEX idx_message_feedback_message_id ON message_feedback(message_id);
CREATE INDEX idx_message_feedback_type ON message_feedback(feedback_type);
CREATE INDEX idx_search_analytics_kb_id ON search_analytics(knowledge_base_id);
CREATE INDEX idx_search_analytics_created ON search_analytics(created_at DESC);

-- =============================================================================
-- FUNCTIONS AND TRIGGERS
-- =============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_knowledge_bases_updated_at BEFORE UPDATE ON knowledge_bases FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_qa_pairs_updated_at BEFORE UPDATE ON qa_pairs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to update last_activity_at for chat sessions
CREATE OR REPLACE FUNCTION update_session_activity()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE chat_sessions 
    SET last_activity_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.session_id;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to update session activity on new messages
CREATE TRIGGER update_chat_session_activity 
    AFTER INSERT ON chat_messages 
    FOR EACH ROW 
    EXECUTE FUNCTION update_session_activity();

-- =============================================================================
-- SAMPLE DATA (Optional - for development)
-- =============================================================================

-- Insert default knowledge base
INSERT INTO knowledge_bases (name, description, metadata) VALUES 
('Default Knowledge Base', 'Default knowledge base for general questions', '{"created_by": "system", "version": "1.0"}');

-- Insert sample Q&A pairs
INSERT INTO qa_pairs (knowledge_base_id, question, answer, question_variations, tags) VALUES 
(
    (SELECT id FROM knowledge_bases WHERE name = 'Default Knowledge Base'),
    'What is RAG?',
    'RAG (Retrieval-Augmented Generation) is a technique that combines information retrieval with text generation. It retrieves relevant documents from a knowledge base and uses them to generate more accurate and contextual responses.',
    ARRAY['What does RAG stand for?', 'Explain RAG', 'What is Retrieval-Augmented Generation?'],
    ARRAY['rag', 'ai', 'nlp', 'retrieval']
),
(
    (SELECT id FROM knowledge_bases WHERE name = 'Default Knowledge Base'),
    'How does vector similarity search work?',
    'Vector similarity search works by converting text into high-dimensional vectors (embeddings) and then finding vectors that are close to each other in the vector space. This allows for semantic similarity matching rather than just keyword matching.',
    ARRAY['Explain vector search', 'What is semantic search?', 'How do embeddings work?'],
    ARRAY['vectors', 'embeddings', 'similarity', 'search']
);

-- =============================================================================
-- PERMISSIONS AND SECURITY
-- =============================================================================

-- Create read-only user for analytics (optional)
-- CREATE USER rag_readonly WITH PASSWORD 'readonly_password_2024';
-- GRANT CONNECT ON DATABASE rag_chatbot TO rag_readonly;
-- GRANT USAGE ON SCHEMA public TO rag_readonly;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO rag_readonly;

-- Grant permissions to main user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO rag_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO rag_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO rag_user;

-- =============================================================================
-- COMPLETION MESSAGE
-- =============================================================================

DO $$
BEGIN
    RAISE NOTICE 'Exercise 6 RAG Chatbot database initialized successfully!';
    RAISE NOTICE 'Database: rag_chatbot';
    RAISE NOTICE 'User: rag_user';
    RAISE NOTICE 'Extensions enabled: uuid-ossp, pgcrypto, vector';
    RAISE NOTICE 'Tables created: %, %, %, %, %, %', 
        (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'),
        'knowledge_bases', 'documents', 'document_chunks', 'qa_pairs', 'chat_sessions', 'chat_messages';
END $$;
