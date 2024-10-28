from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Post, User
from src.schemas.post import CreatePostSchema, UpdatePostSchema
from src.conf import messages


async def get_posts(limit: int, offset: int, db: AsyncSession, current_user: User):
    """
    Asynchronously retrieves a list of posts for the specified user, applying pagination with limit and offset.

    This function fetches a specified number of posts created by the current user, allowing for
    pagination through the use of a limit and an offset. It returns a list of posts that fall within
    the given parameters.

    :param limit: The maximum number of posts to retrieve.
    :param offset: The number of posts to skip before starting to retrieve.
    :param db: The asynchronous database session used to execute the query.
    :param current_user: The user whose posts are to be retrieved.

    :return: A list of posts for the specified user within the given limit and offset.
    """

    stmt = select(Post).filter_by(user=current_user).limit(limit).offset(offset)
    posts = await db.execute(stmt)
    return posts.scalars().all()


async def get_post(post_id: int, db: AsyncSession, current_user: User):
    """
    Asynchronously retrieves a specific post for the currently authenticated user.

    This function fetches a post by its ID, ensuring that it belongs to the currently authenticated user.
    If the post is found, it returns the post object; otherwise, it returns None.

    :param post_id: The ID of the post to retrieve.
    :param db: The asynchronous database session used for querying the post.
    :param current_user: The user object representing the currently authenticated user.

    :return: The post object if found and if it belongs to the current user; otherwise, returns None.
    """

    stmt = select(Post).filter_by(id=post_id, user=current_user)
    post = await db.execute(stmt)
    return post.scalar_one_or_none()


async def create_post(body: CreatePostSchema, db: AsyncSession, current_user: User):
    """
    Asynchronously creates a new post for the currently authenticated user.

    This function takes the provided post data, checks for profanity, and then saves the post
    to the database. If the post contains forbidden words, an HTTPException is raised.

    :param body: The schema containing the data required to create a new post.
    :param db: The asynchronous session used to interact with the database.
    :param current_user: The user object representing the currently authenticated user.

    :return: The newly created Post object if successful.
    :raises HTTPException: If the post contains forbidden words.
    """

    new_post = Post(**body.model_dump(exclude_unset=True))

    if await new_post.check_profanity():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=messages.POST_CONTAINS_FORBIDDEN_WORDS)

    new_post.user = current_user

    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    return new_post


async def update_post(post_id: int, body: UpdatePostSchema, db: AsyncSession, current_user: User):
    """
    Asynchronously updates an existing post with new data for the currently authenticated user.

    This function retrieves the specified post and updates its title and content
    if it belongs to the authenticated user. If the post contains forbidden words,
    an HTTPException is raised. If the post is not found, a 404 error is returned.

    :param post_id: The ID of the post to be updated.
    :param body: The new data for updating the post, encapsulated in an UpdatePostSchema object.
    :param db: The asynchronous database session to be used for executing queries and transactions.
    :param current_user: The current logged-in user attempting to update the post.

    :return: The updated post object if the update is successful.
    :raises HTTPException: If the post is not found or contains forbidden words.
    """

    stmt = select(Post).filter_by(id=post_id, user=current_user)
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.POST_NOT_FOUND.format(post_id=post_id))

    post.title = body.title
    post.content = body.content

    if await post.check_profanity():
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=messages.POST_CONTAINS_FORBIDDEN_WORDS)

    await db.commit()
    await db.refresh(post)
    return post


async def delete_post(post_id: int, db: AsyncSession, current_user: User):
    """
    Asynchronously deletes a post by its ID for the currently authenticated user.

    This function attempts to delete the specified post if it belongs to the authenticated user.
    If the post is not found, an HTTPException is raised.

    :param post_id: The ID of the post to be deleted.
    :param db: The asynchronous database session to be used for executing queries and transactions.
    :param current_user: The current logged-in user attempting to delete the post.

    :raises HTTPException: If the post is not found or does not belong to the current user.
    """

    stmt = select(Post).filter_by(id=post_id, user=current_user)
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.POST_NOT_FOUND.format(post_id=post_id))

    await db.delete(post)
    await db.commit()
    return post
