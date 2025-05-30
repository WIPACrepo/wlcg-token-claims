from grp import getgrall, struct_group
import logging
from pathlib import Path
from pwd import getpwnam, struct_passwd
import os
import stat

import cachetools.func


@cachetools.func.ttl_cache(ttl=60)
def get_all_groups() -> list[struct_group]:
    return getgrall()


@cachetools.func.ttl_cache(maxsize=1000, ttl=60)
def get_user_info(username) -> struct_passwd:
    return getpwnam(username)


@cachetools.func.ttl_cache(maxsize=100000, ttl=60)
def get_stat(path: Path) -> os.stat_result:
    return os.stat(str(path))


class Validator:
    def __init__(self, base_path: str):
        self._base_path = Path(base_path if base_path else '/')

    def __call__(self, username='', scope='') -> bool:
        if username and scope and scope.startswith('storage.') and ':' in scope:
            perm, scope_path = scope.split('.', 1)[-1].split(':', 1)
            path = (self._base_path / scope_path.lstrip('/')).resolve()
            if not path.is_relative_to(self._base_path):
                logging.debug('path is not relative to base: %s', scope_path)
                return False
            while not path.exists():
                path = path.parent
            logging.debug('checking perms for user %s, perm %s, on path %s', username, perm, path)

            if perm in ('read', 'stage', 'create', 'modify'):
                groups = self.get_user_groups(username)
                logging.debug('groups: %r', groups)
                path_stat = get_stat(path)
                logging.debug('stat: uid:%d gid:%d', path_stat.st_uid, path_stat.st_gid)
                if path_stat.st_uid == get_user_info(username).pw_uid:
                    logging.debug('match username')
                    if perm in ('read', 'stage'):
                        return bool(path_stat.st_mode & stat.S_IRUSR)
                    elif perm in ('create', 'modify'):
                        return bool(path_stat.st_mode & stat.S_IWUSR)
                elif path_stat.st_gid in groups:
                    logging.debug('match groups')
                    if perm in ('read', 'stage'):
                        return bool(path_stat.st_mode & stat.S_IRGRP)
                    elif perm in ('create', 'modify'):
                        return bool(path_stat.st_mode & stat.S_IWGRP)
                elif perm in ('read', 'stage'):
                    return bool(path_stat.st_mode & stat.S_IROTH)
                elif perm in ('create', 'modify'):
                    return bool(path_stat.st_mode & stat.S_IWOTH)

        return False

    def get_user_groups(self, username: str) -> list[int]:
        """Gets all group ids for a given username."""
        groups = [g.gr_gid for g in get_all_groups() if username in g.gr_mem]
        # Add the user's primary group
        try:
            groups.append(get_user_info(username).pw_gid)
        except KeyError:
            logging.info('User %s not found', username)
        return groups
