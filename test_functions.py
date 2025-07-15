import os
from dotenv import load_dotenv
load_dotenv()

from tradingagents.dataflows import interface
from datetime import datetime

# Test the functions to see what they actually do
print("Testing get_stock_news_openai function...")
print("This function should now use FinnHub, not OpenAI\n")

try:
    result = interface.get_stock_news_openai("WMT", "2025-07-15")
    print("Result type:", type(result))
    print("First 500 chars of result:")
    print(result[:500] if isinstance(result, str) else str(result)[:500])
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80 + "\n")

print("Testing get_fundamentals_openai function...")
print("This function should now use yfinance, not OpenAI\n")

try:
    result = interface.get_fundamentals_openai("WMT", "2025-07-15")
    print("Result type:", type(result))
    print("First 500 chars of result:")
    print(result[:500] if isinstance(result, str) else str(result)[:500])
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()