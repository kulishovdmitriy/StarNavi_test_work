from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.auth import current_active_user
from src.database.db import get_database
from src.entity.models import User
from src.repository.posts import get_posts, get_post, create_post, update_post, delete_post
from src.schemas.post import CreatePostSchema, UpdatePostSchema, ResponsePostSchema
from src.services.logger import setup_logger
from src.conf import messages


logger = setup_logger(__name__)

router = APIRouter(prefix='/posts', tags=['posts'])


@router.get('/', response_model=list[ResponsePostSchema])
async def get_posts_view(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                         db: AsyncSession = Depends(get_database), user: User = Depends(current_active_user)):
    """
    Get all posts for a specific post.
    """

    posts = await get_posts(limit, offset, db, user)

    if not posts:
        logger.error("No posts found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NO_POSTS_FOUND)

    return posts


@router.get('/{post_id:int}', response_model=ResponsePostSchema)
async def get_post_view(post_id: int, db: AsyncSession = Depends(get_database),
                        user: User = Depends(current_active_user)):
    """
    Get a specific post by ID.
    """

    post = await get_post(post_id, db, user)

    if not post:
        logger.error(f"Post with id {post_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.POST_NOT_FOUND.format(post_id=post_id))

    return post


@router.post('/create', response_model=ResponsePostSchema, status_code=status.HTTP_201_CREATED)
async def create_post_view(body: CreatePostSchema, db: AsyncSession = Depends(get_database),
                           user: User = Depends(current_active_user)):
    """
    Create a new post
    """

    if not body.title or not body.content:
        logger.error("Title and content are required")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=messages.TITLE_AND_CONTENT_REQUIRED)

    try:
        now_post = await create_post(body, db, user)
        return now_post

    except Exception as err:
        logger.error(f"Error creating post: {err}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=messages.FAILED_TO_CREATE_POST)


@router.put('/{post_id:int}', response_model=ResponsePostSchema, status_code=status.HTTP_202_ACCEPTED)
async def update_post_view(post_id: int, body: UpdatePostSchema, db: AsyncSession = Depends(get_database),
                           user: User = Depends(current_active_user)):
    """
    Update an existing post with the specified ID.
    """

    post = await get_post(post_id, db, user)

    if not post:
        logger.error(f"Post with id {post_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.POST_NOT_FOUND.format(post_id=post_id))

    if not body.title or not body.content:
        logger.error("Title and content are required")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=messages.TITLE_AND_CONTENT_REQUIRED)

    try:
        post_updated = await update_post(post_id, body, db, user)
        return post_updated

    except Exception as err:
        logger.error(f"Error updating post {post_id}: {err}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=messages.FAILED_TO_UPDATE_POST)


@router.delete('/{post_id:int}', response_model=ResponsePostSchema)
async def delete_post_view(post_id: int, db: AsyncSession = Depends(get_database),
                           user: User = Depends(current_active_user)):
    """
    Delete a post by its ID.
    """

    post = await get_post(post_id, db, user)

    if not post:
        logger.error(f"Post with id {post_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.POST_NOT_FOUND.format(post_id=post_id))

    try:
        await delete_post(post_id, db, user)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except Exception as err:
        logger.error(f"Error deleting post {post_id}: {err}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=messages.FAILED_TO_DELETE_POST)
