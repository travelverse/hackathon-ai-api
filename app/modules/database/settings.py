# -*- coding: utf-8 -*-
from typing import Optional, List
from pydantic import BaseModel, Field, AnyUrl


class AlchemySettings(BaseModel, extra="forbid"):
    url: AnyUrl
    migrations: str = "migrations"
    connect_args: Optional[dict] = Field(alias="connect-args")
    echo: Optional[bool]
    echo_pool: Optional[bool] = Field(alias="echo-pool")
    enable_from_linting: Optional[bool] = Field(alias="enable-from-linting")
    execution_options: Optional[dict] = Field(alias="execution-options")
    hide_parameters: Optional[bool] = Field(alias="hide-parameters")
    insertmanyvalues_page_size: Optional[int] = Field(alias="insertmanyvalues-page-size")
    isolation_level: Optional[str] = Field(alias="isolation-level")
    label_length: Optional[int] = Field(alias="label-length")
    logging_name: Optional[str] = Field(alias="logging-name")
    max_identifier_length: Optional[int] = Field(alias="max-identifier-length")
    max_overflow: Optional[int] = Field(alias="max-overflow")
    paramstyle: Optional[str]
    pool_logging_name: Optional[str] = Field(alias="pool-logging-name")
    pool_pre_ping: Optional[bool] = Field(alias="pool-pre-ping")
    pool_size: Optional[int] = Field(alias="pool-size")
    pool_recycle: Optional[int] = Field(alias="pool-recycle")
    pool_reset_on_return: Optional[str] = Field(alias="pool-reset-on-return")
    pool_timeout: Optional[int] = Field(alias="pool-timeout")
    pool_use_lifo: Optional[bool] = Field(alias="pool-use-lifo")
    plugins: Optional[List[str]]
    query_cache_size: Optional[int] = Field(alias="query-cache-size")
    use_insertmanyvalues: Optional[bool] = Field(alias="use-insertmanyvalues")
