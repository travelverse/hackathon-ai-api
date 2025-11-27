# -*- coding: utf-8 -*-

import handlers.base
import handlers.index
import handlers.security
import handlers.example.handlers
import handlers.databases.handlers
import handlers.health
import handlers.profile

export = [
    handlers.base,
    handlers.index,
    handlers.example.handlers,
    handlers.databases.handlers,
    handlers.health,
    handlers.profile,
]


