import aiosqlite

DB_NAME = "history.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                url TEXT NOT NULL,
                timestamp DATETIME
            )
        """)
        await db.commit()

async def add_download(user_id: int, url: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO downloads (user_id, url) VALUES (?, ?)",
            (user_id, url)
        )
        await db.commit()

async def get_user_history(user_id: int, limit: int = 10):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT url, timestamp FROM downloads WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, limit)
        )
        return await cursor.fetchall()

async def clear_user_history(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "DELETE FROM downloads WHERE user_id = ?",
            (user_id,)
        )
        await db.commit()
