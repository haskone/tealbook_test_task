import math

from flask_httpauth import HTTPBasicAuth

from flask import Flask, Blueprint, request, jsonify
from flask_restplus import Resource, Api, fields, abort

from model.database import db, ma, ClimateEntity, climate_schema, climates_schema

from utils.core import logger

climate_blueprint = Blueprint('api', __name__, url_prefix='/api/climate')

api = Api(climate_blueprint, doc='/doc/', version='1.0', title='Kind of climate api',
    description='API based on some climate data', default ='Climates', default_label='Climate again, ok')

base_fields = {
    'station_name': fields.String(required=True),
    'climate_id': fields.String(required=True),
    'province_code': fields.String(required=True),
    # 'local_date': fields.DateTime(dt_format='iso8601', required=True),
    # Let's keep it simple for now
    'local_date': fields.String(required=True),
    'mean_temp': fields.Float(required=True),
    'min_temp': fields.Float(required=True),
    'max_temp': fields.Float(required=True),
    'record_id': fields.String(required=True),
}

input_climate = api.model(
    'Climate',
    base_fields
)
response_climate = api.model('ResponseClimate', {
    'id': fields.String(required=True),
    **base_fields,
})
response_climates = api.model('ListClimate', {
    'climates': fields.List(fields.Nested(response_climate)),
    'page': fields.Integer(),
    'total_pages': fields.Integer(),
})

base_fields_optional = {
    'mean_temp': fields.Float(required=True),
    'min_temp': fields.Float(required=True),
    'max_temp': fields.Float(required=True),
}
input_climate_optional = api.model('OptionalClimate', base_fields_optional)

PAGE_SIZE = 10

auth = HTTPBasicAuth()
# TODO: from db and with registration/etc of course
USER_DATA = {
    "admin": "password"
}

@auth.verify_password
def verify(username, password):
    if not (username and password):
        return False
    return USER_DATA.get(username) == password

@api.route('/')
class Climates(Resource):

    @api.doc(params={
        'sort': 'Sort order by date, asc | desc',
        'filter_station': 'filter by station name',
        'page': f'A page number, each page has {PAGE_SIZE} items',
        'total_pages': 'A total number of pages'
    })
    @api.marshal_with(response_climates, code=200)
    def get(self):
        sort_date = request.args.get('sort')
        filter_station = request.args.get('filter_station')
        try:
            page = int(request.args.get('page', 1))
        except:
            page = 1
        logger.info(
            'Get with params: '
            f'page ({page}), '
            f'sort ({sort_date}), '
            f'stations ({filter_station})'
        )

        base_query = ClimateEntity.query
        if sort_date and sort_date in ['asc', 'desc']:
            base_query = base_query.order_by(
                ClimateEntity.local_date.desc()
                if sort_date == 'desc'
                else ClimateEntity.due_date.asc()
            )
        if filter_station:
            base_query = base_query.filter(
                ClimateEntity.station_name.contains(filter_station)
            )

        climates = base_query.paginate(page, PAGE_SIZE, error_out=False)
        total = climates.total
        record_items = climates.items

        result = climates_schema.dump(record_items)
        return {
            'climates': result,
            'page': page,
            'total_pages': math.ceil(total / PAGE_SIZE)
        }

    @auth.login_required
    @api.expect(input_climate, validate=True)
    @api.marshal_with(response_climate, code=201)
    def post(self):
        climate_json = request.get_json()

        logger.info(f'Post new with body: {climate_json}')

        new_climate = ClimateEntity(**climate_json)
        db.session.add(new_climate)
        db.session.commit()
        return new_climate, 201


@api.route('/<int:climate_id>')
@api.doc(params={'climate_id': 'An ID of an entity'})
class Climate(Resource):
    
    @api.marshal_with(response_climate, code=200)
    def get(self, climate_id):
        climate = ClimateEntity.query.get(climate_id)
        if not climate:
            abort(404, error=f"Climate with id {climate_id} not found")
        return climate

    @api.marshal_with(response_climate, code=200)
    @api.expect(input_climate_optional, validate=True)
    def put(self, climate_id):
        climate = ClimateEntity.query.get(climate_id)
        if not climate:
            abort(404, error=f"Climate with id {climate_id} not found")

        climate_json = request.get_json()
        for key, new_value in climate_json.items():
            setattr(climate, key, new_value)
        db.session.commit()
        return climate

    def delete(self, climate_id):
        climate = ClimateEntity.query.get(climate_id)
        if not climate:
            abort(404, error=f"Climate with id {climate_id} not found")
        db.session.delete(climate)
        db.session.commit()
        return "DELETED", 200

    