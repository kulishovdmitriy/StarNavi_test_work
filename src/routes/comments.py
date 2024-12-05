from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_database
from src.entity.models import User
from src.repository.comments import (
    get_comments,
    create_comment,
    update_comment,
    delete_comment,
    get_comment_by_post,
    get_comments_daily_breakdown
)
from src.schemas.comment import CreateCommentSchema, UpdateCommentSchema, ResponseCommentSchema
from src.services.auth import current_active_user
from src.services.logger import setup_logger
from src.conf import messages


logger = setup_logger(__name__)

router = APIRouter(prefix='/comments', tags=['comments'])


@router.get('/{post_id:int}', response_model=list[ResponseCommentSchema])
async def get_comments_view(post_id: int, db: AsyncSession = Depends(get_database),
                            user: User = Depends(current_active_user)):
    """
    Get all comments for a specific post.
    """

    comments = await get_comments(post_id, db, user)

    if not comments:
        logger.error(f"No comments found for post with id {post_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=messages.NO_COMMENTS_FOUND.format(post_id=post_id))
    return comments


@router.get('/{post_id}/comments/{comment_id}', response_model=ResponseCommentSchema)
async def get_comment_view(post_id: int, comment_id: int, db: AsyncSession = Depends(get_database),
                           user: User = Depends(current_active_user)):
    """
    Get a specific comment by ID for a post.
    """

    comment = await get_comment_by_post(post_id, comment_id, db, user)

    if not comment:
        logger.error(f"No comment found with id {comment_id} for post with id {post_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=messages.NO_COMMENT_FOUND_FOR_POST.format(comment_id=comment_id, post_id=post_id))
    return comment


@router.post('/{post_id}', response_model=ResponseCommentSchema, status_code=status.HTTP_201_CREATED)
async def create_comment_view(post_id: int, body: CreateCommentSchema, db: AsyncSession = Depends(get_database),
                              user: User = Depends(current_active_user)):
    """
    Create a new comment for a post.
    """

    try:
        new_comment = await create_comment(post_id, body, db, user)
        return new_comment
    except Exception as err:
        logger.error(f"Failed to create comment for post {post_id}: {err}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=messages.FAILED_TO_CREATE_COMMENT)


@router.put('/{comment_id:int}', response_model=ResponseCommentSchema, status_code=status.HTTP_202_ACCEPTED)
async def update_comment_view(comment_id: int, body: UpdateCommentSchema, db: AsyncSession = Depends(get_database),
                              user: User = Depends(current_active_user)):
    """
    Update an existing comment for a post.
    """

    try:
        comment_updated = await update_comment(comment_id, body, db, user)
        return comment_updated
    except Exception as err:
        logger.error(f"Failed to update comment {comment_id}: {err}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=messages.FAILED_TO_UPDATE_COMMENT)


@router.delete('/{comment_id:int}/{post_id:int}', response_model=ResponseCommentSchema)
async def delete_comment_view(comment_id: int, post_id: int, db: AsyncSession = Depends(get_database),
                              user: User = Depends(current_active_user)):
    """
    Delete a specific comment from a post.
    """

    comment = await get_comment_by_post(post_id, comment_id, db, user)

    if not comment:
        logger.error(f"Comment with id {comment_id} not found for post {post_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=messages.COMMENT_NOT_FOUND_FOR_POST.format(comment_id=comment_id, post_id=post_id))

    try:
        await delete_comment(comment_id, db, user)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as err:
        logger.error(f"Error deleting comment {comment_id} for post {post_id}: {err}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=messages.FAILED_TO_DELETE_COMMENT)


@router.get('/daily-breakdown')
async def comments_daily_breakdown_view(date_from: date = Query(...), date_to: date = Query(...),
                                        db: AsyncSession = Depends(get_database)):
    """
    Get daily breakdown of comments within a date range.
    """

    if date_from > date_to:
        raise HTTPException(status_code=400, detail=messages.DATE_FROM_MUST_BE_LESS_OR_EQUAL_DATE_TO)

    daily_data = await get_comments_daily_breakdown(date_from, date_to, db)

    if not daily_data:
        return {"message": messages.NO_COMMENTS_FOR_PERIOD.format(date_from=date_from, date_to=date_to)}

    return daily_data
