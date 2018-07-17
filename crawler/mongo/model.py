from mongoengine import *
import datetime

connect('datashop-mongo')


class Stock(Document):
    id = StringField(required=True)
    name = StringField(required=True)
    create_date = DateTimeField(default=datetime.datetime.now)


class ShareHolder(Document):
    position = StringField(required=True)
    name = StringField(required=True)
    stock_count = LongField(required=True)
    stock_percentage = StringField(required=True)
    stock_update_date = StringField(required=True)
    create_date = DateTimeField(default=datetime.datetime.now)
