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
from src.servises.auth import current_active_user
from src.servises.logger import setup_logger


logger = setup_logger(__name__)

router = APIRouter(prefix='/comments', tags=['comments'])


@router.get('/{post_id:int}', response_model=list[ResponseCommentSchema])
async def get_comments_view(post_id: int, db: AsyncSession = Depends(get_database),
                            user: User = Depends(current_active_user)):
    """
    Retrieve comments for a specified post.

    This endpoint fetches a list of comments associated with the given post ID.
    It requires the user to be authenticated to ensure that only valid users can
    access the comments.

    :param post_id: ID of the post for which comments are being retrieved.
    :param db: Database session dependency for executing queries.
    :param user: Currently authenticated user dependency for user context.
    :return: A list of comments for the specified post.
    """

    comments = await get_comments(post_id, db, user)

    if not comments:
        logger.error(f"No comments found for post with id {post_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No comments found for post with id {post_id}")
    return comments


@router.get('/posts/{post_id}/comments/{comment_id}', response_model=ResponseCommentSchema)
async def get_comment_view(post_id: int, comment_id: int, db: AsyncSession = Depends(get_database),
                           user: User = Depends(current_active_user)):
    """
    Retrieve a specific comment for a given post.

    This endpoint fetches a single comment based on the provided post ID and
    comment ID. It requires the user to be authenticated to ensure access control
    for retrieving comments.

    :param post_id: The ID of the post to which the comment belongs.
    :param comment_id: The ID of the comment to retrieve.
    :param db: Database session dependency for executing queries.
    :param user: Currently authenticated user for authorization context.
    :return: The comment corresponding to the provided post ID and comment ID.
    """

    comment = await get_comment_by_post(post_id, comment_id, db, user)

    if not comment:
        logger.error(f"No comment found with id {comment_id} for post with id {post_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No comment found with id {comment_id} for post with id {post_id}")
    return comment


@router.post('/create', response_model=ResponseCommentSchema, status_code=status.HTTP_201_CREATED)
async def create_comment_view(post_id: int, body: CreateCommentSchema, db: AsyncSession = Depends(get_database),
                              user: User = Depends(current_active_user)):
    """
    Create a new comment for a specified post.

    This endpoint allows an authenticated user to create a new comment associated
    with a particular post. The request must include the post ID and the details
    of the comment in the request body.

    :param post_id: The ID of the post to which the comment is being added.
    :param body: The schema containing the details of the comment to be created.
    :param db: The database session dependency used for database operations.
    :param user: The currently authenticated user creating the comment.
    :return: The created comment object.
    """

    try:
        new_comment = await create_comment(post_id, body, db, user)
        return new_comment
    except Exception as e:
        logger.error(f"Failed to create comment for post {post_id}: {e}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Failed to create comment")


@router.put('/{comment_id:int}', response_model=ResponseCommentSchema, status_code=status.HTTP_202_ACCEPTED)
async def update_comment_view(comment_id: int, body: UpdateCommentSchema, db: AsyncSession = Depends(get_database),
                              user: User = Depends(current_active_user)):
    """
    Update an existing comment.

    This endpoint allows an authenticated user to update the content of a
    specific comment. The request must include the comment ID and the updated
    fields of the comment in the request body. If the comment is successfully
    updated, the updated comment object will be returned.

    :param comment_id: The ID of the comment to be updated.
    :param body: The schema containing the updated comment fields.
    :param db: Database session dependency to interact with the database.
    :param user: The current active user making the request.
    :return: The updated comment if successful, or raises an HTTP 422 exception otherwise.
    """

    try:
        comment_updated = await update_comment(comment_id, body, db, user)
        return comment_updated
    except Exception as err:
        logger.error(f"Failed to update comment {comment_id}: {err}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Failed to update comment")


@router.delete('/{comment_id:int}/{post_id:int}', response_model=ResponseCommentSchema)
async def delete_comment_view(comment_id: int, post_id: int, db: AsyncSession = Depends(get_database),
                              user: User = Depends(current_active_user)):
    """
    Delete a specific comment associated with a post.

    This endpoint allows an authenticated user to delete a comment from a post
    using the comment ID and the post ID. If the comment is successfully deleted,
    the deleted comment object will be returned. If the comment does not exist
    or the user is not authorized to delete it, an appropriate error response will be provided.

    :param comment_id: Unique identifier of the comment to be deleted.
    :param post_id: Unique identifier of the post to which the comment belongs.
    :param db: Asynchronous session dependency for database operations.
    :param user: Currently authenticated user fetched using dependency injection.
    :return: HTTP response indicating the success or failure of the delete operation.
    """

    comment = await get_comment_by_post(post_id, comment_id, db, user)

    if not comment:
        logger.error(f"Comment with id {comment_id} not found for post {post_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Comment with id {comment_id} not found for post {post_id}")

    try:
        await delete_comment(comment_id, db, user)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        logger.error(f"Error deleting comment {comment_id} for post {post_id}: {e}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Failed to delete comment")


@router.get('/daily-breakdown')
async def comments_daily_breakdown_view(date_from: date = Query(...), date_to: date = Query(...),
                                        db: AsyncSession = Depends(get_database)):
    """
    Retrieve a daily breakdown of comments within a specified date range.

    This endpoint returns the total number of comments and blocked comments for each
    day within the specified date range. The user must provide both the start and
    end dates. The data can be used for analysis of comment activity over time.

    :param date_from: Start date for the period to fetch daily comments breakdown.
    :param date_to: End date for the period to fetch daily comments breakdown.
    :param db: The database session dependency.
    :return: Daily breakdown of comments for the specified period.
    """

    if date_from > date_to:
        raise HTTPException(status_code=400, detail="date_from must be less than or equal to date_to")

    daily_data = await get_comments_daily_breakdown(date_from, date_to, db)

    if not daily_data:
        return {"message": f"No comments for this period {date_from} - {date_to}."}
    return daily_data
