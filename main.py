import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.routes import posts, comments
from src.database.db import get_database
from src.servises.logger import setup_logger


logger = setup_logger(__name__)

app = FastAPI()

app.include_router(posts.router, prefix="/api")
app.include_router(comments.router, prefix="/api")


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_database)):

    try:
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(
                status_code=500, detail="Database is not configured correctly"
            )
        return {"message": "Welcome to FastAPI!"}
    except Exception as err:
        logger.error(f"Error connecting to the database: {err}")
        raise HTTPException(status_code=500, detail="Error connecting to the database")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
