"""
Database Query Tool with parameter schema validation and read-only SQL whitelist
"""

import re
import sqlite3
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from pathlib import Path
import logging
from pydantic import BaseModel, ValidationError, Field
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from observability.otel import get_tracer

logger = logging.getLogger(__name__)
tracer = get_tracer(__name__)

class QueryRequest(BaseModel):
    """Schema for database query requests"""
    query: str = Field(..., description="SQL query to execute")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Query parameters")
    database: Optional[str] = Field(default="default", description="Database identifier")
    timeout: Optional[int] = Field(default=30, description="Query timeout in seconds")

class QueryResult(BaseModel):
    """Schema for database query results"""
    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    columns: Optional[List[str]] = None
    row_count: Optional[int] = None
    execution_time_ms: Optional[float] = None
    error: Optional[str] = None

@dataclass
class DatabaseConfig:
    """Database configuration"""
    name: str
    connection_string: str
    read_only: bool = True
    max_connections: int = 5

class SQLWhitelist:
    """SQL whitelist validator for read-only operations"""
    
    # Allowed SQL statement patterns (read-only operations)
    ALLOWED_PATTERNS = [
        r'^\s*SELECT\s+',
        r'^\s*WITH\s+',
        r'^\s*EXPLAIN\s+',
        r'^\s*DESCRIBE\s+',
        r'^\s*SHOW\s+',
    ]
    
    # Forbidden patterns that could modify data
    FORBIDDEN_PATTERNS = [
        r'\b(INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE|REPLACE)\b',
        r'\b(EXEC|EXECUTE|CALL)\b',
        r'--\s*',  # SQL comments that might hide malicious code
        r'/\*.*?\*/',  # Block comments
        r';\s*\w+',  # Multiple statements
    ]
    
    @classmethod
    def validate_query(cls, query: str) -> bool:
        """
        Validate that query is read-only and safe
        
        Args:
            query: SQL query string
            
        Returns:
            True if query is allowed, False otherwise
        """
        query_upper = query.upper().strip()
        
        # Check if query matches allowed patterns
        allowed = any(re.match(pattern, query_upper, re.IGNORECASE) 
                     for pattern in cls.ALLOWED_PATTERNS)
        
        if not allowed:
            return False
        
        # Check for forbidden patterns
        forbidden = any(re.search(pattern, query_upper, re.IGNORECASE) 
                       for pattern in cls.FORBIDDEN_PATTERNS)
        
        return not forbidden
    
    @classmethod
    def sanitize_query(cls, query: str) -> str:
        """
        Basic query sanitization
        
        Args:
            query: Raw SQL query
            
        Returns:
            Sanitized query string
        """
        # Remove leading/trailing whitespace
        query = query.strip()
        
        # Ensure query ends with semicolon
        if not query.endswith(';'):
            query += ';'
        
        return query

class DBQueryTool:
    """Database query tool with safety features"""
    
    def __init__(self):
        self.databases: Dict[str, DatabaseConfig] = {}
        self.engines: Dict[str, Any] = {}
        self.sessions: Dict[str, Any] = {}
        
        # Initialize default SQLite database for demo
        self._setup_default_database()
    
    def _setup_default_database(self):
        """Setup default SQLite database with sample data"""
        db_path = Path("data/demo.db")
        db_path.parent.mkdir(exist_ok=True)
        
        # Create database config
        config = DatabaseConfig(
            name="default",
            connection_string=f"sqlite:///{db_path}",
            read_only=True
        )
        
        self.add_database(config)
        
        # Create sample data if database is empty
        self._create_sample_data(db_path)
    
    def _create_sample_data(self, db_path: Path):
        """Create sample data for demonstration"""
        if db_path.exists() and db_path.stat().st_size > 0:
            return  # Database already has data
        
        # Create sample tables and data
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        try:
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Products table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    price DECIMAL(10,2) NOT NULL,
                    category TEXT,
                    in_stock BOOLEAN DEFAULT TRUE
                )
            ''')
            
            # Sample data
            users_data = [
                ('Alice Johnson', 'alice@example.com'),
                ('Bob Smith', 'bob@example.com'),
                ('Charlie Brown', 'charlie@example.com'),
            ]
            
            products_data = [
                ('Laptop', 999.99, 'Electronics', True),
                ('Mouse', 29.99, 'Electronics', True),
                ('Keyboard', 79.99, 'Electronics', False),
                ('Desk Chair', 199.99, 'Furniture', True),
            ]
            
            cursor.executemany('INSERT INTO users (name, email) VALUES (?, ?)', users_data)
            cursor.executemany('INSERT INTO products (name, price, category, in_stock) VALUES (?, ?, ?, ?)', products_data)
            
            conn.commit()
            logger.info("Sample database created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create sample data: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def add_database(self, config: DatabaseConfig):
        """Add a database configuration"""
        self.databases[config.name] = config
        
        # Create SQLAlchemy engine
        engine = create_engine(
            config.connection_string,
            pool_size=config.max_connections,
            echo=False  # Set to True for SQL logging
        )
        
        self.engines[config.name] = engine
        self.sessions[config.name] = sessionmaker(bind=engine)
    
    async def execute(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a database query with validation
        
        Args:
            request_data: Query request data
            
        Returns:
            Query result dictionary
        """
        
        with tracer.start_as_current_span("db_query") as span:
            span.set_attribute("tool.name", "db_query")
            
            try:
                # Validate request schema
                request = QueryRequest(**request_data)
                span.set_attribute("db.database", request.database)
                
                # Validate query safety
                if not SQLWhitelist.validate_query(request.query):
                    error_msg = "Query not allowed: Only read-only SELECT statements are permitted"
                    span.set_attribute("status", "error")
                    span.set_attribute("error.message", error_msg)
                    return QueryResult(success=False, error=error_msg).dict()
                
                # Check if database exists
                if request.database not in self.databases:
                    error_msg = f"Database '{request.database}' not found"
                    span.set_attribute("status", "error")
                    span.set_attribute("error.message", error_msg)
                    return QueryResult(success=False, error=error_msg).dict()
                
                # Execute query
                result = await self._execute_query(request, span)
                return result.dict()
                
            except ValidationError as e:
                error_msg = f"Invalid request schema: {e}"
                span.set_attribute("status", "error")
                span.set_attribute("error.message", error_msg)
                return QueryResult(success=False, error=error_msg).dict()
                
            except Exception as e:
                error_msg = f"Query execution failed: {str(e)}"
                span.set_attribute("status", "error")
                span.set_attribute("error.message", error_msg)
                logger.error(f"Database query error: {e}")
                return QueryResult(success=False, error=error_msg).dict()
    
    async def _execute_query(self, request: QueryRequest, span) -> QueryResult:
        """Execute the actual database query"""
        import time
        
        engine = self.engines[request.database]
        Session = self.sessions[request.database]
        
        start_time = time.time()
        
        with Session() as session:
            try:
                # Sanitize query
                sanitized_query = SQLWhitelist.sanitize_query(request.query)
                span.set_attribute("db.statement", sanitized_query[:200])  # Truncate for span
                
                # Execute query with parameters
                if request.parameters:
                    result = session.execute(text(sanitized_query), request.parameters)
                else:
                    result = session.execute(text(sanitized_query))
                
                execution_time_ms = (time.time() - start_time) * 1000
                span.set_attribute("latency_ms", execution_time_ms)
                
                # Fetch results
                if result.returns_rows:
                    rows = result.fetchall()
                    columns = list(result.keys()) if rows else []
                    
                    # Convert rows to dictionaries
                    data = [dict(zip(columns, row)) for row in rows]
                    
                    span.set_attribute("db.rows_affected", len(data))
                    span.set_attribute("status", "success")
                    
                    return QueryResult(
                        success=True,
                        data=data,
                        columns=columns,
                        row_count=len(data),
                        execution_time_ms=execution_time_ms
                    )
                else:
                    # Non-SELECT query (shouldn't happen with whitelist, but just in case)
                    span.set_attribute("status", "success")
                    return QueryResult(
                        success=True,
                        data=[],
                        columns=[],
                        row_count=0,
                        execution_time_ms=execution_time_ms
                    )
                    
            except Exception as e:
                execution_time_ms = (time.time() - start_time) * 1000
                span.set_attribute("latency_ms", execution_time_ms)
                raise e
    
    def get_database_info(self, database: str = "default") -> Dict[str, Any]:
        """Get information about a database"""
        if database not in self.databases:
            return {"error": f"Database '{database}' not found"}
        
        config = self.databases[database]
        return {
            "name": config.name,
            "read_only": config.read_only,
            "max_connections": config.max_connections,
            "available": True
        }
    
    def list_databases(self) -> List[str]:
        """List available databases"""
        return list(self.databases.keys())

# Global instance for the API
_global_db_tool = None

def get_db_query_tool() -> DBQueryTool:
    """Get global database query tool instance"""
    global _global_db_tool
    if _global_db_tool is None:
        _global_db_tool = DBQueryTool()
    return _global_db_tool
