
import os
import io
import json

from mediawiki_dump.dumps import LocalWikipediaDump
from mediawiki_dump.reader import DumpReader

from wiktionaryparser import wiki_to_hash
from wiktionaryparser.utilities import utils

def readWikiDump(bz2FileDumpFn, outputFn):
    '''


    It took about an hour to process a whole dump (~7,000,000 pages).
    Not bad, but I think we can do better
    '''
    dump = LocalWikipediaDump(bz2FileDumpFn)
    pages = DumpReader().read(dump)
    counter = utils.ResultCounter()
    targetLang = 'English'

    if os.path.exists(outputFn):
        print("Output fn exists, please move somewhere else before running")
        exit(0)

    try:
        with io.open(outputFn, "w", encoding="utf-8") as fd:
            for page in pages:
                counter.total += 1

                if counter.total % 100000 == 0:
                    print(counter.total)

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
                    outputTxt = json.dumps(
                        {'name': page.title, 'senses': definitionRows},
                        separators=(',', ':')
                    )
                    outputTxt = outputTxt.replace('\n', '')
                    fd.write(outputTxt + '\n')
                else:
                    counter.noErrorButNoData += 1
                    print(page.title)
    finally:
        counter.printResult()

def sortOutput(inputFn, outputFn):
    with io.open(inputFn, "r", encoding="utf-8") as fd:
        dataList = fd.readlines()

    dataList.sort(key=lambda rowText: rowText.lower())

    with io.open(outputFn, "w", encoding="utf-8") as fd:
        fd.write("".join(dataList))

if __name__ == '__main__':
    fn = "../../enwiktionary-latest-pages-articles.xml.bz2"

    outputFn = 'wiki_definitions.txt'
    #readWikiDump(fn, outputFn)

    sortedOutputFn = 'processed_english_wiktionary.txt'
    sortOutput(outputFn, sortedOutputFn)
