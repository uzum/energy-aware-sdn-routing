import sys
class LookupService():
    def __init__(self):
        self.name = 'LookupService'

    def onContentRequest(self, test):
        return { 'request': test, 'version': 12 }
