from betterconf import Config as BaseConfig
from betterconf import field
from betterconf.caster import to_int


class Config(BaseConfig):
    NODE_NAME = field()
    NODE_DESCRIPTION = field()

    MONGO_HOST = field()
    MONGO_PORT = field(caster=to_int)
    MONGO_DB = field()


config = Config()
