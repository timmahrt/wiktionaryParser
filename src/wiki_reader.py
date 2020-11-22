'''
https://en.wiktionary.org/wiki/Wiktionary:Entry_layout
'''

import re

def buildContentTree(page, pruneDepth=None):
    '''
    Given a raw wiki page, return a recursively built Section instance

    'Invalid' pages will return []
    - if a section is missing its parent, for example, it is invalid

    If given, sections of depth greater than pruneDepth will not be included
    in the output
    '''
    headerRe = re.compile(r'(?:^|\n)={2,}[\w\s-]*={2,}\n')

    # Get all of the language section headers
    result = 'dummy val'
    start = 0
    indicies = []
    while result:
        result = headerRe.search(page, start)
        if result:
            start, stop = result.span()
            indicies.append([start, stop])
            start = stop

    # Use the position of the headers to find the content for each header
    sections = []
    if len(indicies) > 0:
        indicies.append([-1, -1])
        for i in range(len(indicies) - 1):
            start, stop = indicies[i]
            nextStart = indicies[i + 1][0]
            title = page[start:stop]
            content = page[stop:nextStart]
            sections.append(Section(title.strip(), content))

    return _buildContentHierarchy(sections, pruneDepth)

class InvalidHierarchy(Exception):
    pass

class InvalidRoot(Exception):
    pass

def _buildContentHierarchy(sectionsList, pruneDepth=None):
    '''
    Given an ordered list of sections with depth labeled, puts child sections under parents

    Only returns valid trees; else []
    '''
    if not pruneDepth:
        pruneDepth == 100

    if len(sectionsList) == 0:
        return []

    head = sectionsList[0]
    prevDepth = head.depth

    if prevDepth != 0:
        raise InvalidRoot()

    retList = [head]
    for section in sectionsList[1:]:
        if section.depth > pruneDepth:
            continue

        insertList = retList
        for _ in range(section.depth):
            try:
                insertList = insertList[-1].subsections
            except IndexError:
                print(section.title)
                raise InvalidHierarchy()

        insertList.append(section)

    return retList


class Section(object):

    def __init__(self, title, content):
        self.title = title.replace('=', '')
        self.content = content
        self.subsections = []
        self.depth = self._calculateDepthFromTitle(title)

    def _calculateDepthFromTitle(self, text):
        i = 0
        while text[i] == '=':
            i += 1
        return i - 2

    def toJson(self):
        '''
        Recursively converts the tree to json

        You can pretty print the tree with something like:
        json.dumps(sectionTree, default=lambda x: x.toJson(), sort_keys=True, indent=2)
        '''
        return {
            'title': self.title,
            'content': self.content,
            'subsections': [section.toJson() for section in self.subsections]
            }

    def getSectionByTitle(self, title):
        '''
        Returns the first section with the given title

        If there are multiple sections with the same title
        (e.g. Pronunciation occurs below the languages' sections
        and also below the 'Etymology' sections)
        In those cases, they will get silently skipped
        '''
        if self.title == title:
            return self

        for node in self.subsections:
            descendent = node.getSectionByTitle(title)
            if descendent:
                return descendent

        return None

    def prune(self, allowList, blockList, maxDepth):
        '''
        Reduce the size of tree

        This prunes
            - nodes with no children if not in the allow list
            - nodes (with/without children) are pruned if in the block list
            - nodes deeper than maxDepth
        '''
        if self.title in blockList or self.depth > maxDepth:
            return None

        subsections = []
        for node in self.subsections:
            descendent = node.prune(allowList, blockList, maxDepth)
            if descendent is not None:
                subsections.append(descendent)
        self.subsections = subsections

        if len(self.subsections) > 0 or self.title in allowList:
            return self

        return None

    def processContent(self, processFunc):
        self.content = processFunc(self)
        for node in self.subsections:
            node.processContent(processFunc)
