from __future__ import absolute_import  # Python 2 only

from jinja2 import Environment

from pastebin import jinja_globals

def environment(**options):
    env = Environment(**options)
    
    # Add methods ported from Django to namespace
    env.globals.update(jinja_globals.JINJA_GLOBALS)
    return env