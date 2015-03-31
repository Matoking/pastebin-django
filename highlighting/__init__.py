from collections import OrderedDict
from itertools import chain

from highlighting import settings
from highlighting.formatter import ListHtmlFormatter

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

def language_exists(language):
    """
    Check that the language exists in the tuple
    """
    if language in chain(*settings.LANGUAGES):
        return True
    else:
        return False

def format_text(text, format="text"):
    """
    Format the text using Pygments and return the formatted text
    """
    lexer = get_lexer_by_name(format)
    formatter = ListHtmlFormatter(linenos=False,
                                  prestyles="border-radius: 0px; background-color: white; border: 0px;")
    result = highlight(text, lexer, formatter)
    
    # A small hack to include CSS styles in the table containing the line numbers
    # This needs to be done because otherwise Bootstrap inserts its own styling to the pre-element, 
    # which makes it look like crap
    result = result.replace("<div class=\"linenodiv\"><pre>", "<div class=\"linenodiv\"><pre style=\"background-color: white; border: 0px; border-radius: 0px; border-right: 3px solid rgb(108, 226, 108) !important; color: rgb(175, 175, 175);\">")
    
    return result