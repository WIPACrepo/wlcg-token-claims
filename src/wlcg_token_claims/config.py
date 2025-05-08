import dataclasses as dc
import logging

from wipac_dev_tools import from_environment_as_dataclass

@dc.dataclass(frozen=True)
class EnvConfig:
    AUTH_SECRET: str = ''
    BASE_PATH: str = '/'

    HOST: str = 'localhost'
    PORT: int = 8080
    DEBUG: bool = False

    LOG_LEVEL: str = 'INFO'

    def __post_init__(self) -> None:
        object.__setattr__(self, 'LOG_LEVEL', self.LOG_LEVEL.upper())  # b/c frozen

ENV = from_environment_as_dataclass(EnvConfig, collection_sep=',')


def config_logging():
    # handle logging
    setlevel = {
        'CRITICAL': logging.CRITICAL,  # execution cannot continue
        'FATAL': logging.CRITICAL,
        'ERROR': logging.ERROR,  # something is wrong, but try to continue
        'WARNING': logging.WARNING,  # non-ideal behavior, important event
        'WARN': logging.WARNING,
        'INFO': logging.INFO,  # initial debug information
        'DEBUG': logging.DEBUG  # the things no one wants to see
    }

    if ENV.LOG_LEVEL not in setlevel:
        raise Exception('LOG_LEVEL is not a proper log level')
    logformat = '%(asctime)s %(levelname)s %(name)s %(module)s:%(lineno)s - %(message)s'
    logging.basicConfig(format=logformat, level=setlevel[ENV.LOG_LEVEL])
