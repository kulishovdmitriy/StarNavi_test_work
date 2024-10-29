import jwt
import pytest
from unittest.mock import Mock
from src.conf import messages
from tests.conftest import SECRET

from src.services.logger import setup_logger
from src.entity.models import Post


logger = setup_logger(__name__)


# def test_get_not_posts(client, get_token):
#     token = get_token
#     headers = {"Authorization": f"Bearer {token}"}
#     response = client.get('/api/v1/posts', headers=headers)
#
#     assert response.status_code == 404, response.text
#     data = response.json()
#     assert data['detail'] == messages.NO_POSTS_FOUND


def test_create_post(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post('/api/v1/posts/create', headers=headers, json={
        'title': 'test_title',
        'content': 'test_content',
        'completed': 'true'
    })

    assert response.status_code == 201, response.text
    data = response.json()
    assert 'id' in data
    assert data['title'] == 'test_title'
    assert data['content'] == 'test_content'
    assert data['completed'] == True

def test_get_posts(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get('/api/v1/posts', headers=headers)

    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == 1