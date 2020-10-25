from pymongo.mongo_client import MongoClient


class Mongodb():

    def init_app(self, app):
        self.db = MongoClient('localhost')['booktracker']
