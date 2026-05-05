import asyncio
import asyncpg

async def check():
    try:
        conn = await asyncpg.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password="sqlWw159123",
            database="sbs_db"
        )
        print("✅ База данных работает!")
        await conn.close()
    except Exception as e:
        print(f"❌ Ошибка: {e}")

asyncio.run(check())