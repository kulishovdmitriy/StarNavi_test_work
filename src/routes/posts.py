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
    Retrieve a list of posts for the currently authenticated user.

    This endpoint allows the user to fetch a specified number of posts, with support for pagination
    through the `limit` and `offset` parameters. The `limit` parameter defines how many posts to return,
    while `offset` specifies the starting point for the retrieval.

    :param limit: The number of posts to retrieve. Must be between 10 and 500.
    :param offset: The starting point within the collection of posts. Must be 0 or greater.
    :param db: The database session to use for querying posts.
    :param user: The current active user making the request.
    :return: A list of posts retrieved from the database.
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
    Retrieve the details of a specific post by its ID.

    This endpoint allows the user to fetch the details of a single post. If the post exists
    and belongs to the currently authenticated user, it returns the post's details.
    If the post is not found or does not belong to the user, a 404 HTTPException is raised.

    :param post_id: The ID of the post to retrieve.
    :param db: Database session dependency to interact with the database.
    :param user: Currently authenticated active user making the request.

    :return: The post details if found; raises a 404 HTTPException otherwise.
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
    Create a new post with the provided data.

    This endpoint allows an authenticated user to create a new post. The post's details must
    be provided in the request body using the CreatePostSchema. Upon successful creation,
    it returns the newly created post as a ResponsePostSchema instance with a 201 status code.

    :param body: The schema containing data for the post to be created. Expected to be of type CreatePostSchema.
    :param db: The asynchronous database session dependency, providing methods for database operations.
    :param user: The currently authenticated and active user making the request. Expected to be of type User.

    :return: A response model instance of type ResponsePostSchema representing the newly created post.
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


@router.put('/update/{post_id:int}', response_model=ResponsePostSchema, status_code=status.HTTP_202_ACCEPTED)
async def update_post_view(post_id: int, body: UpdatePostSchema, db: AsyncSession = Depends(get_database),
                           user: User = Depends(current_active_user)):
    """
    Update an existing post with the specified ID.

    This endpoint allows an authenticated user to update the details of a post. The updated data
    must be provided in the request body using the UpdatePostSchema. Upon successful update,
    it returns the updated post as a ResponsePostSchema instance with a 202 status code.

    :param post_id: The ID of the post to be updated.
    :param body: The schema containing the updated data for the post. Expected to be of type UpdatePostSchema.
    :param db: The asynchronous database session dependency, providing methods for database operations.
    :param user: The currently authenticated and active user making the request. Expected to be of type User.

    :return: A response model instance of type ResponsePostSchema representing the updated post.
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


@router.delete('/delete/{post_id:int}', response_model=ResponsePostSchema)
async def delete_post_view(post_id: int, db: AsyncSession = Depends(get_database),
                           user: User = Depends(current_active_user)):
    """
    Delete a post by its ID.

    This endpoint allows an authenticated user to delete a post identified by the given post_id.
    If the post exists and is successfully deleted, a response with HTTP 204 No Content is returned.
    If the post does not exist, a 404 error is raised. In case of any failure during deletion,
    a 422 error is returned.

    :param post_id: The unique identifier of the post to be deleted.
    :type post_id: int

    :param db: The database session to be used for deleting the post.
    :type db: AsyncSession

    :param user: The currently authenticated user attempting to delete the post.
    :type user: User

    :return: A response indicating the success or failure of the deletion action.
    :rtype: ResponsePostSchema
    """

    post = await get_post(post_id, db, user)

    if not post:
        logger.error(f"Post with id {post_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.POST_NOT_FOUND.format(post_id=post_id))

    try:
        await delete_post(post_id, db, user)
        logger.info(
            f"Post with id {post_id} deleted successfully by user {user.username} ({user.email})"
        )

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except Exception as err:
        logger.error(f"Error deleting post {post_id}: {err}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=messages.FAILED_TO_DELETE_POST)
