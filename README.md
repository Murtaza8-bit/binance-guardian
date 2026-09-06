# 🛡️ Binance Guardian – AI Trading Safety Agent

An AI-powered trading safety agent built with **Binance Agent OS** that interprets trading intent, evaluates it against live Binance portfolio data and user-defined risk policies, and returns an explainable ALLOW, RESIZE, or BLOCK decision before execution.

Guardian determines whether a trade should be:

* 🟢 **ALLOW** — The trade satisfies all configured safety policies.
* 🟡 **RESIZE** — The trade exceeds a risk limit, so Guardian reduces it to the maximum permitted amount.
* 🔴 **BLOCK** — The trade violates a critical safety rule and should not proceed.

> **Binance Guardian is a safety layer between AI trading intent and trade execution.**

---

## 🎯 Problem

AI agents can understand trading instructions, but understanding a request does not necessarily mean the requested action is safe for the user's portfolio.

For example:

> "Buy $300 of SOL."

An AI agent may correctly understand the request, but the user may have a personal rule such as:

> "Never let one asset exceed 15% of my portfolio."

Without a safety layer, the requested trade could exceed the user's intended risk.

**Binance Guardian** addresses this problem by checking trading intent against portfolio information and user-defined safety policies before execution.

---

## 💡 Solution

Binance Guardian acts as a policy-driven safety layer for AI-powered trading.

It combines:

* Trading intent
* Binance Agent OS account and market data
* User-defined risk policies
* Natural-language policy interpretation
* A deterministic policy engine
* Explainable risk checks
* An audit trail

AI interprets the user's trading intent and safety instructions, while Guardian's deterministic policy engine makes the final ALLOW, RESIZE, or BLOCK decision using Binance data and the user's configured risk policies.

The result is a simple safety decision:

```text
🟢 ALLOW
🟡 RESIZE
🔴 BLOCK
```

Instead of blindly following an AI-generated trading instruction, Guardian evaluates whether the action is consistent with the user's predefined safety rules.

---

## 🚀 Features

* 🛡️ **AI Trading Safety Layer** — Evaluates trading requests before execution.
* 🟢 **ALLOW** — Approves trades that satisfy all configured safety policies.
* 🟡 **RESIZE** — Reduces trades that exceed permitted risk limits.
* 🔴 **BLOCK** — Rejects trades that violate critical safety rules.
* 🧠 **Natural-Language Policies** — Converts user risk instructions into structured policies.
* 📊 **Portfolio-Aware** — Considers portfolio value, asset exposure, USDT balance, and market data.
* ⚡ **Binance Agent OS Integration** — Uses Binance Agent OS MCP for account and market data.
* 🔍 **Explainable Decisions** — Shows which risk checks passed or failed and why.
* 📝 **Audit Trail** — Records requests, portfolio data, policies, decisions, and execution status.
* 🔒 **Read-Only Safety** — Guardian currently does not place, modify, or cancel orders.
* 🖥️ **Interactive Dashboard** — Provides a visual interface for reviewing trade decisions.
* 🧪 **Automated Testing** — Includes tests for Guardian logic and dashboard functionality.

---

## 🛡️ Safety Policies

Guardian evaluates trading requests against configurable safety rules:

* **Maximum Trade Size**
* **Maximum Single-Asset Exposure**
* **Maximum Leverage**
* **Daily Loss Limit**
* **Minimum USDT Reserve**
* **Confirmation Requirement**

These rules can be configured in:

`config/policy.json`

### Example Natural-Language Policy

> "Never let me risk more than 15% on one asset, always keep at least 30% in USDT, and don't let me use more than 2x leverage."

Guardian converts the user's instructions into structured safety rules.

Example:

```text
Maximum asset exposure: 15%
Minimum USDT reserve:   30%
Maximum leverage:        2x
```

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
Portfolio Snapshot
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
```

---

## 🧪 Example Scenarios

### 🟢 ALLOW

User requests:

```text
Buy $50 BTC
```

If the request satisfies all configured policies:

```text
Decision: ALLOW
Requested: $50
Approved:  $50
```

Guardian allows the full requested amount.

---

### 🟡 RESIZE

User requests:

```text
Buy $300 SOL
```

Suppose:

```text
Portfolio value:        $500
Current SOL exposure:    $50
Maximum asset exposure:  15%
Maximum allowed SOL:     $75
Remaining SOL capacity:  $25
```

Guardian determines:

```text
Decision: RESIZE
Requested: $300
Approved:  $25
```

Instead of allowing the full $300 request, Guardian reduces it to the maximum amount that remains within the user's configured risk limits.

---

### 🔴 BLOCK

User requests:

```text
Buy $50 BTC using 10x leverage
```

User policy:

```text
Maximum leverage: 2x
```

Guardian determines:

```text
Decision: BLOCK
Approved: $0
Reason: Requested leverage exceeds the configured maximum.
```

The unsafe request is rejected before execution.

---

## 🔗 Binance Agent OS Integration

Binance Guardian integrates with **Binance Agent OS** through MCP.

Binance Agent OS provides access to relevant Binance account and market information, which Guardian uses to build a portfolio snapshot for risk evaluation.

The current implementation is intentionally read-only for safety.

Guardian currently does not:

* Place orders
* Cancel orders
* Modify orders
* Transfer funds
* Withdraw funds

This allows the safety system to evaluate portfolio information without executing real trades.

---

## 🧠 Natural-Language Policy Compiler

Guardian allows users to express safety rules using natural language.

For example:

```text
Never let me risk more than 15% on one asset,
always keep at least 30% in USDT,
and don't let me use more than 2x leverage.
```

The policy compiler extracts the relevant constraints:

```text
Maximum asset exposure: 15%
Minimum USDT reserve:   30%
Maximum leverage:        2x
```

These values are then passed to the deterministic policy engine.

The process is:

```text
Natural Language
       ↓
Structured Policy
       ↓
Deterministic Evaluation
```

---

## 🔍 Explainable Risk Checks

Guardian does not only return a final decision.

Each evaluation contains individual risk checks.

Example:

```text
Maximum Trade Size       FAIL
Maximum Leverage         PASS
Daily Loss Limit         PASS
Single-Asset Exposure    FAIL
USDT Reserve             PASS
```

This makes the decision explainable and allows the user to understand exactly why a request was allowed, resized, or blocked.

---

## 📝 Audit Trail

Guardian creates a structured audit record for reviewed trading requests.

The audit record can include:

* Trading request
* Timestamp
* Portfolio snapshot
* Active safety policy
* Risk checks
* Final decision
* Requested amount
* Approved amount
* Execution status

Example flow:

```text
Trade Request
      ↓
Portfolio Snapshot
      ↓
Policy Evaluation
      ↓
Risk Checks
      ↓
Decision
      ↓
Audit Record
```

---

## 🖥️ Interactive Dashboard

Binance Guardian includes a Flask-based web dashboard for reviewing trading requests.

The dashboard provides:

* Natural-language trade input
* Portfolio summary
* Guardian decision
* Requested amount
* Approved amount
* Risk checks
* Decision reasoning
* Execution status
* Audit information
* Demo scenarios
* Live Binance Agent OS mode

### Dashboard Modes

```text
🔵 LIVE — Binance Agent OS
🟢 DEMO — ALLOW
🟡 DEMO — RESIZE
🔴 DEMO — BLOCK
```

The demo modes make it possible to demonstrate Guardian's safety decisions without placing real orders.

---

## 📊 Architecture

```text
                    ┌──────────────────────┐
                    │        USER          │
                    │  Trading Intent      │
                    └──────────┬───────────┘
                               │
                               ↓
                    ┌──────────────────────┐
                    │   Guardian AI Layer  │
                    │  Intent Interpretation│
                    └──────────┬───────────┘
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
                 ↓                           ↓
      ┌───────────────────┐       ┌───────────────────┐
      │ Binance Agent OS  │       │ Natural-Language  │
      │ MCP               │       │ Policy Compiler   │
      │                   │       │                   │
      │ Account & Market  │       │ User Risk Rules   │
      │ Data              │       │                   │
      └─────────┬─────────┘       └─────────┬─────────┘
                │                           │
                └─────────────┬─────────────┘
                              ↓
                    ┌──────────────────────┐
                    │ Guardian Policy      │
                    │ Engine               │
                    │                      │
                    │ Deterministic Rules  │
                    └──────────┬───────────┘
                               │
                               ↓
                  ┌─────────────────────────┐
                  │     Safety Decision     │
                  │                         │
                  │  🟢 ALLOW               │
                  │  🟡 RESIZE              │
                  │  🔴 BLOCK               │
                  └────────────┬────────────┘
                               │
                               ↓
                    ┌──────────────────────┐
                    │     Audit Trail      │
                    └──────────────────────┘
```

---

## 📁 Project Structure

```text
binance-guardian/
│
├── app.py
├── requirements.txt
├── README.md
│
├── binance/
│   ├── __init__.py
│   └── account.py
│
├── config/
│   └── policy.json
│
├── guardian/
│   ├── __init__.py
│   ├── audit.py
│   ├── config.py
│   ├── guardian_tool.py
│   ├── intent.py
│   ├── mcp_server.py
│   ├── policy.py
│   └── policy_compiler.py
│
├── templates/
│   └── index.html
│
├── tests/
│   ├── test_guardian_dashboard.py
│   └── test_intent.py
│
└── .vscode/
    └── mcp.json
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/Murtaza8-bit/binance-guardian.git
cd binance-guardian
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

On Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Run the Dashboard

Start the Flask application:

```bash
python app.py
```

Open the local address displayed by Flask in your browser.

---

## 🧪 Run Tests

Run the automated test suite:

```bash
python -m unittest discover -s tests -v
```

The test suite covers:

* Intent parsing
* Guardian policy decisions
* Dashboard functionality

---

## 🔐 Security & Safety

Binance Guardian is designed with safety as a primary consideration.

The current implementation is **read-only**.

No real trade is executed by Guardian.

The system evaluates requests and returns a safety decision:

```text
Request
   ↓
Evaluate
   ↓
ALLOW / RESIZE / BLOCK
```

The execution layer is intentionally not enabled in the current hackathon prototype.

**Never commit API keys, secret keys, passwords, or other credentials to this repository.**

---

## 🏆 Hackathon

Built for the:

**Binance Agent OS Mini Hackathon — Track A**

### Track A

**Build an AI Agent using Binance Agent OS**

Binance Guardian demonstrates how Binance Agent OS can be combined with a policy-driven safety layer to make AI-assisted trading more controlled, explainable, and aligned with user-defined risk rules.

---

## 🎯 Core Idea

The goal of Binance Guardian is not to predict the market better.

The goal is to make sure an AI trading agent **doesn't take an action that violates the user's own safety rules.**

```text
AI understands the trade.
        ↓
Binance provides the data.
        ↓
Guardian checks the risk.
        ↓
User's policy defines the boundary.
        ↓
ALLOW / RESIZE / BLOCK
```

---

## 👨‍💻 Author

**Murtaza8-bit**

GitHub: [https://github.com/Murtaza8-bit/binance-guardian](https://github.com/Murtaza8-bit/binance-guardian)
