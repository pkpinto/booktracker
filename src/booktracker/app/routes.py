import io

from flask import current_app as app
from flask import render_template, send_file

from . import mongo


@app.route('/assets/<assetid>/artwork')
def asset_artwork(assetid):
    art = mongo.db['assets'].find_one({'_id': assetid})['artwork']
    return send_file(io.BytesIO(art), mimetype='image/jpg', as_attachment=False)

@app.route('/assets/<assetid>')
def asset(assetid):
    return render_template('asset.html', assetid=assetid)
