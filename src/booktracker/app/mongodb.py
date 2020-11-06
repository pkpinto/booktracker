from pymongo.mongo_client import MongoClient

from .data_util import asset_to_book


class Mongodb():

    def init_app(self, app):
        self.db = MongoClient('localhost')['booktracker']

    def books(self, filter=None):
        # do a 'join' between asset and content_data
        pipeline = [
            {
                '$lookup': {
                    'from' : 'content_metadata',
                    'localField' : '_id',
                    'foreignField' : '_id',
                    'as' : 'content_metadata',
                }
            },
            # {_id:..., ..., content_metadata: [{..., results: [...]}]}
            {
                '$replaceRoot': {
                    'newRoot': {
                        '$mergeObjects': [ { '$arrayElemAt': [ '$content_metadata', 0 ] }, '$$ROOT' ]
                    },
                }
            },
            { '$project': { 'content_metadata': False } },
            # {_id:..., ..., results: {_id: {...}}}
        ]

        # $match should as early as possible in the pipeline
        if filter is not None:
            pipeline = [{'$match': filter},] + pipeline

        _books = []
        for a in self.db['assets'].aggregate(pipeline):
            _books.append(asset_to_book(a))

        return _books

    def upsert_book(self, assetid, asset, content_metadata):
        self.db['assets'].replace_one({'_id': assetid}, asset, upsert=True)
        self.db['content_metadata'].replace_one({'_id': assetid}, content_metadata, upsert=True)

    def delete_book(self, assetid):
        self.db['assets'].delete_one({'_id': assetid})
        self.db['content_metadata'].delete_one({'_id': assetid})
