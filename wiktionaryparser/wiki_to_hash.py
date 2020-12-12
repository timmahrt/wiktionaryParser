'''
Contains pageToDefinitions(), a utility for stripping down a page to an easy-to-work with format.

The format is:
[
  pageName,
  [
    [pronunciations_1, {'Noun': 'noun definition', 'Verb': 'verb definition', ...},
    [pronunciations_2, {'Adj': 'adjective definition', ...}]
  ]
]
where each entry is a different sense ('etymology' in wikipedia speak)
'''

import re
#import pdb

from wiktionaryparser import wiki_reader

POS_LIST = [
    'Adjective', 'Adverb', 'Ambiposition', 'Article', 'Circumposition',
    'Classifier', 'Conjunction', 'Contraction', 'Counter', 'Determiner',
    'Ideophone', 'Interjection', 'Noun', 'Numeral', 'Participle',
    'Particle', 'Postposition', 'Preposition', 'Pronoun', 'Proper noun',
    'Verb'
    ]

PRONUNCIATION = 'Pronunciation'
ETYMOLOGY_LIST = ['Etymology 1', 'Etymology 2', 'Etymology 3']

languageToCode = {'English': 'en'}

class MissingTargetLangPage(Exception):
    pass

class MissingPronunciationSection(Exception):
    pass

class DeletedTree(Exception):
    pass

def getContentForLanguage(page, pageTitle, language):
    '''
    Get's the top level section for this page in the target language

    If it doesn't exist, raise an error.  If it exists but
    is unparseable, this returns None.
    '''
    languageHeader = '==%s==\n' % language
    if languageHeader not in page:
        raise MissingTargetLangPage()

    for rootSection in wiki_reader.buildContentTree(page, 4, language):
        if rootSection.title == language:
            rootSection.content = pageTitle
            return rootSection

    return None

def _pruneSection(root):
    # Allowed parts of speech
    # https://en.wiktionary.org/wiki/Wiktionary:Entry_layout#:~:text=Parts%20of%20speech%3A%20Adjective%2C%20Adverb,%2C%20Pronoun%2C%20Proper%20noun%2C%20Verb
    return root.prune(POS_LIST + [PRONUNCIATION] + ETYMOLOGY_LIST, [], 100)

def _reduceDefinitions(root):
    '''
    Definitions can be very long;  this takes only the first part of each
    '''

    bracketedRe = re.compile('{{.*?}}')

    def _internalReduceDefinitions(section):
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

    root.processContent(_internalReduceDefinitions)

    return root

def _cleanPronunciations(root, languageCode):
    '''
    Get the phonemic or phonetic representation of the word

    Prefer phonemic over phonetic (don't get both).
    If neither is available, erase the pronunciation's content
    '''
    bracketedRe = re.compile('{{.*?}}')
    phonemicPronRe = re.compile('/.*?/')
    phoneticPronRe = re.compile(r'\[.*?\]')

    def _internalCleanPronunciations(section):
        if section.title != PRONUNCIATION:
            return section.content
        potentialPronList = []
        for pron in bracketedRe.findall(section.content):
            pronParts = pron[2:-2].split('|')
            if 'IPA' not in pronParts[0]:
                continue
            if pronParts[1] != languageCode:
                continue
            potentialPronList.append(pronParts[2])

        pronList = []
        for pron in potentialPronList:
            if phonemicPronRe.match(pron):
                pronList.append(pron)

        # If there was no phonetic pronunciation
        # fall back to the phonemic one
        if not pronList:
            for pron in potentialPronList:
                if phoneticPronRe.match(pron):
                    pronList.append(pron)

        return pronList

    root.processContent(_internalCleanPronunciations)

    return root

def _getPronunciationsFromTree(tree):
    pronunciations = None
    pronSection = tree.getSectionByTitle('Pronunciation')
    if pronSection:
        pronunciations = pronSection.content

    return pronunciations

def _getDefinitionsFromTree(tree):
    definitions = []
    for section in tree.subsections:
        if section.title in POS_LIST:
            pos = section.title.lower()
            definition = section.content
            definitions.append([pos, definition])

    return definitions

def _pairDefinitionsAndPronunciations(pronunciations, definitions, defaultPronunciations=None):
    if pronunciations is None:
        pronunciations = defaultPronunciations

    # Aggregate definitions:
    posToDef = {}
    for pos, definition in definitions:
        if pos not in posToDef.keys():
            posToDef[pos] = []
        posToDef[pos].append(definition)

    wordData = []
    if pronunciations and posToDef:
        wordData = [pronunciations, posToDef]

    return wordData

def _posHashMerge(hashA, hashB):
    '''
    Combines two hashs where the values are lists
    '''
    allKeys = list(hashA.keys()) + list(hashB.keys())
    mergedHash = {}
    for key in allKeys:
        data = hashA.get(key, []) + hashB.get(key, [])
        mergedHash[key] = data

    return mergedHash

def _getTreeEssentials(tree):
    '''
    Get just the essentials that will be stored in the output
    '''
    subtrees = []
    for etymology in ETYMOLOGY_LIST:
        subtree = tree.popSubsection(etymology)
        if not subtree:
            break
        subtrees.append(subtree)

    treeSummary = []
    rootPronunciations = _getPronunciationsFromTree(tree)
    rootDefinitions = _getDefinitionsFromTree(tree)
    treeSummary.extend(_pairDefinitionsAndPronunciations(rootPronunciations, rootDefinitions))

    # Sometimes the etymologies only add definitions but without pronunciation
    # In that case, take the pronunciation from the higher level
    # But prefer to use the etymologies' pronunciations if they exist
    for subtree in subtrees:
        subPronunciations = _getPronunciationsFromTree(subtree)
        subDefinitions = _getDefinitionsFromTree(subtree)
        treeSummary.extend(_pairDefinitionsAndPronunciations(
            subPronunciations,
            subDefinitions,
            rootPronunciations)
        )

    return treeSummary

def getDefinitionsFromPage(page, language):
    '''
    Given a page a definition, returns all the definitions found on the pages

    There must be at least one definition and one pronunciation for a word to appear in the output.
    There is one entry per sense.  The root of the document may be a sense, as well as any
    etymology sections.
    '''
    langCode = languageToCode[language]

    # Debug the target word by skipping all previous words here before parsing happens
    # targetWord = 'Saturday'
    # if page.title != targetWord:
    #     return []

    sectionTree = getContentForLanguage(page.content, page.title, language)

    if sectionTree is None:
        return []

    if not sectionTree.getSectionByTitle(PRONUNCIATION):
        raise MissingPronunciationSection()

    sectionTree = _pruneSection(sectionTree)

    if sectionTree is None:
        raise DeletedTree()

    sectionTree = _reduceDefinitions(sectionTree)
    sectionTree = _cleanPronunciations(sectionTree, langCode)
    wordSenseDefinitions = _getTreeEssentials(sectionTree)

    # if page.title == targetWord:
    #     pdb.set_trace()

    return wordSenseDefinitions
