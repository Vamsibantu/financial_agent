# Financial Agent

A multi-agent AI system built with Phidata, Groq LLMs, and Yahoo Finance to fetch stock data, analyst recommendations, fundamentals, and company news — including full support for Indian stocks.

---

## Project Setup

### 1. Create a Virtual Environment

```bash
py -3.11 -m venv venv
```

### 2. Activate the Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```
**macOS / Linux:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the `.env` File

Create a `.env` file in the project root with the following keys:

```env
PHIDATA_API_KEY=your_phidata_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

| Key | Description |
| `GROQ_API_KEY` | API key for Groq LLM inference |

### 5. Run the Agent

```bash
python financial_agent.py
```

---

## Indian Stocks — Ticker Symbol Rules

Yahoo Finance requires exchange-specific suffixes to identify Indian stocks. Without these, queries will fail or return wrong data.

### Exchange Suffixes

| Exchange | Suffix | Example |
|---|---|---|
| National Stock Exchange (NSE) | `.NS` | `TATAMOTORS.NS` |
| Bombay Stock Exchange (BSE) | `.BO` | `TATAMOTORS.BO` |

> **Default:** Prefer `.NS` (NSE) unless you specifically need BSE data.

### Common Indian Stock Tickers

| Company | NSE Ticker | BSE Ticker |
|---|---|---|
| Tata Motors | `TATAMOTORS.NS` | `TATAMOTORS.BO` |
| Reliance Industries | `RELIANCE.NS` | `RELIANCE.BO` |
| Infosys | `INFY.NS` | `INFY.BO` |
| Tata Consultancy Services | `TCS.NS` | `TCS.BO` |
| HDFC Bank | `HDFCBANK.NS` | `HDFCBANK.BO` |
| Wipro | `WIPRO.NS` | `WIPRO.BO` |
| State Bank of India | `SBIN.NS` | `SBIN.BO` |
| ITC | `ITC.NS` | `ITC.BO` |

### How to Find the Correct Ticker

1. Visit [finance.yahoo.com](https://finance.yahoo.com)
2. Search the company name
3. Select the result showing `.NS` (NSE) or `.BO` (BSE) in the ticker

### Rules Enforced in the Agent

The agents are instructed to:
- Automatically append `.NS` for any Indian company name query on NSE
- Automatically append `.BO` for BSE-specific queries
- Resolve company names to correct tickers before calling Yahoo Finance

---

## Agents Overview

| Agent | Model | Tools | Purpose |
|---|---|---|---|
| Financial Agent | `llama-3.3-70b-versatile` | YFinance | Stock price, fundamentals, news |
| Web Search Agent | `llama-3.3-70b-versatile` | DuckDuckGo | Web search with sources |
| Multi AI Agent | `llama-4-scout-17b-16e-instruct` | YFinance + DuckDuckGo | Combined financial + web data |

