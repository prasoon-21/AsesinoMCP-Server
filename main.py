from fastmcp import FastMCP
import aiosqlite
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
async def init_db():
    async with aiosqlite.connect(TASK_DB) as c:
        await c.execute("""
            CREATE TABLE IF NOT EXISTS Doozy(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                task TEXT NOT NULL,
                category TEXT NOT NULL,
                subCategory TEXT NOT NULL,
                note TEXT DEFAULT ''
            )
        """)
        await c.commit()

    async with aiosqlite.connect(HABIT_DB) as c:
        await c.execute("""
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
        await c.commit()

    async with aiosqlite.connect(FINANCE_DB) as c:
        await c.execute("""
            CREATE TABLE IF NOT EXISTS Credits(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT NOT NULL DEFAULT 'default',
                credit INTEGER DEFAULT 21,
                last_updated TEXT DEFAULT ''
            )
        """)
        await c.commit()

    async with aiosqlite.connect(EXPENSE_DB) as c:
        await c.execute("""
            CREATE TABLE IF NOT EXISTS Expenses(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                source TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                note TEXT DEFAULT ''
            )
        """)
        await c.commit()

    async with aiosqlite.connect(NOTES_DB) as c:
        await c.execute("""
            CREATE TABLE IF NOT EXISTS Notes(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                important INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await c.commit()


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
    async with aiosqlite.connect(TASK_DB) as c:
        cur = await c.execute(
            "INSERT INTO Doozy(date, task, category, subCategory, note) VALUES (?, ?, ?, ?, ?)",
            (date, task, category, subCategory, note)
        )
        await c.commit()
        return {"status": "ok", "id": cur.lastrowid}


@mcp.tool()
async def list_task(start_date: str, end_date: str):
    """List tasks between start_date and end_date"""
    async with aiosqlite.connect(TASK_DB) as c:
        cur = await c.execute("""
            SELECT id, date, task, category, note
            FROM Doozy
            WHERE date BETWEEN ? AND ?
            ORDER BY id ASC
        """, (start_date, end_date))
        rows = await cur.fetchall()
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in rows]


@mcp.tool()
async def update_task(id: int, date: str, task: str, category: str, subCategory: str, note: str):
    """Update an existing task"""
    async with aiosqlite.connect(TASK_DB) as c:
        await c.execute("""
            UPDATE Doozy
            SET date=?, task=?, category=?, subCategory=?, note=?
            WHERE id=?
        """, (date, task, category, subCategory, note, id))
        await c.commit()
        return {"status": "ok", "id": id}


@mcp.tool()
async def delete_task(id: int):
    """Delete a task by ID"""
    async with aiosqlite.connect(TASK_DB) as c:
        await c.execute("DELETE FROM Doozy WHERE id=?", (id,))
        await c.commit()
        return {"status": "deleted", "id": id}


@mcp.tool()
async def summary():
    """Get summary of all tasks"""
    async with aiosqlite.connect(TASK_DB) as c:
        cur = await c.execute("""
            SELECT id, date, task, category, note
            FROM Doozy
            ORDER BY id ASC
        """)
        rows = await cur.fetchall()
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in rows]


@mcp.tool()
async def add_habit(name: str, category: str, subCategory: str = "", frequency: str = "daily", 
                    goal: int = 30, note: str = "", highlighted: bool = False):
    """Add a new habit to track"""
    async with aiosqlite.connect(HABIT_DB) as c:
        cur = await c.execute("""
            INSERT INTO Habits(name, category, subCategory, frequency, goal, note, highlighted)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, category, subCategory, frequency, goal, note, int(highlighted)))
        await c.commit()
        return {"status": "ok", "id": cur.lastrowid}


@mcp.tool()
async def update_habit_progress(habit_id: int, done_today: bool):
    """Update habit progress and credit system"""
    today = datetime.date.today().isoformat()

    async with aiosqlite.connect(HABIT_DB) as c:
        if done_today:
            await c.execute("UPDATE Habits SET progress = progress + 1 WHERE id = ?", (habit_id,))
            await c.commit()

    async with aiosqlite.connect(FINANCE_DB) as c:
        cur = await c.execute("SELECT id, credit, last_updated FROM Credits WHERE user='default'")
        row = await cur.fetchone()

        if row is None:
            credit = 21 + (1 if done_today else 0)
            await c.execute(
                "INSERT INTO Credits(user, credit, last_updated) VALUES ('default', ?, ?)",
                (credit, today)
            )
        else:
            row_id, credit, last_updated = row
            if last_updated != today and not done_today:
                credit = max(0, credit - 1)
            if done_today:
                credit += 1
            await c.execute(
                "UPDATE Credits SET credit=?, last_updated=? WHERE id=?",
                (credit, today, row_id)
            )
        await c.commit()

    reward = await get_reward_tier(credit)
    return {"current_credit": credit, "reward": reward}


@mcp.tool()
async def get_credit():
    """Get current credit and reward tier"""
    async with aiosqlite.connect(FINANCE_DB) as c:
        cur = await c.execute("SELECT credit FROM Credits WHERE user='default'")
        row = await cur.fetchone()
        credit = row[0] if row else 21
        reward = await get_reward_tier(credit)
        return {"current_credit": credit, "reward": reward}


@mcp.tool()
async def list_habits():
    """List all habits"""
    async with aiosqlite.connect(HABIT_DB) as c:
        cur = await c.execute("SELECT * FROM Habits ORDER BY id ASC")
        rows = await cur.fetchall()
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in rows]

@mcp.tool()
async def add_expense(date: str, source: str, category: str, amount: float, note: str = ""):
    """Add a new expense"""
    async with aiosqlite.connect(EXPENSE_DB) as c:
        cur = await c.execute("""
            INSERT INTO Expenses(date, source, category, amount, note)
            VALUES (?, ?, ?, ?, ?)
        """, (date, source, category, amount, note))
        await c.commit()
        return {"status": "ok", "id": cur.lastrowid}


@mcp.tool()
async def list_expenses(start_date: str = None, end_date: str = None):
    """List expenses, optionally filtered by date range"""
    async with aiosqlite.connect(EXPENSE_DB) as c:
        if start_date and end_date:
            cur = await c.execute("""
                SELECT * FROM Expenses WHERE date BETWEEN ? AND ? ORDER BY date ASC
            """, (start_date, end_date))
        else:
            cur = await c.execute("SELECT * FROM Expenses ORDER BY date ASC")
        rows = await cur.fetchall()
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in rows]


@mcp.tool()
async def summarize_expenses(start_date: str = None, end_date: str = None):
    """Get expense summary by category"""
    async with aiosqlite.connect(EXPENSE_DB) as c:
        if start_date and end_date:
            cur = await c.execute("""
                SELECT category, SUM(amount) AS total FROM Expenses
                WHERE date BETWEEN ? AND ? GROUP BY category
            """, (start_date, end_date))
            total_cur = await c.execute("""
                SELECT SUM(amount) FROM Expenses WHERE date BETWEEN ? AND ?
            """, (start_date, end_date))
        else:
            cur = await c.execute("SELECT category, SUM(amount) AS total FROM Expenses GROUP BY category")
            total_cur = await c.execute("SELECT SUM(amount) FROM Expenses")

        summary = [dict(zip([d[0] for d in cur.description], r)) for r in await cur.fetchall()]
        total = (await total_cur.fetchone())[0] or 0
        return {"total_expense": total, "by_category": summary}


@mcp.tool()
async def add_note(title: str, content: str, important: bool = False):
    """Add a new note"""
    async with aiosqlite.connect(NOTES_DB) as c:
        cur = await c.execute("""
            INSERT INTO Notes(title, content, important)
            VALUES (?, ?, ?)
        """, (title, content, 1 if important else 0))
        await c.commit()
        return {"status": "ok", "id": cur.lastrowid}


@mcp.tool()
async def list_notes(important_only: bool = False):
    """List notes, optionally filtering for important ones only"""
    async with aiosqlite.connect(NOTES_DB) as c:
        if important_only:
            cur = await c.execute("SELECT * FROM Notes WHERE important=1 ORDER BY created_at DESC")
        else:
            cur = await c.execute("SELECT * FROM Notes ORDER BY created_at DESC")
        rows = await cur.fetchall()
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in rows]


@mcp.resource("category://list")
async def category():
    """Get category list"""
    try:
        if os.path.exists(CATEGORY_PATH):
            async with aiosqlite.connect(TASK_DB) as _:
                # Simplified resource return
                return '{"categories": ["Work", "Personal", "Health", "Learning"]}'
        return '{"categories": []}'
    except Exception as e:
        return f'{{"error": "{str(e)}"}}'

if __name__ == "__main__":
    import asyncio
    asyncio.run(init_db())
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8000
    )