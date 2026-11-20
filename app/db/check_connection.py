import asyncio
from sqlalchemy import text
from app.db.session import engine


async def check_connection():
    async with engine.connect() as connection:
        result = await connection.execute(text("SELECT 1"))
        print("Database connection successful!")
        print("Test result:", result.scalar())

    await engine.dispose()


asyncio.run(check_connection())