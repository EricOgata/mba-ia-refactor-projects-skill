"""Testes de integração dos contratos HTTP da API."""

import hashlib

import pytest

from app import create_app
from config.settings import TestConfig
from database import db
from models.user import User


@pytest.fixture
def client():
    application = create_app(TestConfig)
    with application.app_context():
        db.create_all()
        yield application.test_client()
        db.session.remove()
        db.drop_all()


def create_user(client, **overrides):
    payload = {
        'name': 'Ana',
        'email': 'ana@example.com',
        'password': 'secret123',
        **overrides,
    }
    return client.post('/users', json=payload)


def create_category(client, **overrides):
    payload = {'name': 'Backend', 'color': '#3498db', **overrides}
    return client.post('/categories', json=payload)


def test_health_and_index(client):
    assert client.get('/health').status_code == 200
    body = client.get('/').get_json()
    assert body['message'] == 'Task Manager API'


def test_users_crud_and_no_password_leak(client):
    response = create_user(client)
    assert response.status_code == 201
    user = response.get_json()
    assert 'password' not in user
    user_id = user['id']

    assert client.get('/users').get_json()[0]['task_count'] == 0
    assert client.get(f'/users/{user_id}').status_code == 200

    updated = client.put(f'/users/{user_id}', json={'name': 'Ana Maria'})
    assert updated.status_code == 200
    assert updated.get_json()['name'] == 'Ana Maria'

    duplicate = create_user(client)
    assert duplicate.status_code == 409
    assert client.get(f'/users/{user_id}/tasks').get_json() == []

    assert client.delete(f'/users/{user_id}').status_code == 200
    assert client.get(f'/users/{user_id}').status_code == 404


def test_login_returns_jwt(client):
    create_user(client)
    response = client.post('/login', json={'email': 'ana@example.com', 'password': 'secret123'})
    assert response.status_code == 200
    body = response.get_json()
    assert body['token'].count('.') == 2
    assert 'password' not in body['user']

    assert client.post('/login', json={'email': 'ana@example.com', 'password': 'wrong'}).status_code == 401


def test_tasks_flow_and_relations(client):
    user_id = create_user(client).get_json()['id']
    category_id = create_category(client).get_json()['id']

    created = client.post('/tasks', json={
        'title': 'Escrever testes',
        'description': 'Cobrir endpoints',
        'priority': 1,
        'user_id': user_id,
        'category_id': category_id,
        'due_date': '2020-01-01',
        'tags': ['qa', 'backend'],
    })
    assert created.status_code == 201
    task = created.get_json()
    task_id = task['id']
    assert task['tags'] == ['qa', 'backend']

    listed = client.get('/tasks').get_json()
    assert listed[0]['user_name'] == 'Ana'
    assert listed[0]['category_name'] == 'Backend'
    assert listed[0]['overdue'] is True

    assert client.get(f'/tasks/{task_id}').status_code == 200
    assert client.get('/tasks/search?q=testes').get_json()[0]['id'] == task_id
    assert client.get('/tasks/stats').get_json()['overdue'] == 1

    updated = client.put(f'/tasks/{task_id}', json={'status': 'done', 'due_date': None})
    assert updated.status_code == 200
    assert updated.get_json()['status'] == 'done'

    assert client.delete(f'/tasks/{task_id}').status_code == 200
    assert client.get(f'/tasks/{task_id}').status_code == 404


def test_categories_and_reports(client):
    user_id = create_user(client).get_json()['id']
    category_id = create_category(client).get_json()['id']
    client.post('/tasks', json={'title': 'Task A', 'user_id': user_id, 'category_id': category_id})

    categories = client.get('/categories').get_json()
    assert categories[0]['task_count'] == 1

    assert client.put(f'/categories/{category_id}', json={'name': 'API'}).status_code == 200
    assert client.delete(f'/categories/{category_id}').status_code == 200

    summary = client.get('/reports/summary')
    assert summary.status_code == 200
    body = summary.get_json()
    assert body['overview']['total_tasks'] == 1
    assert body['user_productivity'][0]['total_tasks'] == 1
    assert body['tasks_by_priority']['critical'] == 0

    assert client.get(f'/reports/user/{user_id}').status_code == 200


def test_invalid_payloads_return_400(client):
    assert client.post('/tasks', json={}).status_code == 400
    assert client.post('/tasks', json={'title': 'ab'}).status_code == 400
    assert client.post('/tasks', json={'title': 'Titulo', 'priority': 9}).status_code == 400
    assert client.post('/tasks', json={'title': 'Titulo', 'due_date': 'not-a-date'}).status_code == 400
    assert client.post('/users', json={'name': 'Ana', 'email': 'bad', 'password': 'x'}).status_code == 400
    assert client.post('/categories', json={}).status_code == 400
    assert client.post('/tasks', data='not json', content_type='text/plain').status_code == 400

    category = create_category(client).get_json()
    assert client.put(f"/categories/{category['id']}", json=None).status_code == 400


def test_auth_guard_blocks_writes_when_enabled():
    class AuthConfig(TestConfig):
        AUTH_REQUIRED = True

    application = create_app(AuthConfig)
    with application.app_context():
        db.create_all()
        client = application.test_client()

        assert client.post('/tasks', json={'title': 'Sem token'}).status_code == 401

        user = User(name='Ana', email='ana@example.com', role='user')
        user.set_password('secret123')
        db.session.add(user)
        db.session.commit()

        token = client.post('/login', json={
            'email': 'ana@example.com',
            'password': 'secret123',
        }).get_json()['token']

        allowed = client.post(
            '/tasks',
            json={'title': 'Com token'},
            headers={'Authorization': f'Bearer {token}'},
        )
        assert allowed.status_code == 201

        db.session.remove()
        db.drop_all()


def test_legacy_md5_password_is_rehashed_on_login():
    application = create_app(TestConfig)
    with application.app_context():
        db.create_all()
        legacy = User(name='Legacy', email='legacy@example.com', role='user')
        legacy.password = hashlib.md5(b'oldpass').hexdigest()
        db.session.add(legacy)
        db.session.commit()

        client = application.test_client()
        assert client.post('/login', json={
            'email': 'legacy@example.com',
            'password': 'oldpass',
        }).status_code == 200

        stored = User.query.filter_by(email='legacy@example.com').first().password
        assert not User._is_legacy_md5(stored)

        db.session.remove()
        db.drop_all()
