"""
Tests for file operations tool with workspace sandbox and path traversal protection
"""

import pytest
import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume

from tools.file_ops import FileOperations, WorkspaceSandbox

class TestWorkspaceSandbox:
    """Test workspace sandbox functionality"""
    
    def test_sandbox_initialization(self, temp_workspace):
        """Test sandbox initialization"""
        sandbox = WorkspaceSandbox(
            root_path=temp_workspace,
            max_file_size=1024,
            blocked_extensions=['.exe', '.bat']
        )
        
        assert sandbox.root_path == temp_workspace.resolve()
        assert sandbox.max_file_size == 1024
        assert '.exe' in sandbox.blocked_extensions
        assert '.bat' in sandbox.blocked_extensions
        assert temp_workspace.exists()

class TestFileOperations:
    """Test file operations functionality"""
    
    @pytest.fixture
    def file_ops(self, temp_workspace):
        """Create file operations instance with temp workspace"""
        return FileOperations(workspace_root=str(temp_workspace))
    
    @pytest.mark.asyncio
    async def test_write_and_read_file(self, file_ops):
        """Test writing and reading a file"""
        # Write file
        write_request = {
            "operation": "write",
            "path": "test.txt",
            "content": "Hello, World!\nThis is a test file.",
            "create_dirs": True
        }
        
        result = await file_ops.execute(write_request)
        
        assert result["success"] is True
        assert result["operation"] == "write"
        assert "size" in result
        assert "checksum" in result
        
        # Read file
        read_request = {
            "operation": "read",
            "path": "test.txt"
        }
        
        result = await file_ops.execute(read_request)
        
        assert result["success"] is True
        assert result["operation"] == "read"
        assert result["data"] == "Hello, World!\nThis is a test file."
        assert result["size"] > 0
        assert "checksum" in result
        assert "mime_type" in result
    
    @pytest.mark.asyncio
    async def test_create_directory_and_list(self, file_ops):
        """Test creating directory and listing contents"""
        # Create directory
        mkdir_request = {
            "operation": "mkdir",
            "path": "test_dir/subdir"
        }
        
        result = await file_ops.execute(mkdir_request)
        
        assert result["success"] is True
        assert result["operation"] == "mkdir"
        
        # Create some files in the directory
        for i in range(3):
            write_request = {
                "operation": "write",
                "path": f"test_dir/file_{i}.txt",
                "content": f"Content of file {i}",
                "create_dirs": True
            }
            await file_ops.execute(write_request)
        
        # List directory contents
        list_request = {
            "operation": "list",
            "path": "test_dir"
        }
        
        result = await file_ops.execute(list_request)
        
        assert result["success"] is True
        assert result["operation"] == "list"
        assert isinstance(result["data"], list)
        assert len(result["data"]) == 4  # 3 files + 1 subdirectory
        
        # Check entry structure
        for entry in result["data"]:
            assert "name" in entry
            assert "path" in entry
            assert "type" in entry
            assert entry["type"] in ["file", "directory"]
    
    @pytest.mark.asyncio
    async def test_copy_file(self, file_ops):
        """Test copying files"""
        # Create source file
        write_request = {
            "operation": "write",
            "path": "source.txt",
            "content": "Original content"
        }
        await file_ops.execute(write_request)
        
        # Copy file
        copy_request = {
            "operation": "copy",
            "path": "source.txt",
            "destination": "copy.txt"
        }
        
        result = await file_ops.execute(copy_request)
        
        assert result["success"] is True
        assert result["operation"] == "copy"
        
        # Verify both files exist and have same content
        for filename in ["source.txt", "copy.txt"]:
            read_request = {"operation": "read", "path": filename}
            read_result = await file_ops.execute(read_request)
            assert read_result["success"] is True
            assert read_result["data"] == "Original content"
    
    @pytest.mark.asyncio
    async def test_move_file(self, file_ops):
        """Test moving files"""
        # Create source file
        write_request = {
            "operation": "write",
            "path": "source.txt",
            "content": "Content to move"
        }
        await file_ops.execute(write_request)
        
        # Move file
        move_request = {
            "operation": "move",
            "path": "source.txt",
            "destination": "moved.txt"
        }
        
        result = await file_ops.execute(move_request)
        
        assert result["success"] is True
        assert result["operation"] == "move"
        
        # Verify source doesn't exist and destination does
        read_source = {"operation": "read", "path": "source.txt"}
        source_result = await file_ops.execute(read_source)
        assert source_result["success"] is False
        
        read_dest = {"operation": "read", "path": "moved.txt"}
        dest_result = await file_ops.execute(read_dest)
        assert dest_result["success"] is True
        assert dest_result["data"] == "Content to move"
    
    @pytest.mark.asyncio
    async def test_delete_file(self, file_ops):
        """Test deleting files"""
        # Create file
        write_request = {
            "operation": "write",
            "path": "to_delete.txt",
            "content": "This will be deleted"
        }
        await file_ops.execute(write_request)
        
        # Delete file
        delete_request = {
            "operation": "delete",
            "path": "to_delete.txt"
        }
        
        result = await file_ops.execute(delete_request)
        
        assert result["success"] is True
        assert result["operation"] == "delete"
        
        # Verify file doesn't exist
        read_request = {"operation": "read", "path": "to_delete.txt"}
        read_result = await file_ops.execute(read_request)
        assert read_result["success"] is False
    
    @pytest.mark.asyncio
    async def test_path_traversal_protection(self, file_ops):
        """Test protection against path traversal attacks"""
        traversal_paths = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config\\sam",
            "/etc/passwd",
            "C:\\Windows\\System32\\config\\SAM",
            "subdir/../../../sensitive_file",
        ]
        
        for path in traversal_paths:
            request = {
                "operation": "read",
                "path": path
            }
            
            result = await file_ops.execute(request)
            
            # Should either fail due to path validation or file not found within sandbox
            assert result["success"] is False
            # The error should indicate path issues or file not found, not system access
    
    @pytest.mark.asyncio
    async def test_blocked_file_extensions(self, file_ops):
        """Test that blocked file extensions are rejected"""
        blocked_extensions = ['.exe', '.bat', '.cmd', '.ps1', '.scr']
        
        for ext in blocked_extensions:
            request = {
                "operation": "write",
                "path": f"malicious{ext}",
                "content": "malicious content"
            }
            
            result = await file_ops.execute(request)
            
            assert result["success"] is False
            assert "extension not allowed" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_file_size_limit(self, file_ops):
        """Test file size limit enforcement"""
        # Create content larger than default limit (10MB)
        large_content = "x" * (11 * 1024 * 1024)  # 11MB
        
        request = {
            "operation": "write",
            "path": "large_file.txt",
            "content": large_content
        }
        
        result = await file_ops.execute(request)
        
        assert result["success"] is False
        assert "too large" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_nonexistent_file_operations(self, file_ops):
        """Test operations on nonexistent files"""
        nonexistent_operations = [
            {"operation": "read", "path": "nonexistent.txt"},
            {"operation": "delete", "path": "nonexistent.txt"},
            {"operation": "copy", "path": "nonexistent.txt", "destination": "copy.txt"},
            {"operation": "move", "path": "nonexistent.txt", "destination": "moved.txt"},
        ]
        
        for request in nonexistent_operations:
            result = await file_ops.execute(request)
            assert result["success"] is False
            assert "not found" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_invalid_operation(self, file_ops):
        """Test handling of invalid operations"""
        request = {
            "operation": "invalid_op",
            "path": "test.txt"
        }
        
        result = await file_ops.execute(request)
        
        assert result["success"] is False
        assert "unsupported operation" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_encoding_handling(self, file_ops):
        """Test different file encodings"""
        # Test UTF-8 content with special characters
        utf8_content = "Hello 世界! 🌍 Ñoño café"
        
        write_request = {
            "operation": "write",
            "path": "utf8_test.txt",
            "content": utf8_content,
            "encoding": "utf-8"
        }
        
        result = await file_ops.execute(write_request)
        assert result["success"] is True
        
        read_request = {
            "operation": "read",
            "path": "utf8_test.txt",
            "encoding": "utf-8"
        }
        
        result = await file_ops.execute(read_request)
        assert result["success"] is True
        assert result["data"] == utf8_content
    
    def test_sandbox_info(self, file_ops):
        """Test getting sandbox information"""
        info = file_ops.get_sandbox_info()
        
        assert "root_path" in info
        assert "max_file_size" in info
        assert "blocked_extensions" in info
        assert isinstance(info["blocked_extensions"], list)

class TestFileOperationsPropertyBased:
    """Property-based tests using Hypothesis"""
    
    @pytest.fixture
    def file_ops(self, temp_workspace):
        return FileOperations(workspace_root=str(temp_workspace))
    
    @given(st.text(
        alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Pc")),
        min_size=1,
        max_size=50
    ).filter(lambda x: not x.startswith('.') and '/' not in x and '\\' not in x))
    @settings(max_examples=10, deadline=5000)
    @pytest.mark.asyncio
    async def test_filename_handling(self, file_ops, filename):
        """Property: Valid filenames can be created and read"""
        assume(not any(filename.endswith(ext) for ext in ['.exe', '.bat', '.cmd', '.ps1', '.scr']))
        
        content = f"Content for {filename}"
        
        # Write file
        write_request = {
            "operation": "write",
            "path": filename,
            "content": content
        }
        
        write_result = await file_ops.execute(write_request)
        
        if write_result["success"]:
            # Read file back
            read_request = {
                "operation": "read",
                "path": filename
            }
            
            read_result = await file_ops.execute(read_request)
            
            assert read_result["success"] is True
            assert read_result["data"] == content
    
    @given(st.text(max_size=1000))
    @settings(max_examples=10, deadline=5000)
    @pytest.mark.asyncio
    async def test_content_preservation(self, file_ops, content):
        """Property: File content is preserved exactly through write/read cycle"""
        # Filter out null bytes which can cause issues
        assume('\x00' not in content)
        
        filename = "test_content.txt"
        
        write_request = {
            "operation": "write",
            "path": filename,
            "content": content
        }
        
        write_result = await file_ops.execute(write_request)
        
        if write_result["success"]:
            read_request = {
                "operation": "read",
                "path": filename
            }
            
            read_result = await file_ops.execute(read_request)
            
            assert read_result["success"] is True
            assert read_result["data"] == content
    
    @given(st.lists(
        st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")),
            min_size=1,
            max_size=20
        ),
        min_size=1,
        max_size=5
    ))
    @settings(max_examples=5, deadline=5000)
    @pytest.mark.asyncio
    async def test_directory_operations(self, file_ops, path_components):
        """Property: Directory paths can be created and listed"""
        # Create nested directory path
        dir_path = "/".join(path_components)
        
        mkdir_request = {
            "operation": "mkdir",
            "path": dir_path
        }
        
        result = await file_ops.execute(mkdir_request)
        
        if result["success"]:
            # List parent directory
            parent_path = "/".join(path_components[:-1]) if len(path_components) > 1 else "."
            
            list_request = {
                "operation": "list",
                "path": parent_path
            }
            
            list_result = await file_ops.execute(list_request)
            
            assert list_result["success"] is True
            assert isinstance(list_result["data"], list)
            
            # Check that our directory appears in the listing
            dir_names = [entry["name"] for entry in list_result["data"] if entry["type"] == "directory"]
            assert path_components[-1] in dir_names
