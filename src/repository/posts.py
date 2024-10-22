from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Post
from src.schemas.post import CreatePostSchema, UpdatePostSchema
from src.entity.models import User


async def get_posts(limit: int, offset: int, db: AsyncSession, current_user: User):
    """
    :param limit: The maximum number of posts to retrieve.
    :param offset: The number of posts to skip before starting to retrieve.
    :param db: The database session used to execute the query.
    :param current_user: The user whose posts are to be retrieved.
    :return: A list of posts for the specified user within the given limit and offset.
    """

    stmt = select(Post).filter_by(user=current_user).limit(limit).offset(offset)
    posts = await db.execute(stmt)
    return posts.scalars().all()


async def get_post(post_id: int, db: AsyncSession, current_user: User):
    """
    :param post_id: The ID of the post to retrieve.
    :param db: The asynchronous database session used for querying the post.
    :param current_user: The user object representing the currently authenticated user.
    :return: The post object if found and if it belongs to the current user, otherwise None.
    """

    stmt = select(Post).filter_by(id=post_id, user=current_user)
    post = await db.execute(stmt)
    return post.scalar_one_or_none()


async def create_post(body: CreatePostSchema, db: AsyncSession, current_user: User):
    """
    :param body: The schema containing the data required to create a new post.
    :param db: The asynchronous session used to interact with the database.
    :param current_user: The user object representing the currently authenticated user.
    :return: The newly created Post object.
    """

    new_post = Post(**body.model_dump(exclude_unset=True))

    if await new_post.check_profanity():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Post contains forbidden words")

    new_post.user = current_user

    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    return new_post


async def update_post(post_id: int, body: UpdatePostSchema, db: AsyncSession, current_user: User):
    """
    :param post_id: The ID of the post to be updated.
    :param body: The new data for updating the post, encapsulated in an UpdatePostSchema object.
    :param db: The asynchronous database session to be used for executing queries and transactions.
    :param current_user: The current logged-in user attempting to update the post.
    :return: The updated post object.

    """

    stmt = select(Post).filter_by(id=post_id, user=current_user)
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} not found")

    post.title = body.title
    post.content = body.content

    if await post.check_profanity():
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Post contains forbidden words")

    await db.commit()
    await db.refresh(post)
    return post


async def delete_post(post_id: int, db: AsyncSession, current_user: User):
    """
    :param post_id: The unique identifier of the post to be deleted.
    :param db: The asynchronous database session used for executing queries.
    :param current_user: The user who is currently authenticated and attempting to delete the post.
    :return: The post that was deleted or None if no post was found.
    """

    stmt = select(Post).filter_by(id=post_id, user=current_user)
    post = await db.execute(stmt)
    post = post.scalar_one_or_none()
    if post:
        await db.delete(post)
        await db.commit()
    return post
