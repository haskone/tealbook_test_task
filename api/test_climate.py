import json
import pytest

from requests.auth import _basic_auth_str

from flask import Flask
from api.climate import climate_blueprint
from model.database import db, ma


@pytest.fixture
def client():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.register_blueprint(climate_blueprint)

    db.init_app(app)
    ma.init_app(app)
    with app.app_context():
        db.create_all()

    client = app.test_client()
    ctx = app.app_context()
    ctx.push()

    yield client

    ctx.pop()

TEST_USER = 'admin'
TEST_PASS = 'password'

EMPTY_RESPONSE = {
    "climates": [],
    "page": 1,
    "total_pages": 0
}

OBJ_TO_SEND = {
    "station_name": "name",
    "climate_id": "climate_id",
    "province_code": "AA",
    "local_date": "some date no format",
    "mean_temp": -1.0,
    "min_temp": 4.5,
    "max_temp": 100500.64,
    "record_id": "123"
}

def test_get_empty_db(client):
    """Start with a blank database."""

    rv = client.get('/api/climate/')
    assert EMPTY_RESPONSE == json.loads(rv.data)

def test_post_no_cred_empty_db(client):
    """Start with a blank database."""

    rv = client.post(
        '/api/climate/',
        data=json.dumps(OBJ_TO_SEND),
        content_type='application/json',
    )
    assert b'Unauthorized Access' == rv.data

def test_post_cres_empty_db(client):
    """Start with a blank database."""

    rv = client.post(
        '/api/climate/',
        data=json.dumps(OBJ_TO_SEND),
        content_type='application/json',
        headers={
            "Authorization":  _basic_auth_str(TEST_USER, TEST_PASS)
        }
    )
    expect_dict = OBJ_TO_SEND.copy()
    expect_dict['id'] = '1'
    assert expect_dict == json.loads(rv.data)