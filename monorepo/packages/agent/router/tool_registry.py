"""
Tool Registry with registration and permission management
Centralized registry for managing available tools and their permissions
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable, Set, Union
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
import inspect
from datetime import datetime

from ..schema.structured_outputs import ToolType, BaseToolInput, BaseToolOutput, ToolStatus

logger = logging.getLogger(__name__)

class PermissionLevel(str, Enum):
    """Permission levels for tool access"""
    PUBLIC = "public"          # Anyone can use
    AUTHENTICATED = "authenticated"  # Requires authentication
    ADMIN = "admin"           # Admin only
    SYSTEM = "system"         # System internal use only

@dataclass
class ToolPermission:
    """Tool permission configuration"""
    level: PermissionLevel = PermissionLevel.PUBLIC
    allowed_users: Optional[Set[str]] = None
    allowed_roles: Optional[Set[str]] = None
    rate_limit_per_minute: Optional[int] = None
    max_concurrent_calls: Optional[int] = None

@dataclass
class ToolMetadata:
    """Tool metadata and configuration"""
    name: str
    tool_type: ToolType
    description: str
    version: str = "1.0.0"
    author: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    permission: ToolPermission = field(default_factory=ToolPermission)
    enabled: bool = True
    deprecated: bool = False
    deprecation_message: Optional[str] = None

@dataclass
class RegisteredTool:
    """Registered tool with metadata and handler"""
    metadata: ToolMetadata
    handler: Callable
    input_schema: type
    output_schema: type
    registered_at: datetime = field(default_factory=datetime.utcnow)
    call_count: int = 0
    last_called: Optional[datetime] = None
    error_count: int = 0

class ToolRegistry:
    """Central registry for managing tools"""
    
    def __init__(self):
        self._tools: Dict[str, RegisteredTool] = {}
        self._type_mapping: Dict[ToolType, List[str]] = {}
        self._call_history: List[Dict[str, Any]] = []
        self._max_history = 1000
    
    def register_tool(
        self,
        name: str,
        tool_type: ToolType,
        handler: Callable,
        input_schema: type,
        output_schema: type,
        description: str = "",
        permission: Optional[ToolPermission] = None,
        **metadata_kwargs
    ) -> None:
        """
        Register a new tool
        
        Args:
            name: Unique tool name
            tool_type: Type of tool
            handler: Tool execution function
            input_schema: Pydantic input schema class
            output_schema: Pydantic output schema class
            description: Tool description
            permission: Permission configuration
            **metadata_kwargs: Additional metadata
        """
        
        if name in self._tools:
            raise ValueError(f"Tool '{name}' is already registered")
        
        # Validate handler signature
        self._validate_handler(handler)
        
        # Create metadata
        metadata = ToolMetadata(
            name=name,
            tool_type=tool_type,
            description=description,
            permission=permission or ToolPermission(),
            **metadata_kwargs
        )
        
        # Register tool
        registered_tool = RegisteredTool(
            metadata=metadata,
            handler=handler,
            input_schema=input_schema,
            output_schema=output_schema
        )
        
        self._tools[name] = registered_tool
        
        # Update type mapping
        if tool_type not in self._type_mapping:
            self._type_mapping[tool_type] = []
        self._type_mapping[tool_type].append(name)
        
        logger.info(f"Registered tool: {name} (type: {tool_type})")
    
    def unregister_tool(self, name: str) -> bool:
        """
        Unregister a tool
        
        Args:
            name: Tool name to unregister
            
        Returns:
            True if tool was unregistered, False if not found
        """
        if name not in self._tools:
            return False
        
        tool = self._tools[name]
        tool_type = tool.metadata.tool_type
        
        # Remove from registry
        del self._tools[name]
        
        # Update type mapping
        if tool_type in self._type_mapping:
            self._type_mapping[tool_type].remove(name)
            if not self._type_mapping[tool_type]:
                del self._type_mapping[tool_type]
        
        logger.info(f"Unregistered tool: {name}")
        return True
    
    def get_tool(self, name: str) -> Optional[RegisteredTool]:
        """Get a registered tool by name"""
        return self._tools.get(name)
    
    def list_tools(
        self,
        tool_type: Optional[ToolType] = None,
        permission_level: Optional[PermissionLevel] = None,
        enabled_only: bool = True
    ) -> List[RegisteredTool]:
        """
        List registered tools with optional filtering
        
        Args:
            tool_type: Filter by tool type
            permission_level: Filter by permission level
            enabled_only: Only return enabled tools
            
        Returns:
            List of matching tools
        """
        tools = list(self._tools.values())
        
        if tool_type:
            tools = [t for t in tools if t.metadata.tool_type == tool_type]
        
        if permission_level:
            tools = [t for t in tools if t.metadata.permission.level == permission_level]
        
        if enabled_only:
            tools = [t for t in tools if t.metadata.enabled and not t.metadata.deprecated]
        
        return sorted(tools, key=lambda t: t.metadata.name)
    
    def get_tools_by_type(self, tool_type: ToolType) -> List[str]:
        """Get tool names by type"""
        return self._type_mapping.get(tool_type, [])
    
    async def execute_tool(
        self,
        name: str,
        input_data: Dict[str, Any],
        user_id: Optional[str] = None,
        user_roles: Optional[Set[str]] = None
    ) -> Dict[str, Any]:
        """
        Execute a registered tool
        
        Args:
            name: Tool name
            input_data: Tool input data
            user_id: User identifier for permission checking
            user_roles: User roles for permission checking
            
        Returns:
            Tool execution result
        """
        
        # Get tool
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found")
        
        # Check if tool is enabled
        if not tool.metadata.enabled:
            raise ValueError(f"Tool '{name}' is disabled")
        
        # Check deprecation
        if tool.metadata.deprecated:
            logger.warning(f"Tool '{name}' is deprecated: {tool.metadata.deprecation_message}")
        
        # Check permissions
        if not self._check_permissions(tool, user_id, user_roles):
            raise PermissionError(f"Insufficient permissions to execute tool '{name}'")
        
        # Validate input
        try:
            validated_input = tool.input_schema(**input_data)
        except Exception as e:
            raise ValueError(f"Invalid input for tool '{name}': {e}")
        
        # Execute tool
        start_time = datetime.utcnow()
        try:
            # Call handler
            if asyncio.iscoroutinefunction(tool.handler):
                result = await tool.handler(validated_input.dict())
            else:
                result = tool.handler(validated_input.dict())
            
            # Validate output
            validated_output = tool.output_schema(**result)
            
            # Update statistics
            tool.call_count += 1
            tool.last_called = datetime.utcnow()
            
            # Record call history
            self._record_call(name, input_data, result, start_time, True)
            
            return validated_output.dict()
            
        except Exception as e:
            tool.error_count += 1
            self._record_call(name, input_data, {"error": str(e)}, start_time, False)
            raise
    
    def _validate_handler(self, handler: Callable) -> None:
        """Validate tool handler signature"""
        if not callable(handler):
            raise ValueError("Handler must be callable")
        
        # Check signature
        sig = inspect.signature(handler)
        params = list(sig.parameters.values())
        
        if len(params) != 1:
            raise ValueError("Handler must accept exactly one parameter (input_data)")
        
        param = params[0]
        if param.annotation != Dict[str, Any] and param.annotation != inspect.Parameter.empty:
            logger.warning(f"Handler parameter should be annotated as Dict[str, Any]")
    
    def _check_permissions(
        self,
        tool: RegisteredTool,
        user_id: Optional[str],
        user_roles: Optional[Set[str]]
    ) -> bool:
        """Check if user has permission to execute tool"""
        permission = tool.metadata.permission
        
        # Public tools are always allowed
        if permission.level == PermissionLevel.PUBLIC:
            return True
        
        # System tools require special handling
        if permission.level == PermissionLevel.SYSTEM:
            return False  # System tools cannot be called directly
        
        # Check authentication requirement
        if permission.level in [PermissionLevel.AUTHENTICATED, PermissionLevel.ADMIN]:
            if not user_id:
                return False
        
        # Check admin requirement
        if permission.level == PermissionLevel.ADMIN:
            if not user_roles or "admin" not in user_roles:
                return False
        
        # Check specific user allowlist
        if permission.allowed_users:
            if not user_id or user_id not in permission.allowed_users:
                return False
        
        # Check role allowlist
        if permission.allowed_roles:
            if not user_roles or not permission.allowed_roles.intersection(user_roles):
                return False
        
        return True
    
    def _record_call(
        self,
        tool_name: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        start_time: datetime,
        success: bool
    ) -> None:
        """Record tool call in history"""
        call_record = {
            "tool_name": tool_name,
            "timestamp": start_time.isoformat(),
            "duration_ms": (datetime.utcnow() - start_time).total_seconds() * 1000,
            "success": success,
            "input_size": len(str(input_data)),
            "output_size": len(str(output_data))
        }
        
        self._call_history.append(call_record)
        
        # Trim history if too long
        if len(self._call_history) > self._max_history:
            self._call_history = self._call_history[-self._max_history:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics"""
        total_tools = len(self._tools)
        enabled_tools = len([t for t in self._tools.values() if t.metadata.enabled])
        deprecated_tools = len([t for t in self._tools.values() if t.metadata.deprecated])
        
        total_calls = sum(t.call_count for t in self._tools.values())
        total_errors = sum(t.error_count for t in self._tools.values())
        
        return {
            "total_tools": total_tools,
            "enabled_tools": enabled_tools,
            "deprecated_tools": deprecated_tools,
            "total_calls": total_calls,
            "total_errors": total_errors,
            "success_rate": (total_calls - total_errors) / total_calls if total_calls > 0 else 0,
            "tools_by_type": {
                tool_type.value: len(tools) 
                for tool_type, tools in self._type_mapping.items()
            }
        }
    
    def get_call_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent call history"""
        return self._call_history[-limit:]
    
    def export_registry(self) -> Dict[str, Any]:
        """Export registry configuration"""
        return {
            "tools": {
                name: {
                    "metadata": {
                        "name": tool.metadata.name,
                        "tool_type": tool.metadata.tool_type.value,
                        "description": tool.metadata.description,
                        "version": tool.metadata.version,
                        "author": tool.metadata.author,
                        "tags": tool.metadata.tags,
                        "enabled": tool.metadata.enabled,
                        "deprecated": tool.metadata.deprecated,
                        "deprecation_message": tool.metadata.deprecation_message,
                    },
                    "permission": {
                        "level": tool.metadata.permission.level.value,
                        "rate_limit_per_minute": tool.metadata.permission.rate_limit_per_minute,
                        "max_concurrent_calls": tool.metadata.permission.max_concurrent_calls,
                    },
                    "statistics": {
                        "registered_at": tool.registered_at.isoformat(),
                        "call_count": tool.call_count,
                        "error_count": tool.error_count,
                        "last_called": tool.last_called.isoformat() if tool.last_called else None,
                    }
                }
                for name, tool in self._tools.items()
            },
            "statistics": self.get_statistics()
        }

# Global registry instance
_global_registry = ToolRegistry()

def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance"""
    return _global_registry

def register_tool(
    name: str,
    tool_type: ToolType,
    input_schema: type,
    output_schema: type,
    description: str = "",
    permission: Optional[ToolPermission] = None,
    **metadata_kwargs
):
    """
    Decorator for registering tools
    
    Usage:
        @register_tool("my_tool", ToolType.CUSTOM, MyInput, MyOutput, "Description")
        async def my_tool_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
            # Tool implementation
            return {"result": "success"}
    """
    def decorator(handler: Callable):
        _global_registry.register_tool(
            name=name,
            tool_type=tool_type,
            handler=handler,
            input_schema=input_schema,
            output_schema=output_schema,
            description=description,
            permission=permission,
            **metadata_kwargs
        )
        return handler
    
    return decorator
