import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from data.db_session import *
from sqlalchemy.future import select
from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession
import json


class User(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, unique=True)
    username = sqlalchemy.Column(sqlalchemy.VARCHAR(128), unique=True, default=None)
    shops = sqlalchemy.Column(sqlalchemy.VARCHAR(512))
    cards = sqlalchemy.Column(sqlalchemy.JSON, default={})

    async def add_card(self, shop_name, file_id, user_file_id):
        if not self.cards:
            self.cards = {}
            a = {}
        a = self.cards.copy()
        a[shop_name] = {'file_id': file_id, 'user_photo_file_id': user_file_id}
        self.cards = a.copy()

    async def delete_card(self, shop_name):
        a = self.cards.copy()
        del a[shop_name]
        self.cards = a.copy()

