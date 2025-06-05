import socket
from unittest.mock import patch, Mock

import pytest
import pytest_asyncio
from rest_tools.client import RestClient

import wlcg_token_claims.config
import wlcg_token_claims.server
from wlcg_token_claims.server import Server

@pytest.fixture
def port():
    """Get an ephemeral port number."""
    # https://unix.stackexchange.com/a/132524
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    addr = s.getsockname()
    ephemeral_port = addr[1]
    s.close()
    return ephemeral_port


@pytest_asyncio.fixture
async def server(monkeypatch, port, storage):
    users, groups, tmp_path = storage
    mock = Mock(spec=wlcg_token_claims.server.ENV)
    with patch('wlcg_token_claims.server.ENV', return_value=mock) as env:
        env.BASE_PATH = tmp_path
        env.HOST = 'localhost'
        env.PORT = int(port)
        env.DEBUG = True
        env.AUTH_SECRET = 'secret'
        env.USE_LDAP = False

        s = Server()
        await s.start()
        yield f'http://localhost:{port}'
        await s.stop()

async def test_main(server):
    client = RestClient(server, retries=0)

    ret = await client.request('GET', '/')
    assert ret == {}

async def test_auth(server, storage):
    users, groups, tmp_path = storage
    client = RestClient(server, token='secret', retries=0)

    with pytest.raises(Exception):
        await client.request('GET', '/auth')
    
    ret = await client.request('POST', '/auth', {'username': 'test1', 'scopes': 'storage.read:/'})
    assert ret == {'scopes': ''}
    
    ret = await client.request('POST', '/auth', {'username': 'test1', 'scopes': 'storage.read:/data/user/test1'})
    assert ret == {'scopes': 'storage.read:/data/user/test1'}

async def test_auth_invalid(server):
    client = RestClient(server, retries=0)
    with pytest.raises(Exception):
        await client.request('POST', '/auth', {})
