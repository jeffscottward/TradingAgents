from typing import Optional
import os
from dotenv import load_dotenv

# 🚀 ~ load environment variables from .env file
env_loaded = load_dotenv()
if env_loaded:
    print('🌱 ~ Environment variables loaded from .env')
import datetime
import typer
from pathlib import Path
from functools import wraps
from rich.console import Console
from rich.panel import Panel
from rich.spinner import Spinner
from rich.live import Live
from rich.columns import Columns
from rich.markdown import Markdown
from rich.layout import Layout
from rich.text import Text
from rich.live import Live
from rich.table import Table
from collections import deque
import time
from rich.tree import Tree
from rich import box
from rich.align import Align
from rich.rule import Rule

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.utils.error_logger import get_error_logger
from cli.models import AnalystType
from cli.utils import *
import random

console = Console()

# Rate limiting decorator with exponential backoff
def with_rate_limit(min_delay=1.0, max_delay=60.0, max_retries=5):
    """Decorator to add rate limiting and exponential backoff to functions."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = min_delay
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    # Add a small random jitter to prevent thundering herd
                    jitter = random.uniform(0, delay * 0.1)
                    actual_delay = delay + jitter
                    
                    if attempt > 0:
                        console.print(f"[yellow]Waiting {actual_delay:.1f}s before retry (attempt {attempt + 1}/{max_retries})...[/yellow]")
                        time.sleep(actual_delay)
                    
                    return func(*args, **kwargs)
                    
                except Exception as e:
                    last_exception = e
                    error_msg = str(e).lower()
                    
                    # Check for rate limit errors
                    if any(phrase in error_msg for phrase in ['over capacity', 'rate limit', '503', 'too many requests', '429']):
                        # Exponential backoff
                        delay = min(delay * 2, max_delay)
                        continue
                    else:
                        # For other errors, re-raise immediately
                        raise
            
            # If we've exhausted all retries, raise the last exception
            if last_exception:
                raise last_exception
                
        return wrapper
    return decorator

app = typer.Typer(
    name="TradingAgents",
    help="TradingAgents CLI: Multi-Agents LLM Financial Trading Framework",
    add_completion=True,  # Enable shell completion
)


# Create a deque to store recent messages with a maximum length
class MessageBuffer:
    def __init__(self, max_length=100):
        self.messages = deque(maxlen=max_length)
        self.tool_calls = deque(maxlen=max_length)
        self.current_report = None
        self.final_report = None  # Store the complete final report
        self.agent_status = {
            # Analyst Team
            "Market Analyst": "pending",
            "Social Analyst": "pending",
            "News Analyst": "pending",
            "Fundamentals Analyst": "pending",
            # Research Team
            "Bull Researcher": "pending",
            "Bear Researcher": "pending",
            "Research Manager": "pending",
            # Trading Team
            "Trader": "pending",
            # Risk Management Team
            "Risky Analyst": "pending",
            "Neutral Analyst": "pending",
            "Safe Analyst": "pending",
            # Portfolio Management Team
            "Portfolio Manager": "pending",
        }
        self.current_agent = None
        self.report_sections = {
            "market_report": None,
            "sentiment_report": None,
            "news_report": None,
            "fundamentals_report": None,
            "investment_plan": None,
            "trader_investment_plan": None,
            "final_trade_decision": None,
        }

    def add_message(self, message_type, content):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.messages.append((timestamp, message_type, content))

    def add_tool_call(self, tool_name, args):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.tool_calls.append((timestamp, tool_name, args))

    def update_agent_status(self, agent, status):
        if agent in self.agent_status:
            self.agent_status[agent] = status
            self.current_agent = agent

    def update_report_section(self, section_name, content):
        if section_name in self.report_sections:
            self.report_sections[section_name] = content
            self._update_current_report()

    def _update_current_report(self):
        # For the panel display, only show the most recently updated section
        latest_section = None
        latest_content = None

        # Find the most recently updated section
        for section, content in self.report_sections.items():
            if content is not None:
                latest_section = section
                latest_content = content
               
        if latest_section and latest_content:
            # Format the current section for display
            section_titles = {
                "market_report": "Market Analysis",
                "sentiment_report": "Social Sentiment",
                "news_report": "News Analysis",
                "fundamentals_report": "Fundamentals Analysis",
                "investment_plan": "Research Team Decision",
                "trader_investment_plan": "Trading Team Plan",
                "final_trade_decision": "Portfolio Management Decision",
            }
            self.current_report = (
                f"### {section_titles[latest_section]}\n{latest_content}"
            )

        # Update the final complete report
        self._update_final_report()

    def _update_final_report(self):
        report_parts = []

        # Analyst Team Reports
        if any(
            self.report_sections[section]
            for section in [
                "market_report",
                "sentiment_report",
                "news_report",
                "fundamentals_report",
            ]
        ):
            report_parts.append("## Analyst Team Reports")
            if self.report_sections["market_report"]:
                report_parts.append(
                    f"### Market Analysis\n{self.report_sections['market_report']}"
                )
            if self.report_sections["sentiment_report"]:
                report_parts.append(
                    f"### Social Sentiment\n{self.report_sections['sentiment_report']}"
                )
            if self.report_sections["news_report"]:
                report_parts.append(
                    f"### News Analysis\n{self.report_sections['news_report']}"
                )
            if self.report_sections["fundamentals_report"]:
                report_parts.append(
                    f"### Fundamentals Analysis\n{self.report_sections['fundamentals_report']}"
                )

        # Research Team Reports
        if self.report_sections["investment_plan"]:
            report_parts.append("## Research Team Decision")
            report_parts.append(f"{self.report_sections['investment_plan']}")

        # Trading Team Reports
        if self.report_sections["trader_investment_plan"]:
            report_parts.append("## Trading Team Plan")
            report_parts.append(f"{self.report_sections['trader_investment_plan']}")

        # Portfolio Management Decision
        if self.report_sections["final_trade_decision"]:
            report_parts.append("## Portfolio Management Decision")
            report_parts.append(f"{self.report_sections['final_trade_decision']}")

        self.final_report = "\n\n".join(report_parts) if report_parts else None


message_buffer = MessageBuffer()


def create_layout():
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="footer", size=3),
    )
    layout["main"].split_column(
        Layout(name="upper", ratio=3), Layout(name="analysis", ratio=5)
    )
    layout["upper"].split_row(
        Layout(name="progress", ratio=2), Layout(name="messages", ratio=3)
    )
    return layout


def update_display(layout, spinner_text=None):
    # Header with welcome message
    layout["header"].update(
        Panel(
            "[bold green]Welcome to TradingAgents CLI[/bold green]\n"
            "[dim]© [Tauric Research](https://github.com/TauricResearch)[/dim]",
            title="Welcome to TradingAgents",
            border_style="green",
            padding=(1, 2),
            expand=True,
        )
    )

    # Progress panel showing agent status
    progress_table = Table(
        show_header=True,
        header_style="bold magenta",
        show_footer=False,
        box=box.SIMPLE_HEAD,  # Use simple header with horizontal lines
        title=None,  # Remove the redundant Progress title
        padding=(0, 2),  # Add horizontal padding
        expand=True,  # Make table expand to fill available space
    )
    progress_table.add_column("Team", style="cyan", justify="center", width=20)
    progress_table.add_column("Agent", style="green", justify="center", width=20)
    progress_table.add_column("Status", style="yellow", justify="center", width=20)

    # Group agents by team
    teams = {
        "Analyst Team": [
            "Market Analyst",
            "Social Analyst",
            "News Analyst",
            "Fundamentals Analyst",
        ],
        "Research Team": ["Bull Researcher", "Bear Researcher", "Research Manager"],
        "Trading Team": ["Trader"],
        "Risk Management": ["Risky Analyst", "Neutral Analyst", "Safe Analyst"],
        "Portfolio Management": ["Portfolio Manager"],
    }

    for team, agents in teams.items():
        # Add first agent with team name
        first_agent = agents[0]
        status = message_buffer.agent_status[first_agent]
        if status == "in_progress":
            spinner = Spinner(
                "dots", text="[blue]in_progress[/blue]", style="bold cyan"
            )
            status_cell = spinner
        else:
            status_color = {
                "pending": "yellow",
                "completed": "green",
                "error": "red",
            }.get(status, "white")
            status_cell = f"[{status_color}]{status}[/{status_color}]"
        progress_table.add_row(team, first_agent, status_cell)

        # Add remaining agents in team
        for agent in agents[1:]:
            status = message_buffer.agent_status[agent]
            if status == "in_progress":
                spinner = Spinner(
                    "dots", text="[blue]in_progress[/blue]", style="bold cyan"
                )
                status_cell = spinner
            else:
                status_color = {
                    "pending": "yellow",
                    "completed": "green",
                    "error": "red",
                }.get(status, "white")
                status_cell = f"[{status_color}]{status}[/{status_color}]"
            progress_table.add_row("", agent, status_cell)

        # Add horizontal line after each team
        progress_table.add_row("─" * 20, "─" * 20, "─" * 20, style="dim")

    layout["progress"].update(
        Panel(progress_table, title="Progress", border_style="cyan", padding=(1, 2))
    )

    # Messages panel showing recent messages and tool calls
    messages_table = Table(
        show_header=True,
        header_style="bold magenta",
        show_footer=False,
        expand=True,  # Make table expand to fill available space
        box=box.MINIMAL,  # Use minimal box style for a lighter look
        show_lines=True,  # Keep horizontal lines
        padding=(0, 1),  # Add some padding between columns
    )
    messages_table.add_column("Time", style="cyan", width=8, justify="center")
    messages_table.add_column("Type", style="green", width=10, justify="center")
    messages_table.add_column(
        "Content", style="white", no_wrap=False, ratio=1
    )  # Make content column expand

    # Combine tool calls and messages
    all_messages = []

    # Add tool calls
    for timestamp, tool_name, args in message_buffer.tool_calls:
        # Truncate tool call args if too long
        if isinstance(args, str) and len(args) > 100:
            args = args[:97] + "..."
        all_messages.append((timestamp, "Tool", f"{tool_name}: {args}"))

    # Add regular messages
    for timestamp, msg_type, content in message_buffer.messages:
        # Convert content to string if it's not already
        content_str = content
        if isinstance(content, list):
            # Handle list of content blocks (Anthropic format)
            text_parts = []
            for item in content:
                if isinstance(item, dict):
                    if item.get('type') == 'text':
                        text_parts.append(item.get('text', ''))
                    elif item.get('type') == 'tool_use':
                        text_parts.append(f"[Tool: {item.get('name', 'unknown')}]")
                else:
                    text_parts.append(str(item))
            content_str = ' '.join(text_parts)
        elif not isinstance(content_str, str):
            content_str = str(content)
            
        # Truncate message content if too long
        if len(content_str) > 200:
            content_str = content_str[:197] + "..."
        all_messages.append((timestamp, msg_type, content_str))

    # Sort by timestamp
    all_messages.sort(key=lambda x: x[0])

    # Calculate how many messages we can show based on available space
    # Start with a reasonable number and adjust based on content length
    max_messages = 12  # Increased from 8 to better fill the space

    # Get the last N messages that will fit in the panel
    recent_messages = all_messages[-max_messages:]

    # Add messages to table
    for timestamp, msg_type, content in recent_messages:
        # Format content with word wrapping
        wrapped_content = Text(content, overflow="fold")
        messages_table.add_row(timestamp, msg_type, wrapped_content)

    if spinner_text:
        messages_table.add_row("", "Spinner", spinner_text)

    # Add a footer to indicate if messages were truncated
    if len(all_messages) > max_messages:
        messages_table.footer = (
            f"[dim]Showing last {max_messages} of {len(all_messages)} messages[/dim]"
        )

    layout["messages"].update(
        Panel(
            messages_table,
            title="Messages & Tools",
            border_style="blue",
            padding=(1, 2),
        )
    )

    # Analysis panel showing current report
    if message_buffer.current_report:
        layout["analysis"].update(
            Panel(
                Markdown(message_buffer.current_report),
                title="Current Report",
                border_style="green",
                padding=(1, 2),
            )
        )
    else:
        layout["analysis"].update(
            Panel(
                "[italic]Waiting for analysis report...[/italic]",
                title="Current Report",
                border_style="green",
                padding=(1, 2),
            )
        )

    # Footer with statistics
    tool_calls_count = len(message_buffer.tool_calls)
    llm_calls_count = sum(
        1 for _, msg_type, _ in message_buffer.messages if msg_type == "Reasoning"
    )
    reports_count = sum(
        1 for content in message_buffer.report_sections.values() if content is not None
    )

    stats_table = Table(show_header=False, box=None, padding=(0, 2), expand=True)
    stats_table.add_column("Stats", justify="center")
    stats_table.add_row(
        f"Tool Calls: {tool_calls_count} | LLM Calls: {llm_calls_count} | Generated Reports: {reports_count}"
    )

    layout["footer"].update(Panel(stats_table, border_style="grey50"))


def get_user_selections():
    """Get all user selections before starting the analysis display."""
    # Display ASCII art welcome message
    with open("./cli/static/welcome.txt", "r") as f:
        welcome_ascii = f.read()

    # Create welcome box content
    welcome_content = f"{welcome_ascii}\n"
    welcome_content += "[bold green]TradingAgents: Multi-Agents LLM Financial Trading Framework - CLI[/bold green]\n\n"
    welcome_content += "[bold]Workflow Steps:[/bold]\n"
    welcome_content += "I. Analyst Team → II. Research Team → III. Trader → IV. Risk Management → V. Portfolio Management\n\n"
    welcome_content += (
        "[dim]Built by [Tauric Research](https://github.com/TauricResearch)[/dim]"
    )

    # Create and center the welcome box
    welcome_box = Panel(
        welcome_content,
        border_style="green",
        padding=(1, 2),
        title="Welcome to TradingAgents",
        subtitle="Multi-Agents LLM Financial Trading Framework",
    )
    console.print(Align.center(welcome_box))
    console.print()  # Add a blank line after the welcome box

    # Create a boxed questionnaire for each step
    def create_question_box(title, prompt, default=None):
        box_content = f"[bold]{title}[/bold]\n"
        box_content += f"[dim]{prompt}[/dim]"
        if default:
            box_content += f"\n[dim]Default: {default}[/dim]"
        return Panel(box_content, border_style="blue", padding=(1, 2))

    # Step 0: Select mode (single or batch)
    console.print(
        create_question_box(
            "Step 0: Analysis Mode", "Select analysis mode"
        )
    )
    analysis_mode = select_analysis_mode()
    
    if analysis_mode == "batch":
        # Batch mode: select JSON file
        console.print(
            create_question_box(
                "Step 1: Select Batch File", "Choose a JSON file with companies to analyze"
            )
        )
        batch_file = select_batch_file()
        selected_ticker = None  # Will be set later for batch mode
    else:
        # Single mode: Step 1: Ticker symbol
        console.print(
            create_question_box(
                "Step 1: Ticker Symbol", "Enter the ticker symbol to analyze", "SPY"
            )
        )
        selected_ticker = get_ticker()
        batch_file = None

    # Step 2: Analysis date
    default_date = datetime.datetime.now().strftime("%Y-%m-%d")
    console.print(
        create_question_box(
            "Step 2: Analysis Date",
            "Enter the analysis date (YYYY-MM-DD)",
            default_date,
        )
    )
    analysis_date = get_analysis_date()

    # Step 3: Select analysts
    console.print(
        create_question_box(
            "Step 3: Analysts Team", "Select your LLM analyst agents for the analysis"
        )
    )
    selected_analysts = select_analysts()
    console.print(
        f"[green]Selected analysts:[/green] {', '.join(analyst.value for analyst in selected_analysts)}"
    )

    # Step 4: Research depth
    console.print(
        create_question_box(
            "Step 4: Research Depth", "Select your research depth level"
        )
    )
    selected_research_depth = select_research_depth()

    # Step 5: Using Groq backend (skipped - using default)
    # Use Groq by default
    selected_llm_provider = "Groq"
    backend_url = "https://api.groq.com/openai/v1"
    
    # Skip Step 6: Model selection for batch processing
    # For batch mode, use more stable models to avoid capacity issues
    # Options: deepseek-r1-distill-llama-70b, mixtral-8x7b-32768, gemma2-9b-it
    
    # Allow environment variables to override default models
    default_batch_model = os.getenv("TRADINGAGENTS_BATCH_MODEL", "deepseek-r1-distill-llama-70b")
    default_single_model_deep = os.getenv("TRADINGAGENTS_SINGLE_MODEL_DEEP", "moonshotai/kimi-k2-instruct")
    default_single_model_quick = os.getenv("TRADINGAGENTS_SINGLE_MODEL_QUICK", "deepseek-r1-distill-llama-70b")
    
    if analysis_mode == "batch":
        # Use deepseek for better stability during batch processing
        selected_shallow_thinker = default_batch_model
        selected_deep_thinker = default_batch_model
    else:
        # For single analysis, use specialized models
        selected_shallow_thinker = default_single_model_quick  # DeepSeek for quick thinking
        selected_deep_thinker = default_single_model_deep      # Kimi for deep thinking

    return {
        "mode": analysis_mode,
        "ticker": selected_ticker,
        "batch_file": batch_file,
        "analysis_date": analysis_date,
        "analysts": selected_analysts,
        "research_depth": selected_research_depth,
        "llm_provider": selected_llm_provider.lower(),
        "backend_url": backend_url,
        "shallow_thinker": selected_shallow_thinker,
        "deep_thinker": selected_deep_thinker,
    }


def select_analysis_mode():
    """Select between single ticker or batch analysis mode."""
    import questionary
    mode = questionary.select(
        "Select analysis mode:",
        choices=[
            questionary.Choice("Single ticker analysis", value="single"),
            questionary.Choice("Batch analysis (JSON file)", value="batch"),
        ],
        instruction="\n- Use arrow keys to navigate\n- Press Enter to select",
        style=questionary.Style(
            [
                ("selected", "fg:magenta noinherit"),
                ("highlighted", "fg:magenta noinherit"),
                ("pointer", "fg:magenta noinherit"),
            ]
        ),
    ).ask()
    return mode if mode else "single"


def select_batch_file():
    """Select a JSON file for batch analysis."""
    import questionary
    from pathlib import Path
    
    # Look for JSON files in resources/earnings directory
    earnings_dir = Path("resources/earnings")
    json_files = []
    
    if earnings_dir.exists():
        for folder in earnings_dir.iterdir():
            if folder.is_dir():
                for json_file in folder.glob("*.json"):
                    json_files.append((f"{folder.name}/{json_file.name}", str(json_file)))
    
    if not json_files:
        console.print("[red]No JSON files found in resources/earnings directory[/red]")
        return None
    
    choice = questionary.select(
        "Select a JSON file to analyze:",
        choices=[
            questionary.Choice(display, value=path)
            for display, path in json_files
        ],
        instruction="\n- Use arrow keys to navigate\n- Press Enter to select",
        style=questionary.Style(
            [
                ("selected", "fg:magenta noinherit"),
                ("highlighted", "fg:magenta noinherit"),
                ("pointer", "fg:magenta noinherit"),
            ]
        ),
    ).ask()
    
    return choice


def get_ticker():
    """Get ticker symbol from user input."""
    import questionary
    ticker = questionary.text(
        "",
        default="SPY",
        style=questionary.Style(
            [
                ("text", "fg:green"),
                ("answer", "fg:white bold"),
            ]
        ),
    ).ask()
    return ticker if ticker else "SPY"


def get_analysis_date():
    """Get the analysis date from user input."""
    import questionary
    import re
    
    def validate_date(date_str: str) -> bool:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            return False
        try:
            analysis_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            if analysis_date.date() > datetime.datetime.now().date():
                return False
            return True
        except ValueError:
            return False
    
    date_str = questionary.text(
        "",
        default=datetime.datetime.now().strftime("%Y-%m-%d"),
        validate=lambda x: validate_date(x.strip()) or "Please enter a valid date in YYYY-MM-DD format (not in the future).",
        style=questionary.Style(
            [
                ("text", "fg:green"),
                ("answer", "fg:white bold"),
            ]
        ),
    ).ask()
    
    return date_str if date_str else datetime.datetime.now().strftime("%Y-%m-%d")


def display_complete_report(final_state):
    """Display the complete analysis report with team-based panels."""
    console.print("\n[bold green]Complete Analysis Report[/bold green]\n")

    # I. Analyst Team Reports
    analyst_reports = []

    # Market Analyst Report
    if final_state.get("market_report"):
        analyst_reports.append(
            Panel(
                Markdown(final_state["market_report"]),
                title="Market Analyst",
                border_style="blue",
                padding=(1, 2),
            )
        )

    # Social Analyst Report
    if final_state.get("sentiment_report"):
        analyst_reports.append(
            Panel(
                Markdown(final_state["sentiment_report"]),
                title="Social Analyst",
                border_style="blue",
                padding=(1, 2),
            )
        )

    # News Analyst Report
    if final_state.get("news_report"):
        analyst_reports.append(
            Panel(
                Markdown(final_state["news_report"]),
                title="News Analyst",
                border_style="blue",
                padding=(1, 2),
            )
        )

    # Fundamentals Analyst Report
    if final_state.get("fundamentals_report"):
        analyst_reports.append(
            Panel(
                Markdown(final_state["fundamentals_report"]),
                title="Fundamentals Analyst",
                border_style="blue",
                padding=(1, 2),
            )
        )

    if analyst_reports:
        console.print(
            Panel(
                Columns(analyst_reports, equal=True, expand=True),
                title="I. Analyst Team Reports",
                border_style="cyan",
                padding=(1, 2),
            )
        )

    # II. Research Team Reports
    if final_state.get("investment_debate_state"):
        research_reports = []
        debate_state = final_state["investment_debate_state"]

        # Bull Researcher Analysis
        if debate_state.get("bull_history"):
            research_reports.append(
                Panel(
                    Markdown(debate_state["bull_history"]),
                    title="Bull Researcher",
                    border_style="blue",
                    padding=(1, 2),
                )
            )

        # Bear Researcher Analysis
        if debate_state.get("bear_history"):
            research_reports.append(
                Panel(
                    Markdown(debate_state["bear_history"]),
                    title="Bear Researcher",
                    border_style="blue",
                    padding=(1, 2),
                )
            )

        # Research Manager Decision
        if debate_state.get("judge_decision"):
            research_reports.append(
                Panel(
                    Markdown(debate_state["judge_decision"]),
                    title="Research Manager",
                    border_style="blue",
                    padding=(1, 2),
                )
            )

        if research_reports:
            console.print(
                Panel(
                    Columns(research_reports, equal=True, expand=True),
                    title="II. Research Team Decision",
                    border_style="magenta",
                    padding=(1, 2),
                )
            )

    # III. Trading Team Reports
    if final_state.get("trader_investment_plan"):
        console.print(
            Panel(
                Panel(
                    Markdown(final_state["trader_investment_plan"]),
                    title="Trader",
                    border_style="blue",
                    padding=(1, 2),
                ),
                title="III. Trading Team Plan",
                border_style="yellow",
                padding=(1, 2),
            )
        )

    # IV. Risk Management Team Reports
    if final_state.get("risk_debate_state"):
        risk_reports = []
        risk_state = final_state["risk_debate_state"]

        # Aggressive (Risky) Analyst Analysis
        if risk_state.get("risky_history"):
            risk_reports.append(
                Panel(
                    Markdown(risk_state["risky_history"]),
                    title="Aggressive Analyst",
                    border_style="blue",
                    padding=(1, 2),
                )
            )

        # Conservative (Safe) Analyst Analysis
        if risk_state.get("safe_history"):
            risk_reports.append(
                Panel(
                    Markdown(risk_state["safe_history"]),
                    title="Conservative Analyst",
                    border_style="blue",
                    padding=(1, 2),
                )
            )

        # Neutral Analyst Analysis
        if risk_state.get("neutral_history"):
            risk_reports.append(
                Panel(
                    Markdown(risk_state["neutral_history"]),
                    title="Neutral Analyst",
                    border_style="blue",
                    padding=(1, 2),
                )
            )

        if risk_reports:
            console.print(
                Panel(
                    Columns(risk_reports, equal=True, expand=True),
                    title="IV. Risk Management Team Decision",
                    border_style="red",
                    padding=(1, 2),
                )
            )

        # V. Portfolio Manager Decision
        if risk_state.get("judge_decision"):
            console.print(
                Panel(
                    Panel(
                        Markdown(risk_state["judge_decision"]),
                        title="Portfolio Manager",
                        border_style="blue",
                        padding=(1, 2),
                    ),
                    title="V. Portfolio Manager Decision",
                    border_style="green",
                    padding=(1, 2),
                )
            )


def update_research_team_status(status):
    """Update status for all research team members and trader."""
    research_team = ["Bull Researcher", "Bear Researcher", "Research Manager", "Trader"]
    for agent in research_team:
        message_buffer.update_agent_status(agent, status)

def extract_content_string(content):
    """Extract string content from various message formats."""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        # Handle Anthropic's list format
        text_parts = []
        for item in content:
            if isinstance(item, dict):
                if item.get('type') == 'text':
                    text_parts.append(item.get('text', ''))
                elif item.get('type') == 'tool_use':
                    text_parts.append(f"[Tool: {item.get('name', 'unknown')}]")
            else:
                text_parts.append(str(item))
        return ' '.join(text_parts)
    else:
        return str(content)

def create_composite_report(selections, all_results, buy_recommendations, sell_recommendations, hold_recommendations):
    """Create a composite report summarizing all batch analysis results."""
    from datetime import datetime
    from pathlib import Path
    
    # Create batch results directory
    batch_name = Path(selections["batch_file"]).stem
    results_dir = Path(DEFAULT_CONFIG["results_dir"]) / "batch" / batch_name / selections["analysis_date"]
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Create composite report content
    report_content = f"""# Batch Analysis Report: {batch_name}
Date: {selections["analysis_date"]}
Total Companies Analyzed: {len(all_results)}

## Summary
- **Buy Recommendations**: {len(buy_recommendations)}
- **Sell Recommendations**: {len(sell_recommendations)}
- **Hold Recommendations**: {len(hold_recommendations)}

## Buy Recommendations

"""
    
    # Add buy recommendations
    for result in buy_recommendations:
        ticker = result["ticker"]
        name = result.get("company_name", ticker)
        reports = result.get("reports", {})
        
        report_content += f"### {name} ({ticker})\n"
        
        # Extract key information from reports
        if "final_trade_decision" in result.get("final_state", {}):
            report_content += f"**Decision**: {result['final_state']['final_trade_decision']}\n\n"
        
        if "trader_investment_plan" in reports:
            report_content += f"**Trading Plan**: {reports['trader_investment_plan'][:500]}...\n\n"
        
        report_content += "---\n\n"
    
    # Add sell recommendations
    report_content += "## Sell Recommendations\n\n"
    
    for result in sell_recommendations:
        ticker = result["ticker"]
        name = result.get("company_name", ticker)
        reports = result.get("reports", {})
        
        report_content += f"### {name} ({ticker})\n"
        
        if "final_trade_decision" in result.get("final_state", {}):
            report_content += f"**Decision**: {result['final_state']['final_trade_decision']}\n\n"
        
        if "trader_investment_plan" in reports:
            report_content += f"**Trading Plan**: {reports['trader_investment_plan'][:500]}...\n\n"
        
        report_content += "---\n\n"
    
    # Add hold recommendations summary
    report_content += "## Hold Recommendations\n\n"
    
    for result in hold_recommendations:
        ticker = result["ticker"]
        name = result.get("company_name", ticker)
        report_content += f"- {name} ({ticker})\n"
    
    # Add timestamp
    report_content += f"\n\n---\n*Report generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
    
    # Save composite report
    composite_report_path = results_dir / "composite_report.md"
    with open(composite_report_path, 'w') as f:
        f.write(report_content)
    
    console.print(f"\n[green]Composite report saved to: {composite_report_path}[/green]")
    
    # Save individual reports
    for result in all_results:
        ticker = result["ticker"]
        ticker_dir = results_dir / ticker
        ticker_dir.mkdir(exist_ok=True)
        
        # Save all reports for this ticker
        if "reports" in result:
            for report_name, report_content in result["reports"].items():
                report_path = ticker_dir / f"{report_name}.md"
                with open(report_path, 'w') as f:
                    f.write(report_content)


def run_batch_analysis(selections, companies):
    """Run analysis for multiple companies and create a composite report."""
    import json
    from datetime import datetime
    
    all_results = []
    buy_recommendations = []
    sell_recommendations = []
    hold_recommendations = []
    
    # For batch processing, use more stable models to avoid rate limiting
    batch_selections = selections.copy()
    # Use deepseek-r1-distill-llama-70b for batch processing as it's more stable
    batch_selections["deep_thinker"] = os.getenv("TRADINGAGENTS_BATCH_MODEL", "deepseek-r1-distill-llama-70b")
    batch_selections["shallow_thinker"] = os.getenv("TRADINGAGENTS_BATCH_MODEL", "deepseek-r1-distill-llama-70b")
    
    console.print(f"\n[bold green]Starting batch analysis for {len(companies)} companies[/bold green]")
    console.print(f"[dim]Using model: {batch_selections['deep_thinker']}[/dim]\n")
    
    for i, company in enumerate(companies, 1):
        ticker = company.get("ticker", "")
        name = company.get("name", ticker)
        
        console.print(f"\n[bold cyan]Analyzing {i}/{len(companies)}: {name} ({ticker})[/bold cyan]")
        
        # Run individual analysis
        try:
            result = run_single_analysis(batch_selections, ticker, name)
            all_results.append(result)
            
            # Categorize based on recommendation
            if result.get("recommendation") == "BUY":
                buy_recommendations.append(result)
            elif result.get("recommendation") == "SELL":
                sell_recommendations.append(result)
            else:
                hold_recommendations.append(result)
            
            # Add a small delay between analyses to prevent overwhelming the API
            if i < len(companies):  # Don't delay after the last company
                delay = random.uniform(1.0, 3.0)  # Random delay between 1-3 seconds
                console.print(f"[dim]Waiting {delay:.1f}s before next analysis...[/dim]")
                time.sleep(delay)
                
        except Exception as e:
            console.print(f"[red]Error analyzing {ticker}: {e}[/red]")
            
            # Log the error
            error_logger = get_error_logger()
            error_logger.log_error(
                error_type=type(e).__name__,
                error_message=str(e),
                component="batch_analysis",
                ticker=ticker,
                additional_context={
                    "company_name": name,
                    "analysis_date": selections["analysis_date"],
                    "llm_provider": selections["llm_provider"],
                },
                exception=e
            )
            continue
    
    # Create composite report
    create_composite_report(selections, all_results, buy_recommendations, sell_recommendations, hold_recommendations)
    
    console.print(f"\n[bold green]Batch analysis complete![/bold green]")
    console.print(f"- Buy recommendations: {len(buy_recommendations)}")
    console.print(f"- Sell recommendations: {len(sell_recommendations)}")
    console.print(f"- Hold recommendations: {len(hold_recommendations)}")
    
    # Show error summary if there were any errors
    error_logger = get_error_logger()
    error_summary = error_logger.summarize_errors()
    if error_summary["total_errors"] > 0:
        console.print(f"\n[yellow]Errors encountered during analysis:[/yellow]")
        console.print(f"- Total errors: {error_summary['total_errors']}")
        for error_type, count in error_summary["errors_by_type"].items():
            console.print(f"- {error_type}: {count}")
        console.print(f"\n[dim]Error logs saved to: error_logs/[/dim]")


@with_rate_limit(min_delay=2.0, max_delay=120.0, max_retries=5)
def run_single_analysis(selections, ticker, company_name=None):
    """Run analysis for a single ticker and return results."""
    # Update selections with current ticker
    analysis_selections = selections.copy()
    analysis_selections["ticker"] = ticker
    
    # Allow environment variable override for single analysis models
    if os.getenv("TRADINGAGENTS_SINGLE_MODEL_DEEP"):
        analysis_selections["deep_thinker"] = os.getenv("TRADINGAGENTS_SINGLE_MODEL_DEEP")
    if os.getenv("TRADINGAGENTS_SINGLE_MODEL_QUICK"):
        analysis_selections["shallow_thinker"] = os.getenv("TRADINGAGENTS_SINGLE_MODEL_QUICK")
    # Legacy support for single model override
    if os.getenv("TRADINGAGENTS_SINGLE_MODEL"):
        analysis_selections["deep_thinker"] = os.getenv("TRADINGAGENTS_SINGLE_MODEL")
        analysis_selections["shallow_thinker"] = os.getenv("TRADINGAGENTS_SINGLE_MODEL")
    
    # Run the standard analysis
    result = execute_trading_analysis(analysis_selections)
    
    # Add company name if provided
    if company_name:
        result["company_name"] = company_name
    
    return result


def run_analysis():
    # First get all user selections
    selections = get_user_selections()
    
    if selections["mode"] == "batch" and selections["batch_file"]:
        # Load companies from JSON file
        import json
        with open(selections["batch_file"], 'r') as f:
            data = json.load(f)
            companies = data.get("companies", [])
        
        if companies:
            run_batch_analysis(selections, companies)
        else:
            console.print("[red]No companies found in the selected file[/red]")
    else:
        # Single ticker analysis
        result = execute_trading_analysis(selections)
        display_complete_report(result.get("final_state", {}))


def execute_trading_analysis(selections):
    """Execute trading analysis for a single ticker."""
    # Create config with selected research depth
    config = DEFAULT_CONFIG.copy()
    config["max_debate_rounds"] = selections["research_depth"]
    config["max_risk_discuss_rounds"] = selections["research_depth"]
    config["quick_think_llm"] = selections["shallow_thinker"]
    config["deep_think_llm"] = selections["deep_thinker"]
    config["backend_url"] = selections["backend_url"]
    config["llm_provider"] = selections["llm_provider"].lower()

    # Initialize the graph
    graph = TradingAgentsGraph(
        [analyst.value for analyst in selections["analysts"]], config=config, debug=True
    )

    # Create result directory
    results_dir = Path(config["results_dir"]) / selections["ticker"] / selections["analysis_date"]
    results_dir.mkdir(parents=True, exist_ok=True)
    report_dir = results_dir / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    log_file = results_dir / "message_tool.log"
    log_file.touch(exist_ok=True)

    def save_message_decorator(obj, func_name):
        func = getattr(obj, func_name)
        @wraps(func)
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            timestamp, message_type, content = obj.messages[-1]
            content = content.replace("\n", " ")  # Replace newlines with spaces
            with open(log_file, "a") as f:
                f.write(f"{timestamp} [{message_type}] {content}\n")
        return wrapper
    
    def save_tool_call_decorator(obj, func_name):
        func = getattr(obj, func_name)
        @wraps(func)
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            timestamp, tool_name, args = obj.tool_calls[-1]
            args_str = ", ".join(f"{k}={v}" for k, v in args.items())
            with open(log_file, "a") as f:
                f.write(f"{timestamp} [Tool Call] {tool_name}({args_str})\n")
        return wrapper

    def save_report_section_decorator(obj, func_name):
        func = getattr(obj, func_name)
        @wraps(func)
        def wrapper(section_name, content):
            func(section_name, content)
            if section_name in obj.report_sections and obj.report_sections[section_name] is not None:
                content = obj.report_sections[section_name]
                if content:
                    file_name = f"{section_name}.md"
                    with open(report_dir / file_name, "w") as f:
                        f.write(content)
        return wrapper

    message_buffer.add_message = save_message_decorator(message_buffer, "add_message")
    message_buffer.add_tool_call = save_tool_call_decorator(message_buffer, "add_tool_call")
    message_buffer.update_report_section = save_report_section_decorator(message_buffer, "update_report_section")

    # Now start the display layout
    layout = create_layout()

    with Live(layout, refresh_per_second=4) as live:
        # Initial display
        update_display(layout)

        # Add initial messages
        message_buffer.add_message("System", f"Selected ticker: {selections['ticker']}")
        message_buffer.add_message(
            "System", f"Analysis date: {selections['analysis_date']}"
        )
        message_buffer.add_message(
            "System",
            f"Selected analysts: {', '.join(analyst.value for analyst in selections['analysts'])}",
        )
        update_display(layout)

        # Reset agent statuses
        for agent in message_buffer.agent_status:
            message_buffer.update_agent_status(agent, "pending")

        # Reset report sections
        for section in message_buffer.report_sections:
            message_buffer.report_sections[section] = None
        message_buffer.current_report = None
        message_buffer.final_report = None

        # Update agent status to in_progress for the first analyst
        first_analyst = f"{selections['analysts'][0].value.capitalize()} Analyst"
        message_buffer.update_agent_status(first_analyst, "in_progress")
        update_display(layout)

        # Create spinner text
        spinner_text = (
            f"Analyzing {selections['ticker']} on {selections['analysis_date']}..."
        )
        update_display(layout, spinner_text)

        # Initialize state and get graph args
        init_agent_state = graph.propagator.create_initial_state(
            selections["ticker"], selections["analysis_date"]
        )
        args = graph.propagator.get_graph_args()

        # Stream the analysis
        trace = []
        for chunk in graph.graph.stream(init_agent_state, **args):
            if len(chunk["messages"]) > 0:
                # Get the last message from the chunk
                last_message = chunk["messages"][-1]

                # Extract message content and type
                if hasattr(last_message, "content"):
                    content = extract_content_string(last_message.content)  # Use the helper function
                    msg_type = "Reasoning"
                else:
                    content = str(last_message)
                    msg_type = "System"

                # Add message to buffer
                message_buffer.add_message(msg_type, content)                

                # If it's a tool call, add it to tool calls
                if hasattr(last_message, "tool_calls"):
                    for tool_call in last_message.tool_calls:
                        # Handle both dictionary and object tool calls
                        if isinstance(tool_call, dict):
                            message_buffer.add_tool_call(
                                tool_call["name"], tool_call["args"]
                            )
                        else:
                            message_buffer.add_tool_call(tool_call.name, tool_call.args)

                # Update reports and agent status based on chunk content
                # Analyst Team Reports
                if "market_report" in chunk and chunk["market_report"]:
                    message_buffer.update_report_section(
                        "market_report", chunk["market_report"]
                    )
                    message_buffer.update_agent_status("Market Analyst", "completed")
                    # Set next analyst to in_progress
                    if "social" in selections["analysts"]:
                        message_buffer.update_agent_status(
                            "Social Analyst", "in_progress"
                        )

                if "sentiment_report" in chunk and chunk["sentiment_report"]:
                    message_buffer.update_report_section(
                        "sentiment_report", chunk["sentiment_report"]
                    )
                    message_buffer.update_agent_status("Social Analyst", "completed")
                    # Set next analyst to in_progress
                    if "news" in selections["analysts"]:
                        message_buffer.update_agent_status(
                            "News Analyst", "in_progress"
                        )

                if "news_report" in chunk and chunk["news_report"]:
                    message_buffer.update_report_section(
                        "news_report", chunk["news_report"]
                    )
                    message_buffer.update_agent_status("News Analyst", "completed")
                    # Set next analyst to in_progress
                    if "fundamentals" in selections["analysts"]:
                        message_buffer.update_agent_status(
                            "Fundamentals Analyst", "in_progress"
                        )

                if "fundamentals_report" in chunk and chunk["fundamentals_report"]:
                    message_buffer.update_report_section(
                        "fundamentals_report", chunk["fundamentals_report"]
                    )
                    message_buffer.update_agent_status(
                        "Fundamentals Analyst", "completed"
                    )
                    # Set all research team members to in_progress
                    update_research_team_status("in_progress")

                # Research Team - Handle Investment Debate State
                if (
                    "investment_debate_state" in chunk
                    and chunk["investment_debate_state"]
                ):
                    debate_state = chunk["investment_debate_state"]

                    # Update Bull Researcher status and report
                    if "bull_history" in debate_state and debate_state["bull_history"]:
                        # Keep all research team members in progress
                        update_research_team_status("in_progress")
                        # Extract latest bull response
                        bull_responses = debate_state["bull_history"].split("\n")
                        latest_bull = bull_responses[-1] if bull_responses else ""
                        if latest_bull:
                            message_buffer.add_message("Reasoning", latest_bull)
                            # Update research report with bull's latest analysis
                            message_buffer.update_report_section(
                                "investment_plan",
                                f"### Bull Researcher Analysis\n{latest_bull}",
                            )

                    # Update Bear Researcher status and report
                    if "bear_history" in debate_state and debate_state["bear_history"]:
                        # Keep all research team members in progress
                        update_research_team_status("in_progress")
                        # Extract latest bear response
                        bear_responses = debate_state["bear_history"].split("\n")
                        latest_bear = bear_responses[-1] if bear_responses else ""
                        if latest_bear:
                            message_buffer.add_message("Reasoning", latest_bear)
                            # Update research report with bear's latest analysis
                            message_buffer.update_report_section(
                                "investment_plan",
                                f"{message_buffer.report_sections['investment_plan']}\n\n### Bear Researcher Analysis\n{latest_bear}",
                            )

                    # Update Research Manager status and final decision
                    if (
                        "judge_decision" in debate_state
                        and debate_state["judge_decision"]
                    ):
                        # Keep all research team members in progress until final decision
                        update_research_team_status("in_progress")
                        message_buffer.add_message(
                            "Reasoning",
                            f"Research Manager: {debate_state['judge_decision']}",
                        )
                        # Update research report with final decision
                        message_buffer.update_report_section(
                            "investment_plan",
                            f"{message_buffer.report_sections['investment_plan']}\n\n### Research Manager Decision\n{debate_state['judge_decision']}",
                        )
                        # Mark all research team members as completed
                        update_research_team_status("completed")
                        # Set first risk analyst to in_progress
                        message_buffer.update_agent_status(
                            "Risky Analyst", "in_progress"
                        )

                # Trading Team
                if (
                    "trader_investment_plan" in chunk
                    and chunk["trader_investment_plan"]
                ):
                    message_buffer.update_report_section(
                        "trader_investment_plan", chunk["trader_investment_plan"]
                    )
                    # Set first risk analyst to in_progress
                    message_buffer.update_agent_status("Risky Analyst", "in_progress")

                # Risk Management Team - Handle Risk Debate State
                if "risk_debate_state" in chunk and chunk["risk_debate_state"]:
                    risk_state = chunk["risk_debate_state"]

                    # Update Risky Analyst status and report
                    if (
                        "current_risky_response" in risk_state
                        and risk_state["current_risky_response"]
                    ):
                        message_buffer.update_agent_status(
                            "Risky Analyst", "in_progress"
                        )
                        message_buffer.add_message(
                            "Reasoning",
                            f"Risky Analyst: {risk_state['current_risky_response']}",
                        )
                        # Update risk report with risky analyst's latest analysis only
                        message_buffer.update_report_section(
                            "final_trade_decision",
                            f"### Risky Analyst Analysis\n{risk_state['current_risky_response']}",
                        )

                    # Update Safe Analyst status and report
                    if (
                        "current_safe_response" in risk_state
                        and risk_state["current_safe_response"]
                    ):
                        message_buffer.update_agent_status(
                            "Safe Analyst", "in_progress"
                        )
                        message_buffer.add_message(
                            "Reasoning",
                            f"Safe Analyst: {risk_state['current_safe_response']}",
                        )
                        # Update risk report with safe analyst's latest analysis only
                        message_buffer.update_report_section(
                            "final_trade_decision",
                            f"### Safe Analyst Analysis\n{risk_state['current_safe_response']}",
                        )

                    # Update Neutral Analyst status and report
                    if (
                        "current_neutral_response" in risk_state
                        and risk_state["current_neutral_response"]
                    ):
                        message_buffer.update_agent_status(
                            "Neutral Analyst", "in_progress"
                        )
                        message_buffer.add_message(
                            "Reasoning",
                            f"Neutral Analyst: {risk_state['current_neutral_response']}",
                        )
                        # Update risk report with neutral analyst's latest analysis only
                        message_buffer.update_report_section(
                            "final_trade_decision",
                            f"### Neutral Analyst Analysis\n{risk_state['current_neutral_response']}",
                        )

                    # Update Portfolio Manager status and final decision
                    if "judge_decision" in risk_state and risk_state["judge_decision"]:
                        message_buffer.update_agent_status(
                            "Portfolio Manager", "in_progress"
                        )
                        message_buffer.add_message(
                            "Reasoning",
                            f"Portfolio Manager: {risk_state['judge_decision']}",
                        )
                        # Update risk report with final decision only
                        message_buffer.update_report_section(
                            "final_trade_decision",
                            f"### Portfolio Manager Decision\n{risk_state['judge_decision']}",
                        )
                        # Mark risk analysts as completed
                        message_buffer.update_agent_status("Risky Analyst", "completed")
                        message_buffer.update_agent_status("Safe Analyst", "completed")
                        message_buffer.update_agent_status(
                            "Neutral Analyst", "completed"
                        )
                        message_buffer.update_agent_status(
                            "Portfolio Manager", "completed"
                        )

                # Update the display
                update_display(layout)

            trace.append(chunk)

        # Get final state and decision
        final_state = trace[-1]
        decision = graph.process_signal(final_state["final_trade_decision"])

        # Update all agent statuses to completed
        for agent in message_buffer.agent_status:
            message_buffer.update_agent_status(agent, "completed")

        message_buffer.add_message(
            "Analysis", f"Completed analysis for {selections['analysis_date']}"
        )

        # Update final report sections
        for section in message_buffer.report_sections.keys():
            if section in final_state:
                message_buffer.update_report_section(section, final_state[section])

        # Display the complete final report
        # Store final state for return
        final_state = chunk
        
        # Only display in non-batch mode
        if selections.get("mode") != "batch":
            display_complete_report(final_state)
            update_display(layout)
        
        # Extract recommendation from final state
        recommendation = "HOLD"  # Default
        if "final_trade_decision" in final_state:
            decision_text = final_state["final_trade_decision"].lower()
            if "buy" in decision_text:
                recommendation = "BUY"
            elif "sell" in decision_text:
                recommendation = "SELL"
        
        return {
            "ticker": selections["ticker"],
            "recommendation": recommendation,
            "final_state": final_state,
            "reports": message_buffer.report_sections
        }


@app.command()
def analyze():
    run_analysis()


if __name__ == "__main__":
    app()
