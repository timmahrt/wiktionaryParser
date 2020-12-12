
class ResultCounter:

    def __init__(self):
        self.total = 0
        self.dataful = 0
        self.errored = 0
        self.wrongLang = 0
        self.noPronunciation = 0
        self.noErrorButNoData = 0

    def printResult(self):
        resultsList = [
            "%d / %d pages had at least 1 definition" % (self.dataful, self.total),
            '%d pages not in target language' % self.wrongLang,
            '%d pages without pronunciation' % self.noPronunciation,
            '%d pages errored out' % self.errored,
            '%d pages dataful' % self.dataful,
            '%d pages not dataful' % self.noErrorButNoData,
            '%d pages total' % self.total
        ]
        for result in resultsList:
            print(result)
