import logging
from os import stat as os_stat, stat_result
from pathlib import Path

import pytest
from unittest.mock import Mock, MagicMock, patch
from wlcg_token_claims import group_validation


def _mkuser(uid, gid):
    ret = Mock(spec=['pw_uid', 'pw_gid'])
    ret.pw_uid = uid
    ret.pw_gid = gid
    return ret


def _mkgroup(gid, members):
    ret = Mock(spec=['gr_gid', 'gr_mem'])
    ret.gr_gid = gid
    ret.gr_mem = members
    return ret

def _mock_perms(uid, gid, mode):
    ret = Mock(spec=stat_result)
    ret.st_uid = uid
    ret.st_gid = gid
    ret.st_mode = mode
    return ret

@pytest.fixture
def storage(tmp_path, monkeypatch):
    groups = [
        _mkgroup(12350, ['test1', 'test2']),
        _mkgroup(12351, ['test1']),
        _mkgroup(12352, ['test2']),
        _mkgroup(12353, []),
    ]
    monkeypatch.setattr(group_validation, 'get_all_groups', MagicMock(return_value=groups))

    users = {
        'non': {'uid': 12300, 'gid': 12300},
        'test1': {'uid': 12345, 'gid': 12345},
        'test2': {'uid': 12346, 'gid': 12347},
    }
    def get_user(username):
        return _mkuser(**users[username])
    monkeypatch.setattr(group_validation, 'get_user_info', get_user)

    def fake_stat(path, *args, **kwargs):
        if Path(path).is_relative_to(tmp_path):
            rpath = str(path)[len(str(tmp_path)):]
            logging.debug(f'mocking! "{rpath}"')
            if rpath.startswith('/data/user/'):
                user = users[rpath.split('/')[-1]]
                return _mock_perms(user['uid'], user['gid'], 0o775)
            elif rpath.startswith('/data/ana'):
                if rpath.startswith('/data/ana/project1/sub1'):
                    return _mock_perms(1, 12351, 0o775)
                elif rpath.startswith('/data/ana/project1'):
                    return _mock_perms(1, 12350, 0o775)
                elif rpath.startswith('/data/ana/project2/sub1'):
                    return _mock_perms(1, 12353, 0o770)
                elif rpath.startswith('/data/ana/project2'):
                    return _mock_perms(1, 12352, 0o775)
                elif rpath.startswith('/data/ana/project3/sub1'):
                    return _mock_perms(1, 12345, 0o775)
                elif rpath.startswith('/data/ana/project3'):
                    return _mock_perms(1, 12353, 0o775)
            return _mock_perms(1, 1, 0o700)
        else:
            return os_stat(path, *args, **kwargs)

    data_user = tmp_path / 'data' / 'user'
    data_user.mkdir(parents=True)
    for username in users:
        p = data_user / username
        p.mkdir()
        p.chmod(0o755)

    data_ana = tmp_path / 'data' / 'ana'
    data_ana.mkdir(parents=True)
    data_ana.chmod(0o755)

    p = data_ana / 'project1'
    p2 = data_ana / 'project1' / 'sub1'
    p2.mkdir(parents=True)
    p.chmod(0o775)
    p2.chmod(0o775)
    #chown(str(p2), -1, 12351)
    #chown(str(p), -1, 12350)

    p = data_ana / 'project2'
    p2 = data_ana / 'project2' / 'sub1'
    p2.mkdir(parents=True)
    p.chmod(0o775)
    p2.chmod(0o775)
    #chown(str(p2), -1, 12353)
    #chown(str(p), -1, 12352)

    p = data_ana / 'project3'
    p2 = data_ana / 'project3' / 'sub1'
    p2.mkdir(parents=True)
    p.chmod(0o775)
    p2.chmod(0o775)
    #chown(str(p2), -1, 12345)
    #chown(str(p), -1, 12353)

    with patch('os.stat') as mock_stat:
        mock_stat.side_effect = fake_stat
        yield (users, groups, tmp_path)
