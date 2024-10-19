from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from src.servises.auth import current_active_user

from src.database.db import get_database
from src.entity.models import User
from src.repository.posts import get_posts, get_post, create_post, update_post, delete_post
from src.schemas.post import CreatePostSchema, UpdatePostSchema, ResponsePostSchema
from src.servises.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix='/posts', tags=['posts'])


@router.get('/', response_model=list[ResponsePostSchema])
async def get_posts_view(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                         db: AsyncSession = Depends(get_database), user: User = Depends(current_active_user)):

    posts = await get_posts(limit, offset, db, user)

    if not posts:
        logger.error("No posts found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No posts found")

    return posts


@router.get('/{post_id:int}', response_model=ResponsePostSchema)
async def get_post_view(post_id: int, db: AsyncSession = Depends(get_database),
                        user: User = Depends(current_active_user)):

    post = await get_post(post_id, db, user)

    if not post:
        logger.error(f"Post with id {post_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} not found")

    return post


@router.post('/create', response_model=ResponsePostSchema, status_code=status.HTTP_201_CREATED)
async def create_post_view(body: CreatePostSchema, db: AsyncSession = Depends(get_database),
                           user: User = Depends(current_active_user)):

    if not body.title or not body.content:
        logger.error("Title and content are required")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title and content are required")

    try:
        now_post = await create_post(body, db, user)
        return now_post

    except Exception as e:
        logger.error(f"Error creating post: {e}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Failed to create post")


@router.put('/{post_id:int}', response_model=ResponsePostSchema, status_code=status.HTTP_202_ACCEPTED)
async def update_post_view(post_id: int, body: UpdatePostSchema, db: AsyncSession = Depends(get_database),
                           user: User = Depends(current_active_user)):

    post = await get_post(post_id, db, user)

    if not post:
        logger.error(f"Post with id {post_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} not found")

    if not body.title or not body.content:
        logger.error("Title and content are required")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title and content are required")

    try:
        post_updated = await update_post(post_id, body, db)
        return post_updated

    except Exception as e:
        logger.error(f"Error updating post {post_id}: {e}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Failed to update post")


@router.delete('/{post_id:int}', response_model=ResponsePostSchema)
async def delete_post_view(post_id: int, db: AsyncSession = Depends(get_database),
                           user: User = Depends(current_active_user)):

    post = await get_post(post_id, db, user)

    if not post:
        logger.error(f"Post with id {post_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} not found")

    try:
        await delete_post(post_id, db)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        logger.error(f"Error deleting post {post_id}: {e}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Failed to delete post")
