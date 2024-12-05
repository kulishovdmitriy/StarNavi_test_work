from src.conf import messages
from src.services.logger import setup_logger


logger = setup_logger(__name__)


def test_get_not_posts(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get('/api/v1/posts', headers=headers)

    assert response.status_code == 404, response.text
    data = response.json()
    assert data['detail'] == messages.NO_POSTS_FOUND


def test_get_not_post(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    post_id = 1
    response = client.get(f'/api/v1/posts/{post_id}', headers=headers)

    assert response.status_code == 404, response.text
    data = response.json()
    assert data['detail'] == messages.POST_NOT_FOUND.format(post_id=post_id)


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
    assert data['completed'] is True


def test_create_post_not_title_and_content(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post('/api/v1/posts/create', headers=headers, json={
        'title': '',
        'content': '',
        'completed': 'true'
    })

    assert response.status_code == 400, response.text
    data = response.json()
    assert data['detail'] == messages.TITLE_AND_CONTENT_REQUIRED


def test_get_posts(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get('/api/v1/posts', headers=headers)

    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == 1


def test_get_post(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    post_id = 1
    response = client.get(f'/api/v1/posts/{post_id}', headers=headers)

    assert response.status_code == 200, response.text
    data = response.json()
    assert data['id'] == 1


def test_update_post(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    post_id = 1
    response = client.put(f'/api/v1/posts/{post_id}', headers=headers, json={
        'title': 'test_title2',
        'content': 'test_content2',
        'completed': 'true'
    })

    assert response.status_code == 202, response.text
    data = response.json()
    assert 'id' in data
    assert data['title'] == 'test_title2'
    assert data['content'] == 'test_content2'
    assert data['completed'] is True


def test_get_update_not_post(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    post_id = 2
    response = client.get(f'/api/v1/posts/{post_id}', headers=headers)

    assert response.status_code == 404, response.text
    data = response.json()
    assert data['detail'] == messages.POST_NOT_FOUND.format(post_id=post_id)


def test_update_post_not_title_and_content(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    post_id = 1
    response = client.put(f'/api/v1/posts/{post_id}', headers=headers, json={
        'title': '',
        'content': '',
        'completed': 'true'
    })

    assert response.status_code == 400, response.text
    data = response.json()
    assert data['detail'] == messages.TITLE_AND_CONTENT_REQUIRED


def test_delete_post(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    post_id = 1
    response = client.delete(f'/api/v1/posts/{post_id}', headers=headers)

    assert response.status_code == 204
    assert response.content == b''


def test_delete_not_post(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    post_id = 1
    response = client.delete(f'/api/v1/posts/{post_id}', headers=headers)

    assert response.status_code == 404, response.text
    data = response.json()
    assert data['detail'] == messages.POST_NOT_FOUND.format(post_id=post_id)
