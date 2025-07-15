import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# Create a custom config
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "groq"
config["backend_url"] = "https://api.groq.com/openai/v1"
config["deep_think_llm"] = "moonshotai/kimi-k2-instruct"
config["quick_think_llm"] = "deepseek-r1-distill-llama-70b"
config["max_debate_rounds"] = 1
config["online_tools"] = True  # We can use online tools now since they're fixed

# Initialize with custom config
print("Initializing TradingAgents...")
print(f"Using online_tools: {config['online_tools']}")
print(f"Quick Thinking LLM: {config['quick_think_llm']}")
print(f"Deep Thinking LLM: {config['deep_think_llm']}")
print("\n" + "="*80 + "\n")

ta = TradingAgentsGraph(debug=True, config=config)

# Run analysis for Walmart
print("Starting analysis for Walmart (WMT) on 2025-07-15...")
print("\n" + "="*80 + "\n")

try:
    _, decision = ta.propagate("WMT", "2025-07-15")
    print("\n" + "="*80)
    print("\nFinal Decision:", decision)
except Exception as e:
    print(f"\nError occurred: {e}")
    import traceback
    traceback.print_exc()