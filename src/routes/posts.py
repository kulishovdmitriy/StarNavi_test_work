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
    """
    :param limit: The number of posts to retrieve. Must be between 10 and 500.
    :param offset: The starting point within the collection of posts. Must be 0 or greater.
    :param db: The database session to use for querying posts.
    :param user: The current active user making the request.
    :return: A list of posts retrieved from the database.
    """

    posts = await get_posts(limit, offset, db, user)

    if not posts:
        logger.error("No posts found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No posts found")

    return posts


@router.get('/{post_id:int}', response_model=ResponsePostSchema)
async def get_post_view(post_id: int, db: AsyncSession = Depends(get_database),
                        user: User = Depends(current_active_user)):
    """
    :param post_id: The ID of the post to retrieve.
    :param db: Database session dependency.
    :param user: Currently authenticated active user.

    :return: The post details if found, otherwise raises a 404 HTTPException.
    """

    post = await get_post(post_id, db, user)

    if not post:
        logger.error(f"Post with id {post_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} not found")

    return post


@router.post('/create', response_model=ResponsePostSchema, status_code=status.HTTP_201_CREATED)
async def create_post_view(body: CreatePostSchema, db: AsyncSession = Depends(get_database),
                           user: User = Depends(current_active_user)):
    """
    :param body: The schema containing data for the post to be created. Expected to be of type CreatePostSchema.
    :param db: The asynchronous database session dependency, providing methods for database operations.
    :param user: The currently authenticated and active user making the request. Expected to be of type User.
    :return: A response model instance of type ResponsePostSchema representing the newly created post.
    """

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
    """
    :param post_id: The ID of the post to be updated
    :param body: The schema containing the updated data for the post
    :param db: The database session dependency
    :param user: The current active user dependency
    :return: The updated post
    """

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
    """
    :param post_id: The unique identifier of the post to be deleted
    :type post_id: int

    :param db: The database session to be used for deleting the post
    :type db: AsyncSession

    :param user: The currently authenticated user attempting to delete the post
    :type user: User

    :return: A response indicating the success or failure of the deletion action
    :rtype: ResponsePostSchema
    """

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
