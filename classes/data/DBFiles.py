# -*- coding: utf-8 -*-
def enum(**enums):
    return type('Enum', (), enums)

DBFiles = enum(Scenarios = 1)