
import re
import io
import csv

from mediawiki_dump.dumps import LocalWikipediaDump
from mediawiki_dump.reader import DumpReader

import wiki_reader

POS_LIST = [
    'Adjective', 'Adverb', 'Ambiposition', 'Article', 'Circumposition',
    'Classifier', 'Conjunction', 'Contraction', 'Counter', 'Determiner',
    'Ideophone', 'Interjection', 'Noun', 'Numeral', 'Participle',
    'Particle', 'Postposition', 'Preposition', 'Pronoun', 'Proper noun',
    'Verb'
    ]

PRONUNCIATION = 'Pronunciation'

def getContentForLanguage(page, pageTitle, language):
    for rootSection in wiki_reader.buildContentTree(page, 1):
        if rootSection.title == language:
            rootSection.content = pageTitle
            return rootSection

def pruneSection(root):
    # Allowed parts of speech
    # https://en.wiktionary.org/wiki/Wiktionary:Entry_layout#:~:text=Parts%20of%20speech%3A%20Adjective%2C%20Adverb,%2C%20Pronoun%2C%20Proper%20noun%2C%20Verb
    return root.prune(POS_LIST + [PRONUNCIATION], [], 1)

def reduceDefinitions(root):

    bracketedRe = re.compile('{{.*?}}')

    def _reduceDefinitions(section):
        if section.title not in POS_LIST:
            return section.content

        returnContent = section.content
        splitContent = section.content.split("#")
        if len(splitContent) > 1:
            returnContent = splitContent[1]

        for char in ['[', ']']:
            returnContent = returnContent.replace(char, '')

        returnContent = bracketedRe.sub('', returnContent)

        return returnContent.strip()

    root.processContent(_reduceDefinitions)

    return root

def cleanPronunciations(root):

    bracketedRe = re.compile('{{.*?}}')

    def _cleanPronunciations(section):
        if section.title != PRONUNCIATION:
            return section.content

        pronList = []
        for pron in bracketedRe.findall(section.content):
            if 'IPA' not in pron or 'IPA letters' in pron:
                continue
            left, right = pron.rsplit('|', 1)
            if 'en' not in left:
                continue
            remaining = right.split('/')
            if len(remaining) != 3:
                continue
            pronList.append(remaining[1])

        return pronList

    try:
        root.processContent(_cleanPronunciations)
    except:
        print(root.toJson())
        raise

    return root

def getTreeEssentials(tree):
    '''
    Get just the essentials that will be stored in the output
    '''
    word = tree.content

    pronunciations = None
    pronSection = tree.getSectionByTitle('Pronunciation')
    if pronSection:
        pronunciations = pronSection.content

    definition = None
    for section in tree.subsections:
        if section.title in POS_LIST:
            pos = section.title.lower()
            definition = section.content
            break

    treeSummary = []
    if pronunciations and definition:
        for pronunciation in pronunciations:
            treeSummary.append([word, pronunciation, pos, definition])

    return treeSummary

class DeletedTree(Exception):
    pass

def pageToDefinitions(page, language):
    sectionTree = getContentForLanguage(page.content, page.title, language)
    if sectionTree is None:
        return []

    sectionTree = pruneSection(sectionTree)
    if sectionTree is None:
        raise DeletedTree()

    sectionTree = reduceDefinitions(sectionTree)
    sectionTree = cleanPronunciations(sectionTree)
    definitionRows = getTreeEssentials(sectionTree)

    return definitionRows


def testPage(pageAsTextFn):
    '''
    Debugging problems with specific pages
    '''
    class TestPage:
        def __init__(self, content, title):
            self.content = content
            self.title = title

    with io.open(pageAsTextFn, "r", encoding="utf-8") as fd:
        pageTxt = fd.read()

    testPage = TestPage(pageTxt, "Sleep")
    print(pageToDefinitions(testPage, 'English'))


def readWikiDump(bz2FileDumpFn, outputFn):
    dump = LocalWikipediaDump(bz2FileDumpFn)
    pages = DumpReader().read(dump)
    total = 0
    dataful = 0
    errored = 0
    with io.open(outputFn, "w", encoding="utf-8") as fd:
        csvWriter = csv.writer(fd, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        for page in pages:
            total += 1

            if total % 50000 == 0:
                print("%d / %d pages had at least 1 definition" % (dataful, total))

            try:
                definitionRows = pageToDefinitions(page, 'English')
            except: # Shhh
                errored += 1
                if errored % 1000 == 0:
                    print('%d pages errored out' % errored)

                print(page.title)

                if errored > 1000:
                    raise


            if len(definitionRows) > 0:
                dataful += 1
            for definitionRow in definitionRows:
                csvWriter.writerow(definitionRow)

    print("%d / %d pages had at least 1 definition" % (dataful, total))
    print('%d pages errored out' % errored)

if __name__ == '__main__':
    fn = "enwiktionary-latest-pages-articles.xml.bz2"
    outputFn = 'wiki_definitions.txt'
    readWikiDump(fn, outputFn)

    # testPage('test_page.txt')
