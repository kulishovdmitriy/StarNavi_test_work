import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.routes import posts, comments, auth
from src.database.db import get_database
from src.servises.logger import setup_logger


logger = setup_logger(__name__)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(posts.router, prefix="/api")
app.include_router(comments.router, prefix="/api")


@app.get("/")
def read_root():
    """
    :return: A dictionary containing a greeting message with key "Hello" and value "World".
    """
    return {"Hello": "World"}


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_database)):
    """
    :param db: The database session dependency injected into the endpoint.
    :return: A JSON response with a welcome message if the database check succeeds, or raises an HTTPException if it fails.
    """

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
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
