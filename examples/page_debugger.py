'''
Can be used to load a single page in from disk.  Useful for debugging issues with
specific pages without dealing with the whole corpus
'''
import io
from os.path import join

from wiktionaryparser import wiki_to_hash

class TestPage:

    def __init__(self, content, title):
        self.content = content
        self.title = title

def loadTestPage(pageAsTextFn, title, language):
    '''
    Debugging problems with specific pages
    '''
    with io.open(pageAsTextFn, "r", encoding="utf-8") as fd:
        pageTxt = fd.read()

    testPage = TestPage(pageTxt, title)
    print(wiki_to_hash.getDefinitionsFromPage(testPage, language))


_pageAsTextFn = join('.', 'files', 'cheap.txt')
_title = 'Cheap'
_language = 'English'
loadTestPage(_pageAsTextFn, _title, _language)
