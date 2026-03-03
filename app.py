# =============================================================================
# app.py — FastAPI web server for the Financial Agent UI
# =============================================================================

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os
import traceback

# ── Load environment ─────────────────────────────────────────────────────────
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY is not set. Check your .env file.")
os.environ["GROQ_API_KEY"] = api_key

# ── Import agents ────────────────────────────────────────────────────────────
from agents.finance_agent import finance_agent
from agents.web_search_agent import web_search_agent
from agents.multi_agent import multi_ai_agent

# ── FastAPI app ──────────────────────────────────────────────────────────────
app = FastAPI(title="Finance Sight")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

AGENT_MAP = {
    "finance":    finance_agent,
    "web_search": web_search_agent,
    "multi":      multi_ai_agent,
    "auto":       multi_ai_agent,   # safety fallback — detect_agent() replaces this at runtime
}

# ── Keyword-based auto-routing ────────────────────────────────────────────────
_FINANCE_KEYWORDS = {
    "stock", "share", "price", "ticker", "market", "nse", "bse",
    "nasdaq", "nyse", "dividend", "earnings", "pe ratio", "fundamental",
    "analyst", "recommendation", "portfolio", "trading", "invest",
    "equity", "fund", "etf", "option", "bond", "crypto", "bitcoin",
    "ipo", "sensex", "nifty", "dow", "s&p", "futures",
}
_WEB_SEARCH_KEYWORDS = {
    "news", "latest", "recent", "search", "today", "current events",
    "who is", "what is", "when was", "where is", "how does", "why does",
    "explain", "history", "definition", "weather", "trending",
    "blog", "article", "website", "government", "policy", "election",
    "sports", "technology", "science", "health", "medicine",
}


def detect_agent(query: str) -> str:
    """
    Automatically pick the best agent based on query keywords.

    Returns one of: 'finance', 'web_search', 'multi'
    """
    lower = query.lower()
    has_finance = any(kw in lower for kw in _FINANCE_KEYWORDS)
    has_web     = any(kw in lower for kw in _WEB_SEARCH_KEYWORDS)

    if has_finance and has_web:
        return "multi"       # query needs both tools
    if has_finance:
        return "finance"
    if has_web:
        return "web_search"
    return "multi"           # default fallback — multi can handle anything


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the main UI page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/query")
async def query_agent(request: Request):
    """
    Accept a JSON body with:
        { "agent": "finance" | "web_search" | "multi", "query": "..." }
    Run the selected agent and return the response.
    """
    try:
        body = await request.json()
        agent_key  = body.get("agent", "auto")
        user_query = body.get("query", "").strip()

        if not user_query:
            return JSONResponse({"success": False, "error": "Query cannot be empty."})

        # ── Auto-routing: pick the best agent for this query ──────────────────
        if agent_key == "auto":
            agent_key = detect_agent(user_query)

        agent = AGENT_MAP.get(agent_key)
        if not agent:
            return JSONResponse(
                {"success": False, "error": f"Unknown agent: {agent_key}"}
            )

        # Use agent.run() to get the response programmatically
        response = agent.run(user_query)

        # Extract content from RunResponse
        content = ""
        if hasattr(response, "content") and response.content:
            content = response.content
        elif hasattr(response, "messages") and response.messages:
            # Fallback: get the last assistant message
            for msg in reversed(response.messages):
                if hasattr(msg, "content") and msg.content:
                    content = msg.content
                    break
        
        if not content:
            content = str(response)

        return JSONResponse({"success": True, "response": content, "agent_used": agent_key})

    except Exception as e:
        traceback.print_exc()
        error_msg = str(e)

        # ── GROQ tool-call validation error (400) ────────────────────────────
        # Happens when the LLM tries to call a tool without all required
        # parameters (e.g. calling get_current_stock_price without 'symbol').
        if "tool call validation failed" in error_msg or "missing properties" in error_msg:
            friendly = (
                "The agent tried to look up data before you provided a stock symbol or company name. "
                "Please include the stock name or ticker in your query "
                "(e.g. \"What is the stock price of Reliance?\")."
            )
            return JSONResponse(
                {"success": False, "error": friendly},
                status_code=400,
            )

        # ── Generic agent / API errors ────────────────────────────────────────
        return JSONResponse(
            {"success": False, "error": f"Agent error: {error_msg}"},
            status_code=500,
        )


# ── Run with: python app.py ─────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
