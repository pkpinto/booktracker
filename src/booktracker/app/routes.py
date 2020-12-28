import io

from flask import current_app as app
from flask import abort, flash, redirect, render_template, request, send_file

from . import mongo
from .data_util import asset_to_book, query_asset_records


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html', title='404', assetid=str(e)), 404


@app.route('/', methods=['GET'])
def home():
    books = mongo.books()
    return render_template('index.html', title='home', books=books)

@app.route('/books')
def books():
    books = mongo.books()
    books = sorted(books, key=lambda x: (x['series'] if x['series'] is not None else x['title'], x['date']))
    return render_template('books.html', title='books', books=books)

@app.route('/asset-get', methods=['GET'])
def _asset_get():
    assetid = request.args.get('assetid')
    return redirect('/books/{}'.format(assetid), code=303)

@app.route('/asset-add', methods=['GET'])
def _asset_add():
    assetid = request.args.get('assetid')
    asset, content_metadata = query_asset_records(assetid)
    if asset is None:
        abort(404, description='{} could not be found in Apple Content Metadata'.format(assetid))
    mongo.upsert_book(assetid, asset, content_metadata)
    return redirect('/books/{}'.format(assetid), code=303)

@app.route('/asset-rm', methods=['GET'])
def _asset_rm():
    assetid = request.args.get('assetid')
    mongo.delete_book(assetid)
    return redirect('/books', code=303)

@app.route('/books/<assetid>', methods=['GET'])
def asset(assetid):

    # first try mongo
    books = mongo.books(filter={'_id': assetid})
    if len(books) == 1:
        return render_template('asset_local.html', title=assetid, books=books)
        
    # otherwise query apple content metadata
    asset, content_metadata = query_asset_records(assetid)
    if asset is not None:
        asset['results'] = content_metadata['results']
        return render_template('asset_content_metadata.html', title=assetid, books=[asset_to_book(asset)])
    
    abort(404, description='{} could not be found locally nor in Apple Content Metadata'.format(assetid))

@app.route('/books/<assetid>/artwork', methods=['GET'])
def asset_artwork(assetid):
    art = mongo.db['assets'].find_one({'_id': assetid})['artwork']
    return send_file(io.BytesIO(art), mimetype='image/jpg', as_attachment=False)
