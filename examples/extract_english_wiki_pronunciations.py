
from mediawiki_dump.dumps import LocalWikipediaDump
from mediawiki_dump.reader import DumpReader

from wikitionaryparser.con
from wikitionaryparser.utilities import utils

def readWikiDump(bz2FileDumpFn, outputFn):
    dump = LocalWikipediaDump(bz2FileDumpFn)
    pages = DumpReader().read(dump)
    counter = utils.ResultCounter()
    targetLang = 'English'
    try:
        with io.open(outputFn, "w", encoding="utf-8") as fd:
            for page in pages:
                counter.total += 1

                definitionRows = []
                try:
                    definitionRows = pageToDefinitions(page, targetLang)
                except MissingTargetLangPage:
                    counter.wrongLang += 1
                    continue
                except MissingPronunciationSection:
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
            # for definitionRow in definitionRows:
            #     csvWriter.writerow(definitionRow)
    finally:
        counter.printResult()


if __name__ == '__main__':
    fn = "../../enwiktionary-latest-pages-articles.xml.bz2"
    outputFn = 'wiki_definitions.txt'
    readWikiDump(fn, outputFn)

    # testPage('test_page.txt')
