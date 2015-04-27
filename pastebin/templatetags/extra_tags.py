from django import template
from django.template import Template, Variable, TemplateSyntaxError

from itertools import chain

from pastes.models import Paste
from comments.models import Comment

import humanfriendly
import datetime

import highlighting

import math

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

class PaginationListNode(template.Node):
    """
    A template tag that returns a list with links to be inserted into a pagination element
    
    Takes three arguments, current page, entries per page and total amount of entries
    """
    def __init__(self, current_page, entries_per_page, total_entries):
        self.current_page = Variable(current_page)
        self.entries_per_page = Variable(entries_per_page)
        self.total_entries = Variable(total_entries)
        
    def render(self, context):
        entries = []
        
        self.current_page = self.current_page.resolve(context)
        self.entries_per_page = self.entries_per_page.resolve(context)
        self.total_entries = self.total_entries.resolve(context)
        
        self.total_pages = math.ceil(float(self.total_entries) / float(self.entries_per_page))
        
        # Add the first and previous pages
        if self.current_page != 1:
            entries.append("first")
            entries.append("previous")
        
        # Add four pages before the current page
        for i in range(0, 4):
            page = self.current_page - i
            
            if page >= 1:
                entries.append(page)
                
        # Add the current page
        entries.append(current_page)
        
        # Add four pages after the current page
        for i in range(0, 4):
            page = self.current_page + i
            
            if page <= self.total_pages:
                entries.append(page)
                
        # Add the next and last page
        if self.current_page != self.total_pages:
            entries.append("next")
            entries.append("last")
            
        return entries

@register.tag(name="pagination_list")
def pagination_list(parser, token):
    bits = token.split_contents()
    
    if len(bits) != 4:
        raise TemplateSyntaxError("'%s' requires three arguments: current page, entries per page and total amount of entries" % bits[0])
    
    return PaginationListNode(bits[1], bits[2], bits[3])

class TotalPasteCountNode(template.Node):
    """
    Returns total amount of pastes uploaded to the site
    """
    def render(self, context):
        return Paste.get_paste_count()
    
@register.tag(name="get_total_paste_count")
def get_total_paste_count(parser, token):
    return TotalPasteCountNode()

class TotalCommentCountNode(template.Node):
    """
    Returns total amount of comments posted on the site
    """
    def render(self, context):
        return Comment.get_comment_count()
    
@register.tag(name="get_total_comment_count")
def get_total_comment_count(parser, token):
    return TotalCommentCountNode()

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

@register.filter(name="syntax_format_to_text")
def syntax_format_to_text(value):
    """
    Returns the given syntax highlighting format as a human readable string
    """
    if highlighting.language_exists(value):
        languages = chain(*highlighting.settings.LANGUAGES)
        
        for language in languages:
            if language == value:
                # Since we converted the language tuple into an iterator,
                # the human readable string is always the next one
                return languages.next()
    else:
        raise TemplateSyntaxError("Given syntax highlighting format wasn't found")