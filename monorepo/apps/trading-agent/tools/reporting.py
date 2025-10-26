"""
Trading Report Generation Tools
File operations for daily trading reports (Exercise 2 integration)
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from decimal import Decimal
from datetime import datetime, date
import logging

# OpenTelemetry imports
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from .schemas import (
    ReportInput, ReportOutput, FileOperationInput, FileOperationOutput,
    FileOperation, ToolStatus
)
from .registry import (
    register_trading_tool, ToolCategory, ToolPermission, PermissionLevel
)
from .reliability import with_retry, TradingRetryConfigs

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

# Database connection (will be injected)
_db_connection = None

def set_database_connection(db_conn):
    """Set the database connection for reporting tools"""
    global _db_connection
    _db_connection = db_conn

class TradingReportGenerator:
    """Generate comprehensive trading reports"""
    
    def __init__(self, reports_dir: str = "reports"):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)
    
    async def generate_daily_report(
        self,
        user_id: str,
        report_date: date,
        include_charts: bool = False
    ) -> Dict[str, Any]:
        """Generate comprehensive daily trading report"""
        
        with tracer.start_as_current_span("generate_daily_report") as span:
            span.set_attribute("report.type", "daily")
            span.set_attribute("report.date", report_date.isoformat())
            span.set_attribute("user_id", user_id)
            
            try:
                # Gather report data
                report_data = await self._gather_daily_data(user_id, report_date)
                
                # Generate report content
                report_content = self._format_daily_report(report_data, report_date)
                
                # Save report to file
                file_path = await self._save_report_file(
                    user_id, report_date, "daily", report_content
                )
                
                # Save report metadata to database
                report_id = await self._save_report_metadata(
                    user_id, report_date, "daily", file_path, report_data
                )
                
                span.set_attribute("report.id", report_id)
                span.set_attribute("report.file_path", str(file_path))
                span.set_attribute("status", "success")
                
                return {
                    "status": ToolStatus.SUCCESS,
                    "report_id": report_id,
                    "file_path": str(file_path),
                    "report_summary": {
                        "transactions_count": report_data.get("transactions_count", 0),
                        "total_volume": float(report_data.get("total_volume", 0)),
                        "portfolio_value": float(report_data.get("portfolio_value", 0)),
                        "daily_return": float(report_data.get("daily_return", 0))
                    },
                    "performance_metrics": report_data.get("performance_metrics", {}),
                    "timestamp": datetime.utcnow()
                }
                
            except Exception as e:
                span.set_attribute("status", "error")
                span.set_attribute("error.message", str(e))
                span.set_status(Status(StatusCode.ERROR, str(e)))
                
                logger.error(f"Daily report generation failed: {e}")
                return {
                    "status": ToolStatus.ERROR,
                    "error_message": str(e),
                    "timestamp": datetime.utcnow()
                }
    
    async def _gather_daily_data(self, user_id: str, report_date: date) -> Dict[str, Any]:
        """Gather all data needed for daily report"""
        
        if not _db_connection:
            return self._get_mock_daily_data()
        
        # Get transactions for the day
        transactions = await _db_connection.fetch(
            """
            SELECT * FROM transactions 
            WHERE user_id = $1 AND DATE(executed_at) = $2
            ORDER BY executed_at
            """,
            user_id, report_date
        )
        
        # Get portfolio snapshot
        portfolio = await _db_connection.fetch(
            """
            SELECT p.*, sq.price as current_price,
                   (p.shares * sq.price) as market_value,
                   (p.shares * sq.price) - (p.shares * p.avg_cost) as unrealized_pnl
            FROM portfolio p
            LEFT JOIN stock_quotes sq ON p.symbol = sq.symbol
            WHERE p.user_id = $1 AND p.shares > 0
            """,
            user_id
        )
        
        # Get cash balance
        cash_result = await _db_connection.fetchrow(
            "SELECT balance FROM cash_balance WHERE user_id = $1",
            user_id
        )
        cash_balance = Decimal(str(cash_result["balance"])) if cash_result else Decimal("0")
        
        # Calculate metrics
        total_volume = sum(Decimal(str(t["total_amount"])) for t in transactions)
        portfolio_value = sum(Decimal(str(p["market_value"] or 0)) for p in portfolio)
        total_value = cash_balance + portfolio_value
        
        # Get previous day value for return calculation
        prev_day_result = await _db_connection.fetchrow(
            """
            SELECT total_value FROM daily_reports 
            WHERE user_id = $1 AND report_date < $2 
            ORDER BY report_date DESC LIMIT 1
            """,
            user_id, report_date
        )
        
        prev_total_value = Decimal(str(prev_day_result["total_value"])) if prev_day_result else total_value
        daily_return = ((total_value - prev_total_value) / prev_total_value * 100) if prev_total_value > 0 else Decimal("0")
        
        return {
            "transactions": [dict(t) for t in transactions],
            "portfolio": [dict(p) for p in portfolio],
            "cash_balance": cash_balance,
            "portfolio_value": portfolio_value,
            "total_value": total_value,
            "total_volume": total_volume,
            "transactions_count": len(transactions),
            "daily_return": daily_return,
            "performance_metrics": {
                "total_return": sum(Decimal(str(p["unrealized_pnl"] or 0)) for p in portfolio),
                "positions_count": len(portfolio),
                "cash_percentage": (cash_balance / total_value * 100) if total_value > 0 else Decimal("100")
            }
        }
    
    def _get_mock_daily_data(self) -> Dict[str, Any]:
        """Generate mock data for testing"""
        return {
            "transactions": [],
            "portfolio": [],
            "cash_balance": Decimal("1000000"),
            "portfolio_value": Decimal("0"),
            "total_value": Decimal("1000000"),
            "total_volume": Decimal("0"),
            "transactions_count": 0,
            "daily_return": Decimal("0"),
            "performance_metrics": {
                "total_return": Decimal("0"),
                "positions_count": 0,
                "cash_percentage": Decimal("100")
            }
        }
    
    def _format_daily_report(self, data: Dict[str, Any], report_date: date) -> str:
        """Format daily report as readable text"""
        
        report_lines = [
            f"DAILY TRADING REPORT - {report_date.strftime('%B %d, %Y')}",
            "=" * 60,
            "",
            "PORTFOLIO SUMMARY",
            "-" * 20,
            f"Total Portfolio Value: ${data['total_value']:,.2f}",
            f"Cash Balance: ${data['cash_balance']:,.2f} ({data['performance_metrics']['cash_percentage']:.1f}%)",
            f"Invested Amount: ${data['portfolio_value']:,.2f}",
            f"Daily Return: {data['daily_return']:+.2f}%",
            f"Total Positions: {data['performance_metrics']['positions_count']}",
            "",
            "DAILY TRANSACTIONS",
            "-" * 20,
            f"Total Transactions: {data['transactions_count']}",
            f"Total Volume: ${data['total_volume']:,.2f}",
            ""
        ]
        
        # Add transaction details
        if data['transactions']:
            report_lines.append("Transaction Details:")
            for i, tx in enumerate(data['transactions'], 1):
                report_lines.append(
                    f"{i:2d}. {tx['executed_at'].strftime('%H:%M')} - "
                    f"{tx['transaction_type']} {tx['shares']} {tx['symbol']} @ ${tx['price']:.2f} "
                    f"(Total: ${tx['total_amount']:,.2f})"
                )
            report_lines.append("")
        else:
            report_lines.append("No transactions today.")
            report_lines.append("")
        
        # Add portfolio positions
        if data['portfolio']:
            report_lines.extend([
                "CURRENT POSITIONS",
                "-" * 20,
                f"{'Symbol':<8} {'Shares':<10} {'Avg Cost':<10} {'Current':<10} {'Value':<12} {'P&L':<12} {'Return':<8}"
            ])
            
            for pos in data['portfolio']:
                return_pct = ((Decimal(str(pos['current_price'] or 0)) - Decimal(str(pos['avg_cost']))) / Decimal(str(pos['avg_cost'])) * 100) if pos['avg_cost'] > 0 else Decimal("0")
                report_lines.append(
                    f"{pos['symbol']:<8} {pos['shares']:<10.2f} ${pos['avg_cost']:<9.2f} "
                    f"${pos['current_price'] or 0:<9.2f} ${pos['market_value'] or 0:<11,.2f} "
                    f"${pos['unrealized_pnl'] or 0:<11,.2f} {return_pct:>7.1f}%"
                )
            report_lines.append("")
        
        # Add performance summary
        report_lines.extend([
            "PERFORMANCE SUMMARY",
            "-" * 20,
            f"Unrealized P&L: ${data['performance_metrics']['total_return']:,.2f}",
            f"Cash Allocation: {data['performance_metrics']['cash_percentage']:.1f}% (Target: 10%)",
            "",
            "NOTES",
            "-" * 20,
            "• This report is generated automatically by the AI Trading Agent",
            "• All trades are executed based on AI recommendations",
            "• Target cash allocation is 10% for flexibility",
            "",
            f"Report generated at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            ""
        ])
        
        return "\n".join(report_lines)
    
    async def _save_report_file(
        self,
        user_id: str,
        report_date: date,
        report_type: str,
        content: str
    ) -> Path:
        """Save report content to file"""
        
        # Create user-specific directory
        user_dir = self.reports_dir / user_id
        user_dir.mkdir(exist_ok=True)
        
        # Generate filename
        filename = f"{report_type}_report_{report_date.strftime('%Y%m%d')}.txt"
        file_path = user_dir / filename
        
        # Write content to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Saved {report_type} report to {file_path}")
        return file_path
    
    async def _save_report_metadata(
        self,
        user_id: str,
        report_date: date,
        report_type: str,
        file_path: Path,
        report_data: Dict[str, Any]
    ) -> str:
        """Save report metadata to database"""
        
        if not _db_connection:
            return f"mock_report_{report_date.strftime('%Y%m%d')}"
        
        report_id = await _db_connection.fetchval(
            """
            INSERT INTO daily_reports (
                user_id, report_date, starting_balance, ending_balance,
                cash_balance, portfolio_value, total_value, daily_return,
                transactions_count, report_data, file_path
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            ON CONFLICT (user_id, report_date) DO UPDATE SET
                ending_balance = EXCLUDED.ending_balance,
                cash_balance = EXCLUDED.cash_balance,
                portfolio_value = EXCLUDED.portfolio_value,
                total_value = EXCLUDED.total_value,
                daily_return = EXCLUDED.daily_return,
                transactions_count = EXCLUDED.transactions_count,
                report_data = EXCLUDED.report_data,
                file_path = EXCLUDED.file_path
            RETURNING id
            """,
            user_id, report_date,
            report_data.get("total_value", 0),  # starting_balance (simplified)
            report_data.get("total_value", 0),  # ending_balance
            report_data.get("cash_balance", 0),
            report_data.get("portfolio_value", 0),
            report_data.get("total_value", 0),
            report_data.get("daily_return", 0),
            report_data.get("transactions_count", 0),
            json.dumps(report_data, default=str),
            str(file_path)
        )
        
        return str(report_id)

# Global report generator
_global_report_generator = None

def get_report_generator() -> TradingReportGenerator:
    """Get global report generator instance"""
    global _global_report_generator
    if _global_report_generator is None:
        reports_dir = os.getenv("REPORTS_DIR", "reports")
        _global_report_generator = TradingReportGenerator(reports_dir)
    return _global_report_generator

# Register report generation tool
@register_trading_tool(
    name="generate_daily_report",
    description="Generate comprehensive daily trading report",
    category=ToolCategory.REPORTING,
    input_schema=ReportInput,
    output_schema=ReportOutput,
    permission=ToolPermission(
        level=PermissionLevel.AUTHENTICATED,
        sandbox_enabled=True,
        allowed_operations=["daily", "weekly", "monthly"]
    ),
    tags=["reporting", "files", "analysis"],
    version="1.0.0"
)
@with_retry(TradingRetryConfigs.file_operation())
async def generate_daily_report(input_data: Dict[str, Any], trace_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Generate daily trading report and save to file
    Demonstrates Exercise 2 (File Operations) integration
    """
    
    with tracer.start_as_current_span("generate_daily_report_tool") as span:
        span.set_attribute("tool.name", "generate_daily_report")
        
        try:
            user_id = input_data.get("user_id", "default_trader")
            report_date = input_data.get("report_date", date.today())
            report_type = input_data.get("report_type", "daily")
            include_charts = input_data.get("include_charts", False)
            
            if isinstance(report_date, str):
                report_date = datetime.strptime(report_date, "%Y-%m-%d").date()
            
            generator = get_report_generator()
            
            if report_type == "daily":
                result = await generator.generate_daily_report(user_id, report_date, include_charts)
            else:
                raise ValueError(f"Unsupported report type: {report_type}")
            
            span.set_attribute("report.type", report_type)
            span.set_attribute("status", "success")
            
            return result
            
        except Exception as e:
            span.set_attribute("status", "error")
            span.set_attribute("error.message", str(e))
            span.set_status(Status(StatusCode.ERROR, str(e)))
            
            logger.error(f"Report generation tool failed: {e}")
            return {
                "status": ToolStatus.ERROR,
                "error_message": str(e),
                "timestamp": datetime.utcnow()
            }

# File operations tool (Exercise 2 integration)
@register_trading_tool(
    name="file_operations",
    description="Perform file operations for reports and data",
    category=ToolCategory.FILE_OPS,
    input_schema=FileOperationInput,
    output_schema=FileOperationOutput,
    permission=ToolPermission(
        level=PermissionLevel.AUTHENTICATED,
        sandbox_enabled=True,
        allowed_operations=["read", "write", "append"]  # No delete for safety
    ),
    tags=["files", "io", "reports"],
    version="1.0.0"
)
@with_retry(TradingRetryConfigs.file_operation())
async def file_operations(input_data: Dict[str, Any], trace_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Perform sandboxed file operations
    Demonstrates Exercise 5 (Sandboxing) with file access restrictions
    """
    
    with tracer.start_as_current_span("file_operations_tool") as span:
        span.set_attribute("tool.name", "file_operations")
        span.set_attribute("operation", input_data.get("operation"))
        span.set_attribute("file_path", input_data.get("file_path"))
        
        try:
            operation = FileOperation(input_data["operation"])
            file_path = input_data["file_path"]
            content = input_data.get("content")
            encoding = input_data.get("encoding", "utf-8")
            user_id = input_data.get("user_id", "default_trader")
            
            # Sandbox validation - restrict to reports directory
            safe_path = _validate_and_sanitize_path(file_path, user_id)
            
            if operation == FileOperation.READ:
                result_content = await _read_file(safe_path, encoding)
                file_size = safe_path.stat().st_size if safe_path.exists() else 0
                
                return {
                    "status": ToolStatus.SUCCESS,
                    "operation": operation.value,
                    "file_path": str(safe_path),
                    "content": result_content,
                    "file_size": file_size,
                    "timestamp": datetime.utcnow()
                }
            
            elif operation == FileOperation.WRITE:
                if not content:
                    raise ValueError("Content is required for write operation")
                
                file_size = await _write_file(safe_path, content, encoding)
                
                return {
                    "status": ToolStatus.SUCCESS,
                    "operation": operation.value,
                    "file_path": str(safe_path),
                    "file_size": file_size,
                    "timestamp": datetime.utcnow()
                }
            
            elif operation == FileOperation.APPEND:
                if not content:
                    raise ValueError("Content is required for append operation")
                
                file_size = await _append_file(safe_path, content, encoding)
                
                return {
                    "status": ToolStatus.SUCCESS,
                    "operation": operation.value,
                    "file_path": str(safe_path),
                    "file_size": file_size,
                    "timestamp": datetime.utcnow()
                }
            
            else:
                raise ValueError(f"Operation {operation} not allowed in sandbox")
            
        except Exception as e:
            span.set_attribute("status", "error")
            span.set_attribute("error.message", str(e))
            span.set_status(Status(StatusCode.ERROR, str(e)))
            
            logger.error(f"File operations tool failed: {e}")
            return {
                "status": ToolStatus.ERROR,
                "error_message": str(e),
                "operation": input_data.get("operation"),
                "file_path": input_data.get("file_path"),
                "timestamp": datetime.utcnow()
            }

def _validate_and_sanitize_path(file_path: str, user_id: str) -> Path:
    """Validate and sanitize file path for sandbox security"""
    
    # Remove any path traversal attempts
    clean_path = file_path.replace("..", "").replace("//", "/")
    
    # Ensure path is within reports directory
    reports_dir = Path("reports")
    user_dir = reports_dir / user_id
    
    # Create user directory if it doesn't exist
    user_dir.mkdir(parents=True, exist_ok=True)
    
    # Resolve final path
    final_path = user_dir / clean_path
    
    # Ensure the resolved path is still within the user directory
    try:
        final_path.resolve().relative_to(user_dir.resolve())
    except ValueError:
        raise PermissionError("File path outside allowed directory")
    
    return final_path

async def _read_file(file_path: Path, encoding: str) -> str:
    """Read file content"""
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r', encoding=encoding) as f:
        return f.read()

async def _write_file(file_path: Path, content: str, encoding: str) -> int:
    """Write content to file"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding=encoding) as f:
        f.write(content)
    
    return len(content.encode(encoding))

async def _append_file(file_path: Path, content: str, encoding: str) -> int:
    """Append content to file"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'a', encoding=encoding) as f:
        f.write(content)
    
    return file_path.stat().st_size
