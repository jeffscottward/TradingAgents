import os
from dotenv import load_dotenv

# 🚀 ~ load environment variables from .env file
load_dotenv()

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# Create a custom config
config = DEFAULT_CONFIG.copy()
# Use Groq API with Kimi K2 model
config["llm_provider"] = "groq"
config["backend_url"] = "https://api.groq.com/openai/v1"
config["deep_think_llm"] = "moonshotai/kimi-k2-instruct"
config["quick_think_llm"] = "deepseek-r1-distill-llama-70b"
config["max_debate_rounds"] = 1  # Increase debate rounds
config["online_tools"] = False  # Use FinnHub data instead of online tools

# Initialize with custom config
ta = TradingAgentsGraph(debug=True, config=config)

# forward propagate
print("Starting analysis for AAPL on 2025-01-15...")
_, decision = ta.propagate("AAPL", "2025-01-15")
print("\nFinal Decision:", decision)
