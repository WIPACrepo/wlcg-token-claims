from unittest.mock import MagicMock
from wlcg_token_claims import group_validation


def test_get_all_groups(monkeypatch):
    groups = MagicMock()
    m = MagicMock(return_value=groups)
    monkeypatch.setattr(group_validation, 'getgrall', m)

    ret = group_validation.get_all_groups()
    assert ret == groups
    assert m.call_count == 1

    ret = group_validation.get_all_groups()
    assert ret == groups
    assert m.call_count == 1


def test_get_user_info(monkeypatch):
    user1 = MagicMock()
    m = MagicMock(return_value=user1)
    monkeypatch.setattr(group_validation, 'getpwnam', m)

    ret = group_validation.get_user_info('user1')
    assert ret == user1
    assert m.call_count == 1

    ret = group_validation.get_user_info('user1')
    assert ret == user1
    assert m.call_count == 1

    user2 = MagicMock()
    m.return_value = user2

    ret = group_validation.get_user_info('user2')
    assert ret == user2
    assert m.call_count == 2

def test_validator(storage):
    users, groups, tmp_path = storage
    v = group_validation.Validator(tmp_path)
    assert v(username='test1', scope='storage.read:/') == False
    assert v(username='test1', scope='storage.read:/data/user/test1') == True
    assert v(username='test1', scope='storage.modify:/data/user/test1') == True
    assert v(username='test1', scope='storage.read:/data/ana/project1') == True
    assert v(username='test1', scope='storage.modify:/data/ana/project1') == True
    assert v(username='test1', scope='storage.modify:/data/ana/project1/sub1') == True
    assert v(username='test1', scope='storage.read:/data/ana/project2') == True
    assert v(username='test1', scope='storage.modify:/data/ana/project2') == False
    assert v(username='test1', scope='storage.read:/data/ana/project2/sub1') == False
    assert v(username='test1', scope='storage.modify:/data/ana/project2/sub1') == False
    assert v(username='test1', scope='storage.read:/data/ana/project3') == True
    assert v(username='test1', scope='storage.modify:/data/ana/project3') == False
    assert v(username='test1', scope='storage.read:/data/ana/project3/sub1') == True
    assert v(username='test1', scope='storage.modify:/data/ana/project3/sub1') == True
    
    assert v(username='test2', scope='storage.read:/') == False
    assert v(username='test2', scope='storage.read:/data/user/test2') == True
    assert v(username='test2', scope='storage.modify:/data/user/test2') == True
    assert v(username='test2', scope='storage.read:/data/ana/project1') == True
    assert v(username='test2', scope='storage.modify:/data/ana/project1') == True
    assert v(username='test2', scope='storage.modify:/data/ana/project1/sub1') == False
    assert v(username='test2', scope='storage.read:/data/ana/project2') == True
    assert v(username='test2', scope='storage.modify:/data/ana/project2') == True
    assert v(username='test2', scope='storage.read:/data/ana/project2/sub1') == False
    assert v(username='test2', scope='storage.modify:/data/ana/project2/sub1') == False
    assert v(username='test2', scope='storage.read:/data/ana/project3') == True
    assert v(username='test2', scope='storage.modify:/data/ana/project3') == False
    assert v(username='test2', scope='storage.read:/data/ana/project3/sub1') == True
    assert v(username='test2', scope='storage.modify:/data/ana/project3/sub1') == False
