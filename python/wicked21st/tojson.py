# -*- coding: utf-8 -*-
# Copyright (C) 2021 Textualization Software Ltd.
# Distributed under the terms of the Apache Software License 2.0
# http://www.apache.org/licenses/LICENSE-2.0

def to_json(v):
    if v is Int:
        return v
    if v is string:
        return v
    if v is list:
        return [ to_json(_) for _ in v ]
    if v is dict:
        return { k: to_json(vv) for k, vv in v.items() }
    return v.to_json()
        
