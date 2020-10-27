from flask import Markup
from pymongo.mongo_client import MongoClient


class Mongodb():

    def init_app(self, app):
        self.db = MongoClient('localhost')['booktracker']

    def books(self, filter=None):

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
            {
                '$replaceRoot': {
                    'newRoot': {
                        '$mergeObjects': [ { '$arrayElemAt': [ { '$objectToArray': '$results' }, 0 ] }, '$$ROOT' ]
                    },
                }
            },
            { '$project': { 'results': False, 'version': False, 'isAuthenticated': False } },
            {
                '$replaceRoot': {
                    'newRoot': {
                        '$mergeObjects': [ '$v', '$$ROOT' ]
                    },
                }
            },
            { '$project': { 'k': False, 'v': False } },
        ]

        # $match should as early as possible in the pipeline
        if filter is not None:
            pipeline = [{'$match': filter},] + pipeline

        _books = []
        for b in self.db['assets'].aggregate(pipeline):
            _books.append({
                'assetid': b['_id'],
                'title': b['name'],
                'subtitle': b['ebookInfo']['subtitle'],
                'series': (None if b['ebookInfo'].get('seriesInfo') is None else
                        ' '.join([b['ebookInfo']['seriesInfo']['seriesName'], b['ebookInfo']['seriesInfo']['sequenceDisplayLabel']])),
                'author': b['artistName'],
                'publisher': b['ebookInfo']['publisher'],
                'date': b['releaseDate'],
                'ibooks_link': b['ibooks_link'],
                'description': Markup(b['description']['standard']),
            })

        return _books