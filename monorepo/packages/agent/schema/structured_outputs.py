"""
Structured Outputs with Pydantic and JSON Schema
Defines standardized schemas for agent inputs and outputs
"""

from typing import Dict, Any, List, Optional, Union, Literal
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator, root_validator
import json

class ToolStatus(str, Enum):
    """Tool execution status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"

class ToolType(str, Enum):
    """Tool type enumeration"""
    HTTP_FETCH = "http_fetch"
    DB_QUERY = "db_query"
    FILE_OPS = "file_ops"
    CUSTOM = "custom"

class BaseToolInput(BaseModel):
    """Base schema for tool inputs"""
    tool_type: ToolType = Field(..., description="Type of tool to execute")
    request_id: Optional[str] = Field(default=None, description="Unique request identifier")
    timeout: Optional[int] = Field(default=30, ge=1, le=300, description="Timeout in seconds")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        use_enum_values = True
        extra = "forbid"

class BaseToolOutput(BaseModel):
    """Base schema for tool outputs"""
    tool_type: ToolType = Field(..., description="Type of tool that was executed")
    request_id: Optional[str] = Field(default=None, description="Request identifier")
    status: ToolStatus = Field(..., description="Execution status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Execution timestamp")
    execution_time_ms: Optional[float] = Field(default=None, ge=0, description="Execution time in milliseconds")
    error_message: Optional[str] = Field(default=None, description="Error message if status is error")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# HTTP Fetch Tool Schemas
class HTTPMethod(str, Enum):
    """HTTP method enumeration"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"

class HTTPFetchInput(BaseToolInput):
    """Schema for HTTP fetch tool input"""
    tool_type: Literal[ToolType.HTTP_FETCH] = ToolType.HTTP_FETCH
    url: str = Field(..., description="Target URL", min_length=1)
    method: HTTPMethod = Field(default=HTTPMethod.GET, description="HTTP method")
    headers: Optional[Dict[str, str]] = Field(default_factory=dict, description="HTTP headers")
    params: Optional[Dict[str, str]] = Field(default_factory=dict, description="Query parameters")
    data: Optional[Union[Dict[str, Any], str]] = Field(default=None, description="Request body data")
    follow_redirects: Optional[bool] = Field(default=True, description="Follow HTTP redirects")
    max_retries: Optional[int] = Field(default=3, ge=0, le=10, description="Maximum retry attempts")

    @validator('url')
    def validate_url(cls, v):
        """Validate URL format and security"""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        
        # Basic security check for private IPs
        from urllib.parse import urlparse
        parsed = urlparse(v)
        hostname = parsed.hostname
        
        if hostname and any(hostname.startswith(prefix) for prefix in [
            'localhost', '127.', '10.', '172.16.', '172.17.', '172.18.',
            '172.19.', '172.20.', '172.21.', '172.22.', '172.23.', '172.24.',
            '172.25.', '172.26.', '172.27.', '172.28.', '172.29.', '172.30.',
            '172.31.', '192.168.', '169.254.'
        ]):
            raise ValueError('Access to private/local URLs is not allowed')
        
        return v

class HTTPFetchOutput(BaseToolOutput):
    """Schema for HTTP fetch tool output"""
    tool_type: Literal[ToolType.HTTP_FETCH] = ToolType.HTTP_FETCH
    status_code: Optional[int] = Field(default=None, description="HTTP status code")
    response_headers: Optional[Dict[str, str]] = Field(default_factory=dict, description="Response headers")
    response_data: Optional[Union[Dict[str, Any], str]] = Field(default=None, description="Response data")
    content_type: Optional[str] = Field(default=None, description="Response content type")
    content_length: Optional[int] = Field(default=None, ge=0, description="Response content length")
    final_url: Optional[str] = Field(default=None, description="Final URL after redirects")
    retry_count: Optional[int] = Field(default=0, ge=0, description="Number of retries performed")

# Database Query Tool Schemas
class DBQueryInput(BaseToolInput):
    """Schema for database query tool input"""
    tool_type: Literal[ToolType.DB_QUERY] = ToolType.DB_QUERY
    query: str = Field(..., description="SQL query to execute", min_length=1)
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Query parameters")
    database: Optional[str] = Field(default="default", description="Database identifier")
    max_rows: Optional[int] = Field(default=1000, ge=1, le=10000, description="Maximum rows to return")

    @validator('query')
    def validate_query_safety(cls, v):
        """Validate query is read-only"""
        query_upper = v.upper().strip()
        
        # Check for allowed patterns
        allowed_patterns = ['SELECT', 'WITH', 'EXPLAIN', 'DESCRIBE', 'SHOW']
        if not any(query_upper.startswith(pattern) for pattern in allowed_patterns):
            raise ValueError('Only read-only queries are allowed (SELECT, WITH, EXPLAIN, DESCRIBE, SHOW)')
        
        # Check for forbidden patterns
        forbidden_patterns = [
            'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 
            'TRUNCATE', 'REPLACE', 'EXEC', 'EXECUTE', 'CALL'
        ]
        if any(pattern in query_upper for pattern in forbidden_patterns):
            raise ValueError('Data modification queries are not allowed')
        
        return v

class DBQueryOutput(BaseToolOutput):
    """Schema for database query tool output"""
    tool_type: Literal[ToolType.DB_QUERY] = ToolType.DB_QUERY
    rows: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Query result rows")
    columns: Optional[List[str]] = Field(default_factory=list, description="Column names")
    row_count: Optional[int] = Field(default=0, ge=0, description="Number of rows returned")
    query_plan: Optional[Dict[str, Any]] = Field(default=None, description="Query execution plan")

# File Operations Tool Schemas
class FileOperation(str, Enum):
    """File operation enumeration"""
    READ = "read"
    WRITE = "write"
    LIST = "list"
    DELETE = "delete"
    COPY = "copy"
    MOVE = "move"
    MKDIR = "mkdir"

class FileOpsInput(BaseToolInput):
    """Schema for file operations tool input"""
    tool_type: Literal[ToolType.FILE_OPS] = ToolType.FILE_OPS
    operation: FileOperation = Field(..., description="File operation to perform")
    path: str = Field(..., description="Target file or directory path", min_length=1)
    content: Optional[str] = Field(default=None, description="Content for write operations")
    destination: Optional[str] = Field(default=None, description="Destination path for copy/move operations")
    encoding: Optional[str] = Field(default="utf-8", description="File encoding")
    create_dirs: Optional[bool] = Field(default=False, description="Create parent directories")

    @validator('path')
    def validate_path_safety(cls, v):
        """Validate path for security"""
        # Prevent path traversal
        if '..' in v or v.startswith('/'):
            raise ValueError('Path traversal and absolute paths are not allowed')
        return v

    @root_validator
    def validate_operation_requirements(cls, values):
        """Validate operation-specific requirements"""
        operation = values.get('operation')
        content = values.get('content')
        destination = values.get('destination')
        
        if operation == FileOperation.WRITE and content is None:
            raise ValueError('Content is required for write operations')
        
        if operation in [FileOperation.COPY, FileOperation.MOVE] and destination is None:
            raise ValueError('Destination is required for copy/move operations')
        
        return values

class FileInfo(BaseModel):
    """File information schema"""
    name: str = Field(..., description="File or directory name")
    path: str = Field(..., description="Full path")
    type: Literal["file", "directory"] = Field(..., description="Item type")
    size: Optional[int] = Field(default=None, ge=0, description="File size in bytes")
    modified: Optional[datetime] = Field(default=None, description="Last modified timestamp")
    mime_type: Optional[str] = Field(default=None, description="MIME type")
    checksum: Optional[str] = Field(default=None, description="File checksum")

class FileOpsOutput(BaseToolOutput):
    """Schema for file operations tool output"""
    tool_type: Literal[ToolType.FILE_OPS] = ToolType.FILE_OPS
    operation: FileOperation = Field(..., description="Operation that was performed")
    path: str = Field(..., description="Target path")
    content: Optional[str] = Field(default=None, description="File content for read operations")
    files: Optional[List[FileInfo]] = Field(default_factory=list, description="File listing for list operations")
    file_info: Optional[FileInfo] = Field(default=None, description="File information")

# Agent Conversation Schemas
class MessageRole(str, Enum):
    """Message role enumeration"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"

class Message(BaseModel):
    """Chat message schema"""
    role: MessageRole = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Message metadata")

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ToolCall(BaseModel):
    """Tool call schema"""
    id: str = Field(..., description="Unique tool call identifier")
    tool_type: ToolType = Field(..., description="Type of tool to call")
    input_data: Dict[str, Any] = Field(..., description="Tool input data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Call timestamp")

class ToolResult(BaseModel):
    """Tool result schema"""
    call_id: str = Field(..., description="Tool call identifier")
    output_data: Dict[str, Any] = Field(..., description="Tool output data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Result timestamp")

class AgentResponse(BaseModel):
    """Agent response schema"""
    message: Optional[str] = Field(default=None, description="Response message")
    tool_calls: Optional[List[ToolCall]] = Field(default_factory=list, description="Tool calls to make")
    finished: bool = Field(default=False, description="Whether the conversation is finished")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Response metadata")

# Utility functions for schema validation and conversion
def validate_tool_input(tool_type: ToolType, input_data: Dict[str, Any]) -> BaseToolInput:
    """Validate and convert tool input data to appropriate schema"""
    schema_map = {
        ToolType.HTTP_FETCH: HTTPFetchInput,
        ToolType.DB_QUERY: DBQueryInput,
        ToolType.FILE_OPS: FileOpsInput,
    }
    
    schema_class = schema_map.get(tool_type)
    if not schema_class:
        raise ValueError(f"Unknown tool type: {tool_type}")
    
    return schema_class(**input_data)

def validate_tool_output(tool_type: ToolType, output_data: Dict[str, Any]) -> BaseToolOutput:
    """Validate and convert tool output data to appropriate schema"""
    schema_map = {
        ToolType.HTTP_FETCH: HTTPFetchOutput,
        ToolType.DB_QUERY: DBQueryOutput,
        ToolType.FILE_OPS: FileOpsOutput,
    }
    
    schema_class = schema_map.get(tool_type)
    if not schema_class:
        raise ValueError(f"Unknown tool type: {tool_type}")
    
    return schema_class(**output_data)

def generate_json_schema(model_class: BaseModel) -> Dict[str, Any]:
    """Generate JSON schema for a Pydantic model"""
    return model_class.schema()

def export_all_schemas() -> Dict[str, Dict[str, Any]]:
    """Export JSON schemas for all defined models"""
    models = [
        HTTPFetchInput, HTTPFetchOutput,
        DBQueryInput, DBQueryOutput,
        FileOpsInput, FileOpsOutput,
        Message, ToolCall, ToolResult, AgentResponse
    ]
    
    return {
        model.__name__: generate_json_schema(model)
        for model in models
    }
