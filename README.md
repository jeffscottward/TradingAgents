# TradingAgents: Multi-Agents LLM Financial Trading Framework

<!-- markdownlint-disable MD033 -->

<p align="center">
  <img src="assets/TauricResearch.png" alt="Tauric Research logo" style="width: 60%; height: auto;">
</p>

<div align="center" style="line-height: 1;">
  <a href="https://arxiv.org/abs/2412.20138" target="_blank"><img alt="arXiv" src="https://img.shields.io/badge/arXiv-2412.20138-B31B1B?logo=arxiv"/></a>
  <a href="https://discord.com/invite/hk9PGKShPK" target="_blank"><img alt="Discord" src="https://img.shields.io/badge/Discord-TradingResearch-7289da?logo=discord&logoColor=white&color=7289da"/></a>
  <a href="./assets/wechat.png" target="_blank"><img alt="WeChat" src="https://img.shields.io/badge/WeChat-TauricResearch-brightgreen?logo=wechat&logoColor=white"/></a>
  <a href="https://x.com/TauricResearch" target="_blank"><img alt="X Follow" src="https://img.shields.io/badge/X-TauricResearch-white?logo=x&logoColor=white"/></a>
  <br>
  <a href="https://github.com/TauricResearch/" target="_blank"><img alt="Community" src="https://img.shields.io/badge/Join_GitHub_Community-TauricResearch-14C290?logo=discourse"/></a>
</div>

<div align="center">
  <!-- Keep these links. Translations will automatically update with the README. -->
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=de">Deutsch</a> |
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=es">Español</a> |
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=fr">français</a> |
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=ja">日本語</a> |
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=ko">한국어</a> |
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=pt">Português</a> |
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=ru">Русский</a> |
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=zh">中文</a>
</div>

---

> 🎉 **TradingAgents** officially released! We have received numerous inquiries about the work, and we would like to express our thanks for the enthusiasm in our community.
>
> So we decided to fully open-source the framework. Looking forward to building impactful projects with you!

<div align="center">
<a href="https://www.star-history.com/#TauricResearch/TradingAgents&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=TauricResearch/TradingAgents&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=TauricResearch/TradingAgents&type=Date" />
   <img alt="TradingAgents Star History" src="https://api.star-history.com/svg?repos=TauricResearch/TradingAgents&type=Date" style="width: 80%; height: auto;" />
 </picture>
</a>
</div>

<div align="center">

🚀 [TradingAgents](#tradingagents-framework) | ⚡ [Installation & CLI](#installation-and-cli) | 🎬 [Demo](https://www.youtube.com/watch?v=90gr5lwjIho) | 📦 [Package Usage](#tradingagents-package) | 🤝 [Contributing](#contributing) | 📄 [Citation](#citation)

</div>

## TradingAgents Framework

TradingAgents is a multi-agent trading framework that mirrors the dynamics of real-world trading firms. By deploying specialized LLM-powered agents: from fundamental analysts, sentiment experts, and technical analysts, to trader, risk management team, the platform collaboratively evaluates market conditions and informs trading decisions. Moreover, these agents engage in dynamic discussions to pinpoint the optimal strategy.

<p align="center">
  <img src="assets/schema.png" alt="TradingAgents framework schema" style="width: 100%; height: auto;">
</p>

> TradingAgents framework is designed for research purposes. Trading performance may vary based on many factors, including the chosen backbone language models, model temperature, trading periods, the quality of data, and other non-deterministic factors. [It is not intended as financial, investment, or trading advice.](https://tauric.ai/disclaimer/)

Our framework decomposes complex trading tasks into specialized roles. This ensures the system achieves a robust, scalable approach to market analysis and decision-making.

### Analyst Team

- Fundamentals Analyst: Evaluates company financials and performance metrics, identifying intrinsic values and potential red flags.
- Sentiment Analyst: Analyzes social media and public sentiment using sentiment scoring algorithms to gauge short-term market mood.
- News Analyst: Monitors global news and macroeconomic indicators, interpreting the impact of events on market conditions.
- Technical Analyst: Utilizes technical indicators (like MACD and RSI) to detect trading patterns and forecast price movements.

<p align="center">
  <img src="assets/analyst.png" alt="Analyst team diagram" width="100%" style="display: inline-block; margin: 0 2%;">
</p>

### Researcher Team

- Comprises both bullish and bearish researchers who critically assess the insights provided by the Analyst Team. Through structured debates, they balance potential gains against inherent risks.

<p align="center">
  <img src="assets/researcher.png" alt="Researcher team diagram" width="70%" style="display: inline-block; margin: 0 2%;">
</p>

### Trader Agent

- Composes reports from the analysts and researchers to make informed trading decisions. It determines the timing and magnitude of trades based on comprehensive market insights.

<p align="center">
  <img src="assets/trader.png" alt="Trader agent diagram" width="70%" style="display: inline-block; margin: 0 2%;">
</p>

### Risk Management and Portfolio Manager

- Continuously evaluates portfolio risk by assessing market volatility, liquidity, and other risk factors. The risk management team evaluates and adjusts trading strategies, providing assessment reports to the Portfolio Manager for final decision.
- The Portfolio Manager approves/rejects the transaction proposal. If approved, the order will be sent to the simulated exchange and executed.

<p align="center">
  <img src="assets/risk.png" alt="Risk management diagram" width="70%" style="display: inline-block; margin: 0 2%;">
</p>

## Installation and CLI

### Installation

Clone TradingAgents:

```bash
git clone https://github.com/TauricResearch/TradingAgents.git
cd TradingAgents
```

#### Option 1: Using UV (Recommended)

[UV](https://github.com/astral-sh/uv) is a fast Python package installer and resolver. If you don't have UV installed:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# or with Homebrew
brew install uv
```

Set up the project with UV:

```bash
# Create virtual environment with Python 3.13
uv venv .venv --python 3.13

# Activate the virtual environment
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate   # On Windows

# Install all dependencies
uv pip install -r requirements.txt

# Install the package in development mode
uv pip install -e .
```

#### Option 2: Using Traditional Python/Conda

Create a virtual environment in any of your favorite environment managers:

```bash
conda create -n tradingagents python=3.13
conda activate tradingagents
```

Install dependencies:

```bash
pip install -r requirements.txt
pip install -e .
```

### Required APIs

You will need API keys for FinnHub (financial data) and OpenAI (LLM agents). All of our code is implemented with the free tier.

1. Copy the sample environment file:

   ```bash
   cp .env.sample .env
   ```

2. Edit `.env` and add your API keys:

   ```bash
   # Get your free FinnHub API key from: https://finnhub.io/register
   FINNHUB_API_KEY=your_finnhub_api_key_here

   # Get your OpenAI API key from: https://platform.openai.com/api-keys
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. The API keys will be automatically loaded when you run the CLI.

### CLI Usage

Run the CLI directly:

```bash
# With UV (recommended)
uv run python -m cli.main

# Or with standard Python
python -m cli.main
```

You will see a screen where you can select your desired tickers, date, LLMs, research depth, etc.

<p align="center">
  <img src="assets/cli/cli_init.png" alt="CLI initialization screenshot" width="100%" style="display: inline-block; margin: 0 2%;">
</p>

An interface will appear showing results as they load, letting you track the agent's progress as it runs.

<p align="center">
  <img src="assets/cli/cli_news.png" alt="CLI news screenshot" width="100%" style="display: inline-block; margin: 0 2%;">
</p>

<p align="center">
  <img src="assets/cli/cli_transaction.png" alt="CLI transaction screenshot" width="100%" style="display: inline-block; margin: 0 2%;">
</p>

### Troubleshooting

#### Common Issues

1. **ModuleNotFoundError: No module named 'tradingagents'**

   - Make sure you installed the package in development mode: `uv pip install -e .` or `pip install -e .`
   - This allows Python to find the local `tradingagents` module

2. **Missing tradingagents directory**

   - If you see deleted files in git status, restore them: `git restore tradingagents/`
   - This can happen if the directory was accidentally deleted

3. **API Key Errors**

   - Ensure your `.env` file exists and contains valid API keys
   - The `.env` file should be in the root directory of the project
   - API keys are automatically loaded when using the CLI

4. **UV-specific issues**
   - UV might recreate the virtual environment. Always activate it: `source .venv/bin/activate`
   - If dependencies are missing after UV commands, run: `uv pip install -r requirements.txt` again

5. **Rate Limiting and Capacity Errors**
   - If you encounter "over capacity" or 503 errors with Groq models, the system will automatically retry with exponential backoff
   - For batch processing, the system uses more stable models by default (`deepseek-r1-distill-llama-70b`)
   - You can override models using environment variables:
     - `TRADINGAGENTS_BATCH_MODEL`: Model for batch processing (default: `deepseek-r1-distill-llama-70b`)
     - `TRADINGAGENTS_SINGLE_MODEL`: Model for single analysis (default: uses your selection)
   - Example: `export TRADINGAGENTS_BATCH_MODEL=mixtral-8x7b-32768`

6. **Groq Configuration**
   - The system now uses Groq API instead of OpenAI
   - Make sure your `.env` file contains: `GROQ_API_KEY=your_groq_api_key`
   - Default models:
     - Quick Thinking: `deepseek-r1-distill-llama-70b` (fast reasoning)
     - Deep Thinking: `moonshotai/kimi-k2-instruct` (advanced analysis)
     - Batch Processing: `deepseek-r1-distill-llama-70b` (stable for long runs)
   - Available Groq models:
     - `deepseek-r1-distill-llama-70b` (excellent for quick analysis)
     - `moonshotai/kimi-k2-instruct` (advanced reasoning, may have capacity issues)
     - `deepseek-r1-distill-llama-70b` (recommended for stability)
     - `mixtral-8x7b-32768`
   - Environment variable overrides:
     - `TRADINGAGENTS_SINGLE_MODEL_DEEP`: Deep thinking model for single analysis
     - `TRADINGAGENTS_SINGLE_MODEL_QUICK`: Quick thinking model for single analysis
     - `TRADINGAGENTS_BATCH_MODEL`: Model for batch processing (default: deepseek-r1-distill-llama-70b)
   - The system automatically handles rate limiting with retry logic

## TradingAgents Package

### Implementation Details

We built TradingAgents with LangGraph to ensure flexibility and modularity. We utilize `o1-preview` and `gpt-4o` as our deep thinking and fast thinking LLMs for our experiments. However, for testing purposes, we recommend you use `o4-mini` and `gpt-4.1-mini` to save on costs as our framework makes **lots of** API calls.

### Python Usage

To use TradingAgents inside your code, you can import the `tradingagents` module and initialize a `TradingAgentsGraph()` object. The `.propagate()` function will return a decision. You can run `main.py`, here's also a quick example:

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

ta = TradingAgentsGraph(debug=True, config=DEFAULT_CONFIG.copy())

# forward propagate
_, decision = ta.propagate("NVDA", "2024-05-10")
print(decision)
```

You can also adjust the default configuration to set your own choice of LLMs, debate rounds, etc.

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# Create a custom config
config = DEFAULT_CONFIG.copy()
config["deep_think_llm"] = "gpt-4.1-nano"  # Use a different model
config["quick_think_llm"] = "gpt-4.1-nano"  # Use a different model
config["max_debate_rounds"] = 1  # Increase debate rounds
config["online_tools"] = True # Use online tools or cached data

# Initialize with custom config
ta = TradingAgentsGraph(debug=True, config=config)

# forward propagate
_, decision = ta.propagate("NVDA", "2024-05-10")
print(decision)
```

> For `online_tools`, we recommend enabling them for experimentation, as they provide access to real-time data. The agents' offline tools rely on cached data from our **Tauric TradingDB**, a curated dataset we use for backtesting. We're currently in the process of refining this dataset, and we plan to release it soon alongside our upcoming projects. Stay tuned!

You can view the full list of configurations in `tradingagents/default_config.py`.

## Contributing

We welcome contributions from the community! Whether it's fixing a bug, improving documentation, or suggesting a new feature, your input helps make this project better. If you are interested in this line of research, please consider joining our open-source financial AI research community [Tauric Research](https://tauric.ai/).

## Citation

Please reference our work if you find _TradingAgents_ provides you with some help :)

```bibtex
@misc{xiao2025tradingagentsmultiagentsllmfinancial,
      title={TradingAgents: Multi-Agents LLM Financial Trading Framework},
      author={Yijia Xiao and Edward Sun and Di Luo and Wei Wang},
      year={2025},
      eprint={2412.20138},
      archivePrefix={arXiv},
      primaryClass={q-fin.TR},
      url={https://arxiv.org/abs/2412.20138},
}
```

To run, use
uv run python -m cli.main
