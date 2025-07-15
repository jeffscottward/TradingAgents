import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from cli.main import run_batch_analysis, create_composite_report
from tradingagents.default_config import DEFAULT_CONFIG
from cli.models import AnalystType
import json

# Create test selections that mimic what the CLI would provide
selections = {
    "mode": "batch",
    "ticker": None,
    "batch_file": "resources/earnings/Q1-2025/test_companies.json",
    "analysis_date": "2025-01-15",
    "analysts": [
        AnalystType.FUNDAMENTALS,
        AnalystType.MARKET,
        AnalystType.NEWS,
        AnalystType.SOCIAL
    ],
    "research_depth": 1,
    "llm_provider": "groq",
    "backend_url": "https://api.groq.com/openai/v1",
    "shallow_thinker": "moonshotai/kimi-k2-instruct",
    "deep_thinker": "moonshotai/kimi-k2-instruct"
}

# Load companies from the batch file
with open(selections["batch_file"], 'r') as f:
    data = json.load(f)
    companies = data.get("companies", [])

print(f"Testing batch analysis with {len(companies)} companies...")
print(f"Companies: {[c['ticker'] for c in companies]}")

# Run the batch analysis with just the first 2 companies for testing
run_batch_analysis(selections, companies[:2])