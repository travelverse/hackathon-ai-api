# -*- coding: utf-8 -*-
from sqlmodel import select
import system
from modules.database.sqlmodel import async_session
from modules.database.sqlmodel import sqlmodel_exceptions
from database.models import postgres


class ExampleGateway:

    databases = system.runtime.databases

    @sqlmodel_exceptions
    async def list(self, alias: str):
        """Get examples list.

        :param alias: database alias.
        """
        if alias == "postgres":
            async with async_session(self.databases[alias]) as session:
                return (await session.exec(select(postgres.Example))).all()

    @sqlmodel_exceptions
    async def read(self, alias: str, example_id: str):
        """Get example by ID.

        :param alias: database alias.
        :param example_id: example id.
        """
        if alias == "postgres":
            async with async_session(self.databases[alias]) as session:
                return await session.get(postgres.Example, example_id)

    @sqlmodel_exceptions
    async def create(self, alias: str, model: object, refresh: bool = False):
        """Create example.

        :param alias: database alias.
        :param model: example model.
        :param refresh: refresh model, eg record id.
        """
        if alias == "postgres":
            async with async_session(self.databases[alias]) as session:
                session.add(model)
                await session.commit()
                if refresh:
                    await session.refresh(model)
                return model
