import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.routes import posts, comments, auth
from src.database.db import get_database
from src.services.logger import setup_logger
from src.conf import messages


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

API_PREFIX = 'api/v1'

app.include_router(auth.router)
app.include_router(posts.router, prefix=f"/{API_PREFIX}")
app.include_router(comments.router, prefix=f"/{API_PREFIX}")


@app.get("/")
def read_root():
    """
    Root endpoint for the API.
    """

    return {"Hello": "World"}


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_database)):
    """
    Health checker endpoint to verify the database connection.
    """

    try:
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(
                status_code=500, detail=messages.DATABASE_NOT_CONFIGURED
            )
        return {"message": "Welcome to FastAPI!"}
    except Exception as err:
        logger.error(f"Error connecting to the database: {err}")
        raise HTTPException(status_code=500, detail=messages.DATABASE_CONNECTION_ERROR)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
