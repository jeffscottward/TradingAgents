"""
Error logging utilities for TradingAgents
"""
import os
import json
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class ErrorLogger:
    """Centralized error logging for TradingAgents"""
    
    def __init__(self, log_dir: str = "error_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.current_session_file = self.log_dir / f"errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.errors = []
    
    def log_error(
        self,
        error_type: str,
        error_message: str,
        component: str,
        ticker: Optional[str] = None,
        additional_context: Optional[Dict[str, Any]] = None,
        exception: Optional[Exception] = None
    ):
        """Log an error with context"""
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "error_message": error_message,
            "component": component,
            "ticker": ticker,
            "additional_context": additional_context or {},
        }
        
        # Add traceback if exception provided
        if exception:
            error_entry["traceback"] = traceback.format_exception(
                type(exception), exception, exception.__traceback__
            )
        
        self.errors.append(error_entry)
        
        # Write to file immediately
        self._write_to_file(error_entry)
        
        # Also write to a master log file
        self._append_to_master_log(error_entry)
    
    def _write_to_file(self, error_entry: Dict[str, Any]):
        """Write error to session file"""
        with open(self.current_session_file, 'w') as f:
            json.dump(self.errors, f, indent=2, default=str)
    
    def _append_to_master_log(self, error_entry: Dict[str, Any]):
        """Append error to master log file"""
        master_log = self.log_dir / "master_error_log.jsonl"
        with open(master_log, 'a') as f:
            f.write(json.dumps(error_entry, default=str) + '\n')
    
    def get_errors_by_type(self, error_type: str) -> list:
        """Get all errors of a specific type"""
        return [e for e in self.errors if e["error_type"] == error_type]
    
    def get_errors_by_ticker(self, ticker: str) -> list:
        """Get all errors for a specific ticker"""
        return [e for e in self.errors if e.get("ticker") == ticker]
    
    def summarize_errors(self) -> Dict[str, Any]:
        """Get a summary of all errors"""
        summary = {
            "total_errors": len(self.errors),
            "errors_by_type": {},
            "errors_by_component": {},
            "errors_by_ticker": {},
        }
        
        for error in self.errors:
            # Count by type
            error_type = error["error_type"]
            summary["errors_by_type"][error_type] = summary["errors_by_type"].get(error_type, 0) + 1
            
            # Count by component
            component = error["component"]
            summary["errors_by_component"][component] = summary["errors_by_component"].get(component, 0) + 1
            
            # Count by ticker
            ticker = error.get("ticker")
            if ticker:
                summary["errors_by_ticker"][ticker] = summary["errors_by_ticker"].get(ticker, 0) + 1
        
        return summary


# Global error logger instance
_error_logger = None

def get_error_logger() -> ErrorLogger:
    """Get or create the global error logger instance"""
    global _error_logger
    if _error_logger is None:
        _error_logger = ErrorLogger()
    return _error_logger