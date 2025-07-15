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
config["quick_think_llm"] = "moonshotai/kimi-k2-instruct"
config["max_debate_rounds"] = 1  # Increase debate rounds
config["online_tools"] = True  # Use online tools for real-time data

# Initialize with custom config
ta = TradingAgentsGraph(debug=True, config=config)

# forward propagate
_, decision = ta.propagate("NVDA", "2024-05-10")
print(decision)

# Memorize mistakes and reflect
# ta.reflect_and_remember(1000) # parameter is the position returns
