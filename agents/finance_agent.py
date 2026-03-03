from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.yfinance import YFinanceTools


# agent configuration
AGENT_NAME      = "Financial Agent"
AGENT_MODEL_ID  = "llama-3.3-70b-versatile"
SHOW_TOOL_CALLS = True
MARKDOWN_OUTPUT = True

AGENT_INSTRUCTIONS = [
    "Use tables to display the data",
    "For Indian stocks listed on NSE, always append '.NS' to the ticker symbol (e.g., TATAMOTORS.NS, RELIANCE.NS, INFY.NS)",
    "For Indian stocks listed on BSE, always append '.BO' to the ticker symbol (e.g., TATAMOTORS.BO)",
    "If the user asks about an Indian company by name, resolve it to the correct NSE ticker with '.NS' suffix before querying",
    # Safety guard: never call a tool unless ALL required parameters are known
    "IMPORTANT: Never call any tool or function unless you already have all required parameters from the user's message. "
    "If the stock symbol or company name is missing, ask the user to provide it BEFORE making any tool call. "
    "Do not attempt to call get_current_stock_price, get_stock_fundamentals, get_analyst_recommendations, "
    "or get_company_news without a concrete ticker symbol.",
]


def build_yfinance_tool():
    try:
        return YFinanceTools(
            stock_price=True,
            analyst_recommendations=True,
            stock_fundamentals=True,
            company_news=True,
        )
    except Exception as e:
        raise RuntimeError(f"[finance_agent] Failed to initialize YFinanceTools: {e}")


def build_groq_model():
    try:
        return Groq(id=AGENT_MODEL_ID)
    except Exception as e:
        raise RuntimeError(f"[finance_agent] Failed to initialize Groq model: {e}")


def build_finance_agent():
    try:
        model = build_groq_model()
        tool  = build_yfinance_tool()
        return Agent(
            name=AGENT_NAME,
            model=model,
            tools=[tool],
            instructions=AGENT_INSTRUCTIONS,
            show_tools_calls=SHOW_TOOL_CALLS,
            markdown=MARKDOWN_OUTPUT,
        )
    except Exception as e:
        raise RuntimeError(f"[finance_agent] Failed to build agent: {e}")


finance_agent = build_finance_agent()


