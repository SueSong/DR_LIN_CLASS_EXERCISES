"""
File Operations Tool with workspace sandbox and path traversal protection
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
import mimetypes
import hashlib
import logging
from pydantic import BaseModel, ValidationError, Field
from observability.otel import get_tracer

logger = logging.getLogger(__name__)
tracer = get_tracer(__name__)

class FileOperationRequest(BaseModel):
    """Schema for file operation requests"""
    operation: str = Field(..., description="Operation type: read, write, list, delete, copy, move, mkdir")
    path: str = Field(..., description="Target file or directory path")
    content: Optional[str] = Field(default=None, description="Content for write operations")
    destination: Optional[str] = Field(default=None, description="Destination path for copy/move operations")
    encoding: Optional[str] = Field(default="utf-8", description="File encoding")
    create_dirs: Optional[bool] = Field(default=False, description="Create parent directories if they don't exist")

class FileOperationResult(BaseModel):
    """Schema for file operation results"""
    success: bool
    operation: str
    path: str
    data: Optional[Union[str, List[Dict[str, Any]]]] = None
    size: Optional[int] = None
    mime_type: Optional[str] = None
    checksum: Optional[str] = None
    error: Optional[str] = None

@dataclass
class WorkspaceSandbox:
    """Workspace sandbox configuration"""
    root_path: Path
    max_file_size: int = 10 * 1024 * 1024  # 10MB default
    allowed_extensions: Optional[List[str]] = None
    blocked_extensions: List[str] = None
    
    def __post_init__(self):
        if self.blocked_extensions is None:
            self.blocked_extensions = ['.exe', '.bat', '.cmd', '.sh', '.ps1', '.scr']
        
        # Ensure root path exists and is absolute
        self.root_path = self.root_path.resolve()
        self.root_path.mkdir(parents=True, exist_ok=True)

class FileOperations:
    """File operations tool with security features"""
    
    def __init__(self, workspace_root: Optional[str] = None):
        # Set up workspace sandbox
        if workspace_root:
            root_path = Path(workspace_root)
        else:
            # Default to a sandbox directory
            root_path = Path.cwd() / "workspace"
        
        self.sandbox = WorkspaceSandbox(
            root_path=root_path,
            max_file_size=10 * 1024 * 1024,  # 10MB
            blocked_extensions=['.exe', '.bat', '.cmd', '.ps1', '.scr', '.com', '.pif']
        )
        
        logger.info(f"File operations sandbox initialized at: {self.sandbox.root_path}")
    
    async def execute(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a file operation with validation
        
        Args:
            request_data: File operation request data
            
        Returns:
            File operation result dictionary
        """
        
        with tracer.start_as_current_span("file_operation") as span:
            span.set_attribute("tool.name", "file_ops")
            
            try:
                # Validate request schema
                request = FileOperationRequest(**request_data)
                span.set_attribute("file.operation", request.operation)
                span.set_attribute("file.path", request.path)
                
                # Normalize and validate path
                safe_path = self._normalize_path(request.path)
                span.set_attribute("file.safe_path", str(safe_path))
                
                # Execute operation
                result = await self._execute_operation(request, safe_path, span)
                return result.dict()
                
            except ValidationError as e:
                error_msg = f"Invalid request schema: {e}"
                span.set_attribute("status", "error")
                span.set_attribute("error.message", error_msg)
                return FileOperationResult(
                    success=False, 
                    operation=request_data.get("operation", "unknown"),
                    path=request_data.get("path", ""),
                    error=error_msg
                ).dict()
                
            except Exception as e:
                error_msg = f"File operation failed: {str(e)}"
                span.set_attribute("status", "error")
                span.set_attribute("error.message", error_msg)
                logger.error(f"File operation error: {e}")
                return FileOperationResult(
                    success=False,
                    operation=request_data.get("operation", "unknown"),
                    path=request_data.get("path", ""),
                    error=error_msg
                ).dict()
    
    def _normalize_path(self, path: str) -> Path:
        """
        Normalize path and prevent directory traversal attacks
        
        Args:
            path: Input path string
            
        Returns:
            Normalized Path object within sandbox
            
        Raises:
            ValueError: If path is outside sandbox or invalid
        """
        # Convert to Path object and resolve
        input_path = Path(path)
        
        # If path is absolute, make it relative to sandbox root
        if input_path.is_absolute():
            # Remove the root component and make relative
            try:
                relative_path = input_path.relative_to(input_path.anchor)
            except ValueError:
                relative_path = Path(*input_path.parts[1:])
        else:
            relative_path = input_path
        
        # Resolve the path within sandbox
        resolved_path = (self.sandbox.root_path / relative_path).resolve()
        
        # Security check: ensure path is within sandbox
        try:
            resolved_path.relative_to(self.sandbox.root_path)
        except ValueError:
            raise ValueError(f"Path outside sandbox: {path}")
        
        return resolved_path
    
    def _validate_file_extension(self, path: Path) -> bool:
        """Validate file extension against allowed/blocked lists"""
        extension = path.suffix.lower()
        
        # Check blocked extensions
        if extension in self.sandbox.blocked_extensions:
            return False
        
        # Check allowed extensions (if specified)
        if self.sandbox.allowed_extensions:
            return extension in self.sandbox.allowed_extensions
        
        return True
    
    async def _execute_operation(self, request: FileOperationRequest, safe_path: Path, span) -> FileOperationResult:
        """Execute the actual file operation"""
        operation = request.operation.lower()
        
        if operation == "read":
            return await self._read_file(safe_path, request.encoding, span)
        elif operation == "write":
            return await self._write_file(safe_path, request.content, request.encoding, request.create_dirs, span)
        elif operation == "list":
            return await self._list_directory(safe_path, span)
        elif operation == "delete":
            return await self._delete_path(safe_path, span)
        elif operation == "copy":
            dest_path = self._normalize_path(request.destination) if request.destination else None
            return await self._copy_path(safe_path, dest_path, span)
        elif operation == "move":
            dest_path = self._normalize_path(request.destination) if request.destination else None
            return await self._move_path(safe_path, dest_path, span)
        elif operation == "mkdir":
            return await self._create_directory(safe_path, span)
        else:
            raise ValueError(f"Unsupported operation: {operation}")
    
    async def _read_file(self, path: Path, encoding: str, span) -> FileOperationResult:
        """Read file content"""
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        if not path.is_file():
            raise ValueError(f"Path is not a file: {path}")
        
        # Check file size
        file_size = path.stat().st_size
        if file_size > self.sandbox.max_file_size:
            raise ValueError(f"File too large: {file_size} bytes (max: {self.sandbox.max_file_size})")
        
        # Read content
        try:
            content = path.read_text(encoding=encoding)
            mime_type, _ = mimetypes.guess_type(str(path))
            checksum = self._calculate_checksum(path)
            
            span.set_attribute("file.size", file_size)
            span.set_attribute("status", "success")
            
            return FileOperationResult(
                success=True,
                operation="read",
                path=str(path),
                data=content,
                size=file_size,
                mime_type=mime_type,
                checksum=checksum
            )
        except UnicodeDecodeError:
            # Try binary read for non-text files
            content_bytes = path.read_bytes()
            return FileOperationResult(
                success=True,
                operation="read",
                path=str(path),
                data=f"<binary file: {len(content_bytes)} bytes>",
                size=len(content_bytes),
                mime_type=mimetypes.guess_type(str(path))[0],
                checksum=hashlib.md5(content_bytes).hexdigest()
            )
    
    async def _write_file(self, path: Path, content: str, encoding: str, create_dirs: bool, span) -> FileOperationResult:
        """Write content to file"""
        if content is None:
            raise ValueError("Content is required for write operation")
        
        # Validate file extension
        if not self._validate_file_extension(path):
            raise ValueError(f"File extension not allowed: {path.suffix}")
        
        # Check content size
        content_size = len(content.encode(encoding))
        if content_size > self.sandbox.max_file_size:
            raise ValueError(f"Content too large: {content_size} bytes (max: {self.sandbox.max_file_size})")
        
        # Create parent directories if requested
        if create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write content
        path.write_text(content, encoding=encoding)
        
        # Calculate checksum
        checksum = self._calculate_checksum(path)
        
        span.set_attribute("file.size", content_size)
        span.set_attribute("status", "success")
        
        return FileOperationResult(
            success=True,
            operation="write",
            path=str(path),
            size=content_size,
            checksum=checksum
        )
    
    async def _list_directory(self, path: Path, span) -> FileOperationResult:
        """List directory contents"""
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {path}")
        
        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {path}")
        
        # List contents
        entries = []
        for item in path.iterdir():
            try:
                stat = item.stat()
                mime_type, _ = mimetypes.guess_type(str(item))
                
                entry = {
                    "name": item.name,
                    "path": str(item.relative_to(self.sandbox.root_path)),
                    "type": "directory" if item.is_dir() else "file",
                    "size": stat.st_size if item.is_file() else None,
                    "modified": stat.st_mtime,
                    "mime_type": mime_type if item.is_file() else None
                }
                entries.append(entry)
            except (OSError, PermissionError) as e:
                logger.warning(f"Could not stat {item}: {e}")
                continue
        
        # Sort by name
        entries.sort(key=lambda x: (x["type"] == "file", x["name"]))
        
        span.set_attribute("directory.entry_count", len(entries))
        span.set_attribute("status", "success")
        
        return FileOperationResult(
            success=True,
            operation="list",
            path=str(path),
            data=entries
        )
    
    async def _delete_path(self, path: Path, span) -> FileOperationResult:
        """Delete file or directory"""
        if not path.exists():
            raise FileNotFoundError(f"Path not found: {path}")
        
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)
        else:
            raise ValueError(f"Cannot delete: {path}")
        
        span.set_attribute("status", "success")
        
        return FileOperationResult(
            success=True,
            operation="delete",
            path=str(path)
        )
    
    async def _copy_path(self, src_path: Path, dest_path: Path, span) -> FileOperationResult:
        """Copy file or directory"""
        if not src_path.exists():
            raise FileNotFoundError(f"Source not found: {src_path}")
        
        if dest_path is None:
            raise ValueError("Destination path is required for copy operation")
        
        if src_path.is_file():
            # Validate destination file extension
            if not self._validate_file_extension(dest_path):
                raise ValueError(f"Destination file extension not allowed: {dest_path.suffix}")
            
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dest_path)
        elif src_path.is_dir():
            shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
        
        span.set_attribute("file.destination", str(dest_path))
        span.set_attribute("status", "success")
        
        return FileOperationResult(
            success=True,
            operation="copy",
            path=str(src_path),
            data=str(dest_path)
        )
    
    async def _move_path(self, src_path: Path, dest_path: Path, span) -> FileOperationResult:
        """Move file or directory"""
        if not src_path.exists():
            raise FileNotFoundError(f"Source not found: {src_path}")
        
        if dest_path is None:
            raise ValueError("Destination path is required for move operation")
        
        # Validate destination file extension for files
        if src_path.is_file() and not self._validate_file_extension(dest_path):
            raise ValueError(f"Destination file extension not allowed: {dest_path.suffix}")
        
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src_path), str(dest_path))
        
        span.set_attribute("file.destination", str(dest_path))
        span.set_attribute("status", "success")
        
        return FileOperationResult(
            success=True,
            operation="move",
            path=str(src_path),
            data=str(dest_path)
        )
    
    async def _create_directory(self, path: Path, span) -> FileOperationResult:
        """Create directory"""
        path.mkdir(parents=True, exist_ok=True)
        
        span.set_attribute("status", "success")
        
        return FileOperationResult(
            success=True,
            operation="mkdir",
            path=str(path)
        )
    
    def _calculate_checksum(self, path: Path) -> str:
        """Calculate MD5 checksum of file"""
        if not path.is_file():
            return ""
        
        hash_md5 = hashlib.md5()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def get_sandbox_info(self) -> Dict[str, Any]:
        """Get sandbox configuration information"""
        return {
            "root_path": str(self.sandbox.root_path),
            "max_file_size": self.sandbox.max_file_size,
            "allowed_extensions": self.sandbox.allowed_extensions,
            "blocked_extensions": self.sandbox.blocked_extensions
        }

# Global instance for the API
_global_file_ops = None

def get_file_operations() -> FileOperations:
    """Get global file operations instance"""
    global _global_file_ops
    if _global_file_ops is None:
        _global_file_ops = FileOperations()
    return _global_file_ops
