from pydantic import AnyUrl, BaseModel, BaseSettings


class Mongodb(BaseModel):
    host: AnyUrl = 'localhost'
    replicaset: str = None
    database = 'booktracker'


class API(BaseModel):
    title = 'Booktracker web frontend'
    description = 'Books, tracked'
    host: AnyUrl = '0.0.0.0'
    port = 5000
    mongodb = Mongodb()


class Web(BaseModel):
    title = 'Booktracker REST API'
    description = 'Books, tracked'
    host: AnyUrl = '0.0.0.0'
    port = 5001
    backend_url: AnyUrl = 'http://localhost:5000'


class Config(BaseSettings):

    api = API()
    web = Web()

    class Config:
        env_prefix = 'BOOKT_'
        case_sensitive = False


config = Config()
