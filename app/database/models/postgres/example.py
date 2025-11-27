# -*- coding: utf-8 -*-
from typing import Optional
from sqlmodel import SQLModel, Field


class Example(SQLModel, table=True):

    __tablename__ = "postgres"

    id: Optional[int] = Field(primary_key=True, nullable=False,
                              description="Example ID", schema_extra={"example": 11})
    name: str = Field(..., description="Example name", schema_extra={"example": "John"})
    surname: str = Field(..., description="Example surname", schema_extra={"example": "Doe"})
    age: Optional[int] = Field(None, description="Example age", schema_extra={"example": 33})
