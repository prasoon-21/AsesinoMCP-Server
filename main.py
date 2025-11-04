from fastmcp import FastMCP
import sqlite3
import datetime
import os

BASE_DIR = os.path.dirname(__file__)
TASK_DB = os.path.join(BASE_DIR, "Doozy.db")
HABIT_DB = os.path.join(BASE_DIR, "Habits.db")
FINANCE_DB = os.path.join(BASE_DIR, "Finance.db")
EXPENSE_DB = os.path.join(BASE_DIR, "Expenses.db")
NOTES_DB = os.path.join(BASE_DIR, "Notes.db")
CATEGORY_PATH = os.path.join(BASE_DIR, "category.json")

mcp = FastMCP("AsesinoMCP")

def init_db():
    conn = sqlite3.connect(TASK_DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS Doozy(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            task TEXT NOT NULL,
            category TEXT NOT NULL,
            subCategory TEXT NOT NULL,
            note TEXT DEFAULT ''
        )
    """)
    conn.commit()
    conn.close()

    conn = sqlite3.connect(HABIT_DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS Habits(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            subCategory TEXT,
            frequency TEXT NOT NULL,
            progress INTEGER DEFAULT 0,
            goal INTEGER DEFAULT 0,
            note TEXT DEFAULT '',
            highlighted INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

    conn = sqlite3.connect(FINANCE_DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS Credits(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL DEFAULT 'default',
            credit INTEGER DEFAULT 21,
            last_updated TEXT DEFAULT ''
        )
    """)
    conn.commit()
    conn.close()

    conn = sqlite3.connect(EXPENSE_DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS Expenses(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            source TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            note TEXT DEFAULT ''
        )
    """)
    conn.commit()
    conn.close()

    conn = sqlite3.connect(NOTES_DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS Notes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            important INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def get_reward_tier(credit: int):
    if credit < 50:
        return {"message": "You have guts 💪", "rank": "Newbie"}
    elif credit < 100:
        return {"message": "You can do it!", "rank": "Bronze"}
    elif credit < 147:
        return {"message": "You have potential, one more and you can make it!", "rank": "Silver"}
    elif credit < 200:
        return {"message": "You are built to develop!", "rank": "Gold"}
    else:
        return {"message": "You made it!", "rank": "Champion"}

@mcp.tool()
async def add_task(date: str, task: str = "", category: str = "", subCategory: str = "", note: str = ""):
    """Add a new task to Doozy"""
    conn = sqlite3.connect(TASK_DB)
    c = conn.cursor()
    c.execute(
        "INSERT INTO Doozy(date, task, category, subCategory, note) VALUES (?, ?, ?, ?, ?)",
        (date, task, category, subCategory, note)
    )
    conn.commit()
    last_id = c.lastrowid
    conn.close()
    return {"status": "ok", "id": last_id}


@mcp.tool()
async def list_task(start_date: str, end_date: str):
    """List tasks between start_date and end_date"""
    conn = sqlite3.connect(TASK_DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
        SELECT id, date, task, category, note
        FROM Doozy
        WHERE date BETWEEN ? AND ?
        ORDER BY id ASC
    """, (start_date, end_date))
    rows = c.fetchall()
    result = [dict(row) for row in rows]
    conn.close()
    return result


@mcp.tool()
async def update_task(id: int, date: str, task: str, category: str, subCategory: str, note: str):
    """Update an existing task"""
    conn = sqlite3.connect(TASK_DB)
    c = conn.cursor()
    c.execute("""
        UPDATE Doozy
        SET date=?, task=?, category=?, subCategory=?, note=?
        WHERE id=?
    """, (date, task, category, subCategory, note, id))
    conn.commit()
    conn.close()
    return {"status": "ok", "id": id}


@mcp.tool()
async def delete_task(id: int):
    """Delete a task by ID"""
    conn = sqlite3.connect(TASK_DB)
    c = conn.cursor()
    c.execute("DELETE FROM Doozy WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return {"status": "deleted", "id": id}


@mcp.tool()
async def summary():
    """Get summary of all tasks"""
    conn = sqlite3.connect(TASK_DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
        SELECT id, date, task, category, note
        FROM Doozy
        ORDER BY id ASC
    """)
    rows = c.fetchall()
    result = [dict(row) for row in rows]
    conn.close()
    return result


@mcp.tool()
async def add_habit(name: str, category: str, subCategory: str = "", frequency: str = "daily", 
                    goal: int = 30, note: str = "", highlighted: bool = False):
    """Add a new habit to track"""
    conn = sqlite3.connect(HABIT_DB)
    c = conn.cursor()
    c.execute("""
        INSERT INTO Habits(name, category, subCategory, frequency, goal, note, highlighted)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, category, subCategory, frequency, goal, note, int(highlighted)))
    conn.commit()
    last_id = c.lastrowid
    conn.close()
    return {"status": "ok", "id": last_id}


@mcp.tool()
async def update_habit_progress(habit_id: int, done_today: bool):
    """Update habit progress and credit system"""
    today = datetime.date.today().isoformat()

    conn = sqlite3.connect(HABIT_DB)
    c = conn.cursor()
    if done_today:
        c.execute("UPDATE Habits SET progress = progress + 1 WHERE id = ?", (habit_id,))
        conn.commit()
    conn.close()

    conn = sqlite3.connect(FINANCE_DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT id, credit, last_updated FROM Credits WHERE user='default'")
    row = c.fetchone()

    if row is None:
        credit = 21 + (1 if done_today else 0)
        c.execute(
            "INSERT INTO Credits(user, credit, last_updated) VALUES ('default', ?, ?)",
            (credit, today)
        )
    else:
        row_id, credit, last_updated = row['id'], row['credit'], row['last_updated']
        if last_updated != today and not done_today:
            credit = max(0, credit - 1)
        if done_today:
            credit += 1
        c.execute(
            "UPDATE Credits SET credit=?, last_updated=? WHERE id=?",
            (credit, today, row_id)
        )
    conn.commit()
    conn.close()

    reward = get_reward_tier(credit)
    return {"current_credit": credit, "reward": reward}


@mcp.tool()
async def get_credit():
    """Get current credit and reward tier"""
    conn = sqlite3.connect(FINANCE_DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT credit FROM Credits WHERE user='default'")
    row = c.fetchone()
    credit = row['credit'] if row else 21
    conn.close()
    reward = get_reward_tier(credit)
    return {"current_credit": credit, "reward": reward}


@mcp.tool()
async def list_habits():
    """List all habits"""
    conn = sqlite3.connect(HABIT_DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM Habits ORDER BY id ASC")
    rows = c.fetchall()
    result = [dict(row) for row in rows]
    conn.close()
    return result

@mcp.tool()
async def add_expense(date: str, source: str, category: str, amount: float, note: str = ""):
    """Add a new expense"""
    conn = sqlite3.connect(EXPENSE_DB)
    c = conn.cursor()
    c.execute("""
        INSERT INTO Expenses(date, source, category, amount, note)
        VALUES (?, ?, ?, ?, ?)
    """, (date, source, category, amount, note))
    conn.commit()
    last_id = c.lastrowid
    conn.close()
    return {"status": "ok", "id": last_id}


@mcp.tool()
async def list_expenses(start_date: str = None, end_date: str = None):
    """List expenses, optionally filtered by date range"""
    conn = sqlite3.connect(EXPENSE_DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    if start_date and end_date:
        c.execute("""
            SELECT * FROM Expenses WHERE date BETWEEN ? AND ? ORDER BY date ASC
        """, (start_date, end_date))
    else:
        c.execute("SELECT * FROM Expenses ORDER BY date ASC")
    rows = c.fetchall()
    result = [dict(row) for row in rows]
    conn.close()
    return result


@mcp.tool()
async def summarize_expenses(start_date: str = None, end_date: str = None):
    """Get expense summary by category"""
    conn = sqlite3.connect(EXPENSE_DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    if start_date and end_date:
        c.execute("""
            SELECT category, SUM(amount) AS total FROM Expenses
            WHERE date BETWEEN ? AND ? GROUP BY category
        """, (start_date, end_date))
        total_row = c.execute("""
            SELECT SUM(amount) FROM Expenses WHERE date BETWEEN ? AND ?
        """, (start_date, end_date)).fetchone()
    else:
        c.execute("SELECT category, SUM(amount) AS total FROM Expenses GROUP BY category")
        total_row = c.execute("SELECT SUM(amount) FROM Expenses").fetchone()

    summary = [dict(row) for row in c.fetchall()]
    total = total_row[0] if total_row[0] else 0
    conn.close()
    return {"total_expense": total, "by_category": summary}


@mcp.tool()
async def add_note(title: str, content: str, important: bool = False):
    """Add a new note"""
    conn = sqlite3.connect(NOTES_DB)
    c = conn.cursor()
    c.execute("""
        INSERT INTO Notes(title, content, important)
        VALUES (?, ?, ?)
    """, (title, content, 1 if important else 0))
    conn.commit()
    last_id = c.lastrowid
    conn.close()
    return {"status": "ok", "id": last_id}


@mcp.tool()
async def list_notes(important_only: bool = False):
    """List notes, optionally filtering for important ones only"""
    conn = sqlite3.connect(NOTES_DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    if important_only:
        c.execute("SELECT * FROM Notes WHERE important=1 ORDER BY created_at DESC")
    else:
        c.execute("SELECT * FROM Notes ORDER BY created_at DESC")
    rows = c.fetchall()
    result = [dict(row) for row in rows]
    conn.close()
    return result


@mcp.resource("category://list")
async def category():
    """Get category list"""
    try:
        if os.path.exists(CATEGORY_PATH):
            return '{"categories": ["Work", "Personal", "Health", "Learning"]}'
        return '{"categories": []}'
    except Exception as e:
        return f'{{"error": "{str(e)}"}}'

if __name__ == "__main__":
    init_db()
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8000
    )