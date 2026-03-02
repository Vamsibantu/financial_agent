from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.yfinance import YFinanceTools
from phi.tools.duckduckgo import DuckDuckGo


# -----------------------------------------------------------------------------
# Agent Configuration Constants
# -----------------------------------------------------------------------------

AGENT_NAME      = "Multi AI Agent"
AGENT_MODEL_ID  = "meta-llama/llama-4-scout-17b-16e-instruct"
SHOW_TOOL_CALLS = True
MARKDOWN_OUTPUT = True

AGENT_INSTRUCTIONS = [
    "Always include sources",
    "Use tables to display the data",
    "For Indian stocks listed on NSE, always append '.NS' to the ticker symbol (e.g., TATAMOTORS.NS, RELIANCE.NS, INFY.NS)",
    "For Indian stocks listed on BSE, always append '.BO' to the ticker symbol (e.g., TATAMOTORS.BO)",
    "If the user asks about an Indian company by name, resolve it to the correct NSE ticker with '.NS' suffix before querying",
]


def build_duckduckgo_tool():
    try:
        return DuckDuckGo()
    except Exception as e:
        print(f"[multi_ai_agent] Failed to initialize DuckDuckGo tool: {e}")
        raise


def build_yfinance_tool():
    try:
        return YFinanceTools(
            stock_price=True,
            analyst_recommendations=True,
            stock_fundamentals=True,
            company_news=True,
        )
    except Exception as e:
        print(f"[multi_ai_agent] Failed to initialize YFinanceTools: {e}")
        raise


def build_groq_model():
    try:
        return Groq(id=AGENT_MODEL_ID)
    except Exception as e:
        print(f"[multi_ai_agent] Failed to initialize Groq model: {e}")
        raise


def build_multi_agent():
    try:
        model        = build_groq_model()
        search_tool  = build_duckduckgo_tool()
        finance_tool = build_yfinance_tool()
        return Agent(
            name=AGENT_NAME,
            model=model,
            tools=[search_tool, finance_tool],
            instructions=AGENT_INSTRUCTIONS,
            markdown=MARKDOWN_OUTPUT,
            show_tools_calls=SHOW_TOOL_CALLS,
        )
    except Exception as e:
        print(f"[multi_ai_agent] Failed to initialize agent: {e}")
        raise


multi_ai_agent = build_multi_agent()

