"""
Pytest configuration and fixtures for AI Agent Training API tests
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from httpx import AsyncClient
import sqlite3

from app import app
from tools.http_fetch import HTTPFetcher
from tools.db_query import DBQueryTool, DatabaseConfig
from tools.file_ops import FileOperations
from observability.otel import setup_observability

# Configure pytest-asyncio
pytest_plugins = ('pytest_asyncio',)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
def setup_test_observability():
    """Setup observability for tests"""
    setup_observability(
        service_name="ai-agent-training-api-test",
        enable_console_export=False  # Disable console output in tests
    )

@pytest.fixture
def client() -> TestClient:
    """FastAPI test client"""
    return TestClient(app)

@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client for testing"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def temp_workspace() -> Generator[Path, None, None]:
    """Temporary workspace directory for file operations tests"""
    temp_dir = Path(tempfile.mkdtemp(prefix="test_workspace_"))
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def file_ops_with_temp_workspace(temp_workspace: Path) -> FileOperations:
    """File operations instance with temporary workspace"""
    return FileOperations(workspace_root=str(temp_workspace))

@pytest.fixture
def temp_database() -> Generator[Path, None, None]:
    """Temporary SQLite database for testing"""
    temp_db = Path(tempfile.mktemp(suffix=".db"))
    
    # Create test database with sample data
    conn = sqlite3.connect(str(temp_db))
    cursor = conn.cursor()
    
    # Create test tables
    cursor.execute('''
        CREATE TABLE test_users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            age INTEGER
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE test_products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price DECIMAL(10,2),
            category TEXT
        )
    ''')
    
    # Insert test data
    test_users = [
        (1, 'Alice', 'alice@test.com', 25),
        (2, 'Bob', 'bob@test.com', 30),
        (3, 'Charlie', 'charlie@test.com', 35),
    ]
    
    test_products = [
        (1, 'Laptop', 999.99, 'Electronics'),
        (2, 'Mouse', 29.99, 'Electronics'),
        (3, 'Desk', 199.99, 'Furniture'),
    ]
    
    cursor.executemany('INSERT INTO test_users VALUES (?, ?, ?, ?)', test_users)
    cursor.executemany('INSERT INTO test_products VALUES (?, ?, ?, ?)', test_products)
    
    conn.commit()
    conn.close()
    
    try:
        yield temp_db
    finally:
        if temp_db.exists():
            temp_db.unlink()

@pytest.fixture
def db_query_tool_with_temp_db(temp_database: Path) -> DBQueryTool:
    """Database query tool with temporary database"""
    tool = DBQueryTool()
    
    # Add test database configuration
    config = DatabaseConfig(
        name="test",
        connection_string=f"sqlite:///{temp_database}",
        read_only=True
    )
    tool.add_database(config)
    
    return tool

@pytest.fixture
def http_fetcher() -> HTTPFetcher:
    """HTTP fetcher instance for testing"""
    return HTTPFetcher(
        timeout=5.0,
        max_retries=2,
        rate_limit_rps=100.0,  # Higher rate limit for tests
        user_agent="AI-Agent-Training-Test/1.0"
    )

@pytest.fixture
def sample_json_response():
    """Sample JSON response for HTTP tests"""
    return {
        "status": "success",
        "data": {
            "id": 123,
            "name": "Test Item",
            "values": [1, 2, 3, 4, 5]
        },
        "timestamp": "2024-01-01T00:00:00Z"
    }

@pytest.fixture
def sample_text_file_content():
    """Sample text file content for file operations tests"""
    return """# Sample Text File

This is a sample text file for testing file operations.

## Features
- Reading files
- Writing files
- File validation

## Data
Numbers: 1, 2, 3, 4, 5
Text: Hello, World!
"""

@pytest.fixture
def sample_sql_queries():
    """Sample SQL queries for database tests"""
    return {
        "valid_select": "SELECT * FROM test_users WHERE age > 25;",
        "valid_join": """
            SELECT u.name, p.name as product_name, p.price
            FROM test_users u
            JOIN test_products p ON u.id = p.id
            WHERE p.category = 'Electronics';
        """,
        "invalid_insert": "INSERT INTO test_users (name, email) VALUES ('Hacker', 'hack@evil.com');",
        "invalid_drop": "DROP TABLE test_users;",
        "invalid_comment": "SELECT * FROM test_users; -- DROP TABLE test_users;",
    }

# Hypothesis strategies for property-based testing
from hypothesis import strategies as st

@pytest.fixture
def hypothesis_strategies():
    """Hypothesis strategies for property-based testing"""
    return {
        "file_names": st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Pc")),
            min_size=1,
            max_size=50
        ).filter(lambda x: not x.startswith('.')),
        
        "file_content": st.text(
            alphabet=st.characters(blacklist_characters="\x00"),
            max_size=1000
        ),
        
        "http_urls": st.builds(
            lambda scheme, host, path: f"{scheme}://{host}{path}",
            scheme=st.sampled_from(["http", "https"]),
            host=st.text(
                alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")),
                min_size=3,
                max_size=20
            ).map(lambda x: x + ".com"),
            path=st.text(
                alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Pc")),
                max_size=50
            ).map(lambda x: "/" + x if x else "")
        ),
        
        "sql_select_queries": st.builds(
            lambda table, columns, condition: f"SELECT {columns} FROM {table} WHERE {condition};",
            table=st.sampled_from(["test_users", "test_products"]),
            columns=st.sampled_from(["*", "id", "name", "id, name"]),
            condition=st.sampled_from(["1=1", "id > 0", "name IS NOT NULL"])
        )
    }
