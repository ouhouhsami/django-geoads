#-*- coding: utf-8 -*-
VERSION = (0, 0, 2, 'alpha', 0)

def get_version():
    from django.utils.version import get_version
    return get_version(VERSION)
