from pygments.formatters import HtmlFormatter

class ListHtmlFormatter(HtmlFormatter):
    """
    Wraps the code inside an <ol> element, which works nicely with line wrapping
    """
    def wrap(self, source, outfile):
        return self._wrap_ol(source)

    def _wrap_ol(self, source):
        yield 0, '<ol class="code">'
        for i, t in source:
            if i == 1:
                t = '<li class="line"><div class="line">' + t + '</div></li>'
            yield i, t
        yield 0, '</ol>'