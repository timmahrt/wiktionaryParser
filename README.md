# wiktionaryParser
High-level parser of wiktionary files

I played around with some of the libraries for reading wikis and had difficulty
getting what I wanted out of wikitionary.

So, I wrote my own parser, and thats this library.

(As an aside, this
[mwparserfromhell](https://github.com/earwig/mwparserfromhell)
is a popular library but it wasn't correctly parsing some of the sections I wanted.
Maybe I should give it another shot.)

# Table of contents
1. [Usage](#usage)
2. [Data Dumps](#data-dumps)
3. [Documentation](#documentation)
4. [Version History](#version-history)
5. [Requirements](#requirements)
6. [Installation](#installation)

## Usage

There are two files in this library:

- wiki_reader.py

This file is for parsing a wikimedia page.  It puts the data into a
recursive data structure based on sections and subsections.  I designed
it particularly for wiktionary, so it might break wildly if used on
wikipedia pages, for example.

I don't have any examples using this but
the function for building trees is :`buildContentTree(page)` where
page is the raw text of a wiktionary page.

- wiki_to_hash.py

This contains the meat of the code for extracting the pronunciation data
that I was interested in.  It will take a tree representation built by
wiki_reader and condense it down to a simple hash (trimming a lot of
information that I was interested in)

Please see `examples/extract_english_wiki_pronunciations.py` to see
how I use this library.


## Data Dumps

I wrote this library to get all pronunciation data from wiktionary. There
is a good amount of data but less than I expected and it seems pretty noisy.

Data dumps can be found under `data_dumps/` in a zipped format.

- Each line is a json representation of a wiktionary page.

eg
```
{"name":"spam","senses":[["/\u02c8sp\u00e6m/"],{"noun":["Unsolicited bulk electronic messages."],"verb":["To send spam (i.e. unsolicited electronic messages.)"]}]}
```

- Pages with pronunciation, definition, and part of speech were included
  - all info is discarded
  - only pronunciations labeled as IPA were included.

- Some words have multiple senses
  - each sense is included if each sense had a definition and pronunciation.


Here are some stats from the last data dump (downloaded from wiktionary on 2020-11-21):

- 60,713 / 7,070,632 pages had at least 1 usable definition
- 6,116,777 pages not in target language
- 869,344 pages without pronunciation
- 4 pages could not be parsed
- 23,794 pages not dataful

In summary, most pages were not in English. But roughly 1,000,000 were.

Of those, most were missing their 'pronunciation'. Only about 6% of the
English pages had pronunciation data.  Pronunciation annotation level
is variable (e.g. sometimes stress and syllables are marked, sometimes not).

## Documentation

Automatically generated pdocs can be found here:

http://timmahrt.github.io/wiktionaryparser/

## Version History

Ver 1.0 (Dec 12, 2020)
- wiki parsing code is up
- first data dump made

## Requirements

There are no dependencies to use the library.  However, for my purposes,
I feed the output of mediawiki_dump to my library.  mediawiki_dump will
take a wiki dump and give you one page at a time to process.  It's very
fast in my limited experience.

See `examples/extract_english_wiki_pronunciations.py` to see how I'm using it.

[mediawiki_dump](https://github.com/macbre/mediawiki-dump)
`pip install mediawiki_dump`

## Installation

WiktionaryParser is on pypi and can be installed or upgraded from the command-line shell with pip like so

    python -m pip install wiktionaryparser --upgrade

Otherwise, to manually install, after downloading the source from github, from a command-line shell, navigate to the directory containing setup.py and type

    python setup.py install

If python is not in your path, you'll need to enter the full path e.g.

    C:\Python36\python.exe setup.py install
