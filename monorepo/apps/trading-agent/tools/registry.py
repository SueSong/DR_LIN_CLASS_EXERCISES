"""
Exercise 2: Tool Registry with Metadata
Central registry for all trading agent tools with permissions and sandboxing (Exercise 5)
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable, Set, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from functools import wraps
import inspect

from .schemas import BaseToolInput, BaseToolOutput, ToolStatus

logger = logging.getLogger(__name__)

class PermissionLevel(str, Enum):
    """Permission levels for tools (Exercise 5)"""
    PUBLIC = "public"           # Anyone can use
    AUTHENTICATED = "authenticated"  # Requires authentication
    TRADER = "trader"          # Trading permissions required
    ADMIN = "admin"            # Admin only
    SYSTEM = "system"          # System internal use only

class ToolCategory(str, Enum):
    """Tool categories for organization"""
    MARKET_DATA = "market_data"
    TRADING = "trading"
    PORTFOLIO = "portfolio"
    ANALYSIS = "analysis"
    REPORTING = "reporting"
    DATABASE = "database"
    FILE_OPS = "file_ops"
    SYSTEM = "system"

@dataclass
class ToolPermission:
    """Tool permission configuration (Exercise 5)"""
    level: PermissionLevel = PermissionLevel.PUBLIC
    allowed_users: Optional[Set[str]] = None
    allowed_roles: Optional[Set[str]] = None
    rate_limit_per_minute: Optional[int] = None
    max_concurrent_calls: Optional[int] = None
    sandbox_enabled: bool = True
    allowed_operations: Optional[List[str]] = None  # For granular permissions

@dataclass
class ToolMetadata:
    """Comprehensive tool metadata"""
    name: str
    description: str
    category: ToolCategory
    input_schema: type
    output_schema: type
    version: str = "1.0.0"
    author: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    permission: ToolPermission = field(default_factory=ToolPermission)
    enabled: bool = True
    deprecated: bool = False
    deprecation_message: Optional[str] = None
    reliability_config: Optional[Dict[str, Any]] = None  # Exercise 3 config

@dataclass
class RegisteredTool:
    """Registered tool with metadata and handler"""
    metadata: ToolMetadata
    handler: Callable
    registered_at: datetime = field(default_factory=datetime.utcnow)
    call_count: int = 0
    success_count: int = 0
    error_count: int = 0
    last_called: Optional[datetime] = None
    avg_execution_time: float = 0.0

class TradingToolRegistry:
    """Central registry for trading agent tools"""
    
    def __init__(self):
        self._tools: Dict[str, RegisteredTool] = {}
        self._categories: Dict[ToolCategory, List[str]] = {}
        self._permissions: Dict[str, ToolPermission] = {}
        self._call_history: List[Dict[str, Any]] = []
        self._max_history = 1000
        
        # Initialize categories
        for category in ToolCategory:
            self._categories[category] = []
    
    def register_tool(
        self,
        name: str,
        description: str,
        category: ToolCategory,
        handler: Callable,
        input_schema: type,
        output_schema: type,
        permission: Optional[ToolPermission] = None,
        **metadata_kwargs
    ) -> None:
        """Register a new tool in the registry"""
        
        if name in self._tools:
            raise ValueError(f"Tool '{name}' is already registered")
        
        # Validate handler signature
        self._validate_handler(handler)
        
        # Create metadata
        metadata = ToolMetadata(
            name=name,
            description=description,
            category=category,
            input_schema=input_schema,
            output_schema=output_schema,
            permission=permission or ToolPermission(),
            **metadata_kwargs
        )
        
        # Register tool
        registered_tool = RegisteredTool(
            metadata=metadata,
            handler=handler
        )
        
        self._tools[name] = registered_tool
        self._categories[category].append(name)
        self._permissions[name] = metadata.permission
        
        logger.info(f"Registered tool: {name} (category: {category}, permission: {metadata.permission.level})")
    
    def unregister_tool(self, name: str) -> bool:
        """Unregister a tool"""
        if name not in self._tools:
            return False
        
        tool = self._tools[name]
        category = tool.metadata.category
        
        # Remove from registry
        del self._tools[name]
        self._categories[category].remove(name)
        del self._permissions[name]
        
        logger.info(f"Unregistered tool: {name}")
        return True
    
    def get_tool(self, name: str) -> Optional[RegisteredTool]:
        """Get a registered tool by name"""
        return self._tools.get(name)
    
    def list_tools(
        self,
        category: Optional[ToolCategory] = None,
        permission_level: Optional[PermissionLevel] = None,
        enabled_only: bool = True,
        user_id: Optional[str] = None,
        user_roles: Optional[Set[str]] = None
    ) -> List[RegisteredTool]:
        """List tools with filtering and permission checking"""
        tools = list(self._tools.values())
        
        # Filter by category
        if category:
            tools = [t for t in tools if t.metadata.category == category]
        
        # Filter by permission level
        if permission_level:
            tools = [t for t in tools if t.metadata.permission.level == permission_level]
        
        # Filter by enabled status
        if enabled_only:
            tools = [t for t in tools if t.metadata.enabled and not t.metadata.deprecated]
        
        # Filter by user permissions (Exercise 5)
        if user_id or user_roles:
            tools = [t for t in tools if self._check_permissions(t, user_id, user_roles)]
        
        return sorted(tools, key=lambda t: t.metadata.name)
    
    def get_tools_by_category(self, category: ToolCategory) -> List[str]:
        """Get tool names by category"""
        return self._categories.get(category, [])
    
    async def execute_tool(
        self,
        name: str,
        input_data: Dict[str, Any],
        user_id: Optional[str] = None,
        user_roles: Optional[Set[str]] = None,
        trace_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a registered tool with permission checking and observability"""
        
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
        
        # Check permissions (Exercise 5)
        if not self._check_permissions(tool, user_id, user_roles):
            raise PermissionError(f"Insufficient permissions to execute tool '{name}'")
        
        # Validate input
        try:
            validated_input = tool.metadata.input_schema(**input_data)
        except Exception as e:
            raise ValueError(f"Invalid input for tool '{name}': {e}")
        
        # Execute tool with observability (Exercise 4)
        start_time = datetime.utcnow()
        try:
            # Add sandboxing wrapper if enabled (Exercise 5)
            if tool.metadata.permission.sandbox_enabled:
                result = await self._execute_sandboxed(tool, validated_input.dict(), trace_context)
            else:
                result = await self._execute_direct(tool, validated_input.dict(), trace_context)
            
            # Validate output
            validated_output = tool.metadata.output_schema(**result)
            
            # Update statistics
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._update_tool_stats(tool, True, execution_time)
            
            # Record call history
            self._record_call(name, input_data, result, start_time, True, user_id)
            
            return validated_output.dict()
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._update_tool_stats(tool, False, execution_time)
            self._record_call(name, input_data, {"error": str(e)}, start_time, False, user_id)
            raise
    
    async def _execute_sandboxed(
        self, 
        tool: RegisteredTool, 
        input_data: Dict[str, Any],
        trace_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute tool in sandbox (Exercise 5)"""
        # Implement sandboxing logic
        # For now, this is a wrapper that could add resource limits, timeouts, etc.
        
        # Check allowed operations
        permission = tool.metadata.permission
        if permission.allowed_operations:
            operation = input_data.get('operation') or input_data.get('action')
            if operation and operation not in permission.allowed_operations:
                raise PermissionError(f"Operation '{operation}' not allowed for tool '{tool.metadata.name}'")
        
        # Execute with resource limits
        try:
            # Add timeout if specified
            if permission.max_concurrent_calls:
                # In a real implementation, you'd track concurrent calls
                pass
            
            return await self._execute_direct(tool, input_data, trace_context)
            
        except asyncio.TimeoutError:
            raise TimeoutError(f"Tool '{tool.metadata.name}' execution timed out")
    
    async def _execute_direct(
        self, 
        tool: RegisteredTool, 
        input_data: Dict[str, Any],
        trace_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute tool directly"""
        
        # Call handler
        if asyncio.iscoroutinefunction(tool.handler):
            result = await tool.handler(input_data, trace_context)
        else:
            result = tool.handler(input_data, trace_context)
        
        return result
    
    def _validate_handler(self, handler: Callable) -> None:
        """Validate tool handler signature"""
        if not callable(handler):
            raise ValueError("Handler must be callable")
        
        # Check signature
        sig = inspect.signature(handler)
        params = list(sig.parameters.values())
        
        if len(params) < 1:
            raise ValueError("Handler must accept at least one parameter (input_data)")
    
    def _check_permissions(
        self,
        tool: RegisteredTool,
        user_id: Optional[str],
        user_roles: Optional[Set[str]]
    ) -> bool:
        """Check if user has permission to execute tool (Exercise 5)"""
        permission = tool.metadata.permission
        
        # Public tools are always allowed
        if permission.level == PermissionLevel.PUBLIC:
            return True
        
        # System tools require special handling
        if permission.level == PermissionLevel.SYSTEM:
            return False  # System tools cannot be called directly
        
        # Check authentication requirement
        if permission.level in [PermissionLevel.AUTHENTICATED, PermissionLevel.TRADER, PermissionLevel.ADMIN]:
            if not user_id:
                return False
        
        # Check trader permission
        if permission.level == PermissionLevel.TRADER:
            if not user_roles or "trader" not in user_roles:
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
    
    def _update_tool_stats(self, tool: RegisteredTool, success: bool, execution_time: float):
        """Update tool execution statistics"""
        tool.call_count += 1
        tool.last_called = datetime.utcnow()
        
        if success:
            tool.success_count += 1
        else:
            tool.error_count += 1
        
        # Update average execution time
        if tool.call_count == 1:
            tool.avg_execution_time = execution_time
        else:
            tool.avg_execution_time = (
                (tool.avg_execution_time * (tool.call_count - 1) + execution_time) / tool.call_count
            )
    
    def _record_call(
        self,
        tool_name: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        start_time: datetime,
        success: bool,
        user_id: Optional[str] = None
    ) -> None:
        """Record tool call in history"""
        call_record = {
            "tool_name": tool_name,
            "user_id": user_id,
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
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get comprehensive registry statistics"""
        total_tools = len(self._tools)
        enabled_tools = len([t for t in self._tools.values() if t.metadata.enabled])
        deprecated_tools = len([t for t in self._tools.values() if t.metadata.deprecated])
        
        total_calls = sum(t.call_count for t in self._tools.values())
        total_successes = sum(t.success_count for t in self._tools.values())
        total_errors = sum(t.error_count for t in self._tools.values())
        
        category_stats = {}
        for category, tools in self._categories.items():
            category_stats[category.value] = {
                "tool_count": len(tools),
                "total_calls": sum(self._tools[name].call_count for name in tools if name in self._tools),
                "avg_execution_time": sum(self._tools[name].avg_execution_time for name in tools if name in self._tools) / len(tools) if tools else 0
            }
        
        return {
            "total_tools": total_tools,
            "enabled_tools": enabled_tools,
            "deprecated_tools": deprecated_tools,
            "total_calls": total_calls,
            "success_rate": total_successes / total_calls if total_calls > 0 else 0,
            "error_rate": total_errors / total_calls if total_calls > 0 else 0,
            "categories": category_stats,
            "recent_calls": len(self._call_history)
        }
    
    def export_registry(self) -> Dict[str, Any]:
        """Export registry configuration for inspection"""
        return {
            "tools": {
                name: {
                    "metadata": {
                        "name": tool.metadata.name,
                        "description": tool.metadata.description,
                        "category": tool.metadata.category.value,
                        "version": tool.metadata.version,
                        "enabled": tool.metadata.enabled,
                        "deprecated": tool.metadata.deprecated,
                        "tags": tool.metadata.tags,
                    },
                    "permission": {
                        "level": tool.metadata.permission.level.value,
                        "sandbox_enabled": tool.metadata.permission.sandbox_enabled,
                        "rate_limit_per_minute": tool.metadata.permission.rate_limit_per_minute,
                    },
                    "statistics": {
                        "call_count": tool.call_count,
                        "success_count": tool.success_count,
                        "error_count": tool.error_count,
                        "avg_execution_time": tool.avg_execution_time,
                        "last_called": tool.last_called.isoformat() if tool.last_called else None,
                    }
                }
                for name, tool in self._tools.items()
            },
            "statistics": self.get_registry_stats()
        }

# Global registry instance
_global_registry = TradingToolRegistry()

def get_trading_registry() -> TradingToolRegistry:
    """Get the global trading tool registry instance"""
    return _global_registry

def register_trading_tool(
    name: str,
    description: str,
    category: ToolCategory,
    input_schema: type,
    output_schema: type,
    permission: Optional[ToolPermission] = None,
    **metadata_kwargs
):
    """Decorator for registering trading tools"""
    def decorator(handler: Callable):
        _global_registry.register_tool(
            name=name,
            description=description,
            category=category,
            handler=handler,
            input_schema=input_schema,
            output_schema=output_schema,
            permission=permission,
            **metadata_kwargs
        )
        return handler
    
    return decorator
