import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from data.db_session import *
from sqlalchemy.future import select
from aiogram import Bot


class Shops(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'shops'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    ru_name = sqlalchemy.Column(sqlalchemy.VARCHAR(50))
    en_name = sqlalchemy.Column(sqlalchemy.VARCHAR(50))
