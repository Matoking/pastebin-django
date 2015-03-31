"""
Iterate through all languages supported by Pygments and print a sorted list of languages

This can then be copied into settings.py
"""
from pygments.lexers import get_all_lexers
import operator

languages = {}

for lexer in get_all_lexers():
    if lexer[1][0] != "text":
        languages[lexer[1][0]] = lexer[0]
    
sorted_list = sorted(languages.items(), key=operator.itemgetter(0))

# Add "text only" at the beginning
sorted_list.insert(0, ("text", "Text only"))

print(sorted_list)