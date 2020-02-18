from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
db = SQLAlchemy()
ma = Marshmallow()

class ClimateEntity(db.Model):
    __tablename__ = 'climate'
    id = db.Column(db.Integer, primary_key=True)
    # TODO: maybe will make it as primary key
    record_id = db.Column(db.String(120))
    station_name = db.Column(db.String(120))
    climate_id = db.Column(db.String(120))
    local_date = db.Column(db.String(120))
    province_code = db.Column(db.String(120))
    mean_temp = db.Column(db.Float())
    min_temp = db.Column(db.Float())
    max_temp = db.Column(db.Float())

class ClimateSchema(ma.Schema):
    class Meta:
        fields = (
            'id',
            'station_name',
            'climate_id',
            'local_date',
            'province_code',
            'mean_temp',
            'min_temp',
            'max_temp',
        )

climate_schema = ClimateSchema()
climates_schema = ClimateSchema(many=True)
