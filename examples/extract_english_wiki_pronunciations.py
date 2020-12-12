
from mediawiki_dump.dumps import LocalWikipediaDump
from mediawiki_dump.reader import DumpReader

from wiktionaryparser import wiki_to_hash
from wiktionaryparser.utilities import utils

def readWikiDump(bz2FileDumpFn, outputFn):
    dump = LocalWikipediaDump(bz2FileDumpFn)
    pages = DumpReader().read(dump)
    counter = utils.ResultCounter()
    targetLang = 'English'
    try:
        for page in pages:
            counter.total += 1

            if counter.total > 10000:
                counter.printResult()
                exit(0)

            definitionRows = []
            try:
                definitionRows = wiki_to_hash.getDefinitionsFromPage(page, targetLang)
            except wiki_to_hash.MissingTargetLangPage:
                counter.wrongLang += 1
                continue
            except wiki_to_hash.MissingPronunciationSection:
                counter.noPronunciation += 1
                continue
            except: # Shhh
                counter.errored += 1
                if counter.errored % 1000 == 0:
                    counter.printResult()
                continue

            if len(definitionRows) > 0:
                counter.dataful += 1
            else:
                counter.noErrorButNoData += 1
                print(page.title)
    finally:
        counter.printResult()


if __name__ == '__main__':
    fn = "../../enwiktionary-latest-pages-articles.xml.bz2"
    outputFn = 'wiki_definitions.txt'
    readWikiDump(fn, outputFn)

    # testPage('test_page.txt')
