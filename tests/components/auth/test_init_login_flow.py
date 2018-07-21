"""Tests for the login flow."""
from . import async_setup_auth

from tests.common import CLIENT_ID, CLIENT_REDIRECT_URI


async def test_fetch_auth_providers(hass, aiohttp_client):
    """Test fetching auth providers."""
    client = await async_setup_auth(hass, aiohttp_client)
    resp = await client.get('/auth/providers')
    assert await resp.json() == [{
        'name': 'Example',
        'type': 'insecure_example',
        'id': None
    }]


async def test_cannot_get_flows_in_progress(hass, aiohttp_client):
    """Test we cannot get flows in progress."""
    client = await async_setup_auth(hass, aiohttp_client, [])
    resp = await client.get('/auth/login_flow')
    assert resp.status == 405


async def test_invalid_username_password(hass, aiohttp_client):
    """Test we cannot get flows in progress."""
    client = await async_setup_auth(hass, aiohttp_client)
    resp = await client.post('/auth/login_flow', json={
        'client_id': CLIENT_ID,
        'handler': ['insecure_example', None],
        'redirect_uri': CLIENT_REDIRECT_URI
    })
    assert resp.status == 200
    step = await resp.json()

    # Incorrect username
    resp = await client.post(
        '/auth/login_flow/{}'.format(step['flow_id']), json={
            'client_id': CLIENT_ID,
            'username': 'wrong-user',
            'password': 'test-pass',
        })

    assert resp.status == 200
    step = await resp.json()

    assert step['step_id'] == 'init'
    assert step['errors']['base'] == 'invalid_auth'

    # Incorrect password
    resp = await client.post(
        '/auth/login_flow/{}'.format(step['flow_id']), json={
            'client_id': CLIENT_ID,
            'username': 'test-user',
            'password': 'wrong-pass',
        })

    assert resp.status == 200
    step = await resp.json()

    assert step['step_id'] == 'init'
    assert step['errors']['base'] == 'invalid_auth'
