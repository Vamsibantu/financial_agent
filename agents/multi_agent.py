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
    # Safety guard: never call a finance tool without a known symbol
    "IMPORTANT: Never call any finance tool (get_current_stock_price, get_stock_fundamentals, etc.) "
    "unless you already have a concrete stock symbol from the user's message. "
    "If the symbol is missing, ask the user to provide it BEFORE making any tool call. "
    "For general questions (news, definitions, explanations), use DuckDuckGo web search instead.",
]


def build_duckduckgo_tool():
    try:
        return DuckDuckGo()
    except Exception as e:
        raise RuntimeError(f"[multi_ai_agent] Failed to initialize DuckDuckGo tool: {e}")


def build_yfinance_tool():
    try:
        return YFinanceTools(
            stock_price=True,
            analyst_recommendations=True,
            stock_fundamentals=True,
            company_news=True,
        )
    except Exception as e:
        raise RuntimeError(f"[multi_ai_agent] Failed to initialize YFinanceTools: {e}")


def build_groq_model():
    try:
        return Groq(id=AGENT_MODEL_ID)
    except Exception as e:
        raise RuntimeError(f"[multi_ai_agent] Failed to initialize Groq model: {e}")


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
        raise RuntimeError(f"[multi_ai_agent] Failed to initialize agent: {e}")


multi_ai_agent = build_multi_agent()

