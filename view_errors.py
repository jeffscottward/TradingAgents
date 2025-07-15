#!/usr/bin/env python
"""
Simple script to view error logs from TradingAgents
"""
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def view_latest_errors():
    """View the latest error log file"""
    error_logs_dir = Path("error_logs")
    
    if not error_logs_dir.exists():
        console.print("[yellow]No error logs found.[/yellow]")
        return
    
    # Find the latest error log file
    error_files = sorted(error_logs_dir.glob("errors_*.json"), reverse=True)
    
    if not error_files:
        console.print("[yellow]No error log files found.[/yellow]")
        return
    
    latest_file = error_files[0]
    console.print(f"[cyan]Viewing errors from: {latest_file.name}[/cyan]\n")
    
    with open(latest_file, 'r') as f:
        errors = json.load(f)
    
    if not errors:
        console.print("[green]No errors recorded in this session.[/green]")
        return
    
    # Create a table
    table = Table(title=f"Errors ({len(errors)} total)")
    table.add_column("Time", style="cyan")
    table.add_column("Type", style="red")
    table.add_column("Component", style="yellow")
    table.add_column("Ticker", style="green")
    table.add_column("Message", style="white")
    
    for error in errors:
        time = error['timestamp'].split('T')[1].split('.')[0]
        table.add_row(
            time,
            error['error_type'],
            error['component'],
            error.get('ticker', '-'),
            error['error_message'][:50] + "..." if len(error['error_message']) > 50 else error['error_message']
        )
    
    console.print(table)
    
    # Show summary
    console.print("\n[bold]Error Summary:[/bold]")
    error_types = {}
    for error in errors:
        error_type = error['error_type']
        error_types[error_type] = error_types.get(error_type, 0) + 1
    
    for error_type, count in error_types.items():
        console.print(f"  {error_type}: {count}")

if __name__ == "__main__":
    view_latest_errors()