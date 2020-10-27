import io

from flask import current_app as app
from flask import render_template, send_file

from . import mongo


@app.route('/', methods=['GET'])
def home():
    books = mongo.books()
    return render_template('index.html', title='home', books=books)


@app.route('/books')
def books():
    books = mongo.books()
    return render_template('books.html', title='books', books=books)


@app.route('/assets/<assetid>/artwork', methods=['GET'])
def asset_artwork(assetid):
    art = mongo.db['assets'].find_one({'_id': assetid})['artwork']
    return send_file(io.BytesIO(art), mimetype='image/jpg', as_attachment=False)


@app.route('/assets/<assetid>', methods=['GET'])
def asset(assetid):
    books = mongo.books(filter={'_id': assetid})
    return render_template('asset.html', title=assetid, books=books)

# @app.route('/assets/<assetid>', methods=['POST'])
# def asset(assetid):
#     return render_template('asset.html', title=assetid, assetid=assetid)