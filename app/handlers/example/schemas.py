# -*- coding: utf-8 -*-
from typing import Optional
from pydantic import BaseModel, Field


class SampleEchoRequest(BaseModel):
    name: str = Field(..., example="Foo")
    description: Optional[str] = Field(None, example="A very nice Item")
    price: float = Field(..., example=35.4)
    tax: Optional[float] = Field(None, example=3.2)


class SampleEchoResponse(BaseModel):
    name: str = Field(..., example="Foo")
    description: Optional[str] = Field(None, example="A very nice Item")
    price: float = Field(..., example=35.4)
    tax: Optional[float] = Field(None, example=3.2)
    processed: bool = True


class SubappHelloResponse(BaseModel):
    message: str = Field(..., example="Hello!")
