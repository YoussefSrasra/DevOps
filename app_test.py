import pytest
from app import app, saved_links, generate_link_id

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_homepage(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"shorten_link" in response.data

def test_link_shortening_and_redirect(client):
    # Simulate creating a shortened link
    url = "https://example.com"
    response = client.get('/', query_string={"url": url})
    assert response.status_code == 200
    # Extract the link_id from the response
    link_id = None
    for k, v in saved_links.items():
        if v == url:
            link_id = k
            break
    assert link_id is not None
    # Test redirection
    redirect_response = client.get(f'/{link_id}')
    assert redirect_response.status_code == 302
    assert redirect_response.location == url
