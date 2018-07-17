from mongoengine import *
import datetime

connect('stock', host='datashop-mongo')


class Stock(Document):
    stock_id = StringField(required=True)
    stock_name = StringField(required=True)
    stock_type = StringField(required=True)
    create_date = DateTimeField(default=datetime.datetime.now)


class ShareHolder(Document):
    stock_id = StringField(required=True)
    stock_name = StringField(required=True)
    stock_type = StringField(required=True)
    position = StringField(required=True)
    name = StringField(required=True)
    stock_count = LongField(required=True)
    stock_percentage = StringField(required=True)
    stock_update_date = StringField(required=True)
    create_date = DateTimeField(default=datetime.datetime.now)