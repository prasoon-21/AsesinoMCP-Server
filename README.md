# ⚡ AsesinoMCP Server  
*A FastMCP-powered productivity ecosystem by Binary Asesino (B³ – Building Brick by Brick)*

---

## 🏗️ Built by Binary Asesino

**Binary Asesino** is a future-driven SaaS company founded and led by **Prasoon Mishra** —  
a passionate engineer on a mission to solve real-world problems with clean, scalable, and intelligent software solutions.  

Our philosophy:  
> “**B³ – Building Brick by Brick** — a future-driven company that brings tomorrow’s solutions into today’s world.”

**AsesinoMCP** is the **first product** under the Binary Asesino banner — a testament to innovation, precision, and purpose.  
It’s built not just to manage productivity, but to redefine how humans interact with their daily goals.

---

## 🚀 What Is AsesinoMCP?

**AsesinoMCP** is a modular **Model Context Protocol (MCP)** server designed to unify your personal and professional life under one roof — from tasks and habits to finances, expenses, and notes.  

It’s more than just a productivity tool.  
It’s your **digital ecosystem**, your **AI-ready life assistant**, and your **habit coach** — all powered by FastMCP and SQLite.

---

## 🧩 Core Features

### ✅ Task Manager (Doozy)
Stay ahead of your schedule with effortless task tracking.  
- Add, list, update, or delete tasks.  
- Categorize and subcategorize easily.  
- Get a clear **daily summary** at a glance.  

> Example: `add_task("2025-11-04", "Finish project docs", "Work", "Documentation", "Categorized")`

---

### 🔁 Habit Tracker (Hablo)
Consistency meets gamification.  
- Track habits with custom frequencies.  
- Earn credits and climb reward tiers — *Newbie → Bronze → Silver → Gold → Champion.*  
- Build momentum with positive reinforcement and progress tracking.  

---

### 🧾 Expense Tracker (Pockit)
Your financial clarity dashboard.  
- Record expenses with category & source.  
- View **category-wise** and **total summaries**.  
- Filter by custom date ranges for smarter insights.

> `summarize_expenses("2025-11-01", "2025-11-30")` → instant monthly breakdown.

---

### 📝 Notes Manager (Fynk) 
Keep your ideas safe, structured, and synced.  
- Add, edit, and delete notes.  
- Mark important ones for priority review.  
- Timestamped and neatly organized.  

> The perfect minimal note vault for thinkers and doers.

---

### 💰 Credit System
Your growth, visualized.  
- Each completed habit earns you **credit points**.  
- Your score reflects your consistency and growth mindset.  
- Unlock ranks and stay motivated through achievement tiers.

---

## ☁️ Hosted on FastMCP Cloud

Deploy **AsesinoMCP** seamlessly on [FastMCP Cloud](https://AsesinoMCP.fastmcp.app/mcp) and access it globally.

---

## To Run this MCP-server
- Must have python installed on your device
- Update pip or use UV package manager
- FastMCP/MCP SDK on your system

---

## To Run follow these steps 
i.) initialize the folder - uv init
ii.) install the fastMCP on your device - uv fastmcp
iii.) to run rthe server - uv run fastmcp run main.py
iv.) to check the health - uv main.py status
v.) to inspect the server - uv run fastmcp dev main.py
vi.) local - prefer STDIO transportation, for remote - prefer HTTP/SSE transportation
vii.) check the server by - list/tools, initialization, and seeking for thr prompt

---

## Tech Stack: 
- 🐍 Python 3.11+  
- ⚡ FastMCP Framework  
- 💾 Aiosqlite  
- 🚀 Uvicorn ASGI Server  
- 🧠 Pydantic & SQLAlchemy for Data Modeling

---

** If you have changes**
1. Fork the repo
2. Create a new branch (`add/your-feature`)
3. Commit your changes
4. Push and open a Pull Request
5. Star this repo if you find it useful! ⭐

---

**Developed by:** Prasoon Mishra  
**Company:** Binary Asesino (B³ – Building Brick by Brick)  
**Email:** binaryasesino@gmail.com


