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
app = FastAPI(title="Financial Agent")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

AGENT_MAP = {
    "finance": finance_agent,
    "web_search": web_search_agent,
    "multi": multi_ai_agent,
}


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
        agent_key = body.get("agent", "finance")
        user_query = body.get("query", "").strip()

        if not user_query:
            return JSONResponse({"success": False, "error": "Query cannot be empty."})

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

        return JSONResponse({"success": True, "response": content})

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            {"success": False, "error": f"Agent error: {str(e)}"},
            status_code=500,
        )


# ── Run with: python app.py ─────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
