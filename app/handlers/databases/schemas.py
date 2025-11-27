# -*- coding: utf-8 -*-
# pylint: disable=R0903
from typing import List
from pydantic import BaseModel
from database.gateway.example import postgres


class PostgresListResponse(BaseModel):
    examples: List[postgres.Example]
