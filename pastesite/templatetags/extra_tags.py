from django import template
from django.template import Template, Variable, TemplateSyntaxError

import humanfriendly
import datetime

register = template.Library()

class RenderAsTemplateNode(template.Node):
    """
    A simple template tag that renders the given variable as a template
    """
    def __init__(self, item_to_be_rendered):
        self.item_to_be_rendered = Variable(item_to_be_rendered)

    def render(self, context):
        try:
            actual_item = self.item_to_be_rendered.resolve(context)
            return Template(actual_item).render(context)
        except template.VariableDoesNotExist:
            return ''

@register.tag(name="render_as_template")
def render_as_template(parser, token):
    bits = token.split_contents()
    if len(bits) !=2:
        raise TemplateSyntaxError("'%s' takes only one argument"
                                  " (a variable representing a template to render)" % bits[0])    
    return RenderAsTemplateNode(bits[1])

class SecondsToStringNode(template.Node):
    """
    A template tag that converts an amount of seconds into a human-readable string
    (couldn't find a Django template tag that does this, maybe I missed something?)
    """
    def __init__(self, seconds):
        self.seconds = Variable(seconds)
    
    def render(self, context):
        time_string = humanfriendly.format_timespan(self.seconds.resolve(context))
        return time_string
    
@register.tag(name="seconds_to_str")
def seconds_to_str(parser, token):
    bits = token.split_contents()
    
    if len(bits) != 2:
        raise TemplateSyntaxError("'%s' requires one argument with a number of seconds" % bits[0])
    
    return SecondsToStringNode(bits[1])

@register.filter(name="timesince_in_seconds")
def timesince_in_seconds(value):
    """
    Converts a provided datetime to amount of seconds that have passed
    """
    current_datetime = datetime.datetime.now()
    
    difference = current_datetime - value
    
    return difference.total_seconds()

@register.filter(name="timeuntil_in_seconds")
def timeuntil_in_seconds(value):
    """
    Returns the time until a given datetime in seconds
    """
    current_datetime = datetime.datetime.now()
    
    difference = value - current_datetime
    
    return abs(difference.total_seconds())