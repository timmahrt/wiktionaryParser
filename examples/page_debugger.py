'''
Can be used to load a single page in from disk.  Useful for debugging issues with
specific pages without dealing with the whole corpus
'''
import io
from os.path import join

from wikitionaryparser import wiki_to_pron

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
    print(wiki_to_pron.pageToDefinitions(testPage, language))

if __name__ == "__main__":
    _pageAsTextFn = join('.', 'files', 'cheap.txt')
    _title = 'Cheap'
    _language = 'English'
    loadTestPage(_pageAsTextFn, _title, _language)