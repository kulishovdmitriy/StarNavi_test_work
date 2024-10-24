import unittest
from unittest.mock import MagicMock, AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from src.entity.models import Post, User
from src.schemas.post import CreatePostSchema, UpdatePostSchema
from src.repository.posts import get_posts, get_post, create_post, update_post, delete_post


class TestAsyncPosts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.user = User(id=1, username="test_user")
        self.session = AsyncMock(spec=AsyncSession)

    async def test_get_posts(self):
        limit = 10
        offset = 0
        posts = [
            Post(id=1, title='test_1', content='content_test_1', user=self.user),
            Post(id=2, title='test_2', content='content_test_2', user=self.user)
        ]
        mocked_posts = MagicMock()
        mocked_posts.scalars().all.return_value = posts
        self.session.execute.return_value = mocked_posts

        result = await get_posts(limit, offset, self.session, self.user)

        self.assertEqual(result, posts)
        self.session.execute.assert_called_once()

    async def test_get_post(self):
        post_id = 1
        post = Post(id=post_id, user=self.user)

        mocked_result = MagicMock()
        mocked_result.scalar_one_or_none.return_value = post
        self.session.execute.return_value = mocked_result

        result = await get_post(post_id, self.session, self.user)

        self.assertEqual(result, post)
        self.session.execute.assert_called_once()

    async def test_create_post(self):
        body = CreatePostSchema(title='test_title', content='test_content')

        with patch.object(Post, 'check_profanity', return_value=False):

            result = await create_post(body, self.session, self.user)

            self.assertIsInstance(result, Post)
            self.assertEqual(result.title, body.title)
            self.assertEqual(result.content, body.content)
            self.assertEqual(result.user, self.user)
            self.session.add.assert_called_once()
            self.session.commit.assert_called_once()
            self.session.refresh.assert_called_once_with(result)

    async def test_create_post_with_profanity(self):
        body = CreatePostSchema(title='test_title', content='forbidden_content')

        with patch.object(Post, 'check_profanity', return_value=True):
            with self.assertRaises(HTTPException) as context:
                await create_post(body, self.session, self.user)

            self.assertEqual(context.exception.status_code, 400)
            self.assertEqual(context.exception.detail, "Post contains forbidden words")
            self.session.add.assert_not_called()
            self.session.commit.assert_not_called()
            self.session.refresh.assert_not_called()

    async def test_update_post(self):
        post_id = 1
        body = UpdatePostSchema(title='test_title', content='test_content', completed=True)
        post = Post(id=post_id, user=self.user, title='old_title', content='old_content')

        mocked_result = MagicMock()
        mocked_result.scalar_one_or_none.return_value = post
        self.session.execute.return_value = mocked_result

        with patch.object(post, 'check_profanity', return_value=False):
            result = await update_post(post_id, body, self.session, self.user)

            self.assertEqual(result, post)
            self.assertEqual(result.title, body.title)
            self.assertEqual(result.content, body.content)
            self.session.commit.assert_called_once()
            self.session.refresh.assert_called_once_with(post)

    async def test_update_post_not_found(self):
        post_id = 2
        body = UpdatePostSchema(title='test_title', content='test_content', completed=True)

        mocked_result = MagicMock()
        mocked_result.scalar_one_or_none.return_value = None
        self.session.execute.return_value = mocked_result

        with self.assertRaises(HTTPException) as context:
            await update_post(post_id, body, self.session, self.user)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, f"Post with id {post_id} not found")
        self.session.commit.assert_not_called()
        self.session.refresh.assert_not_called()

    async def test_update_post_with_profanity(self):
        post_id = 1
        body = UpdatePostSchema(title='test_title', content='forbidden_content', completed=True)
        post = Post(id=post_id, user=self.user)

        mocked_result = MagicMock()
        mocked_result.scalar_one_or_none.return_value = post
        self.session.execute.return_value = mocked_result

        with patch.object(post, 'check_profanity', return_value=True):
            with self.assertRaises(HTTPException) as context:
                await update_post(post_id, body, self.session, self.user)

            self.assertEqual(context.exception.status_code, 400)
            self.assertEqual(context.exception.detail, "Post contains forbidden words")
            self.session.rollback.assert_called_once()
            self.session.commit.assert_not_called()
            self.session.refresh.assert_not_called()

    async def test_delete_post(self):
        post_id = 1
        post = Post(id=post_id, user=self.user)
        mocked_result = MagicMock()
        mocked_result.scalar_one_or_none.return_value = post
        self.session.execute.return_value = mocked_result

        result = await delete_post(post_id, self.session, self.user)

        self.assertEqual(result, post)
        self.session.delete.assert_called_once_with(post)
        self.session.commit.assert_called_once()

    async def test_delete_post_not_found(self):
        post_id = 1
        mocked_result = MagicMock()
        mocked_result.scalar_one_or_none.return_value = None
        self.session.execute.return_value = mocked_result

        with self.assertRaises(HTTPException) as context:
            await delete_post(post_id, self.session, self.user)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, f"Post with id {post_id} not found")
        self.session.delete.assert_not_called()
