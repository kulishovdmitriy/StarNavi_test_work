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
app.include_router(posts.router, prefix=f"{API_PREFIX}")
app.include_router(comments.router, prefix=f"{API_PREFIX}")


@app.get("/")
def read_root():
    """
    Root endpoint for the API.

    This endpoint returns a simple greeting message.

    :return: A dictionary containing a greeting message with the key "Hello"
             and the value "World".
    """

    return {"Hello": "World"}


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_database)):
    """
    Health checker endpoint to verify the database connection.

    This endpoint checks if the database is accessible by executing a simple
    query. If the query succeeds, it returns a welcome message. If the
    query fails or the database is not configured correctly, it raises
    an HTTPException with a corresponding error message.

    :param db: The database session dependency injected into the endpoint.
    :type db: AsyncSession
    :return: A JSON response containing a welcome message.
    :rtype: dict
    :raises HTTPException: If the database check fails or if there is a connection error.
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
