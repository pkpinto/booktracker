from typing import List, Tuple

from pymongo.mongo_client import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from starlette.requests import Request


class Mongodb:

    def __init__(self, host, replicaset, database):
        self.db = MongoClient(host=host, replicaset=replicaset)[database]

    def list_assets(self):
        c = self.db['content_metadata'].find({}, projection={'_id': True})
        for r in c:
            yield r['_id']

    def get_asset(self, assetid):
        r = self.db['content_metadata'].find_one({'_id': assetid})
        return r if r is not None else {}

    def upsert_asset(self, assetid, data):
        data['_id'] = assetid
        r = self.db['content_metadata'].replace_one({'_id': assetid}, data, upsert=True)
        return {'modified_count': r.modified_count, 'upserted_id': r.upserted_id}

    def delete_asset(self, assetid):
        r = self.db['content_metadata'].delete_one({'_id': assetid})
        return {'deleted_count': r.deleted_count}

    def get_asset_artwork(self, assetid):
        r = self.db['asset_artwork'].find_one({'_id': assetid}, projection={'artwork': True})
        return r['artwork'] if r is not None else None

    def upsert_asset_artwork(self, assetid, data):
        _data = {'_id': assetid, 'artwork': data}
        r = self.db['asset_artwork'].replace_one({'_id': assetid}, _data, upsert=True)
        return {'modified_count': r.modified_count, 'upserted_id': r.upserted_id}

    def delete_asset_artwork(self, assetid):
        r = self.db['asset_artwork'].delete_one({'_id': assetid})
        return {'deleted_count': r.deleted_count}

    def get_books(self, assetids=None):

        if assetids is None:
            filter = {}
        elif not isinstance(assetids, List) and not isinstance(assetids, Tuple):
            filter = {'_id': {'$in': [assetids]}}
        else:
            filter = {'_id': {'$in': assetids}}

        pipeline = [
            {'$match': filter},
            {'$project': {'results': {'$objectToArray': '$results'}}},
            {'$unwind': '$results'},
            {'$replaceRoot': {'newRoot': {'$mergeObjects': ['$results.v', '$$ROOT']}}},
            {
                '$project': {
                    'name': True,
                    'nameSortValue': True,
                    'artistName': True,
                    'artistId': True,
                    'releaseDate': True,
                    'ebookInfo.publisher': True,
                    'ebookInfo.subtitle': True,
                    'ebookInfo.seriesInfo': True,
                    'ebookInfo.sequenceNumber': True,
                    'description.standard': True,
                }
            }
        ]

        yield from self.db['content_metadata'].aggregate(pipeline)


# get_mongodb needs `request: Request` to be added to the function signature for dependency resolution
def get_mongodb(request: Request) -> Mongodb:
    return request.app.state.mongodb
