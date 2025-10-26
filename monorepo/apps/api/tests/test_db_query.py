"""
Tests for database query tool with schema validation and SQL whitelist
"""

import pytest
import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings

from tools.db_query import DBQueryTool, SQLWhitelist, QueryRequest, DatabaseConfig

class TestSQLWhitelist:
    """Test SQL whitelist validation"""
    
    def test_valid_select_queries(self):
        """Test that valid SELECT queries are allowed"""
        valid_queries = [
            "SELECT * FROM users;",
            "SELECT id, name FROM products WHERE price > 100;",
            "SELECT u.name, p.title FROM users u JOIN products p ON u.id = p.user_id;",
            "WITH ranked_users AS (SELECT *, ROW_NUMBER() OVER (ORDER BY created_at) as rn FROM users) SELECT * FROM ranked_users;",
            "EXPLAIN SELECT * FROM users;",
            "DESCRIBE users;",
            "SHOW TABLES;",
            "  \n  SELECT\n    *\n  FROM\n    users\n  WHERE\n    active = 1;  ",  # With whitespace
        ]
        
        for query in valid_queries:
            assert SQLWhitelist.validate_query(query), f"Query should be valid: {query}"
    
    def test_invalid_modification_queries(self):
        """Test that data modification queries are rejected"""
        invalid_queries = [
            "INSERT INTO users (name) VALUES ('hacker');",
            "UPDATE users SET name = 'hacker' WHERE id = 1;",
            "DELETE FROM users WHERE id = 1;",
            "DROP TABLE users;",
            "CREATE TABLE evil (id INT);",
            "ALTER TABLE users ADD COLUMN evil TEXT;",
            "TRUNCATE TABLE users;",
            "REPLACE INTO users VALUES (1, 'hacker');",
            "EXEC sp_evil_procedure;",
            "EXECUTE IMMEDIATE 'DROP TABLE users';",
            "CALL evil_function();",
        ]
        
        for query in invalid_queries:
            assert not SQLWhitelist.validate_query(query), f"Query should be invalid: {query}"
    
    def test_sql_injection_attempts(self):
        """Test that SQL injection attempts are rejected"""
        injection_queries = [
            "SELECT * FROM users; DROP TABLE users;",
            "SELECT * FROM users WHERE id = 1; INSERT INTO users VALUES (999, 'hacker');",
            "SELECT * FROM users -- DROP TABLE users;",
            "SELECT * FROM users /* DROP TABLE users */;",
            "SELECT * FROM users WHERE name = 'test'; DELETE FROM users;",
        ]
        
        for query in injection_queries:
            assert not SQLWhitelist.validate_query(query), f"Injection attempt should be invalid: {query}"
    
    def test_query_sanitization(self):
        """Test query sanitization"""
        test_cases = [
            ("SELECT * FROM users", "SELECT * FROM users;"),
            ("  SELECT * FROM users  ", "SELECT * FROM users;"),
            ("SELECT * FROM users;", "SELECT * FROM users;"),
            ("SELECT * FROM users;;", "SELECT * FROM users;;;"),  # Multiple semicolons preserved
        ]
        
        for input_query, expected in test_cases:
            result = SQLWhitelist.sanitize_query(input_query)
            assert result == expected, f"Expected '{expected}', got '{result}'"

class TestDBQueryTool:
    """Test database query tool functionality"""
    
    @pytest.fixture
    def db_tool_with_test_db(self, temp_database):
        """Create DB tool with test database"""
        tool = DBQueryTool()
        config = DatabaseConfig(
            name="test",
            connection_string=f"sqlite:///{temp_database}",
            read_only=True
        )
        tool.add_database(config)
        return tool
    
    @pytest.mark.asyncio
    async def test_valid_select_query(self, db_tool_with_test_db):
        """Test executing valid SELECT query"""
        request_data = {
            "query": "SELECT * FROM test_users WHERE age > 25;",
            "database": "test"
        }
        
        result = await db_tool_with_test_db.execute(request_data)
        
        assert result["success"] is True
        assert "data" in result
        assert len(result["data"]) == 2  # Bob and Charlie (age > 25)
        assert "execution_time_ms" in result
        assert result["row_count"] == 2
        
        # Check data structure
        for row in result["data"]:
            assert "id" in row
            assert "name" in row
            assert "email" in row
            assert "age" in row
    
    @pytest.mark.asyncio
    async def test_query_with_parameters(self, db_tool_with_test_db):
        """Test query execution with parameters"""
        request_data = {
            "query": "SELECT * FROM test_users WHERE age > :min_age;",
            "parameters": {"min_age": 30},
            "database": "test"
        }
        
        result = await db_tool_with_test_db.execute(request_data)
        
        assert result["success"] is True
        assert len(result["data"]) == 1  # Only Charlie (age 35)
        assert result["data"][0]["name"] == "Charlie"
    
    @pytest.mark.asyncio
    async def test_join_query(self, db_tool_with_test_db):
        """Test JOIN query execution"""
        request_data = {
            "query": """
                SELECT u.name, p.name as product_name, p.price
                FROM test_users u
                JOIN test_products p ON u.id = p.id
                WHERE p.category = 'Electronics';
            """,
            "database": "test"
        }
        
        result = await db_tool_with_test_db.execute(request_data)
        
        assert result["success"] is True
        assert len(result["data"]) == 2  # Laptop and Mouse
        
        # Verify column names
        assert "columns" in result
        expected_columns = ["name", "product_name", "price"]
        assert all(col in result["columns"] for col in expected_columns)
    
    @pytest.mark.asyncio
    async def test_invalid_query_rejection(self, db_tool_with_test_db):
        """Test that invalid queries are rejected"""
        invalid_requests = [
            {"query": "INSERT INTO test_users (name, email) VALUES ('hacker', 'hack@evil.com');", "database": "test"},
            {"query": "DROP TABLE test_users;", "database": "test"},
            {"query": "UPDATE test_users SET name = 'hacker';", "database": "test"},
            {"query": "DELETE FROM test_users;", "database": "test"},
        ]
        
        for request_data in invalid_requests:
            result = await db_tool_with_test_db.execute(request_data)
            assert result["success"] is False
            assert "not allowed" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_nonexistent_database(self, db_tool_with_test_db):
        """Test query to nonexistent database"""
        request_data = {
            "query": "SELECT * FROM test_users;",
            "database": "nonexistent"
        }
        
        result = await db_tool_with_test_db.execute(request_data)
        
        assert result["success"] is False
        assert "not found" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_invalid_sql_syntax(self, db_tool_with_test_db):
        """Test handling of invalid SQL syntax"""
        request_data = {
            "query": "SELECT * FORM test_users;",  # Typo: FORM instead of FROM
            "database": "test"
        }
        
        result = await db_tool_with_test_db.execute(request_data)
        
        assert result["success"] is False
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_empty_result_set(self, db_tool_with_test_db):
        """Test query that returns no results"""
        request_data = {
            "query": "SELECT * FROM test_users WHERE age > 100;",
            "database": "test"
        }
        
        result = await db_tool_with_test_db.execute(request_data)
        
        assert result["success"] is True
        assert result["data"] == []
        assert result["row_count"] == 0
        assert "columns" in result
    
    @pytest.mark.asyncio
    async def test_request_schema_validation(self, db_tool_with_test_db):
        """Test request schema validation"""
        # Missing required query field
        invalid_request = {"database": "test"}
        
        result = await db_tool_with_test_db.execute(invalid_request)
        
        assert result["success"] is False
        assert "schema" in result["error"].lower()
    
    def test_database_info(self, db_tool_with_test_db):
        """Test getting database information"""
        info = db_tool_with_test_db.get_database_info("test")
        
        assert info["name"] == "test"
        assert info["read_only"] is True
        assert info["available"] is True
        
        # Test nonexistent database
        info = db_tool_with_test_db.get_database_info("nonexistent")
        assert "error" in info
    
    def test_list_databases(self, db_tool_with_test_db):
        """Test listing available databases"""
        databases = db_tool_with_test_db.list_databases()
        
        assert "test" in databases
        assert "default" in databases  # Default database should exist

class TestDBQueryToolPropertyBased:
    """Property-based tests using Hypothesis"""
    
    @pytest.fixture
    def db_tool(self, temp_database):
        tool = DBQueryTool()
        config = DatabaseConfig(
            name="test",
            connection_string=f"sqlite:///{temp_database}",
            read_only=True
        )
        tool.add_database(config)
        return tool
    
    @given(st.text(min_size=1, max_size=100))
    @settings(max_examples=10, deadline=5000)
    @pytest.mark.asyncio
    async def test_query_parameter_handling(self, db_tool, param_value):
        """Property: Query parameters are handled safely"""
        # Use a parameterized query to test parameter handling
        request_data = {
            "query": "SELECT * FROM test_users WHERE name = :param_value;",
            "parameters": {"param_value": param_value},
            "database": "test"
        }
        
        result = await db_tool.execute(request_data)
        
        # Should not crash, regardless of parameter value
        assert "success" in result
        if result["success"]:
            assert "data" in result
            assert isinstance(result["data"], list)
    
    @given(st.sampled_from(["test_users", "test_products"]))
    @settings(max_examples=5, deadline=5000)
    @pytest.mark.asyncio
    async def test_table_access(self, db_tool, table_name):
        """Property: All valid tables can be queried"""
        request_data = {
            "query": f"SELECT COUNT(*) as count FROM {table_name};",
            "database": "test"
        }
        
        result = await db_tool.execute(request_data)
        
        assert result["success"] is True
        assert len(result["data"]) == 1
        assert "count" in result["data"][0]
        assert isinstance(result["data"][0]["count"], int)
    
    @given(st.integers(min_value=1, max_value=100))
    @settings(max_examples=10, deadline=5000)
    @pytest.mark.asyncio
    async def test_limit_clause_handling(self, db_tool, limit_value):
        """Property: LIMIT clauses work correctly"""
        request_data = {
            "query": f"SELECT * FROM test_users LIMIT {limit_value};",
            "database": "test"
        }
        
        result = await db_tool.execute(request_data)
        
        assert result["success"] is True
        assert len(result["data"]) <= min(limit_value, 3)  # Max 3 users in test data
        assert result["row_count"] <= min(limit_value, 3)
