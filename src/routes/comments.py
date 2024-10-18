from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_database
from src.repository.comments import (
    get_comments,
    create_comment,
    update_comment,
    delete_comment,
    get_comment_by_post,
    get_comments_daily_breakdown
)
from src.schemas.comments import CreateCommentSchema, UpdateCommentSchema, ResponseCommentSchema
from src.servises.logger import setup_logger


logger = setup_logger(__name__)

router = APIRouter(prefix='/comments', tags=['comments'])


@router.get('/{post_id:int}', response_model=list[ResponseCommentSchema])
async def get_comments_view(post_id: int, db: AsyncSession = Depends(get_database)):
    comments = await get_comments(post_id, db)
    if not comments:
        logger.error(f"No comments found for post with id {post_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No comments found for post with id {post_id}")
    return comments


@router.get('/posts/{post_id}/comments/{comment_id}', response_model=ResponseCommentSchema)
async def get_comment_view(post_id: int, comment_id: int, db: AsyncSession = Depends(get_database)):
    comment = await get_comment_by_post(post_id, comment_id, db)
    if not comment:
        logger.error(f"No comment found with id {comment_id} for post with id {post_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No comment found with id {comment_id} for post with id {post_id}")
    return comment


@router.post('/create', response_model=ResponseCommentSchema, status_code=status.HTTP_201_CREATED)
async def create_comment_view(post_id: int, body: CreateCommentSchema, db: AsyncSession = Depends(get_database)):
    try:
        new_comment = await create_comment(post_id, body, db)
        return new_comment
    except Exception as e:
        logger.error(f"Failed to create comment for post {post_id}: {e}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Failed to create comment")


@router.put('/{comment_id:int}', response_model=ResponseCommentSchema, status_code=status.HTTP_202_ACCEPTED)
async def update_comment_view(comment_id: int, body: UpdateCommentSchema, db: AsyncSession = Depends(get_database)):
    try:
        comment_updated = await update_comment(comment_id, body, db)
        return comment_updated
    except Exception as err:
        logger.error(f"Failed to update comment {comment_id}: {err}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Failed to update comment")


@router.delete('/{comment_id:int}/{post_id:int}', response_model=ResponseCommentSchema)
async def delete_comment_view(comment_id: int, post_id: int, db: AsyncSession = Depends(get_database)):
    comment = await get_comment_by_post(post_id, comment_id, db)

    if not comment:
        logger.error(f"Comment with id {comment_id} not found for post {post_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Comment with id {comment_id} not found for post {post_id}")

    try:
        await delete_comment(comment_id, db)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        logger.error(f"Error deleting comment {comment_id} for post {post_id}: {e}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Failed to delete comment")


@router.get('/daily-breakdown')
async def comments_daily_breakdown_view(
        date_from: date = Query(...),
        date_to: date = Query(...),
        db: AsyncSession = Depends(get_database)
):
    if date_from > date_to:
        raise HTTPException(status_code=400, detail="date_from must be less than or equal to date_to")

    daily_data = await get_comments_daily_breakdown(date_from, date_to, db)

    if not daily_data:
        return {"message": f"No comments for this period {date_from} - {date_to}."}
    return daily_data
