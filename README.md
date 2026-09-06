# 🛡️ Binance Guardian – AI Trading Safety Agent

An AI-powered trading safety agent built with Binance Agent OS that evaluates trading intent against portfolio data and user-defined risk policies before execution. Guardian determines whether a trade should be **ALLOWED, RESIZED, or BLOCKED** based on configurable safety rules.

---

## 🚀 Features

- 🛡️ **AI Trading Safety Layer:** Evaluates trading requests before execution
- 🟢 **ALLOW:** Approves trades that satisfy all configured safety policies
- 🟡 **RESIZE:** Reduces trades that exceed risk limits to the maximum permitted amount
- 🔴 **BLOCK:** Rejects trades that violate critical safety rules
- 🧠 **Natural-Language Policies:** Converts user risk instructions into structured safety rules
- 📊 **Portfolio-Aware:** Considers portfolio value, asset exposure, USDT balance, and market data
- ⚡ **Binance Agent OS Integration:** Uses Binance Agent OS MCP for account and market data
- 🔍 **Explainable Decisions:** Shows which risk checks passed or failed and why
- 📝 **Audit Trail:** Records trade requests, portfolio data, policies, decisions, and execution status
- 🔒 **Read-Only Safety:** Guardian currently does not place, modify, or cancel orders
- 🖥️ **Interactive Dashboard:** Provides a visual interface for reviewing trade decisions
- 🧪 **Automated Testing:** Includes tests for Guardian logic and dashboard functionality

---

## 🛡️ Safety Policies

Guardian evaluates trades against configurable safety rules:

- **Maximum Trade Size**
- **Maximum Single-Asset Exposure**
- **Maximum Leverage**
- **Daily Loss Limit**
- **Minimum USDT Reserve**
- **Confirmation Requirement**

Example natural-language policy:

> "Never let me risk more than 15% on one asset, always keep at least 30% in USDT, and don't let me use more than 2x leverage."

Guardian converts these instructions into structured risk policies before evaluating a trade.

---

## 🔄 How It Works

```text
User Trading Intent
        ↓
Guardian Intent Parser
        ↓
Binance Agent OS
(Account & Market Data)
        ↓
Guardian Policy Engine
        ↓
┌─────────┬─────────┬─────────┐
│  ALLOW  │ RESIZE  │  BLOCK  │
└─────────┴─────────┴─────────┘
        ↓
  Safety Decision
        ↓
    Audit Trail
