import pytest
from app import app

@pytest.fixture
def client():
    app.config.update({"TESTING": True})

    with app.test_client() as client:
        yield client

def test_homepage(client):
    response = client.get("/")
    assert response.status_code == 200

def test_setprivate(client):
    response = client.get("/setprivate/<item_id>")
    assert response.status_code == 200

@pytest.fixture
def user():
    client.post('/login', data=dict(username='marc1', password='password'))
    with app.test_client() as client:
        yield client


def test_index_page__not_logged_in(client):
    res = client.get('/')
    assert res.status_code == 401
    
def test_index_page__logged_in(client):
    client.post('/login', data=dict(username='marc1', password='password'))
    response = client.get('/')
    assert response.status_code == 200

#def test_item_posted(client, ):

def test_dummy():
    assert 1 == 1

pytest.main()