# -*- coding: utf-8 -*-
from sqlmodel import insert
from modules.database.sqlmodel import async_session
from database.models.postgres.example import Example


async def seed(engine):
    """Seed database data."""
    async with async_session(engine) as session:
        await session.execute(insert(Example).values([
            {"name": "John", "surname": "Doe", "age": 20},
            {"name": "Justin", "surname": "Doe", "age": 30},
            {"name": "Miranda", "surname": "Doe", "age": 27}
        ]))
        await session.commit()
