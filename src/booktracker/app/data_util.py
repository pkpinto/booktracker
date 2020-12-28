import io

from flask import Markup
import requests


def asset_to_book(asset):
    asset_results = asset['results'][asset['_id']]
    series_info = asset_results['ebookInfo'].get('seriesInfo')
    return {
        'assetid': asset['_id'],
        'ibooks_link': asset['ibooks_link'],
        'title': asset_results['name'],
        'series': (None if asset_results['ebookInfo'].get('seriesInfo') is None else
                   ' '.join([series_info['seriesName'], '' if series_info['sequenceNumber'] is None else series_info['sequenceNumber']])),
        'author': asset_results['artistName'],
        'publisher': asset_results['ebookInfo']['publisher'],
        'date': asset_results['releaseDate'],
        'description': Markup(asset_results['description']['standard']),
        'artwork_url': asset['artwork_url'],
    }


def query_asset_records(assetid):
    content_metadata = query_content_metadata(assetid)

    if content_metadata['results'].get(assetid, False):

        artwork_url = content_metadata['results'][assetid]['artwork']['url'].format(
            w=content_metadata['results'][assetid]['artwork']['width'],
            h=content_metadata['results'][assetid]['artwork']['height'],
            f='jpg',
        )
        r = requests.get(artwork_url)
        artwork = io.BytesIO(r.content)
        asset = {
            '_id': assetid,
            'ibooks_link': 'ibooks://assetid/{}'.format(assetid),
            'artwork': artwork.getvalue(),
            'artwork_url': artwork_url,
        }
        return asset, content_metadata

    else:
        return None, None

def query_content_metadata(assetid, store='gb'):
    # content metadata
    r = requests.get('https://uclient-api.itunes.apple.com/WebObjects/MZStorePlatform.woa/wa/lookup?version=2&id={}&p=mdm-lockup&caller=MDM&platform=omni&cc={}'.format(assetid, store))
    cm = r.json()
    cm['_id'] = assetid
    return cm
