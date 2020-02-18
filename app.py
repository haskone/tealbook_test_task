import urllib 

from flask import Flask, Blueprint, jsonify
from flask_restplus import Api

from api.climate import climate_blueprint
from model.database import db, ma

from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default',
        },
        'file': {
            'class': 'logging.FileHandler',
            'level': 'INFO',
            'formatter': 'default',
            'filename': 'logs/info.log'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi', 'file']
    }
})

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
ma.init_app(app)
with app.app_context():
    db.create_all()

app.register_blueprint(climate_blueprint)

@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error="Not found"), 404

if __name__ == "__main__":
    app.run()
