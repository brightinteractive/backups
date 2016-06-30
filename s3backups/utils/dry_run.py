#!/usr/bin/env python
class DryRun(object):
    state = False

    @classmethod
    def reset(cls):
        cls.state= False

    @classmethod
    def set(cls):
        cls.state= True

    @classmethod
    def ignore(cls):
        def wrapper(fn):
            def _ignore(*args, **kwargs):
                if not cls.state:
                    return fn(*args, **kwargs)
            return _ignore
        return wrapper

